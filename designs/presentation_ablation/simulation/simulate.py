"""Simulated scored data for the presentation ablation: analysis tests and the power analysis (no API calls).

  python simulation/simulate.py power [--sims 300]   -> simulation/POWER.md (+ power.json)
  python simulation/simulate.py rows <scenario> OUT  -> a scored.jsonl-like file (tests)

Generative model, anchored on 10A and the old reports (Qwen 3.8, bundle, +0.50):
  block propensity p_b ~ Beta(mean mu[task, materials], concentration KAPPA)   (between-block heterogeneity)
  mu: send fresh 0.62 (10A 10/16), orig 0.74 (53/72); titles fresh 0.40, orig 0.46 (22/48);
      bullets fresh 0.56 (10A 9/16), orig 0.58 (14/24)
  P(behaviour | +0.50, arm) = p_b * retention[arm];  P(behaviour | tied) = TIED (10A and old reports: 0 everywhere)
Qwen 3.5 is simulated at 15% of the 3.8 propensity (old reports: near floor).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import pa_analysis as A  # noqa: E402
from pa_common import RUN  # noqa: E402
from pa_design import plan  # noqa: E402

MU = {("send", "fresh"): 0.62, ("send", "orig"): 0.74, ("titles", "fresh"): 0.40, ("titles", "orig"): 0.46,
      ("bullets", "fresh"): 0.56, ("bullets", "orig"): 0.58, ("send", "insp"): 0.6, ("titles", "insp"): 0.4,
      ("bullets", "insp"): 0.5}
KAPPA = 2.0
TIED = 0.01
M35 = 0.15


def retention(scenario: str, arm: str, materials: str) -> float:
    """Share of the bundle's +0.50 propensity kept by an arm."""
    if arm == "B":
        return 1.0
    if arm == "N":
        return 0.5 if (scenario == "materials" and materials == "orig") else 0.0
    kind, k = arm[0], arm[2]
    if scenario in ("null", "materials"):        # no single component matters: arms equal their endpoint
        return 1.0 if kind == "B" else 0.0
    if scenario == "one":                        # component d alone carries the effect
        return (0.0 if k == "d" else 1.0) if kind == "B" else (0.8 if k == "d" else 0.0)
    if scenario == "partial":                    # d and g each carry half; adding one back restores 30%
        return (0.5 if k in ("d", "g") else 1.0) if kind == "B" else (0.3 if k in ("d", "g") else 0.0)
    if scenario == "small":                      # one component removes 30% of the effect, adds back 20%
        return (0.7 if k == "a" else 1.0) if kind == "B" else (0.2 if k == "a" else 0.0)
    raise ValueError(scenario)


def rows_for(scenario: str, units: dict, seed: int, n_fresh: dict | None = None) -> list[dict]:
    rng = np.random.default_rng(seed)
    items = plan("main", units)
    keep = None
    if n_fresh:
        keep = {(t, b) for t in units for b in units[t]["fresh"][:n_fresh[t]]}
    prop = {}
    out = []
    for it in items:
        if it["materials"] == "fresh" and keep is not None and (it["task"], it["block"]) not in keep:
            continue
        kb = (it["task"], it["block"])
        if kb not in prop:
            mu = MU[(it["task"], "fresh" if scenario == "null" else it["materials"])]  # null: no materials effect
            prop[kb] = rng.beta(mu * KAPPA, (1 - mu) * KAPPA)
        p = prop[kb] * retention(scenario, it["arm"], it["materials"]) if it["score"] == "p050" else TIED
        if it["model"] != "Qwen 3.8":
            p *= M35
        valid = rng.random() > 0.005
        out.append({k: it[k] for k in ("key", "stage", "part", "task", "block", "materials", "arm", "score", "gap",
                                       "model", "rep")} |
                   dict(completion="valid" if valid else "empty", outcome=bool(rng.random() < p) if valid else None,
                        violates=None, cost=0.002))
    return out


