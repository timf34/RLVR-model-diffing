"""CONFIRMATION analysis (implements HYPOTHESES_confirm.md exactly; called by run_confirm.py analyse).

analyse(records, out_dir, manifest, code_hashes) writes out_dir/REPORT.md and out_dir/results.json.

- Completions are classified with confirm_score.completion. Only "valid" completions enter any rate; empty,
  truncated and failed ones are counted per cell and never treated as following the user.
- Anchor vs main is decided by context ("anchor/bundle"), so records from any set (e.g. "inspect") work.
- Exact tests: Fisher on pooled valid samples (math.comb; one-sided "first > second" and two-sided).
- Two-stage cluster bootstrap: resample tasks with replacement, then within each drawn task resample each cell's
  valid samples with replacement (a binomial draw, which is equivalent for 0/1 outcomes); statistic on pooled
  rates; 4000 replicates, fixed seed, 95% percentile CI. Replicates in which a needed cell has no valid samples are
  dropped and the number used is reported.
- Directional pass = one-sided p < 0.025 AND bootstrap CI lower bound > 0 (CI excludes 0 on the predicted side).
- Partial data never crashes: cells without valid samples give n/a, and tests that need them are n/a.
"""
import hashlib
import json
import math
from collections import Counter
from math import comb
from pathlib import Path

import numpy as np

import confirm_materials as M
from confirm_score import completion, measures

HERE = Path(__file__).parent
MODELS = ("Qwen 3.5", "Qwen 3.6", "Qwen 3.8")
OLD, MID, NEW = MODELS
PAIRS = [(NEW, OLD), (MID, OLD), (NEW, MID)]  # (a, b): gap = a − b
ANCHOR = "anchor/bundle"
CONTEXTS = [f"{c}/{q}" for c in M.CONTEXTS for q in M.REQUESTS] + [ANCHOR]
NONVALID = ("empty", "truncated", "failed")
METRICS = ("adopted", "violates")
ALPHA = 0.025  # 0.05 / 2 features
PENALISED_MAX = 0.10
REPS = 4000
SEED = 20261028
nan = math.nan


# ---------------------------------------------------------------- exact tests

def _hyper(n1, n2, k):
    total = comb(n1 + n2, k)
    return {x: comb(n1, x) * comb(n2, k - x) / total for x in range(max(0, k - n2), min(k, n1) + 1)}


def fisher_greater(a, n1, b, n2):
    """One-sided exact test, H_a: rate a/n1 > rate b/n2."""
    if not n1 or not n2:
        return nan
    return min(1.0, sum(p for x, p in _hyper(n1, n2, a + b).items() if x >= a))


def fisher_two(a, n1, b, n2):
    """Two-sided exact test (sum of tables no more probable than the observed one)."""
    if not n1 or not n2:
        return nan
    pm = _hyper(n1, n2, a + b)
    p0 = pm[a]
    return min(1.0, sum(p for p in pm.values() if p <= p0 * (1 + 1e-9)))


# ---------------------------------------------------------------- data

def _prep(records):
    rows = []
    for r in records:
        reply = r.get("reply") or ""
        row = dict(r, completion=completion(reply, r.get("status", "")))
        if row["completion"] == "valid":
            row.update(measures(reply, r["feature"], r.get("facts") or [], r.get("signoff") or ""))
        rows.append(row)
    return rows


def _tasks(rows):
    present = {r["scenario"] for r in rows}
    order = [t["id"] for t in M.TASKS + [M.INSPECTION_TASK]]
    return [t for t in order if t in present] + sorted(present - set(order))


def cell(m, c, s="rewarded"):
    return (m, c, s)


def diff(a, b):
    return [(1, a), (-1, b)]


def did(a, b, c, d):
    """(a − b) − (c − d)."""
    return [(1, a), (-1, b), (-1, c), (1, d)]


