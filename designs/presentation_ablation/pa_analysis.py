"""Frozen analysis for the presentation ablation (numpy only; see PROTOCOL.md "Analysis").

  python pa_analysis.py analyse [--stage main] [--root DIR]  -> <root>/<stage>/results.json, REPORT_auto.md
  python pa_analysis.py select  [--enable]                   -> <root>/factorial/selection.json (frozen rule)

Unit = block. Per block b, arm, model: y = mean outcome over valid reps (original materials have reps; fresh 1).
Score effect D(b, arm) = y(+0.50) - y(tied); a block missing a valid episode in a needed cell is dropped from that
contrast (count reported). Primary model Qwen 3.8; Qwen 3.5 gets the same tables, labelled descriptive.

Primaries (pooled over PRIMARY_TASKS = send, titles with equal task weights; Holm within each family):
  Part 1 family (2):  PRES  presentation main effect = mean_t mean_mat mean_b [D(b,B) - D(b,N)]
                      MAT   materials main effect    = mean_t [mean_orig S(b) - mean_fresh S(b)], S = (D_B + D_N)/2
  Part 2 family (13): REM:k = mean_t mean_fresh [D(b,B) - D(b,B-k)]     (k = a..g)
                      ADD:k = mean_t mean_fresh [D(b,N+k) - D(b,N)]     (k = a, b, d, e, f, g)
Tests: paired contrasts -> two-sided block sign-flip (Monte Carlo); MAT (blocks differ between materials) ->
stratified permutation of the materials label within task. 95% CIs: stratified block bootstrap (percentile).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from pa_common import GAPS, HERE, MODELS, PRIMARY_MODEL, PRIMARY_TASKS, RUN, TASKS, iter_jsonl
from pa_render import COMPONENTS, N_END, NAMES, part2_arms

N_FLIP, N_PERM, N_BOOT = 20000, 20000, 5000
REM = [f"REM:{k}" for k in COMPONENTS]
ADD = [f"ADD:{k}" for k in COMPONENTS if N_END[k] == "N"]


# ------------------------------------------------------------------------------------------- data

class Data:
    def __init__(self, rows: list[dict]):
        acc = defaultdict(list)
        self.nonvalid = Counter()
        self.mat = {}
        self.cells = defaultdict(lambda: [0, 0])
        for r in rows:
            self.mat[(r["task"], r["block"])] = r["materials"]
            ck = (r["task"], r["materials"], r["arm"], r["score"], r["model"])
            if r["completion"] == "valid":
                acc[(r["task"], r["block"], r["arm"], r["score"], r["model"])].append(int(bool(r["outcome"])))
                self.cells[ck][0] += int(bool(r["outcome"]))
                self.cells[ck][1] += 1
            else:
                self.nonvalid[ck + (r["completion"],)] += 1
        self.y = {k: float(np.mean(v)) for k, v in acc.items()}
        self.blocks = defaultdict(list)
        for (t, b), m in sorted(self.mat.items()):
            self.blocks[(t, m)].append(b)
        self.tasks = [t for t in TASKS if any(k[0] == t for k in self.blocks)]

    def D(self, t, b, arm, m):
        hi, lo = self.y.get((t, b, arm, "p050", m)), self.y.get((t, b, arm, "tied", m))
        return None if hi is None or lo is None else hi - lo


def strata_values(D: Data, strata) -> list[tuple[float, np.ndarray]]:
    """strata: [(task, materials, weight, fn(block)->value|None)] -> [(weight, values)] (empty strata dropped)."""
    out = []
    for t, mat, w, fn in strata:
        v = [fn(b) for b in D.blocks.get((t, mat), [])]
        v = np.array([x for x in v if x is not None], float)
        if len(v):
            out.append((w, v))
    tot = sum(w for w, _ in out)
    return [(w / tot, v) for w, v in out] if out and tot > 0 else []


def est(sv) -> float:
    return float(sum(w * v.mean() for w, v in sv)) if sv else float("nan")


def boot_ci(sv, rng) -> tuple[float, float]:
    if not sv:
        return (float("nan"), float("nan"))
    out = np.zeros(N_BOOT)
    for w, v in sv:
        out += w * v[rng.integers(0, len(v), (N_BOOT, len(v)))].mean(1)
    return float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))


def signflip_p(sv, rng) -> float:
    if not sv:
        return float("nan")
    obs = est(sv)
    contrib = np.concatenate([w * v / len(v) for w, v in sv])
    if not np.any(contrib != 0):
        return 1.0
    null = np.zeros(N_FLIP)
    for s in range(0, N_FLIP, 5000):
        n = min(5000, N_FLIP - s)
        null[s:s + n] = (rng.choice([-1.0, 1.0], size=(n, len(contrib))) * contrib).sum(1)
    return float((1 + (np.abs(null) >= abs(obs) - 1e-12).sum()) / (N_FLIP + 1))


def summarise(name, sv, rng, test="signflip", perm=None) -> dict:
    vals = np.concatenate([v for _, v in sv]) if sv else np.array([])
    e = est(sv)
    lo, hi = boot_ci(sv, rng) if test == "signflip" else perm["ci"]
    p = signflip_p(sv, rng) if test == "signflip" else perm["p"]
    out = dict(name=name, estimate=e, ci95=[lo, hi], p=p, test=test, n_blocks=int(len(vals)),
               n_nonzero_blocks=int((vals != 0).sum()))
    if len(vals) and not (vals != 0).any():
        out["note"] = f"all block contrasts 0 (degenerate CI); one-sided 95% bound on share of blocks affected " \
                      f"{1 - 0.05 ** (1 / len(vals)):.3f}"
    return out


def materials_test(D: Data, tasks, m, rng) -> dict:
    """MAT: per task mean_orig S - mean_fresh S, pooled with equal task weights; within-task label permutation."""
    S = lambda t: (lambda b: None if D.D(t, b, "B", m) is None or D.D(t, b, "N", m) is None  # noqa: E731
                   else (D.D(t, b, "B", m) + D.D(t, b, "N", m)) / 2)
    per = []
    for t in tasks:
        o = np.array([x for x in (S(t)(b) for b in D.blocks.get((t, "orig"), [])) if x is not None], float)
        f = np.array([x for x in (S(t)(b) for b in D.blocks.get((t, "fresh"), [])) if x is not None], float)
        if len(o) and len(f):
            per.append((o, f))
    if not per:
        return dict(estimate=float("nan"), p=float("nan"), ci=(float("nan"), float("nan")), n=0)
    stat = lambda pp: float(np.mean([o.mean() - f.mean() for o, f in pp]))  # noqa: E731

    def welch(pp):  # studentized test statistic: original blocks average several reps, fresh blocks one, so the
        tt = []     # two groups have unequal variances; a studentized permutation statistic stays calibrated
        for o, f in pp:
            se = math.sqrt(max(o.var(ddof=1) if len(o) > 1 else 0, 1e-4) / len(o)
                           + max(f.var(ddof=1) if len(f) > 1 else 0, 1e-4) / len(f))
            tt.append((o.mean() - f.mean()) / se)
        return float(np.mean(tt))
    obs = stat(per)
    tobs = welch(per)
    cnt = 0
    for _ in range(N_PERM):
        pp = []
        for o, f in per:
            allv = rng.permutation(np.concatenate([o, f]))
            pp.append((allv[:len(o)], allv[len(o):]))
        cnt += abs(welch(pp)) >= abs(tobs) - 1e-12
    bs = [stat([(o[rng.integers(0, len(o), len(o))], f[rng.integers(0, len(f), len(f))]) for o, f in per])
          for _ in range(N_BOOT)]
    return dict(estimate=obs, p=(1 + cnt) / (N_PERM + 1), ci=(float(np.percentile(bs, 2.5)),
                                                               float(np.percentile(bs, 97.5))),
                n=sum(len(o) + len(f) for o, f in per))


def holm(res: dict):
    keys = sorted(res, key=lambda k: (math.isnan(res[k]["p"]), res[k]["p"]))
    run, n = 0.0, len(keys)
    for i, k in enumerate(keys):
        p = res[k]["p"]
        run = max(run, min(1.0, (n - i) * p)) if not math.isnan(p) else run
        res[k]["p_holm"] = run if not math.isnan(p) else float("nan")
    return res


# ------------------------------------------------------------------------------------------- contrasts

def part1_strata(D, tasks, m):
    fn = lambda t: (lambda b: None if D.D(t, b, "B", m) is None or D.D(t, b, "N", m) is None  # noqa: E731
                    else D.D(t, b, "B", m) - D.D(t, b, "N", m))
    return [(t, mat, 1.0, fn(t)) for t in tasks for mat in ("orig", "fresh")]


def comp_strata(D, tasks, m, name):
    kind, k = name.split(":")
    if kind == "REM":
        a1, a2 = "B", f"B-{k}"
    else:
        a1, a2 = f"N+{k}", "N"
    fn = lambda t: (lambda b: None if D.D(t, b, a1, m) is None or D.D(t, b, a2, m) is None  # noqa: E731
                    else D.D(t, b, a1, m) - D.D(t, b, a2, m))
    return [(t, "fresh", 1.0, fn(t)) for t in tasks]


def cell_effect_strata(D, t, mat, arm, m):
    return [(t, mat, 1.0, lambda b: D.D(t, b, arm, m))]


def contrasts(D: Data, tasks, m, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    p1 = {"PRES": summarise("PRES", strata_values(D, part1_strata(D, tasks, m)), rng)}
    mt = materials_test(D, tasks, m, rng)
    p1["MAT"] = dict(name="MAT", estimate=mt["estimate"], ci95=list(mt["ci"]), p=mt["p"], test="permutation",
                     n_blocks=mt["n"])
    p2 = {n: summarise(n, strata_values(D, comp_strata(D, tasks, m, n)), rng) for n in REM + ADD}
    return dict(part1=p1, part2=p2)


def secondary(D: Data, m, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    out = {}
    for t in D.tasks:
        s = {}
        for mat in ("orig", "fresh"):
            for arm in ["B", "N"] + (list(part2_arms()) if mat == "fresh" else []):
                sv = strata_values(D, cell_effect_strata(D, t, mat, arm, m))
                if sv:
                    s[f"score effect {mat} {arm}"] = summarise(f"{t} {mat} {arm}", sv, rng)
        # interaction: (B - N) on original minus on fresh blocks (different blocks: bootstrap only, descriptive)
        o = strata_values(D, [part1_strata(D, [t], m)[0]])
        f = strata_values(D, [part1_strata(D, [t], m)[1]])
        if o and f:
            diff = o[0][1].mean() - f[0][1].mean()
            bs = [o[0][1][rng.integers(0, len(o[0][1]), len(o[0][1]))].mean()
                  - f[0][1][rng.integers(0, len(f[0][1]), len(f[0][1]))].mean() for _ in range(N_BOOT)]
            s["interaction (B-N) orig - fresh"] = dict(estimate=float(diff), ci95=[float(np.percentile(bs, 2.5)),
                                                                                  float(np.percentile(bs, 97.5))],
                                                       test="bootstrap only (descriptive)")
        tc = contrasts(D, [t], m, seed + 1)
        s |= {f"{k} (task)": v for k, v in tc["part1"].items()}
        fam = {f"{k} (task)": v for k, v in tc["part2"].items()}
        holm(fam)
        s |= fam
        out[t] = s
    return out


def cell_table(D: Data) -> list[dict]:
    rows = []
    for (t, mat, arm, sc, m), (k, n) in sorted(D.cells.items()):
        lo, hi = wilson(k, n)
        nv = {c: v for (t2, mat2, a2, s2, m2, c), v in D.nonvalid.items()
              if (t2, mat2, a2, s2, m2) == (t, mat, arm, sc, m)}
        rows.append(dict(task=t, materials=mat, arm=arm, score=sc, model=m, k=k, n=n, rate=k / n if n else None,
                         lo=lo, hi=hi, nonvalid=nv))
    return rows


def wilson(k, n, z=1.959964):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def analyse_rows(rows: list[dict], seed: int = 11) -> dict:
    D = Data(rows)
    prim = contrasts(D, [t for t in PRIMARY_TASKS if t in D.tasks], PRIMARY_MODEL, seed)
    holm(prim["part1"])
    holm(prim["part2"])
    res = dict(primary_model=PRIMARY_MODEL, primary_tasks=[t for t in PRIMARY_TASKS if t in D.tasks],
               primary=prim, cells=cell_table(D),
               secondary={PRIMARY_MODEL: secondary(D, PRIMARY_MODEL, seed + 10)},
               all_tasks_pooled={})
    allt = contrasts(D, D.tasks, PRIMARY_MODEL, seed + 20)
    holm(allt["part1"])
    holm(allt["part2"])
    res["all_tasks_pooled"][PRIMARY_MODEL] = allt
    for m in MODELS:
        if m == PRIMARY_MODEL:
            continue
        res.setdefault("descriptive", {})[m] = dict(
            pooled_primary_tasks=contrasts(D, res["primary_tasks"], m, seed + 30),
            per_task=secondary(D, m, seed + 40))
    # additivity (descriptive): sum of removal effects vs total B - N on fresh blocks, per task
    add = {}
    for t in D.tasks:
        tot = est(strata_values(D, [(t, "fresh", 1.0, part1_strata(D, [t], PRIMARY_MODEL)[1][3])]))
        rems = {k: est(strata_values(D, comp_strata(D, [t], PRIMARY_MODEL, f"REM:{k}"))) for k in COMPONENTS}
        add[t] = dict(total_B_minus_N=tot, removal_effects=rems, sum_removal=float(np.nansum(list(rems.values()))))
    res["additivity"] = add
    return res


def load_rows(stage: str, root: Path) -> list[dict]:
    rows = []
    for t in TASKS:
        rows += list(iter_jsonl(root / stage / t / "scored.jsonl"))
    return rows


def fmt_e(r: dict) -> str:
    e, (lo, hi) = r["estimate"], r["ci95"]
    s = f"{e:+.3f} [{lo:+.3f}, {hi:+.3f}]" if not math.isnan(e) else "n/a"
    return s


def report(res: dict, rows: list[dict]) -> str:
    L = ["# Presentation ablation: auto tables (frozen analysis)", "",
         f"Primary model {res['primary_model']}; pooled primaries over {', '.join(res['primary_tasks'])} "
         "(equal task weights). Estimates are differences in P(user-conflicting behaviour); [95% block bootstrap].",
         "", "## Part 1 primaries (Holm over 2)", "", "| contrast | estimate [95% CI] | p | Holm p | blocks |",
         "|---|---|---|---|---|"]
    for k, r in res["primary"]["part1"].items():
        L.append(f"| {k} | {fmt_e(r)} | {r['p']:.4f} | {r['p_holm']:.4f} | {r['n_blocks']} |")
    L += ["", "## Part 2 primaries: component effects on fresh blocks (Holm over 13)", "",
          "| contrast | component | estimate [95% CI] | p | Holm p | blocks | non-zero |", "|---|---|---|---|---|---|---|"]
    for k, r in res["primary"]["part2"].items():
        L.append(f"| {k} | {NAMES[k.split(':')[1]]} | {fmt_e(r)} | {r['p']:.4f} | {r['p_holm']:.4f} | "
                 f"{r['n_blocks']} | {r['n_nonzero_blocks']} |")
    L += ["", "REM:k = D(B) - D(B-k) (> 0: removing k from the bundle lowers the score effect). "
          "ADD:k = D(N+k) - D(N) (> 0: adding k to the new presentation raises it).", "",
          "## Cell rates (k/n valid, Wilson 95%)", "", "| task | materials | arm | score | model | k/n | rate | 95% | "
          "non-valid |", "|---|---|---|---|---|---|---|---|---|"]
    for c in res["cells"]:
        if c["arm"] in ("B", "N") or c["model"] == PRIMARY_MODEL:
            L.append(f"| {c['task']} | {c['materials']} | {c['arm']} | {c['score']} | {c['model']} | {c['k']}/{c['n']} "
                     f"| {c['rate']:.2f} | {c['lo']:.2f}-{c['hi']:.2f} | {c['nonvalid'] or ''} |")
    L += ["", "## Per task (Qwen 3.8; secondary; Part 2 Holm within task)", ""]
    for t, s in res["secondary"][PRIMARY_MODEL].items():
        L += [f"### {t}", "", "| contrast | estimate [95% CI] | p | Holm p (task) |", "|---|---|---|---|"]
        for k, r in s.items():
            p = f"{r['p']:.4f}" if "p" in r else ""
            ph = f"{r['p_holm']:.4f}" if "p_holm" in r else ""
            L.append(f"| {k} | {fmt_e(r)} | {p} | {ph} |")
        L.append("")
    L += ["## All three tasks pooled (secondary)", "", "| contrast | estimate [95% CI] | p | Holm p |", "|---|---|---|---|"]
    for fam in ("part1", "part2"):
        for k, r in res["all_tasks_pooled"][PRIMARY_MODEL][fam].items():
            L.append(f"| {k} | {fmt_e(r)} | {r['p']:.4f} | {r['p_holm']:.4f} |")
    for m, d in (res.get("descriptive") or {}).items():
        L += ["", f"## {m} (descriptive; no multiplicity correction)", "", "| contrast | estimate [95% CI] | p |",
              "|---|---|---|"]
        for fam in ("part1", "part2"):
            for k, r in d["pooled_primary_tasks"][fam].items():
                L.append(f"| {k} | {fmt_e(r)} | {r['p']:.4f} |")
    L += ["", "## Additivity (descriptive, Qwen 3.8, fresh blocks)", "", "| task | D(B)-D(N) | sum of REM:k |",
          "|---|---|---|"]
    for t, a in res["additivity"].items():
        L.append(f"| {t} | {a['total_B_minus_N']:+.3f} | {a['sum_removal']:+.3f} |")
    dg = Counter()
    for r in rows:
        if r["completion"] == "valid":
            dg[(r["task"], "text_form_tool_call")] += int(bool(r.get("text_form_tool_call")))
            dg[(r["task"], "extra_calls")] += int(bool(r.get("extra_calls")))
    L += ["", f"Diagnostics: {dict((f'{a}|{b}', v) for (a, b), v in dg.items())}",
          f"Total cost (scored rows): ${sum(r.get('cost') or 0 for r in rows):.3f}", ""]
    return "\n".join(L)


# ------------------------------------------------------------------------------------------- factorial selection

def select(res: dict, max_k: int = 3) -> dict:
    """Frozen rule (PROTOCOL.md): components with pooled Holm p < 0.05 for REM or ADD, ranked by
    max(REM, ADD) estimate, top max_k; if fewer than 2 qualify, fill up to 2 by REM estimate (flagged)."""
    p2 = res["primary"]["part2"]
    score, sig = {}, set()
    for k in COMPONENTS:
        es = [p2[n]["estimate"] for n in (f"REM:{k}", f"ADD:{k}") if n in p2 and not math.isnan(p2[n]["estimate"])]
        score[k] = max(es) if es else float("-inf")
        if any(p2[n]["p_holm"] < 0.05 for n in (f"REM:{k}", f"ADD:{k}") if n in p2):
            sig.add(k)
    chosen = sorted(sig, key=lambda k: -score[k])[:max_k]
    filled = []
    if len(chosen) < 2:
        rest = sorted((k for k in COMPONENTS if k not in chosen),
                      key=lambda k: -p2[f"REM:{k}"]["estimate"] if not math.isnan(p2[f"REM:{k}"]["estimate"]) else 9)
        filled = rest[: 2 - len(chosen)]
        chosen += filled
    return dict(components=sorted(chosen, key=COMPONENTS.index), significant=sorted(sig), filled_exploratory=filled,
                others="B", rule="PROTOCOL.md Stage 3", enabled=False)


def main():
    sys.path.insert(0, str(HERE))
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["analyse", "select"])
    ap.add_argument("--stage", default="main")
    ap.add_argument("--root", default=str(RUN))
    ap.add_argument("--enable", action="store_true", help="select: mark the factorial stage enabled")
    a = ap.parse_args()
    root = Path(a.root)
    if a.cmd == "analyse":
        rows = load_rows(a.stage, root)
        res = analyse_rows(rows)
        (root / a.stage / "results.json").write_text(json.dumps(res, indent=1, default=float))
        md = report(res, rows)
        (root / a.stage / "REPORT_auto.md").write_text(md)
        for k, r in list(res["primary"]["part1"].items()) + list(res["primary"]["part2"].items()):
            print(f"{k:7s} {fmt_e(r):32s} Holm p {r['p_holm']:.4f}")
    else:
        res = json.loads((root / "main" / "results.json").read_text())
        sel = select(res)
        sel["enabled"] = bool(a.enable)
        (root / "factorial").mkdir(parents=True, exist_ok=True)
        (root / "factorial" / "selection.json").write_text(json.dumps(sel, indent=1))
        print(json.dumps(sel))


if __name__ == "__main__":
    main()
