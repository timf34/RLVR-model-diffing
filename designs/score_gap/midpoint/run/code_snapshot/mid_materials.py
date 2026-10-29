"""EXPLORATORY score-midpoint experiment: prompts (see ANALYSIS_PLAN.md).

A wrapper around the two existing score-gap renderers, which are loaded read-only and never modified:
  upsell  designs/score_gap/recommendation/gap_materials.py  (-> designs/recommendation/rec_materials.py)
  send    designs/score_gap/sending/gap_materials.py         (-> designs/action/materials.py)
Both renderers already take the per-slot scores as a parameter (`examples(..., slot_scores / pair_scores)`), so the
only thing this file changes is the score strings: each pair here is rendered at 2 decimals, the same pair in every
history slot. `check()` asserts that across conditions only the score numbers change, and that the 0.75/0.25 cell
reproduces the existing score-gap prompts at +0.50 (rendered 0.750/0.250) apart from the decimal places.

Note: this module loads designs/action/materials.py under the name `materials`; never import designs/rl_context
modules (which also define `materials`/`score`) in the same process.
"""
from __future__ import annotations

import importlib.util
import itertools
import re
import sys

from mid_design import (BIG, MODELS, NONE, PAIRS, ROOT, SAMPLES, SEND_ORDINARY_PAIRS, UPSELL_BASELINE,
                        UPSELL_PANELS, label)

SG = ROOT / "designs" / "score_gap"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


GU = _load("gap_materials_upsell", SG / "recommendation" / "gap_materials.py")   # imports rec_materials
GS = _load("gap_materials_send", SG / "sending" / "gap_materials.py")            # imports action materials
MU = GU.M   # designs/recommendation/rec_materials.py
MS = GS.M   # designs/action/materials.py

UPSELL_SCEN = MU.SCENARIOS + MU.INSPECTION          # index = counterbalancing index si (as in gap_materials.check)
SEND_TASKS = {t["id"]: t for t in MS.TASKS + MS.INSPECTION_TASKS}


# ---------------------------------------------------------------- rendering

def upsell_render(sid: str, panel: str, pair) -> dict:
    si = next(i for i, s in enumerate(UPSELL_SCEN) if s["id"] == sid)
    s = UPSELL_SCEN[si]
    if pair is None:
        return GU.render(s, si, panel, None)          # panel is nohist_chat / nohist_bundle
    return GU.render_with(s, GU.examples(si, 0, [tuple(pair), tuple(pair)]), panel)


def send_render(tid: str, panel: str, pair) -> dict:
    task = SEND_TASKS[tid]
    if pair is None:
        return GS.render(task, panel, GS.NONE)
    return GS.render_with(task, panel, GS.examples(task, None, [tuple(pair), tuple(pair)]))


def render(item: dict) -> dict:
    pair = None if item["pair"] == NONE else tuple(item["pair"].split("/"))
    fn = upsell_render if item["env"] == "upsell" else send_render
    return fn(item["scenario"], item["panel"], pair)


# ---------------------------------------------------------------- plan

def conditions():
    """(env, panel, pair) cells."""
    out = [("upsell", p, pr) for p, pr in itertools.product(UPSELL_PANELS, PAIRS)]
    out += [("upsell", b, None) for b in dict.fromkeys(UPSELL_BASELINE.values())]
    out += [("send", "bundle", pr) for pr in PAIRS + (None,)]
    out += [("send", "ordinary", pr) for pr in SEND_ORDINARY_PAIRS]
    return out


def n_samples(env, panel) -> int:
    return SAMPLES["upsell"] if env == "upsell" else SAMPLES[f"send_{panel}"]


def plan(tag="mid", upsell_ids=None, send_ids=None, conds=None, samples=None) -> list[dict]:
    upsell_ids = [s["id"] for s in MU.SCENARIOS] if upsell_ids is None else upsell_ids
    send_ids = [t["id"] for t in MS.TASKS] if send_ids is None else send_ids
    out = []
    for env, panel, pair in (conds or conditions()):
        for sid in (upsell_ids if env == "upsell" else send_ids):
            for m, r in itertools.product(MODELS, range(samples or n_samples(env, panel))):
                lab = label(pair)
                out.append(dict(key=f"{tag}|{env}|{sid}|{panel}|{lab}|{m}|{r}", set=tag, env=env, scenario=sid,
                                panel=panel, pair=lab, model=m, rep=r,
                                family=SEND_TASKS[sid]["family"] if env == "send" else None))
    return out


def inspection_plan() -> list[dict]:
    """Setup check on inspection-only scenarios (never in the main run)."""
    hi, rev = ("0.90", "0.70"), ("0.10", "0.30")
    conds = [("upsell", p, pr) for p in UPSELL_PANELS for pr in (hi, rev)] + [("upsell", "nohist_chat", None)]
    conds += [("send", "bundle", pr) for pr in (hi, rev, None)] + [("send", "ordinary", ("0.75", "0.25"))]
    return plan("inspect", [MU.INSPECTION[0]["id"]], [MS.INSPECTION_TASKS[0]["id"]], conds, samples=1)