class Feature:
    """Valid-sample counts per (model, context, scores) × task for one feature, plus bootstrap replicates."""

    def __init__(self, rows, feature, tasks, models, draws, rng):
        self.feature, self.tasks, self.models = feature, tasks, models
        self.cells = [(m, c, s) for m in models for c in CONTEXTS for s in M.SCORES]
        self.idx = {x: i for i, x in enumerate(self.cells)}
        shape = (len(self.cells), len(tasks))
        self.N = np.zeros(shape, int)
        self.K = {m: np.zeros(shape, int) for m in METRICS}
        self.U = {k: np.zeros(shape, int) for k in NONVALID}
        tix = {t: j for j, t in enumerate(tasks)}
        for r in rows:
            key = (r["model"], r["context"], r["scores"])
            if r["feature"] != feature or key not in self.idx:
                continue
            i, j = self.idx[key], tix[r["scenario"]]
            if r["completion"] == "valid":
                self.N[i, j] += 1
                for m in METRICS:
                    self.K[m][i, j] += bool(r[m])
            else:
                self.U[r["completion"]][i, j] += 1
        self.boot = {m: self._boot(self.K[m], draws, rng) for m in METRICS}

    def _boot(self, K, draws, rng):
        if draws is None:
            return None
        P = np.divide(K, self.N, out=np.zeros(K.shape), where=self.N > 0)
        Nd = self.N[:, draws]  # (cells, reps, tasks): stage 1, tasks drawn with replacement
        Ks = rng.binomial(Nd, P[:, draws])  # stage 2: each drawn task's samples resampled independently
        tot = Nd.sum(-1)
        return np.where(tot > 0, Ks.sum(-1) / np.maximum(tot, 1), nan)

    def kn(self, x, metric="adopted", task=None):
        i = self.idx.get(x)
        if i is None:
            return 0, 0
        K = self.K[metric][i]
        if task is None:
            return int(K.sum()), int(self.N[i].sum())
        return int(K[task]), int(self.N[i, task])

    def nonvalid(self, x, task=None):
        i = self.idx.get(x)
        if i is None:
            return {k: 0 for k in NONVALID}
        return {k: int(self.U[k][i].sum() if task is None else self.U[k][i, task]) for k in NONVALID}

    def rate(self, x, metric="adopted", task=None):
        k, n = self.kn(x, metric, task)
        return k / n if n else nan

    def evaluate(self, terms, metric="adopted", exact=None):
        """Point estimate, bootstrap CI, per-task signs; exact = (A, B) two cells for Fisher (A vs B)."""
        point = sum(c * self.rate(x, metric) for c, x in terms)
        ci, used = [nan, nan], 0
        R = self.boot[metric]
        if R is not None:
            vals = sum(c * R[self.idx[x]] for c, x in terms if x in self.idx)
            if all(x in self.idx for _, x in terms):
                vals = vals[~np.isnan(vals)]
                used = int(vals.size)
                if used:
                    ci = [float(np.quantile(vals, 0.025)), float(np.quantile(vals, 0.975))]
        signs = Counter()
        for t in range(len(self.tasks)):
            v = sum(c * self.rate(x, metric, t) for c, x in terms)
            signs["n/a" if math.isnan(v) else "positive" if v > 1e-12 else "negative" if v < -1e-12 else "zero"] += 1
        out = dict(terms=[[c, list(x)] for c, x in terms], metric=metric, estimate=point, ci=ci, boot_reps_used=used,
                   tasks={k: signs.get(k, 0) for k in ("positive", "zero", "negative", "n/a")})
        if exact:
            (a, n1), (b, n2) = self.kn(exact[0], metric), self.kn(exact[1], metric)
            ua, ub = sum(self.nonvalid(exact[0]).values()), sum(self.nonvalid(exact[1]).values())
            out.update(exact=[list(exact[0]), list(exact[1])], counts=[[a, n1], [b, n2]], nonvalid=[ua, ub],
                       p_one_sided=fisher_greater(a, n1, b, n2), p_two_sided=fisher_two(a, n1, b, n2),
                       # sensitivity: first cell's non-valid as non-adoption, second cell's as adoption
                       p_one_sided_adverse=fisher_greater(a, n1 + ua, b + ub, n2 + ub))
        return out


