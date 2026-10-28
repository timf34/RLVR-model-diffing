"""Disclosed deviation wrapper (not part of the frozen, hashed code): run the frozen analysis on Qwen 3.5 and 3.8
only, while Qwen 3.6 is still generating.

- Uses run_gap.analyse / run_gap.figure unchanged on the 3.5 and 3.8 items.
- Holm is kept over the FULL planned families (9 trend tests, 18 curve comparisons): every planned test that is
  missing because 3.6 is pending enters the correction with p = 1. This is done by wrapping gap_analysis.holm in
  this process only; no frozen file is edited.
- Outputs are renamed so the full analysis can later write the planned file names:
    run/REPORT_auto_3.5_3.8.md, run/results_3.5_3.8.json, figure/score_gap_curve_3.5_3.8.png
Run: ~/.claude/bin/memguard -m 3 -- .venv/bin/python designs/score_gap/recommendation/analyse_subset.py
"""
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.argv = ["analyse_subset"]
sys.path.insert(0, str(HERE))
import run_gap as RG  # noqa: E402

A, G = RG.A, RG.G
TREND_FAMILY = [f"{m}|{p}" for m in RG.MODELS for p in G.PANELS]
COMPARE_FAMILY = ([f"model|{p}|{a} vs {b}" for p in G.PANELS for a, b in RG.MODEL_PAIRS]
                  + [f"panel|{m}|{a} vs {b}" for m in RG.MODELS for a, b in RG.PANEL_PAIRS])
assert len(TREND_FAMILY) == 9 and len(COMPARE_FAMILY) == 18
_holm = A.holm


def padded_holm(ps: dict) -> dict:
    family = TREND_FAMILY if all("|" in k and not k.startswith(("model|", "panel|")) for k in ps) else COMPARE_FAMILY
    assert set(ps) <= set(family), set(ps) - set(family)
    full = {k: ps.get(k, 1.0) for k in family}  # pending (Qwen 3.6) tests count as p = 1
    return _holm(full)


A.holm = padded_holm


def main():
    items = [i for i in RG.plan() if i["model"] in ("Qwen 3.5", "Qwen 3.8")]
    manifest = json.loads((RG.OUT / "manifest.json").read_text())
    full_items = RG.plan()
    assert RG.P.digest(full_items, RG.R.serving()) == manifest["sha256"], "prompts/serving changed since freezing"
    RG.analyse(items, RG.OUT, manifest)
    RG.figure(RG.OUT)
    shutil.move(RG.OUT / "REPORT_auto.md", RG.OUT / "REPORT_auto_3.5_3.8.md")
    shutil.move(RG.OUT / "results.json", RG.OUT / "results_3.5_3.8.json")
    shutil.move(HERE / "figure" / "score_gap_curve.png", HERE / "figure" / "score_gap_curve_3.5_3.8.png")
    print("Wrote run/REPORT_auto_3.5_3.8.md, run/results_3.5_3.8.json, figure/score_gap_curve_3.5_3.8.png")


if __name__ == "__main__":
    main()
