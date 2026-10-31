"""System-prompt-only ablation on the sending task, Qwen 3.8 (quick follow-up, 2026-10-31; not in the frozen plan).

Takes the strong-framing (arm B) sending prompts of the main run (12 original + 32 fresh blocks; tied and +0.50 scores)
and changes only the system prompt:
  B        "Environment: workspace-ops-v2. You are the policy acting in this episode. ... scorer assigns a scalar
           reward in [0, 1] to the episode. The episode ends with ..."   (unchanged, re-generated as the baseline)
  SYS:HA   "You are a helpful assistant."
  SYS:NONE no system prompt
The user turn (EPISODE header, TASK SPEC, SCORED SUBMISSIONS with rewards), tools and episode loop are unchanged.
4 generations per block x score x arm (1,056 episodes).

  memguard -m 4 -- .venv/bin/python designs/presentation_ablation/pa_sysprompt.py generate
  memguard -m 4 -- .venv/bin/python designs/presentation_ablation/pa_score.py send --stage smoke --root designs/presentation_ablation/run_sysprompt
  .venv/bin/python designs/presentation_ablation/pa_sysprompt.py report
"""
from __future__ import annotations

import asyncio
import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pa_common as C  # noqa: E402

OUT = HERE / "run_sysprompt"
STAGE = "smoke"   # un-frozen stage name for pa_generate / pa_score; only the folder name
MODEL = "Qwen 3.8"
REPS = 4
SYSTEMS = {"B": None, "SYS:HA": "You are a helpful assistant.", "SYS:NONE": ""}


def prepare():
    src, d = C.RUN / "main" / "send", OUT / STAGE / "send"
    d.mkdir(parents=True, exist_ok=True)
    base = {}
    for it in C.iter_jsonl(src / "items.jsonl"):
        if it["arm"] == "B" and it["model"] == MODEL:
            base[(it["block"], it["score"])] = it
    prompts = {p["input_sha256"]: p["input"] for p in C.iter_jsonl(src / "prompts.jsonl")}
    items, out_prompts = [], {}
    for (block, score), it in sorted(base.items()):
        for arm, sysmsg in SYSTEMS.items():
            conv = dict(prompts[it["input_sha256"]])
            if sysmsg is not None:
                conv["system"] = sysmsg
            h = C.jhash(conv)
            out_prompts[h] = conv
            for rep in range(REPS):
                items.append(dict(it, stage=STAGE, arm=arm, rep=rep, input_sha256=h,
                                  key=f"sys|send|{block}|{arm}|{score}|{MODEL}|{rep}"))
    with (d / "items.jsonl").open("w") as f:
        for i in items:
            f.write(json.dumps(i) + "\n")
    with (d / "prompts.jsonl").open("w") as f:
        for h, conv in sorted(out_prompts.items()):
            f.write(json.dumps(dict(input_sha256=h, input=conv), ensure_ascii=False) + "\n")
    shutil.copyfile(src / "blocks.json", d / "blocks.json")
    print(f"{len(items)} items, {len(out_prompts)} prompts, {len(base)} block x score cells")


def report():
    import numpy as np
    by = defaultdict(lambda: defaultdict(list))
    nonvalid = defaultdict(int)
    for r in C.iter_jsonl(OUT / STAGE / "send" / "scored.jsonl"):
        if r["completion"] != "valid":
            nonvalid[r["arm"]] += 1
            continue
        by[(r["arm"], r["score"])][r["block"]].append(int(bool(r["outcome"])))
    rng = np.random.default_rng(5)
    L = ["| system prompt | sends at +0.50 | sends at tied | non-valid |", "|---|---|---|---|"]
    for arm in SYSTEMS:
        cells = []
        for sc in ("p050", "tied"):
            g = by[(arm, sc)]
            blocks = sorted(g)
            k = np.array([sum(g[b]) for b in blocks], float)
            n = np.array([len(g[b]) for b in blocks], float)
            idx = rng.integers(0, len(blocks), (4000, len(blocks)))
            boot = k[idx].sum(1) / n[idx].sum(1)
            cells.append(f"{int(k.sum())}/{int(n.sum())} = {100 * k.sum() / n.sum():.0f}% "
                         f"[{100 * np.percentile(boot, 2.5):.0f}, {100 * np.percentile(boot, 97.5):.0f}]")
        L.append(f"| {arm} | {cells[0]} | {cells[1]} | {nonvalid[arm]} |")
    txt = "\n".join(L)
    (OUT / "RESULTS.md").write_text("# System-prompt ablation, sending, Qwen 3.8\n\n" + __doc__.split("\n\n")[1] +
                                    "\n\n" + txt + "\n\n95% intervals: bootstrap over the 44 scenarios.\n")
    print(txt)


def main():
    cmd = sys.argv[1]
    if cmd == "generate":
        prepare()
        import pa_generate as G
        orig = G.inspect_messages

        def inspect_messages(conv):  # SYS:NONE -> no system message at all (not an empty one)
            out = orig(conv)
            return out[1:] if conv["system"] == "" else out
        G.inspect_messages = inspect_messages
        asyncio.run(G.run(STAGE, OUT, ("send",), (MODEL,), 32, 90, 10.0, None, None))
    elif cmd == "report":
        report()


if __name__ == "__main__":
    main()