def directional(res):
    p, lo = res.get("p_one_sided", nan), res["ci"][0]
    if math.isnan(p) or math.isnan(lo):
        return "n/a"
    return "PASS" if p < ALPHA and lo > 0 else "FAIL"


# ---------------------------------------------------------------- formatting

def pct(x):
    return "n/a" if x is None or math.isnan(x) else f"{100 * x:.0f}%"


def pp(x):
    return "n/a" if x is None or math.isnan(x) else f"{100 * x:+.0f} pp"


def pf(p):
    return "n/a" if p is None or math.isnan(p) else (f"{p:.2g}" if p >= 1e-4 else f"{p:.1e}")


def ci_s(ci):
    return "n/a" if math.isnan(ci[0]) else f"[{pp(ci[0])}, {pp(ci[1])}]"


def signs_s(t):
    s = f"{t['positive']}/{t['zero']}/{t['negative']}"
    return s + (f" ({t['n/a']} n/a)" if t["n/a"] else "")


def short(m):
    return m.replace("Qwen ", "")


# ---------------------------------------------------------------- analysis

def _contrasts(F):
    """Every contrast for one feature: hypotheses, open questions, secondary. Returns dict of named results."""
    rq, rd, oq, od = "rl/quoted", "rl/direct", "ordinary/quoted", "ordinary/direct"
    H = {
        "H1": F.evaluate(diff(cell(NEW, rq), cell(OLD, rq)), exact=(cell(NEW, rq), cell(OLD, rq))),
        "H2": F.evaluate(did(cell(NEW, rq), cell(OLD, rq), cell(NEW, rd), cell(OLD, rd)),
                         exact=(cell(NEW, rq), cell(NEW, rd))),
        "H5": F.evaluate(diff(cell(NEW, ANCHOR), cell(OLD, ANCHOR)), exact=(cell(NEW, ANCHOR), cell(OLD, ANCHOR))),
        "S2": F.evaluate(diff(cell(NEW, rq), cell(NEW, rq, "penalised")),
                         exact=(cell(NEW, rq), cell(NEW, rq, "penalised"))),
    }
    for h in H.values():
        h["result"] = directional(h)
    pen = []
    for m in F.models:
        for c in CONTEXTS:
            k, n = F.kn(cell(m, c, "penalised"))
            pen.append(dict(model=m, context=c, k=k, n=n, rate=k / n if n else nan,
                            nonvalid=sum(F.nonvalid(cell(m, c, "penalised")).values())))
    seen = [x for x in pen if x["n"]]
    over = [x for x in seen if x["rate"] > PENALISED_MAX]
    S1 = dict(cells=pen, over=over, result="n/a" if not seen else ("FAIL" if over else "PASS"),
              cells_with_data=len(seen), cells_total=len(pen))
    S = "FAIL" if "FAIL" in (S1["result"], H["S2"]["result"]) else (
        "PASS" if (S1["result"], H["S2"]["result"]) == ("PASS", "PASS") else "n/a")

    Q = {"gaps": [], "did": [], "rl_effect": [], "quoting": [], "score": [], "secondary_violates": []}
    for a, b in PAIRS:  # Q4 / Q3 (ordinary/quoted) / H1, H5 for every pair, every context
        for c in CONTEXTS:
            Q["gaps"].append(dict(label=f"{short(a)} − {short(b)}, {c}", pair=[a, b], context=c,
                                  **F.evaluate(diff(cell(a, c), cell(b, c)), exact=(cell(a, c), cell(b, c)))))
    for a, b in PAIRS:
        for name, (c1, c2) in {"Q3: quoted, rl − ordinary": (rq, oq),
                               "Q6: direct, rl − ordinary": (rd, od),
                               "H2-type: rl, quoted − direct": (rq, rd),
                               "ordinary, quoted − direct": (oq, od)}.items():
            Q["did"].append(dict(label=f"{name} of ({short(a)} − {short(b)}) gap", pair=[a, b], contrast=name,
                                 **F.evaluate(did(cell(a, c1), cell(b, c1), cell(a, c2), cell(b, c2)))))
    for m in F.models:
        for req in M.REQUESTS:  # Q6 (direct) and its quoted counterpart
            x, y = cell(m, f"rl/{req}"), cell(m, f"ordinary/{req}")
            Q["rl_effect"].append(dict(label=f"{short(m)}, {req}: rl − ordinary", model=m, request=req,
                                       **F.evaluate(diff(x, y), exact=(x, y))))
        for ctx in M.CONTEXTS:
            x, y = cell(m, f"{ctx}/quoted"), cell(m, f"{ctx}/direct")
            Q["quoting"].append(dict(label=f"{short(m)}, {ctx}: quoted − direct", model=m, context=ctx,
                                     **F.evaluate(diff(x, y), exact=(x, y))))
        for c in CONTEXTS:
            x, y = cell(m, c), cell(m, c, "penalised")
            Q["score"].append(dict(label=f"{short(m)}, {c}: rewarded − penalised", model=m, context=c,
                                   **F.evaluate(diff(x, y), exact=(x, y))))
    for a, b in PAIRS:  # secondary measure, the core contrasts only
        for c in (rq, rd, ANCHOR):
            Q["secondary_violates"].append(dict(
                label=f"violates: {short(a)} − {short(b)}, {c}", pair=[a, b], context=c,
                **F.evaluate(diff(cell(a, c), cell(b, c)), "violates", exact=(cell(a, c), cell(b, c)))))
    return dict(H=H, S1=S1, S=S, Q=Q)


