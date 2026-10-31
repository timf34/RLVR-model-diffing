"""Qwen 3.6 addendum to the score-gap sending curve (2026-10-31). Not part of the frozen run.

Same plan as run/ (12 scenarios; bundle 6 and ordinary 2 samples per scenario x level, incl. no-history and the
original-score reference), same renderer, episode loop and settings (run_gap.py, imported unchanged). Qwen 3.6 is
served as in every earlier 3.6 run (experiment.grading.3way.json: Alibaba only, no fallbacks).

  memguard -m 4 -- ../../../.venv/bin/python run_gap_q36.py generate    # -> run_q36/gen/Qwen_3.6/episodes.jsonl
  ../../../.venv/bin/python run_gap_q36.py status
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_gap as R  # noqa: E402

LABEL = "Qwen 3.6"
OUT = HERE / "run_q36"
R.MODELS = (LABEL,)
R.PRICES[LABEL] = (0.45, 2.7)


def main():
    items = R.plan()
    assert len(items) == 864 and all(i["model"] == LABEL for i in items)
    if sys.argv[1] == "generate":
        asyncio.run(R.generate(items, OUT, LABEL, 32))
    else:
        recs = R.latest(OUT, items)
        print(len(recs), "records;", sum(R.completion(e) == "valid" for e in recs), "valid; $%.2f" % R.spent(OUT))


if __name__ == "__main__":
    main()
