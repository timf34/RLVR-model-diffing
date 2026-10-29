"""Generation for the IFEval incidental-grader experiment (runs under the repo .venv with inspect_ai).

    memguard -m 4 -- .venv/bin/python designs/ifeval_incidental_grader/ig_generate.py <exp> [--minutes N]

exp in {smoke, dev, main, discovery}. Resumable by key: a key is done once it has a non-error record; errors get
at most MAX_ATTEMPTS attempts. Every call's usage is costed (listed OpenRouter prices) and written with the record.
Hard stops: IFEval ledger >= BUDGET_STOP, or account usage_daily >= ACCOUNT_STOP (shared key, upper bound).
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(HERE))
import ig_render as R  # noqa: E402

SERVING_CONFIG = ROOT / "experiment.grading.3way.json"
MODELS = ("Qwen 3.5", "Qwen 3.8")
MAX_TOKENS, TIMEOUT, TEMPERATURE = 32768, 1200, 0.7
PRICES = {"Qwen 3.5": (0.26, 2.6), "Qwen 3.8": (0.039, 1.25)}  # $/M in, out (listed, as in the repo's 2026-10-29 runs)
CONCURRENCY = int(os.environ.get("IG_CONCURRENCY", 16))         # per model (A/B share providers)
MAX_STEPS = {"main": 3, "smoke": 3, "dev": 3, "discovery": 5, "applicability": 3}    # model turns after the replayed prefix
MAX_ATTEMPTS = 3
BUDGET, BUDGET_STOP = 600.0, 550.0          # runaway guard only (user: budget not a concern); cost still ledgered
ACCOUNT_STOP = 1500.0                       # runaway guard on the shared key's usage_daily
RATE_WORDS = ("429", "rate limit", "rate-limit", "ratelimit", "too many requests", "overloaded", "502", "503", "504",
              "timeout", "temporarily", "connection")
RUN = HERE / "run"
REG = HERE / "registry" / "blocks.json"


def serving() -> dict:
    s = json.loads(SERVING_CONFIG.read_text())
    targets = [{k: v for k, v in t.items() if k != "serving_note"} for t in s["targets"] if t["label"] in MODELS]
    return dict(targets=targets, target_generate=s["target_generate"], temperature=TEMPERATURE,
                target_max_tokens=MAX_TOKENS, timeout=TIMEOUT)


def cost(model: str, usage: dict) -> float:
    pin, pout = PRICES[model]
    return (usage.get("input_tokens") or 0) * pin / 1e6 + (usage.get("output_tokens") or 0) * pout / 1e6


def blocks() -> dict:
    return {b["block_id"]: b for b in json.loads(REG.read_text())}


def plan(exp: str, retained: list[str] | None = None, n_main: int | None = None) -> list[dict]:
    """Items for an experiment. For main/discovery, `retained` subtypes and `n_main` blocks come from the frozen
    design (run/main/design.json)."""
    B = blocks()
    items = []
    if exp in ("main", "discovery", "applicability"):
        d = json.loads((RUN / exp / "design.json").read_text())
        retained, n_main = d["retained_subtypes"], d["blocks_per_subtype"]
    for b in B.values():
        if exp == "dev" and b["split"] == "dev":
            cells = [("ordinary", "no_grader")]
        elif exp == "smoke" and b["split"] == "smoke" and b["block_id"].endswith("-01"):
            cells = [("ordinary", "no_grader"), ("evaluation", "metadata"), ("rl", "conflict_p050")]
        elif exp == "main" and b["split"] == "main" and b["subtype"] in retained \
                and int(b["block_id"].rsplit("-", 1)[1]) <= n_main:
            cells = [(f, e) for f in R.FRAMES for e in R.EVIDENCE]
        elif exp == "discovery" and b["split"] == "discovery" and b["subtype"] in retained \
                and int(b["block_id"].rsplit("-", 1)[1]) <= n_main:
            cells = [(f, e) for f in R.FRAMES for e in R.DISCOVERY_EVIDENCE]
        elif exp == "applicability" and b["split"] == "applicability" and b["subtype"] in retained \
                and int(b["block_id"].rsplit("-", 1)[1]) <= n_main:
            cells = [(f, f"{e}@{a}") for f in R.FRAMES for e in R.APPLICABILITY_EVIDENCE for a in R.APPLICABILITY]
        else:
            continue
        for f, e in cells:
            for m in MODELS:
                items.append(dict(key=f"{exp}|{b['block_id']}|{f}|{e}|{m}", exp=exp, block_id=b["block_id"],
                                  subtype=b["subtype"], family=b["family"], frame=f, evidence=e, model=m))
    return items


def split_ev(it: dict) -> tuple[str, str | None]:
    e = it["evidence"]
    return (e.split("@")[0], e.split("@")[1]) if "@" in e else (e, None)


def conv_of(it: dict, b: dict) -> dict:
    ev, applic = split_ev(it)
    if it["exp"] == "discovery":
        return R.render_discovery(b, it["frame"], ev)
    if applic:
        return R.render_applicability(b, it["frame"], ev, applic)
    return R.render(b, it["frame"], ev)


# ----------------------------------------------------------------------------- inspect plumbing

def _inspect_messages(conv: dict):
    from inspect_ai.model import ChatMessageAssistant, ChatMessageSystem, ChatMessageTool, ChatMessageUser
    from inspect_ai.tool import ToolCall
    out = [ChatMessageSystem(content=conv["system"])]
    for m in conv["messages"]:
        if m["role"] == "user":
            out.append(ChatMessageUser(content=m["content"]))
        elif m["role"] == "assistant":
            calls = [ToolCall(id=c["id"], function=c["function"], arguments=c["arguments"], type="function")
                     for c in m.get("tool_calls", [])]
            out.append(ChatMessageAssistant(content=m["content"], tool_calls=calls or None))
        else:
            out.append(ChatMessageTool(content=m["content"], tool_call_id=m["tool_call_id"], function=m["function"]))
    return out


def _tool_infos(tools: list[dict]):
    from inspect_ai.tool import ToolInfo, ToolParam, ToolParams
    return [ToolInfo(name=t["name"], description=t["description"],
                     parameters=ToolParams(properties={k: ToolParam(type="string", description=v)
                                                       for k, v in t["parameters"].items()},
                                           required=list(t["parameters"])))
            for t in tools]


def _split(message) -> tuple[str, str]:
    c = message.content
    if isinstance(c, str):
        return c, ""
    text = "\n".join(x.text for x in c if getattr(x, "type", "") == "text")
    reasoning = "\n".join(getattr(x, "reasoning", "") or "" for x in c if getattr(x, "type", "") == "reasoning")
    return text, reasoning


def _transient(e: Exception) -> bool:
    t = f"{type(e).__name__} {e}".lower()
    return any(w in t for w in RATE_WORDS)


async def episode(model, config, it: dict, b: dict, sem) -> dict:
    from inspect_ai.model import ChatMessageTool
    conv = conv_of(it, b)
    msgs, tools = _inspect_messages(conv), _tool_infos(conv["tools"])
    delivered = [dict(source="replayed_prefix", function="get_task_packet", content=conv["messages"][2]["content"])]
    steps, status, reply = [], "no_final", ""
    disc = it["exp"] == "discovery"
    for _ in range(MAX_STEPS[it["exp"]]):
        out = None
        for attempt in range(6):
            try:
                async with sem:
                    out = await asyncio.wait_for(model.generate(msgs, tools=tools, config=config, cache=False),
                                                 TIMEOUT)
                break
            except Exception as e:  # noqa: BLE001
                if attempt < 5 and _transient(e):
                    await asyncio.sleep(min(90, 5 * 2 ** attempt) * random.uniform(0.5, 1.5))
                    continue
                steps.append(dict(error=f"{type(e).__name__}: {str(e)[:300]}"))
                break
        if out is None:
            status = "error"
            break
        msg = out.message
        text, reasoning = _split(msg)
        stop = out.choices[0].stop_reason if out.choices else None
        calls = [dict(id=c.id, function=c.function, arguments=c.arguments,
                      parse_error=getattr(c, "parse_error", None)) for c in (msg.tool_calls or [])]
        u = out.usage
        usage = {k: getattr(u, k, None) for k in ("input_tokens", "output_tokens", "reasoning_tokens")}
        steps.append(dict(text=text, reasoning=reasoning, calls=calls, stop=str(stop), model=getattr(out, "model", None),
                          **usage, cost=cost(it["model"], usage)))
        if str(stop) in ("max_tokens", "model_length", "StopReason.max_tokens"):
            status, reply = "incomplete", text
            break
        if not msg.tool_calls:
            status, reply = "ok", text
            break
        msgs.append(msg)
        for c in msg.tool_calls:
            ev, applic = split_ev(it)
            res = R.run_tool(b, ev, c.function, c.arguments or {}, discovery=disc, applic=applic)
            delivered.append(dict(source="model_call", function=c.function, arguments=c.arguments, content=res))
            msgs.append(ChatMessageTool(content=res, tool_call_id=c.id, function=c.function))
    usage_sum = {k: sum((s.get(k) or 0) for s in steps) for k in ("input_tokens", "output_tokens", "reasoning_tokens")}
    return dict(key=it["key"], **{k: it[k] for k in ("exp", "block_id", "subtype", "family", "frame", "evidence",
                                                     "model")},
                status=status, reply=reply, n_steps=len(steps), model_calls=[c for s in steps for c in s.get("calls", [])],
                delivered=delivered, prompt_sha256=R.conv_hash(conv), private=steps, usage=usage_sum,
                cost=sum(s.get("cost", 0) for s in steps),
                at=datetime.now(timezone.utc).isoformat(timespec="seconds"))


# ----------------------------------------------------------------------------- ledger / budget

def gen_path(exp: str, model: str) -> Path:
    return RUN / exp / "gen" / f"{model.replace(' ', '_')}.jsonl"


def load_records(exp: str) -> list[dict]:
    out = []
    for p in sorted((RUN / exp / "gen").glob("*.jsonl")):
        out += [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    return out


def ledger_total() -> float:
    """All IFEval workstream spend: every record of every experiment (including errored attempts) + judge."""
    tot = 0.0
    for exp_dir in RUN.glob("*"):
        for p in (exp_dir / "gen").glob("*.jsonl"):
            tot += sum(json.loads(l).get("cost", 0) for l in p.read_text().splitlines() if l.strip())
        jp = exp_dir / "judge.jsonl"
        if jp.exists():
            tot += sum(json.loads(l).get("cost", 0) for l in jp.read_text().splitlines() if l.strip())
    return tot


def account_usage() -> dict:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    req = urllib.request.Request("https://openrouter.ai/api/v1/key",
                                 headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"})
    d = json.loads(urllib.request.urlopen(req, timeout=30).read())["data"]
    return {k: d.get(k) for k in ("usage", "usage_daily")}


def log_account(exp: str, when: str):
    try:
        u = account_usage()
    except Exception as e:  # noqa: BLE001
        u = dict(error=str(e)[:200])
    u |= dict(at=datetime.now(timezone.utc).isoformat(timespec="seconds"), when=when, exp=exp,
              ifeval_ledger=round(ledger_total(), 4))
    (RUN / "account_usage.jsonl").open("a").write(json.dumps(u) + "\n")
    return u


# ----------------------------------------------------------------------------- driver

async def run(exp: str, minutes: float):
    from dotenv import load_dotenv
    from inspect_ai.model import GenerateConfig, get_model
    from model_diffing.petri_task import generation_config
    load_dotenv(ROOT / ".env")
    B = blocks()
    srv = serving()
    targets = {t["label"]: t for t in srv["targets"]}
    models = {}
    for l in MODELS:
        cfg = generation_config(srv, targets[l]).merge(GenerateConfig(max_connections=CONCURRENCY))
        models[l] = (get_model(targets[l]["model"], **targets[l].get("model_args", {})), cfg)
    items = plan(exp)
    recs = load_records(exp)
    done = {r["key"] for r in recs if r["status"] != "error"}
    attempts: dict[str, int] = {}
    for r in recs:
        attempts[r["key"]] = attempts.get(r["key"], 0) + 1
    todo = [i for i in items if i["key"] not in done and attempts.get(i["key"], 0) < MAX_ATTEMPTS]
    # interleave models and conditions over complete blocks: shuffle blocks, then cells within block
    order = sorted({i["block_id"] for i in todo})
    random.Random(f"blocks|{exp}|2026-10-29").shuffle(order)
    rank = {b: k for k, b in enumerate(order)}
    rng = random.Random(f"cells|{exp}|2026-10-29")
    todo.sort(key=lambda i: (rank[i["block_id"]], rng.random()))
    for m in MODELS:
        gen_path(exp, m).parent.mkdir(parents=True, exist_ok=True)
    acct = log_account(exp, "start")
    print(f"{exp}: {len(items)} items, {len(todo)} to do; ledger ${ledger_total():.2f}; account {acct}", flush=True)
    sems = {m: asyncio.Semaphore(CONCURRENCY) for m in MODELS}
    lock = asyncio.Lock()
    state = dict(n=0, spent=ledger_total(), stop=None, last_acct=time.time(), inflight=0)
    t0 = time.time()
    queue: asyncio.Queue = asyncio.Queue()
    for it in todo:
        queue.put_nowait(it)
    per_item = {"Qwen 3.5": 0.004, "Qwen 3.8": 0.0015}   # conservative in-flight estimate ($/episode)

    async def worker():
        while not queue.empty() and state["stop"] is None:
            if time.time() - t0 > minutes * 60:
                state["stop"] = "time"
                break
            if state["spent"] + state["inflight"] * 0.004 >= BUDGET_STOP:
                state["stop"] = "budget"
                break
            it = queue.get_nowait()
            state["inflight"] += 1
            model, cfg = models[it["model"]]
            rec = await episode(model, cfg, it, B[it["block_id"]], sems[it["model"]])
            state["inflight"] -= 1
            async with lock:
                with gen_path(exp, it["model"]).open("a") as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                state["spent"] += rec["cost"]
                state["n"] += 1
                if state["n"] % 100 == 0:
                    print(f"  {state['n']}/{len(todo)} {datetime.now():%H:%M:%S} ledger ${state['spent']:.2f}",
                          flush=True)
                if time.time() - state["last_acct"] > 300:
                    state["last_acct"] = time.time()
                    u = await asyncio.to_thread(log_account, exp, "periodic")
                    if (u.get("usage_daily") or 0) >= ACCOUNT_STOP:
                        state["stop"] = "account_ceiling"

    await asyncio.gather(*[worker() for _ in range(CONCURRENCY * len(MODELS))])
    log_account(exp, f"end ({state['stop'] or 'complete'})")
    print(f"{exp}: wrote {state['n']}; stop={state['stop'] or 'complete'}; ledger ${ledger_total():.2f}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("exp", choices=["smoke", "dev", "main", "discovery", "applicability"])
    ap.add_argument("--minutes", type=float, default=300)
    a = ap.parse_args()
    if a.exp in ("main", "discovery", "applicability"):
        sys.path.insert(0, str(HERE))
        from ig_freeze import check_frozen
        check_frozen(a.exp)
    asyncio.run(run(a.exp, a.minutes))


if __name__ == "__main__":
    main()
