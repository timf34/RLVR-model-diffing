"""Frozen analysis for the formatting replication (PLAN.md). Works on real (run/) or mock (run_mock/) data.

  .venv/bin/python designs/steer_transfer_fmt/sf_analysis.py [--root run|run_mock] [--stage main] [--B 4000]

Per family x model, cell arrays over [scenario, condition, score arm]. Rates are among VALID episodes.
  DiD(c) = [override(conflict, c) - override(reversed, c)] - [override(conflict, none) - override(reversed, none)]
Primary family (per formatting family; Holm over 3 families x 2 = 6):
  P1(f): DiD(xfer +0.3)                         transferred vs unsteered
  P2(f): DiD(xfer +0.3) - DiD(native +0.3)      transferred vs native at the SAME strength (not at each optimum)
Additional (labelled, unadjusted 95% CIs): every other condition's DiD and conflict-minus-tied DiD, matched +/- contrasts,
xfer vs native at +/-0.1 and -0.3, xfer vs mean(random), shifts in override and in ANY violation under the reversed,
tied and no-history arms (output-bias / disruption checks), facts_ok shift (competence), valid-share shift, and the
Qwen 3.8 source control. Full strength curves are reported for every direction.
Uncertainty: cluster bootstrap over distinct scenarios (all reps, arms and conditions of a scenario resampled together:
paired), percentile CIs, two-sided bootstrap p. Primary estimates also get worst/best-case bounds that set every
non-valid or missing item in the four cells involved to override 0 or 1 (whichever moves the DiD most).
Writes <root>/<stage>/{scored.jsonl, results.json, REPORT_auto.md}.
"""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np

from sf_common import FAMILIES, HERE, MODELS, SCORE_ARMS, conditions
from sf_score import score_rows

ARMS = list(SCORE_ARMS)
COUNTS = ("override", "complies", "neither", "facts_ok", "malformed")
STATUSES = ("valid", "empty", "truncated", "step_limit", "failed", "missing")


def arrays(rows, family, model):
    conds = conditions(model)
    scen = sorted({r["scenario"] for r in rows if r["family"] == family and r["model"] == model})
    si = {s: i for i, s in enumerate(scen)}
    shape = (len(scen), len(conds), len(ARMS))
    A = {k: np.zeros(shape) for k in COUNTS + STATUSES + ("planned", "recorded")}
    for r in rows:
        if r["family"] != family or r["model"] != model:
            continue
        ix = (si[r["scenario"]], conds.index(r["cond"]), ARMS.index(r["score"]))
        A["planned"][ix] += 1
        A["recorded"][ix] += r["recorded"]
        A[r["completion"]][ix] += 1
        if r["recorded"]:
            A["malformed"][ix] += r.get("malformed", False)
        if r["completion"] == "valid":
            for k in ("override", "complies", "neither", "facts_ok"):
                A[k][ix] += r[k]
    return conds, scen, A


def rate(X, V, j, k):
    return X[:, j, k].sum() / max(V[:, j, k].sum(), 1)


def did(X, V, conds, c, a1="conflict", a2="reversed", ref="none"):
    j, j0, k1, k2 = conds.index(c), conds.index(ref), ARMS.index(a1), ARMS.index(a2)
    return (rate(X, V, j, k1) - rate(X, V, j, k2)) - (rate(X, V, j0, k1) - rate(X, V, j0, k2))


def boot(fn, X, V, B, seed=7):
    est = float(fn(X, V))
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, X.shape[0], size=(B, X.shape[0]))
    vals = np.array([fn(X[ix], V[ix]) for ix in idx])
    lo, hi = np.percentile(vals, [2.5, 97.5])
    p = 2 * min((vals <= 0).mean(), (vals >= 0).mean())
    return dict(est=est, lo=float(lo), hi=float(hi), p=float(min(1.0, max(p, 1.0 / B))))


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, run = [0.0] * len(ps), 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - r) * ps[i]))
        adj[i] = run
    return adj


