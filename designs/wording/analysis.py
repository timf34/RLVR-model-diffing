"""Analysis of the request-wording experiment (plan: HYPOTHESES.md as amended by HYPOTHESES_AMENDMENT.md, which
governs where they conflict; discovery-labelled throughout).

  .venv/bin/python designs/wording/run.py analyse main|inspection        # real runs (records joined by run.py)
  .venv/bin/python designs/wording/analysis.py selftest <scratch dir>     # synthetic records: an effect and a null
  .venv/bin/python designs/wording/analysis.py calibrate <out.md> [n]     # synthetic null/power datasets -> CALIBRATION.md

Outcome: `adopted` = any em dash in a VALID completion (rl_context score.completion: empty, truncated and
failed completions are never counted as compliance; they are excluded and reported per cell). Secondary:
`violates` = any dash used as punctuation (emdash_score.measures), reported in the cell table.

Cells are (model, presentation, wording, scores, task). Rates are among valid completions; in the main run a
rewarded model x presentation x wording cell has n = 12 (6 tasks x 2 samples) before exclusions.

Primary (Amendment 1): exception effect E = 1/2 [(W3 - W1) + (W4 - W2)] per model x presentation (rewarded
cells); each difference is the equal-weight mean over tasks of per-task rate differences (over tasks where both
arms have valid completions). Primary contrast: E(3.8) - E(3.5) in `anchor` and in `rl/quoted` -- two tests,
each a task-stratified permutation test (wording labels redrawn within model x task for each component
difference, hypergeometric given margins; 10,000 draws, fixed seed), Holm-corrected across the two at 0.05,
each with a 95% two-stage bootstrap interval (tasks with replacement, then samples with replacement within each
task's cells; percentile). A task-level sign-flip p (exact, 2^6 flips, smallest possible 0.031) is reported
beside it as a robustness check that does not assume samples are independent.

Secondary (prespecified, uncorrected): E per model; E(3.6) vs each other model; E in rl/direct; the frozen
plan's contrasts (pooled exception, phrasing, interaction, priority, W5-W1, quoting), score sensitivity and
model differences. Single within-model differences use the task-stratified exact conditional test; composites
and model differences use the stratified permutation test. Every contrast gets a bootstrap interval and an
equivalence verdict ("similar" only if the 95% interval lies within +/-10 pp).
"""
from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import math
import sys
import time
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

SEED, N_PERM, N_BOOT = 20261028, 10_000, 2_000
ALPHA = 0.05
EQUIV = 0.10        # "similar" only if the 95% interval lies within +/- 10 pp
MEANINGFUL = 0.20   # practical convention for a meaningful effect (not a statistical boundary)
LOW_RATE = 2 / 12   # low-rate presentation: rewarded adoption <= 2/12 at every wording
MODELS = ("Qwen 3.5", "Qwen 3.6", "Qwen 3.8")
MODEL_PAIRS = (("Qwen 3.8", "Qwen 3.5"), ("Qwen 3.6", "Qwen 3.5"), ("Qwen 3.8", "Qwen 3.6"))
WORDS = tuple(W.WORDINGS)
PRES = W.PRESENTATIONS
PRIMARY_PRES = ("anchor", "rl/quoted")
PRIMARY_PAIR = ("Qwen 3.8", "Qwen 3.5")
MAIN_MANIFEST = HERE / "runs" / "main" / "manifest.json"  # freeze record only (hashes); written before generation
SCOPE = ("Scope: p-values are conditional on these tasks and prompts (samples within a cell treated as "
         "independent draws); there is no claim beyond them. Task sign counts describe consistency across tasks "
         "(descriptive, not evidence of broad generalisation). Only the two primary tests are multiplicity-corrected "
         "(Holm); everything else is secondary and uncorrected. Everything here is discovery-labelled.")


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

    @classmethod
    def from_arrays(cls, k: np.ndarray, n: np.ndarray, tasks, models=MODELS) -> "Counts":
        """Synthetic counts (calibration): arrays indexed [model, presentation, wording, scores, task]."""
        self = cls([])
        for idx in itertools.product(*(range(s) for s in k.shape)):
            c = (models[idx[0]], PRES[idx[1]], WORDS[idx[2]], W.SCORES[idx[3]], tasks[idx[4]])
            self.k[c], self.n[c], self.all[c] = int(k[idx]), int(n[idx]), int(n[idx])
        return self

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


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float] | None:
    if not n:
        return None
    p, d = k / n, 1 + z * z / n
    c, h = (p + z * z / (2 * n)) / d, z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def holm(ps: list[float | None]) -> list[float | None]:
    """Holm step-down adjusted p-values (None entries are skipped and stay None)."""
    idx = sorted((i for i, p in enumerate(ps) if p is not None), key=lambda i: ps[i])
    out, run, m = [None] * len(ps), 0.0, len(idx)
    for j, i in enumerate(idx):
        run = max(run, min(1.0, (m - j) * ps[i]))
        out[i] = run
    return out


# ---------------------------------------------------------------- differences and composites

class Diff:
    """Arm 1 minus arm 0, stratified by task (or task x block). blocks: list of (arm1 cell prefixes, arm0 cell
    prefixes); a prefix is (model, presentation, wording, scores). Each block is split into one stratum per task."""

    def __init__(self, counts: Counts, tasks, blocks):
        self.strata = []  # (task, k1, n1, k0, n0)
        self.arr = np.zeros((len(blocks), len(tasks), 4), dtype=np.int64)  # [block, task, (k1, n1, k0, n0)]
        for b, (arm1, arm0) in enumerate(blocks):
            for j, t in enumerate(tasks):
                k1, n1 = counts.get([(*a, t) for a in arm1])
                k0, n0 = counts.get([(*a, t) for a in arm0])
                self.strata.append((t, k1, n1, k0, n0))
                self.arr[b, j] = (k1, n1, k0, n0)
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

    def perm(self, rng, n_perm: int = N_PERM) -> np.ndarray:
        """Null draws of the estimate: arm labels shuffled within each stratum (hypergeometric given margins)."""
        a = np.array([s[1:] for s in self.usable], dtype=int)
        k1, n1, k0, n0 = a.T
        K = k1 + k0
        shape = (n_perm, len(K))
        d1 = rng.hypergeometric(np.broadcast_to(K, shape), np.broadcast_to(n1 + n0 - K, shape),
                                np.broadcast_to(n1, shape)).astype(float)
        return (d1 / n1 - (K - d1) / n0).mean(axis=1)

    def boot(self, idx: np.ndarray, rng) -> np.ndarray:
        """Two-stage bootstrap draws of the estimate. idx: (B, n_tasks) resampled task indices (shared by every
        term of a composite); then each drawn cell's samples are resampled with replacement (binomial)."""
        k1, n1, k0, n0 = np.moveaxis(self.arr[:, idx], -1, 0)  # each (blocks, B, tasks)
        use = (n1 > 0) & (n0 > 0)
        s1, s0 = np.maximum(n1, 1), np.maximum(n0, 1)
        r1 = rng.binomial(n1, k1 / s1) / s1
        r0 = rng.binomial(n0, k0 / s0) / s0
        num, den = ((r1 - r0) * use).sum(axis=(0, 2)), use.sum(axis=(0, 2))
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(den > 0, num / den, np.nan)


