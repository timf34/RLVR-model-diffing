"""Blinded LLM judge for text labels (extends designs/action/agent.py judge_claim).

Experiments write their own rubric prompts. A judge must see only what a label needs: the user request, relevant
facts / tool semantics and the VISIBLE answer or transcript. Never model identity, reward history, framing labels or
reasoning (unless a specific label requires one of them, documented in that experiment's HYPOTHESES.md).

label(prompt, schema) -> {"labels": {name: value}, "justification": str, "usage": {...}} or None if unparseable.
`schema` maps each label name to its allowed values; the prompt must ask for JSON with exactly those keys plus
"justification".
"""
from __future__ import annotations

import asyncio
import json
import re

from . import limiter, serving

_JUDGE = None


def judge_model():
    global _JUDGE
    if _JUDGE is None:
        _JUDGE = serving.get_judge()
    return _JUDGE


async def label(prompt: str, schema: dict[str, tuple[str, ...]], judge=None, max_tokens: int = 800) -> dict | None:
    from inspect_ai.model import ChatMessageUser, GenerateConfig
    judge = judge or judge_model()
    usage = {}
    for attempt in range(4):
        try:
            async with limiter.slot("judge"):
                out = await judge.generate([ChatMessageUser(content=prompt)],
                                           config=GenerateConfig(temperature=0, max_tokens=max_tokens), cache=False)
            u = out.usage
            for k in ("input_tokens", "output_tokens"):
                usage[k] = usage.get(k, 0) + (getattr(u, k, 0) or 0)
            m = re.search(r"\{.*\}", out.completion, re.DOTALL)
            data = json.loads(m.group(0)) if m else {}
            if all(data.get(k) in v for k, v in schema.items()):
                return dict(labels={k: data[k] for k in schema}, justification=data.get("justification", ""),
                            usage=usage)
        except Exception:  # noqa: BLE001
            await asyncio.sleep(3 * (attempt + 1))
    return dict(labels=None, justification="unparseable", usage=usage)


class FakeJudge:
    """Offline stand-in: `fn(prompt) -> dict of labels`."""

    def __init__(self, fn):
        self.fn = fn

    async def generate(self, messages, config=None, cache=False):
        data = dict(self.fn(messages[0].text), justification="fake")
        return type("Out", (), {"completion": json.dumps(data), "usage": None})
