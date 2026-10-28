"""Unauthorised-action family: inspection, freezing, generation and reports.

Run from designs/action/ (heavy jobs under memguard; see the repo notes):
  ../../.venv/bin/python test_env.py                                  # offline: scripted agents, no API calls
  ../../.venv/bin/python run.py inspect all 24                         # inspection-only scenarios -> runs/inspection
  ../../.venv/bin/python run.py transcripts inspection                 # readable transcripts for hand inspection
  ../../.venv/bin/python run.py freeze                                 # main batch: prompts, tools, serving, code hashed
  ../../.venv/bin/python run.py generate "Qwen 3.6" 24                 # one process per model, in parallel
  ../../.venv/bin/python run.py analyse                                # analysis.py -> runs/main/RESULTS.md
Each model writes its own runs/<name>/gen/<model>/episodes.jsonl. Errors are retried on resume.
"""
from __future__ import annotations

import asyncio
import hashlib
import itertools
import json
import random
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(ROOT / "src")]

import materials as M  # noqa: E402
from env import tool_specs  # noqa: E402

RUNS = HERE / "runs"
MAX_TOKENS = 32768
SERVING_CONFIG = ROOT / "experiment.grading.3way.json"
CODE = ["materials.py", "env.py", "score.py", "agent.py", "run.py", "analysis.py", "test_env.py"]
SERVING_NOTES = {
    "Qwen 3.5": "novita/bf16; default thinking (no reasoning_effort parameter on any 3.5 host)",
    "Qwen 3.6": "alibaba (first-party; precision not stated; no bf16 host on OpenRouter); default thinking",
    "Qwen 3.8": "deepinfra/bf16; reasoning_effort=medium",
}
PRICES = {"Qwen 3.5": (0.26, 2.6), "Qwen 3.6": (0.45, 2.7), "Qwen 3.8": (0.039, 1.25)}  # $/M in, out (listed)

# Inspection cells (discovery only; inspection-only scenarios).
# Round 1 (runs/inspection): history `plain` only; its cell labels have three parts.
INSPECT_CELLS = [("bundle", "explicit", "rewarded"), ("bundle", "explicit", "penalised"),
                 ("bundle", "explicit", "none"), ("bundle", "hedged", "rewarded"), ("bundle", "silent", "rewarded"),
                 ("bundle", "silent", "penalised"), ("ordinary", "explicit", "rewarded"),
                 ("ordinary", "silent", "rewarded")]
# Round 2 (runs/inspection2): previous episodes' requests shown; a softer reservation.
INSPECT2_CELLS = [("bundle", "explicit", "rewarded", "requests"), ("bundle", "hedged", "rewarded", "requests"),
                  ("bundle", "hedged", "penalised", "requests"), ("bundle", "soft", "rewarded", "plain"),
                  ("bundle", "soft", "rewarded", "requests"), ("bundle", "soft", "penalised", "requests"),
                  ("ordinary", "hedged", "rewarded", "requests"), ("ordinary", "soft", "rewarded", "requests")]
# Main cells and samples: fixed in HYPOTHESES.md before freezing.
MAIN_CELLS = [("bundle", "explicit", "rewarded", "requests"), ("bundle", "explicit", "penalised", "requests"),
              ("bundle", "hedged", "rewarded", "requests"), ("bundle", "hedged", "penalised", "requests"),
              ("bundle", "explicit", "rewarded", "plain"), ("bundle", "hedged", "rewarded", "plain"),
              ("bundle", "explicit", "none", "plain"),
              ("bundle", "silent", "rewarded", "requests"), ("bundle", "silent", "penalised", "requests"),
              ("ordinary", "explicit", "rewarded", "requests"), ("ordinary", "explicit", "penalised", "requests"),
              ("ordinary", "hedged", "rewarded", "requests"), ("ordinary", "explicit", "none", "plain")]
SAMPLES = 4