def signs(per_task: dict, n_tasks: int) -> dict:
    vals = list(per_task.values())
    return {"+": sum(v > 1e-12 for v in vals), "-": sum(v < -1e-12 for v in vals),
            "0": sum(abs(v) <= 1e-12 for v in vals), "of": n_tasks, "defined": len(vals)}


def signflip_p(vals) -> float | None:
    """Exact two-sided task-level sign-flip test of the mean per-task contrast (all 2^m flips)."""
    v = np.asarray(list(vals), dtype=float)
    if not len(v):
        return None
    flips = np.array(list(itertools.product((1, -1), repeat=len(v))))
    null = (flips * v).mean(axis=1)
    return float(np.mean(np.abs(null) >= abs(v.mean()) - 1e-12))


def verdict(ci, hard: bool = False) -> str:
    if ci is None:
        return "n/a"
    lo, hi = ci
    if hard:
        return "hard to estimate (low rate)"
    if hi - lo < 1e-9:  # every resample identical (all-0 / all-1 cells): no information about precision
        return "degenerate interval (too little variation)"
    if lo >= -EQUIV - 1e-12 and hi <= EQUIV + 1e-12:
        return "similar (within ±10 pp)"
    if lo > 0 or hi < 0:
        return "interval excludes 0"
    return "inconclusive"


def composite(label: str, terms: list[tuple[float, Diff]], n_tasks: int, test: str = "auto", *,
              n_perm: int = N_PERM, n_boot: int = N_BOOT, seed: int = SEED, sign_flip: bool = False) -> dict:
    """sum(weight * Diff). One term with test 'auto' -> exact stratified test; otherwise stratified permutation.
    Adds a two-stage bootstrap interval (n_boot > 0) and optionally the task-level sign-flip p."""
    out = dict(label=label, estimate=None, p=None, test=None, signs=None, per_task={}, ci=None)
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
    crc = zlib.crc32(label.encode())
    if len(terms) == 1 and test == "auto":
        out["p"], out["test"] = terms[0][1].exact_p(), "exact stratified"
    else:
        rng = np.random.default_rng([seed, crc])
        null = sum(s * d.perm(rng, n_perm) for s, d in terms)
        out["p"] = float((1 + np.sum(np.abs(null) >= abs(out["estimate"]) - 1e-12)) / (n_perm + 1))
        out["test"] = f"stratified permutation ({n_perm})"
    if n_boot:
        rng = np.random.default_rng([seed, crc, 1])
        idx = rng.integers(0, terms[0][1].arr.shape[1], size=(n_boot, terms[0][1].arr.shape[1]))
        draws = sum(s * d.boot(idx, rng) for s, d in terms)
        draws = draws[~np.isnan(draws)]
        if len(draws) >= 0.9 * n_boot:
            out["ci"] = tuple(float(x) for x in np.percentile(draws, [2.5, 97.5]))
    if sign_flip:
        out["p_signflip"] = signflip_p(out["per_task"].values())
    return out


# ---------------------------------------------------------------- the planned contrasts

def contrast_terms(counts, tasks, m, p, name, s="rewarded"):
    """Terms (weight, Diff) for a named contrast in model m, presentation p, score direction s."""
    D = lambda a1, a0: Diff(counts, tasks, [([(m, p, w, s) for w in a1], [(m, p, w, s) for w in a0])])  # noqa
    if name == "E":  # Amendment 1: exception effect averaged over both phrasings
        return [(0.5, D(["W3"], ["W1"])), (0.5, D(["W4"], ["W2"]))]
    if name == "exception_pooled":  # frozen-plan definition, (W3+W4) - (W1+W2) with counts pooled within task
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


def pair_terms(counts, tasks, a, b, p, name):
    return ([(s, d) for s, d in contrast_terms(counts, tasks, a, p, name)]
            + [(-s, d) for s, d in contrast_terms(counts, tasks, b, p, name)])


CONTRASTS = ("exception_pooled", "phrasing", "interaction", "priority", "W5_vs_W1")
QUOTING = tuple(f"quoting_{w}" for w in WORDS)


def primary(counts, tasks, models, **kw) -> list[dict]:
    """E(3.8) - E(3.5) in anchor and rl/quoted: two permutation tests, Holm across them."""
    a, b = PRIMARY_PAIR
    if a not in models or b not in models:
        return []
    rows = []
    for p in PRIMARY_PRES:
        c = composite(f"primary|{p}", pair_terms(counts, tasks, a, b, p, "E"), len(tasks), test="perm",
                      sign_flip=True, **kw)
        rows.append(dict(pair=f"{short(a)}-{short(b)}", presentation=p, contrast="E") | c)
    for r, h in zip(rows, holm([r["p"] for r in rows])):
        r["p_holm"] = h
        r["reject_holm"] = h is not None and h <= ALPHA
    return rows


def secondary_E(counts, tasks, models, **kw) -> list[dict]:
    """Secondary, uncorrected: E per model x presentation; E(3.6) vs each other model; E(3.8)-E(3.5) in rl/direct."""
    rows = []
    for m, p in itertools.product(models, PRES):
        c = composite(f"E|{m}|{p}", contrast_terms(counts, tasks, m, p, "E"), len(tasks), test="perm", **kw)
        rows.append(dict(kind="E per model", who=m, presentation=p, contrast="E", involved=[(m, p)]) | c)
    pairs = [(PRIMARY_PAIR, ("rl/direct",)), (("Qwen 3.6", "Qwen 3.5"), PRES), (("Qwen 3.6", "Qwen 3.8"), PRES)]
    for (a, b), ps in pairs:
        if a not in models or b not in models:
            continue
        for p in ps:
            c = composite(f"Ediff|{a}|{b}|{p}", pair_terms(counts, tasks, a, b, p, "E"), len(tasks), test="perm", **kw)
            rows.append(dict(kind="E model difference", who=f"{short(a)}-{short(b)}", presentation=p, contrast="E",
                             involved=[(a, p), (b, p)]) | c)
    return rows


def within_model(counts, tasks, models, **kw) -> list[dict]:
    rows = []
    for m in models:
        for p in PRES:
            for name in CONTRASTS:
                c = composite(f"{m}|{p}|{name}", contrast_terms(counts, tasks, m, p, name), len(tasks), **kw)
                rows.append(dict(model=m, presentation=p, contrast=name, involved=[(m, p)]) | c)
        for name in QUOTING:
            c = composite(f"{m}|rl|{name}", contrast_terms(counts, tasks, m, None, name), len(tasks), **kw)
            rows.append(dict(model=m, presentation="rl/quoted-rl/direct", contrast=name,
                             involved=[(m, "rl/quoted"), (m, "rl/direct")]) | c)
    return rows