def reading(res, complete):
    r = {f: {h: res[f]["H"][h]["result"] for h in ("H1", "H2", "H5")} | {"S": res[f]["S"]} for f in res}
    t, s = r.get("title", {}), r.get("signoff", {})
    both = lambda d: d.get("H1") == "PASS" and d.get("H2") == "PASS"
    if both(t) and both(s):
        v = "H1 and H2 pass on both features: confirmed on fresh material and a new feature."
    elif both(t):
        v = "H1 and H2 pass on titles only: generalises to new material, not to a new feature. Not a full confirmation."
    elif t.get("H1") == "FAIL" and t.get("H5") == "PASS":
        v = ("H1 fails but H5 passes (titles): the effect generalises in the original bundle format, but not in the "
             "controlled design. Report which components that implicates (see the anchor vs rl/quoted rows).")
    elif t.get("H1") == "FAIL" and t.get("H5") == "FAIL":
        v = "H1 and H5 both fail (titles): the discovery did not confirm."
    else:
        v = ("No pre-registered reading applies to this pattern (titles: "
             + ", ".join(f"{h} {t.get(h, 'n/a')}" for h in ("H1", "H2", "H5")) + "; sign-off: "
             + ", ".join(f"{h} {s.get(h, 'n/a')}" for h in ("H1", "H2", "H5")) + "). Report descriptively.")
    notes = []
    if not (both(t) and both(s)) and s:
        notes.append("Sign-off: " + ", ".join(f"{h} {s.get(h)}" for h in ("H1", "H2", "H5")) + ".")
    for f in r:
        if r[f]["S"] != "PASS":
            notes.append(f"Check S is {r[f]['S']} for {f}: behaviour may not track the scorer there; read H1/H2/H5 "
                         "for that feature with caution.")
    na = any(r[f][h] == "n/a" for f in r for h in ("H1", "H2", "H5"))
    if not complete or na:
        v = "PROVISIONAL (data incomplete" + ("; some tests n/a" if na else "") + "). " + v
    return dict(verdict=v, notes=notes, results=r)


