"""EXPLORATORY score-midpoint experiment: generation (both environments, both models, all conditions interleaved).

Serving and generation code are reused read-only:
  upsell  model_diffing.core.converse + model_diffing.petri_task.adapter / generation_config (as run_pilot.generate,
          used by the recommendation score-gap run): one user turn, final visible reply kept.
  send    designs/score_gap/sending/run_gap.py: serving(), model_policy(), run_episode() (the 8-step tool loop over
          designs/action/env.py; the outcome `acted` is computed by designs/action/score.py inside run_episode).
Serving: experiment.grading.3way.json targets for Qwen 3.5 (novita/bf16) and Qwen 3.8 (deepinfra/bf16,
reasoning_effort medium), temperature 0.7, top_p 0.95, top_k 20, max_tokens 32768, timeout 1200 s per call.

Chunked, resumable by item key (each invocation runs <= ~9 min; repeat until done):
  - one process runs both models at once, up to CONCURRENCY items in flight per model (one request in flight per
    item; a send episode makes its calls one at a time);
  - each model's items follow one fixed shuffled order across both environments and every condition (interleaved);
  - no new items are launched after `cutoff` seconds; at `deadline` seconds in-flight items are cancelled and an
    `interrupt` line (seconds in flight) is written. An item whose cumulative in-flight time without completing
    reaches STALL (30 min) is recorded as `abandoned` (non-valid) and not retried;
  - API failures are retried up to RETRY_PASSES more times (failed records are kept; a later success wins);
    429 / rate-limit errors are backed off and retried in place without counting as a pass;
  - spend = token usage x listed prices over all records (both models, inspection included) plus an estimate for
    cancelled calls; no new item is launched once it reaches BUDGET_STOP.
"""
from __future__ import annotations

import asyncio
import hashlib
import importlib.util
import json
import random
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone

import mid_materials as MM
from mid_design import (BUDGET_STOP, CONCURRENCY, INSPECT_OUT, MODELS, OUT, RETRY_PASSES, ROOT, STALL, TIMEOUT,
                        cost)

_spec = importlib.util.spec_from_file_location("send_run_gap", ROOT / "designs/score_gap/sending/run_gap.py")
SR = importlib.util.module_from_spec(_spec)
sys.modules["send_run_gap"] = SR
_spec.loader.exec_module(SR)   # read-only reuse: serving(), model_policy(), run_episode()
from env import tool_specs  # noqa: E402  (designs/action/env.py)

RATE_WORDS = ("429", "rate limit", "rate-limit", "ratelimit", "too many requests")


def serving() -> dict:
    s = SR.serving()
    assert [t["label"] for t in s["targets"]] == list(MODELS)
    assert s["target_max_tokens"] == 32768 and s["timeout"] == TIMEOUT == 1200 and s["temperature"] == 0.7
    return s


def digest(items) -> str:
    body = []
    for i in items:
        p = MM.render(i)
        extra = []
        if i["env"] == "send":
            task = MM.SEND_TASKS[i["scenario"]]
            extra = [tool_specs(task), task["context"], task["facts"], task["key"]]
        body.append([i["key"], p["system"], p["turns"], *extra])
    return hashlib.sha256(json.dumps([body, serving()], sort_keys=True, ensure_ascii=False).encode()).hexdigest()


# ---------------------------------------------------------------- records

def files(out_dir, label):
    d = out_dir / "gen" / label.replace(" ", "_")
    return dict(upsell=d / "generations.jsonl", send=d / "episodes.jsonl", interrupts=d / "interrupts.jsonl")


def _read(path):
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()] if path.exists() else []


def all_records(out_dir):
    rows = []
    for m in MODELS:
        f = files(out_dir, m)
        rows += _read(f["upsell"]) + _read(f["send"])
    return rows


def is_fail(r) -> bool:
    return r["status"] in ("error", "failed")