def score_sensitivity(counts, tasks, models, **kw) -> list[dict]:
    rows = []
    for m, p in itertools.product(models, PRES):
        for w in WORDS:
            d = Diff(counts, tasks, [([(m, p, w, "rewarded")], [(m, p, w, "penalised")])])
            rows.append(dict(model=m, presentation=p, wording=w)
                        | composite(f"{m}|{p}|{w}|sens", [(1, d)], len(tasks), **kw))
        d = Diff(counts, tasks, [([(m, p, w, "rewarded")], [(m, p, w, "penalised")]) for w in WORDS])
        rows.append(dict(model=m, presentation=p, wording="all (task x wording strata)")
                    | composite(f"{m}|{p}|all|sens", [(1, d)], len(tasks), **kw))
    return rows


def rate_diff_models(counts, tasks, a, b, p, w, s="rewarded"):
    """Adoption rate in model a minus model b, same cell, stratified by task."""
    return Diff(counts, tasks, [([(a, p, w, s)], [(b, p, w, s)])])


def model_differences(counts, tasks, models, **kw) -> list[dict]:
    rows = []
    for a, b in MODEL_PAIRS:
        if a not in models or b not in models:
            continue
        pair = f"{short(a)}-{short(b)}"
        for p in PRES:
            inv = [(a, p), (b, p)]
            for w in WORDS:  # adoption itself
                c = composite(f"{pair}|{p}|{w}|adoption", [(1, rate_diff_models(counts, tasks, a, b, p, w))],
                              len(tasks), test="perm", **kw)
                rows.append(dict(pair=pair, presentation=p, contrast=f"adoption {w}", involved=inv) | c)
            for name in CONTRASTS:
                c = composite(f"{pair}|{p}|{name}", pair_terms(counts, tasks, a, b, p, name), len(tasks),
                              test="perm", **kw)
                rows.append(dict(pair=pair, presentation=p, contrast=name, involved=inv) | c)
        for name in QUOTING:
            c = composite(f"{pair}|rl|{name}", pair_terms(counts, tasks, a, b, None, name), len(tasks), test="perm", **kw)
            rows.append(dict(pair=pair, presentation="rl/quoted-rl/direct", contrast=name,
                             involved=[(x, q) for x in (a, b) for q in ("rl/quoted", "rl/direct")]) | c)
    return rows


def cell_table(counts, models) -> list[dict]:
    out = []
    for m, p, w in itertools.product(models, PRES, WORDS):
        row = dict(model=m, presentation=p, wording=w)
        for s in W.SCORES:
            keys = [c for c in counts.all if c[:4] == (m, p, w, s)]
            k, n = counts.get(keys)
            row[s] = dict(k=k, n=n, total=sum(counts.all[c] for c in keys), violates=sum(counts.v[c] for c in keys),
                          rate=(k / n if n else None), wilson=wilson(k, n))
        out.append(row)
    return out


def low_rate(cells, models) -> list[dict]:
    """Model x presentation whose rewarded adoption is <= 2/12 at every wording (n = 0 counts as low)."""
    out = []
    for m, p in itertools.product(models, PRES):
        rs = [c["rewarded"] for c in cells if c["model"] == m and c["presentation"] == p]
        if all(r["n"] == 0 or r["k"] / r["n"] <= LOW_RATE + 1e-12 for r in rs):
            out.append(dict(model=m, presentation=p, rewarded={c["wording"]: f"{c['rewarded']['k']}/{c['rewarded']['n']}"
                                                                for c in cells if c["model"] == m and c["presentation"] == p}))
    return out


def flag(rows, low: set) -> None:
    """Mark a contrast hard to estimate when every model x presentation it involves is low-rate; add the verdict."""
    for r in rows:
        inv = r.get("involved") or []
        r["hard"] = bool(inv) and all(tuple(x) in low for x in inv)
        r["verdict"] = verdict(r.get("ci"), r["hard"])


def nonvalid_table(counts) -> list[dict]:
    agg = defaultdict(Counter)
    for c, st in counts.status.items():
        agg[c[:4]] += st
    return [dict(model=m, presentation=p, wording=w, scores=s, **{k: v for k, v in st.items() if k != "valid"},
                 valid=st.get("valid", 0), total=sum(st.values()))
            for (m, p, w, s), st in sorted(agg.items()) if sum(st.values()) != st.get("valid", 0)]


def provenance(manifest: dict, hashes: dict) -> dict:
    """Frozen hashes (manifest) vs the files as they are now. The inspection run is analysed without a manifest, so
    the main run's freeze record (hashes only; written before generation) is read for the header."""
    src = "passed by run.py"
    if not manifest and MAIN_MANIFEST.exists():
        m = json.loads(MAIN_MANIFEST.read_text())
        manifest, src = {k: m.get(k) for k in ("sha256", "hypotheses_sha256", "code_sha256", "at")}, str(
            MAIN_MANIFEST.relative_to(HERE))
    frozen_code = manifest.get("code_sha256") or {}
    now_hyp = hashlib.sha256((HERE / "HYPOTHESES.md").read_bytes()).hexdigest()
    amend = HERE / "HYPOTHESES_AMENDMENT.md"
    return dict(manifest_source=src if manifest else "none", frozen_at=manifest.get("at"),
                prompts_sha256=manifest.get("sha256"), hypotheses_frozen=manifest.get("hypotheses_sha256"),
                hypotheses_now=now_hyp,
                amendment_sha256=hashlib.sha256(amend.read_bytes()).hexdigest() if amend.exists() else None,
                code_frozen=frozen_code, code_now=hashes,
                code_changed=sorted(k for k in hashes if frozen_code.get(k) and frozen_code[k] != hashes[k]))


