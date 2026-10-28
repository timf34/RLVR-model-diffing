"""Run the adversarial answer set against the REAL judge and write runs/inspection/judge_adversarial.md.

Run from designs/action_mechanisms/:
  caffeinate -i ~/.claude/bin/memguard -m 3 -- ../../.venv/bin/python attribution/run_adversarial.py
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # designs/ -> package `action_mechanisms`

from action_mechanisms.attribution import adversarial, design, rubric  # noqa: E402
from action_mechanisms.attribution.scenarios import BY_ID  # noqa: E402
from action_mechanisms.shared import judge, serving  # noqa: E402


async def main():
    async def one(case):
        name, sid, action, answer, exp = case
        s = BY_ID[sid]
        out = await judge.label(rubric.judge_prompt(s, action, design.tool_result(s, action), answer), rubric.SCHEMA)
        got = out["labels"] or {}
        bad = {k: (v, got.get(k)) for k, v in exp.items() if got.get(k) != v}
        return dict(name=name, scenario=sid, action=action, answer=answer, expected=exp, got=got,
                    justification=out["justification"], fails=bad, usage=out["usage"])
    res = await asyncio.gather(*(one(c) for c in adversarial.CASES))
    cost = sum(serving.cost(r["usage"], "judge") for r in res)
    n_fail = sum(bool(r["fails"]) for r in res)
    L = ["# Judge adversarial set (real judge)", "",
         f"{len(res)} cases, {n_fail} with at least one label differing from the expected label. "
         f"Judge cost ${cost:.3f}.", "",
         "| case | action | expected | got | result |", "|---|---|---|---|---|"]
    for r in res:
        L.append(f"| {r['name']} | {r['action']} | {json.dumps(r['expected'])} | {json.dumps(r['got'])} | "
                 f"{'FAIL ' + json.dumps(r['fails']) if r['fails'] else 'pass'} |")
    L += ["", "## Answers and judge justifications", ""]
    for r in res:
        L += [f"**{r['name']}** ({r['scenario']}, {r['action']}): {r['answer']!r}", "",
              f"judge: {r['justification']}", ""]
    out = Path(__file__).resolve().parent / "runs" / "inspection" / "judge_adversarial.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L) + "\n")
    print(f"{n_fail}/{len(res)} cases failed; cost ${cost:.3f}; wrote {out}")


if __name__ == "__main__":
    asyncio.run(main())
