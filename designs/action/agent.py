"""Multi-turn tool episode loop. Real models and scripted agents go through the same loop and the same scoring.

The episode ends at the first assistant message with no tool call (that message is the reply to the user), or at
MAX_STEPS model turns (status step_limit). Tool calls are dispatched to env.ActionEnv; nothing has external effects.
Reasoning is recorded for researchers only.
"""
from __future__ import annotations

import asyncio
import json
import re
from typing import Awaitable, Callable

import materials as M
import score as S
from env import ActionEnv, tool_specs

MAX_STEPS = 8
TIMEOUT = 1200
JUDGE_MODEL = "openrouter/anthropic/claude-sonnet-5.5"
JUDGE_ARGS = {"provider": {"only": ["anthropic"], "allow_fallbacks": False}}

Policy = Callable[[list, list], Awaitable[dict]]  # (messages, tools) -> {message, stop, usage}


def inspect_tools(task: dict):
    from inspect_ai.tool import ToolInfo, ToolParam, ToolParams
    out = []
    for t in tool_specs(task):
        p = t["parameters"]
        out.append(ToolInfo(name=t["name"], description=t["description"], parameters=ToolParams(
            properties={k: ToolParam(**v) for k, v in p["properties"].items()}, required=p["required"])))
    return out


def split_content(message) -> tuple[str, str]:
    content = message.content
    if isinstance(content, str):
        return content, ""
    text = "\n".join(c.text for c in content if getattr(c, "type", "") == "text")
    reasoning = "\n".join(getattr(c, "reasoning", "") or "" for c in content if getattr(c, "type", "") == "reasoning")
    return text, reasoning


# ---------------------------------------------------------------- policies

def model_policy(model, config, semaphore) -> Policy:
    async def policy(messages, tools):
        async with semaphore:
            out = await asyncio.wait_for(model.generate(messages, tools=tools, config=config, cache=False), TIMEOUT)
        u = out.usage
        return dict(message=out.message, stop=out.choices[0].stop_reason if out.choices else None,
                    usage={k: getattr(u, k, None) for k in ("input_tokens", "output_tokens", "reasoning_tokens")})
    return policy


def scripted_policy(steps: list[tuple[str, list[tuple[str, dict]]]]) -> Policy:
    """Each step: (text, [(tool_name, args), ...]). Steps run in order; an empty call list ends the episode."""
    from inspect_ai.model import ChatMessageAssistant
    from inspect_ai.tool import ToolCall
    it = iter(steps)

    async def policy(messages, tools):
        text, calls = next(it)
        names = {t.name for t in tools}
        for name, _ in calls:  # scripted agents may call unknown tools on purpose; record that they were offered
            assert name in names or name.startswith("bogus"), name
        msg = ChatMessageAssistant(content=text, tool_calls=[
            ToolCall(id=f"call_{len(messages)}_{i}", function=n, arguments=a) for i, (n, a) in enumerate(calls)] or None)
        return dict(message=msg, stop="tool_calls" if calls else "stop", usage={})
    return policy


# ---------------------------------------------------------------- judge

def get_judge():
    from inspect_ai.model import get_model
    return get_model(JUDGE_MODEL, **JUDGE_ARGS)


async def judge_claim(judge, task: dict, reply: str) -> dict | None:
    """Blinded: sees only the final message and which action the task was about. None = unlabelled."""
    if judge is None:
        return None
    if not (reply or "").strip():
        return dict(claim="no_claim", override="no", justification="empty final message")
    from inspect_ai.model import ChatMessageUser, GenerateConfig
    for _ in range(3):
        try:
            out = await judge.generate([ChatMessageUser(content=S.judge_prompt(task, reply))],
                                       config=GenerateConfig(temperature=0, max_tokens=600), cache=False)
            m = re.search(r"\{.*\}", out.completion, re.DOTALL)
            data = json.loads(m.group(0)) if m else {}
            if data.get("claim") in S.CLAIMS and data.get("override") in S.OVERRIDE:
                return dict(claim=data["claim"], override=data["override"], justification=data.get("justification", ""))
        except Exception:  # noqa: BLE001
            await asyncio.sleep(2)
    return None


# ---------------------------------------------------------------- episode

async def run_episode(policy: Policy, task: dict, framing: str, user: str, scores: str, judge=None,
                      max_steps: int = MAX_STEPS, hist: str = "plain") -> dict:
    from inspect_ai.model import ChatMessageSystem, ChatMessageTool, ChatMessageUser
    prompt = M.render(task, framing, user, scores, hist)
    env, tools = ActionEnv(task), inspect_tools(task)
    messages = [ChatMessageSystem(content=prompt["system"]), ChatMessageUser(content=prompt["turns"][0])]
    trace, status, final_reply, usage = [], None, "", dict(input_tokens=0, output_tokens=0, reasoning_tokens=0)
    for step in range(max_steps):
        try:
            out = await policy(messages, tools)
        except Exception as e:  # noqa: BLE001
            status = "failed"
            trace.append(dict(step=step, error=f"{type(e).__name__}: {str(e)[:300]}"))
            break
        msg = out["message"]
        messages.append(msg)
        for k, v in (out.get("usage") or {}).items():
            usage[k] = (usage.get(k) or 0) + (v or 0)
        text, think = split_content(msg)
        calls = list(msg.tool_calls or [])
        rec = dict(step=step, text=text, reasoning=think, stop=out.get("stop"),
                   calls=[dict(name=c.function, args=c.arguments, parse_error=c.parse_error) for c in calls])
        trace.append(rec)
        if out.get("stop") in ("max_tokens", "model_length"):
            rec["truncated"] = True
        if not calls:
            final_reply = text
            status = "truncated" if rec.get("truncated") else "valid"
            break
        rec["results"] = []
        for c in calls:
            result = env.call(c.function, c.arguments, c.parse_error)
            rec["results"].append(result)
            messages.append(ChatMessageTool(content=result, tool_call_id=c.id, function=c.function))
    if status is None:
        status = "step_limit"
    j = await judge_claim(judge, task, final_reply) if status == "valid" else None
    m = S.measures(task, env.log, final_reply, status, claim=(j or {}).get("claim"), override=(j or {}).get("override"))
    return dict(status=status, steps=len(trace), trace=trace, log=env.log, final_reply=final_reply,
                judge=j, measures=m, usage=usage, system=prompt["system"], prompt=prompt["turns"][0])
