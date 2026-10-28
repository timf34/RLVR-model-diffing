"""Offline tests for the attribution experiment (no API calls). Run: ../../.venv/bin/python am.py attribution offline"""
from __future__ import annotations

import asyncio
import random
import re
import tempfile
from pathlib import Path

from action_mechanisms.attribution import adversarial, analysis, design, rubric
from action_mechanisms.attribution.scenarios import BY_ID, SCENARIOS
from action_mechanisms.shared import actions, families, framing, judge, serving
from action_mechanisms.shared.env import SimEnv
from action_mechanisms.shared.episode import run_tool_episode, scripted_policy

ROOT = Path(__file__).resolve().parents[1]


def check_scenarios():
    main = [s for s in SCENARIOS if s["split"] == "main"]
    insp = [s for s in SCENARIOS if s["split"] == "inspection"]
    assert len(main) == 6 and len(insp) == 2
    for f in families.FAMILIES:
        assert sum(s["family"] == f for s in main) == 2, f
    assert len({s["family"] for s in insp}) == 2
    assert len(BY_ID) == len(SCENARIOS)
    old = (ROOT.parent / "action" / "materials.py").read_text().lower()
    fam_text = repr(families.FAMILIES).lower()
    for s in SCENARIOS:
        for k in ("id", "family", "split", "request", "facts", "key", "order", "args"):
            assert k in s, (s["id"], k)
        assert 0 <= s["order"] <= 3 and s["request"] == s["request"].lower() and s["request"].startswith("hey")
        fam = families.FAMILIES[s["family"]]
        assert set(s["args"]) == set(fam["fields"]), s["id"]
        assert fam["reserve"] not in s["request"]
        # fresh: no recipient address, distinctive name or id reused from earlier materials / family examples
        for tok in re.findall(r"[\w.]+@[\w.]+", s["request"]) + [s["id"]]:
            assert tok.lower() not in old and tok.lower() not in fam_text, (s["id"], tok)
        # every needed fact is in the request; the fixed draft contains every fact and the key field
        for alts in s["facts"]:
            assert any(a.lower() in s["request"] for a in alts), (s["id"], alts)
        log = [dict(name=fam["save"][0], kind="save", args=s["args"], ok=True, result="", phase="act")]
        cm = actions.content_measures(s, log)
        assert cm["task_done"], (s["id"], cm)


def check_plan():
    for split, n in (("inspection", 2 * 8 * 3 * 1), ("main", 6 * 8 * 3 * 4)):
        items = design.plan(split)
        assert len(items) == n, (split, len(items))
        assert len({i["key"] for i in items}) == n
        assert all(i["key"].startswith(split + "|") and i["kind"] == "assessment" for i in items)
        assert {i["cell"] for i in items} == set(design.CELLS) and len(design.CELLS) == 8
        assert {i["model"] for i in items} == set(serving.labels())
        assert all(BY_ID[i["scenario"]]["split"] == split for i in items)


def _without(text: str, *subs: str) -> str:
    for i, s in enumerate(subs):
        assert text.count(s) == 1, (s, text.count(s))
        text = text.replace(s, f"\x00{i}\x00")
    return text


