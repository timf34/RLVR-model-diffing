"""EXPLORATORY score-gap response curve on the review-rating task (see ANALYSIS_PLAN.md).

Run from the repo root:
  .venv/bin/python designs/score_gap/review/run_gap.py check
  .venv/bin/python designs/score_gap/review/run_gap.py inspect            # setup check only (a few items)
  .venv/bin/python designs/score_gap/review/run_gap.py freeze
  .venv/bin/python designs/score_gap/review/run_gap.py generate "Qwen 3.8" 64   # one process per model, in parallel
  .venv/bin/python designs/score_gap/review/run_gap.py status
  .venv/bin/python designs/score_gap/review/run_gap.py analyse

Reuses designs/action_mechanisms/review_rating (design, scenarios, rubrics; shared framing, episode helpers, serving)
and designs/rl_context (domains/review.py, confirm_materials.py; run_domains.py for the equivalence check) read-only;
their hashes are recorded in the manifest.

Generation policy (shared spec): one process per model, up to N concurrent target requests; only 429s are backed off
(exponential, capped at 120 s) and retried in place; any other error makes the attempt "failed", and failed items are
retried in up to 2 further passes. An item with no progress (no API call started or finished) for 30 min is recorded
as "abandoned" (final, non-valid). Cost = token usage returned by OpenRouter x listed prices (serving.PRICES); the
process stops starting new items once the folder total reaches the budget.
"""
import asyncio
import hashlib
import itertools
import json
import random
import shutil
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gap_materials as G  # noqa: E402  (puts designs/ and rl_context paths on sys.path)
import gap_episode as E  # noqa: E402
from action_mechanisms.shared import serving  # noqa: E402
from action_mechanisms.review_rating import scenarios as S  # noqa: E402
import review as RD  # noqa: E402

OUT = HERE / "run"
INSPECT_OUT = HERE / "inspection"
SAMPLES = 4
BUDGET = 100.0
STOP_AT = 95.0  # stop starting new items here, leaving room for those in flight
ABANDON_S = 1800
RETRY_PASSES = 2
JUDGE_CONCURRENCY = 32
MODELS = ("Qwen 3.5", "Qwen 3.8")
DESIGNS = HERE.parents[1]
CODE = ["gap_materials.py", "gap_episode.py", "gap_analysis.py", "gap_report.py", "run_gap.py", "simulate.py", "ANALYSIS_PLAN.md",
        "simulation/CALIBRATION.md"]
DEPS = [DESIGNS / "action_mechanisms" / "review_rating" / f for f in ("design.py", "scenarios.py", "rubrics.py")] + \
       [DESIGNS / "action_mechanisms" / "shared" / f for f in ("framing.py", "episode.py", "judge.py", "serving.py")] + \
       [DESIGNS / "rl_context" / f for f in ("domains/review.py", "confirm_materials.py", "run_domains.py")] + \
       [HERE.parents[2] / "experiment.grading.3way.json"]


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ------------------------------------------------------------------------------------------------ plan

def plan(split="main", samples=SAMPLES, gaps=G.GAPS, with_ref=True, models=MODELS) -> list[dict]:
    out = []
    neutral = G.neutral_scenarios("main") if split == "main" else G.neutral_scenarios("inspection")[:1]
    bundle = G.bundle_tasks(split)
    for panel, g in G.conditions():
        if (g is not None and g != G.REF and g not in gaps) or (g == G.REF and not with_ref):
            continue
        scen = bundle if G.source(panel) == "bundle" else neutral
        for si, s in enumerate(scen):
            for r in range(samples):
                ep = G.episode_number(s["id"], g, r)
                prompt = G.render(panel, si, s, g, ep)
                for m in models:
                    out.append(dict(key=f"{split}|{panel}|{s['id']}|{G.gap_label(g)}|{m}|{r}", split=split,
                                    panel=panel, source=G.source(panel), scenario=s["id"], gap=g,
                                    gap_label=G.gap_label(g), model=m, rep=r, ep=ep, prompt=prompt))
    return out