def analyse(records: list[dict], out: Path, manifest: dict, hashes: dict, run: str = "main") -> dict:
    out.mkdir(parents=True, exist_ok=True)
    rows = [r | {"_o": outcome(r)} for r in records]
    counts = Counts(rows)
    tasks = sorted({r["scenario"] for r in rows})
    models = [m for m in MODELS if any(r["model"] == m for r in rows)]
    comp = Counter(r["_o"]["completion"] for r in rows)
    comp_by_model = {m: dict(Counter(r["_o"]["completion"] for r in rows if r["model"] == m)) for m in models}
    cells = cell_table(counts, models)
    low = low_rate(cells, models)
    lowset = {(x["model"], x["presentation"]) for x in low}
    prim = primary(counts, tasks, models)
    for r in prim:
        r["involved"] = [(PRIMARY_PAIR[0], r["presentation"]), (PRIMARY_PAIR[1], r["presentation"])]
    sec_E = secondary_E(counts, tasks, models)
    wm = within_model(counts, tasks, models)
    md = model_differences(counts, tasks, models)
    for group in (prim, sec_E, wm, md):
        flag(group, lowset)
    res = dict(run=run, n_records=len(rows), tasks=tasks, models=models, completion=dict(comp),
               completion_by_model=comp_by_model, cells=cells, low_rate=low, primary=prim, secondary_E=sec_E,
               within_model=wm, score_sensitivity=score_sensitivity(counts, tasks, models), model_differences=md,
               nonvalid=nonvalid_table(counts), provenance=provenance(manifest, hashes), scope=SCOPE,
               settings=dict(seed=SEED, n_perm=N_PERM, n_boot=N_BOOT, alpha=ALPHA, equivalence_margin=EQUIV,
                             meaningful=MEANINGFUL, low_rate=LOW_RATE))
    (out / "results.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
    (out / "ANALYSIS.md").write_text(report(res))
    print(f"analysis: {len(rows)} records, {len(tasks)} tasks -> {out / 'ANALYSIS.md'}")
    return res


# ---------------------------------------------------------------- report

def f_kn(k, n):
    return f"{k}/{n}" + (f" ({k / n:.0%})" if n else "")


def f_wil(k, n):
    w = wilson(k, n)
    return f_kn(k, n) + (f" [{w[0]:.0%}, {w[1]:.0%}]" if w else "")


def f_num(x, sign=True):
    return "n/a" if x is None else (f"{x:+.2f}" if sign else f"{x:.2f}")


def f_ci(ci):
    return "n/a" if ci is None else f"[{ci[0]:+.2f}, {ci[1]:+.2f}]"


def f_p(p):
    return "n/a" if p is None else ("<0.001" if p < 0.001 else f"{p:.3f}")


def f_sg(s):
    return "n/a" if not s else f"+{s['+']} -{s['-']} ={s['0']} of {s['of']}"


def header(res) -> list[str]:
    pv = res["provenance"]
    L = [f"# Request wording: analysis ({res['run']})", "",
         "**Discovery-labelled.** The question and wordings were chosen after seeing the title results in "
         "`designs/rl_context/`; nothing here is confirmatory or proof of a mechanism. The plan (`HYPOTHESES.md`) "
         "was **finalised after the 90-conversation inspection, which is excluded** from all main analyses (it "
         "informed the choice of primary presentations). **Amendment 1 (`HYPOTHESES_AMENDMENT.md`) was recorded "
         "before any main-run data were viewed** and governs where the two conflict.", "",
         res["scope"], ""]
    if res["run"] == "inspection":
        L += ["**Inspection run: n = 1 per cell, one task. Nothing below is interpretable; it only shows that the "
              "pipeline runs end to end.**", ""]
    L += ["**Calibration (`CALIBRATION.md`, 1,000 synthetic null datasets per scenario, no main-run data).** The "
          "primary permutation test was not anti-conservative in any scenario (raw false-positive rate 0.00-0.05, "
          "Holm family-wise 0.00-0.055 ± 0.007, including sparse/all-zero cells, task heterogeneity, unequal model "
          "levels and equal nuisance exception effects). Within-cell correlation (prompt-level variation treated as "
          "random, logit sd 1) raised it to the nominal level (0.05); stronger prompt-level variation would push it "
          "above, so the p-values are read as conditional on these prompts. The task-level sign-flip p beside the "
          "primary result does not need that assumption, but with 6 tasks its smallest value is 0.031 and it cannot "
          "pass Holm's 0.025 on its own. **Power is low:** a true +0.30 primary contrast is detected after Holm about "
          "24% of the time at moderate base rates (about 60% when the base rate is near zero); +0.20 about 10%. A "
          "non-significant primary result is therefore not evidence of no difference; read the interval.", ""]
    L += ["### Provenance", "",
          f"- Manifest ({pv['manifest_source']}; frozen {pv['frozen_at'] or 'n/a'}): prompts/serving sha256 "
          f"`{pv['prompts_sha256'] or 'n/a'}`",
          f"- HYPOTHESES.md: frozen `{pv['hypotheses_frozen'] or 'n/a'}`, now `{pv['hypotheses_now']}` "
          f"({'unchanged' if pv['hypotheses_frozen'] == pv['hypotheses_now'] else 'DIFFERS' if pv['hypotheses_frozen'] else 'no frozen hash'})",
          f"- HYPOTHESES_AMENDMENT.md (amendment 1): `{pv['amendment_sha256'] or 'missing'}`"]
    fa, na = pv["code_frozen"].get("analysis.py"), pv["code_now"].get("analysis.py")
    L.append(f"- analysis.py: frozen `{fa or 'n/a'}`, now `{na or 'n/a'}`"
             + (" -- **differs from the frozen hash: this analysis implements Amendment 1** (primary E contrast, "
                "Holm, intervals, equivalence, low-rate note, calibration); prompts, serving and data collection are "
                "unchanged." if fa and na and fa != na else (" (unchanged)" if fa and fa == na else "")))
    other = [k for k in pv["code_changed"] if k != "analysis.py"]
    L.append(f"- Other code differing from the frozen hashes: {', '.join(other) if other else 'none'}")
    L.append("")
    return L


def report(res) -> str:
    L = header(res)
    L += [f"Records: {res['n_records']}; tasks: {len(res['tasks'])} ({', '.join(res['tasks'])}); "
          f"completion: {res['completion']}.", ""]
    for m, c in res["completion_by_model"].items():
        L.append(f"- {m}: {c}")
    L += ["", "Outcome: any em dash in a valid completion. Empty, truncated and failed completions are excluded "
          "(counted at the end). **n = valid completions in rewarded cells: 12 per model × presentation × wording "
          "(6 tasks × 2 samples) before exclusions.** Estimates are equal-weight means over tasks of per-task rate "
          "differences. Intervals: 95% two-stage bootstrap (tasks, then samples within task; "
          f"{res['settings']['n_boot']} draws). Effects of at least {MEANINGFUL:.0%} are 'meaningful' by convention "
          "only; every effect is reported with its interval. **Similar** = 95% interval within ±10 pp; otherwise "
          "a small estimate is **inconclusive**.", ""]

    # ---- primary
    L += ["## Primary", "",
          "Exception effect **E = ½[(W3 − W1) + (W4 − W2)]** (rewarded cells). Primary contrast: **E(Qwen 3.8) − "
          "E(Qwen 3.5)**, separately in `anchor` and `rl/quoted` (two tests; task-stratified permutation, "
          f"{res['settings']['n_perm']} draws, seed {SEED}; Holm across the two at α = {ALPHA}).", "",
          "| presentation | E(3.8) | E(3.5) | E(3.8) − E(3.5) | 95% interval | p (raw) | p (Holm) | Holm reject | "
          "task signs | sign-flip p (robustness) | verdict |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    se = {(r["who"], r["presentation"]): r for r in res["secondary_E"] if r["kind"] == "E per model"}
    for r in res["primary"]:
        e8, e5 = se.get((PRIMARY_PAIR[0], r["presentation"]), {}), se.get((PRIMARY_PAIR[1], r["presentation"]), {})
        L.append(f"| {r['presentation']} | {f_num(e8.get('estimate'))} {f_ci(e8.get('ci'))} | "
                 f"{f_num(e5.get('estimate'))} {f_ci(e5.get('ci'))} | **{f_num(r['estimate'])}** | {f_ci(r['ci'])} | "
                 f"{f_p(r['p'])} | {f_p(r['p_holm'])} | {'yes' if r['reject_holm'] else 'no'} | {f_sg(r['signs'])} | "
                 f"{f_p(r.get('p_signflip'))} | {r['verdict']} |")
    if not res["primary"]:
        L.append("(primary pair not present in these records)")
    L += ["", "Per-task E(3.8) − E(3.5): " + "; ".join(
        f"{r['presentation']}: " + ", ".join(f"{t} {v:+.2f}" for t, v in r["per_task"].items()) for r in res["primary"]), ""]

    # ---- low-rate presentations
    L += ["## Low-rate presentations (a finding, not an exclusion)", "",
          "Model × presentation where rewarded adoption is ≤ 2/12 at every wording. These presentations **rarely "
          "produce accommodation**; no cell is dropped, but wording contrasts there are **hard to estimate** (their "
          "bootstrap intervals can be degenerate, e.g. [0, 0], so they are never read as 'similar'). A contrast "
          "whose resamples are all identical is marked 'degenerate interval' wherever it occurs.", ""]
    if res["low_rate"]:
        for x in res["low_rate"]:
            L.append(f"- {x['model']}, {x['presentation']}: " + ", ".join(f"{w} {v}" for w, v in x["rewarded"].items()))
    else:
        L.append("None.")

    # ---- secondary E
    L += ["", "## Secondary (prespecified, not multiplicity-corrected)", "",
          "### Exception effect E per model, E(3.6) vs the others, E(3.8) − E(3.5) in rl/direct", "",
          "| kind | model(s) | presentation | estimate | 95% interval | p | task signs | verdict |",
          "|---|---|---|---|---|---|---|---|"]
    for r in res["secondary_E"]:
        L.append(f"| {r['kind']} | {r['who']} | {r['presentation']} | {f_num(r['estimate'])} | {f_ci(r['ci'])} | "
                 f"{f_p(r['p'])} | {f_sg(r['signs'])} | {r['verdict']} |")

    def ctable(rows, key):
        T = [f"| {key} | presentation | contrast | arm 1 | arm 0 | estimate | 95% interval | p | test | task signs | "
             "verdict |", "|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in rows:
            a1 = f_kn(r["k1"], r["n1"]) if "k1" in r else "composite"
            a0 = f_kn(r["k0"], r["n0"]) if "k0" in r else ""
            T.append(f"| {r[key]} | {r['presentation']} | {r['contrast']} | {a1} | {a0} | {f_num(r['estimate'])} | "
                     f"{f_ci(r.get('ci'))} | {f_p(r['p'])} | {r['test'] or 'n/a'} | {f_sg(r['signs'])} | "
                     f"{r.get('verdict', '')} |")
        return T

    L += ["", "### Other within-model contrasts (rewarded cells)", "",
          "exception_pooled = (W3+W4) − (W1+W2) with counts pooled within task (the frozen definition; equals E "
          "when all cells have equal n); phrasing = (W2+W4) − (W1+W3); interaction = (W4−W2) − (W3−W1); "
          "priority = W5 − W4; W5_vs_W1 = W5 − W1; quoting_Wk = rl/quoted − rl/direct at Wk.", ""]
    L += ctable(res["within_model"], "model")
    L += ["", "### Model differences (rewarded cells; task-stratified permutation tests)", "",
          "`adoption Wk` = difference in adoption rate at that wording; other rows = difference in the contrast. "
          "Hard to estimate when both models are low-rate in that presentation.", ""]
    L += ctable(res["model_differences"], "pair")
    L += ["", "### Score sensitivity (rewarded − penalised)", "",
          "| model | presentation | wording | rewarded | penalised | estimate | 95% interval | p | task signs |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r in res["score_sensitivity"]:
        L.append(f"| {r['model']} | {r['presentation']} | {r['wording']} | {f_kn(r['k1'], r['n1'])} | "
                 f"{f_kn(r['k0'], r['n0'])} | {f_num(r['estimate'])} | {f_ci(r.get('ci'))} | {f_p(r['p'])} | "
                 f"{f_sg(r['signs'])} |")

    L += ["", "## Adoption per cell (Wilson 95% intervals)", "",
          "| model | presentation | wording | rewarded: em dash | penalised: em dash | rewarded: any dash punct. |",
          "|---|---|---|---|---|---|"]
    for c in res["cells"]:
        r, p = c["rewarded"], c["penalised"]
        L.append(f"| {c['model']} | {c['presentation']} | {c['wording']} | {f_wil(r['k'], r['n'])} | "
                 f"{f_wil(p['k'], p['n'])} | {f_kn(r['violates'], r['n'])} |")

    L += ["", "## Readings (numbers only; see HYPOTHESES.md and the amendment for the pre-registered readings)", ""]
    wm = {(r["model"], r["presentation"], r["contrast"]): r for r in res["within_model"]}
    md = {(r["pair"], r["presentation"], r["contrast"]): r for r in res["model_differences"]}
    for p in PRES:
        L.append(f"- **{p}**")
        for m in res["models"]:
            g = lambda n: wm.get((m, p, n), {})  # noqa: E731
            e = se.get((m, p), {})
            L.append(f"  - {m}: E {f_num(e.get('estimate'))} {f_ci(e.get('ci'))}, phrasing "
                     f"{f_num(g('phrasing').get('estimate'))} {f_ci(g('phrasing').get('ci'))}, interaction "
                     f"{f_num(g('interaction').get('estimate'))}, priority {f_num(g('priority').get('estimate'))} "
                     f"{f_ci(g('priority').get('ci'))}, W5-W1 {f_num(g('W5_vs_W1').get('estimate'))} "
                     f"{f_ci(g('W5_vs_W1').get('ci'))} ({g('W5_vs_W1').get('verdict', 'n/a')})")
        for n in ("phrasing", "priority"):
            r = md.get(("3.8-3.5", p, n))
            if r:
                L.append(f"  - 3.8-3.5 {n}: {f_num(r['estimate'])} {f_ci(r['ci'])} (p {f_p(r['p'])}, signs "
                         f"{f_sg(r['signs'])}; {r['verdict']})")
    for m in res["models"]:
        r = wm.get((m, "rl/quoted-rl/direct", "quoting_W1"))
        if r:
            L.append(f"- quoting at W1, {m}: {f_num(r['estimate'])} {f_ci(r['ci'])} (p {f_p(r['p'])}, signs "
                     f"{f_sg(r['signs'])}; {r['verdict']})")
    r = md.get(("3.8-3.5", "rl/quoted-rl/direct", "quoting_W1"))
    if r:
        L.append(f"- quoting at W1, 3.8-3.5: {f_num(r['estimate'])} {f_ci(r['ci'])} (p {f_p(r['p'])}, signs "
                 f"{f_sg(r['signs'])})")

    L += ["", "## Non-valid completions per cell (excluded from every rate)", ""]
    if not res["nonvalid"]:
        L.append("None.")
    else:
        L += ["| model | presentation | wording | scores | valid | empty | truncated | failed | total |",
              "|---|---|---|---|---|---|---|---|---|"]
        for r in res["nonvalid"]:
            L.append(f"| {r['model']} | {r['presentation']} | {r['wording']} | {r['scores']} | {r['valid']} | "
                     f"{r.get('empty', 0)} | {r.get('truncated', 0)} | {r.get('failed', 0)} | {r['total']} |")
    L += ["", f"Code sha256 (now): `{json.dumps(res['provenance']['code_now'])}`", ""]
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
    # unit checks
    assert holm([0.01, 0.04]) == [0.02, 0.04] and holm([0.04, 0.03]) == [0.06, 0.06] and holm([None, 0.2]) == [None, 0.2]
    lo, hi = wilson(0, 12)
    assert lo == 0 and abs(hi - 0.2425) < 1e-3, hi
    assert abs(signflip_p([1] * 6) - 2 / 64) < 1e-12
    assert verdict((-0.05, 0.08)) .startswith("similar") and verdict((-0.05, 0.2)) == "inconclusive"
    assert verdict((0.01, 0.2)) == "interval excludes 0" and verdict((0, 0), hard=True).startswith("hard")
    assert verdict((0.0, 0.0)).startswith("degenerate") and verdict((0.5, 0.5)).startswith("degenerate")

    def effect(m, p, w, s):
        if s == "penalised":
            return 0.02
        if m == "Qwen 3.8":
            return {"W1": 0.05, "W2": 0.1, "W3": 0.8, "W4": 0.85, "W5": 0.1}[w]
        return 0.05 if m == "Qwen 3.5" else 0.3

    fake_manifest = dict(sha256="abc", hypotheses_sha256="0" * 64, code_sha256={"analysis.py": "0" * 64})
    res = analyse(synthetic(effect, 1), tmp / "effect", fake_manifest, {"analysis.py": "1" * 64}, run="selftest-effect")
    pv = res["provenance"]
    assert pv["code_changed"] == ["analysis.py"] and pv["hypotheses_frozen"] != pv["hypotheses_now"]
    assert "differs from the frozen hash" in (tmp / "effect" / "ANALYSIS.md").read_text()
    se = {(r["who"], r["presentation"]): r for r in res["secondary_E"]}
    wm = {(r["model"], r["presentation"], r["contrast"]): r for r in res["within_model"]}
    md = {(r["pair"], r["presentation"], r["contrast"]): r for r in res["model_differences"]}
    for r in res["primary"]:
        assert r["p"] < 0.001 and r["reject_holm"] and r["estimate"] > 0.5 and r["ci"][0] > 0.2, r
        assert r["verdict"] == "interval excludes 0"
    for p in PRES:
        e = se[("Qwen 3.8", p)]
        assert e["p"] < 0.001 and e["estimate"] > 0.5 and e["ci"][0] > 0.2 and e["signs"]["+"] >= 5
        assert wm[("Qwen 3.8", p, "priority")]["p"] < 0.05 and wm[("Qwen 3.8", p, "priority")]["estimate"] < -0.4
        assert md[("3.8-3.5", p, "exception_pooled")]["p"] < 0.001 and se[("3.6-3.5", p)]["p"] > 0.01
        assert ("Qwen 3.5", p) in {(x["model"], x["presentation"]) for x in res["low_rate"]}
        assert se[("Qwen 3.5", p)]["verdict"].startswith("hard")
        assert ("Qwen 3.6", p) not in {(x["model"], x["presentation"]) for x in res["low_rate"]}
    assert sum(r.get("failed", 0) + r.get("empty", 0) + r.get("truncated", 0) for r in res["nonvalid"]) > 0
    print("selftest effect: planted E / priority effects, primary contrast (Holm), low-rate note, hash diff detected")

    # null smoke test (the real calibration is `calibrate`): p-values should not be anti-conservative
    ps_primary, ps_perm = [], []
    for seed in range(20):
        res = analyse(synthetic(lambda *a: 0.3, 100 + seed), tmp / "null", {}, {}, run="selftest-null")
        ps_primary += [r["p"] for r in res["primary"]]
        ps_perm += [r["p"] for r in res["secondary_E"] if r["p"] is not None]
        assert not res["low_rate"]
    fp = np.mean(np.array(ps_perm) < 0.05)
    print(f"selftest null (smoke, 20 datasets): P(p<0.05) secondary E {fp:.3f} (n={len(ps_perm)}), "
          f"primary {np.mean(np.array(ps_primary) < 0.05):.3f} (n={len(ps_primary)})")
    assert fp <= 0.09, fp
    print(f"selftest passed; reports in {tmp}")


# ---------------------------------------------------------------- calibration on synthetic datasets

def _expit(x):
    return 1 / (1 + np.exp(-x))


def _logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


SHAPE = (len(MODELS), len(PRES), len(WORDS), len(W.SCORES), 6)  # [model, presentation, wording, scores, task]
MI, PI, WI = ({m: i for i, m in enumerate(MODELS)}, {p: i for i, p in enumerate(PRES)},
              {w: i for i, w in enumerate(WORDS)})


def _base(levels, penalised=0.03):
    """levels[model][presentation] -> rewarded rate at every wording and task."""
    P = np.zeros(SHAPE)
    for m, row in levels.items():
        for p, v in row.items():
            P[MI[m], PI[p], :, 0, :] = v
    P[:, :, :, 1, :] = penalised
    return P


MODERATE = {"Qwen 3.5": {"rl/direct": 0.2, "rl/quoted": 0.25, "anchor": 0.3},
            "Qwen 3.6": {"rl/direct": 0.3, "rl/quoted": 0.35, "anchor": 0.4},
            "Qwen 3.8": {"rl/direct": 0.35, "rl/quoted": 0.45, "anchor": 0.5}}


def _sparse(rng):
    lv = {"Qwen 3.5": {"rl/direct": 0.0, "rl/quoted": 0.0, "anchor": 0.01},
          "Qwen 3.6": {"rl/direct": 0.0, "rl/quoted": 0.02, "anchor": 0.03},
          "Qwen 3.8": {"rl/direct": 0.01, "rl/quoted": 0.05, "anchor": 0.05}}
    P = _base(lv, penalised=0.01)
    P[..., 0, :] *= np.array([0, 0, 0.5, 1, 1, 1])  # two tasks never adopt
    return P


def _task_het(rng):
    task = rng.normal(0, 1.5, 6)
    tm = rng.normal(0, 0.7, (3, 1, 1, 1, 6))
    lp = _logit(_base(MODERATE))
    P = _base(MODERATE)
    P[..., 0, :] = _expit(lp[..., 0, :] + task + tm[..., 0, :])
    return P


def _nuisance(rng):
    """Equal exception effect (+0.25) and phrasing effect (+0.1) in every model, model level differences:
    E(3.8) - E(3.5) = 0 and E(3.6) - E(other) = 0, but each model's own E = 0.25."""
    P = _base({"Qwen 3.5": dict.fromkeys(PRES, 0.1), "Qwen 3.6": dict.fromkeys(PRES, 0.3),
               "Qwen 3.8": dict.fromkeys(PRES, 0.35)})
    for w, add in (("W2", 0.1), ("W3", 0.25), ("W4", 0.35), ("W5", 0.35)):
        P[:, :, WI[w], 0, :] += add
    return P


def _planted(delta, base=0.2):
    def make(rng):
        P = _base({m: dict.fromkeys(PRES, base) for m in MODELS})
        for p in PRIMARY_PRES:
            for w in ("W3", "W4"):
                P[MI["Qwen 3.8"], PI[p], WI[w], 0, :] += delta
        return P
    return make


SCENARIOS = {  # name: (description, rate generator, within-cell logit sd)
    "a_moderate": ("moderate base rates (0.20-0.50 by model x presentation), no wording effects",
                   lambda rng: _base(MODERATE), 0.0),
    "b_sparse": ("sparse: rewarded rates 0-5% (2 of 6 tasks never adopt; 3.5 rl/direct and rl/quoted all zero), "
                 "many all-zero cells", _sparse, 0.0),
    "c_task_het": ("task heterogeneity: per-task logit offsets N(0, 1.5) plus task x model N(0, 0.7), redrawn per "
                   "dataset; no wording effects", _task_het, 0.0),
    "d_cluster": ("cluster correlation: moderate base rates plus a per-cell logit effect N(0, 1) shared by the "
                  "cell's 2 samples (prompt-level variation treated as random); no wording effects on average",
                  lambda rng: _base(MODERATE), 1.0),
    "e_nuisance": ("composite null: every model has E = +0.25 and a phrasing effect, models differ in level; "
                   "E(3.8) - E(3.5) = 0", _nuisance, 0.0),
    "p_+0.30": ("power: base 0.20 everywhere; 3.8 W3/W4 +0.30 in anchor and rl/quoted", _planted(0.30), 0.0),
    "p_+0.20": ("power: base 0.20 everywhere; 3.8 W3/W4 +0.20 in anchor and rl/quoted", _planted(0.20), 0.0),
    "p_+0.30_sparse": ("power, sparse: base 0.02 everywhere; 3.8 W3/W4 +0.30 in anchor and rl/quoted",
                       _planted(0.30, 0.02), 0.0),
}


def _true_E(P, m, p):
    r = P[MI[m], PI[p], :, 0, :]
    return float(np.mean(0.5 * ((r[WI["W3"]] - r[WI["W1"]]) + (r[WI["W4"]] - r[WI["W2"]]))))


def _truths(P, label):
    """True value of each tested E quantity, from the generating rates (on average over cell effects)."""
    if label.startswith("primary|"):
        p = label.split("|")[1]
        return _true_E(P, *PRIMARY_PAIR[:1], p) - _true_E(P, PRIMARY_PAIR[1], p)
    parts = label.split("|")
    if parts[0] == "E":
        return _true_E(P, parts[1], parts[2])
    return _true_E(P, parts[1], parts[3]) - _true_E(P, parts[2], parts[3])  # Ediff|a|b|p


def calibrate(out: Path, n_sets: int = 1000, n_perm: int = 2000, n_boot: int = 1000):
    tasks = [f"T{i}" for i in range(6)]
    t0, results = time.time(), {}
    for si, (name, (desc, gen, sd)) in enumerate(SCENARIOS.items()):
        rng = np.random.default_rng([SEED, 7, si])
        rec = defaultdict(list)
        for i in range(n_sets):
            P = np.clip(gen(rng), 0, 1)
            Pc = _expit(_logit(P) + rng.normal(0, sd, SHAPE)) * (P > 0) if sd else P
            n = 2 - rng.binomial(2, 0.03, SHAPE)  # 3% non-valid completions
            k = rng.binomial(n, Pc)
            counts = Counts.from_arrays(k, n, tasks)
            kw = dict(n_perm=n_perm, seed=SEED + 1000 * si + i)
            prim = primary(counts, tasks, list(MODELS), n_boot=n_boot, **kw)
            sec = secondary_E(counts, tasks, list(MODELS), n_boot=0, **kw)
            truth_p = [_truths(P, r["label"]) for r in prim]
            rec["prim_p"].append([r["p"] if r["p"] is not None else 1.0 for r in prim])
            rec["prim_holm"].append([bool(r["reject_holm"]) for r in prim])
            rec["prim_sf"].append([r.get("p_signflip") if r.get("p_signflip") is not None else 1.0 for r in prim])
            rec["prim_truth"].append(truth_p)
            rec["prim_cover"].append([r["ci"] is not None and r["ci"][0] - 1e-9 <= t <= r["ci"][1] + 1e-9
                                      for r, t in zip(prim, truth_p)])
            rec["prim_similar"].append([r["ci"] is not None and verdict(r["ci"]).startswith("similar") for r in prim])
            low = {(x["model"], x["presentation"]) for x in low_rate(cell_table(counts, list(MODELS)), list(MODELS))}
            rec["prim_similar_guard"].append([verdict(r["ci"], all((m, r["presentation"]) in low for m in PRIMARY_PAIR))
                                              .startswith("similar") for r in prim])
            rec["prim_hard"].append([all((m, r["presentation"]) in low for m in PRIMARY_PAIR) for r in prim])
            rec["prim_ci_excl0"].append([r["ci"] is not None and (r["ci"][0] > 0 or r["ci"][1] < 0) for r in prim])
            rec["prim_undefined"].append([r["p"] is None for r in prim])
            nulls = [(r["p"] if r["p"] is not None else 1.0) < ALPHA for r in sec if abs(_truths(P, r["label"])) < 1e-9]
            rec["sec_null_rej"].append(np.mean(nulls) if nulls else np.nan)
            rec["sec_null_n"].append(len(nulls))
        results[name] = {k: np.array(v) for k, v in rec.items()}
        print(f"calibrate {name}: {n_sets} datasets, {time.time() - t0:.0f}s elapsed", flush=True)
    out.write_text(calibration_report(results, n_sets, n_perm, n_boot, time.time() - t0))
    print(f"wrote {out}")
    return results


def _rate(x):
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    r = float(x.mean()) if len(x) else float("nan")
    return r, (float(x.std(ddof=1) / math.sqrt(len(x))) if len(x) > 1 else float("nan"))


def _fr(x):
    r, se = _rate(x)
    return "n/a" if math.isnan(r) else f"{r:.3f} ± {se:.3f}"


def calibration_report(R, n_sets, n_perm, n_boot, secs) -> str:
    L = ["# Request wording: calibration of the amended analysis (synthetic data only)", "",
         f"Generated by `.venv/bin/python designs/wording/analysis.py calibrate designs/wording/CALIBRATION.md "
         f"{n_sets}` ({secs / 60:.1f} min). **No main-run data were used**; every dataset is synthetic with the real "
         "design shape: 6 tasks × 5 wordings × 3 presentations × 2 score directions × 3 models × 2 samples "
         "(1,080 conversations), 3% of completions non-valid at random (so some cells have n = 1 or 0).", "",
         f"- **{n_sets} datasets per scenario.** Rates are proportions ± Monte Carlo standard error.",
         f"- **Reduced resampling inside the harness, for speed:** {n_perm} permutation draws per test (the real "
         f"analysis uses {N_PERM}) and {n_boot} bootstrap draws for the primary intervals (real: {N_BOOT}). The "
         "secondary tests are run without intervals here. The code path is otherwise the one the real analysis uses "
         "(`primary`, `secondary_E`, `composite`, `Diff`).",
         "- **Primary raw** = P(p < 0.05) for each primary test (anchor, rl/quoted). **Holm FWER** = P(at least one "
         "of the two rejected after Holm at 0.05). **Sign-flip** = the task-level robustness p < 0.05. **Secondary "
         "E** = mean over the secondary E tests whose true value is 0 in that scenario (E per model × presentation, "
         "E(3.6) − E(3.5), E(3.6) − E(3.8), E(3.8) − E(3.5) in rl/direct; 16 tests, fewer where some are non-null) "
         "of P(p < 0.05), with the Monte Carlo SE taken over datasets.",
         "- **Coverage** = P(95% bootstrap interval contains the true E(3.8) − E(3.5)). **'Similar'** = P(interval "
         "within ±10 pp), i.e. how often the equivalence rule would call the two models similar; 'with low-rate "
         "guard' applies the report's rule that a contrast whose models are both low-rate (≤ 2/12 at every "
         "wording) is 'hard to estimate', never 'similar'.", "",
         "## Scenarios", ""]
    for name, (desc, _, _) in SCENARIOS.items():
        L.append(f"- `{name}`: {desc}")
    L += ["", "## False-positive rates (true E(3.8) − E(3.5) = 0)", "",
          "| scenario | primary raw: anchor | primary raw: rl/quoted | primary Holm FWER | sign-flip p<0.05 (either) | "
          "secondary E (mean over null tests) | interval coverage (anchor / rl/quoted) | interval excludes 0 (either) "
          "| 'similar', raw rule / with low-rate guard (anchor / rl/quoted) | flagged hard to estimate (anchor / "
          "rl/quoted) |", "|---|---|---|---|---|---|---|---|---|---|"]
    anti = []
    for name, r in R.items():
        if name.startswith("p_"):
            continue
        pr = r["prim_p"] < ALPHA
        fw = r["prim_holm"].any(axis=1)
        for j, p in enumerate(PRIMARY_PRES):
            rate, se = _rate(pr[:, j])
            if rate - 2 * se > ALPHA:
                anti.append(f"{name} ({p}: {rate:.3f} ± {se:.3f})")
        L.append(f"| {name} | {_fr(pr[:, 0])} | {_fr(pr[:, 1])} | {_fr(fw)} | {_fr((r['prim_sf'] < ALPHA).any(axis=1))} "
                 f"| {_fr(r['sec_null_rej'])} | {_rate(r['prim_cover'][:, 0])[0]:.3f} / {_rate(r['prim_cover'][:, 1])[0]:.3f} "
                 f"| {_fr(r['prim_ci_excl0'].any(axis=1))} | {_rate(r['prim_similar'][:, 0])[0]:.3f} / "
                 f"{_rate(r['prim_similar'][:, 1])[0]:.3f} / {_rate(r['prim_similar_guard'][:, 0])[0]:.3f} / "
                 f"{_rate(r['prim_similar_guard'][:, 1])[0]:.3f} | {_rate(r['prim_hard'][:, 0])[0]:.3f} / "
                 f"{_rate(r['prim_hard'][:, 1])[0]:.3f} |")
    L += ["", "## Power (planted E(3.8) − E(3.5) in anchor and rl/quoted)", "",
          "| scenario | true contrast | raw reject: anchor | raw reject: rl/quoted | Holm reject: anchor | "
          "Holm reject: rl/quoted | Holm: both | interval coverage (anchor / rl/quoted) | 'similar' wrongly claimed "
          "(either) | secondary E FPR (null tests) |", "|---|---|---|---|---|---|---|---|---|---|"]
    for name, r in R.items():
        if not name.startswith("p_"):
            continue
        pr, hr = r["prim_p"] < ALPHA, r["prim_holm"]
        L.append(f"| {name} | {r['prim_truth'][0, 0]:+.2f} | {_fr(pr[:, 0])} | {_fr(pr[:, 1])} | {_fr(hr[:, 0])} | "
                 f"{_fr(hr[:, 1])} | {_fr(hr.all(axis=1))} | {_rate(r['prim_cover'][:, 0])[0]:.3f} / "
                 f"{_rate(r['prim_cover'][:, 1])[0]:.3f} | {_fr(r['prim_similar'].any(axis=1))} | "
                 f"{_fr(r['sec_null_rej'])} |")
    L += ["", "## Verdict", ""]
    if anti:
        L.append("**Anti-conservative primary test** (raw rejection rate more than 2 MC SE above 0.05) in: "
                 + "; ".join(anti) + ". See the notes below; this is stated in the ANALYSIS.md header.")
    else:
        L.append("The primary permutation test is not anti-conservative (raw rate within 2 MC SE of, or below, 0.05) "
                 "in any scenario.")
    L += ["", "AUTO-GENERATED TABLES END; notes follow.", ""]
    return "\n".join(L)


if __name__ == "__main__":
    if sys.argv[1:2] == ["selftest"] and len(sys.argv) == 3:
        selftest(Path(sys.argv[2]))
    elif sys.argv[1:2] == ["calibrate"] and len(sys.argv) in (3, 4):
        calibrate(Path(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) == 4 else 1000)
    else:
        raise SystemExit(__doc__)
