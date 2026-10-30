"""Render the sending prompts and the item grid (no API, no GPU).

  .venv/bin/python designs/steer_transfer/st_prepare.py [--stage main|bridge|smoke]

Prompts are the presentation ablation's old-bundle (arm B) sending prompts, rendered by its own renderer
(pa_render.render) with the archived materials. Checks, all asserted:
  * conflict and tied prompts are byte-identical (same sha) to the archived run/main/send prompts for every block;
  * reversed differs from conflict ONLY in the displayed score strings (0.750 <-> 0.250);
  * nohist = the tied prompt with the scored-records section removed (nothing else changes);
  * tools, tool descriptions and system prompt are identical across arms.
Writes run/<stage>/send/{items.jsonl, prompts.jsonl, blocks.json, prepare.json}.
"""
from __future__ import annotations

import argparse
import json
import re

from st_common import ARM, MATERIALS, MODELS, PA, REPS, RUN, SCORE_ARMS, conditions, iter_jsonl, jhash

import pa_common  # noqa: E402  (presentation ablation, read-only)
from pa_materials import adapter  # noqa: E402
from pa_render import SCORED_HEAD, arm_cfg, render  # noqa: E402


def nohist(conv: dict) -> dict:
    """Tied prompt minus the 'SCORED SUBMISSIONS' section (arm B: the observation is the single user turn)."""
    assert conv["packet_tool"] is None and len(conv["messages"]) == 1
    u = conv["messages"][0]["content"]
    i, j = u.index(f"\n\n{SCORED_HEAD}\n"), u.index("\n\nEND OBSERVATION")
    out = json.loads(json.dumps(conv))
    out["messages"][0]["content"] = u[:i] + u[j:]
    return out


def render_all(K, units) -> dict:
    """-> {(block, arm): conv}"""
    out = {}
    for u in units:
        for a, g in SCORE_ARMS.items():
            out[(u["block"], a)] = render(K, u, arm_cfg(ARM), g if g is not None else 0.0)
        out[(u["block"], "nohist")] = nohist(out[(u["block"], "nohist")])
    return out


def checks(convs: dict, units) -> list[str]:
    arch = {p["input_sha256"]: p["input"] for p in iter_jsonl(PA / "run" / "main" / "send" / "prompts.jsonl")}
    arch_items = {(i["block"], i["score"]): i["input_sha256"] for i in iter_jsonl(PA / "run" / "main" / "send" /
                                                                                     "items.jsonl") if i["arm"] == ARM}
    n = 0
    for u in units:
        b = u["block"]
        for a, s in (("conflict", "p050"), ("tied", "tied")):
            h = arch_items[(b, s)]
            assert jhash(convs[(b, a)]) == h and arch[h] == convs[(b, a)], f"{b} {a}: differs from the archive"
            n += 1
        c, r, t, nh = (convs[(b, a)] for a in ("conflict", "reversed", "tied", "nohist"))
        for x in (r, t, nh):
            assert x["system"] == c["system"] and x["tools"] == c["tools"] and x["packet_tool"] == c["packet_tool"]
        cu, ru = c["messages"][0]["content"], r["messages"][0]["content"]
        sw = re.sub(r"0\.(750|250)", lambda m: "0.250" if m[1] == "750" else "0.750", cu)
        assert sw == ru and cu.count("0.750") == 2 and cu.count("0.250") == 2, f"{b}: reversed is not a pure swap"
        assert "0.500" not in nh["messages"][0]["content"] and SCORED_HEAD not in nh["messages"][0]["content"]
        assert t["messages"][0]["content"].startswith(nh["messages"][0]["content"].split("\n\nEND OBSERVATION")[0])
    return [f"{n} conflict/tied prompts byte-identical to the archived presentation-ablation prompts",
            f"{len(units)} blocks: reversed = conflict with 0.750<->0.250 swapped only; nohist = tied minus records",
            "system prompt, tools and tool descriptions identical across score arms"]


def plan(stage: str, units) -> list[dict]:
    items = []
    blocks = [u["block"] for u in units]
    if stage == "smoke":
        blocks, reps = blocks[:2], 1
    elif stage == "bridge":
        reps = REPS
    else:
        reps = REPS
    for model in MODELS:
        conds = ["none"] if stage == "bridge" else conditions(model)
        arms = ("conflict", "tied") if stage == "bridge" else tuple(SCORE_ARMS)
        if stage == "smoke":
            conds = [c for c in conds if c == "none" or c.endswith("_+0.3")]
        for b in blocks:
            for a in arms:
                for c in conds:
                    for rep in range(reps):
                        items.append(dict(key=f"st|{stage}|send|{b}|{a}|{model}|{c}|{rep}", stage=stage, task="send",
                                          block=b, materials=b.split(":")[0], arm=ARM, score=a, cond=c,
                                          model=model, rep=rep))
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="main", choices=["main", "bridge", "smoke"])
    a = ap.parse_args()
    pa_common.load_kind("send")
    K = adapter("send")
    units = [u for m in MATERIALS for u in K.units(m)]
    convs = render_all(K, units)
    log = checks(convs, units)
    items = plan(a.stage, units)
    d = RUN / a.stage / "send"
    d.mkdir(parents=True, exist_ok=True)
    prompts = {}
    with (d / "items.jsonl").open("w") as f:
        for it in items:
            conv = convs[(it["block"], it["score"])]
            h = jhash(conv)
            prompts[h] = conv
            f.write(json.dumps(it | dict(input_sha256=h), ensure_ascii=False) + "\n")
    with (d / "prompts.jsonl").open("w") as f:
        for h in sorted(prompts):
            f.write(json.dumps(dict(input_sha256=h, input=prompts[h]), ensure_ascii=False) + "\n")
    used = {it["block"] for it in items}
    ub = {u["block"]: u for u in units}
    (d / "blocks.json").write_text(json.dumps({b: dict(raw=ub[b]["raw"], sub=None, scenario=ub[b]["scenario"],
                                                      materials=ub[b]["materials"], family=ub[b]["family"])
                                               for b in sorted(used)}, indent=1, ensure_ascii=False))
    info = dict(stage=a.stage, checks=log, n_items=len(items), n_prompts=len(prompts), n_blocks=len(used),
                items_digest=jhash([[i["key"], i.get("input_sha256")] for i in items]))
    (d / "prepare.json").write_text(json.dumps(info, indent=1))
    print("\n".join(log))
    print(f"{a.stage}: {len(items)} items, {len(prompts)} prompts, {len(used)} blocks")


if __name__ == "__main__":
    main()
