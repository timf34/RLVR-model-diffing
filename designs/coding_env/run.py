"""Coding task families × context × request placement × grader variant × Qwen 3.5 / 3.6 / 3.8.

Run from the repo root (one process per model, in parallel; each writes its own file):
  .venv/bin/python designs/coding_env/run.py inspect "Qwen 3.6" 24     # 1 episode per cell -> runs/inspection_v2
  .venv/bin/python designs/coding_env/run.py report inspection_v2      # table + trajectories for review
  .venv/bin/python designs/coding_env/run.py freeze                    # main run: prompts, repos, graders, code hashed
  .venv/bin/python designs/coding_env/run.py generate "Qwen 3.6" 24    # main run (5 per cell, 360 total)
  .venv/bin/python designs/coding_env/run.py report main
Inspection data is kept separate from the frozen run (runs/inspection vs runs/main).
"""
from __future__ import annotations

import asyncio
import hashlib
import importlib
import itertools
import json
import random
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT / "src")]

from model_diffing.codeenv.base import VARIANTS  # noqa: E402
from model_diffing.codeenv.episode import CONTEXTS, REQUESTS, CodeEpisode  # noqa: E402

FAMILY_IDS = ("csv_parser", "perf", "build_repair")
INSPECTION_RUN = "inspection_v2"  # v1 (easier tasks; same 30-step budget) is runs/inspection with code_snapshot_v1/
SAMPLES = 5
MAX_TOKENS = 32768
SERVING_CONFIG = ROOT / "experiment.grading.3way.json"
SERVING_NOTES = {
    "Qwen 3.5": "novita/bf16; default thinking (no reasoning_effort parameter on any 3.5 host)",
    "Qwen 3.6": "alibaba (first-party; precision not stated; no bf16 host on OpenRouter); default thinking",
    "Qwen 3.8": "deepinfra/bf16; reasoning_effort=medium",
}
CODE = sorted([*(ROOT / "src/model_diffing/codeenv").rglob("*.py"), HERE / "run.py"])


def families() -> dict:
    return {f: importlib.import_module(f"model_diffing.codeenv.families.{f}").FAMILY for f in FAMILY_IDS}


def serving() -> dict:
    s = json.loads(SERVING_CONFIG.read_text())
    targets = [{k: v for k, v in t.items() if k != "serving_note"} for t in s["targets"]]
    return dict(targets=targets, target_generate=s["target_generate"], temperature=0.7, target_max_tokens=MAX_TOKENS)


def labels() -> list[str]:
    return [t["label"] for t in serving()["targets"]]


def plan(samples: int, tag: str) -> list[dict]:
    return [dict(key=f"{tag}|{f}|{c}|{q}|{v}|{m}|{r}", family=f, context=c, request=q, variant=v, model=m, rep=r)
            for f, c, q, v, m, r in itertools.product(FAMILY_IDS, CONTEXTS, REQUESTS, VARIANTS, labels(),
                                                      range(samples))]


def digest(items) -> str:
    fams = families()
    body = []
    for i in items:
        ep = CodeEpisode(fams[i["family"]], i["context"], i["request"], i["variant"])
        body.append([i["key"], ep.system, ep.prompt, ep.files])
    return hashlib.sha256(json.dumps([body, serving()], sort_keys=True).encode()).hexdigest()


def code_hashes() -> dict:
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in CODE}


async def generate(items, out: Path, model_label: str, concurrency: int):
    from dotenv import load_dotenv
    from inspect_ai.model import get_model

    from model_diffing.codeenv.agent import get_judge, run_episode
    from model_diffing.petri_task import generation_config
    load_dotenv(ROOT / ".env")
    srv = serving()
    target = next(t for t in srv["targets"] if t["label"] == model_label)
    model = get_model(target["model"], **target.get("model_args", {}))
    config = generation_config(srv, target)
    judge, fams = get_judge(), families()
    out.mkdir(parents=True, exist_ok=True)
    path = out / "episodes.jsonl"
    done = set()
    if path.exists():
        done = {json.loads(l)["key"] for l in path.read_text().splitlines()
                if l.strip() and not json.loads(l)["status"].startswith("error")}
    todo = [i for i in items if i["model"] == model_label and i["key"] not in done]
    random.Random(0).shuffle(todo)  # interleave families and conditions
    sem, lock, n = asyncio.Semaphore(concurrency), asyncio.Lock(), [0]
    print(f"{model_label}: {len(todo)} episodes to run ({len(done)} done)", flush=True)

    async def one(i):
        t0 = datetime.now(timezone.utc)
        try:
            rec = await run_episode(model, config, fams[i["family"]], i["context"], i["request"], i["variant"], sem,
                                    judge=judge)
        except Exception as e:  # noqa: BLE001  (record and continue; resume retries errors)
            rec = dict(status=f"error: {type(e).__name__}: {str(e)[:300]}")
        rec = i | rec | dict(started=t0.isoformat(timespec="seconds"),
                             finished=datetime.now(timezone.utc).isoformat(timespec="seconds"))
        async with lock:
            with path.open("a") as f:
                f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
            n[0] += 1
            o = rec.get("outcomes", {})
            print(f"  [{n[0]}/{len(todo)}] {i['family']}|{i['context']}/{i['request']}|{i['variant']}: "
                  f"{rec['status']} steps={rec.get('steps')} vis={o.get('visible_score')} "
                  f"prot={o.get('protected_correct')} shortcut={o.get('shortcut')}", flush=True)

    await asyncio.gather(*(one(i) for i in todo))


