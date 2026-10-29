"""EXPLORATORY score-midpoint experiment (see ANALYSIS_PLAN.md). Run from this folder with memguard, e.g.
  M="$HOME/.claude/bin/memguard -m 4 -- ../../../.venv/bin/python"
  $M run_midpoint.py check             # materials checks (no API calls)
  $M run_midpoint.py inspect           # setup check: inspection-only scenarios, both models (generation)
  $M run_midpoint.py inspect-analyse   # inspection: judge + scoring + INSPECTION.md (separate process)
  $M run_midpoint.py freeze            # manifest + plan + prompts + code snapshot (before the main run)
  $M run_midpoint.py generate          # one <= ~9 min chunk, both models at once; repeat until 0 left
  $M run_midpoint.py status
  $M run_midpoint.py judge             # blind judge for ambiguous upsell openings only
  $M run_midpoint.py analyse           # run/results.json, run/REPORT_auto.md, figure/midpoint.png
Generation-side commands (check / inspect / freeze / generate / status) load designs/action modules; analysis-side
commands (inspect-analyse / judge / analyse) load designs/rl_context modules. The two never share a process.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import shutil
import sys
from collections import Counter
from datetime import datetime, timezone

from mid_design import HERE, INSPECT_OUT, OUT, ROOT

CODE = ["mid_design.py", "mid_materials.py", "mid_generate.py", "mid_analysis.py", "mid_report.py",
        "run_midpoint.py", "simulate.py", "ANALYSIS_PLAN.md", "simulation/CALIBRATION.md"]
DEPS = ["designs/score_gap/recommendation/gap_materials.py", "designs/recommendation/rec_materials.py",
        "designs/recommendation/rec_score.py", "designs/recommendation/run_rec.py",
        "designs/score_gap/sending/gap_materials.py", "designs/score_gap/sending/run_gap.py",
        "designs/action/materials.py", "designs/action/env.py", "designs/action/score.py", "designs/action/agent.py",
        "designs/rl_context/run_pilot.py", "designs/rl_context/run_confirm.py", "designs/rl_context/score.py",
        "src/model_diffing/core.py", "src/model_diffing/petri_task.py", "experiment.grading.3way.json"]
REL = "designs/score_gap/midpoint/"


def code_hashes():
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in [REL + f for f in CODE] + DEPS}


def manifest():
    return json.loads((OUT / "manifest.json").read_text())


def items_from(path):
    return json.loads(path.read_text())


def inspection_report(items):
    import mid_generate as MG
    L = ["# Inspection (setup check only; inspection-only scenarios, never in the main run)", "",
         "Checks: prompts render with the intended 2-decimal scores, calls go through on both models with the pinned "
         "serving, statuses are recorded, the scorers yield an outcome. The behaviour is NOT required to appear.", ""]
    recs = {r["key"]: r for r in MG.all_records(INSPECT_OUT)}
    ok = 0
    for i in items:
        r = recs.get(i["key"])
        if not r:
            L.append(f"- `{i['key']}` MISSING")
            continue
        shown = Counter(r.get("shown_scores", []))
        want = [] if i["pair"] == "none" else i["pair"].split("/")
        good = all(shown[w] >= 2 for w in want) and (want or not any(t.startswith(("0.1", "0.3", "0.7", "0.9"))
                                                                     for t in shown))
        ok += bool(good)
        L.append(f"- `{i['key']}` status **{r['status']}** · scores shown {dict(shown) or 'none'} "
                 f"({'ok' if good else 'MISMATCH'}) · out tokens {(r.get('usage') or {}).get('output_tokens')} · "
                 f"{'acted ' + str((r.get('measures') or {}).get('acted')) if i['env'] == 'send' else 'reply: ' + repr((r.get('reply') or '')[:90])}")
    L += ["", f"**Scores rendered as intended in {ok}/{len(items)}; statuses "
          f"{dict(Counter(r['status'] for r in recs.values()))}.**", ""]
    (INSPECT_OUT / "INSPECTION.md").write_text("\n".join(L) + "\n")
    print(L[-2])


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd in ("check", "inspect", "freeze", "generate", "status"):
        import mid_generate as MG
        import mid_materials as MM
        if cmd == "check":
            MM.check()
            return print(f"serving targets: {[t['label'] for t in MG.serving()['targets']]}")
        if cmd == "inspect":
            items = MM.inspection_plan()
            INSPECT_OUT.mkdir(exist_ok=True)
            (INSPECT_OUT / "plan.json").write_text(json.dumps(items, indent=0))
            if "--report" not in sys.argv:
                asyncio.run(MG.generate(items, INSPECT_OUT))
            return inspection_report(items)
        items = MM.plan()
        if cmd == "freeze":
            MM.check()
            OUT.mkdir(exist_ok=True)
            if (OUT / "manifest.json").exists():
                raise SystemExit("Already frozen")
            snap = OUT / "code_snapshot"
            for p in [REL + f for f in CODE] + DEPS:
                dst = snap / (p[len(REL):] if p.startswith(REL) else "deps/" + p)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(ROOT / p, dst)
            from mid_design import BUDGET, BUDGET_STOP, PAIRS, PRICES, SAMPLES
            (OUT / "plan.json").write_text(json.dumps(items, indent=0))
            json.dump([dict(key=i["key"], **MM.render(i)) for i in items if i["rep"] == 0 and i["model"] == "Qwen 3.5"],
                      open(OUT / "prompts.json", "w"), indent=1, ensure_ascii=False)
            (OUT / "manifest.json").write_text(json.dumps(dict(
                label="EXPLORATORY score-midpoint experiment (analysis plan frozen before generation)",
                sha256=MG.digest(items), at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                total=len(items), pairs=[list(p) for p in PAIRS], samples=SAMPLES,
                cells=Counter(f"{i['env']}|{i['panel']}|{i['pair']}" for i in items),
                upsell_scenarios=sorted({i["scenario"] for i in items if i["env"] == "upsell"}),
                send_scenarios=sorted({i["scenario"] for i in items if i["env"] == "send"}),
                plan_sha256=hashlib.sha256((HERE / "ANALYSIS_PLAN.md").read_bytes()).hexdigest(),
                plan_json_sha256=hashlib.sha256((OUT / "plan.json").read_bytes()).hexdigest(),
                code_sha256=code_hashes(), serving=MG.serving(), prices=PRICES, budget=BUDGET,
                budget_stop=BUDGET_STOP), indent=2) + "\n")
            return print(f"Frozen {len(items)} items -> {OUT / 'manifest.json'}")
        man = manifest()
        if man["sha256"] != MG.digest(items) or man["code_sha256"] != code_hashes():
            raise SystemExit("Prompts, serving or code changed since freezing")
        if cmd == "generate":
            return asyncio.run(MG.generate(items, OUT))
        if cmd == "status":
            st = Counter()
            for m in ("Qwen 3.5", "Qwen 3.8"):
                done, final, fails, inflight = MG.key_state(OUT, m)
                mine = [i for i in items if i["model"] == m]
                st[f"{m} final"] = sum(i["key"] in final for i in mine)
                st[f"{m} total"] = len(mine)
            print(dict(st), MG.spent(OUT, INSPECT_OUT))
            return
    if cmd in ("inspect-analyse", "judge", "analyse"):
        import mid_report as R
        if cmd == "inspect-analyse":
            items = items_from(INSPECT_OUT / "plan.json")
            R.judge(items, INSPECT_OUT)
            R.analyse(items, INSPECT_OUT, perms=500)
            rows = R.scored(items, INSPECT_OUT, R.load_judge(INSPECT_OUT))
            extra = ["## Scoring (analysis process)", ""] + [
                f"- `{r['key']}` completion **{r['completion']}** · y {r['y']} · strict {r.get('strict')}" for r in
                sorted(rows, key=lambda r: r["key"])]
            with (INSPECT_OUT / "INSPECTION.md").open("a") as f:
                f.write("\n".join(extra) + "\n")
            return R.figure(INSPECT_OUT, "inspection.png")
        man = manifest()
        R.check_code_unchanged(man)
        items = items_from(OUT / "plan.json")
        assert hashlib.sha256((OUT / "plan.json").read_bytes()).hexdigest() == man["plan_json_sha256"]
        if cmd == "judge":
            return R.judge(items, OUT)
        R.analyse(items, OUT, man)
        return R.figure(OUT)
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
