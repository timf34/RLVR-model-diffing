"""Analysis of the request-wording experiment (plan: HYPOTHESES.md; discovery-labelled throughout).

  .venv/bin/python designs/wording/run.py analyse main|inspection     # real runs (records joined by run.py)
  .venv/bin/python designs/wording/analysis.py selftest <scratch dir>  # synthetic records: an effect and a null

Outcome: `adopted` = any em dash in a VALID completion (rl_context score.completion: empty, truncated and
failed completions are never counted as compliance; they are excluded and reported per cell). Secondary:
`violates` = any dash used as punctuation (emdash_score.measures), reported in the cell table.

Cells are (model, presentation, wording, scores, task). A contrast arm may pool several cells (e.g. W3+W4); its
per-task rate is pooled over those cells. Every estimate is the equal-weight mean over tasks (strata) of the
per-task rate difference, over tasks where both arms have valid completions.

Statistics:
- single within-model differences (exception, phrasing, priority, quoting, score sensitivity): task-stratified
  exact conditional test (convolution of per-task hypergeometrics; two-sided, Fisher-style);
- differences of differences (the interaction within a model) and every model difference (3.8-3.5, 3.6-3.5,
  3.8-3.6, of adoption and of each contrast): task-stratified permutation test, redrawing each component
  difference's arm labels within task (hypergeometric given the task's margins), 10,000 draws, fixed seed;
- task sign counts: per task, the sign of the contrast, out of the tasks where it is defined (6 in the main run).
Scope: p-values treat the samples in a cell as independent draws for these 6 tasks and these prompts. They are
conditional on the 6 tasks and make no claim beyond them; the sign counts are the cross-task description.
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import math
import sys
import zlib
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
RL = HERE.parent / "rl_context"
if str(RL) not in sys.path:
    sys.path.insert(0, str(RL))
import emdash_score  # noqa: E402  (read-only; re-exports score.completion)

if "wording_materials" in sys.modules:
    W = sys.modules["wording_materials"]
else:
    _spec = importlib.util.spec_from_file_location("wording_materials", HERE / "materials.py")
    W = importlib.util.module_from_spec(_spec)
    sys.modules["wording_materials"] = W
    _spec.loader.exec_module(W)

SEED, N_PERM = 20261028, 10_000
MODELS = ("Qwen 3.5", "Qwen 3.6", "Qwen 3.8")
MODEL_PAIRS = (("Qwen 3.8", "Qwen 3.5"), ("Qwen 3.6", "Qwen 3.5"), ("Qwen 3.8", "Qwen 3.6"))
WORDS = tuple(W.WORDINGS)
PRES = W.PRESENTATIONS
SCOPE = ("Scope: p-values are conditional on these tasks and prompts (samples within a cell treated as "
         "independent draws); there is no claim beyond them. Task sign counts describe consistency across tasks. "
         "No multiplicity correction; everything here is discovery-labelled.")


def short(m: str) -> str:
    return m.replace("Qwen ", "")


# ---------------------------------------------------------------- outcomes

def outcome(r: dict) -> dict:
    status = emdash_score.completion(r.get("reply") or "", r.get("status", "error"))
    out = dict(completion=status, valid=status == "valid")
    if out["valid"]:
        out |= emdash_score.measures(r["reply"], W.FEATURE, r.get("facts", []))
    return out


def cell(r: dict) -> tuple:
    return (r["model"], r["presentation"], r["wording"], r["scores"], r["scenario"])


class Counts:
    def __init__(self, rows: list[dict]):
        self.k, self.n, self.v, self.all = Counter(), Counter(), Counter(), Counter()
        self.status = defaultdict(Counter)
        for r in rows:
            c, o = cell(r), r["_o"]
            self.all[c] += 1
            self.status[c][o["completion"]] += 1
            if o["valid"]:
                self.n[c] += 1
                self.k[c] += bool(o["adopted"])
                self.v[c] += bool(o["violates"])

    def get(self, cells) -> tuple[int, int]:
        return sum(self.k[c] for c in cells), sum(self.n[c] for c in cells)


# ---------------------------------------------------------------- exact test (as designs/coding_env/analysis.py)

def _hyper_pmf(n1, n0, K):
    lo, hi = max(0, K - n0), min(K, n1)
    denom = math.comb(n1 + n0, K)
    return lo, np.array([math.comb(n1, x) * math.comb(n0, K - x) / denom for x in range(lo, hi + 1)])


def exact_stratified(strata) -> float | None:
    """Two-sided exact conditional test of no association, stratified. strata: (k1, n1, k0, n0)."""
    strata = [s for s in strata if s[1] > 0 and s[3] > 0]
    if not strata:
        return None
    lo_tot, dist, obs = 0, np.array([1.0]), 0
    for k1, n1, k0, n0 in strata:
        lo, pmf = _hyper_pmf(n1, n0, k1 + k0)
        dist, lo_tot, obs = np.convolve(dist, pmf), lo_tot + lo, obs + k1
    p_obs = dist[obs - lo_tot]
    return float(min(1.0, dist[dist <= p_obs * (1 + 1e-7)].sum()))


# ---------------------------------------------------------------- differences and composites

class Diff:
    """Arm 1 minus arm 0, stratified by task (or task x block). blocks: list of (arm1 cell prefixes, arm0 cell
    prefixes); a prefix is (model, presentation, wording, scores). Each block is split into one stratum per task."""

    def __init__(self, counts: Counts, tasks, blocks):
        self.strata = []  # (task, k1, n1, k0, n0)
        for arm1, arm0 in blocks:
            for t in tasks:
                k1, n1 = counts.get([(*a, t) for a in arm1])
                k0, n0 = counts.get([(*a, t) for a in arm0])
                self.strata.append((t, k1, n1, k0, n0))
        self.usable = [s for s in self.strata if s[2] > 0 and s[4] > 0]

    def totals(self):
        return tuple(sum(s[i] for s in self.strata) for i in (1, 2, 3, 4))

    def estimate(self):
        if not self.usable:
            return None
        return float(np.mean([s[1] / s[2] - s[3] / s[4] for s in self.usable]))

    def per_task(self) -> dict:
        by = defaultdict(list)
        for t, k1, n1, k0, n0 in self.usable:
            by[t].append(k1 / n1 - k0 / n0)
        return {t: float(np.mean(v)) for t, v in by.items()}

    def exact_p(self):
        return exact_stratified([s[1:] for s in self.usable])

    def perm(self, rng) -> np.ndarray:
        """Null draws of the estimate: arm labels shuffled within each stratum."""
        a = np.array([s[1:] for s in self.usable], dtype=int)
        k1, n1, k0, n0 = a.T
        K = k1 + k0
        shape = (N_PERM, len(K))
        d1 = rng.hypergeometric(np.broadcast_to(K, shape), np.broadcast_to(n1 + n0 - K, shape),
                                np.broadcast_to(n1, shape)).astype(float)
        return (d1 / n1 - (K - d1) / n0).mean(axis=1)


def signs(per_task: dict, n_tasks: int) -> dict:
    vals = list(per_task.values())
    return {"+": sum(v > 1e-12 for v in vals), "-": sum(v < -1e-12 for v in vals),
            "0": sum(abs(v) <= 1e-12 for v in vals), "of": n_tasks, "defined": len(vals)}


def composite(label: str, terms: list[tuple[int, Diff]], n_tasks: int, test: str = "auto") -> dict:
    """sum(sign * Diff). One term with test 'auto' -> exact stratified test; otherwise stratified permutation."""
    out = dict(label=label, estimate=None, p=None, test=None, signs=None, per_task={})
    if len(terms) == 1:
        k1, n1, k0, n0 = terms[0][1].totals()
        out |= dict(k1=k1, n1=n1, k0=k0, n0=n0)
    else:
        out["parts"] = [dict(sign=s, estimate=d.estimate(), totals=d.totals()) for s, d in terms]
    if any(not d.usable for _, d in terms):
        return out
    out["estimate"] = float(sum(s * d.estimate() for s, d in terms))
    pts = [d.per_task() for _, d in terms]
    common = set.intersection(*(set(p) for p in pts))
    out["per_task"] = {t: float(sum(s * p[t] for (s, _), p in zip(terms, pts))) for t in sorted(common)}
    out["signs"] = signs(out["per_task"], n_tasks)
    if len(terms) == 1 and test == "auto":
        out["p"], out["test"] = terms[0][1].exact_p(), "exact stratified"
    else:
        rng = np.random.default_rng([SEED, zlib.crc32(label.encode())])
        null = sum(s * d.perm(rng) for s, d in terms)
        out["p"] = float((1 + np.sum(np.abs(null) >= abs(out["estimate"]) - 1e-12)) / (N_PERM + 1))
        out["test"] = f"stratified permutation ({N_PERM})"
    return out


# ---------------------------------------------------------------- the planned contrasts

def contrast_terms(counts, tasks, m, p, name, s="rewarded"):
    """Terms (sign, Diff) for a named contrast in model m, presentation p, score direction s."""
    D = lambda a1, a0: Diff(counts, tasks, [([(m, p, w, s) for w in a1], [(m, p, w, s) for w in a0])])  # noqa
    if name == "exception":
        return [(1, D(["W3", "W4"], ["W1", "W2"]))]
    if name == "phrasing":
        return [(1, D(["W2", "W4"], ["W1", "W3"]))]
    if name == "interaction":  # exception effect under "I'd prefer" minus under "Please"
        return [(1, D(["W4"], ["W2"])), (-1, D(["W3"], ["W1"]))]
    if name == "priority":
        return [(1, D(["W5"], ["W4"]))]
    if name == "W5_vs_W1":
        return [(1, D(["W5"], ["W1"]))]
    if name.startswith("quoting_"):  # rl/quoted - rl/direct at one wording
        w = name.split("_")[1]
        return [(1, Diff(counts, tasks, [([(m, "rl/quoted", w, s)], [(m, "rl/direct", w, s)])]))]
    raise KeyError(name)


CONTRASTS = ("exception", "phrasing", "interaction", "priority", "W5_vs_W1")
QUOTING = tuple(f"quoting_{w}" for w in WORDS)


def within_model(counts, tasks, models) -> list[dict]:
    rows = []
    for m in models:
        for p in PRES:
            for name in CONTRASTS:
                c = composite(f"{m}|{p}|{name}", contrast_terms(counts, tasks, m, p, name), len(tasks))
                rows.append(dict(model=m, presentation=p, contrast=name) | c)
        for name in QUOTING:
            c = composite(f"{m}|rl|{name}", contrast_terms(counts, tasks, m, None, name), len(tasks))
            rows.append(dict(model=m, presentation="rl/quoted-rl/direct", contrast=name) | c)
    return rows


def score_sensitivity(counts, tasks, models) -> list[dict]:
    rows = []
    for m, p in itertools.product(models, PRES):
        for w in WORDS:
            d = Diff(counts, tasks, [([(m, p, w, "rewarded")], [(m, p, w, "penalised")])])
            rows.append(dict(model=m, presentation=p, wording=w) | composite(f"{m}|{p}|{w}|sens", [(1, d)], len(tasks)))
        d = Diff(counts, tasks, [([(m, p, w, "rewarded")], [(m, p, w, "penalised")]) for w in WORDS])
        rows.append(dict(model=m, presentation=p, wording="all (task x wording strata)")
                    | composite(f"{m}|{p}|all|sens", [(1, d)], len(tasks)))
    return rows


def rate_diff_models(counts, tasks, a, b, p, w, s="rewarded"):
    """Adoption rate in model a minus model b, same cell, stratified by task."""
    return Diff(counts, tasks, [([(a, p, w, s)], [(b, p, w, s)])])


def model_differences(counts, tasks, models) -> list[dict]:
    rows = []
    for a, b in MODEL_PAIRS:
        if a not in models or b not in models:
            continue
        pair = f"{short(a)}-{short(b)}"
        for p in PRES:
            for w in WORDS:  # adoption itself
                c = composite(f"{pair}|{p}|{w}|adoption", [(1, rate_diff_models(counts, tasks, a, b, p, w))],
                              len(tasks), test="perm")
                rows.append(dict(pair=pair, presentation=p, contrast=f"adoption {w}") | c)
            for name in CONTRASTS:
                terms = ([(s, d) for s, d in contrast_terms(counts, tasks, a, p, name)]
                         + [(-s, d) for s, d in contrast_terms(counts, tasks, b, p, name)])
                c = composite(f"{pair}|{p}|{name}", terms, len(tasks), test="perm")
                rows.append(dict(pair=pair, presentation=p, contrast=name) | c)
        for name in QUOTING:
            terms = ([(s, d) for s, d in contrast_terms(counts, tasks, a, None, name)]
                     + [(-s, d) for s, d in contrast_terms(counts, tasks, b, None, name)])
            c = composite(f"{pair}|rl|{name}", terms, len(tasks), test="perm")
            rows.append(dict(pair=pair, presentation="rl/quoted-rl/direct", contrast=name) | c)
    return rows


def cell_table(counts, models) -> list[dict]:
    out = []
    for m, p, w in itertools.product(models, PRES, WORDS):
        row = dict(model=m, presentation=p, wording=w)
        for s in W.SCORES:
            keys = [c for c in counts.all if c[:4] == (m, p, w, s)]
            k, n = counts.get(keys)
            row[s] = dict(k=k, n=n, total=sum(counts.all[c] for c in keys), violates=sum(counts.v[c] for c in keys),
                          rate=(k / n if n else None))
        out.append(row)
    return out


def nonvalid_table(counts) -> list[dict]:
    agg = defaultdict(Counter)
    for c, st in counts.status.items():
        agg[c[:4]] += st
    return [dict(model=m, presentation=p, wording=w, scores=s, **{k: v for k, v in st.items() if k != "valid"},
                 valid=st.get("valid", 0), total=sum(st.values()))
            for (m, p, w, s), st in sorted(agg.items()) if sum(st.values()) != st.get("valid", 0)]


# ---------------------------------------------------------------- report

def f_kn(k, n):
    return f"{k}/{n}" + (f" ({k / n:.0%})" if n else "")


def f_num(x, sign=True):
    return "n/a" if x is None else (f"{x:+.2f}" if sign else f"{x:.2f}")


def f_p(p):
    return "n/a" if p is None else ("<0.001" if p < 0.001 else f"{p:.3f}")


def f_sg(s):
    return "n/a" if not s else f"+{s['+']} -{s['-']} ={s['0']} of {s['of']}"


def analyse(records: list[dict], out: Path, manifest: dict, hashes: dict, run: str = "main") -> dict:
    out.mkdir(parents=True, exist_ok=True)
    rows = [r | {"_o": outcome(r)} for r in records]
    counts = Counts(rows)
    tasks = sorted({r["scenario"] for r in rows})
    models = [m for m in MODELS if any(r["model"] == m for r in rows)]
    comp = Counter(r["_o"]["completion"] for r in rows)
    comp_by_model = {m: dict(Counter(r["_o"]["completion"] for r in rows if r["model"] == m)) for m in models}
    res = dict(run=run, n_records=len(rows), tasks=tasks, models=models, completion=dict(comp),
               completion_by_model=comp_by_model, cells=cell_table(counts, models),
               within_model=within_model(counts, tasks, models), score_sensitivity=score_sensitivity(counts, tasks, models),
               model_differences=model_differences(counts, tasks, models), nonvalid=nonvalid_table(counts),
               manifest_sha256=manifest.get("sha256"), code_sha256=hashes, scope=SCOPE,
               settings=dict(seed=SEED, n_perm=N_PERM))
    (out / "results.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
    (out / "ANALYSIS.md").write_text(report(res))
    print(f"analysis: {len(rows)} records, {len(tasks)} tasks -> {out / 'ANALYSIS.md'}")
    return res


def report(res) -> str:
    L = [f"# Request wording: analysis ({res['run']})", "",
         "**Discovery-labelled.** " + res["scope"], ""]
    if res["run"] == "inspection":
        L += ["**Inspection run: n = 1 per cell, one task. Nothing below is interpretable; it only shows that the "
              "pipeline runs end to end.**", ""]
    L += [f"Records: {res['n_records']}; tasks: {len(res['tasks'])} ({', '.join(res['tasks'])}); "
          f"completion: {res['completion']}.", ""]
    for m, c in res["completion_by_model"].items():
        L.append(f"- {m}: {c}")
    L += ["", "Outcome: any em dash in a valid completion. Empty, truncated and failed completions are excluded "
          "(counted below). Estimates are equal-weight means over tasks of per-task rate differences.", ""]

    L += ["## Adoption per cell", "",
          "| model | presentation | wording | rewarded: em dash | penalised: em dash | rewarded: any dash punct. |",
          "|---|---|---|---|---|---|"]
    for c in res["cells"]:
        r, p = c["rewarded"], c["penalised"]
        L.append(f"| {c['model']} | {c['presentation']} | {c['wording']} | {f_kn(r['k'], r['n'])} | "
                 f"{f_kn(p['k'], p['n'])} | {f_kn(r['violates'], r['n'])} |")

    def ctable(rows, key):
        T = [f"| {key} | presentation | contrast | arm 1 | arm 0 | estimate | p | test | task signs |",
             "|---|---|---|---|---|---|---|---|---|"]
        for r in rows:
            a1 = f_kn(r["k1"], r["n1"]) if "k1" in r else "composite"
            a0 = f_kn(r["k0"], r["n0"]) if "k0" in r else ""
            T.append(f"| {r[key]} | {r['presentation']} | {r['contrast']} | {a1} | {a0} | {f_num(r['estimate'])} | "
                     f"{f_p(r['p'])} | {r['test'] or 'n/a'} | {f_sg(r['signs'])} |")
        return T

    L += ["", "## Within-model contrasts (rewarded cells)", "",
          "exception = (W3+W4) - (W1+W2); phrasing = (W2+W4) - (W1+W3); interaction = (W4-W2) - (W3-W1); "
          "priority = W5 - W4; W5_vs_W1 = W5 - W1 (\"W5 near W1\"); quoting_Wk = rl/quoted - rl/direct at Wk.", ""]
    L += ctable(res["within_model"], "model")
    L += ["", "## Score sensitivity (rewarded - penalised)", "",
          "| model | presentation | wording | rewarded | penalised | estimate | p | task signs |", "|---|---|---|---|---|---|---|---|"]
    for r in res["score_sensitivity"]:
        L.append(f"| {r['model']} | {r['presentation']} | {r['wording']} | {f_kn(r['k1'], r['n1'])} | "
                 f"{f_kn(r['k0'], r['n0'])} | {f_num(r['estimate'])} | {f_p(r['p'])} | {f_sg(r['signs'])} |")
    L += ["", "## Model differences (rewarded cells; task-stratified permutation tests)", "",
          "`adoption Wk` = difference in adoption rate at that wording; other rows = difference in the contrast.", ""]
    L += ctable(res["model_differences"], "pair")

    L += ["", "## Readings (numbers only; see HYPOTHESES.md for the pre-registered readings)", ""]
    wm = {(r["model"], r["presentation"], r["contrast"]): r for r in res["within_model"]}
    md = {(r["pair"], r["presentation"], r["contrast"]): r for r in res["model_differences"]}
    for p in PRES:
        L.append(f"- **{p}**")
        for m in res["models"]:
            g = lambda n: wm.get((m, p, n), {}).get("estimate")  # noqa: E731
            L.append(f"  - {m}: exception {f_num(g('exception'))}, phrasing {f_num(g('phrasing'))}, interaction "
                     f"{f_num(g('interaction'))}, priority {f_num(g('priority'))}, W5-W1 {f_num(g('W5_vs_W1'))}")
        for n in ("exception", "phrasing", "priority"):
            r = md.get(("3.8-3.5", p, n))
            if r:
                L.append(f"  - 3.8-3.5 {n}: {f_num(r['estimate'])} (p {f_p(r['p'])}, signs {f_sg(r['signs'])})")
    for m in res["models"]:
        r = wm.get((m, "rl/quoted-rl/direct", "quoting_W1"))
        if r:
            L.append(f"- quoting at W1, {m}: {f_num(r['estimate'])} (p {f_p(r['p'])}, signs {f_sg(r['signs'])})")
    r = md.get(("3.8-3.5", "rl/quoted-rl/direct", "quoting_W1"))
    if r:
        L.append(f"- quoting at W1, 3.8-3.5: {f_num(r['estimate'])} (p {f_p(r['p'])}, signs {f_sg(r['signs'])})")

    L += ["", "## Non-valid completions per cell (excluded from every rate)", ""]
    if not res["nonvalid"]:
        L.append("None.")
    else:
        L += ["| model | presentation | wording | scores | valid | empty | truncated | failed | total |",
              "|---|---|---|---|---|---|---|---|---|"]
        for r in res["nonvalid"]:
            L.append(f"| {r['model']} | {r['presentation']} | {r['wording']} | {r['scores']} | {r['valid']} | "
                     f"{r.get('empty', 0)} | {r.get('truncated', 0)} | {r.get('failed', 0)} | {r['total']} |")
    L += ["", f"Code sha256: `{json.dumps(res['code_sha256'])}`", f"Manifest sha256: {res['manifest_sha256']}", ""]
    return "\n".join(L)


# ---------------------------------------------------------------- self-test on synthetic records

def synthetic(rates, seed=0, tasks=6, samples=2, bad=0.03, task_noise=0.0):
    """rates(model, presentation, wording, scores) -> probability of an em dash. A fraction `bad` is non-valid."""
    rng = np.random.default_rng(seed)
    recs, ts = [], [f"T{i}" for i in range(tasks)]
    shift = {t: rng.normal(0, task_noise) for t in ts}
    for t, p, w, s, m, r in itertools.product(ts, PRES, WORDS, W.SCORES, MODELS, range(samples)):
        u = rng.random()
        if u < bad:
            status, reply = ("error", "") if u < bad / 3 else (("ok", "") if u < 2 * bad / 3 else ("length", "Hi all"))
        else:
            pr = float(np.clip(rates(m, p, w, s) + shift[t], 0, 1))
            reply = "Hi all — see you there." if rng.random() < pr else "Hi all, see you there."
            status = "ok"
        recs.append(dict(model=m, presentation=p, wording=w, scores=s, scenario=t, rep=r, status=status,
                         reply=reply, facts=[]))
    return recs


def selftest(tmp: Path):

    def effect(m, p, w, s):
        if s == "penalised":
            return 0.02
        if m == "Qwen 3.8":
            return {"W1": 0.05, "W2": 0.1, "W3": 0.8, "W4": 0.85, "W5": 0.1}[w]
        return 0.05

    res = analyse(synthetic(effect, 1), tmp / "effect", {}, {}, run="selftest-effect")
    wm = {(r["model"], r["presentation"], r["contrast"]): r for r in res["within_model"]}
    md = {(r["pair"], r["presentation"], r["contrast"]): r for r in res["model_differences"]}
    for p in PRES:
        assert wm[("Qwen 3.8", p, "exception")]["p"] < 0.001 and wm[("Qwen 3.8", p, "exception")]["estimate"] > 0.5
        assert wm[("Qwen 3.8", p, "priority")]["p"] < 0.05 and wm[("Qwen 3.8", p, "priority")]["estimate"] < -0.4
        assert md[("3.8-3.5", p, "exception")]["p"] < 0.001 and md[("3.6-3.5", p, "exception")]["p"] > 0.05
        assert wm[("Qwen 3.8", p, "exception")]["signs"]["+"] >= 5
    assert sum(r.get("failed", 0) + r.get("empty", 0) + r.get("truncated", 0) for r in res["nonvalid"]) > 0
    print("selftest effect: planted exception/priority effects and the 3.8-3.5 difference detected")

    # null: same rate everywhere -> p-values should be roughly uniform (exact test conservative)
    ps_exact, ps_perm = [], []
    for seed in range(40):
        res = analyse(synthetic(lambda *a: 0.3, 100 + seed), tmp / "null", {}, {}, run="selftest-null")
        ps_exact += [r["p"] for r in res["within_model"] if r["test"] == "exact stratified" and r["p"] is not None]
        ps_perm += [r["p"] for r in res["model_differences"] if r["p"] is not None]
    fe, fp = np.mean(np.array(ps_exact) < 0.05), np.mean(np.array(ps_perm) < 0.05)
    print(f"selftest null: P(p<0.05) exact {fe:.3f} (n={len(ps_exact)}), permutation {fp:.3f} (n={len(ps_perm)})")
    assert fe <= 0.07 and fp <= 0.07, (fe, fp)
    print(f"selftest passed; reports in {tmp}")


if __name__ == "__main__":
    if sys.argv[1:2] == ["selftest"] and len(sys.argv) == 3:
        selftest(Path(sys.argv[2]))
    else:
        raise SystemExit(__doc__)
