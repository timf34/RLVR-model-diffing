"""Generic runner: plan → render/check → inspect → freeze → generate (resumable) → analyse.

An experiment is a module `action_mechanisms.<exp>.design` that defines:
  EXP: str                          experiment name (= folder name)
  CODE: list[str]                   files in the experiment folder to hash and snapshot (relative paths)
  plan(split) -> list[dict]         split is "inspection" or "main"; every item has a unique "key" (prefixed by the
                                    split), "model" (a serving label), "scenario", "cell", "kind"
  render(item) -> dict              deterministic, JSON-serialisable description of everything the model is shown
                                    (system, user turns, tool specs, follow-ups). Hashed into the manifest.
  async run(item, policy) -> dict   runs one item; returns a JSON-serialisable record with at least "status",
                                    "usage" (target tokens) and "judge_usage" (judge tokens)
  offline() -> None                 scripted-policy tests, no API calls; raises on failure
  analyse(records, out_dir, manifest) -> None

Storage: <exp>/runs/<split>/attempts.jsonl gets EVERY attempt, including errors. A key is done once it has an
attempt whose status is not "failed"; failed keys are retried on resume. `load()` returns, per key, the latest
non-failed attempt (or the latest failed one if there is no other), so partial action logs are never lost.
"""
from __future__ import annotations

import asyncio
import hashlib
import importlib
import json
import random
import shutil
from datetime import datetime, timezone
from pathlib import Path

from . import serving

PKG = Path(__file__).resolve().parents[1]           # designs/action_mechanisms
SHARED = Path(__file__).resolve().parent
ORIGINALS = [PKG.parent / "action" / f for f in ("env.py", "agent.py", "materials.py", "run.py", "score.py")]


def module(exp: str):
    return importlib.import_module(f"action_mechanisms.{exp}.design")


def out_dir(exp: str, split: str) -> Path:
    return PKG / exp / "runs" / split


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def digest(mod, items) -> str:
    body = [[i["key"], mod.render(i)] for i in items]
    return hashlib.sha256(json.dumps([body, serving.serving()], sort_keys=True, ensure_ascii=False,
                                     default=str).encode()).hexdigest()


def code_files(mod) -> list[Path]:
    exp_dir = PKG / mod.EXP
    return sorted(SHARED.glob("*.py")) + [exp_dir / f for f in mod.CODE] + [exp_dir / "HYPOTHESES.md"]


