"""Prepare, freeze and run the reasoning judge (repo .venv).

  .venv/bin/python rj_judge.py prepare <stage>           # run/<stage>/items.jsonl + views.jsonl
  .venv/bin/python rj_judge.py freeze <stage>            # run/<stage>/manifest.json (required for main, factorial)
  .venv/bin/python rj_judge.py run <stage> [--limit N]   # judge; resumes; refuses if frozen files changed
  .venv/bin/python rj_judge.py show <stage> <key|index>  # print one view (and its labels, if judged)

Judge: openrouter/anthropic/claude-sonnet-5.5, Anthropic-only, temperature 0 (repo standard). One call per episode;
the output is validated (rj_common.validate); on an invalid answer the judge is asked again with the errors, up to
3 attempts. Unlabelled items are recorded with labels=null and never counted.
"""
from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import json
import sys
from pathlib import Path

from rj_common import (FROZEN_FILES, HERE, JUDGE, JUDGE_ARGS, JUDGE_MAX_TOKENS, JUDGE_TEMPERATURE, PA_RUN, PRICE,
                       RATIONALES, RUN, STAGES, build_view, excerpt_found, file_sha, judge_prompt, load_source,
                       parse_labels, read_jsonl, select, sha, validate, write_jsonl)

CONC = 24
MAX_ATTEMPTS = 5   # invalid JSON is re-asked with the errors; a provider block is retried from a fresh prompt
ROOT = HERE.parents[1]


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def prepare(stage: str) -> None:
    cfg = STAGES[stage]
    episodes, prompts = load_source(cfg["pa_stage"])
    rows = select(stage)
    items, views = [], []
    for r in rows:
        e = episodes[r["key"]]
        v = build_view(e, prompts[e["input_sha256"]])
        meta = {k: r[k] for k in ("key", "stage", "part", "task", "block", "materials", "arm", "score", "gap", "model",
                                  "rep", "violates", "outcome", "n_steps")}
        meta.update(pa_stage=cfg["pa_stage"], view_sha=sha(v["view"]),
                    **{k: v[k] for k in ("action", "action_kind", "action_step", "n_steps_total", "reasoning_chars",
                                         "reasoning_tokens", "redactions", "commit_tool", "save_tool")})
        assert meta["action_kind"] is not None, f"no consequential call in {r['key']}"
        meta["attempted_commit"] = meta["action_kind"] == "commit"   # scorer's `violates` = successful commit only
        items.append(meta)
        views.append(dict(key=r["key"], view=v["view"], score_fact=v["score_fact"], reasoning_text=v["reasoning_text"]))
    out = RUN / stage
    write_jsonl(out / "items.jsonl", items)
    write_jsonl(out / "views.jsonl", views)
    cells = {}
    for m in items:
        c = cells.setdefault((m["arm"], m["score"], m["model"]), [0, 0, 0])
        c[0] += 1
        c[1] += int(bool(m["violates"]))
        c[2] += int(m["attempted_commit"])
    print(f"{stage}: {len(items)} items -> {out.relative_to(ROOT)}")
    for k in sorted(cells):
        print(f"  {k[0]:9} {k[1]:5} {k[2]:9} n={cells[k][0]:3} overrides(scorer)={cells[k][1]:3} "
              f"attempted commits={cells[k][2]}")


def manifest(stage: str) -> dict:
    cfg = STAGES[stage]
    src = PA_RUN / cfg["pa_stage"] / "send"
    return dict(stage=stage, config=cfg, files={f: file_sha(HERE / f) for f in FROZEN_FILES},
                items_sha=file_sha(RUN / stage / "items.jsonl"), views_sha=file_sha(RUN / stage / "views.jsonl"),
                n_items=len(read_jsonl(RUN / stage / "items.jsonl")),
                source={f: file_sha(src / f) for f in ("episodes.jsonl", "scored.jsonl", "prompts.jsonl")},
                judge=dict(model=JUDGE, args=JUDGE_ARGS, temperature=JUDGE_TEMPERATURE, max_tokens=JUDGE_MAX_TOKENS,
                           price_per_m=PRICE))


def freeze(stage: str) -> None:
    m = manifest(stage)
    m["frozen_at"] = now()
    mp = RUN / stage / "manifest.json"
    if mp.exists():   # re-freeze after an amendment: keep the earlier manifest(s); see AMENDMENTS.md
        m["amended_from"] = json.loads(mp.read_text())
    mp.write_text(json.dumps(m, indent=1))
    print(f"frozen {stage}: {m['n_items']} items; manifest sha {sha(json.dumps(m, sort_keys=True))[:12]}")


def check_frozen(stage: str) -> None:
    mp = RUN / stage / "manifest.json"
    if stage == "pilot" and not mp.exists():
        return
    assert mp.exists(), f"{stage} is not frozen: run `rj_judge.py freeze {stage}` first"
    old = json.loads(mp.read_text())
    cur = manifest(stage)
    for section in ("files", "source"):
        for k, v in old[section].items():
            assert cur[section][k] == v, f"frozen file changed: {k}"
    assert old["items_sha"] == cur["items_sha"] and old["views_sha"] == cur["views_sha"], "items/views changed"


