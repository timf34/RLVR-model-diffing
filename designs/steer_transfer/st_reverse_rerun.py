"""Within-session sensitivity for the reverse transfer (AMENDMENTS_reverse.md #1).

  .venv/bin/python designs/steer_transfer/st_reverse_rerun.py prepare
  ~/.claude/bin/memguard -m 6 -- .venv/bin/python designs/steer_transfer/st_reverse_rerun.py generate --endpoints <json>
  .venv/bin/python designs/steer_transfer/st_reverse_rerun.py analyse

Re-generates the five REUSED 3.8 conditions (none, native +/-0.1, +/-0.3) on all arms, same blocks, reps and seeds,
into run/reverse_rerun; the analysis is st_reverse.analyse with these cells substituted for run/main's 3.8 cells
(3.5's cells for the cross-model contrast still come from run/main). st_reverse.py is not modified.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import st_reverse as R
from st_common import RUN, iter_jsonl, jhash

STAGE = "reverse_rerun"


def prepare():
    src = R.stage_dir(RUN, "main")
    items = [dict(i, key=i["key"].replace("st|main|", f"st|{STAGE}|"), stage=STAGE)
             for i in iter_jsonl(src / "items.jsonl") if i["model"] == R.T and i["cond"] in R.REUSED]
    assert len(items) == 3520
    d = R.stage_dir(RUN, STAGE)
    d.mkdir(parents=True, exist_ok=True)
    with (d / "items.jsonl").open("w") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    used = {i["input_sha256"] for i in items}
    with (d / "prompts.jsonl").open("w") as f:
        for p in iter_jsonl(src / "prompts.jsonl"):
            if p["input_sha256"] in used:
                f.write(json.dumps(p, ensure_ascii=False) + "\n")
    shutil.copy(src / "blocks.json", d / "blocks.json")
    (d / "prepare.json").write_text(json.dumps(dict(stage=STAGE, n_items=len(items),
                                                    items_digest=jhash([[i["key"], i["input_sha256"]] for i in items]))))
    print(f"{STAGE}: {len(items)} items")


def analyse(B=4000):
    orig = R.score

    def score(root, stage):
        if stage == "main" and R.T == "Qwen 3.8":
            return [dict(r, stage="main") for r in orig(root, STAGE)]
        return orig(root, stage)
    R.score = score
    try:
        res = R.analyse(RUN, B)
    finally:
        R.score = orig
    res["note"] = "SENSITIVITY: all Qwen 3.8 cells from this session (run/reverse + run/reverse_rerun)"
    (RUN / STAGE / "results.json").write_text(json.dumps(res, indent=1))
    md = "# SENSITIVITY (within-session 3.8 cells)\n\n" + R.report(res)
    (RUN / STAGE / "REPORT_auto.md").write_text(md)
    print(md[:3000])


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "prepare":
        prepare()
    elif cmd == "generate":
        ep = sys.argv[sys.argv.index("--endpoints") + 1]
        R.generate(STAGE, RUN, {R.T: json.loads(Path(ep).read_text())[R.T]}, 64, None, 120)
    elif cmd == "analyse":
        analyse()