def key_state(out_dir, label):
    """done keys (completed or final), failure counts, cumulative interrupted seconds."""
    f = files(out_dir, label)
    recs = _read(f["upsell"]) + _read(f["send"])
    fails, done = Counter(), set()
    for r in recs:
        if is_fail(r):
            fails[r["key"]] += 1
        else:
            done.add(r["key"])  # completed (any status) or abandoned
    inflight = defaultdict(float)
    for r in _read(f["interrupts"]):
        inflight[r["key"]] += r["seconds"]
    final = done | {k for k, n in fails.items() if n > RETRY_PASSES}
    return done, final, fails, inflight


def spent(*dirs) -> dict:
    tgt = sum(r.get("cost", 0.0) for d in dirs for r in all_records(d))
    n = Counter(r["model"] for d in dirs for r in all_records(d) if not is_fail(r) and r.get("cost"))
    c = Counter()
    for d in dirs:
        for r in all_records(d):
            if not is_fail(r) and r.get("cost"):
                c[r["model"]] += r["cost"]
    mean = {m: c[m] / n[m] for m in n}
    intr = 0.0
    for d in dirs:
        for m in MODELS:
            intr += len(_read(files(d, m)["interrupts"])) * mean.get(m, 0.01)
    return dict(target=tgt, interrupted_est=intr, total=tgt + intr)


# ---------------------------------------------------------------- workers

def _rate_limited(text: str) -> bool:
    t = (text or "").lower()
    return any(w in t for w in RATE_WORDS)


async def upsell_one(gen, item):
    from model_diffing.core import converse
    p = MM.render(item)
    for k in range(6):
        messages, status, private = await converse(gen, p["turns"], system=p["system"], timeout=TIMEOUT,
                                                   semaphore=asyncio.Semaphore(1))
        err = " ".join(str(x.get("error", "")) for x in private)
        if status == "error" and _rate_limited(err) and k < 5:
            await asyncio.sleep(min(90, 5 * 2 ** k) * (0.5 + random.random()))
            continue
        break
    reply = messages[-1]["content"] if messages and messages[-1]["role"] == "assistant" else ""
    usage = {u: sum((x.get(u) or 0) for x in private) for u in ("input_tokens", "output_tokens", "reasoning_tokens")}
    return dict(status=status, private=private, reply=reply, usage=usage, rate_limit_retries=k,
                shown_scores=MM.SCORE2.findall(p["turns"][0]))


async def send_one(policy, item, on_progress):
    task = MM.SEND_TASKS[item["scenario"]]
    for k in range(6):
        rec = await SR.run_episode(policy, task, MM.render(item), on_progress)
        err = " ".join(str(s.get("error", "")) for s in rec.get("trace", []))
        if rec["status"] == "failed" and _rate_limited(err) and k < 5:
            await asyncio.sleep(min(90, 5 * 2 ** k) * (0.5 + random.random()))
            continue
        break
    rec["rate_limit_retries"] = k
    rec["shown_scores"] = MM.SCORE2.findall(rec.get("prompt", ""))
    return rec


# ---------------------------------------------------------------- driver

