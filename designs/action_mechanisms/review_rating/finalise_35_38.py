"""Deviation wrapper (NOT a hashed file): run the FROZEN review_rating analysis on Qwen 3.5 and 3.8 only, while Qwen 3.6
is still generating. Requested by the user on 2026-10-28.

- Uses the frozen analysis.analyse unchanged, on the latest attempt per key for the 3.5 and 3.8 main items.
- Qwen 3.6 rows are excluded, so its tests see no data. Pending 3.6 tests count as p = 1 and stay in every Holm
  family, which keeps the planned family sizes (6 primaries, 3 per secondary family, ...). That is conservative: Holm
  multipliers depend on the family size.
  - The frozen mean tests (P1, P2, S2-S5) already return p = 1 when there is no data.
  - shared stats.directional / interaction_test return NaN on empty groups, and stats.holm silently DROPS NaN. In this
    process only, the wrapper replaces those two functions' results with p = 1 (est and CI NaN) when a group has no
    data. Non-empty groups go through the unchanged functions.
- Writes to runs/main_3.5_3.8/, never to runs/main/, so the full analysis can later run on all three models.

From designs/action_mechanisms/:
  ~/.claude/bin/memguard -m 3 -- ../../.venv/bin/python review_rating/finalise_35_38.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from action_mechanisms.shared import runner  # noqa: E402
from action_mechanisms.review_rating import analysis, design  # noqa: E402

MODELS = ("Qwen 3.5", "Qwen 3.8")
NAN = float("nan")


def _has(counts, g):
    return any(k[0] == g and v[1] for k, v in counts.items())


def _patch():
    st = analysis.stats
    d0, i0, c0 = st.directional, st.interaction_test, st.calibrate_interaction

    def directional(counts, ga, gb, *a, **k):
        if not (_has(counts, ga) and _has(counts, gb)):
            return dict(a="0/0", b="0/0", est=NAN, p=1.0, ci=[NAN, NAN], passed=False, note="pending (no data)")
        return d0(counts, ga, gb, *a, **k)

    def _groups(counts, m1, m2):
        return any(k[0][0] == m1 for k in counts) and any(k[0][0] == m2 for k in counts)

    def interaction_test(counts, m1, m2, c1, c2, *a, **k):
        if not _groups(counts, m1, m2):
            return dict(est=NAN, p=1.0, ci=[NAN, NAN], note="pending (no data)")
        return i0(counts, m1, m2, c1, c2, *a, **k)

    def calibrate_interaction(counts, m1, m2, c1, c2, *a, **k):
        if not _groups(counts, m1, m2):
            return dict(size="pending", sims=0)
        return c0(counts, m1, m2, c1, c2, *a, **k)
    st.directional, st.interaction_test, st.calibrate_interaction = directional, interaction_test, calibrate_interaction


def main():
    _patch()
    items = [i for i in design.plan("main") if i["model"] in MODELS]
    recs = runner.load("review_rating", "main", items)
    man = json.loads((runner.out_dir("review_rating", "main") / "manifest.json").read_text())
    man["code_changed_since_freeze"] = [f for f, h in runner.code_hashes(design).items()
                                        if man["code_sha256"].get(f) != h]
    missing = len(items) - len(recs)
    out = runner.out_dir("review_rating", "main_3.5_3.8")
    out.mkdir(parents=True, exist_ok=True)
    print(f"{len(recs)}/{len(items)} records for {MODELS}; missing {missing}; code changed: "
          f"{man['code_changed_since_freeze']}")
    analysis.analyse(recs, out, man)


if __name__ == "__main__":
    main()