# ---------------------------------------------------------------- checks

SCORE2 = re.compile(r"(?<![\d.])[01]\.\d{2}(?![\d])")
SENT_C, SENT_S = "⁣CONFLICT⁣", "⁣COMPLY⁣"


def _only_scores_change(template: dict, prompts: dict, n_slots=4):
    """Every pair's prompt equals the sentinel template with the sentinels replaced by that pair's scores."""
    t = template["turns"][0]
    assert t.count(SENT_C) == n_slots // 2 and t.count(SENT_S) == n_slots // 2, "sentinels"
    base_count = len(SCORE2.findall(t))
    for pair, v in prompts.items():
        assert v["system"] == template["system"] and len(v["turns"]) == 1
        assert v["turns"][0] == t.replace(SENT_C, pair[0]).replace(SENT_S, pair[1]), pair
        assert len(SCORE2.findall(v["turns"][0])) == base_count + n_slots, pair
    # and therefore: with the scores masked, all conditions are byte-identical
    strip = {SCORE2.sub("S", v["turns"][0]) for v in prompts.values()}
    assert len(strip) == 1


def _to_2dp(text: str, a: str, b: str) -> str:
    for x in (a, b):
        text = re.sub(rf"(?<![\d.]){re.escape(x)}(?![\d])", x[:-1], text)
    return text


def check():
    GU.check()
    GS.check()
    n = 0
    # upsell
    for si, s in enumerate(UPSELL_SCEN):
        for panel in UPSELL_PANELS:
            template = GU.render_with(s, GU.examples(si, 0, [(SENT_C, SENT_S)] * 2), panel)
            ex = GU.examples(si, 0, [(SENT_C, SENT_S)] * 2)
            assert [x[0] for x in ex if x[3]] == [SENT_C] * 2 and [x[0] for x in ex if not x[3]] == [SENT_S] * 2
            prompts = {pr: upsell_render(s["id"], panel, pr) for pr in PAIRS}
            _only_scores_change(template, prompts)
            # 0.75/0.25 reproduces the existing +0.50 prompt (0.750/0.250) apart from decimal places
            old = GU.render(s, si, panel, 0.5)
            assert old["turns"][0].count("0.750") == 2 and old["turns"][0].count("0.250") == 2
            mine = prompts[BIG[0]]
            assert mine["system"] == old["system"]
            assert mine["turns"][0] == _to_2dp(old["turns"][0], "0.750", "0.250"), (s["id"], panel)
            n += len(prompts) + 1
        for b in dict.fromkeys(UPSELL_BASELINE.values()):
            assert upsell_render(s["id"], b, None) == GU.render(s, si, b, None) == MU.render(s, si, b, GU.WORDING, "none")
    # sending
    for tid, task in SEND_TASKS.items():
        msg = MS.requester_message(task, GS.USER)
        for panel in ("bundle", "ordinary"):
            ex = GS.examples(task, None, [(SENT_C, SENT_S)] * 2)
            assert [x[0] for x in ex if x[2]] == [SENT_C] * 2 and [x[0] for x in ex if not x[2]] == [SENT_S] * 2
            template = GS.render_with(task, panel, ex)
            prompts = {pr: send_render(tid, panel, pr) for pr in PAIRS}
            _only_scores_change(template, prompts)
            for v in prompts.values():
                assert v["turns"][0].count(msg) == 1
                assert v["turns"][0].count(MS.preference(task, GS.USER)) == 5
            old = GS.render(task, panel, 0.5)
            assert old["turns"][0].count("0.750") == 2 and old["turns"][0].count("0.250") == 2
            assert prompts[BIG[0]]["system"] == old["system"]
            assert prompts[BIG[0]]["turns"][0] == _to_2dp(old["turns"][0], "0.750", "0.250"), (tid, panel)
            assert send_render(tid, panel, None) == GS.render(task, panel, GS.NONE) == \
                MS.render(task, panel, GS.USER, "none", "plain")
            n += len(prompts) + 1
    # plan sanity
    items = plan()
    assert len({i["key"] for i in items}) == len(items)
    print(f"mid_materials: checks pass ({n} scenario x panel x condition prompts; only score numbers change across "
          f"conditions; 0.75/0.25 == existing +0.50 prompts at 2 dp). Main plan {len(items)} items, "
          f"inspection {len(inspection_plan())}.")


if __name__ == "__main__":
    check()
    items = plan()
    from collections import Counter
    print(Counter((i["env"], i["panel"], i["model"]) for i in items))
    t = MS.TASKS[0]["id"]
    v = send_render(t, "bundle", ("0.60", "0.40"))
    print(v["turns"][0][-1500:])
