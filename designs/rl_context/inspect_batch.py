"""Inspection batch (not analysed): 1 sample of every fire_drill main cell plus 3 diagnostics, per model.

Uses the project's own adapter (reasoning blocks stripped) and the serving settings of
experiment.grading.35v38.json, so outputs match what the full pilot would get.
Writes inspection/outputs.jsonl and inspection/outputs.md for reading by hand.

Run from the repo root:  .venv/bin/python designs/rl_context/inspect_batch.py
"""
import asyncio
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(ROOT / "src")]

from dotenv import load_dotenv  # noqa: E402
from inspect_ai.model import get_model  # noqa: E402

from materials import CONTEXTS, SCORES, TASKS, USERS, render, render_capability, render_comprehension  # noqa: E402
from model_diffing.core import converse  # noqa: E402
from model_diffing.petri_task import adapter, generation_config  # noqa: E402
from score import comprehension_mentions_title, measures  # noqa: E402

TASK = next(t for t in TASKS if t["id"] == "fire_drill")
OUT = HERE / "inspection"


def items():
    for c in CONTEXTS:
        for s in SCORES:
            for u in USERS:
                yield dict(set="main", context=c, scores=s, user=u, **render(TASK, c, s, u))
    yield dict(set="comprehension", context="rl_framing", scores="title_rewarded", user="-",
               **render_comprehension(TASK, "rl_framing", "title_rewarded"))
    yield dict(set="capability_plain", context="none", scores="none", user="wants_title", **render_capability(TASK, False))
    yield dict(set="capability_vs_scorer", context="ordinary", scores="title_penalised", user="wants_title",
               **render_capability(TASK, True))


async def main():
    load_dotenv(ROOT / ".env")
    settings = json.loads((ROOT / "experiment.grading.35v38.json").read_text())
    gens = {t["label"]: adapter(get_model(t["model"], **t.get("model_args", {})), config=generation_config(settings, t))
            for t in settings["targets"]}
    semaphore = asyncio.Semaphore(6)
    jobs = [(label, item) for label in gens for item in items()]

    async def run(label, item):
        messages, status, private = await converse(gens[label], item["turns"], system=item["system"],
                                                   timeout=settings.get("timeout", 300), semaphore=semaphore)
        reply = messages[-1]["content"] if messages and messages[-1]["role"] == "assistant" else ""
        return dict(model=label, **{k: v for k, v in item.items() if k not in ("turns", "system")},
                    status=status, private=private, reply=reply,
                    measures=measures(reply, TASK["facts"]) if item["set"] != "comprehension" else
                    {"mentions_title": comprehension_mentions_title(reply)})

    results = await asyncio.gather(*(run(label, item) for label, item in jobs))
    OUT.mkdir(exist_ok=True)
    with (OUT / "outputs.jsonl").open("w") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    lines = ["# Inspection batch outputs (fire_drill; not analysed)", ""]
    for r in results:
        m = r["measures"]
        tok = r["private"][-1] if r["private"] else {}
        lines += [f"## {r['model']} | {r['set']} | {r['context']} | {r['scores']} | {r['user']}",
                  f"status={r['status']} · out_tokens={tok.get('output_tokens')} reasoning={tok.get('reasoning_tokens')} "
                  f"· {', '.join(f'{k}={v}' for k, v in m.items())}" + (f" · ERROR {tok.get('error')}" if 'error' in tok else ""),
                  "", "```text", r["reply"].strip() or "(no reply)", "```", ""]
    (OUT / "outputs.md").write_text("\n".join(lines))
    print(f"{len(results)} conversations; statuses: "
          f"{ {s: sum(r['status'] == s for r in results) for s in {r['status'] for r in results}} }")


asyncio.run(main())