async def run_model(items, out_dir, label, model, config, state, t0, cutoff, deadline, conc):
    from model_diffing.petri_task import adapter
    gen = adapter(model, config=config)
    policy = SR.model_policy(model, config)
    f = files(out_dir, label)
    f["upsell"].parent.mkdir(parents=True, exist_ok=True)
    mine = [i for i in items if i["model"] == label]
    random.Random(f"order|{label}|2026-10-29").shuffle(mine)  # one fixed interleaved order for all chunks
    done, final, fails, inflight = key_state(out_dir, label)
    # abandon items whose cumulative in-flight time reached STALL
    for i in mine:
        if i["key"] not in final and inflight[i["key"]] >= STALL:
            rec = i | dict(status="abandoned", error=f"no completion after {inflight[i['key']]:.0f} s cumulative "
                                                     f"in flight", usage={}, cost=0.0, measures={},
                           finished=datetime.now(timezone.utc).isoformat(timespec="seconds"))
            with f[i["env"]].open("a") as fh:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            final.add(i["key"])
    queue = [i for i in mine if i["key"] not in final]
    print(f"{label}: {len(queue)} to do ({len(mine) - len(queue)} done/final of {len(mine)})", flush=True)
    lock = asyncio.Lock()
    running: dict = {}
    stats = Counter()

    async def worker():
        while queue:
            if state["stop"] or time.monotonic() - t0 > cutoff:
                return
            i = queue.pop(0)
            started, mono = datetime.now(timezone.utc), time.monotonic()
            running[i["key"]] = (i, mono)
            try:
                if i["env"] == "upsell":
                    rec = await upsell_one(gen, i)
                else:
                    rec = await send_one(policy, i, lambda: None)
            except asyncio.CancelledError:
                raise
            except Exception as e:  # noqa: BLE001
                rec = dict(status="error" if i["env"] == "upsell" else "failed",
                           error=f"{type(e).__name__}: {str(e)[:300]}", usage={}, measures={})
            finally:
                running.pop(i["key"], None)
            rec = i | rec | dict(attempt=fails[i["key"]], started=started.isoformat(timespec="seconds"),
                                 finished=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                 seconds=round(time.monotonic() - mono, 1), cost=cost(label, rec.get("usage") or {}))
            async with lock:
                with f[i["env"]].open("a") as fh:
                    fh.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
                state["spent"] += rec["cost"]
                stats[rec["status"]] += 1
                stats["rl_retries"] += rec.get("rate_limit_retries", 0)
                if is_fail(rec):
                    fails[i["key"]] += 1
                    if fails[i["key"]] <= RETRY_PASSES:
                        queue.append(i)  # retry pass
                n = sum(v for k, v in stats.items() if k != "rl_retries")
                if n % 100 == 0:
                    state["spent"] = spent(OUT, INSPECT_OUT)["total"]
                    print(f"  {label}: {n} finished this chunk {dict(stats)} | spend ${state['spent']:.2f} | "
                          f"{time.monotonic() - t0:.0f}s", flush=True)
                if state["spent"] >= BUDGET_STOP and not state["stop"]:
                    state["stop"] = True
                    print(f"BUDGET STOP at ${state['spent']:.2f}", flush=True)

    tasks = [asyncio.ensure_future(worker()) for _ in range(conc)]
    remaining = deadline - (time.monotonic() - t0)
    _, pending = await asyncio.wait(tasks, timeout=max(1, remaining))
    if pending:
        snapshot = list(running.values())
        for t in pending:
            t.cancel()
        await asyncio.gather(*pending, return_exceptions=True)
        with f["interrupts"].open("a") as fh:
            for i, mono in snapshot:
                fh.write(json.dumps(dict(key=i["key"], seconds=round(time.monotonic() - mono, 1),
                                         at=datetime.now(timezone.utc).isoformat(timespec="seconds"))) + "\n")
        stats["interrupted"] += len(snapshot)
    left = len([i for i in mine if i["key"] not in key_state(out_dir, label)[1]])
    print(f"{label}: chunk end {dict(stats)}; {left} items not yet done/final", flush=True)
    return left


async def generate(items, out_dir, cutoff=330, deadline=500, conc=CONCURRENCY):
    from dotenv import load_dotenv
    from inspect_ai.model import get_model

    from model_diffing.petri_task import generation_config
    load_dotenv(ROOT / ".env")
    srv = serving()
    t0 = time.monotonic()
    s = spent(OUT, INSPECT_OUT)
    state = dict(spent=s["total"], stop=s["total"] >= BUDGET_STOP)
    print(f"session spend so far ${s['total']:.2f} (target ${s['target']:.2f} + cancelled-call estimate "
          f"${s['interrupted_est']:.2f}); stop at ${BUDGET_STOP:.0f}", flush=True)
    jobs = []
    for t in srv["targets"]:
        config = generation_config(srv, t)
        config = config.merge(type(config)(max_connections=conc))
        model = get_model(t["model"], **t.get("model_args", {}))
        jobs.append(run_model(items, out_dir, t["label"], model, config, state, t0, cutoff, deadline, conc))
    left = await asyncio.gather(*jobs)
    s = spent(OUT, INSPECT_OUT)
    print(f"ALL: {sum(left)} items left; session spend ${s['total']:.2f} (target ${s['target']:.2f} + "
          f"cancelled estimate ${s['interrupted_est']:.2f})", flush=True)
    return sum(left)
