"""CONFIRMATION batch (see CONFIRMATION_PLAN.md, HYPOTHESES_confirm.md). Kept separate from all discovery runs.

Run from the repo root:
  .venv/bin/python designs/rl_context/run_confirm.py inspect                 # separate inspection task only
  .venv/bin/python designs/rl_context/run_confirm.py freeze                  # hash prompts, serving, hypotheses, code
  .venv/bin/python designs/rl_context/run_confirm.py generate "Qwen 3.6" 20  # one process per model, in parallel
  .venv/bin/python designs/rl_context/run_confirm.py analyse                 # confirm_analysis.py
Each model writes its own confirm/gen/<model>.jsonl, so the three processes never share a file.
"""
import asyncio
import hashlib
import itertools
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import run_pilot as P  # noqa: E402  (shares generation and the pinned src snapshot)
import confirm_materials as M  # noqa: E402

OUT = HERE / "confirm"
SAMPLES = 5
MAX_TOKENS = 32768  # Qwen 3.6 reasoned up to 15.8k tokens in the serving check; same cap for every model
TIMEOUT = 1200
SERVING_CONFIG = ROOT / "experiment.grading.3way.json"
CODE = ["confirm_materials.py", "confirm_score.py", "score.py", "run_confirm.py", "confirm_analysis.py"]
SERVING_NOTES = {
    "Qwen 3.5": "novita/bf16; default thinking (no reasoning_effort parameter on any 3.5 host)",
    "Qwen 3.6": "alibaba (first-party; precision not stated; no bf16 host exists on OpenRouter); default thinking "
                "(no reasoning_effort parameter on any 3.6 host). Long reasoning: 8k-16k tokens in the serving check.",
    "Qwen 3.8": "deepinfra/bf16; reasoning_effort=medium",
}


def serving() -> dict:
    s = json.loads(SERVING_CONFIG.read_text())
    targets = [{k: v for k, v in t.items() if k != "serving_note"} for t in s["targets"]]
    return dict(targets=targets, target_generate=s["target_generate"], temperature=0.7,
                target_max_tokens=MAX_TOKENS, timeout=TIMEOUT)


def labels() -> list[str]:
    return [t["label"] for t in serving()["targets"]]


def item(set_, task, feature, context, request, scores, model, rep, prompt) -> dict:
    cell = f"{context}/{request}"
    return dict(key=f"{set_}|{task['id']}|{feature}|{cell}|{scores}|{model}|{rep}", set=set_, scenario=task["id"],
                domain=task["domain"], feature=feature, context=cell, scores=scores, user=feature, model=model,
                rep=rep, facts=task["facts"], signoff=M.DOMAINS[task["domain"]]["signoff"], **prompt)


def plan(tasks=M.TASKS, samples=SAMPLES, tag="") -> list[dict]:
    main, anchor = tag or "main", tag or "anchor"
    out = []
    for task, feature, scores in itertools.product(tasks, M.FEATURES, M.SCORES):
        for m, r in itertools.product(labels(), range(samples)):
            for c, q in itertools.product(M.CONTEXTS, M.REQUESTS):
                out.append(item(main, task, feature, c, q, scores, m, r, M.render(task, feature, c, q, scores)))
            out.append(item(anchor, task, feature, "anchor", "bundle", scores, m, r,
                            M.render_anchor(task, feature, scores)))
    return out


def run_generate(items, out_dir: Path, model: str, concurrency: int):
    """Generate one model's items into out_dir/gen/<model>.jsonl (resumable; errors are retried)."""
    gen = out_dir / "gen" / model.replace(" ", "_")
    gen.mkdir(parents=True, exist_ok=True)
    P.OUT, P.TIMEOUT, P.CONCURRENCY = gen, TIMEOUT, concurrency  # P.generate writes P.OUT/generations.jsonl
    asyncio.run(P.generate([i for i in items if i["model"] == model], serving()))


def load_records(out_dir: Path, items) -> list[dict]:
    """Latest record per key across all model files, joined with its plan item (prompt fields dropped)."""
    by_key, rows = {i["key"]: i for i in items}, {}
    for path in sorted((out_dir / "gen").glob("*/generations.jsonl")):
        for line in path.read_text().splitlines():
            g = json.loads(line)
            if g["key"] in by_key:
                meta = {k: v for k, v in by_key[g["key"]].items() if k not in ("system", "turns")}
                rows[g["key"]] = meta | {k: g[k] for k in ("status", "private", "reply", "at")}
    return list(rows.values())


def code_hashes() -> dict:
    return {f: hashlib.sha256((HERE / f).read_bytes()).hexdigest() for f in CODE if (HERE / f).exists()}


def inspect():
    out = OUT / "inspection"
    items = plan([M.INSPECTION_TASK], 1, "inspect")
    lines = ["# Confirmation prompts preview (inspection task only)", ""]
    for i in items:
        if i["model"] == labels()[0] and i["scores"] == "rewarded":
            lines += [f"## {i['feature']} | {i['context']}", "", "SYSTEM:", "```text", i["system"], "```",
                      "USER:", "```text", i["turns"][0], "```", ""]
    out.mkdir(parents=True, exist_ok=True)
    (out / "prompts_preview.md").write_text("\n".join(lines))
    gen = out / "gen" / "all"  # one process, all models interleaved
    gen.mkdir(parents=True, exist_ok=True)
    P.OUT, P.TIMEOUT, P.CONCURRENCY = gen, TIMEOUT, 24
    asyncio.run(P.generate(items, serving()))
    print(f"inspection: {len(load_records(out, items))} records -> {out}")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "inspect":
        return inspect()
    items, srv = plan(), serving()
    manifest = OUT / "manifest.json"
    if cmd == "freeze":
        OUT.mkdir(exist_ok=True)
        if manifest.exists():
            raise SystemExit("Already frozen; start a new, separately named run to change anything")
        hyp = (HERE / "HYPOTHESES_confirm.md").read_text()
        snap = OUT / "code_snapshot"
        snap.mkdir(exist_ok=True)
        for f in [f for f in CODE + ["HYPOTHESES_confirm.md"] if (HERE / f).exists()]:
            shutil.copy(HERE / f, snap / f)
        manifest.write_text(json.dumps(dict(
            sha256=P.digest(items, srv), label="CONFIRMATION (fresh material; analysed separately from discovery)",
            at=datetime.now(timezone.utc).isoformat(timespec="seconds"), samples=SAMPLES,
            counts={s: sum(i["set"] == s for i in items) for s in ("main", "anchor")}, total=len(items),
            hypotheses_sha256=hashlib.sha256(hyp.encode()).hexdigest(), code_sha256=code_hashes(),
            serving=srv, serving_notes=SERVING_NOTES), indent=2) + "\n")
        json.dump([{k: i[k] for k in ("key", "system", "turns", "facts")} for i in items],
                  open(OUT / "prompts.json", "w"), indent=1)
        return print(f"Frozen {len(items)} conversations")
    if not manifest.exists() or json.loads(manifest.read_text())["sha256"] != P.digest(items, srv):
        raise SystemExit("Not frozen, or prompts/serving changed since freezing")
    if cmd == "generate":
        return run_generate(items, OUT, sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 8)
    if cmd == "analyse":
        import confirm_analysis
        return confirm_analysis.analyse(load_records(OUT, items), OUT, json.loads(manifest.read_text()), code_hashes())
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