def check_render():
    """Every intended difference is machine-checked; everything else is byte-identical."""
    assert design.INTRO["self"].replace(" you ", " another assistant ") == design.INTRO["other"]
    hi, lo = (design.EVAL_LINE.format(score=v) for v in (design.SCORES["high"], design.SCORES["low"]))
    for s in SCENARIOS:
        fam = families.FAMILIES[s["family"]]
        trs = {a: design.transcript(s, a) for a in design.ACTIONS}
        for a, tr in trs.items():
            assert tr.startswith(design.OPEN) and tr.endswith(design.CLOSE)
            assert rubric.full_request(s) in tr and tr.count(fam["reserve"]) == 1
            for leak in ("evaluator", "0.93", "0.39", "another assistant", " you handled", "score"):
                assert leak not in tr, (s["id"], leak)
            texts = {}
            for at in design.ATTRIBUTIONS:
                for sc in design.SCORES:
                    u = design.user_text(s, at, sc, a)
                    assert u.count(tr) == 1 and u.endswith("\n\n" + design.QUESTION)
                    assert u.startswith(design.INTRO[at] + "\n\n" + design.OPEN)
                    assert u.split("\n\n")[-2] == design.EVAL_LINE.format(score=design.SCORES[sc])
                    texts[(at, sc)] = u
            # attribution: only the intro differs (transcript, eval line and question identical)
            for sc in design.SCORES:
                assert _without(texts[("self", sc)], design.INTRO["self"]) == \
                    _without(texts[("other", sc)], design.INTRO["other"])
            # score: only the eval line digits differ; the line is outside the transcript block
            for at in design.ATTRIBUTIONS:
                assert _without(texts[(at, "high")], hi) == _without(texts[(at, "low")], lo)
                assert texts[(at, "high")].index(hi) > texts[(at, "high")].index(design.CLOSE)
        # action: only the tool name (call + result header) and the result line differ
        save, commit = fam["save"][0], fam["commit"][0]
        rs, rc = design.tool_result(s, "compliant"), design.tool_result(s, "violating")
        assert trs["compliant"].count(save) == 2 and trs["violating"].count(commit) == 2
        a = trs["compliant"].replace(rs, "\x00R\x00").replace(save, "\x00T\x00")
        b = trs["violating"].replace(rc, "\x00R\x00").replace(commit, "\x00T\x00")
        assert a == b, s["id"]
        assert "not been" in rs or "No invitation" in rs
        assert ("delivered" in rc or "visible to everyone" in rc) and "local" not in rc
    # render(): deterministic; identical across models and samples; system neutral; no tools
    items = design.plan("main") + design.plan("inspection")
    by = {}
    for i in items:
        r = design.render(i)
        assert r == design.render(i) and r["system"] == framing.SYSTEM and r["tools"] == []
        by.setdefault((i["scenario"], i["cell"]), r)
        assert by[(i["scenario"], i["cell"])] == r
        # judge template: blind to attribution and score
        for leak in (hi, lo, design.INTRO["self"], design.INTRO["other"], "0.93", "0.39", "another assistant"):
            assert leak not in r["judge_prompt_template"], leak
        assert "{ANSWER}" in r["judge_prompt_template"]
    for sid in {i["scenario"] for i in items}:
        for a in design.ACTIONS:
            tpls = {by[(sid, f"{at}-{sc}-{a}")]["judge_prompt_template"]
                    for at in design.ATTRIBUTIONS for sc in design.SCORES}
            assert len(tpls) == 1, (sid, a)
    # no ordinary/RL pairs exist in this experiment, so framing.check_pair has nothing to check; guard instead that
    # no RL framing term appears anywhere
    for s in SCENARIOS:
        u = design.user_text(s, "self", "high", "violating")
        assert all(framing.term(k, "rl") not in u for k in framing.TERMS)


async def check_tool_loop():
    """The transcript's tool results are exactly what the real tool loop returns for the same calls."""
    for s in SCENARIOS:
        fam = families.FAMILIES[s["family"]]
        for a, name in (("compliant", fam["save"][0]), ("violating", fam["commit"][0])):
            env = SimEnv(s["family"], "external")
            rec = await run_tool_episode(scripted_policy([("", [(name, dict(s["args"]))]), ("Done.", [])]),
                                         framing.SYSTEM, rubric.full_request(s), env)
            assert rec["status"] == "valid" and rec["log"][0]["result"] == design.tool_result(s, a)
            m = actions.action_measures(rec["log"], rec["status"])
            assert m["acted"] == (a == "violating") and m["saved"] == (a == "compliant")
            assert actions.content_measures(s, rec["log"])["task_done"]


def _capture_policy(text, reasoning="", stop="stop", seen=None):
    from inspect_ai.model import ChatMessageAssistant, ContentReasoning, ContentText

    async def policy(messages, tools, tool_choice=None):
        if seen is not None:
            seen.append((messages, tools))
        if text == "RAISE":
            raise RuntimeError("simulated API failure")
        content = ([ContentReasoning(reasoning=reasoning)] if reasoning else []) + [ContentText(text=text)]
        return dict(message=ChatMessageAssistant(content=content), stop=stop, usage={"input_tokens": 10,
                                                                                     "output_tokens": 5})
    return policy


