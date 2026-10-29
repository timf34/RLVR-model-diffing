"""Episode loops (adapted from designs/action/agent.py). Real models and scripted agents share the same loop.

run_tool_episode: multi-turn tool loop; the first assistant message without a tool call ends the action phase.
  Optional `followup`: a fixed user question appended after that message. It is asked with tool_choice="none" AND
  the env frozen, so it can never trigger an action; any tool call the model still emits is logged as blocked and
  the follow-up text is scored separately.
run_single: one user turn, no tools (detached assessments, transcript judgments, diagnostics).

Reasoning is kept in `trace[*].reasoning` (researcher-only). `visible` fields never contain reasoning.
Statuses: valid | truncated | step_limit | failed. Actions are always read from env.log, whatever the status, so a
successful commit is never lost because the episode later truncated or failed.
"""
from __future__ import annotations

import asyncio
from typing import Awaitable, Callable

from . import limiter, serving
from .env import SimEnv

MAX_STEPS = 8
RETRIES = 5
Policy = Callable[..., Awaitable[dict]]  # (messages, tools, tool_choice=None) -> {message, stop, usage}


def inspect_tools(specs: list[dict]):
    from inspect_ai.tool import ToolInfo, ToolParam, ToolParams
    return [ToolInfo(name=t["name"], description=t["description"], parameters=ToolParams(
        properties={k: ToolParam(**v) for k, v in t["parameters"]["properties"].items()},
        required=t["parameters"]["required"])) for t in specs]


def split_content(message) -> tuple[str, str]:
    content = message.content
    if isinstance(content, str):
        return content, ""
    text = "\n".join(c.text for c in content if getattr(c, "type", "") == "text")
    reasoning = "\n".join(getattr(c, "reasoning", "") or "" for c in content if getattr(c, "type", "") == "reasoning")
    return text, reasoning


def _transient(e: Exception) -> bool:
    s = f"{type(e).__name__} {e}".lower()
    return any(w in s for w in ("429", "rate", "timeout", "overloaded", "502", "503", "504", "connection", "temporar"))


def model_policy(label: str) -> Policy:
    """Policy for a target model. Each API call holds one slot of the shared cross-process budget for `label`;
    transient errors (429s, timeouts) are retried with exponential backoff outside the slot."""
    model, config = serving.get_target(label)

    async def policy(messages, tools, tool_choice=None):
        for attempt in range(RETRIES):
            try:
                async with limiter.slot(label):
                    out = await asyncio.wait_for(model.generate(messages, tools=tools, tool_choice=tool_choice,
                                                                config=config, cache=False), serving.TIMEOUT)
                u = out.usage
                return dict(message=out.message, stop=out.choices[0].stop_reason if out.choices else None,
                            usage={k: getattr(u, k, None) for k in ("input_tokens", "output_tokens",
                                                                    "reasoning_tokens")},
                            retries=attempt)
            except Exception as e:  # noqa: BLE001
                if attempt == RETRIES - 1 or not _transient(e):
                    raise
                await asyncio.sleep(min(120, 5 * 2 ** attempt))
    policy.label = label
    return policy


def scripted_policy(steps: list[tuple[str, list[tuple[str, dict]]]], label: str = "scripted") -> Policy:
    """Each step: (text, [(tool_name, args), ...]). Use ("RAISE", []) to simulate an API failure at that step."""
    from inspect_ai.model import ChatMessageAssistant
    from inspect_ai.tool import ToolCall
    it = iter(steps)

    async def policy(messages, tools, tool_choice=None):
        text, calls = next(it)
        if text == "RAISE":
            raise RuntimeError("simulated API failure")
        stop = "max_tokens" if text == "TRUNCATE" else ("tool_calls" if calls else "stop")
        text = "" if text == "TRUNCATE" else text
        msg = ChatMessageAssistant(content=text, tool_calls=[
            ToolCall(id=f"call_{len(messages)}_{i}", function=n, arguments=a) for i, (n, a) in enumerate(calls)] or None)
        return dict(message=msg, stop=stop, usage={})
    policy.label = label
    return policy


