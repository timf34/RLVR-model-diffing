"""Request-wording experiment (see PROPOSAL.md, HYPOTHESES.md, materials.py, analysis.py).

Same serving, generation and record loading as the rl_context confirmation batch (run_confirm.py, read-only):
experiment.grading.3way.json, temperature 0.7, max tokens 32768, each model writes its own
runs/<run>/gen/<model>/generations.jsonl.

Run from the repo root (wrap live runs in ~/.claude/bin/memguard -m 3 -- ...):
  .venv/bin/python designs/wording/run.py inspect "Qwen 3.8" 15     # held-out task, 30 per model; one process per model
  .venv/bin/python designs/wording/run.py freeze                    # refuses while HYPOTHESES.md line 1 says DRAFT
  .venv/bin/python designs/wording/run.py generate "Qwen 3.6" 24    # main run, one process per model
  .venv/bin/python designs/wording/run.py analyse main              # or: analyse inspection
"""
import hashlib
import importlib.util
import itertools
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
RL = HERE.parent / "rl_context"
sys.path.insert(0, str(RL))
# run_confirm -> run_pilot imports rl_context/materials.py as `materials`; import it before our materials.py,
# which is loaded under a distinct module name so the two never collide.
import run_confirm as R  # noqa: E402
import run_pilot as P  # noqa: E402


def _load(name: str, file: str):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


W = _load("wording_materials", "materials.py")

RUNS = HERE / "runs"
SAMPLES = 2
HYPOTHESES = HERE / "HYPOTHESES.md"
CODE = {  # hashed into the manifest and copied into the snapshot
    "materials.py": HERE / "materials.py", "run.py": HERE / "run.py", "analysis.py": HERE / "analysis.py",
    "rl_context/emdash_materials.py": RL / "emdash_materials.py",
    "rl_context/confirm_materials.py": RL / "confirm_materials.py",
    "rl_context/emdash_score.py": RL / "emdash_score.py", "rl_context/score.py": RL / "score.py",
    "rl_context/run_confirm.py": RL / "run_confirm.py", "rl_context/run_pilot.py": RL / "run_pilot.py",
}


def item(set_, task, presentation, wording, scores, model, rep) -> dict:
    return dict(key=f"{set_}|{task['id']}|{presentation}|{wording}|{scores}|{model}|{rep}", set=set_,
                scenario=task["id"], domain=task["domain"], feature=W.FEATURE, context=presentation, user=wording,
                presentation=presentation, wording=wording, scores=scores, model=model, rep=rep,
                facts=task["facts"], **W.render(task, presentation, wording, scores))


def plan(tasks=None, samples=SAMPLES, set_="main") -> list[dict]:
    tasks = W.TASKS if tasks is None else tasks
    return [item(set_, t, p, w, s, m, r)
            for t, p, w, s, m, r in itertools.product(tasks, W.PRESENTATIONS, W.WORDINGS, W.SCORES, R.labels(),
                                                      range(samples))]


def inspection_plan() -> list[dict]:
    return plan([W.INSPECTION_TASK], 1, "inspect")


def code_hashes() -> dict:
    return {k: hashlib.sha256(p.read_bytes()).hexdigest() for k, p in CODE.items()}


def write_preview(out: Path, items):
    lines = ["# Request-wording prompts preview (inspection task, first model, rewarded scores)", ""]
    first = R.labels()[0]
    for i in items:
        if i["model"] == first and i["scores"] == "rewarded" and (i["wording"] == "W1" or i["presentation"] == "rl/direct"):
            lines += [f"## {i['presentation']} | {i['wording']}", "", "SYSTEM:", "```text", i["system"], "```",
                      "USER:", "```text", i["turns"][0], "```", ""]
    out.mkdir(parents=True, exist_ok=True)
    (out / "prompts_preview.md").write_text("\n".join(lines))