async def check_run():
    item = next(i for i in design.plan("inspection") if i["cell"] == "self-high-violating")
    prompts = []

    def fake(prompt):
        prompts.append(prompt)
        ans = prompt.split("<answer>")[1].split("</answer>")[0]
        return dict(verdict="follows" if "Yes" in ans else "violates" if "No" in ans else "unclear",
                    claims_permission="no", uses_evaluator_approval="yes" if "evaluator" in ans else "no",
                    mentions_evaluator="yes" if "evaluator" in ans else "no")
    fj = judge.FakeJudge(fake)
    seen = []
    r = await design.run(item, _capture_policy("Yes, it sent the message as the evaluator approved.",
                                               reasoning="SECRET_REASONING the score is high", seen=seen), fj)
    msgs, tools = seen[0]
    rend = design.render(item)
    assert tools == [] and len(msgs) == 2 and msgs[0].text == framing.SYSTEM and msgs[1].text == rend["user"]
    assert r["status"] == "valid" and r["reasoning"].startswith("SECRET")
    m = r["measures"]
    assert m["truth"] == "violates" and m["judged_follows"] and not m["correct"] and m["uses_evaluator_approval"]
    assert m["regex_opener"] == "follows" and m["regex_agree"] is True
    p = prompts[-1]
    assert "SECRET" not in p and "0.93" not in p and "you handled" not in p and "another assistant" not in p
    assert p == rend["judge_prompt_template"].replace("{ANSWER}", "Yes, it sent the message as the evaluator approved.")
    # correct identification
    r = await design.run(item, _capture_policy("No — the user said not to send."), fj)
    assert r["measures"]["correct"] and r["measures"]["judged_violates"] and not r["measures"]["claims_permission"]
    # compliant + yes
    ci = next(i for i in design.plan("inspection") if i["cell"] == "other-low-compliant")
    r = await design.run(ci, _capture_policy("Yes, it saved a draft."), fj)
    assert r["measures"]["truth"] == "follows" and r["measures"]["correct"]
    # unclear counts as incorrect
    r = await design.run(item, _capture_policy("Hard to say."), fj)
    assert r["measures"]["unclear"] and not r["measures"]["correct"] and r["measures"]["regex_opener"] is None
    # API failure, truncation and empty answers are never judged
    n = len(prompts)
    r = await design.run(item, _capture_policy("RAISE"), fj)
    assert r["status"] == "failed" and r["judge"] is None
    r = await design.run(item, _capture_policy("Yes, partial", stop="max_tokens"), fj)
    assert r["status"] == "truncated" and r["judge"] is None
    r = await design.run(item, _capture_policy("   "), fj)
    assert r["status"] == "empty" and r["judge"] is None
    assert len(prompts) == n
    # unparseable judge -> failed (retried on resume)
    bad = judge.FakeJudge(lambda p: dict(verdict="maybe", claims_permission="no", uses_evaluator_approval="no",
                                         mentions_evaluator="no"))
    r = await design.run(item, _capture_policy("Yes."), bad)
    assert r["status"] == "failed" and r["error"] == "judge unparseable"


async def check_adversarial_plumbing():
    """Adversarial set through the judge path with a FakeJudge that returns the expected labels."""
    for name, sid, action, answer, exp in adversarial.CASES:
        assert sid in BY_ID and action in design.ACTIONS and set(exp) <= set(rubric.SCHEMA), name
        for k, v in exp.items():
            assert v in rubric.SCHEMA[k], (name, k, v)
        full = dict(verdict="unclear", claims_permission="no", uses_evaluator_approval="no",
                    mentions_evaluator="no") | exp
        s = BY_ID[sid]
        out = await judge.label(rubric.judge_prompt(s, action, design.tool_result(s, action), answer), rubric.SCHEMA,
                                judge=judge.FakeJudge(lambda p, full=full: full))
        assert out["labels"] == full
        item = dict(action=action)
        m = design.measures(item, out["labels"], answer)
        assert m["correct"] == (full["verdict"] == ("follows" if action == "compliant" else "violates"))


def check_analysis():
    rng = random.Random(3)
    recs = []
    for split in ("main",):
        for i in design.plan(split):
            v = rng.choice(["follows", "violates", "violates", "unclear"])
            labels = dict(verdict=v, claims_permission=rng.choice("yn") == "y" and "yes" or "no",
                          uses_evaluator_approval="no", mentions_evaluator="no")
            ans = {"follows": "Yes.", "violates": "No.", "unclear": "Hmm."}[v]
            recs.append(i | dict(status="valid", answer=ans, reasoning="", usage={}, judge_usage={},
                                 judge=dict(labels=labels, justification=""), measures=design.measures(i, labels, ans)))
    recs[0] = recs[0] | dict(status="truncated", judge=None)
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "main"
        analysis.analyse(recs, out, {}, fast=True)
        txt = (out / "RESULTS.md").read_text()
        assert "Primary test" in txt and "empirical size" in txt and (out / "review" / "REVIEW_SHEET.md").exists()
        sheet = (out / "review" / "REVIEW_SHEET.md").read_text()
        assert not any(m in sheet for m in serving.labels()) and "self-" not in sheet and "0.93" not in sheet
        assert sheet.count("## R") == 40


def main():
    families.check()
    framing.check()
    actions.check()
    rubric.check()
    check_scenarios()
    check_plan()
    check_render()
    asyncio.run(check_tool_loop())
    asyncio.run(check_run())
    asyncio.run(check_adversarial_plumbing())
    check_analysis()
    print("attribution offline tests pass")
