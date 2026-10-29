"""Status manifest for workstream C (repo .venv):  .venv/bin/python ig_status.py
Writes STATUS.json + STATUS.md from durable files and live processes (counts only; no outcome rates)."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ig_generate as G  # noqa: E402

EXPS = ["smoke", "dev", "main", "applicability", "discovery"]


def procs() -> list[str]:
    out = subprocess.run(["ps", "-axo", "pid=,etime=,command="], capture_output=True, text=True).stdout
    return [l.strip() for l in out.splitlines() if "ifeval_incidental_grader" in l and "python" in l
            and "ig_status" not in l]


def main():
    now = datetime.now(timezone.utc)
    st, live = {}, procs()
    for e in EXPS:
        d = G.RUN / e
        if not d.exists():
            continue
        recs = G.load_records(e)
        try:
            planned = len(G.plan(e))
        except Exception:  # noqa: BLE001
            planned = None
        ok = {r["key"] for r in recs if r["status"] != "error"}
        failed = {r["key"] for r in recs if r["status"] == "error"} - ok
        ts = sorted(r["at"] for r in recs)
        man = d / "manifest.json"
        stage = "frozen" if man.exists() else ("done-unfrozen" if e in ("smoke", "dev") else "implementing")
        running = [p for p in live if f"ig_generate.py {e}" in p or f"ig_judge.py {e}" in p]
        if running:
            stage = "generating" if any("ig_generate" in p for p in running) else "scoring"
        if (d / "results.json").exists() and not running:
            stage = "analysed"
        rate = None
        if len(ts) > 50:
            t0 = datetime.fromisoformat(ts[0])
            t1 = datetime.fromisoformat(ts[-1])
            rate = len(ok) / max(1.0, (t1 - t0).total_seconds() / 60)
        eta = None
        if rate and planned and len(ok) < planned:
            eta = (now.timestamp() + (planned - len(ok)) / rate * 60)
            eta = datetime.fromtimestamp(eta, timezone.utc).isoformat(timespec="minutes")
        st[e] = dict(stage=stage, run_id=(json.loads(man.read_text())["prompts_sha256"][:12] if man.exists() else None),
                     processes=running, first_response=ts[0] if ts else None, latest_response=ts[-1] if ts else None,
                     planned=planned, completed=len(ok), failed_unresolved=len(failed),
                     attempts=len(recs), spend_usd=round(sum(r.get("cost", 0) for r in recs), 4),
                     rate_per_min=round(rate, 1) if rate else None, eta_utc=eta)
    out = dict(workstream="C: IFEval framing x grader evidence", updated=now.isoformat(timespec="seconds"),
               ledger_total_usd=round(G.ledger_total(), 4), experiments=st)
    (HERE / "STATUS.json").write_text(json.dumps(out, indent=1) + "\n")
    lines = [f"# Workstream C status ({out['updated']})", "", f"Ledger total (generation + judge): ${out['ledger_total_usd']:.2f}", "",
             "| exp | stage | run id | planned | completed | failed | spend $ | first | latest | ETA |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for e, s in st.items():
        lines.append(f"| {e} | {s['stage']} | {s['run_id']} | {s['planned']} | {s['completed']} | {s['failed_unresolved']} | "
                     f"{s['spend_usd']:.2f} | {s['first_response']} | {s['latest_response']} | {s['eta_utc']} |")
    lines += ["", "Processes:"] + [f"- `{p[:160]}`" for p in live]
    (HERE / "STATUS.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