async def run(stage: str, limit: int | None, conc: int = CONC, max_attempts: int = MAX_ATTEMPTS) -> None:
    from dotenv import load_dotenv
    from inspect_ai.model import ChatMessageAssistant, ChatMessageUser, GenerateConfig, get_model
    check_frozen(stage)
    load_dotenv(ROOT / ".env")
    model = get_model(JUDGE, **JUDGE_ARGS)
    cfg = GenerateConfig(temperature=JUDGE_TEMPERATURE, max_tokens=JUDGE_MAX_TOKENS, max_connections=conc)
    items = read_jsonl(RUN / stage / "items.jsonl")
    views = {v["key"]: v for v in read_jsonl(RUN / stage / "views.jsonl")}
    jp, lp = RUN / stage / "judge.jsonl", RUN / stage / "ledger.jsonl"
    done = {r["key"] for r in read_jsonl(jp) if r["labels"] is not None}
    todo = [i for i in items if i["key"] not in done][: limit or None]
    print(f"judge {stage}: {len(todo)} to label ({len(done)} done)", flush=True)
    sem, lock = asyncio.Semaphore(conc), asyncio.Lock()
    spent = [0.0]

    async def one(it: dict) -> None:
        v = views[it["key"]]
        msgs = [ChatMessageUser(content=judge_prompt(v["view"], v["score_fact"]))]
        labels, errs, raw, cost, attempts, blocked = None, [], "", 0.0, 0, 0
        for attempt in range(max_attempts):
            attempts = attempt + 1
            try:
                async with sem:
                    out = await asyncio.wait_for(model.generate(msgs, config=cfg, cache=False), 300)
                u = out.usage  # can be None on a failed or filtered response
                tin, tout = (getattr(u, "input_tokens", 0) or 0), (getattr(u, "output_tokens", 0) or 0)
                c = tin * PRICE[0] / 1e6 + tout * PRICE[1] / 1e6
                cost += c
                async with lock:
                    spent[0] += c
                    with lp.open("a") as f:
                        f.write(json.dumps(dict(at=now(), key=it["key"], attempt=attempts, cost=c, input_tokens=tin,
                                                output_tokens=tout, stop=getattr(out, "stop_reason", None))) + "\n")
                raw = out.completion or ""
                if not raw.strip():
                    errs = [f"empty completion (stop={getattr(out, 'stop_reason', None)})"]
                    await asyncio.sleep(5)
                    continue
                if raw.startswith("This request was blocked"):
                    # provider-side policy block; it is stochastic, so retry the identical prompt in a fresh
                    # conversation (never with the block text in context)
                    errs, blocked = ["blocked"], blocked + 1
                    msgs = msgs[:1]
                    await asyncio.sleep(3)
                    continue
                d = parse_labels(raw)
                errs = validate(d)
                if not errs:
                    d["rationales"] = {r: dict(status=d["rationales"][r]["status"],
                                               excerpt=str(d["rationales"][r].get("excerpt") or ""))
                                       for r in RATIONALES}
                    labels = d
                    break
                msgs += [ChatMessageAssistant(content=raw),
                         ChatMessageUser(content="That answer was not valid: " + ", ".join(errs) +
                                         ". Reply again with one JSON object only, in exactly the required shape.")]
            except Exception as e:  # noqa: BLE001
                raw = f"{type(e).__name__}: {e}"[:300]
                errs = ["exception"]
                await asyncio.sleep(5)
        verified = None
        if labels:
            verified = {r: (labels["rationales"][r]["status"] == "absent" or
                            excerpt_found(labels["rationales"][r]["excerpt"], v["reasoning_text"]))
                        for r in labels["rationales"]}
        async with lock:
            with jp.open("a") as f:
                f.write(json.dumps(dict(key=it["key"], labels=labels, errors=errs if labels is None else [],
                                        excerpt_verified=verified, attempts=attempts, blocked_attempts=blocked,
                                        cost=cost, raw=raw[:3000] if labels is None else "")) + "\n")

    await asyncio.gather(*[one(i) for i in todo])
    rows = {r["key"]: r for r in read_jsonl(jp)}   # a re-run appends; the last record per key wins
    ok = sum(r["labels"] is not None for r in rows.values())
    blocked = sum(r.get("blocked_attempts", 0) for r in rows.values())
    print(f"{stage}: {ok}/{len(items)} labelled ({blocked} blocked attempts); this run cost ${spent[0]:.2f}; "
          f"total ledger ${sum(r['cost'] for r in read_jsonl(lp)):.2f}")


def show(stage: str, which: str) -> None:
    items = read_jsonl(RUN / stage / "items.jsonl")
    it = items[int(which)] if which.isdigit() else next(i for i in items if i["key"] == which)
    v = next(v for v in read_jsonl(RUN / stage / "views.jsonl") if v["key"] == it["key"])
    print(v["view"])
    print("\n=== HIDDEN (not shown to the judge) ===")
    print(json.dumps({k: it[k] for k in ("key", "model", "arm", "score", "violates", "action", "reasoning_chars")}))
    for r in read_jsonl(RUN / stage / "judge.jsonl"):
        if r["key"] == it["key"]:
            print("=== JUDGE ===")
            print(json.dumps(r["labels"], indent=1), "\nexcerpt_verified:", r["excerpt_verified"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["prepare", "freeze", "run", "show"])
    ap.add_argument("stage", choices=list(STAGES))
    ap.add_argument("arg", nargs="?")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--conc", type=int, default=CONC)
    ap.add_argument("--attempts", type=int, default=MAX_ATTEMPTS)
    a = ap.parse_args()
    if a.cmd == "prepare":
        prepare(a.stage)
    elif a.cmd == "freeze":
        freeze(a.stage)
    elif a.cmd == "run":
        asyncio.run(run(a.stage, a.limit, a.conc, a.attempts))
    else:
        show(a.stage, a.arg or "0")