def code_hashes(mod) -> dict:
    return {str(p.relative_to(PKG.parent)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in code_files(mod) + ORIGINALS if p.exists()}


def attempts(exp: str, split: str) -> list[dict]:
    path = out_dir(exp, split) / "attempts.jsonl"
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def load(exp: str, split: str, items=None) -> list[dict]:
    rows = {}
    for r in attempts(exp, split):
        if r["key"] in rows and r["status"] == "failed" and rows[r["key"]]["status"] != "failed":
            continue
        rows[r["key"]] = r
    if items is not None:
        keys = {i["key"] for i in items}
        rows = {k: v for k, v in rows.items() if k in keys}
    return list(rows.values())


def record_cost(r: dict) -> float:
    return serving.cost(r.get("usage") or {}, r.get("model", "")) + serving.cost(r.get("judge_usage") or {}, "judge")


async def generate(exp: str, split: str, models: list[str] | None = None, max_inflight: int = 256):
    from .episode import model_policy
    mod = module(exp)
    items = mod.plan(split)
    if split == "main":
        check_frozen(mod, items)
    if models:
        items = [i for i in items if i["model"] in models]
    out = out_dir(exp, split)
    out.mkdir(parents=True, exist_ok=True)
    done = {r["key"] for r in attempts(exp, split) if r["status"] != "failed"}
    todo = [i for i in items if i["key"] not in done]
    random.Random(0).shuffle(todo)  # interleave conditions within each model
    policies = {m: model_policy(m) for m in sorted({i["model"] for i in todo})}
    sem, lock, n = asyncio.Semaphore(max_inflight), asyncio.Lock(), [0]
    path = out / "attempts.jsonl"
    print(f"{exp}/{split}: {len(todo)} to run ({len(done)} done)", flush=True)

    async def one(i):
        async with sem:
            t0 = now()
            try:
                rec = await mod.run(i, policies[i["model"]])
            except Exception as e:  # noqa: BLE001  (saved; retried on resume)
                rec = dict(status="failed", error=f"{type(e).__name__}: {str(e)[:300]}", usage={}, judge_usage={})
            rec = {k: v for k, v in i.items()} | rec | dict(started=t0, finished=now())
            async with lock:
                with path.open("a") as f:
                    f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
                n[0] += 1
                if n[0] % 10 == 0 or n[0] == len(todo):
                    print(f"  [{n[0]}/{len(todo)}] last: {i['key']} -> {rec['status']}", flush=True)

    await asyncio.gather(*(one(i) for i in todo))


def check_frozen(mod, items):
    m = out_dir(mod.EXP, "main") / "manifest.json"
    if not m.exists() or json.loads(m.read_text())["sha256"] != digest(mod, items):
        raise SystemExit(f"{mod.EXP}: main batch not frozen, or prompts/tools/serving changed since freezing")
    man = json.loads(m.read_text())
    changed = [f for f, h in code_hashes(mod).items() if man["code_sha256"].get(f) != h]
    if changed:
        raise SystemExit(f"{mod.EXP}: code changed since freezing: {changed}")


def freeze(exp: str):
    mod = module(exp)
    items = mod.plan("main")
    out = out_dir(exp, "main")
    m = out / "manifest.json"
    if m.exists():
        raise SystemExit("Already frozen; start a new, separately named run to change anything")
    out.mkdir(parents=True, exist_ok=True)
    snap = out / "code_snapshot"
    for p in code_files(mod) + ORIGINALS:
        if p.exists():
            dest = snap / p.relative_to(PKG.parent)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(p, dest)
    kinds = {}
    for i in items:
        kinds[i["kind"]] = kinds.get(i["kind"], 0) + 1
    m.write_text(json.dumps(dict(
        exp=exp, sha256=digest(mod, items), at=now(), total=len(items), counts_by_kind=kinds,
        cells=sorted({i["cell"] for i in items}), scenarios=sorted({i["scenario"] for i in items}),
        code_sha256=code_hashes(mod), serving=serving.serving(), serving_notes=serving.SERVING_NOTES,
        caps=serving.CAPS, shuffle_seed=0, label="PRE-REGISTERED main batch"), indent=2, default=str) + "\n")
    json.dump([dict(key=i["key"], render=mod.render(i)) for i in items], open(out / "prompts.json", "w"), indent=1,
              ensure_ascii=False, default=str)
    print(f"Frozen {exp}: {len(items)} items, sha {json.loads(m.read_text())['sha256'][:12]}")


def preview(exp: str, split: str, path: Path | None = None):
    """Write the rendering of one item per (cell, kind) for one model, for hand inspection."""
    mod = module(exp)
    seen, L = set(), [f"# {exp}: {split} renderings (one item per cell/kind, first model)", ""]
    for i in mod.plan(split):
        tag = (i["cell"], i["kind"], i["scenario"])
        if i["model"] != serving.labels()[0] or (i["cell"], i["kind"]) in {t[:2] for t in seen}:
            continue
        seen.add(tag)
        L += [f"## {i['kind']} | {i['cell']} | {i['scenario']}", "```json",
              json.dumps(mod.render(i), indent=1, ensure_ascii=False, default=str), "```", ""]
    path = path or out_dir(exp, split) / "PREVIEW.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(L) + "\n")
    print(f"wrote {path}")


def status(exp: str, split: str):
    import collections
    mod = module(exp)
    items = mod.plan(split)
    recs = load(exp, split, items)
    c = collections.Counter((r["model"], r["status"]) for r in recs)
    print(f"{exp}/{split}: {len(recs)}/{len(items)} keys recorded; attempts {len(attempts(exp, split))}; "
          f"cost ~${sum(record_cost(r) for r in attempts(exp, split)):.2f}")
    for k, v in sorted(c.items()):
        print(f"  {k}: {v}")