def bounds(A, conds, terms):
    """terms: list of (sign, cond, arm). Worst/best case DiD when non-valid+missing items are set to 0/1."""
    X, V, P = A["override"].sum(0), A["valid"].sum(0), A["planned"].sum(0)
    out = []
    for direction in (-1, 1):
        tot = 0.0
        for sgn, c, a in terms:
            j, k = conds.index(c), ARMS.index(a)
            nv = P[j, k] - V[j, k]
            fill = nv if (sgn * direction) > 0 else 0.0
            tot += sgn * (X[j, k] + fill) / max(P[j, k], 1)
        out.append(float(tot))
    return dict(min=min(out), max=max(out))


def did_terms(c, ref="none"):
    return [(1, c, "conflict"), (-1, c, "reversed"), (-1, ref, "conflict"), (1, ref, "reversed")]


def analyse(rows, B: int) -> dict:
    res = dict(families={}, primary={})
    prim = []
    for fam in FAMILIES:
        res["families"][fam] = {}
        for model in MODELS:
            conds, scen, A = arrays(rows, fam, model)
            if A["planned"].sum() == 0:
                continue
            X, V = A["override"], A["valid"]
            cells = {}
            for j, c in enumerate(conds):
                for k, a in enumerate(ARMS):
                    v = int(V[:, j, k].sum())
                    cell = {s: int(A[s][:, j, k].sum()) for s in STATUSES + ("planned", "recorded")}
                    cell.update({o: int(A[o][:, j, k].sum()) for o in COUNTS})
                    cell.update({f"{o}_rate": A[o][:, j, k].sum() / max(v, 1) for o in COUNTS[:4]})
                    cells[f"{c}|{a}"] = cell
            eff = {}
            for c in conds[1:]:
                jc = conds.index(c)
                eff[c] = dict(
                    did_conf_rev=boot(lambda x, v, c=c: did(x, v, conds, c), X, V, B),
                    did_conf_tied=boot(lambda x, v, c=c: did(x, v, conds, c, "conflict", "tied"), X, V, B),
                    **{f"override_shift_{a}": boot(lambda x, v, jc=jc, k=ARMS.index(a): rate(x, v, jc, k)
                                                   - rate(x, v, 0, k), X, V, B) for a in ("reversed", "tied", "nohist")},
                    **{f"violation_shift_{a}": boot(lambda x, v, jc=jc, k=ARMS.index(a): (1 - rate(x, v, jc, k))
                                                    - (1 - rate(x, v, 0, k)), A["complies"], V, B)
                       for a in ARMS},
                    facts_shift=boot(lambda x, v, jc=jc: x[:, jc].sum() / max(v[:, jc].sum(), 1)
                                     - x[:, 0].sum() / max(v[:, 0].sum(), 1), A["facts_ok"], V, B),
                    valid_shift=boot(lambda x, v, jc=jc: x[:, jc].sum() / max(v[:, jc].sum(), 1)
                                     - x[:, 0].sum() / max(v[:, 0].sum(), 1), A["valid"], A["planned"], B),
                )
            base = dict(conf_minus_rev=boot(lambda x, v: rate(x, v, 0, 0) - rate(x, v, 0, 1), X, V, B),
                        conf_minus_tied=boot(lambda x, v: rate(x, v, 0, 0) - rate(x, v, 0, 2), X, V, B))
            comp = {}
            dirs = sorted({c.rsplit("_", 1)[0] for c in conds[1:]})
            for d in dirs:
                for s in ("0.1", "0.3"):
                    if f"{d}_+{s}" in conds:
                        comp[f"{d}_+{s} minus {d}_-{s}"] = boot(
                            lambda x, v, d=d, s=s: did(x, v, conds, f"{d}_+{s}") - did(x, v, conds, f"{d}_-{s}"),
                            X, V, B)
            for s in ("+0.1", "-0.1", "+0.3", "-0.3"):
                comp[f"xfer_{s} minus native_{s}"] = boot(
                    lambda x, v, s=s: did(x, v, conds, f"xfer_{s}") - did(x, v, conds, f"native_{s}"), X, V, B)
            for s in ("+0.3", "-0.3"):
                for dn in ("xfer", "native"):
                    comp[f"{dn}_{s} minus mean(random_{s})"] = boot(
                        lambda x, v, s=s, dn=dn: did(x, v, conds, f"{dn}_{s}") - 0.5 * (
                            did(x, v, conds, f"random0_{s}") + did(x, v, conds, f"random1_{s}")), X, V, B)
            xn = did_terms("xfer_+0.3") + [(-s, c, a) for s, c, a in did_terms("native_+0.3")]
            if model == "Qwen 3.5":       # xfer = 3.8's direction, native = 3.5's
                p1 = eff["xfer_+0.3"]["did_conf_rev"] | dict(bounds=bounds(A, conds, did_terms("xfer_+0.3")))
                p2 = comp["xfer_+0.3 minus native_+0.3"] | dict(bounds=bounds(A, conds, xn))
                prim += [(f"{fam}: P1 [3.5] DiD xfer(3.8 dir)+0.3 vs unsteered", p1),
                         (f"{fam}: P2 [3.5] DiD xfer(3.8 dir)+0.3 minus native(3.5 dir)+0.3", p2)]
            else:                          # Qwen 3.8: native = 3.8's direction, xfer = 3.5's
                e = comp["xfer_+0.3 minus native_+0.3"]
                p3 = dict(est=-e["est"], lo=-e["hi"], hi=-e["lo"], p=e["p"])
                b = bounds(A, conds, [(-s, c, a) for s, c, a in xn])
                prim += [(f"{fam}: P3 [3.8] DiD native(3.8 dir)+0.3 minus xfer(3.5 dir)+0.3", p3 | dict(bounds=b))]
            res["families"][fam][model] = dict(
                n_scenarios=len(scen), n_planned=int(A["planned"].sum()), n_recorded=int(A["recorded"].sum()),
                n_valid=int(V.sum()), status_totals={s: int(A[s].sum()) for s in STATUSES},
                cells=cells, effects=eff, baseline=base, comparisons=comp)
    adj = holm([v["p"] for _, v in prim])
    res["primary"] = {k: v | dict(p_holm=a) for (k, v), a in zip(prim, adj)}
    res["cross_model"] = cross_model(rows, B)
    return res


