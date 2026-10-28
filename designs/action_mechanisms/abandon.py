"""Operational helper (not part of any frozen experiment): record stuck items as non-valid after their process was
stopped, so analyses count them as failed / not observed instead of waiting indefinitely.

  ../../.venv/bin/python abandon.py <exp> <split> "<reason>"

Appends one attempt per planned key that has no attempt at all, with status "failed" and the reason. Existing
attempts are never modified. Resuming `generate` later would retry these keys; we deliberately don't.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from action_mechanisms.shared import runner  # noqa: E402


def main():
    exp, split, reason = sys.argv[1], sys.argv[2], sys.argv[3]
    mod = runner.module(exp)
    have = {r["key"] for r in runner.attempts(exp, split)}
    missing = [i for i in mod.plan(split) if i["key"] not in have]
    path = runner.out_dir(exp, split) / "attempts.jsonl"
    with path.open("a") as f:
        for i in missing:
            rec = dict(i) | dict(status="failed", error=f"abandoned: {reason}", usage={}, judge_usage={},
                       abandoned=True, started=None, finished=runner.now())
            f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
    print(f"{exp}/{split}: recorded {len(missing)} abandoned item(s): {[i['key'] for i in missing]}")


if __name__ == "__main__":
    main()
