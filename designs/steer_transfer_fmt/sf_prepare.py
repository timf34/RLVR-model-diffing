"""Render the formatting prompts and the item grid (no API, no GPU).

  .venv/bin/python designs/steer_transfer_fmt/sf_prepare.py --stage main [--design full|reduced]
  stages: main (full grid) | smoke (2 scenarios per family, none + xfer/native +0.3, 1 rep)

Prompts are the presentation ablation's arm-B (old bundle) title / sign-off / bullets prompts rendered by its own
renderer with the archived materials. Asserted for EVERY block:
  * conflict (+0.50) and tied prompts are byte-identical (same sha) to the archived run/main/{titles,bullets} prompts;
  * reversed differs from conflict ONLY in the displayed scores (0.750 <-> 0.250; examples, order, wording equal);
  * nohist = the tied prompt with the scored-records section removed (the only unavoidable change; documented);
  * system prompt and (empty) tool list identical across arms.
Writes run/<stage>/fmt/{items.jsonl, prompts.jsonl, blocks.json, prepare.json}.
"""
from __future__ import annotations

import argparse
import json
import re

from sf_common import ARM, FAMILIES, HERE, MATERIALS, MODELS, PA, REPS, SCORE_ARMS, conditions, iter_jsonl, jhash

import pa_common  # noqa: E402
from pa_materials import adapter  # noqa: E402
from pa_render import SCORED_HEAD, arm_cfg, render  # noqa: E402


def nohist(conv: dict) -> dict:
    assert conv["packet_tool"] is None and len(conv["messages"]) == 1
    u = conv["messages"][0]["content"]
    i, j = u.index(f"\n\n{SCORED_HEAD}\n"), u.index("\n\nEND OBSERVATION")
    out = json.loads(json.dumps(conv))
    out["messages"][0]["content"] = u[:i] + u[j:]
    return out


def family_units() -> dict:
    """{family: [unit, ...]} over orig + fresh materials."""
    Ks = {"titles": adapter("titles"), "bullets": adapter("bullets")}
    out = {}
    for fam, (task, sub) in FAMILIES.items():
        out[fam] = [(Ks[task], u) for m in MATERIALS for u in Ks[task].units(m) if u["sub"] == sub]
    return out


def render_all(fu: dict) -> dict:
    convs = {}
    for fam, kus in fu.items():
        for K, u in kus:
            for a, g in SCORE_ARMS.items():
                c = render(K, u, arm_cfg(ARM), 0.0 if g is None else g)
                convs[(u["block"], a)] = nohist(c) if a == "nohist" else c
    return convs


def checks(fu: dict, convs: dict) -> list[str]:
    log, n = [], 0
    for task in ("titles", "bullets"):
        arch = {p["input_sha256"]: p["input"] for p in iter_jsonl(PA / "run/main" / task / "prompts.jsonl")}
        ai = {(i["block"], i["score"]): i["input_sha256"] for i in iter_jsonl(PA / "run/main" / task / "items.jsonl")
              if i["arm"] == ARM}
        for fam, kus in fu.items():
            if FAMILIES[fam][0] != task:
                continue
            for K, u in kus:
                b = u["block"]
                for a, s in (("conflict", "p050"), ("tied", "tied")):
                    h = ai[(b, s)]
                    assert jhash(convs[(b, a)]) == h and arch[h] == convs[(b, a)], f"{b} {a} differs from archive"
                    n += 1
                c, r, t, nh = (convs[(b, a)] for a in ("conflict", "reversed", "tied", "nohist"))
                for x in (r, t, nh):
                    assert x["system"] == c["system"] and x["tools"] == c["tools"] == [] and x["packet_tool"] is None
                cu, ru = c["messages"][0]["content"], r["messages"][0]["content"]
                assert cu.count("0.750") == 2 and cu.count("0.250") == 2, b
                sw = re.sub(r"0\.(750|250)", lambda m: "0.250" if m[1] == "750" else "0.750", cu)
                assert sw == ru, f"{b}: reversed is not a pure score swap"
                nu = nh["messages"][0]["content"]
                assert SCORED_HEAD not in nu and "0.500" not in nu
                assert t["messages"][0]["content"].replace(t["messages"][0]["content"][
                    t["messages"][0]["content"].index(f"\n\n{SCORED_HEAD}\n"):
                    t["messages"][0]["content"].index("\n\nEND OBSERVATION")], "") == nu
    log.append(f"{n} conflict/tied prompts byte-identical to the archived presentation-ablation arm-B prompts")
    log.append("reversed = conflict with 0.750<->0.250 swapped only; nohist = tied minus the scored-records section")
    log.append("system prompt identical and no tools in every arm")
    return log


def plan(stage: str, design: str, fu: dict) -> list[dict]:
    items = []
    for model in MODELS:
        conds = conditions(model)
        if stage == "smoke":
            conds = [c for c in conds if c in ("none", "xfer_+0.3", "native_+0.3")]
        for fam, kus in fu.items():
            scen = [u for _, u in kus]
            reps = 1 if stage == "smoke" else REPS[design][fam]
            if stage == "smoke":
                scen = scen[:2]
            for u in scen:
                for a in SCORE_ARMS:
                    for c in conds:
                        for rep in range(reps):
                            items.append(dict(key=f"sf|{stage}|{fam}|{u['block']}|{a}|{model}|{c}|{rep}",
                                              stage=stage, family=fam, task=FAMILIES[fam][0], block=u["block"],
                                              scenario=u["scenario"], materials=u["materials"], arm=ARM, score=a,
                                              cond=c, model=model, rep=rep))
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="main", choices=["main", "smoke"])
    ap.add_argument("--design", default="full", choices=list(REPS))
    ap.add_argument("--root", default="run", choices=["run", "run_mock"])
    a = ap.parse_args()
    pa_common.load_kind("fmt")
    fu = family_units()
    convs = render_all(fu)
    log = checks(fu, convs)
    items = plan(a.stage, a.design, fu)
    d = HERE / a.root / a.stage / "fmt"
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
    ub = {u["block"]: u for kus in fu.values() for _, u in kus}
    used = sorted({it["block"] for it in items})
    (d / "blocks.json").write_text(json.dumps({b: dict(raw=ub[b]["raw"], sub=ub[b]["sub"], scenario=ub[b]["scenario"],
                                                      materials=ub[b]["materials"], family=ub[b]["family"])
                                               for b in used}, indent=1, ensure_ascii=False))
    counts = {fam: dict(scenarios=len({it["scenario"] for it in items if it["family"] == fam}),
                        generations=sum(it["family"] == fam for it in items)) for fam in FAMILIES}
    info = dict(stage=a.stage, design=a.design, checks=log, n_items=len(items), n_prompts=len(prompts),
                per_family=counts, items_digest=jhash([[i["key"], i.get("input_sha256")] for i in items]))
    (d / "prepare.json").write_text(json.dumps(info, indent=1))
    print("\n".join(log))
    print(f"{a.stage}/{a.design}: {len(items)} items, {len(prompts)} prompts; {counts}")


if __name__ == "__main__":
    main()