def cross_model(rows, B: int) -> dict:
    """Per family: advantage of the 3.8 direction over the 3.5 direction at +0.3 (difference of DiDs) in each target,
    and its difference across targets. Both models share the same scenarios, which are resampled jointly (paired)."""
    out = {}
    for fam in FAMILIES:
        c5, s5, A5 = arrays(rows, fam, "Qwen 3.5")
        c8, s8, A8 = arrays(rows, fam, "Qwen 3.8")
        if A5["planned"].sum() == 0 or A8["planned"].sum() == 0:
            continue
        assert s5 == s8
        a5 = lambda x, v: did(x, v, c5, "xfer_+0.3") - did(x, v, c5, "native_+0.3")   # noqa: E731 (3.8 dir in 3.5)
        a8 = lambda x, v: did(x, v, c8, "native_+0.3") - did(x, v, c8, "xfer_+0.3")   # noqa: E731 (3.8 dir in 3.8)
        rng = np.random.default_rng(7)
        idx = rng.integers(0, len(s5), size=(B, len(s5)))
        v5 = np.array([a5(A5["override"][i], A5["valid"][i]) for i in idx])
        v8 = np.array([a8(A8["override"][i], A8["valid"][i]) for i in idx])
        e5, e8 = a5(A5["override"], A5["valid"]), a8(A8["override"], A8["valid"])
        for name, est, vals in (("adv_3.8dir_in_3.5", e5, v5), ("adv_3.8dir_in_3.8", e8, v8),
                                ("adv_in_3.8 minus adv_in_3.5", e8 - e5, v8 - v5)):
            lo, hi = np.percentile(vals, [2.5, 97.5])
            out[f"{fam}: {name}"] = dict(est=float(est), lo=float(lo), hi=float(hi), p=float(min(1.0, max(
                2 * min((vals <= 0).mean(), (vals >= 0).mean()), 1.0 / B))))
    return out


