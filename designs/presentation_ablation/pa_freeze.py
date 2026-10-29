"""Freeze / verify a stage: manifest with code hashes, prompt hashes and plan digests (no API calls).

  python pa_freeze.py freeze main      # writes run/main/manifest.json (PROTOCOL.md must exist)
  python pa_freeze.py verify main      # recomputes everything; exits non-zero on any change

The manifest hashes: every file of this study, every old file the renderers/scorers/checks import or compare against
(designs/action, score_gap/{sending,formatting} materials + frozen prompts/manifests, rl_context materials/scorers,
the IFEval renderer, 10A's blocks + inputs), the serving config; per task the item list ([key, input_sha256]) and
the set of unique prompt hashes; each stored prompt is re-hashed from its content on verify. pa_generate refuses to
run main/factorial unless verify passes.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pa_common import (ACTION, FORMATTING, GAPS, HERE, IG, MAX_STEPS, MODELS, PRICES, PRIMARY_TASKS, REFCHECK, RL,
                       ROOT, RUN, SENDING, SERVING_CONFIG, TASKS, iter_jsonl, jhash, now, rel, serving, sha)
from pa_design import FRESH_REPS, N_FRESH, ORIG_REPS, plan
from pa_render import all_arms, factorial_arms

OWN = ["pa_common.py", "pa_blocks.py", "pa_materials.py", "pa_render.py", "pa_checks.py", "pa_design.py",
       "pa_prepare.py", "pa_freeze.py", "pa_generate.py", "pa_score.py", "pa_analysis.py", "pa_figures.py",
       "pa_tests.py", "simulation/simulate.py", "PROTOCOL.md"]
OLD = ([ACTION / f for f in ("materials.py", "env.py", "score.py", "agent.py")]
       + [SENDING / f for f in ("gap_materials.py", "run/manifest.json", "run/prompts.json")]
       + [FORMATTING / f for f in ("fmt_materials.py", "run/manifest.json", "run/prompts.json")]
       + [RL / f for f in ("confirm_materials.py", "confirm_score.py", "emdash_materials.py", "score.py",
                           "domains/structure.py")]
       + [IG / "ig_render.py", REFCHECK / "ref_blocks.py", REFCHECK / "run/send/inputs.json",
          REFCHECK / "run/fmt/inputs.json", SERVING_CONFIG])


def file_hashes(root: Path) -> dict:
    files = [HERE / f for f in OWN] + OLD
    sel = root / "factorial" / "selection.json"
    if sel.exists():
        files.append(sel)
    return {rel(p): sha(p.read_bytes()) for p in files}


def stage_digests(stage: str, root: Path) -> dict:
    out = {}
    units = json.loads((root / "units.json").read_text())
    planned = plan(stage, units, root)
    for task in TASKS:
        d = root / stage / task
        if not (d / "items.jsonl").exists():
            continue
        rows = list(iter_jsonl(d / "items.jsonl"))
        hashes = set()
        for p in iter_jsonl(d / "prompts.jsonl"):
            assert jhash(p["input"]) == p["input_sha256"], f"{stage}/{task}: prompt content does not match its hash"
            hashes.add(p["input_sha256"])
        assert {r["input_sha256"] for r in rows} == hashes, f"{stage}/{task}: items and prompts disagree"
        assert [r["key"] for r in rows] == [i["key"] for i in planned if i["task"] == task], \
            f"{stage}/{task}: items differ from the plan"
        out[task] = dict(n_items=len(rows), n_prompts=len(hashes),
                         items_digest=jhash([[r["key"], r["input_sha256"]] for r in rows]),
                         prompts_digest=jhash(sorted(hashes)),
                         blocks_sha256=sha((d / "blocks.json").read_bytes()))
    assert out, f"no prepared tasks under {root / stage}"
    return out


def design_info(stage: str, root: Path) -> dict:
    info = dict(stage=stage, tasks=list(TASKS), primary_tasks=list(PRIMARY_TASKS), models=list(MODELS), gaps=GAPS,
                n_fresh=N_FRESH, orig_reps=ORIG_REPS, fresh_reps=FRESH_REPS, max_steps=MAX_STEPS, prices=PRICES, serving=serving())
    if stage == "factorial":
        sel = json.loads((root / "factorial" / "selection.json").read_text())
        info["selection"] = sel
        info["arms"] = factorial_arms(sel["components"], sel.get("others", "B"))
    else:
        info["arms"] = all_arms()
    return info


def freeze(stage: str, root: Path):
    assert (HERE / "PROTOCOL.md").exists(), "write PROTOCOL.md first"
    man = dict(at=now(), label=f"presentation ablation, stage {stage}, frozen before generation",
               design=design_info(stage, root), files=file_hashes(root), inputs=stage_digests(stage, root))
    p = root / stage / "manifest.json"
    p.write_text(json.dumps(man, indent=1))
    print(f"frozen {stage}: {sha(p.read_bytes())[:12]} " +
          ", ".join(f"{t} {v['n_items']} items/{v['n_prompts']} prompts" for t, v in man["inputs"].items()))


def verify(stage: str, root: Path) -> dict:
    p = root / stage / "manifest.json"
    assert p.exists(), f"{stage} is not frozen ({p})"
    man = json.loads(p.read_text())
    cur = file_hashes(root)
    bad = [k for k in man["files"] if cur.get(k) != man["files"][k]]
    assert not bad, f"files changed since freeze: {bad}"
    assert stage_digests(stage, root) == man["inputs"], "inputs changed since freeze"
    assert json.loads(json.dumps(design_info(stage, root))) == man["design"], "design/serving changed since freeze"
    return man


def main():
    sys.path.insert(0, str(HERE))
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["freeze", "verify"])
    ap.add_argument("stage", choices=["smoke", "main", "factorial"])
    ap.add_argument("--root", default=str(RUN))
    a = ap.parse_args()
    root = Path(a.root)
    if a.cmd == "freeze":
        freeze(a.stage, root)
    else:
        man = verify(a.stage, root)
        print(f"verify {a.stage}: OK (frozen {man['at']}; " +
              ", ".join(f"{t} {v['n_items']}" for t, v in man["inputs"].items()) + ")")


if __name__ == "__main__":
    main()