def inspection_plan():
    return plan("inspection", 1, gaps=(-0.5, 0.0, 0.5), with_ref=False)


def gen_settings() -> dict:
    return dict(serving=serving.serving(), abandon_s=ABANDON_S, retry_passes=RETRY_PASSES, budget=BUDGET,
                judge=serving.JUDGE_MODEL, judge_args=serving.JUDGE_ARGS, judge_max_tokens=E.JUDGE_MAX_TOKENS)


def digest(items) -> str:
    body = [[i["key"], i["prompt"]] for i in items]
    return hashlib.sha256(json.dumps([body, gen_settings()], sort_keys=True, ensure_ascii=False,
                                     default=str).encode()).hexdigest()


# ------------------------------------------------------------------------------------------------ storage

def attempts_path(out_dir: Path, model: str) -> Path:
    return out_dir / "gen" / model.replace(" ", "_") / "attempts.jsonl"


def read_attempts(out_dir: Path) -> list[dict]:
    rows = []
    for p in sorted((out_dir / "gen").glob("*/attempts.jsonl")):
        for line in p.read_text().splitlines():
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:  # a line being written by the other process
                    pass
    return rows


def record_cost(r: dict) -> float:
    return serving.cost(r.get("usage") or {}, r.get("model", "")) + serving.cost(r.get("judge_usage") or {}, "judge")


def total_cost() -> float:
    return sum(record_cost(r) for d in (OUT, INSPECT_OUT) if (d / "gen").exists() for r in read_attempts(d))


def latest(out_dir: Path, items) -> list[dict]:
    """Per key: the latest non-failed attempt, else the latest failed one."""
    keys, rows = {i["key"] for i in items}, {}
    for r in read_attempts(out_dir):
        if r["key"] not in keys:
            continue
        if r["key"] in rows and r["status"] == "failed" and rows[r["key"]]["status"] != "failed":
            continue
        rows[r["key"]] = r
    return list(rows.values())


# ------------------------------------------------------------------------------------------------ generation

def _is_429(e: Exception) -> bool:
    s = f"{type(e).__name__} {e}".lower()
    return "ratelimit" in s.replace(" ", "").replace("_", "") or "429" in s or "rate limit" in s


def make_policy(label: str, concurrency: int, stats):
    """Target policy policy(messages, touch): one semaphore slot per API call; 429s backed off and retried in place,
    other errors raised. touch() marks progress for the calling item (slot acquired, call finished)."""
    from inspect_ai.model import GenerateConfig
    model, cfg = serving.get_target(label)
    cfg = cfg.merge(GenerateConfig(max_retries=0, max_connections=concurrency))
    sem = asyncio.Semaphore(concurrency)

    async def policy(messages, touch):
        delay = 5.0
        while True:
            try:
                async with sem:
                    touch()
                    out = await asyncio.wait_for(model.generate(messages, config=cfg, cache=False), serving.TIMEOUT)
                touch()
                u = out.usage
                return dict(message=out.message, stop=out.choices[0].stop_reason if out.choices else None,
                            usage={k: getattr(u, k, None) for k in ("input_tokens", "output_tokens",
                                                                    "reasoning_tokens")})
            except asyncio.CancelledError:
                raise
            except Exception as e:  # noqa: BLE001
                if not _is_429(e):
                    raise
                stats["429"] += 1
                await asyncio.sleep(min(120.0, delay) * (0.75 + 0.5 * random.random()))
                delay *= 2
    return policy


def run_generate(items, out_dir: Path, model: str, concurrency: int):
    asyncio.run(_generate([i for i in items if i["model"] == model], out_dir, model, concurrency))