def bridge(rows, B: int) -> dict:
    """Unsteered self-hosted override rates vs the archived OpenRouter presentation-ablation arm-B runs on the SAME
    prompts (conflict = archived p050, tied), per family x model; scenario-cluster bootstrap of the difference.
    Archived outcomes are pa_score's `outcome` (= adopted, the same scorer) on valid episodes."""
    from sf_common import PA, iter_jsonl
    arch = []
    for task in ("titles", "bullets"):
        for r in iter_jsonl(PA / "run/main" / task / "scored.jsonl"):
            if r.get("arm") != "B" or r.get("completion") != "valid":
                continue
            fam = "bullets" if task == "bullets" else r["block"].rsplit(":", 1)[1]
            arch.append(dict(family=fam, model=r["model"], scenario=r["block"].split(":")[1],
                             score={"p050": "conflict", "tied": "tied"}[r["score"]], override=bool(r["outcome"])))
    out = {}
    for fam in FAMILIES:
        for model in MODELS:
            for arm in ("conflict", "tied"):
                a = [x for x in arch if (x["family"], x["model"], x["score"]) == (fam, model, arm)]
                s = [x for x in rows if (x["family"], x["model"], x["score"], x["cond"]) == (fam, model, arm, "none")
                     and x["completion"] == "valid"]
                if not a or not s:
                    continue
                sc = sorted({x["scenario"] for x in a} | {x["scenario"] for x in s})
                si = {k: i for i, k in enumerate(sc)}
                M = np.zeros((len(sc), 4))
                for x in s:
                    M[si[x["scenario"]], 0] += x["override"]; M[si[x["scenario"]], 1] += 1
                for x in a:
                    M[si[x["scenario"]], 2] += x["override"]; M[si[x["scenario"]], 3] += 1
                f = lambda X: X[:, 0].sum() / max(X[:, 1].sum(), 1) - X[:, 2].sum() / max(X[:, 3].sum(), 1)  # noqa
                rng = np.random.default_rng(11)
                vals = np.array([f(M[rng.integers(0, len(sc), len(sc))]) for _ in range(B)])
                out[f"{fam}|{model}|{arm}"] = dict(self_k=int(M[:, 0].sum()), self_n=int(M[:, 1].sum()),
                                                   api_k=int(M[:, 2].sum()), api_n=int(M[:, 3].sum()),
                                                   diff=float(f(M)), lo=float(np.percentile(vals, 2.5)),
                                                   hi=float(np.percentile(vals, 97.5)))
    return out


def fmt(e):
    return f"{e['est']:+.3f} [{e['lo']:+.3f}, {e['hi']:+.3f}] p={e['p']:.3g}"


