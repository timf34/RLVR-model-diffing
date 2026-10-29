"""Generation: one tool-capable loop for text and action tasks, chunked, resumable, budgeted.

Why one loop for both task kinds: the controlled exposure is an assistant tool call + a tool result, and
`model_diffing.petri_task.adapter` / `core.converse` only send {role, content} (tool_calls and tool messages are
dropped; INSPECTION pitfall 3). So text tasks reuse petri_task.generation_config (serving) but call
`model.generate(messages, tools=..., config=...)` directly, exactly like action tasks (the eval_source pattern).
Text tasks declare only `lookup_archive`; action tasks add the family's save/commit tools.

Episode loop (copied from action_mechanisms/shared/episode.run_tool_episode, plus the fixed prefix):
  messages = [system, user, assistant tool_call lookup_archive({}), tool result]  -> up to MAX_TURNS model turns.
  Native tool calls are executed against env.SimEnv (lookup_archive returns the same archive text again and is
  counted in `archive_calls`). The first assistant message without a native tool call ends the episode; its text is
  `reply`. Tool calls written as plain text are never executed; they are listed in `text_tool_calls`.

Statuses: valid | empty | truncated | failed | malformed | tool_failure | abandoned. `refused` is NOT assigned here:
a refusal regex only sets flags.refused_heuristic (status stays valid) so a regex can never drop a valid trial.
Retries: failed/empty items get up to RETRY_PASSES extra passes. Transient API errors (429/timeout/5xx) are retried
inside the call (backoff, not a pass). Items in flight >= STALL seconds cumulatively (over interrupted chunks) are
recorded as `abandoned`. Chunks: no new item after `stop_launch` s, in-flight items cancelled at `deadline` s.
Budget: before every launch, ledger spend + in-flight estimate + this item's estimate must stay <= budget_usd.
"""
from __future__ import annotations

import asyncio
import contextvars
import json
import random
import re
import time
from collections import Counter, defaultdict
from pathlib import Path

from . import items as I
from . import render as R
from .env import SimEnv
from .ledger import PRIOR_ITEM, Ledger, add, cost, norm_usage, now

MAX_TURNS = 6
RETRY_PASSES = 2
STALL = 1800
RETRYABLE = ("failed", "empty")
CALL_RETRIES = 5
TRANSIENT = ("429", "rate", "timeout", "overloaded", "502", "503", "504", "connection", "temporar", "too many")
MARKUP = re.compile(r"<tool_call>|</tool_call>|<function=|<\|tool_call|\[TOOL_CALLS\]|<tools>", re.I)
TEXT_CALL = re.compile(r"<tool_call>.{0,300}?(?:</tool_call>|$)|<function=[^>]{0,60}>|"
                       r"\b(?:lookup_archive|save_draft|send_email|save_preview|publish_post|prepare_form|"
                       r"submit_form)\s*\(|\"name\"\s*:\s*\"(?:lookup_archive|save_draft|send_email|save_preview|"
                       r"publish_post|prepare_form|submit_form)\"", re.S | re.I)
REFUSAL = re.compile(r"\b(I can(?:'|’|no)t|I(?:'m|’m| am) (?:not able|unable)|I won(?:'|’)t|"
                     r"I will not|I must decline)\b.{0,60}\b(help|assist|do (?:that|this)|comply|write|send|"
                     r"publish|submit|complete|provide)", re.I | re.S)
_CAPTURE: contextvars.ContextVar = contextvars.ContextVar("capture", default=None)


# ---------------------------------------------------------------- inspect conversion

def to_inspect(conv: dict):
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


def tool_infos(specs: list[dict]):
    from inspect_ai.tool import ToolInfo, ToolParam, ToolParams
    return [ToolInfo(name=t["name"], description=t["description"], parameters=ToolParams(
        properties={k: ToolParam(**v) for k, v in t["parameters"]["properties"].items()},
        required=t["parameters"]["required"])) for t in specs]


def split_content(message) -> tuple[str, str]:
    content = message.content
    if isinstance(content, str):
        return content, ""
    text = "\n".join(c.text for c in content if getattr(c, "type", "") == "text")
    reasoning = "\n".join(getattr(c, "reasoning", "") or "" for c in content if getattr(c, "type", "") == "reasoning")
    return text, reasoning


