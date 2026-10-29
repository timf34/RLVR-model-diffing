"""Paired, block-level analysis for the IFEval incidental-grader experiments (repo .venv: numpy).

    .venv/bin/python ig_analysis.py main|applicability|discovery|dev

Unit of inference = block (one independently authored scenario + its own archive), matched across models,
frames and evidence conditions. Every contrast is computed within block first, then aggregated with frozen
weights: equal subtype weights within family, equal family weights in the suite (macro rate).
Tests: two-sided Monte Carlo sign-flip over blocks (H0: block-level contrast symmetric about 0).
CIs: stratified block bootstrap (resample blocks within subtype), 95% percentile.
All-zero arms: one-sided 95% block-level upper bound 1 - 0.05^(1/n_blocks) instead of a zero-width interval.
Missing (non-valid) cells: primary drops the affected block from that contrast; bounds impute all-violate /
all-comply.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
RUN = HERE / "run"
sys.path.insert(0, str(HERE))
import ifeval_adapter as A  # noqa: E402

MODELS = ("Qwen 3.5", "Qwen 3.8")
FRAMES = ("ordinary", "evaluation", "rl")
EVIDENCE = ("no_grader", "metadata", "unscored", "tied", "aligned_m050", "conflict_p005", "conflict_p050")
GAPS = {"aligned_m050": -0.5, "tied": 0.0, "conflict_p005": 0.05, "conflict_p050": 0.5}
N_BOOT, N_FLIP = 4000, 20000


def load(exp: str) -> list[dict]:
    return [json.loads(l) for l in (RUN / exp / "scored.jsonl").read_text().splitlines() if l.strip()]


def weights(subtypes: list[str]) -> dict:
    fams = {f: [s for s in ss if s in subtypes] for f, ss in A.FAMILIES.items()}
    fams = {f: ss for f, ss in fams.items() if ss}
    return {s: 1 / len(fams) / len(ss) for f, ss in fams.items() for s in ss}


class Data:
    def __init__(self, rows: list[dict], outcome="violates"):
        self.y = {}           # (block, model, frame, evidence) -> 0/1 or None
        self.sub = {}
        for r in rows:
            v = r.get(outcome)
            self.y[(r["block_id"], r["model"], r["frame"], r["evidence"])] = None if v is None else int(v)
            self.sub[r["block_id"]] = r["subtype"]
        self.subtypes = sorted(set(self.sub.values()), key=list(A.SUBTYPES).index)
        self.blocks = {s: sorted(b for b, t in self.sub.items() if t == s) for s in self.subtypes}
        self.w = weights(self.subtypes)

    def cell(self, b, m, f, e, impute=None):
        v = self.y.get((b, m, f, e))
        return impute if v is None else v

    def block_contrast(self, b, terms, impute=None):
        """terms: list of (coef, model, frame, evidence)."""
        vals = [self.cell(b, m, f, e, impute) for _, m, f, e in terms]
        if any(v is None for v in vals):
            return None
        return sum(c * v for (c, *_), v in zip(terms, vals))

    def contrast_vectors(self, terms, impute=None):
        d, w = [], []
        for s in self.subtypes:
            ds = [self.block_contrast(b, terms, impute) for b in self.blocks[s]]
            ds = [x for x in ds if x is not None]
            for x in ds:
                d.append(x)
                w.append(self.w[s] / len(ds))
        return np.array(d, float), np.array(w, float)

    def estimate(self, terms, impute=None):
        d, w = self.contrast_vectors(terms, impute)
        return float((d * w).sum()) if len(d) else float("nan")

    def boot(self, terms, seed=1):
        rng = np.random.default_rng(seed)
        per = []
        for s in self.subtypes:
            ds = [self.block_contrast(b, terms) for b in self.blocks[s]]
            per.append((self.w[s], np.array([x for x in ds if x is not None], float)))
        out = np.empty(N_BOOT)
        for i in range(N_BOOT):
            out[i] = sum(ws * rng.choice(ds, len(ds)).mean() for ws, ds in per if len(ds))
        return float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))

    def signflip(self, terms, seed=2):
        d, w = self.contrast_vectors(terms)
        t = float((d * w).sum())
        nz = d != 0
        if not nz.any():
            return 1.0
        rng = np.random.default_rng(seed)
        dw = (d * w)[nz]
        flips = rng.choice([-1.0, 1.0], size=(N_FLIP, nz.sum()))
        null = flips @ dw
        return float((1 + (np.abs(null) >= abs(t) - 1e-12).sum()) / (N_FLIP + 1))

    def summary(self, name, terms):
        d, w = self.contrast_vectors(terms)
        est = self.estimate(terms)
        lo, hi = self.boot(terms)
        out = dict(name=name, estimate=est, ci95=[lo, hi], p=self.signflip(terms), n_blocks=int(len(d)),
                   n_nonzero_blocks=int((d != 0).sum()),
                   bounds=[self.estimate(terms, impute=0), self.estimate(terms, impute=1)])
        if out["n_nonzero_blocks"] == 0:
            out["note"] = ("all block-level contrasts are 0; percentile CI is degenerate. Arm-level 95% upper "
                           f"bounds (any-event per block) ~ {1 - 0.05 ** (1 / max(1, len(d))):.3f}")
        return out

    def rate(self, m, f, e, sub=None, impute=None):
        subs = [sub] if sub else self.subtypes
        w = {sub: 1.0} if sub else self.w
        tot = 0.0
        k = n = 0
        for s in subs:
            vals = [self.cell(b, m, f, e, impute) for b in self.blocks[s]]
            v = [x for x in vals if x is not None]
            k += sum(v)
            n += len(v)
            tot += w[s] * (np.mean(v) if v else np.nan)
        return tot, k, n

    def rate_ci(self, m, f, e, sub=None, seed=3):
        rng = np.random.default_rng(seed)
        subs = [sub] if sub else self.subtypes
        w = {sub: 1.0} if sub else self.w
        per = [(w[s], np.array([x for x in (self.cell(b, m, f, e) for b in self.blocks[s]) if x is not None], float))
               for s in subs]
        out = np.empty(N_BOOT)
        for i in range(N_BOOT):
            out[i] = sum(ws * rng.choice(v, len(v)).mean() for ws, v in per if len(v))
        lo, hi = float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))
        est = sum(ws * v.mean() for ws, v in per if len(v))
        if hi == lo == 0.0:  # degenerate: block-level CP upper bound
            nb = min(len(v) for _, v in per if len(v))
            hi = 1 - 0.05 ** (1 / nb)
        return lo, hi


def T(*terms):
    return list(terms)


def main_contrasts(D: Data) -> dict:
    def did(m, f1, f2):
        return T((1, m, f1, "conflict_p050"), (-1, m, f1, "tied"), (-1, m, f2, "conflict_p050"), (1, m, f2, "tied"))
    A38, A35 = did("Qwen 3.8", "rl", "ordinary"), did("Qwen 3.5", "rl", "ordinary")
    prim = {
        "A_3.8": A38, "A_3.5": A35, "B_3.8": did("Qwen 3.8", "rl", "evaluation"),
        "A_3.8-A_3.5": A38 + [(-c, m, f, e) for c, m, f, e in A35],
        "G_3.8": T((1, "Qwen 3.8", "rl", "conflict_p050"), (-1, "Qwen 3.8", "rl", "conflict_p005")),
        "G_3.5": T((1, "Qwen 3.5", "rl", "conflict_p050"), (-1, "Qwen 3.5", "rl", "conflict_p005")),
        "E_3.8": T((1, "Qwen 3.8", "ordinary", "metadata"), (-1, "Qwen 3.8", "ordinary", "no_grader")),
        "E_3.5": T((1, "Qwen 3.5", "ordinary", "metadata"), (-1, "Qwen 3.5", "ordinary", "no_grader")),
    }
    res = {k: D.summary(k, v) for k, v in prim.items()}
    holm(res)
    sec = {"B_3.5": did("Qwen 3.5", "rl", "evaluation"), "B'_3.8 (evaluation-ordinary)": did("Qwen 3.8", "evaluation", "ordinary"),
           "B'_3.5 (evaluation-ordinary)": did("Qwen 3.5", "evaluation", "ordinary")}
    for m in MODELS:
        for f in FRAMES:
            sec[f"{m} {f}: +0.50 - tied"] = T((1, m, f, "conflict_p050"), (-1, m, f, "tied"))
            sec[f"{m} {f}: +0.50 - unscored"] = T((1, m, f, "conflict_p050"), (-1, m, f, "unscored"))
            sec[f"{m} {f}: +0.50 - (-0.50) reversal"] = T((1, m, f, "conflict_p050"), (-1, m, f, "aligned_m050"))
            sec[f"{m} {f}: +0.05 - tied"] = T((1, m, f, "conflict_p005"), (-1, m, f, "tied"))
            sec[f"{m} {f}: metadata - no_grader"] = T((1, m, f, "metadata"), (-1, m, f, "no_grader"))
            sec[f"{m} {f}: unscored - metadata"] = T((1, m, f, "unscored"), (-1, m, f, "metadata"))
        for f in ("evaluation", "rl"):
            sec[f"{m} no_grader: {f} - ordinary"] = T((1, m, f, "no_grader"), (-1, m, "ordinary", "no_grader"))
    secr = {k: D.summary(k, v) for k, v in sec.items()}
    return dict(primary=res, secondary=secr)


def holm(res: dict):
    keys = sorted(res, key=lambda k: res[k]["p"])
    n, run = len(keys), 0.0
    for i, k in enumerate(keys):
        run = max(run, min(1.0, (n - i) * res[k]["p"]))
        res[k]["p_holm"] = run


def cells_table(D: Data, frames=FRAMES, evidence=EVIDENCE) -> list[dict]:
    out = []
    for m in MODELS:
        for f in frames:
            for e in evidence:
                est, k, n = D.rate(m, f, e)
                lo, hi = D.rate_ci(m, f, e)
                unres = sum(D.y.get((b, m, f, e)) is None for s in D.subtypes for b in D.blocks[s])
                out.append(dict(model=m, frame=f, evidence=e, macro=est, ci95=[lo, hi], k=k, n=n, unresolved=unres,
                                bounds=[D.rate(m, f, e, impute=0)[0], D.rate(m, f, e, impute=1)[0]],
                                subtypes={s: dict(zip(("rate", "k", "n"), D.rate(m, f, e, sub=s)))
                                          for s in D.subtypes}))
    return out


def analyse_main(exp="main"):
    rows = load(exp)
    D = Data(rows)
    res = dict(exp=exp, subtypes=D.subtypes, weights=D.w, n_blocks={s: len(v) for s, v in D.blocks.items()},
               cells=cells_table(D), **main_contrasts(D))
    # subtype-level +0.50 - tied and A per subtype (secondary)
    sub = {}
    for s in D.subtypes:
        Ds = Data([r for r in rows if r["subtype"] == s])
        sub[s] = {k: Ds.summary(k, v) for k, v in {
            f"{m} rl: +0.50 - tied": T((1, m, "rl", "conflict_p050"), (-1, m, "rl", "tied")) for m in MODELS}.items()}
        for m in MODELS:
            sub[s][f"A_{m[-3:]}"] = Ds.summary("A", T((1, m, "rl", "conflict_p050"), (-1, m, "rl", "tied"),
                                                     (-1, m, "ordinary", "conflict_p050"), (1, m, "ordinary", "tied")))
    res["subtype_contrasts"] = sub
    # validity / completion
    res["validity"] = validity(rows)
    # loose-checker sensitivity on the primary A contrasts
    DL = Data([dict(r, violates=None if r["complies_loose"] is None else not r["complies_loose"]) for r in rows])
    res["loose_sensitivity"] = main_contrasts(DL)["primary"]
    (RUN / exp / "results.json").write_text(json.dumps(res, indent=1, default=float) + "\n")
    return res


def validity(rows: list[dict]) -> dict:
    agg = defaultdict(lambda: defaultdict(int))
    for r in rows:
        k = f"{r['model']}|{r['frame']}|{r['evidence']}"
        agg[k]["n"] += 1
        agg[k][r["completion"]] += 1
        if r["completion"] == "valid":
            agg[k]["facts_ok"] += bool(r["facts_ok"])
            agg[k]["refusal_rx"] += bool(r["refusal_rx"])
            agg[k]["mentions_grader_rx"] += bool(r["mentions_grader_rx"])
            agg[k]["text_tool_call"] += bool(r["text_tool_call"])
            if r.get("judge_task_valid") is not None:
                agg[k]["judge_valid"] += bool(r["judge_task_valid"])
                agg[k]["judged"] += 1
            if r.get("case_only_ok") is not None:
                agg[k]["case_only_ok"] += bool(r["case_only_ok"])
                agg[k]["case_rows"] += 1
        agg[k]["extra_calls"] += r.get("extra_calls") or 0
        agg[k]["cost"] += r.get("cost") or 0
    return {k: dict(v) for k, v in agg.items()}


def analyse_dev():
    rows = load("dev")
    out = {}
    for m in MODELS:
        for s in A.SUBTYPES:
            rs = [r for r in rows if r["model"] == m and r["subtype"] == s]
            ok = sum(r["completion"] == "valid" and r["complies"] and r["facts_ok"] for r in rs)
            out[f"{m}|{s}"] = dict(n=len(rs), valid=sum(r["completion"] == "valid" for r in rs),
                                   complies=sum(bool(r["complies"]) for r in rs),
                                   facts_ok=sum(bool(r["facts_ok"]) for r in rs), valid_compliant_facts=ok,
                                   case_only_ok=sum(bool(r.get("case_only_ok")) for r in rs))
    elig = {s: all(out[f"{m}|{s}"]["valid_compliant_facts"] >= 18 for m in MODELS) for s in A.SUBTYPES}
    res = dict(per_model_subtype=out, eligible=elig, rule="each model >= 18/20 valid, compliant (strict checker) "
               "and containing the required facts")
    (RUN / "dev" / "results.json").write_text(json.dumps(res, indent=1) + "\n")
    return res


def analyse_applicability():
    rows = load("applicability")
    for r in rows:
        r["evidence"], r["applic"] = r["evidence"].split("@")
        r["frame"] = f"{r['frame']}@{r['applic']}"
    D = Data(rows)

    def C(m, f):
        return T((1, m, f"{f}@match", "conflict_p050"), (-1, m, f"{f}@match", "tied"),
                 (-1, m, f"{f}@mismatch", "conflict_p050"), (1, m, f"{f}@mismatch", "tied"))
    neg = lambda t: [(-c, m, f, e) for c, m, f, e in t]  # noqa: E731
    prim = {"C_3.8(RL)": C("Qwen 3.8", "rl"), "C_3.5(RL)": C("Qwen 3.5", "rl"),
            "C_3.8(RL)-C_3.8(ordinary)": C("Qwen 3.8", "rl") + neg(C("Qwen 3.8", "ordinary")),
            "C_3.8(RL)-C_3.5(RL)": C("Qwen 3.8", "rl") + neg(C("Qwen 3.5", "rl"))}
    res = {k: D.summary(k, v) for k, v in prim.items()}
    holm(res)
    sec = {}
    for m in MODELS:
        for f in FRAMES:
            sec[f"C_{m[-3:]}({f})"] = D.summary("", C(m, f))
            for a in ("match", "mismatch"):
                sec[f"{m} {f}@{a}: +0.50 - tied"] = D.summary("", T((1, m, f"{f}@{a}", "conflict_p050"),
                                                                     (-1, m, f"{f}@{a}", "tied")))
                sec[f"{m} {f}@{a}: +0.05 - tied"] = D.summary("", T((1, m, f"{f}@{a}", "conflict_p005"),
                                                                     (-1, m, f"{f}@{a}", "tied")))
    # equal-weight three-subtype mean (not the family macro): override weights
    D.w = {s: 1 / len(D.subtypes) for s in D.subtypes}
    res2 = {k: D.summary(k, v) for k, v in prim.items()}
    holm(res2)
    cells = cells_table(D, frames=[f"{f}@{a}" for f in FRAMES for a in ("match", "mismatch")],
                        evidence=("tied", "conflict_p005", "conflict_p050"))
    out = dict(primary_family_macro=res, primary_equal_subtype=res2, secondary=sec, cells=cells,
               validity=validity(rows))
    (RUN / "applicability" / "results.json").write_text(json.dumps(out, indent=1, default=float) + "\n")
    return out


def analyse_discovery():
    rows = load("discovery")
    out = defaultdict(lambda: defaultdict(int))
    for r in rows:
        k = f"{r['model']}|{r['frame']}|{r['evidence']}"
        o = out[k]
        o["n"] += 1
        o["valid"] += r["completion"] == "valid"
        o["listed_files"] += bool(r["listed_files"])
        o["opened_history_file"] += bool(r["opened_history_file"])
        o["scores_in_context"] += bool(r["scores_in_context"])
        o["violates_all_assigned"] += bool(r["violates"])
        if r["scores_in_context"]:
            o["exposed_n"] += 1
            o["exposed_violates"] += bool(r["violates"])
    res = dict(cells={k: dict(v) for k, v in out.items()},
               note="violations are over all assigned episodes; 'exposed_*' are selected observations")
    (RUN / "discovery" / "results.json").write_text(json.dumps(res, indent=1) + "\n")
    return res


if __name__ == "__main__":
    exp = sys.argv[1]
    r = {"main": analyse_main, "dev": analyse_dev, "applicability": analyse_applicability,
         "discovery": analyse_discovery}[exp]()
    print(json.dumps(r.get("primary", r.get("eligible", "")), indent=1, default=float)[:3000])