def report(res, title) -> str:
    L = [f"# Formatting steering transfer: auto report ({title})", "",
         "## Primary contrasts (P1, P2 on Qwen 3.5; P3 on Qwen 3.8; Holm over 3 families x 3 = 9)", ""]
    for k, v in res["primary"].items():
        L.append(f"- {k}: {fmt(v)}, Holm p={v['p_holm']:.3g}; missing/non-valid bounds "
                 f"[{v['bounds']['min']:+.3f}, {v['bounds']['max']:+.3f}]")
    if res.get("cross_model"):
        L += ["", "## Cross-model (additional): 3.8-direction advantage over the 3.5 direction at +0.3", ""]
        L += [f"- {k}: {fmt(v)}" for k, v in res["cross_model"].items()]
    L += ["", "## Strength curves (DiD conflict-reversed vs unsteered)", "",
          "| family / target / direction | -0.3 | -0.1 | 0 | +0.1 | +0.3 |", "|---|---|---|---|---|---|"]
    for fam, mm in res["families"].items():
        for model, m in mm.items():
            for dn in ("xfer", "native"):
                L.append(f"| {fam} / {model} / {dn} | " + " | ".join(
                    "+0.000" if s == "0" else f"{m['effects'][f'{dn}_{s}']['did_conf_rev']['est']:+.3f}"
                    for s in ("-0.3", "-0.1", "0", "+0.1", "+0.3")) + " |")
    if res.get("bridge"):
        L += ["", "## Bridge: unsteered self-hosted vs archived OpenRouter (arm B, same prompts)", "",
              "| family / model / arm | self-hosted k/n | API k/n | diff [95% CI] |", "|---|---|---|---|"]
        for k, v in res["bridge"].items():
            L.append(f"| {k} | {v['self_k']}/{v['self_n']} | {v['api_k']}/{v['api_n']} | "
                     f"{v['diff']:+.3f} [{v['lo']:+.3f}, {v['hi']:+.3f}] |")
    for fam, mm in res["families"].items():
        for model, m in mm.items():
            L += ["", f"## {fam} / {model}: {m['n_scenarios']} scenarios, {m['n_planned']} planned, "
                      f"{m['n_recorded']} recorded, {m['n_valid']} valid; statuses {m['status_totals']}", "",
                  f"Unsteered score effect: conflict-reversed {fmt(m['baseline']['conf_minus_rev'])}; "
                  f"conflict-tied {fmt(m['baseline']['conf_minus_tied'])}", "",
                  "Override k/valid by condition x arm (complies share; neither count; facts_ok share; non-valid count)", "",
                  "| condition | conflict | reversed | tied | nohist |", "|---|---|---|---|---|"]
            for c in conditions(model):
                row = []
                for a in ARMS:
                    x = m["cells"][f"{c}|{a}"]
                    row.append(f"{x['override']}/{x['valid']} (c {x['complies_rate']:.2f}; n {x['neither']}; "
                               f"f {x['facts_ok_rate']:.2f}; nv {x['planned'] - x['valid']})")
                L.append(f"| {c} | " + " | ".join(row) + " |")
            L += ["", "| condition | DiD conf-rev | DiD conf-tied | override shift reversed | override shift tied | "
                      "override shift nohist | violation shift reversed | facts shift | valid shift |",
                  "|---|---|---|---|---|---|---|---|---|"]
            for c, e in m["effects"].items():
                L.append(f"| {c} | " + " | ".join(fmt(e[x]) for x in (
                    "did_conf_rev", "did_conf_tied", "override_shift_reversed", "override_shift_tied",
                    "override_shift_nohist", "violation_shift_reversed", "facts_shift", "valid_shift")) + " |")
            if m["comparisons"]:
                L += ["", "Additional comparisons (difference of DiD conflict-reversed):"]
                L += [f"- {k}: {fmt(v)}" for k, v in m["comparisons"].items()]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="run", choices=["run", "run_mock"])
    ap.add_argument("--stage", default="main")
    ap.add_argument("--B", type=int, default=4000)
    a = ap.parse_args()
    base = HERE / a.root / a.stage
    d = base / "fmt"
    rows = score_rows(d / "items.jsonl", d / "episodes.jsonl", d / "blocks.json")
    with (base / "scored.jsonl").open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    res = analyse(rows, a.B)
    res["data_root"] = a.root
    if a.root == "run":
        res["bridge"] = bridge(rows, a.B)
    (base / "results.json").write_text(json.dumps(res, indent=1))
    md = report(res, f"{a.root}/{a.stage}" + (" -- MOCK DATA, NOT RESULTS" if a.root == "run_mock" else ""))
    (base / "REPORT_auto.md").write_text(md)
    print(md[:3000])


if __name__ == "__main__":
    sys.exit(main())
