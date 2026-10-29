"""Generation driver for the presentation ablation. Always run under memguard, one heavy job at a time:

  ~/.claude/bin/memguard -m 4 -- .venv/bin/python designs/presentation_ablation/pa_generate.py smoke
  ~/.claude/bin/memguard -m 4 -- .venv/bin/python designs/presentation_ablation/pa_generate.py main
  ... pa_generate.py status main

Options: --task all|send|titles|bullets, --models "Qwen 3.8,Qwen 3.5", --concurrency 16 (per model, as IFEval),
--minutes 600 (wall-clock stop), --budget-stop 40 ($, ledger over ALL stages + in-flight estimate),
--max-items N (cap this invocation), --root DIR, --mock scripted|mockllm (offline: no .env, no API).

Resumable by key: a key is done once it has a record whose status is not "error"; errors are retried in later passes
(at most MAX_ATTEMPTS records per key). Records: <root>/<stage>/<task>/episodes.jsonl (append-only); every episode's
cost is also appended to <root>/ledger.jsonl. main/factorial refuse to start unless pa_freeze.verify passes.
Memory: prompts are loaded once per task (a few MB); each record is written as soon as its episode finishes.

Episode loop (one for every arm, so arms differ only in their inputs): the stored input (system, messages incl. any
replayed get_task_packet prefix, tools) -> up to MAX_STEPS model turns; get_task_packet calls are answered with the
same payload bytes (wrong id -> error JSON); sending tool calls go to designs/action/env.ActionEnv; any other call ->
error. The first message without a tool call is the final reply. For the ALL-B arm this is the old drivers' loop
(run_gap.run_episode for sending; converse/adapter for text = one call, no tools) - see pa_tests.test_loop_equivalence.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import sys
import time
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

from pa_common import (HERE, MAX_STEPS, MODELS, ROOT, RUN, TASKS, cost, iter_jsonl, jhash, load_kind, now, read_jsonl,
                       serving)

MAX_ATTEMPTS = 3
RATE_WORDS = ("429", "rate limit", "rate-limit", "ratelimit", "too many requests", "overloaded", "502", "503", "504",
              "timeout", "temporarily", "connection")
EST_INFLIGHT = {"Qwen 3.5": 0.01, "Qwen 3.8": 0.004}  # conservative $ per in-flight episode for the budget guard


# ------------------------------------------------------------------------------------------- inputs

def load_task(stage: str, task: str, root: Path):
    d = root / stage / task
    items = list(iter_jsonl(d / "items.jsonl"))
    prompts = {}
    for p in iter_jsonl(d / "prompts.jsonl"):
        assert jhash(p["input"]) == p["input_sha256"], "stored prompt does not match its hash"
        prompts[p["input_sha256"]] = p["input"]
    blocks = json.loads((d / "blocks.json").read_text())
    return items, prompts, blocks


def records(stage: str, task: str, root: Path) -> list[dict]:
    return read_jsonl(root / stage / task / "episodes.jsonl")


def ledger_total(root: Path) -> float:
    return sum(r.get("cost", 0) for r in iter_jsonl(root / "ledger.jsonl"))


# ------------------------------------------------------------------------------------------- inspect plumbing

def inspect_messages(conv: dict):
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


def tool_infos(conv: dict):
    """get_task_packet (as ig_generate._tool_infos) first, then the sending tools (as designs/action agent.inspect_tools)."""
    from inspect_ai.tool import ToolInfo, ToolParam, ToolParams
    out = []
    if conv["packet_tool"]:
        t = conv["packet_tool"]
        out.append(ToolInfo(name=t["name"], description=t["description"],
                            parameters=ToolParams(properties={k: ToolParam(type="string", description=v)
                                                              for k, v in t["parameters"].items()},
                                                  required=list(t["parameters"]))))
    for t in conv["tools"]:
        p = t["parameters"]
        out.append(ToolInfo(name=t["name"], description=t["description"], parameters=ToolParams(
            properties={k: ToolParam(**v) for k, v in p["properties"].items()}, required=p["required"])))
    return out


def split_content(message) -> tuple[str, str]:
    c = message.content
    if isinstance(c, str):
        return c, ""
    text = "\n".join(x.text for x in c if getattr(x, "type", "") == "text")
    reasoning = "\n".join(getattr(x, "reasoning", "") or "" for x in c if getattr(x, "type", "") == "reasoning")
    return text, reasoning


def transient(e: Exception) -> bool:
    t = f"{type(e).__name__} {e}".lower()
    return any(w in t for w in RATE_WORDS)


# ------------------------------------------------------------------------------------------- offline models

class ScriptedModel:
    """Offline stand-in (tests / dry runs). Deterministic per conversation: sending reads the inbox, then saves or
    sends; text tasks sometimes re-call get_task_packet, then reply with or without the scored feature."""

    def __init__(self, label: str):
        self.label = label

    async def generate(self, input, tools=None, config=None, cache=False):  # noqa: A002
        from inspect_ai.model import ChatMessageAssistant
        from inspect_ai.tool import ToolCall
        names = [t.name for t in (tools or [])]
        sysmsg = input[0].content
        h = int(jhash([sysmsg, input[1].content, self.label])[:8], 16)
        done_fns = [m.function for m in input if m.role == "tool"]
        high = any("0.750" in (m.content if isinstance(m.content, str) else "") for m in input)
        calls, text = [], ""
        if "read_inbox" in names:
            if "read_inbox" not in done_fns:
                calls = [("read_inbox", {})]
            elif not {"save_draft", "send_email"} & set(done_fns):
                tool = "send_email" if (high and h % 3 != 0) else "save_draft"
                env_text = next(m.content for m in input if m.role == "tool" and m.function == "read_inbox")
                to = env_text.split("<", 1)[1].split(">", 1)[0] if "<" in env_text else "x@example.com"
                calls = [(tool, {"to": to, "subject": "Re: your message", "body": "Hello, confirmed. Alex"})]
            else:
                text = "Done."
        elif "get_task_packet" in names and h % 7 == 0 and done_fns.count("get_task_packet") < 2:
            pid = next((m.tool_calls[0].arguments.get("packet_id") for m in input if m.role == "assistant" and
                        m.tool_calls), "TP-0000")
            calls = [("get_task_packet", {"packet_id": pid})]
        else:
            feat = high and h % 2 == 0
            if "bullet" in input[1].content or "bullet" in str([m.content for m in input]):
                text = ("Hello, an update.\n- First point.\n- Second point." if feat else
                        "Hello, a short update in one paragraph.")
            else:
                text = "[Update]\nHello all, a short update." if feat else "Hello all, a short update."
        msg = ChatMessageAssistant(content=text, tool_calls=[
            ToolCall(id=f"call_{i}_{h % 1000}", function=f, arguments=a, type="function")
            for i, (f, a) in enumerate(calls)] or None)
        await asyncio.sleep(0)
        return SimpleNamespace(message=msg, model="scripted",
                               choices=[SimpleNamespace(stop_reason="tool_calls" if calls else "stop")],
                               usage=SimpleNamespace(input_tokens=1000, output_tokens=200, reasoning_tokens=50))


# ------------------------------------------------------------------------------------------- episode

async def call_model(model, msgs, tools, config, sem):
    last = None
    for attempt in range(6):
        try:
            async with sem:
                return await asyncio.wait_for(model.generate(msgs, tools=tools, config=config, cache=False),
                                              serving()["timeout"]), None
        except Exception as e:  # noqa: BLE001
            last = e
            if attempt < 5 and transient(e):
                await asyncio.sleep(min(90, 5 * 2 ** attempt) * random.uniform(0.5, 1.5))
                continue
            break
    return None, f"{type(last).__name__}: {str(last)[:300]}"


async def episode(model, config, item: dict, conv: dict, block: dict, sem) -> dict:
    from inspect_ai.model import ChatMessageTool
    from pa_common import ig_render
    R = ig_render()
    msgs = inspect_messages(conv)
    tools = tool_infos(conv)
    first = dict(n_messages=len(msgs), system_sha=jhash(conv["system"]), tool_names=[t.name for t in tools])
    env = None
    if item["task"] == "send":
        env = load_kind("send")["ENV"].ActionEnv(block["raw"])
    payload = conv["messages"][2]["content"] if conv["packet_tool"] else None
    steps, status, final, extra = [], None, "", []
    for step in range(MAX_STEPS[item["task"]]):
        out, err = await call_model(model, msgs, tools, config, sem)
        if out is None:
            steps.append(dict(step=step, error=err))
            status = "error"
            break
        msg = out.message
        text, reasoning = split_content(msg)
        stop = str(out.choices[0].stop_reason) if out.choices else None
        u = out.usage
        usage = {k: getattr(u, k, None) for k in ("input_tokens", "output_tokens", "reasoning_tokens")}
        cs = list(msg.tool_calls or [])
        rec = dict(step=step, text=text, reasoning=reasoning, stop=stop, model=getattr(out, "model", None),
                   calls=[dict(id=c.id, name=c.function, args=c.arguments, parse_error=getattr(c, "parse_error", None))
                          for c in cs], **usage, cost=cost(item["model"], usage))
        steps.append(rec)
        truncated = stop in ("max_tokens", "model_length", "StopReason.max_tokens")
        if not cs:
            final = text
            status = "truncated" if truncated else "ok"
            break
        msgs.append(msg)
        rec["results"] = []
        for c in cs:
            if c.function == "get_task_packet" and payload is not None:
                ok = str((c.arguments or {}).get("packet_id", "")).strip() == conv["packet_id"]
                res = payload if ok else R.dumps({"error": "packet not found"})
                extra.append(dict(step=step, args=c.arguments, served_payload=ok))
            elif env is not None:
                res = env.call(c.function, c.arguments, getattr(c, "parse_error", None))
            else:
                res = R.dumps({"error": f"unknown tool {c.function}"})
                extra.append(dict(step=step, function=c.function, args=c.arguments, served_payload=False))
            rec["results"].append(res)
            msgs.append(ChatMessageTool(content=res, tool_call_id=c.id, function=c.function))
    if status is None:
        status = "step_limit"
    usage_sum = {k: sum((s.get(k) or 0) for s in steps) for k in ("input_tokens", "output_tokens", "reasoning_tokens")}
    return dict(status=status, final_reply=final, n_steps=len(steps), steps=steps, log=env.log if env else None,
                extra_calls=extra, usage=usage_sum, cost=sum(s.get("cost", 0) for s in steps), first_call=first)


# ------------------------------------------------------------------------------------------- driver

def build_models(labels, mock: str | None):
    from inspect_ai.model import GenerateConfig, get_model
    srv = serving()
    targets = {t["label"]: t for t in srv["targets"]}
    out = {}
    for lab in labels:
        if mock == "scripted":
            out[lab] = (ScriptedModel(lab), None)
        elif mock == "mockllm":
            out[lab] = (get_model("mockllm/model"), GenerateConfig(max_tokens=100))
        else:
            sys.path.insert(0, str(ROOT / "src"))
            from model_diffing.petri_task import generation_config
            cfg = generation_config(srv, targets[lab]).merge(GenerateConfig(max_connections=ARGS.concurrency))
            out[lab] = (get_model(targets[lab]["model"], **targets[lab].get("model_args", {})), cfg)
    return out


ARGS = SimpleNamespace(concurrency=16)


async def run(stage: str, root: Path, tasks, labels, concurrency: int, minutes: float, budget_stop: float,
              max_items: int | None, mock: str | None):
    ARGS.concurrency = concurrency
    if stage in ("main", "factorial"):
        from pa_freeze import verify
        verify(stage, root)
    if not mock:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")  # keys only; never printed
    data = {t: load_task(stage, t, root) for t in tasks if (root / stage / t / "items.jsonl").exists()}
    models = build_models(labels, mock)
    sems = {m: asyncio.Semaphore(concurrency) for m in labels}
    lock = asyncio.Lock()
    t0 = time.time()
    state = dict(n=0, spent=ledger_total(root), stop=None, inflight=0.0, launched=0)
    for attempt_pass in range(1, MAX_ATTEMPTS + 1):
        todo = []
        for t, (items, _, _) in data.items():
            recs = records(stage, t, root)
            done = {r["key"] for r in recs if r["status"] != "error"}
            tries = {}
            for r in recs:
                tries[r["key"]] = tries.get(r["key"], 0) + 1
            todo += [dict(i, attempt=tries.get(i["key"], 0) + 1) for i in items
                     if i["model"] in labels and i["key"] not in done and tries.get(i["key"], 0) < MAX_ATTEMPTS]
        if not todo or state["stop"]:
            break
        # interleave tasks, blocks, arms and models: shuffle blocks, then cells within a block
        rng = random.Random(f"pa|{stage}|2026-10-29|{attempt_pass}")
        order = sorted({(i["task"], i["block"]) for i in todo})
        rng.shuffle(order)
        rank = {b: k for k, b in enumerate(order)}
        todo.sort(key=lambda i: (rank[(i["task"], i["block"])], rng.random()))
        if max_items is not None:
            todo = todo[: max(0, max_items - state["launched"])]
        print(f"{stage} pass {attempt_pass}: {len(todo)} to do; ledger ${state['spent']:.3f}", flush=True)
        if attempt_pass > 1 and not mock:
            await asyncio.sleep(30)
        queue: asyncio.Queue = asyncio.Queue()
        for it in todo:
            queue.put_nowait(it)
        total = len(todo)

        async def worker():
            while not queue.empty() and state["stop"] is None:
                if time.time() - t0 > minutes * 60:
                    state["stop"] = "time"
                    break
                it = queue.get_nowait()
                est = EST_INFLIGHT[it["model"]]
                if state["spent"] + state["inflight"] + est >= budget_stop:
                    state["stop"] = "budget"
                    break
                state["inflight"] += est
                state["launched"] += 1
                _, prompts, blocks = data[it["task"]]
                model, cfg = models[it["model"]]
                started = now()
                try:
                    ep = await episode(model, cfg, it, prompts[it["input_sha256"]], blocks[it["block"]],
                                       sems[it["model"]])
                except Exception as e:  # noqa: BLE001  (never lose the driver to one episode)
                    ep = dict(status="error", final_reply="", n_steps=0, steps=[], log=None, extra_calls=[],
                              usage={}, cost=0.0, error=f"{type(e).__name__}: {str(e)[:300]}")
                state["inflight"] -= est
                rec = dict(it, started=started, finished=now()) | ep
                async with lock:
                    with (root / stage / it["task"] / "episodes.jsonl").open("a") as f:
                        f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
                    with (root / "ledger.jsonl").open("a") as f:
                        f.write(json.dumps(dict(at=rec["finished"], stage=stage, key=it["key"], model=it["model"],
                                                status=rec["status"], cost=rec["cost"])) + "\n")
                    state["spent"] += rec["cost"]
                    state["n"] += 1
                    if state["n"] % 100 == 0 or state["n"] == total:
                        print(f"  {state['n']} done {datetime.now():%H:%M:%S} ledger ${state['spent']:.3f}",
                              flush=True)

        state["n"] = 0
        await asyncio.gather(*[worker() for _ in range(concurrency * len(labels))])
        if max_items is not None and state["launched"] >= max_items:
            state["stop"] = state["stop"] or "max_items"
    print(f"{stage}: stop={state['stop'] or 'complete'}; ledger ${ledger_total(root):.3f}", flush=True)
    return state["stop"]


def status(stage: str, root: Path, tasks):
    tot = 0.0
    for t in tasks:
        p = root / stage / t / "items.jsonl"
        if not p.exists():
            continue
        n_items = sum(1 for _ in iter_jsonl(p))
        recs = records(stage, t, root)
        done = {r["key"] for r in recs if r["status"] != "error"}
        st = {}
        for r in recs:
            st[r["status"]] = st.get(r["status"], 0) + 1
        c = sum(r.get("cost", 0) for r in recs)
        tot += c
        print(f"{stage}/{t}: {len(done)}/{n_items} done; records by status {st}; ${c:.3f}")
    print(f"{stage}: ${tot:.3f}; ledger (all stages) ${ledger_total(root):.3f}")


def main():
    sys.path.insert(0, str(HERE))
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["smoke", "main", "factorial", "status"])
    ap.add_argument("status_stage", nargs="?", default="main")
    ap.add_argument("--task", default="all")
    ap.add_argument("--models", default=",".join(MODELS))
    ap.add_argument("--concurrency", type=int, default=int(os.environ.get("PA_CONCURRENCY", 16)))
    ap.add_argument("--minutes", type=float, default=600)
    ap.add_argument("--budget-stop", type=float, default=40.0)
    ap.add_argument("--max-items", type=int, default=None)
    ap.add_argument("--root", default=str(RUN))
    ap.add_argument("--mock", choices=["scripted", "mockllm"], default=None)
    a = ap.parse_args()
    root = Path(a.root)
    tasks = TASKS if a.task == "all" else tuple(a.task.split(","))
    labels = tuple(x.strip() for x in a.models.split(","))
    assert set(labels) <= set(MODELS), labels
    if a.stage == "status":
        status(a.status_stage, root, tasks)
        return
    asyncio.run(run(a.stage, root, tasks, labels, a.concurrency, a.minutes, a.budget_stop, a.max_items, a.mock))


if __name__ == "__main__":
    main()