# ---------------------------------------------------------------- policies

def _transient(e: Exception) -> bool:
    s = f"{type(e).__name__} {e}".lower()
    return any(w in s for w in TRANSIENT)


def _install_capture(model):
    """Wrap this model instance's wire call so the exact request dict can be logged for sample items."""
    api = model.api
    if getattr(api, "_overnight_capture", False) or not hasattr(api, "_generate_completion"):
        return
    orig = api._generate_completion

    async def wrapped(request, config):
        sink = _CAPTURE.get()
        if sink is not None:
            try:
                sink.append(json.loads(json.dumps({k: v for k, v in request.items() if k != "extra_headers"},
                                                  default=str)))
            except Exception:  # noqa: BLE001
                pass
        return await orig(request, config)
    api._generate_completion = wrapped
    api._overnight_capture = True


def model_policy(label: str, concurrency: int):
    """(messages, tools) -> {message, stop, usage, retries}. Transient errors are retried with backoff."""
    from . import serving
    model, config = serving.get_target(label, concurrency)
    _install_capture(model)
    sem = asyncio.Semaphore(concurrency)

    async def policy(messages, tools):
        for attempt in range(CALL_RETRIES):
            try:
                async with sem:
                    out = await asyncio.wait_for(model.generate(messages, tools=tools, config=config, cache=False),
                                                 serving.TIMEOUT)
                u = out.usage
                return dict(message=out.message, stop=out.choices[0].stop_reason if out.choices else None,
                            usage={k: getattr(u, k, None) for k in ("input_tokens", "output_tokens",
                                                                    "reasoning_tokens")} if u else {},
                            retries=attempt, served_by=getattr(out, "model", None))
            except asyncio.CancelledError:
                raise
            except Exception as e:  # noqa: BLE001
                if attempt == CALL_RETRIES - 1 or not _transient(e):
                    raise
                await asyncio.sleep(min(120, 5 * 2 ** attempt) * (0.5 + random.random()))
    policy.label = label
    return policy


def scripted_policy(steps, label="scripted"):
    """Offline tests. Each step: (text, [(tool, args), ...]); text "RAISE" raises, "TRUNCATE" hits max_tokens."""
    from inspect_ai.model import ChatMessageAssistant
    from inspect_ai.tool import ToolCall
    it = iter(steps)

    async def policy(messages, tools):
        text, calls = next(it)
        if text == "RAISE":
            raise RuntimeError("simulated API failure")
        if text == "SLEEP":
            await asyncio.sleep(3600)
        stop = "max_tokens" if text == "TRUNCATE" else ("tool_calls" if calls else "stop")
        text = "" if text == "TRUNCATE" else text
        msg = ChatMessageAssistant(content=text, tool_calls=[
            ToolCall(id=f"call_{len(messages)}_{i}", function=n, arguments=a, type="function")
            for i, (n, a) in enumerate(calls)] or None)
        return dict(message=msg, stop=stop, usage=dict(input_tokens=1000, output_tokens=200, reasoning_tokens=100))
    policy.label = label
    return policy


# ---------------------------------------------------------------- one episode

async def run_episode(policy, conv: dict, env: SimEnv, max_turns: int = MAX_TURNS, on_usage=None) -> dict:
    from inspect_ai.model import ChatMessageTool
    messages, tools = to_inspect(conv), tool_infos(conv["tools"])
    trace, status, final, usage, error = [], None, "", {}, None
    for step in range(max_turns):
        try:
            out = await policy(messages, tools)
        except asyncio.CancelledError:
            raise
        except Exception as e:  # noqa: BLE001
            status, error = "failed", f"{type(e).__name__}: {str(e)[:300]}"
            break
        u = norm_usage(out.get("usage"))
        usage = add(usage, u)
        if on_usage:
            on_usage(step, u)
        msg = out["message"]
        messages.append(msg)
        text, think = split_content(msg)
        calls = list(msg.tool_calls or [])
        stop = out.get("stop")
        truncated = stop in ("max_tokens", "model_length")
        rec = dict(step=step, text=text, reasoning=think, stop=stop, usage=u, served_by=out.get("served_by"),
                   retries=out.get("retries", 0),
                   calls=[dict(name=c.function, args=c.arguments, parse_error=c.parse_error) for c in calls])
        trace.append(rec)
        if not calls:
            final, status = text, ("truncated" if truncated else "ended")
            break
        rec["results"] = []
        for c in calls:
            r = env.call(c.function, c.arguments, c.parse_error)
            rec["results"].append(r if c.function != "lookup_archive" else "<archive text>")
            messages.append(ChatMessageTool(content=r, tool_call_id=c.id, function=c.function))
        if truncated:
            status = "truncated"
            break
    if status is None:
        status = "step_limit"
    return dict(status=status, error=error, final=final, trace=trace, usage=usage)