async def _generate(items, out_dir: Path, model: str, concurrency: int):
    from dotenv import load_dotenv
    load_dotenv(HERE.parents[2] / ".env")
    path = attempts_path(out_dir, model)
    path.parent.mkdir(parents=True, exist_ok=True)
    progress, stats, lock, stop = {}, Counter(), asyncio.Lock(), {"flag": False}

    def toucher(key):
        def touch():
            progress[key] = time.monotonic()
        return touch

    judge = serving.get_judge() if any(i["source"] == "neutral" for i in items) else None
    jsem = asyncio.Semaphore(JUDGE_CONCURRENCY)
    policy = make_policy(model, concurrency, stats)

    async def budget_watch():
        while True:
            c = total_cost()
            if c >= STOP_AT:
                if not stop["flag"]:
                    print(f"BUDGET: ${c:.2f} >= ${STOP_AT}; no new items will start", flush=True)
                stop["flag"] = True
            await asyncio.sleep(30)

    def write(rec):
        with path.open("a") as f:
            f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")

    for pass_no in range(RETRY_PASSES + 1):
        prior = [r for r in read_attempts(out_dir) if r["model"] == model]
        final = {r["key"] for r in prior if r["status"] != "failed"}
        fails = Counter(r["key"] for r in prior if r["status"] == "failed")
        todo = [i for i in items if i["key"] not in final and fails[i["key"]] <= RETRY_PASSES]
        if pass_no == 0:
            random.Random(0).shuffle(todo)  # interleave all conditions (panels, levels, baselines, reference)
        else:
            todo = [i for i in todo if fails[i["key"]] > 0]
        print(f"[{now()}] {model} pass {pass_no}: {len(todo)} to run ({len(final)} final); cost so far "
              f"${total_cost():.2f}", flush=True)
        if not todo or stop["flag"]:
            break
        isem = asyncio.Semaphore(concurrency * 2)  # items in flight; target calls are capped by the policy's slots
        done_n = [0]

        async def one(i):
            async with isem:
                if stop["flag"]:
                    return
                touch = toucher(i["key"])
                touch()

                async def item_policy(messages, _touch=touch):
                    return await policy(messages, _touch)
                t0 = now()
                task = asyncio.ensure_future(E.run(i, item_policy, judge, jsem))
                while not task.done():
                    await asyncio.wait({task}, timeout=30)
                    if not task.done() and time.monotonic() - progress[i["key"]] > ABANDON_S:
                        task.cancel()
                        break
                try:
                    rec = task.result()
                except asyncio.CancelledError:
                    rec = dict(status="abandoned", error=f"no progress for {ABANDON_S // 60} min", usage={},
                               judge_usage={}, measures=dict(valid=False))
                except Exception as e:  # noqa: BLE001
                    rec = dict(status="failed", error=f"{type(e).__name__}: {str(e)[:300]}", usage={},
                               judge_usage={}, measures=dict(valid=False))
                meta = {k: v for k, v in i.items() if k != "prompt"}
                rec = meta | rec | dict(started=t0, finished=now(), pass_no=pass_no)
                rec["cost"] = record_cost(rec)
                async with lock:
                    write(rec)
                    done_n[0] += 1
                    if done_n[0] % 25 == 0 or done_n[0] == len(todo):
                        print(f"  [{now()}] {model} pass {pass_no}: {done_n[0]}/{len(todo)}; last {rec['status']}; "
                              f"429s {stats['429']}", flush=True)

        watcher = asyncio.ensure_future(budget_watch())
        await asyncio.gather(*(one(i) for i in todo))
        watcher.cancel()
    print(f"[{now()}] {model} done: {Counter(r['status'] for r in latest(out_dir, items))}; "
          f"cost total ${total_cost():.2f}", flush=True)


# ------------------------------------------------------------------------------------------------ status

def status(items, out_dir):
    rows = latest(out_dir, items)
    c = Counter((r["model"], r["status"]) for r in rows)
    att = read_attempts(out_dir)
    print(f"{len(rows)}/{len(items)} keys recorded; {len(att)} attempts; folder cost ${total_cost():.2f}")
    for k, v in sorted(c.items()):
        print(f"  {k}: {v}")
    return rows


