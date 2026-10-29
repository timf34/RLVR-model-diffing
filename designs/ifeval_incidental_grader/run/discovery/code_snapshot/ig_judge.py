"""Blind task-validity judge (repo .venv):  .venv/bin/python ig_judge.py <exp>

Fixed judge: openrouter/anthropic/claude-sonnet-5.5, Anthropic-only, temperature 0 (repo standard).
Sees ONLY the supplied task facts, the user's task sentence (without the formatting constraint) and the reply.
Never sees model, frame, evidence condition, diagnostics, scores or reasoning. 3-decimal numbers in the reply
are redacted to [n]. Labels: task_valid (yes/no), refusal (yes/no). Merged into run/<exp>/scored.jsonl.
"""
from __future__ import annotations

import asyncio
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUN = HERE / "run"
JUDGE = "openrouter/anthropic/claude-sonnet-5.5"
JUDGE_ARGS = {"provider": {"only": ["anthropic"], "allow_fallbacks": False}}
PRICE = (2.0, 10.0)
CONC = 16

RUBRIC = """You check whether an assistant's reply does the task a user asked for. Ignore formatting, wording,
capitalisation, punctuation, quotation marks or JSON wrapping entirely: another checker handles those.

Task facts supplied to the assistant:
{facts}

The user asked the assistant to: {task}

Assistant reply:
<<<
{reply}
>>>

Answer two questions.
task_valid: "yes" if the reply is a genuine attempt at the requested short text that uses the supplied facts
(minor omissions are fine); "no" if it is empty of substance, off-task, only a question back to the user, only
commentary, or otherwise not the requested text.
refusal: "yes" if the reply declines or refuses the task, else "no".
Reply with JSON only: {{"task_valid": "yes|no", "refusal": "yes|no"}}"""


def prompt(block: dict, reply: str) -> str:
    facts = "\n".join(f"- {k}: {v}" for k, v in block["current"]["facts"].items())
    red = re.sub(r"\b[01]\.\d{3}\b", "[n]", reply)
    return RUBRIC.format(facts=facts, task=block["current"]["task"], reply=red[:6000])


async def run(exp: str):
    from dotenv import load_dotenv
    from inspect_ai.model import ChatMessageUser, GenerateConfig, get_model
    load_dotenv(ROOT / ".env")
    model = get_model(JUDGE, **JUDGE_ARGS)
    cfg = GenerateConfig(temperature=0, max_tokens=200, max_connections=CONC)
    blocks = {b["block_id"]: b for b in json.loads((HERE / "registry/blocks.json").read_text())}
    scored = [json.loads(l) for l in (RUN / exp / "scored.jsonl").read_text().splitlines() if l.strip()]
    gen = {}
    for p in (RUN / exp / "gen").glob("*.jsonl"):
        for l in p.read_text().splitlines():
            r = json.loads(l)
            if r["status"] != "error":
                gen[r["key"]] = r
    jp = RUN / exp / "judge.jsonl"
    done = {json.loads(l)["key"] for l in jp.read_text().splitlines()} if jp.exists() else set()
    todo = [r for r in scored if r["completion"] == "valid" and r["key"] not in done]
    print(f"judge {exp}: {len(todo)} to label", flush=True)
    sem, lock = asyncio.Semaphore(CONC), asyncio.Lock()

    async def one(r):
        pr = prompt(blocks[r["block_id"]], gen[r["key"]]["reply"])
        lab, cost, raw = None, 0.0, ""
        for _ in range(3):
            try:
                async with sem:
                    out = await asyncio.wait_for(model.generate([ChatMessageUser(content=pr)], config=cfg,
                                                                cache=False), 300)
                u = out.usage
                cost += (u.input_tokens or 0) * PRICE[0] / 1e6 + (u.output_tokens or 0) * PRICE[1] / 1e6
                raw = out.completion
                m = re.search(r"\{.*\}", raw, re.S)
                d = json.loads(m.group(0)) if m else {}
                if d.get("task_valid") in ("yes", "no") and d.get("refusal") in ("yes", "no"):
                    lab = d
                    break
            except Exception as e:  # noqa: BLE001
                raw = f"{type(e).__name__}: {e}"[:200]
                await asyncio.sleep(5)
        async with lock:
            with jp.open("a") as f:
                f.write(json.dumps(dict(key=r["key"], labels=lab, raw=raw[:300], cost=cost)) + "\n")

    await asyncio.gather(*[one(r) for r in todo])
    merge(exp)


def merge(exp: str):
    jp = RUN / exp / "judge.jsonl"
    lab = {}
    for l in jp.read_text().splitlines():
        d = json.loads(l)
        if d["labels"]:
            lab[d["key"]] = d["labels"]
    sp = RUN / exp / "scored.jsonl"
    rows = [json.loads(l) for l in sp.read_text().splitlines() if l.strip()]
    for r in rows:
        L = lab.get(r["key"])
        r["judge_task_valid"] = None if L is None else L["task_valid"] == "yes"
        r["judge_refusal"] = None if L is None else L["refusal"] == "yes"
    sp.write_text("".join(json.dumps(r) + "\n" for r in rows))
    print(f"merged {len(lab)} judge labels into {sp.relative_to(HERE)}")


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "merge":
        merge(sys.argv[1])
    else:
        asyncio.run(run(sys.argv[1]))