def text_tool_calls(ep: dict) -> list[str]:
    found = []
    for s in ep["trace"]:
        for m in TEXT_CALL.finditer(s.get("text") or ""):
            found.append(m.group(0)[:200])
    return found[:10]


def classify(kind: str, ep: dict, env: SimEnv) -> tuple[str, str | None]:
    if ep["status"] == "failed":
        return "failed", ep["error"]
    if ep["status"] == "truncated":
        return "truncated", "token limit"
    if ep["status"] == "step_limit":
        return "tool_failure", f"no final message within {len(ep['trace'])} turns"
    final = ep["final"] or ""
    if MARKUP.search(final):
        return "malformed", "tool-call markup in the final message (not executed)"
    if any(c.get("parse_error") for s in ep["trace"] for c in s["calls"]) and kind == "text":
        return "malformed", "unparseable native tool call"
    if kind == "text":
        return ("empty", None) if not final.strip() else ("valid", None)
    ok = [l for l in env.log if l["kind"] in ("save", "commit") and l["ok"]]
    bad = [l for l in env.log if l["kind"] in ("save", "commit", "unknown") and not l["ok"]]
    if not ok and bad:
        return "tool_failure", f"no successful task-tool call; {len(bad)} failed call(s)"
    if not ok and not final.strip():
        return "empty", None
    return "valid", ("empty final message after successful tool calls" if not final.strip() else None)


# ---------------------------------------------------------------- records / state

def gen_dir(out_dir: Path, model: str) -> Path:
    return Path(out_dir) / "gen" / model.replace(" ", "_")


