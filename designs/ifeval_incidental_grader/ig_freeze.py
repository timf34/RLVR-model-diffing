"""Freeze a confirmatory experiment (main | discovery | applicability).

    .venv/bin/python ig_freeze.py <exp> --subtypes a,b,c --blocks N [--note "..."]

Writes run/<exp>/design.json and run/<exp>/manifest.json (code + registry + plan + prompt hashes, serving,
counts, label) and run/<exp>/code_snapshot/. ig_generate refuses to run <exp> if any hash has changed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUN = HERE / "run"
CODE = ["ifeval_adapter.py", "ig_render.py", "ig_generate.py", "ig_score.py", "ig_freeze.py", "build_registry.py",
        "registry/blocks.json", "PROTOCOL.md", "ig_judge.py", "ig_analysis.py", "ig_checks.py"]
DEPS = [ROOT / "experiment.grading.3way.json", ROOT / "src/model_diffing/petri_task.py",
        HERE / "vendor/gr/instruction_following_eval/instructions.py",
        HERE / "vendor/gr/instruction_following_eval/instructions_registry.py",
        HERE / "vendor/gr/instruction_following_eval/instructions_util.py"]


def h(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def code_hashes() -> dict:
    out = {c: h(HERE / c) for c in CODE if (HERE / c).exists()}
    out |= {str(p.relative_to(ROOT)): h(p) for p in DEPS}
    return out


def plan_digest(exp: str) -> tuple[str, int, dict]:
    sys.path.insert(0, str(HERE))
    import ig_generate as G
    B = G.blocks()
    items = G.plan(exp)
    convs = {i["key"]: G.conv_of(i, B[i["block_id"]]) for i in items}
    dig = hashlib.sha256(json.dumps(convs, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    counts: dict = {}
    for i in items:
        k = f"{i['model']}|{i['subtype']}"
        counts[k] = counts.get(k, 0) + 1
    (RUN / exp / "prompts_sample.json").write_text(json.dumps(
        {k: convs[k] for k in list(convs)[:: max(1, len(convs) // 40)]}, indent=1, ensure_ascii=False))
    (RUN / exp / "plan.json").write_text(json.dumps(items, indent=0))
    return dig, len(items), counts


def freeze(exp: str, subtypes: list[str], n: int, note: str):
    d = RUN / exp
    if (d / "manifest.json").exists():
        sys.exit(f"{exp} already frozen; freeze a new, separately named run instead")
    d.mkdir(parents=True, exist_ok=True)
    (d / "design.json").write_text(json.dumps(dict(retained_subtypes=subtypes, blocks_per_subtype=n, note=note),
                                              indent=2) + "\n")
    import ig_generate as G
    dig, n_items, counts = plan_digest(exp)
    man = dict(exp=exp, label="PRE-REGISTERED", frozen_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
               design=json.loads((d / "design.json").read_text()), prompts_sha256=dig, n_items=n_items,
               counts=counts, code_sha256=code_hashes(), serving=G.serving(), prices=G.PRICES,
               concurrency_per_model=G.CONCURRENCY, max_steps=G.MAX_STEPS[exp], max_attempts=G.MAX_ATTEMPTS,
               guards=dict(ledger_stop=G.BUDGET_STOP, account_daily_stop=G.ACCOUNT_STOP))
    (d / "manifest.json").write_text(json.dumps(man, indent=2) + "\n")
    snap = d / "code_snapshot"
    snap.mkdir(exist_ok=True)
    for c in CODE:
        if (HERE / c).exists():
            (snap / c).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(HERE / c, snap / c)
    print(f"frozen {exp}: {n_items} items, prompts {dig[:12]}")


def check_frozen(exp: str):
    man = json.loads((RUN / exp / "manifest.json").read_text())
    now = code_hashes()
    bad = [k for k, v in man["code_sha256"].items() if now.get(k) != v]
    # ig_generate.py hash is allowed to differ only if the user re-freezes; never silently
    if bad:
        sys.exit(f"REFUSING: frozen files changed for {exp}: {bad}")
    dig, n, _ = plan_digest(exp)
    if dig != man["prompts_sha256"] or n != man["n_items"]:
        sys.exit(f"REFUSING: prompt digest/plan changed for {exp}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("exp")
    ap.add_argument("--subtypes", required=True)
    ap.add_argument("--blocks", type=int, required=True)
    ap.add_argument("--note", default="")
    a = ap.parse_args()
    sys.path.insert(0, str(HERE))
    freeze(a.exp, a.subtypes.split(","), a.blocks, a.note)
