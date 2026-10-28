"""EM-DASH follow-up (see emdash_materials.py, HYPOTHESES_emdash.md). Built while the confirmation batch ran;
freeze and generate only after the confirmation results are in and HYPOTHESES_emdash.md is final.

Same serving, design and analysis as the confirmation batch (run_confirm.py, confirm_analysis.py); the analysis
module is reused unchanged, with its feature list and scorer swapped at run time.

Run from the repo root:
  .venv/bin/python designs/rl_context/run_emdash.py inspect
  .venv/bin/python designs/rl_context/run_emdash.py freeze
  .venv/bin/python designs/rl_context/run_emdash.py generate "Qwen 3.6" 24     # one process per model, in parallel
  .venv/bin/python designs/rl_context/run_emdash.py analyse
"""
import asyncio
import hashlib
import itertools
import json
import shutil
import sys
import types
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import run_confirm as R  # noqa: E402  (serving, generation, record loading)
import run_pilot as P  # noqa: E402
import emdash_materials as E  # noqa: E402

OUT = HERE / "emdash"
SAMPLES = 5
CODE = ["emdash_materials.py", "emdash_score.py", "score.py", "run_emdash.py", "run_confirm.py",
        "confirm_analysis.py", "confirm_materials.py"]


def item(set_, task, context, request, scores, model, rep, prompt) -> dict:
    cell = f"{context}/{request}"
    return dict(key=f"{set_}|{task['id']}|{E.FEATURE}|{cell}|{scores}|{model}|{rep}", set=set_, scenario=task["id"],
                domain=task["domain"], feature=E.FEATURE, context=cell, scores=scores, user=E.FEATURE, model=model,
                rep=rep, facts=task["facts"], signoff="", **prompt)


def plan(tasks=E.TASKS, samples=SAMPLES, tag="") -> list[dict]:
    out = []
    for task, scores in itertools.product(tasks, E.SCORES):
        for m, r in itertools.product(R.labels(), range(samples)):
            for c, q in itertools.product(E.CONTEXTS, E.REQUESTS):
                out.append(item(tag or "main", task, c, q, scores, m, r, E.render(task, E.FEATURE, c, q, scores)))
            out.append(item(tag or "anchor", task, "anchor", "bundle", scores, m, r,
                            E.render_anchor(task, E.FEATURE, scores)))
    return out


def analysis_module():
    """confirm_analysis, unchanged, pointed at the em-dash feature and scorer."""
    import confirm_analysis as A
    import emdash_score
    A.M = types.SimpleNamespace(FEATURES=E.FEATURES, CONTEXTS=E.CONTEXTS, REQUESTS=E.REQUESTS, SCORES=E.SCORES,
                                TASKS=E.TASKS, INSPECTION_TASK=E.INSPECTION_TASK, DOMAINS=E.DOMAINS)
    A.measures, A.completion = emdash_score.measures, emdash_score.completion
    A.ALPHA = 0.05  # one feature (HYPOTHESES_emdash.md)

    def reading(res, complete):  # single-feature reading rules from HYPOTHESES_emdash.md
        r = {h: res[E.FEATURE]["H"][h]["result"] for h in ("H1", "H2", "H5")} | {"S": res[E.FEATURE]["S"]}
        if r["H1"] == "PASS" and r["H2"] == "PASS":
            v = "H1 and H2 pass: the effect extends to an in-sentence feature (em dashes)."
        elif r["H1"] == "FAIL" and r["H5"] == "PASS":
            v = "H1 fails but H5 passes: the effect appears in the original bundle format only."
        elif r["H1"] == "FAIL" and r["H5"] == "FAIL":
            v = "H1 and H5 both fail: no evidence that the effect extends to em dashes."
        else:
            v = "No pre-registered reading applies (" + ", ".join(f"{h} {r[h]}" for h in ("H1", "H2", "H5")) + ")."
        if not complete or "n/a" in r.values():
            v = "PROVISIONAL (data incomplete). " + v
        notes = [] if r["S"] == "PASS" else [f"Check S is {r['S']}: read H1/H2/H5 with caution."]
        return dict(verdict=v, notes=notes, results={E.FEATURE: r})
    A.reading = reading
    return A


def inspect():
    out = OUT / "inspection"
    items = plan([E.INSPECTION_TASK], 1, "inspect")
    lines = ["# Em-dash prompts preview (inspection task only)", ""]
    for i in items:
        if i["model"] == R.labels()[0] and i["scores"] == "rewarded":
            lines += [f"## {i['context']}", "", "SYSTEM:", "```text", i["system"], "```",
                      "USER:", "```text", i["turns"][0], "```", ""]
    gen = out / "gen" / "all"
    gen.mkdir(parents=True, exist_ok=True)
    (out / "prompts_preview.md").write_text("\n".join(lines))
    P.OUT, P.TIMEOUT, P.CONCURRENCY = gen, R.TIMEOUT, 24
    asyncio.run(P.generate(items, R.serving()))
    print(f"inspection: {len(R.load_records(out, items))} records -> {out}")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "inspect":
        return inspect()
    items, srv = plan(), R.serving()
    manifest = OUT / "manifest.json"
    hyp_path = HERE / "HYPOTHESES_emdash.md"
    if cmd == "freeze":
        hyp = hyp_path.read_text()
        if "DRAFT" in hyp.splitlines()[0]:
            raise SystemExit("HYPOTHESES_emdash.md is still a draft; finalise it after the confirmation results")
        OUT.mkdir(exist_ok=True)
        if manifest.exists():
            raise SystemExit("Already frozen; start a new, separately named run to change anything")
        snap = OUT / "code_snapshot"
        snap.mkdir(exist_ok=True)
        for f in CODE + [hyp_path.name]:
            shutil.copy(HERE / f, snap / f)
        manifest.write_text(json.dumps(dict(
            sha256=P.digest(items, srv), label="EM-DASH follow-up (new feature; analysed separately)",
            at=datetime.now(timezone.utc).isoformat(timespec="seconds"), samples=SAMPLES,
            counts={s: sum(i["set"] == s for i in items) for s in ("main", "anchor")}, total=len(items),
            hypotheses_sha256=hashlib.sha256(hyp.encode()).hexdigest(),
            code_sha256={f: hashlib.sha256((HERE / f).read_bytes()).hexdigest() for f in CODE},
            serving=srv, serving_notes=R.SERVING_NOTES), indent=2) + "\n")
        json.dump([{k: i[k] for k in ("key", "system", "turns", "facts")} for i in items],
                  open(OUT / "prompts.json", "w"), indent=1)
        return print(f"Frozen {len(items)} conversations")
    if not manifest.exists() or json.loads(manifest.read_text())["sha256"] != P.digest(items, srv):
        raise SystemExit("Not frozen, or prompts/serving changed since freezing")
    if cmd == "generate":
        return R.run_generate(items, OUT, sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 8)
    if cmd == "analyse":
        m = json.loads(manifest.read_text())
        hashes = {f: hashlib.sha256((HERE / f).read_bytes()).hexdigest() for f in CODE}
        return analysis_module().analyse(R.load_records(OUT, items), OUT, m, hashes)
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