def _add(usage: dict, u: dict):
    for k, v in (u or {}).items():
        usage[k] = (usage.get(k) or 0) + (v or 0)


async def run_tool_episode(policy: Policy, system: str, user: str, env: SimEnv, max_steps: int = MAX_STEPS,
                           followup: str | None = None) -> dict:
    from inspect_ai.model import ChatMessageSystem, ChatMessageTool, ChatMessageUser
    tools = inspect_tools(env.tools())
    messages = [ChatMessageSystem(content=system), ChatMessageUser(content=user)]
    trace, status, final, usage, error = [], None, "", {}, None
    for step in range(max_steps):
        try:
            out = await policy(messages, tools)
        except Exception as e:  # noqa: BLE001
            status, error = "failed", f"{type(e).__name__}: {str(e)[:300]}"
            break
        msg = out["message"]
        messages.append(msg)
        _add(usage, out.get("usage"))
        text, think = split_content(msg)
        calls = list(msg.tool_calls or [])
        rec = dict(step=step, phase="act", text=text, reasoning=think, stop=out.get("stop"),
                   calls=[dict(name=c.function, args=c.arguments, parse_error=c.parse_error) for c in calls])
        trace.append(rec)
        truncated = out.get("stop") in ("max_tokens", "model_length")
        rec["truncated"] = truncated
        if not calls:
            final, status = text, ("truncated" if truncated else "valid")
            break
        rec["results"] = []
        for c in calls:
            r = env.call(c.function, c.arguments, c.parse_error)
            rec["results"].append(r)
            messages.append(ChatMessageTool(content=r, tool_call_id=c.id, function=c.function))
        if truncated:  # tool calls emitted but the turn hit the token cap: executed, then stop
            status = "truncated"
            break
    if status is None:
        status = "step_limit"
    fu = None
    if followup is not None and status == "valid":
        env.frozen, env.phase = True, "followup"
        messages.append(ChatMessageUser(content=followup))
        try:
            out = await policy(messages, tools, tool_choice="none")
            msg = out["message"]
            _add(usage, out.get("usage"))
            text, think = split_content(msg)
            calls = list(msg.tool_calls or [])
            for c in calls:
                env.call(c.function, c.arguments, c.parse_error)  # logged as blocked, never executed
            fstop = out.get("stop")
            fu = dict(text=text, reasoning=think, stop=fstop, tool_calls=[c.function for c in calls],
                      status="truncated" if fstop in ("max_tokens", "model_length") else
                      ("valid" if text.strip() else "empty"))
            trace.append(dict(step=len(trace), phase="followup", text=text, reasoning=think, stop=fstop,
                              calls=[dict(name=c.function, args=c.arguments) for c in calls]))
        except Exception as e:  # noqa: BLE001
            fu = dict(text="", reasoning="", status="failed", error=f"{type(e).__name__}: {str(e)[:300]}")
    return dict(status=status, error=error, steps=len(trace), trace=trace, log=env.log, final_reply=final,
                followup=fu, env_score=env.final_score(), mode=env.mode, usage=usage)


async def run_single(policy: Policy, system: str | None, user: str) -> dict:
    from inspect_ai.model import ChatMessageSystem, ChatMessageUser
    messages = ([ChatMessageSystem(content=system)] if system else []) + [ChatMessageUser(content=user)]
    try:
        out = await policy(messages, [])
    except Exception as e:  # noqa: BLE001
        return dict(status="failed", error=f"{type(e).__name__}: {str(e)[:300]}", text="", reasoning="", usage={})
    text, think = split_content(out["message"])
    stop = out.get("stop")
    status = "truncated" if stop in ("max_tokens", "model_length") else ("valid" if text.strip() else "empty")
    return dict(status=status, error=None, text=text, reasoning=think, stop=stop, usage=out.get("usage") or {})
