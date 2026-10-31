"""Qwen 3.6 bars for the sending_example deck figure (API run; no GPU).

Replays the steering experiment's unsteered Qwen 3.5 items (44 blocks x 4 score arms x 4 reps = 704) on Qwen 3.6
through the presentation ablation's unchanged episode loop and serving entry (pa_q36.patch), then scores them with
the ablation's rule-based scorer (sent = acted).

  memguard -m 4 -- .venv/bin/python designs/deck/q36_send.py generate
  memguard -m 4 -- .venv/bin/python designs/deck/q36_send.py score    # -> run_q36_send/smoke/send/scored.jsonl
"""
from __future__ import annotations

import asyncio
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PA = HERE.parent / "presentation_ablation"
ST = HERE.parent / "steer_transfer" / "run" / "main" / "send"
OUT = HERE / "run_q36_send"
STAGE = "smoke"   # pa_generate's un-frozen stage name; only the folder name, no smoke items are used
sys.path.insert(0, str(PA))

import pa_common as C  # noqa: E402

GAP = {"conflict": 0.5, "reversed": -0.5, "tied": 0.0, "nohist": 0.0}


def prepare():
    d = OUT / STAGE / "send"
    d.mkdir(parents=True, exist_ok=True)
    items = []
    for it in C.iter_jsonl(ST / "items.jsonl"):
        if it["model"] == "Qwen 3.5" and it["cond"] == "none":
            items.append(dict(it, model="Qwen 3.6", key=it["key"].replace("|Qwen 3.5|", "|Qwen 3.6|"), part=1,
                              gap=GAP[it["score"]]))
    need = {i["input_sha256"] for i in items}
    with (d / "prompts.jsonl").open("w") as f:
        for p in C.iter_jsonl(ST / "prompts.jsonl"):
            if p["input_sha256"] in need:
                assert C.jhash(p["input"]) == p["input_sha256"]
                f.write(json.dumps(p, ensure_ascii=False) + "\n")
    with (d / "items.jsonl").open("w") as f:
        for i in items:
            f.write(json.dumps(i) + "\n")
    shutil.copyfile(ST / "blocks.json", d / "blocks.json")
    print(f"{len(items)} items, {len(need)} prompts")


def main():
    cmd = sys.argv[1]
    if cmd == "generate":
        prepare()
        import pa_q36
        G = pa_q36.patch(None)
        asyncio.run(G.run(STAGE, OUT, ("send",), ("Qwen 3.6",), 24, 120, 15.0, None, None))
    elif cmd == "score":
        import pa_score
        print(pa_score.score("send", STAGE, OUT))


if __name__ == "__main__":
    main()