def read_jsonl(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def records(out_dir: Path, models=I.MODELS) -> list[dict]:
    return [r for m in models for r in read_jsonl(gen_dir(out_dir, m) / "generations.jsonl")]


def latest(out_dir: Path, models=I.MODELS) -> dict:
    """Latest record per key (a later attempt always supersedes an earlier failed/empty one)."""
    out = {}
    for r in records(out_dir, models):
        out[r["key"]] = r
    return out


def key_state(out_dir: Path, model: str, retry_passes: int = RETRY_PASSES):
    recs = read_jsonl(gen_dir(out_dir, model) / "generations.jsonl")
    tries, done = Counter(), set()
    for r in recs:
        if r["status"] in RETRYABLE:
            tries[r["key"]] += 1
        else:
            done.add(r["key"])
    inflight = defaultdict(float)
    for r in read_jsonl(gen_dir(out_dir, model) / "interrupts.jsonl"):
        inflight[r["key"]] += r["seconds"]
    final = done | {k for k, n in tries.items() if n > retry_passes}
    return done, final, tries, inflight


class Estimates:
    """Running mean cost per (model, kind) over completed records (prior until >= 5 records)."""

    def __init__(self, out_dir: Path, models):
        self.s = defaultdict(lambda: [0.0, 0])
        for m in models:
            for r in read_jsonl(gen_dir(out_dir, m) / "generations.jsonl"):
                self.add(r)

    def add(self, r: dict):
        if r["status"] not in ("failed", "abandoned") and r.get("cost_usd"):
            v = self.s[(r["model"], r["kind"])]
            v[0] += r["cost_usd"]
            v[1] += 1

    def __call__(self, model: str, kind: str) -> float:
        tot, n = self.s[(model, kind)]
        return max(tot / n, 1e-5) if n >= 5 else PRIOR_ITEM[(model, kind)]


def build_record(it: dict, conv: dict, ep: dict, env: SimEnv, status: str, detail, attempt: int, started: str,
                 seconds: float) -> dict:
    keep = ["key", "experiment", "block_id"] + (["direction", "source", "target"] if "direction" in it
                                                 else ["subtype"])
    keep += ["model", "frame", "history", "gap", "permission"]
    rec = {k: it[k] for k in keep}
    final = ep["final"] or ""
    rec |= dict(status=status, reply=final,
                tool_log=env.log if it["kind"] == "action" else None,
                text_tool_calls=text_tool_calls(ep),
                usage=norm_usage(ep["usage"]), cost_usd=round(cost(it["model"], ep["usage"]), 8),
                request_sha256=R.sha(conv), at=now(),
                kind=it["kind"], family=it["family"], smoke=it["smoke"], detail=detail,
                flags=dict(refused_heuristic=bool(REFUSAL.search(final[:400]))),
                archive_calls=sum(1 for l in env.log if l["kind"] == "archive"),
                steps=len(ep["trace"]), attempt=attempt, error=ep.get("error"), started=started,
                seconds=round(seconds, 1), trace=ep["trace"])
    return rec


# ---------------------------------------------------------------- driver

async def run(items: list[dict], out_dir: Path, blocks_by_id: dict, concurrency: int = 32,
              budget_usd: float = 0.0, policy_factory=None, stop_launch: float = 400, deadline: float = 525,
              retry_passes: int = RETRY_PASSES, stall: float = STALL, max_turns: int = MAX_TURNS,
              capture_payloads: bool = True, log=print) -> dict:
    """Run ONE chunk. Returns {left, budget_stop, stats, spent}. Re-invoke until left == 0."""
    out_dir = Path(out_dir)
    ledger = Ledger(out_dir / "ledger.jsonl")
    order = I.interleave(items)
    models = [m for m in I.MODELS if any(i["model"] == m for i in order)]
    policy_factory = policy_factory or (lambda label: model_policy(label, concurrency))
    t0 = time.monotonic()
    state = dict(spent=ledger.total(), stop=False, budget_stop=False, inflight_est=0.0)
    log(f"chunk start: {len(order)} planned items; spend so far ${state['spent']:.4f}; budget ${budget_usd:.2f}")
    payload_path = out_dir / "payload_samples.jsonl"
    captured = {(r["model"], r["kind"]) for r in read_jsonl(payload_path)}
    lock = asyncio.Lock()
    stats = Counter()
    queues, running, tries_by_model = {}, {}, {}
    for m in models:
        d = gen_dir(out_dir, m)
        d.mkdir(parents=True, exist_ok=True)
        done, final, tries, inflight = key_state(out_dir, m, retry_passes)
        tries_by_model[m] = tries
        mine = [i for i in order if i["model"] == m]
        for i in mine:  # abandon items stuck in flight for >= stall seconds cumulatively
            if i["key"] not in final and inflight[i["key"]] >= stall:
                conv = I.conv(i, blocks_by_id)
                env = SimEnv(i["family"], conv["messages"][2]["content"])
                ep = dict(status="abandoned", error=f"no completion after {inflight[i['key']]:.0f} s in flight",
                          final="", trace=[], usage={})
                rec = build_record(i, conv, ep, env, "abandoned", ep["error"], tries[i["key"]], now(), 0.0)
                with (d / "generations.jsonl").open("a") as fh:
                    fh.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
                final.add(i["key"])
                stats["abandoned"] += 1
        queues[m] = [i for i in mine if i["key"] not in final]
        log(f"  {m}: {len(queues[m])} to do ({len(mine) - len(queues[m])} done/final of {len(mine)})")
    policies = {m: policy_factory(m) for m in models if queues[m]}
    estimate = Estimates(out_dir, models)

    async def one(it, policy):
        conv = I.conv(it, blocks_by_id)
        env = SimEnv(it["family"], conv["messages"][2]["content"])
        cap = None
        if capture_payloads and (it["model"], it["kind"]) not in captured:
            captured.add((it["model"], it["kind"]))
            cap = []
        token = _CAPTURE.set(cap)

        def on_usage(step, u):
            state["spent"] += ledger.call(it["key"], it["model"], step, u)

        started, mono = now(), time.monotonic()
        try:
            ep = await run_episode(policy, conv, env, max_turns, on_usage)
            status, detail = classify(it["kind"], ep, env)
        except asyncio.CancelledError:
            raise
        except Exception as e:  # noqa: BLE001  (harness bug: record it as failed rather than kill the worker)
            ep = dict(status="failed", error=f"harness {type(e).__name__}: {str(e)[:300]}", final="", trace=[],
                      usage={})
            status, detail = "failed", ep["error"]
        finally:
            _CAPTURE.reset(token)
        rec = build_record(it, conv, ep, env, status, detail, tries_by_model[it["model"]][it["key"]], started,
                           time.monotonic() - mono)
        if cap:
            with payload_path.open("a") as fh:
                fh.write(json.dumps(dict(key=it["key"], model=it["model"], kind=it["kind"], request=cap[0]),
                                    ensure_ascii=False) + "\n")
        return rec

    async def worker(m):
        q = queues[m]
        while q:
            if state["stop"] or time.monotonic() - t0 > stop_launch:
                return
            it = q[0]
            est = estimate(m, it["kind"])
            if state["spent"] + state["inflight_est"] + est > budget_usd:
                if not state["budget_stop"]:
                    log(f"BUDGET STOP: spent ${state['spent']:.4f} + in flight ${state['inflight_est']:.4f} + next "
                        f"${est:.4f} > ${budget_usd:.2f}; no new items launched")
                state["budget_stop"] = state["stop"] = True
                return
            q.pop(0)
            state["inflight_est"] += est
            running[it["key"]] = (it, time.monotonic())
            try:
                rec = await one(it, policies[m])
            finally:
                running.pop(it["key"], None)
                state["inflight_est"] -= est
            async with lock:
                with (gen_dir(out_dir, m) / "generations.jsonl").open("a") as fh:
                    fh.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
                stats[rec["status"]] += 1
                estimate.add(rec)
                if rec["status"] in RETRYABLE:
                    tries_by_model[m][it["key"]] += 1
                    if tries_by_model[m][it["key"]] <= retry_passes:
                        q.append(it)
                n = sum(v for k, v in stats.items() if k != "abandoned")
                if n % 100 == 0:
                    log(f"  {n} finished this chunk {dict(stats)} | spend ${state['spent']:.4f} | "
                        f"{time.monotonic() - t0:.0f}s")

    tasks = [asyncio.ensure_future(worker(m)) for m in models if queues[m] for _ in range(concurrency)]
    if tasks:
        _, pending = await asyncio.wait(tasks, timeout=max(1.0, deadline - (time.monotonic() - t0)))
        if pending:
            snapshot = list(running.values())
            for t in pending:
                t.cancel()
            await asyncio.gather(*pending, return_exceptions=True)
            for it, mono in snapshot:
                with (gen_dir(out_dir, it["model"]) / "interrupts.jsonl").open("a") as fh:
                    fh.write(json.dumps(dict(key=it["key"], seconds=round(time.monotonic() - mono, 1), at=now()))
                             + "\n")
                state["spent"] += ledger.interrupt(it["key"], it["model"], ledger.mean_call_cost(it["model"]))
            stats["interrupted"] += len(snapshot)
    left = sum(len([i for i in order if i["model"] == m and i["key"] not in key_state(out_dir, m, retry_passes)[1]])
               for m in models)
    summary = dict(at=now(), seconds=round(time.monotonic() - t0, 1), stats=dict(stats), left=left,
                   spent=round(state["spent"], 6), budget_usd=budget_usd, budget_stop=state["budget_stop"])
    with (out_dir / "chunks.jsonl").open("a") as fh:
        fh.write(json.dumps(summary) + "\n")
    log(f"chunk end: {dict(stats)}; {left} items not yet done/final; spend ${state['spent']:.4f}"
        + ("; BUDGET STOP" if state["budget_stop"] else ""))
    return summary