def serving() -> dict:
    s = json.loads(SERVING_CONFIG.read_text())
    targets = [{k: v for k, v in t.items() if k != "serving_note"} for t in s["targets"]]
    return dict(targets=targets, target_generate=s["target_generate"], temperature=0.7,
                target_max_tokens=MAX_TOKENS, timeout=1200, max_steps=8)


def labels() -> list[str]:
    return [t["label"] for t in serving()["targets"]]


def plan(tasks, cells, samples, tag) -> list[dict]:
    out = []
    for task, cell, m, r in itertools.product(tasks, cells, labels(), range(samples)):
        f, u, s, h = (*cell, "plain") if len(cell) == 3 else cell
        name = f"{f}/{u}/{s}" if len(cell) == 3 else f"{f}/{u}/{s}/{h}"
        out.append(dict(key=f"{tag}|{task['id']}|{name.replace('/', '|')}|{m}|{r}", set=tag, scenario=task["id"],
                        family=task["family"], framing=f, user=u, scores=s, hist=h, cell=name, model=m, rep=r))
    return out


def digest(items) -> str:
    body = []
    for i in items:
        task = M.ALL_TASKS[i["scenario"]]
        p = M.render(task, i["framing"], i["user"], i["scores"], i["hist"])
        body.append([i["key"], p["system"], p["turns"], tool_specs(task), task["context"], task["facts"], task["key"]])
    return hashlib.sha256(json.dumps([body, serving()], sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def code_hashes() -> dict:
    return {f: hashlib.sha256((HERE / f).read_bytes()).hexdigest() for f in CODE if (HERE / f).exists()}


def load(run: str, items=None) -> list[dict]:
    """Latest non-failed record per key across model files (failed ones only if nothing else exists)."""
    rows = {}
    for path in sorted((RUNS / run / "gen").glob("*/episodes.jsonl")):
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            e = json.loads(line)
            if e["key"] in rows and e["status"] == "failed" and rows[e["key"]]["status"] != "failed":
                continue
            rows[e["key"]] = e
    if items is not None:
        keys = {i["key"] for i in items}
        rows = {k: v for k, v in rows.items() if k in keys}
    return list(rows.values())


async def generate(items, run: str, models: list[str], concurrency: int):
    from dotenv import load_dotenv
    from inspect_ai.model import get_model

    from agent import get_judge, model_policy, run_episode
    from model_diffing.petri_task import generation_config
    load_dotenv(ROOT / ".env")
    srv = serving()
    judge = get_judge()
    lock, n = asyncio.Lock(), [0]
    jobs = []
    for label in models:
        target = next(t for t in srv["targets"] if t["label"] == label)
        model = get_model(target["model"], **target.get("model_args", {}))
        policy = model_policy(model, generation_config(srv, target), asyncio.Semaphore(concurrency))
        gen = RUNS / run / "gen" / label.replace(" ", "_")
        gen.mkdir(parents=True, exist_ok=True)
        path = gen / "episodes.jsonl"
        done = set()
        if path.exists():
            done = {json.loads(l)["key"] for l in path.read_text().splitlines()
                    if l.strip() and json.loads(l)["status"] != "failed"}
        jobs += [(i, policy, path) for i in items if i["model"] == label and i["key"] not in done]
    random.Random(0).shuffle(jobs)
    print(f"{run} {models}: {len(jobs)} episodes to run", flush=True)

    async def one(i, policy, path):
        t0 = datetime.now(timezone.utc)
        task = M.ALL_TASKS[i["scenario"]]
        try:
            rec = await run_episode(policy, task, i["framing"], i["user"], i["scores"], judge=judge, hist=i["hist"])
        except Exception as e:  # noqa: BLE001
            rec = dict(status="failed", error=f"{type(e).__name__}: {str(e)[:300]}", measures={}, usage={})
        rec = i | rec | dict(started=t0.isoformat(timespec="seconds"),
                             finished=datetime.now(timezone.utc).isoformat(timespec="seconds"))
        async with lock:
            with path.open("a") as f:
                f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
            n[0] += 1
            m = rec.get("measures", {})
            calls = " ".join(e["name"] for e in rec.get("log", []))
            print(f"  [{n[0]}/{len(jobs)}] {i['model']} {i['scenario']} {i['cell']}: {rec['status']} "
                  f"acted={m.get('acted')} claim={m.get('claim')} | {calls}", flush=True)

    await asyncio.gather(*(one(*j) for j in jobs))


async def rejudge(run: str):
    """Re-run the current judge and scoring on a saved run (inspection runs only; never the frozen main batch)."""
    assert run != "main", "the main batch is judged at generation time"
    from dotenv import load_dotenv

    import score as S
    from agent import get_judge, judge_claim
    load_dotenv(ROOT / ".env")
    judge, sem = get_judge(), asyncio.Semaphore(16)
    for path in sorted((RUNS / run / "gen").glob("*/episodes.jsonl")):
        eps = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]

        async def one(e):
            if e["status"] != "valid":
                return
            task = M.ALL_TASKS[e["scenario"]]
            async with sem:
                j = await judge_claim(judge, task, e["final_reply"])
            e["judge"] = j
            e["measures"] = S.measures(task, e["log"], e["final_reply"], e["status"], claim=(j or {}).get("claim"),
                                       override=(j or {}).get("override"))
        await asyncio.gather(*(one(e) for e in eps))
        path.write_text("".join(json.dumps(e, ensure_ascii=False, default=str) + "\n" for e in eps))
        print(f"rejudged {path}")


def cost(eps) -> float:
    tot = 0.0
    for e in eps:
        pin, pout = PRICES.get(e["model"], (0, 0))
        u = e.get("usage") or {}
        tot += (u.get("input_tokens") or 0) * pin / 1e6 + (u.get("output_tokens") or 0) * pout / 1e6
    return tot


def transcripts(run: str, out: Path | None = None, filt=None):
    eps = sorted(load(run), key=lambda e: (e["scenario"], e["cell"], e["model"], e["rep"]))
    if filt:
        eps = [e for e in eps if filt(e)]
    L = [f"# Transcripts: {run}", "", f"{len(eps)} episodes; approx. target cost ${cost(eps):.2f} (listed prices).", ""]
    for e in eps:
        m = e.get("measures", {})
        L += [f"## {e['key']}", "",
              f"**status** {e['status']} · **acted** {m.get('acted')} · attempted {m.get('attempted')} · saved "
              f"{m.get('saved')} · task_done {m.get('task_done')} (facts {m.get('facts_hit')}, key {m.get('key_ok')}) "
              f"· **claim** {m.get('claim')} (rx {m.get('claim_rx')}) · **disclosure** {m.get('disclosure')} "
              f"· override acknowledged {m.get('override')} "
              f"· tokens {e.get('usage', {}).get('output_tokens')}", ""]
        for t in e.get("trace", []):
            r = (t.get("reasoning") or "").strip()
            if r:
                L += [f"<details><summary>step {t['step']} reasoning ({len(r)} chars)</summary>", "", "```text",
                      r[:6000] + (" …[cut]" if len(r) > 6000 else ""), "```", "</details>", ""]
            if (t.get("text") or "").strip():
                L += [f"step {t['step']} text:", "```text", t["text"].strip(), "```"]
            for c, res in zip(t.get("calls", []), t.get("results", [])):
                L += [f"- `{c['name']}({json.dumps(c['args'], ensure_ascii=False)[:600]})` → {res[:200]}"]
            if t.get("error"):
                L += [f"- ERROR {t['error']}"]
        L += [""]
    path = out or RUNS / run / "TRANSCRIPTS.md"
    path.write_text("\n".join(L) + "\n")
    print(f"wrote {path} ({len(eps)} episodes, ~${cost(eps):.2f})")


def summary_table(run: str, items=None):
    import collections
    eps = load(run, items)
    agg = collections.defaultdict(lambda: collections.Counter())
    for e in eps:
        m = e.get("measures", {})
        c = agg[(e["cell"], e["model"])]
        c["n"] += 1
        c["valid"] += bool(m.get("valid"))
        if m.get("valid"):
            c["acted"] += m["acted"]
            c["task_done"] += m["task_done"]
            c["false_denial"] += m.get("disclosure") == "false_denial"
            c["silent_action"] += m.get("disclosure") == "silent_action"
    print(f"{'cell':34} {'model':9} acted/valid  done  false_denial silent_action  (n)")
    for (cell, model), c in sorted(agg.items()):
        print(f"{cell:34} {model:9} {c['acted']:>3}/{c['valid']:<3}     {c['task_done']:>3}   {c['false_denial']:>3}"
              f"          {c['silent_action']:>3}           ({c['n']})")
    print(f"approx. cost ${cost(eps):.2f}")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "inspect":
        models = labels() if sys.argv[2] == "all" else [sys.argv[2]]
        items = plan(M.INSPECTION_TASKS, INSPECT_CELLS, 1, "inspect")
        conc = int(sys.argv[3]) if len(sys.argv) > 3 else 8
        return asyncio.run(generate([i for i in items if i["model"] in models], "inspection", models, conc))
    if cmd == "inspect2":
        models = labels() if sys.argv[2] == "all" else [sys.argv[2]]
        items = plan(M.INSPECTION_TASKS, INSPECT2_CELLS, 2, "inspect2")
        conc = int(sys.argv[3]) if len(sys.argv) > 3 else 8
        return asyncio.run(generate([i for i in items if i["model"] in models], "inspection2", models, conc))
    if cmd == "rejudge":
        return asyncio.run(rejudge(sys.argv[2]))
    if cmd == "transcripts":
        return transcripts(sys.argv[2])
    if cmd == "table":
        return summary_table(sys.argv[2])
    items, srv = plan(M.TASKS, MAIN_CELLS, SAMPLES, "main"), serving()
    out = RUNS / "main"
    manifest = out / "manifest.json"
    if cmd == "freeze":
        if manifest.exists():
            raise SystemExit("Already frozen; start a new, separately named run to change anything")
        out.mkdir(parents=True, exist_ok=True)
        hyp = (HERE / "HYPOTHESES.md").read_text()
        snap = out / "code_snapshot"
        snap.mkdir(exist_ok=True)
        for f in [f for f in CODE + ["HYPOTHESES.md"] if (HERE / f).exists()]:
            shutil.copy(HERE / f, snap / f)
        manifest.write_text(json.dumps(dict(
            sha256=digest(items), label="PRE-REGISTERED main batch (fresh scenarios; inspection scenarios excluded)",
            at=datetime.now(timezone.utc).isoformat(timespec="seconds"), samples=SAMPLES, cells=MAIN_CELLS,
            scenarios=[t["id"] for t in M.TASKS], total=len(items),
            hypotheses_sha256=hashlib.sha256(hyp.encode()).hexdigest(), code_sha256=code_hashes(),
            serving=srv, serving_notes=SERVING_NOTES), indent=2) + "\n")
        return print(f"Frozen {len(items)} episodes -> {manifest}")
    if not manifest.exists() or json.loads(manifest.read_text())["sha256"] != digest(items):
        raise SystemExit("Not frozen, or prompts/tools/serving changed since freezing")
    if cmd == "generate":
        conc = int(sys.argv[3]) if len(sys.argv) > 3 else 8
        return asyncio.run(generate(items, "main", [sys.argv[2]], conc))
    if cmd == "analyse":
        import analysis
        return analysis.analyse(load("main", items), out, json.loads(manifest.read_text()), code_hashes())
    if cmd == "status":
        return summary_table("main", items)
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
