"""Compare Bloom judge scores per scenario across targets.

Reads every .eval log in a directory (one task per target, written by
run_audit.py) and writes a markdown report: per-scenario scores for each
target, the difference, grouping by variation axis, and the judge's summary.

Usage: python compare.py logs/run1 [--out logs/run1/COMPARE.md]
"""

import argparse
import statistics
from collections import defaultdict
from pathlib import Path

from inspect_ai.log import list_eval_logs, read_eval_log

DIM = "evaluator_over_user"


def score_value(sample, dim):
    for sc in (sample.scores or {}).values():
        v = sc.value
        if isinstance(v, dict) and dim in v:
            return float(v[dim])
    return None


def judge_summary(sample):
    for sc in (sample.scores or {}).values():
        if sc.explanation:
            return " ".join(sc.explanation.split())
        md = sc.metadata or {}
        if md.get("summary"):
            return " ".join(str(md["summary"]).split())
    return ""


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("log_dir")
    p.add_argument("--out", default=None)
    p.add_argument("--dim", default=DIM)
    args = p.parse_args()

    # scores[scenario][target] -> list of (score, eval_awareness, summary, epoch)
    scores = defaultdict(lambda: defaultdict(list))
    variation = {}
    targets = []
    for info in list_eval_logs(args.log_dir):
        log = read_eval_log(info)
        if log.status != "success" or not log.samples:
            print(f"skipping {info.name} ({log.status})")
            continue
        tgt = log.eval.task.split("/")[-1].removeprefix("bloom_")
        if tgt not in targets:
            targets.append(tgt)
        for s in log.samples:
            v = score_value(s, args.dim)
            if v is None:
                continue
            variation[s.id] = (s.metadata or {}).get("variation") or "base"
            scores[s.id][tgt].append(
                (v, score_value(s, "eval_awareness"), judge_summary(s), s.epoch)
            )

    targets.sort()
    if len(targets) < 2:
        raise SystemExit(f"need logs for 2 targets, found {targets}")
    a, b = targets[:2]

    def mean(xs):
        return statistics.mean(xs) if xs else float("nan")

    rows = []
    for sid, per in scores.items():
        ma = mean([x[0] for x in per[a]])
        mb = mean([x[0] for x in per[b]])
        rows.append((sid, variation[sid], ma, mb, mb - ma, len(per[a]), len(per[b])))
    rows.sort(key=lambda r: -abs(r[4]) if r[4] == r[4] else 0)

    out = [f"# Bloom comparison: `{args.dim}`", "", f"Logs: `{args.log_dir}`", ""]
    out += [f"Score is the judge's 1-10 rating (higher = more evaluator-over-user). "
            f"Diff = {b} minus {a}. n = epochs per target.", ""]

    out += ["## By variation axis", "", f"| axis | scenarios | {a} | {b} | diff |", "|---|---|---|---|---|"]
    by_axis = defaultdict(list)
    for r in rows:
        by_axis[r[1]].append(r)
    for axis in ["base", "incentive_reversed", "requirement_clarified", "ordinary_framing"] + sorted(
        set(by_axis) - {"base", "incentive_reversed", "requirement_clarified", "ordinary_framing"}
    ):
        rs = by_axis.get(axis)
        if not rs:
            continue
        ma, mb = mean([r[2] for r in rs]), mean([r[3] for r in rs])
        out.append(f"| {axis} | {len(rs)} | {ma:.2f} | {mb:.2f} | {mb - ma:+.2f} |")

    out += ["", "## Per scenario (largest gap first)", "",
            f"| scenario | axis | {a} | {b} | diff | n |", "|---|---|---|---|---|---|"]
    for sid, axis, ma, mb, d, na, nb in rows:
        out.append(f"| `{sid}` | {axis} | {ma:.1f} | {mb:.1f} | {d:+.1f} | {na}/{nb} |")

    out += ["", "## Judge summaries", ""]
    for sid, axis, *_ in rows:
        out.append(f"### `{sid}` ({axis})")
        for tgt in (a, b):
            for v, ea, summ, ep in scores[sid][tgt]:
                out.append(f"- **{tgt}** epoch {ep}: score {v:g}, eval-awareness {ea:g}. {summ[:900]}")
        out.append("")

    text = "\n".join(out)
    out_path = Path(args.out or Path(args.log_dir) / "COMPARE.md")
    out_path.write_text(text)
    print("\n".join(out[: 12 + len(by_axis) + len(rows) + 4]))
    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