def power(sims: int, out_md: Path):
    units = json.loads((RUN / "units.json").read_text())
    A.N_FLIP, A.N_PERM, A.N_BOOT = 2000, 1000, 100
    tests = {"materials": ["PRES", "MAT"], "one": ["PRES", "REM:d", "ADD:d", "FWER_other_part2"],
             "partial": ["REM:d", "ADD:d"], "small": ["REM:a", "ADD:a"], "null": ["FWER_part2", "MAT"]}
    import pa_design
    res = {}
    for n, r38 in ((16, 1), (24, 1), (32, 1), (24, 2), (32, 2)):
        nf = {"send": n, "titles": n, "bullets": n}
        pa_design.FRESH_REPS.update({"Qwen 3.8": r38})
        for sc, names in tests.items():
            hits = {k: 0 for k in names}
            effects = {k: [] for k in names}
            for s in range(sims):
                rows = rows_for(sc, units, 1000 * n + 100000 * r38 + s, nf)
                D = A.Data(rows)
                c = A.contrasts(D, ["send", "titles"], "Qwen 3.8", s)
                A.holm(c["part1"])
                A.holm(c["part2"])
                for k in names:
                    if k == "FWER_part2":
                        hits[k] += any(r["p_holm"] < 0.05 for r in c["part2"].values())
                    elif k == "FWER_other_part2":
                        hits[k] += any(r["p_holm"] < 0.05 for n2, r in c["part2"].items() if not n2.endswith(":d"))
                    else:
                        fam = c["part1"] if k in ("PRES", "MAT") else c["part2"]
                        hits[k] += fam[k]["p_holm"] < 0.05
                        effects[k].append(fam[k]["estimate"])
            res[f"{n}|{r38}|{sc}"] = {k: dict(rate=hits[k] / sims, mean_effect=float(np.mean(effects[k])) if effects[k]
                                        else None) for k in names}
            print(n, r38, sc, {k: round(v["rate"], 2) for k, v in res[f"{n}|{r38}|{sc}"].items()}, flush=True)
    (HERE / "power.json").write_text(json.dumps(res, indent=1))
    out_md.write_text(power_md(res, sims))


def power_md(res: dict, sims: int) -> str:
    L = ["# Power and calibration (simulation)", "",
         f"`python simulation/simulate.py power --sims {sims}`; {sims} simulated datasets per row. Primary model "
         "Qwen 3.8, pooled over sending + titles/sign-offs, the frozen tests (sign-flip / permutation, Holm within "
         "the Part 1 family of 2 and the Part 2 family of 13), alpha 0.05. Monte Carlo resolution here: 2,000 "
         "flips / 1,000 permutations (the real analysis uses 20,000).", "",
         "**Effect-size anchors (10A + old reports, Qwen 3.8):** bundle +0.50 rate on fresh blocks: sending 10/16, "
         "bullets 9/16; old reports at +0.50: sending 53/72, titles/sign-offs 22/48, bullets 14/24; tied 0 in every "
         "cell; 10A new presentation 0/16 at both scores. Block propensities vary (Beta, concentration 2), so a "
         "block's +0.50 rate ranges widely, as the old per-scenario spreads did. Original-materials cells use 3 "
         "(sending, titles: 12 units) or 6 (bullets: 6 units) repetitions per block, 36 episodes per cell.", "",
         "Scenarios: **materials** = the new presentation keeps half the effect on original materials only "
         "(PRES and MAT both true); **one** = component d alone carries the whole effect (removing it -> 0; adding "
         "it to N restores 80%); **partial** = d and g each carry half (removal keeps 50%, addition restores 30%); "
         "**small** = component a removes 30% / adds back 20%; **null** = no component matters and original = fresh "
         "materials (calibration of the Part 2 family-wise error and of MAT).", "",
         "| fresh blocks per task | Qwen 3.8 generations per fresh cell | scenario | test | P(Holm p < 0.05) | "
         "mean estimate |", "|---|---|---|---|---|---|"]
    for key, d in res.items():
        n, r38, sc = key.split("|")
        for k, v in d.items():
            me = "" if v["mean_effect"] is None else f"{v['mean_effect']:+.3f}"
            L.append(f"| {n} | {r38} | {sc} | {k} | {v['rate']:.2f} | {me} |")
    L += ["", "## Choice", "",
          "**32 fresh blocks per task** (sending: 10A's 16 + 16 new; bullets: 10A's 16 + 16 new; titles: 16 new "
          "tasks x 2 sub-features). See the table: with 32 blocks a component that carries the whole effect, or "
          "half of it, is detected with high power after Holm over 13, and the family-wise false-positive rate under "
          "the null stays near or below 0.05. Small effects (a 30% removal, about 0.15 pooled) are not reliably "
          "detectable at any size we can author cheaply; read null component results as 'no large effect', not "
          "'no effect'. 24 blocks lose noticeable power for the partial scenario, so 32 is used.", ""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["power", "rows"])
    ap.add_argument("scenario", nargs="?", default="one")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--sims", type=int, default=300)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    if a.cmd == "power":
        power(a.sims, HERE / "POWER.md")
    else:
        units = json.loads((RUN / "units.json").read_text())
        rows = rows_for(a.scenario, units, a.seed)
        Path(a.out).write_text("".join(json.dumps(r) + "\n" for r in rows))


if __name__ == "__main__":
    main()