def inspect_report():
    """runs/inspection/REPORT.md: one row per conversation, then a short count summary."""
    import emdash_score as S
    from collections import Counter
    out = RUNS / "inspection"
    items = inspection_plan()
    recs = {r["key"]: r for r in R.load_records(out, items)}
    order = {m: i for i, m in enumerate(R.labels())}
    rows, comp = [], Counter()
    L = ["# Request wording: inspection report", "",
         f"Held-out task `{W.INSPECTION_TASK['id']}`, one sample per cell ({len(items)} planned, {len(recs)} recorded).",
         "Completion: valid / empty / truncated / failed (score.completion). Measures only on valid completions.", "",
         "| model | presentation | wording | scores | completion | em dash | dashes | any dash punct. | words | "
         "facts_ok | first 80 chars |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for i in sorted(items, key=lambda i: (order[i["model"]], W.PRESENTATIONS.index(i["presentation"]),
                                          i["wording"], i["scores"])):
        r = recs.get(i["key"])
        c = S.completion(r["reply"] or "", r["status"]) if r else "missing"
        comp[(i["model"], c)] += 1
        m = S.measures(r["reply"], W.FEATURE, i["facts"]) if c == "valid" else None
        head = (r["reply"] or "").strip().replace("\n", " ⏎ ").replace("|", "\\|")[:80] if r else ""
        yn = lambda b: "yes" if b else "no"  # noqa: E731
        L.append(f"| {i['model']} | {i['presentation']} | {i['wording']} | {i['scores']} | {c} | "
                 + (f"{yn(m['adopted'])} | {m['dashes']} | {yn(m['violates'])} | {m['words']} | {yn(m['facts_ok'])}"
                    if m else "- | - | - | - | -") + f" | {head} |")
        rows.append(dict(i=i, c=c, m=m))
    L += ["", "## Counts", ""]
    for mdl in R.labels():
        v = [x for x in rows if x["i"]["model"] == mdl and x["m"]]
        cs = {c: n for (mm, c), n in comp.items() if mm == mdl}
        L.append(f"- **{mdl}**: completion {cs}; em dash in {sum(x['m']['adopted'] for x in v)}/{len(v)} valid "
                 f"(rewarded {sum(x['m']['adopted'] for x in v if x['i']['scores'] == 'rewarded')}/"
                 f"{sum(x['i']['scores'] == 'rewarded' for x in v)}, penalised "
                 f"{sum(x['m']['adopted'] for x in v if x['i']['scores'] == 'penalised')}/"
                 f"{sum(x['i']['scores'] == 'penalised' for x in v)}); facts_ok "
                 f"{sum(x['m']['facts_ok'] for x in v)}/{len(v)}; under 80 words {sum(x['m']['within_limit'] for x in v)}"
                 f"/{len(v)}; output tokens max {max((recs[x['i']['key']]['private'] or [{}])[0].get('output_tokens', 0) or 0 for x in rows if x['i']['model'] == mdl and x['i']['key'] in recs)}")
    (out / "REPORT.md").write_text("\n".join(L) + "\n")
    print(f"wrote {out / 'REPORT.md'}")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "inspect":
        if len(sys.argv) < 3 or sys.argv[2] not in R.labels():
            raise SystemExit(f"usage: inspect <model> [concurrency]; models: {R.labels()}")
        items, out = inspection_plan(), RUNS / "inspection"
        write_preview(out, items)
        R.run_generate(items, out, sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 15)
        return print(f"inspection {sys.argv[2]}: {sum(r['model'] == sys.argv[2] for r in R.load_records(out, items))}"
                     f" records -> {out}")
    if cmd == "inspect-report":
        return inspect_report()
    if cmd == "analyse":
        run = sys.argv[2] if len(sys.argv) > 2 else "main"
        out = RUNS / run
        items = inspection_plan() if run == "inspection" else plan()
        manifest = {}
        if run != "inspection":
            mpath = out / "manifest.json"
            if not mpath.exists() or json.loads(mpath.read_text())["sha256"] != P.digest(items, R.serving()):
                raise SystemExit("Not frozen, or prompts/serving changed since freezing")
            manifest = json.loads(mpath.read_text())
        A = _load("wording_analysis", "analysis.py")
        return A.analyse(R.load_records(out, items), out, manifest, code_hashes(), run=run)
    items, srv = plan(), R.serving()
    out = RUNS / "main"
    manifest = out / "manifest.json"
    if cmd == "freeze":
        hyp = HYPOTHESES.read_text()
        if "DRAFT" in hyp.splitlines()[0]:
            raise SystemExit("HYPOTHESES.md is still a draft (first line says DRAFT); finalise it before freezing")
        out.mkdir(parents=True, exist_ok=True)
        if manifest.exists():
            raise SystemExit("Already frozen; start a new, separately named run to change anything")
        snap = out / "code_snapshot"
        (snap / "rl_context").mkdir(parents=True, exist_ok=True)
        for k, p in list(CODE.items()) + [("HYPOTHESES.md", HYPOTHESES)]:
            shutil.copy(p, snap / k)
        manifest.write_text(json.dumps(dict(
            sha256=P.digest(items, srv), label="Request wording x grader accommodation (discovery-labelled)",
            at=datetime.now(timezone.utc).isoformat(timespec="seconds"), samples=SAMPLES, total=len(items),
            counts={m: sum(i["model"] == m for i in items) for m in R.labels()},
            hypotheses_sha256=hashlib.sha256(hyp.encode()).hexdigest(), code_sha256=code_hashes(),
            serving=srv, serving_notes=R.SERVING_NOTES), indent=2) + "\n")
        json.dump([{k: i[k] for k in ("key", "system", "turns", "facts")} for i in items],
                  open(out / "prompts.json", "w"), indent=1)
        return print(f"Frozen {len(items)} conversations -> {out}")
    if cmd == "generate":
        if not manifest.exists() or json.loads(manifest.read_text())["sha256"] != P.digest(items, srv):
            raise SystemExit("Not frozen, or prompts/serving changed since freezing")
        if len(sys.argv) < 3 or sys.argv[2] not in R.labels():
            raise SystemExit(f"usage: generate <model> [concurrency]; models: {R.labels()}")
        return R.run_generate(items, out, sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 8)
    if cmd == "plan":  # offline: counts and digest only
        insp = inspection_plan()
        return print(json.dumps(dict(main=len(items), inspection=len(insp), main_digest=P.digest(items, srv),
                                     per_model={m: sum(i["model"] == m for i in items) for m in R.labels()},
                                     max_tokens=srv["target_max_tokens"]), indent=1))
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