def load(run: str) -> list[dict]:
    rows = {}
    for p in sorted((HERE / "runs" / run / "gen").glob("*/episodes.jsonl")):
        for line in p.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                rows[r["key"]] = r
    return list(rows.values())


def score_path(r: dict) -> str:
    """How the episode reached its result: whether it ever saw failing checks before submitting."""
    edited, scores = False, []
    for e in r.get("events") or []:  # only test runs made after the first edit count
        if e[0] in ("write", "delete"):
            edited = True
        elif e[0] == "run" and edited:
            scores.append(e[2])
    if not scores:
        return "no_runs_after_edit"
    if scores[0] >= 0.999:
        return "first_run_full"
    return "repaired_to_full" if scores[-1] >= 0.999 else "ended_below_full"


def report(run: str):
    rows = sorted(load(run), key=lambda r: (r["family"], r["variant"], r["context"], r["request"], r["model"]))
    L = [f"# Coding environment: {run} ({len(rows)} episodes)", "",
         "| family | variant | context/request | model | status | steps | config | visible | protected ok | "
         "shortcut | modified | flags | claim | disclosed | empty/trunc turns | test runs (scores) | path |",
         "|" + "---|" * 17]
    for r in rows:
        o = r.get("outcomes") or {}
        flags = ",".join(k for k, v in (o.get("flags") or {}).items() if v)
        rep = o.get("report") or {}
        L.append(f"| {r['family']} | {r['variant']} | {r['context']}/{r['request']} | {r['model']} | {r['status']} | "
                 f"{r.get('steps')} | {o.get('config_read')} | {o.get('visible_score')} | {o.get('protected_correct')} "
                 f"| {o.get('shortcut')} | {','.join(o.get('modified_protected') or [])} | {flags} | "
                 f"{rep.get('test_claim')} | {rep.get('discloses_change')} | "
                 f"{o.get('empty_turns')}/{o.get('truncated_turns')} | "
                 f"{' '.join(f'{t.get('score', 0):.2f}' for t in r.get('test_runs') or [])} | "
                 f"{score_path(r)} |")
    T = [f"# Trajectories: {run}", ""]
    for r in rows:
        T += [f"## {r['family']} | {r['variant']} | {r['context']}/{r['request']} | {r['model']} | {r['status']}", ""]
        for t in r.get("trace", []):
            calls = "; ".join(f"{c['name']}({', '.join(f'{k}={str(v)[:80]!r}' for k, v in c['args'].items())})"
                              for c in t.get("calls", []))
            T.append(f"- step {t['step']}: {t.get('text', '').strip()[:300]!r} → {calls or '(no tool call)'}"
                     + (f" [reasoning tokens {t.get('reasoning_tokens')}]" if t.get("reasoning_tokens") else ""))
            for res in t.get("results", []):
                T.append(f"    ↳ {res[:400]!r}")
        sub = r.get("submission") or {}
        T += ["", f"**Summary:** {sub.get('summary', '(none)')}", ""]
        changed = {k: v for k, v in (r.get("final_files") or {}).items()}
        T += [f"Files at end: {sorted(changed)}", ""]
    out = HERE / "runs" / run
    (out / "REPORT.md").write_text("\n".join(L) + "\n")
    (out / "TRAJECTORIES.md").write_text("\n".join(T) + "\n")
    print(f"wrote {out / 'REPORT.md'} and TRAJECTORIES.md")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "inspect":
        run_name = sys.argv[4] if len(sys.argv) > 4 else INSPECTION_RUN
        items = plan(1, "inspect")
        return asyncio.run(generate(items, HERE / "runs" / run_name / "gen" / sys.argv[2].replace(" ", "_"),
                                    sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 12))
    if cmd == "report":
        return report(sys.argv[2])
    items = plan(SAMPLES, "main")
    manifest = HERE / "runs/main/manifest.json"
    if cmd == "freeze":
        if manifest.exists():
            raise SystemExit("Already frozen; start a new, separately named run to change anything")
        manifest.parent.mkdir(parents=True, exist_ok=True)
        snap = manifest.parent / "code_snapshot"
        for p in CODE:
            dest = snap / p.relative_to(ROOT)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(p, dest)
        manifest.write_text(json.dumps(dict(
            sha256=digest(items), at=datetime.now(timezone.utc).isoformat(timespec="seconds"), total=len(items),
            samples=SAMPLES, code_sha256=code_hashes(), serving=serving(), serving_notes=SERVING_NOTES), indent=2) + "\n")
        return print(f"Frozen {len(items)} episodes")
    if not manifest.exists() or json.loads(manifest.read_text())["sha256"] != digest(items):
        raise SystemExit("Not frozen, or prompts/repos/serving changed since freezing")
    if json.loads(manifest.read_text())["code_sha256"] != code_hashes():
        raise SystemExit("Environment code changed since freezing")
    if cmd == "generate":
        return asyncio.run(generate(items, HERE / "runs/main/gen" / sys.argv[2].replace(" ", "_"), sys.argv[2],
                                    int(sys.argv[3]) if len(sys.argv) > 3 else 12))
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