def preview(items, path: Path):
    seen, L = set(), ["# Rendered prompts (one per panel x level, first scenario, first model)", ""]
    for i in items:
        tag = (i["panel"], i["gap_label"])
        if tag in seen or i["model"] != items[0]["model"]:
            continue
        seen.add(tag)
        L += [f"## {i['panel']} | gap {i['gap_label']} | {i['scenario']}", "```json",
              json.dumps(i["prompt"], indent=1, ensure_ascii=False), "```", ""]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(L) + "\n")


# ------------------------------------------------------------------------------------------------ main

def code_hashes():
    h = {f: hashlib.sha256((HERE / f).read_bytes()).hexdigest() for f in CODE}
    h |= {str(p.relative_to(HERE.parents[2])): hashlib.sha256(p.read_bytes()).hexdigest() for p in DEPS}
    return h


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "check":
        G.check()
        E.offline()
        items = plan()
        n = Counter((i["model"], i["source"]) for i in items)
        return print(f"{len(items)} main items {dict(n)}; {len(inspection_plan())} inspection items")
    if cmd == "inspect":
        items = inspection_plan()
        preview(items, INSPECT_OUT / "PREVIEW.md")

        async def both():
            await asyncio.gather(*(_generate([i for i in items if i["model"] == m], INSPECT_OUT, m, 16)
                                   for m in MODELS))
        asyncio.run(both())
        status(items, INSPECT_OUT)
        import gap_report
        return gap_report.inspection_summary(items, latest(INSPECT_OUT, items), INSPECT_OUT)
    if cmd == "inspect-status":
        return status(inspection_plan(), INSPECT_OUT)
    items = plan()
    manifest = OUT / "manifest.json"
    if cmd == "freeze":
        OUT.mkdir(exist_ok=True)
        if manifest.exists():
            raise SystemExit("Already frozen")
        snap = OUT / "code_snapshot"
        snap.mkdir(exist_ok=True)
        for f in CODE:
            (snap / Path(f).parent).mkdir(parents=True, exist_ok=True)
            shutil.copy(HERE / f, snap / f)
        for p in DEPS:
            dest = snap / "deps" / p.relative_to(HERE.parents[2])
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(p, dest)
        manifest.write_text(json.dumps(dict(
            sha256=digest(items), label="EXPLORATORY score-gap curve, review rating (frozen before generation)",
            at=now(), samples=SAMPLES, total=len(items),
            counts={f"{m}|{s}": n for (m, s), n in Counter((i["model"], i["source"]) for i in items).items()},
            gaps=G.GAPS, panels=G.PANELS, baselines=G.BASELINES, reference=G.REF_SCORES,
            plan_sha256=hashlib.sha256((HERE / "ANALYSIS_PLAN.md").read_bytes()).hexdigest(),
            code_sha256=code_hashes(), generation=gen_settings(), serving_notes=serving.SERVING_NOTES,
            prices=serving.PRICES, shuffle_seed=0), indent=2, default=str) + "\n")
        json.dump([{k: i[k] for k in ("key", "prompt")} for i in items], open(OUT / "prompts.json", "w"), indent=1,
                  ensure_ascii=False)
        return print(f"Frozen {len(items)} items, sha {json.loads(manifest.read_text())['sha256'][:12]}")
    if not manifest.exists() or json.loads(manifest.read_text())["sha256"] != digest(items):
        raise SystemExit("Not frozen, or prompts/serving changed since freezing")
    man = json.loads(manifest.read_text())
    changed = [f for f, h in code_hashes().items() if man["code_sha256"].get(f) != h]
    if cmd == "generate":
        if [f for f in changed if f != "run_gap.py"]:  # operational fixes to run_gap.py are allowed and reported
            raise SystemExit(f"Frozen files changed since freezing: {changed}")
        return run_generate(items, OUT, sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 16)
    if cmd == "status":
        return status(items, OUT)
    if cmd == "analyse":
        import gap_report
        return gap_report.analyse(items, latest(OUT, items), OUT, man, changed)
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
