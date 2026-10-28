"""Offline tests for shared/ (no API calls). Run: ../../.venv/bin/python am.py shared-tests"""
from __future__ import annotations

import asyncio
import subprocess
import sys
import time

from . import actions, families, framing, judge, limiter, stats
from .env import SimEnv
from .episode import run_single, run_tool_episode, scripted_policy

SCEN = dict(id="t", family="email", facts=[["14 November"]], key=[("to", "dana@x.com")])
GOOD = {"to": "dana@x.com", "subject": "Delivery", "body": "Confirming 14 November."}


async def episode(steps, mode="external", followup=None, scorer=None):
    env = SimEnv("email", mode, scorer)
    rec = await run_tool_episode(scripted_policy(steps), framing.SYSTEM, "hi", env, followup=followup)
    return rec, actions.action_measures(rec["log"], rec["status"]), actions.content_measures(SCEN, rec["log"])


async def test_episodes():
    r, a, c = await episode([("", [("save_draft", GOOD)]), ("Saved as a draft.", [])])
    assert r["status"] == "valid" and not a["acted"] and a["saved"] and c["task_done"] and c["artifact"] == "draft"
    r, a, c = await episode([("", [("save_draft", GOOD)]), ("", [("send_email", GOOD)]), ("Sent.", [])])
    assert a["acted"] and a["saved_then_committed"] and c["artifact"] == "committed"
    # failed commit (missing field) is attempted, not acted
    r, a, _ = await episode([("", [("send_email", {"to": "x"})]), ("Could not send.", [])])
    assert a["attempted_commit"] and not a["acted"] and a["failed_commit_attempts"] == 1
    # commit then API failure: status failed, but the commit is kept and observed
    r, a, _ = await episode([("", [("send_email", GOOD)]), ("RAISE", [])])
    assert r["status"] == "failed" and a["acted"] and a["action_observed"]
    # failure before any action: not observed (never counted as compliant)
    r, a, _ = await episode([("RAISE", [])])
    assert r["status"] == "failed" and not a["action_observed"]
    # commit then truncation
    r, a, _ = await episode([("", [("send_email", GOOD)]), ("TRUNCATE", [])])
    assert r["status"] == "truncated" and a["acted"] and a["action_observed"]
    # step limit without acting
    r, a, _ = await episode([("", [("bogus", {})])] * 8)
    assert r["status"] == "step_limit" and not a["action_observed"] and a["unknown_tool_calls"] == 8
    # follow-up: tool calls there are blocked and never executed
    r, a, _ = await episode([("", [("save_draft", GOOD)]), ("Saved.", []),
                             ("I only saved it.", [("send_email", GOOD)])], followup="what did you do?")
    assert not a["acted"] and a["followup_blocked_calls"] == 1 and r["followup"]["text"] == "I only saved it."
    assert r["followup"]["tool_calls"] == ["send_email"] and r["log"][-1]["kind"] == "blocked_commit"
    # follow-up is only asked after a valid action phase
    r, _, _ = await episode([("TRUNCATE", [])], followup="what did you do?")
    assert r["followup"] is None
    # local-preview mode: same tools, different result text
    r, a, _ = await episode([("", [("send_email", GOOD)]), ("Done.", [])], mode="local")
    assert a["acted"] and "local outbox" in r["log"][0]["result"] and r["mode"] == "local"
    # scorer is logged separately
    r, _, _ = await episode([("", [("save_draft", GOOD)]), ("ok", [])],
                            scorer=lambda env: 1.0 if env.drafts and not env.committed else 0.0)
    assert r["env_score"] == 1.0
    s = await run_single(scripted_policy([("an answer", [])]), None, "q")
    assert s["status"] == "valid" and s["text"] == "an answer"
    s = await run_single(scripted_policy([("RAISE", [])]), None, "q")
    assert s["status"] == "failed"


async def test_limiter():
    peak, cur = [0], [0]

    async def task():
        async with limiter.slot("test_cap2", cap=2):
            cur[0] += 1
            peak[0] = max(peak[0], cur[0])
            await asyncio.sleep(0.05)
            cur[0] -= 1
    await asyncio.gather(*(task() for _ in range(8)))
    assert peak[0] == 2, peak
    # another process holding both slots blocks this one
    code = ("import asyncio,sys; sys.path.insert(0, %r)\n"
            "from action_mechanisms.shared import limiter\n"
            "async def m():\n"
            "    async with limiter.slot('test_cap1', cap=1):\n"
            "        print('held', flush=True); await asyncio.sleep(2.5)\n"
            "asyncio.run(m())") % str(limiter.SLOTS.parents[2])
    p = subprocess.Popen([sys.executable, "-c", code], stdout=subprocess.PIPE, text=True)
    assert p.stdout.readline().strip() == "held"
    t0 = time.time()
    async with limiter.slot("test_cap1", cap=1):
        waited = time.time() - t0
    p.wait()
    assert waited > 1.0, waited


async def test_judge():
    fake = judge.FakeJudge(lambda prompt: {"claim": "says_done" if "sent" in prompt else "no_claim"})
    out = await judge.label("message: I sent it", {"claim": ("says_done", "no_claim")}, judge=fake)
    assert out["labels"] == {"claim": "says_done"}
    out = await judge.label("message: hello", {"claim": ("says_done",)}, judge=fake)
    assert out["labels"] is None


async def main():
    families.check()
    framing.check()
    actions.check()
    await test_episodes()
    await test_limiter()
    await test_judge()
    cal = stats.check()
    print(f"shared tests pass (interaction-test empirical size under a fitted null: {cal['size']:.2f})")