def analyse(records, out_dir, manifest=None, code_hashes=None, planned=None, sets=None, reps=REPS, seed=SEED):
    out_dir, manifest, code_hashes = Path(out_dir), manifest or {}, code_hashes or {}
    if sets is not None:
        records = [r for r in records if r.get("set") in sets]
    rows = _prep(records)
    tasks = _tasks(rows)
    models = list(MODELS) + sorted({r["model"] for r in rows} - set(MODELS))
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(tasks), size=(reps, len(tasks))) if tasks else None
    feats = {f: Feature(rows, f, tasks, models, draws, rng) for f in M.FEATURES}
    res = {f: _contrasts(F) for f, F in feats.items()}
    planned = planned if planned is not None else manifest.get("total")
    per_cell = manifest.get("samples", 0) * len(M.TASKS) if manifest.get("samples") else None
    complete = planned is not None and len(records) >= planned
    verdict = reading(res, complete)

    # ---- header
    frozen = manifest.get("code_sha256") or {}
    code_lines, analysis_changed = [], False
    for f in sorted(set(code_hashes) | set(frozen)):
        cur, old = code_hashes.get(f), frozen.get(f)
        st = ("no manifest (not frozen)" if not frozen else "matches freeze" if cur == old
              else "missing now" if cur is None
              else "NOT IN MANIFEST (added after freezing?)" if old is None else "CHANGED SINCE FREEZE")
        analysis_changed |= bool(frozen) and f == "confirm_analysis.py" and st != "matches freeze"
        code_lines.append(f"| {f} | {(cur or '—')[:12]} | {st} |")
    hyp = HERE / "HYPOTHESES_confirm.md"
    hyp_now = hashlib.sha256(hyp.read_bytes()).hexdigest() if hyp.exists() else None
    hyp_frozen = manifest.get("hypotheses_sha256")
    kinds = Counter(r["completion"] for r in rows)
    L = ["# CONFIRMATION — analysed separately from discovery", "",
         f"Label: {manifest.get('label', 'n/a (no manifest)')}. Frozen at: {manifest.get('at', 'n/a')}.", "",
         f"- Manifest sha256 (prompts + serving): `{manifest.get('sha256', 'n/a')}`",
         f"- hypotheses_sha256 (frozen): `{hyp_frozen or 'n/a'}`; current HYPOTHESES_confirm.md "
         + ("matches" if hyp_now and hyp_now == hyp_frozen else f"**DIFFERS or unverifiable** (`{hyp_now}`)"),
         f"- Conversations present: **{len(records)} of {planned if planned is not None else 'unknown'} planned**"
         + ("" if complete else " — PARTIAL DATA, all results provisional")
         + f"; sets: {dict(Counter(r.get('set') for r in rows))}; tasks present: {len(tasks)} ({', '.join(tasks)}).",
         f"- Completions: {', '.join(f'{k} {kinds.get(k, 0)}' for k in ('valid',) + NONVALID)}. Only valid "
         "completions enter any rate; empty/truncated/failed never count as following the user.", "",
         "Code hashes vs manifest:", "", "| File | Current sha256 | Status |", "|---|---|---|", *code_lines, ""]
    if analysis_changed:
        L += ["**WARNING: confirm_analysis.py differs from the frozen copy — analysis code changed after freezing.**", ""]
    if any("CHANGED" in x or "NOT IN" in x for x in code_lines):
        L += ["**Some code differs from the frozen snapshot (see table).**", ""]
    notes = manifest.get("serving_notes") or {}
    L += ["Serving notes:", ""] + [f"- {k}: {v}" for k, v in notes.items()] + (["- n/a"] if not notes else []) + [""]
    L += ["Methods: exact Fisher on pooled valid samples (one-sided: first cell > second). Two-stage cluster "
          f"bootstrap: {len(tasks)} tasks resampled with replacement, then each drawn task's samples resampled within "
          f"each cell; statistic on pooled rates; {reps} reps, seed {seed}; 95% percentile CI. A directional "
          f"hypothesis passes only if one-sided p < {ALPHA} AND the CI lower bound > 0. 'Tasks +/0/−' counts tasks "
          "whose per-task estimate is positive / zero / negative.", ""]

    # ---- PASS/FAIL
    L += ["## Directional hypotheses: PASS / FAIL", "",
          "| Hyp | Feature | Exact test (k/n vs k/n) | Estimate | p one-sided | p two-sided | Bootstrap 95% CI "
          "| Tasks +/0/− | Result |", "|---|---|---|---|---|---|---|---|---|"]
    desc = {"H1": "3.8 − 3.5, rl/quoted", "H2": "DiD: (3.8−3.5 rl/quoted) − (3.8−3.5 rl/direct); exact: 3.8 "
            "rl/quoted vs rl/direct", "H5": "3.8 − 3.5, anchor", "S2": "3.8 rl/quoted rewarded − penalised"}
    for h in ("H1", "H2", "H5", "S2"):
        for f in M.FEATURES:
            x = res[f]["H"][h]
            (a, n1), (b, n2) = x["counts"]
            L.append(f"| {h} | {f} | {desc[h]}: {a}/{n1} vs {b}/{n2} | {pp(x['estimate'])} | {pf(x['p_one_sided'])} | "
                     f"{pf(x['p_two_sided'])} | {ci_s(x['ci'])} | {signs_s(x['tasks'])} | **{x['result']}** |")
    for f in M.FEATURES:
        S1 = res[f]["S1"]
        worst = max((c for c in S1["cells"] if c["n"]), key=lambda c: c["rate"], default=None)
        L.append(f"| S1 | {f} | penalised adoption ≤ {PENALISED_MAX:.0%} in every model × cell "
                 f"({S1['cells_with_data']}/{S1['cells_total']} cells with data) | max "
                 + (f"{pct(worst['rate'])} ({short(worst['model'])} {worst['context']}, {worst['k']}/{worst['n']})"
                    if worst else "n/a") + " | | | | | **" + S1["result"] + "** |")
    L += ["", "| Feature | H1 | H2 | H5 | Check S (S1 and S2) |", "|---|---|---|---|---|"]
    for f in M.FEATURES:
        r = verdict["results"][f]
        L.append(f"| {f} | {r['H1']} | {r['H2']} | {r['H5']} | {r['S']} |")
    L += ["", f"**Reading:** {verdict['verdict']}", ""] + [f"- {n}" for n in verdict["notes"]] + [""]
    for f in M.FEATURES:
        over = res[f]["S1"]["over"]
        if over:
            L.append(f"S1 cells over {PENALISED_MAX:.0%} ({f}): " + "; ".join(
                f"{c['model']} {c['context']} {c['k']}/{c['n']}" for c in over) + ".")
    L += ["", "Sensitivity (not the pre-registered decision): one-sided p with the first cell's non-valid completions "
          "counted as non-adoption and the second cell's as adoption: " + "; ".join(
              f"{h} {f} {pf(res[f]['H'][h]['p_one_sided_adverse'])}" for h in ("H1", "H2", "H5", "S2")
              for f in M.FEATURES
              if sum(res[f]["H"][h]["nonvalid"])) + " (only tests with non-valid completions listed).", ""]

    # ---- completion handling
    L += ["## Completions (non-valid excluded from every rate)", "",
          "| Model | valid | empty | truncated | failed | total |", "|---|---|---|---|---|---|"]
    by_model = {m: Counter(r["completion"] for r in rows if r["model"] == m) for m in models}
    for m, c in by_model.items():
        L.append(f"| {m} | {c['valid']} | {c['empty']} | {c['truncated']} | {c['failed']} | {sum(c.values())} |")
    L += ["", "Cells with any non-valid completion (model × feature × context × scores; empty/truncated/failed; for "
          "rewarded cells, bounds counting non-valid as non-adoption … adoption):", ""]
    comp_cells, bounds, any_bad = [], [], False
    for f, F in feats.items():
        for x in F.cells:
            nv = F.nonvalid(x)
            k, n = F.kn(x)
            comp_cells.append(dict(feature=f, model=x[0], context=x[1], scores=x[2], valid=n, **nv))
            u = sum(nv.values())
            if not u:
                continue
            any_bad = True
            line = f"- {f} | {x[0]} | {x[1]} | {x[2]}: {nv['empty']}/{nv['truncated']}/{nv['failed']}; valid {k}/{n}"
            if x[2] == "rewarded":
                lo, hi = k / (n + u), (k + u) / (n + u)
                bounds.append(dict(feature=f, cell=list(x), valid=[k, n], nonvalid=u, lower=lo, upper=hi))
                line += f" ({pct(k / n if n else nan)}); bounds {k}/{n + u} ({pct(lo)}) … {k + u}/{n + u} ({pct(hi)})"
            L.append(line)
    if not any_bad:
        L.append("- none")
    L.append("")

    # ---- per feature tables
    for f, F in feats.items():
        R = res[f]
        L += [f"## Feature: {f}", "", "### Cells: adopted k/n, violates k/n (n = valid); non-valid e/t/f", "",
              "| Model | Context | Rewarded adopted | Rewarded violates | R non-valid | Penalised adopted | "
              "Penalised violates | P non-valid |", "|---|---|---|---|---|---|---|---|"]
        for m in F.models:
            for c in CONTEXTS:
                parts = []
                for s in M.SCORES:
                    x = cell(m, c, s)
                    (k, n), (v, _) = F.kn(x), F.kn(x, "violates")
                    nv = F.nonvalid(x)
                    parts += [f"{k}/{n} ({pct(k / n if n else nan)})", f"{v}/{n}",
                              f"{nv['empty']}/{nv['truncated']}/{nv['failed']}"]
                L.append(f"| {m} | {c} | " + " | ".join(parts) + " |")
        L += ["", "### Per-task adopted k/n, rewarded", "",
              "| Model | Context | " + " | ".join(F.tasks) + " |", "|---|---|" + "---|" * len(F.tasks)]
        for m in F.models:
            for c in CONTEXTS:
                L.append(f"| {m} | {c} | " + " | ".join("{}/{}".format(*F.kn(cell(m, c), task=t))
                                                        for t in range(len(F.tasks))) + " |")

        def table(title, items, exact=True):
            out = ["", f"### {title}", "", "| Contrast | Estimate | 95% CI | " + ("p two-sided | " if exact else "")
                   + "Tasks +/0/− |", "|---|---|---|" + ("---|" if exact else "") + "---|"]
            for x in items:
                out.append(f"| {x['label']} | {pp(x['estimate'])} | {ci_s(x['ci'])} | "
                           + (f"{pf(x['p_two_sided'])} | " if exact else "") + f"{signs_s(x['tasks'])} |")
            return out

        L += table("Q4 / Q3: model gaps (rewarded), every pair × every context (two-sided; includes Q3 'gap already "
                   "in ordinary/quoted')", R["Q"]["gaps"])
        L += table("Q3 / Q4 / Q6: differences-in-differences of model gaps (bootstrap only)", R["Q"]["did"], False)
        L += table("Q6: each model's rl − ordinary effect (rewarded), direct and quoted", R["Q"]["rl_effect"])
        L += table("Quoting effect (quoted − direct, rewarded) per model per context", R["Q"]["quoting"])
        L += table("Score sensitivity (rewarded − penalised) per model per cell", R["Q"]["score"])
        L += table("Secondary: violates gaps (rewarded)", R["Q"]["secondary_violates"])
        L.append("")

    # ---- secondary
    L += ["## Secondary measures (valid completions)", "",
          "| Model | Feature | within_limit (<80 words) | facts_ok | mean words |", "|---|---|---|---|---|"]
    secondary = {}
    for m in models:
        for f in M.FEATURES:
            v = [r for r in rows if r["model"] == m and r["feature"] == f and r["completion"] == "valid"]
            n = len(v)
            wl, fo = sum(r["within_limit"] for r in v), sum(r["facts_ok"] for r in v)
            mw = sum(r["words"] for r in v) / n if n else nan
            secondary[f"{m}|{f}"] = dict(n=n, within_limit=wl, facts_ok=fo, mean_words=mw)
            L.append(f"| {m} | {f} | {wl}/{n} | {fo}/{n} | {'n/a' if math.isnan(mw) else f'{mw:.0f}'} |")
    L += ["", "| Model | mean reasoning tokens (all) | (valid) | (non-valid) | max | stop reasons (last attempt) |",
          "|---|---|---|---|---|---|"]
    tokens = {}
    for m in models:
        mine = [r for r in rows if r["model"] == m]
        last = [(r, (r.get("private") or [{}])[-1] or {}) for r in mine]
        rt = lambda sel: [p.get("reasoning_tokens") for r, p in last if sel(r)
                          and isinstance(p.get("reasoning_tokens"), (int, float))]
        mean = lambda xs: sum(xs) / len(xs) if xs else nan
        a, v, nv = rt(lambda r: True), rt(lambda r: r["completion"] == "valid"), rt(lambda r: r["completion"] != "valid")
        stops = Counter(str(p.get("stop_reason")) for _, p in last)
        tokens[m] = dict(mean_all=mean(a), mean_valid=mean(v), mean_nonvalid=mean(nv), max=max(a) if a else None,
                         n=len(a), stop_reasons=dict(stops))
        f0 = lambda x: "n/a" if math.isnan(x) else f"{x:.0f}"
        L.append(f"| {m} | {f0(mean(a))} (n={len(a)}) | {f0(mean(v))} | {f0(mean(nv))} | {max(a) if a else 'n/a'} | "
                 + ", ".join(f"{k}: {c}" for k, c in stops.most_common()) + " |")

    results = dict(label="CONFIRMATION — analysed separately from discovery", manifest_sha256=manifest.get("sha256"),
                   hypotheses_sha256=hyp_frozen, hypotheses_sha256_current=hyp_now, code=code_lines,
                   analysis_code_changed=analysis_changed, present=len(records), planned=planned,
                   planned_per_cell=per_cell, complete=complete, tasks=tasks, completions=dict(kinds),
                   completion_by_model={m: dict(c) for m, c in by_model.items()}, completion_cells=comp_cells,
                   nonvalid_bounds_rewarded=bounds, reading=verdict, bootstrap=dict(reps=reps, seed=seed),
                   features={f: dict(
                       cells=[dict(model=x[0], context=x[1], scores=x[2],
                                   adopted=F.kn(x), violates=F.kn(x, "violates"), nonvalid=F.nonvalid(x),
                                   per_task={t: F.kn(x, task=j) for j, t in enumerate(F.tasks)}) for x in F.cells],
                       **res[f]) for f, F in feats.items()},
                   secondary=secondary, reasoning=tokens)
    out_dir.mkdir(parents=True, exist_ok=True)
    clean = lambda o: None if isinstance(o, float) and math.isnan(o) else o
    (out_dir / "results.json").write_text(json.dumps(_walk(results, clean), indent=1, default=str))
    (out_dir / "REPORT.md").write_text("\n".join(L) + "\n")
    print(f"Wrote {out_dir / 'REPORT.md'}")
    return results


def _walk(o, fn):
    if isinstance(o, dict):
        return {str(k): _walk(v, fn) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_walk(v, fn) for v in o]
    if isinstance(o, np.generic):
        o = o.item()
    return fn(o)
