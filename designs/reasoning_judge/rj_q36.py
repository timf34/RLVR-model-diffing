"""Qwen 3.6 addendum to the reasoning judge (2026-10-31; not in the frozen plan).

Runs the frozen judge, rubric and view builder unchanged on the Qwen 3.6 sending episodes of the presentation
ablation's 3.6 addendum (designs/presentation_ablation/run_q36/main/send; same fresh blocks, arms B/N, scores
p050/tied). Output: run/main_q36/. Then merges main + main_q36 into run/main_3models/ for analysis and the figure.

  .venv/bin/python designs/reasoning_judge/rj_q36.py prepare     # items + views, freeze
  .venv/bin/python designs/reasoning_judge/rj_q36.py run         # judge (GPT-5.6 Terra)
  .venv/bin/python designs/reasoning_judge/rj_q36.py merge       # -> run/main_3models/{items,judge}.jsonl
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rj_common as C  # noqa: E402

Q36_RUN = C.ROOT / "designs" / "presentation_ablation" / "run_q36"
STAGE, MERGED = "main_q36", "main_3models"


def patch():
    import rj_judge as J
    C.PA_RUN = J.PA_RUN = Q36_RUN
    C.MODELS = ("Qwen 3.6",)
    C.STAGES[STAGE] = C.STAGES["main"]
    J.STAGES = C.STAGES
    return J


def main():
    cmd = sys.argv[1]
    if cmd in ("prepare", "run"):
        J = patch()
        if cmd == "prepare":
            J.prepare(STAGE)
            J.freeze(STAGE)
        else:
            asyncio.run(J.run(STAGE, None))
    elif cmd == "merge":
        for f in ("items.jsonl", "judge.jsonl"):
            rows = C.read_jsonl(C.RUN / "main" / f) + C.read_jsonl(C.RUN / STAGE / f)
            C.write_jsonl(C.RUN / MERGED / f, rows)
        print("merged", len(C.read_jsonl(C.RUN / MERGED / "items.jsonl")), "items")


if __name__ == "__main__":
    main()
