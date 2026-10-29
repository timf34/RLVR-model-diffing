"""Block-level paired inference for the overnight batch (DESIGN.md "Inference").

Data model
----------
A *panel* holds the labels of one experiment:
    panel = {block_id: {"stratum": subtype_or_direction, "cells": {cellkey: label}}}
    cellkey = (outcome, model, frame, permission, cond)
        outcome    "violation" (A) | "source" | "target" (B)
        permission "na" (A) | "forbidden" | "permitted" | "none" (B no-history)
        cond       "none" | "-0.50" | "+0.00" | "+0.05" | "+0.50"
    label = "violates" | "complies" | "unclear" | "nonvalid"   (absent key = not generated)

A *contrast* is a linear combination of cells, computed within each block first (one generation per cell, so a block
value is e.g. y(+0.50) - y(+0.05) in {-1, 0, 1}). A block whose contrast touches a non-valid, absent or unclear cell
is missing for that contrast (missingness is reported by reason). The estimate is the equal-weighted mean of stratum
means (A family = mean of subtype means; B = mean of direction means).

Test: stratified sign-flip permutation of block values (flip each block's sign independently; the statistic keeps
the stratum weights). Exact enumeration when at most EXACT_MAX blocks are non-zero (zero blocks do not change the
statistic), else Monte Carlo with MC_DRAWS draws and a fixed seed; p = (1 + #{|T*| >= |T|}) / (draws + 1).
CI: cluster bootstrap that resamples blocks within strata (BOOT_REPS, percentile). If the bootstrap interval has zero
width (e.g. every cell 0/n), it is replaced by a block-level bound: with N blocks and no deviating block observed,
the chance a block deviates is at most 1 - 0.05^(1/N) (one-sided 95%, Clopper-Pearson for 0/N), so the contrast lies
in [est - ub*(est - min), est + ub*(max - est)], where min/max are the most extreme values a block can take.
Never a zero-width CI.
Holm over the 8 primary tests. Unclear sensitivity: unclear -> violates, unclear -> complies, and worst-case
bounds (unclear set to whichever value pushes the contrast up / down).
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field

import numpy as np

EXACT_MAX = 18
MC_DRAWS = 20_000
BOOT_REPS = 4000
BASE_SEED = 20261029
ALPHA = 0.05

FOCUS, COMPARE = "Qwen 3.8", "Qwen 3.5"
MODELS = (FOCUS, COMPARE)
FRAMES = ("episode", "ordinary")
CONDS = ("none", "-0.50", "+0.00", "+0.05", "+0.50")
GAP_OF = {"-0.50": -0.5, "+0.00": 0.0, "+0.05": 0.05, "+0.50": 0.5}
FAMILIES = {"formatting": ("title", "signoff", "emdash", "bullets", "emoji"),
            "reserved_actions": ("send", "publish", "submit"),
            "factual_reporting": ("limitation", "certainty", "status")}
FAMILY_SHORT = {"formatting": "formatting", "reserved_actions": "reserved actions",
                "factual_reporting": "factual reporting"}
DIRECTIONS = ("title_to_limitation", "limitation_to_title", "emdash_to_certainty", "certainty_to_emdash",
              "signoff_to_send", "send_to_signoff")
PERMISSIONS = ("forbidden", "permitted")

VALUE = {"violates": 1.0, "complies": 0.0}


def cond_of(history: str | None, gap) -> str:
    if history in (None, "none") or gap is None:
        return "none"
    g = round(float(gap), 2)
    return "+0.00" if g == 0 else f"{g:+.2f}"


def ck(outcome="violation", model=FOCUS, frame="episode", permission="na", cond="+0.50") -> tuple:
    return (outcome, model, frame, permission, cond)


def cell_dict(key: tuple) -> dict:
    return dict(zip(("outcome", "model", "frame", "permission", "cond"), key))


def seed_for(name: str) -> int:
    return (int(hashlib.sha256(name.encode()).hexdigest()[:8], 16) ^ BASE_SEED) % (2**31)


# ----------------------------------------------------------------------------------------------------------------
# intervals for single rates

def upper_bound(n: int, alpha: float = ALPHA) -> float:
    """One-sided (1-alpha) upper bound for a rate when 0 of n independent blocks show the event."""
    return 1.0 - alpha ** (1.0 / n) if n > 0 else 1.0


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def holm(ps: dict) -> dict:
    items = sorted((p, k) for k, p in ps.items() if p is not None and not math.isnan(p))
    out, run, m = {}, 0.0, len(items)
    for i, (p, k) in enumerate(items):
        run = max(run, min(1.0, p * (m - i)))
        out[k] = run
    return out


# ----------------------------------------------------------------------------------------------------------------
# contrasts

@dataclass(frozen=True)
class Contrast:
    id: str
    name: str
    terms: tuple            # ((coef, cellkey), ...)
    strata: tuple           # stratum names (subtypes or directions) averaged with equal weight
    primary: bool = False
    group: str = ""         # family / direction / "B" (for tables)
    kind: str = ""          # short tag for tables, e.g. "gap_effect", "frame_did"
    meta: tuple = field(default_factory=tuple)   # extra (key, value) pairs for tables

    def bounds(self) -> tuple[float, float]:
        lo = sum(c for c, _ in self.terms if c < 0)
        hi = sum(c for c, _ in self.terms if c > 0)
        return lo, hi


def block_values(panel: dict, contrast: Contrast, unclear: str = "missing") -> dict:
    """{stratum: {"values": np.array (non-missing), "blocks": [...], "missing": {reason: n}, "planned": n}}

    unclear: "missing" | "violates" | "complies" | "up" | "down" (up/down = worst case for the contrast)."""
    out = {s: {"values": [], "blocks": [], "missing": {"absent": 0, "nonvalid": 0, "unclear": 0}, "planned": 0}
           for s in contrast.strata}
    for bid, b in panel.items():
        s = b["stratum"]
        if s not in out:
            continue
        o = out[s]
        o["planned"] += 1
        total, reason = 0.0, None
        for coef, key in contrast.terms:
            lab = b["cells"].get(key)
            if lab is None:
                reason = reason or "absent"
                continue
            if lab == "nonvalid":
                reason = "nonvalid" if reason in (None, "unclear") else reason
                continue
            if lab == "unclear":
                if unclear == "missing":
                    reason = reason or "unclear"
                    continue
                v = {"violates": 1.0, "complies": 0.0, "up": 1.0 if coef > 0 else 0.0,
                     "down": 0.0 if coef > 0 else 1.0}[unclear]
            else:
                v = VALUE[lab]
            total += coef * v
        if reason:
            o["missing"][reason] += 1
        else:
            o["values"].append(total)
            o["blocks"].append(bid)
    for o in out.values():
        o["values"] = np.asarray(o["values"], float)
    return out


def _weights(bv: dict) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Flattened values and weights (equal weight per stratum with data, equal within stratum)."""
    used = [s for s, o in bv.items() if len(o["values"])]
    vals, w = [], []
    for s in used:
        n = len(bv[s]["values"])
        vals.append(bv[s]["values"])
        w.append(np.full(n, 1.0 / (len(used) * n)))
    if not used:
        return np.zeros(0), np.zeros(0), used
    return np.concatenate(vals), np.concatenate(w), used


def estimate(bv: dict) -> float:
    v, w, used = _weights(bv)
    return float(np.dot(v, w)) if used else float("nan")


def signflip_p(bv: dict, draws: int = MC_DRAWS, seed: int = BASE_SEED, exact_max: int = EXACT_MAX) -> tuple:
    """Two-sided stratified sign-flip p-value. Returns (p, method)."""
    v, w, used = _weights(bv)
    a = v * w
    a = a[np.abs(a) > 1e-15]
    t = abs(a.sum())
    k = len(a)
    if k == 0 or t < 1e-12:
        return 1.0, "sign-flip (no non-zero blocks)" if k == 0 else "sign-flip (statistic 0)"
    if k <= exact_max:
        idx = np.arange(2 ** k, dtype=np.int64)[:, None]
        signs = 1.0 - 2.0 * ((idx >> np.arange(k)) & 1)
        stat = np.abs(signs @ a)
        return float(np.mean(stat >= t - 1e-10)), f"exact sign-flip (2^{k})"
    rng = np.random.default_rng(seed)
    hits = 0
    done = 0
    while done < draws:
        m = min(5000, draws - done)
        signs = rng.integers(0, 2, size=(m, k), dtype=np.int8) * 2 - 1
        hits += int(np.sum(np.abs(signs @ a) >= t - 1e-10))
        done += m
    return (1 + hits) / (draws + 1), f"Monte Carlo sign-flip ({draws} draws)"


def bootstrap_ci(bv: dict, reps: int = BOOT_REPS, seed: int = BASE_SEED) -> tuple[float, float] | None:
    used = [s for s, o in bv.items() if len(o["values"])]
    if not used:
        return None
    rng = np.random.default_rng(seed)
    tot = np.zeros(reps)
    for s in used:
        x = bv[s]["values"]
        idx = rng.integers(0, len(x), size=(reps, len(x)))
        tot += x[idx].mean(axis=1)
    tot /= len(used)
    return float(np.percentile(tot, 2.5)), float(np.percentile(tot, 97.5))


def evaluate(panel: dict, c: Contrast, draws: int = MC_DRAWS, reps: int = BOOT_REPS) -> dict:
    bv = block_values(panel, c)
    est = estimate(bv)
    seed = seed_for(c.id)
    n_used = sum(len(o["values"]) for o in bv.values())
    res = dict(id=c.id, name=c.name, primary=c.primary, group=c.group, kind=c.kind, **dict(c.meta),
               terms=[[coef, cell_dict(k)] for coef, k in c.terms], strata=list(c.strata),
               estimate=None if math.isnan(est) else est, n_blocks_planned=sum(o["planned"] for o in bv.values()),
               n_blocks_used=n_used,
               n_missing={r: sum(o["missing"][r] for o in bv.values()) for r in ("absent", "nonvalid", "unclear")},
               strata_used=[s for s, o in bv.items() if len(o["values"])],
               per_stratum={s: dict(mean=(float(o["values"].mean()) if len(o["values"]) else None),
                                    n_used=len(o["values"]), n_planned=o["planned"], missing=o["missing"],
                                    n_pos=int(np.sum(o["values"] > 0)), n_neg=int(np.sum(o["values"] < 0)))
                            for s, o in bv.items()})
    if n_used == 0:
        res.update(ci=None, ci_method="no data", p=None, p_method="no data", degenerate=True)
        return res
    p, pm = signflip_p(bv, draws=draws, seed=seed)
    ci = bootstrap_ci(bv, reps=reps, seed=seed + 1)
    degenerate = ci is None or ci[1] - ci[0] < 1e-12
    if degenerate:
        lo_v, hi_v = c.bounds()
        ub = upper_bound(n_used)
        ci = (est - ub * (est - lo_v), est + ub * (hi_v - est))
        cm = (f"zero-variation bound: no block deviated from {est:+.3f} in {n_used} blocks; one-sided 95% "
              f"block-level bound 1-0.05^(1/{n_used}) = {ub:.3f} on each side")
    else:
        cm = f"cluster bootstrap, blocks resampled within strata ({reps} reps, percentile)"
    sens = {}
    for mode in ("violates", "complies", "up", "down"):
        e = estimate(block_values(panel, c, unclear=mode))
        sens[mode] = None if math.isnan(e) else e
    res.update(ci=list(ci), ci_method=cm, p=p, p_method=pm, degenerate=degenerate,
               sens_unclear_violates=sens["violates"], sens_unclear_complies=sens["complies"],
               sens_bounds=[sens["down"], sens["up"]])
    return res


# ----------------------------------------------------------------------------------------------------------------
# cell rates

def cell_summary(panel: dict, key: tuple, strata: tuple, reps: int = BOOT_REPS) -> dict:
    """Rate of `violates` in one cell, equal-weighted over strata (one generation per block)."""
    per = {}
    for s in strata:
        per[s] = dict(k=0, n=0, unclear=0, nonvalid=0, absent=0, planned=0, vals=[])
    for b in panel.values():
        s = b["stratum"]
        if s not in per:
            continue
        o = per[s]
        o["planned"] += 1
        lab = b["cells"].get(key)
        if lab is None:
            o["absent"] += 1
        elif lab == "nonvalid":
            o["nonvalid"] += 1
        elif lab == "unclear":
            o["unclear"] += 1
        else:
            o["n"] += 1
            o["k"] += int(lab == "violates")
            o["vals"].append(VALUE[lab])
    used = [s for s in strata if per[s]["n"]]
    k = sum(per[s]["k"] for s in strata)
    n = sum(per[s]["n"] for s in strata)
    out = dict(**cell_dict(key), strata=list(strata), k=k, n=n,
               n_unclear=sum(per[s]["unclear"] for s in strata), n_nonvalid=sum(per[s]["nonvalid"] for s in strata),
               n_absent=sum(per[s]["absent"] for s in strata), n_planned=sum(per[s]["planned"] for s in strata),
               per_stratum={s: dict(k=per[s]["k"], n=per[s]["n"], unclear=per[s]["unclear"],
                                    nonvalid=per[s]["nonvalid"]) for s in strata})
    if not used:
        out.update(rate=None, lo=None, hi=None, interval="no data")
        return out
    rate = float(np.mean([per[s]["k"] / per[s]["n"] for s in used]))
    if k == 0:
        lo, hi, kind = 0.0, upper_bound(n), "one-sided 95% upper bound, block level (0 events)"
    elif k == n:
        lo, hi, kind = 1.0 - upper_bound(n), 1.0, "one-sided 95% lower bound, block level (all events)"
    elif len(used) == 1:
        lo, hi = wilson(k, n)
        kind = "Wilson 95% (one generation per block)"
    else:
        bv = {s: {"values": np.asarray(per[s]["vals"])} for s in used}
        lo, hi = bootstrap_ci(bv, reps=reps, seed=seed_for(repr(key) + repr(strata)))
        kind = "cluster bootstrap 95%, blocks within strata"
    # sensitivity: unclear as violates / complies
    def alt(as_viol: bool):
        rs = []
        for s in strata:
            o = per[s]
            nn = o["n"] + o["unclear"]
            if nn:
                rs.append((o["k"] + (o["unclear"] if as_viol else 0)) / nn)
        return float(np.mean(rs)) if rs else None
    out.update(rate=rate, lo=lo, hi=hi, interval=kind, rate_unclear_violates=alt(True),
               rate_unclear_complies=alt(False))
    return out


# ----------------------------------------------------------------------------------------------------------------
# contrast definitions

def _gap_terms(outcome, model, frame, perm, hi="+0.50", lo="+0.05", sign=1.0):
    return ((sign, (outcome, model, frame, perm, hi)), (-sign, (outcome, model, frame, perm, lo)))


def contrasts_A(model: str = FOCUS, primary: bool = True, families: dict = FAMILIES) -> list[Contrast]:
    """A1-A3 (episode gap effect +0.50 vs +0.05) and A4-A6 (episode minus ordinary) per family."""
    out = []
    tag = "" if model == FOCUS else f"[{model}] "
    for i, (fam, subs) in enumerate(families.items()):
        ep = _gap_terms("violation", model, "episode", "na")
        od = _gap_terms("violation", model, "ordinary", "na", sign=-1.0)
        out.append(Contrast(f"{tag}A{i + 1}", f"{FAMILY_SHORT[fam]}: episode, rate(+0.50) - rate(+0.05)", ep, subs,
                            primary and model == FOCUS, fam, "gap_effect", (("model", model), ("frame", "episode"))))
        out.append(Contrast(f"{tag}A{i + 4}", f"{FAMILY_SHORT[fam]}: [episode(+0.50 - +0.05)] - "
                            f"[ordinary(+0.50 - +0.05)]", ep + od, subs, primary and model == FOCUS, fam,
                            "frame_did", (("model", model), ("frame", "episode-ordinary"))))
    return sorted(out, key=lambda c: c.id)


def _D(outcome, model, frame, sign=1.0):
    return (_gap_terms(outcome, model, frame, "forbidden", "+0.50", "+0.00", sign)
            + _gap_terms(outcome, model, frame, "permitted", "+0.50", "+0.00", -sign))


def contrasts_B(model: str = FOCUS, primary: bool = True, directions=DIRECTIONS, outcome="target") -> list[Contrast]:
    tag = "" if (model == FOCUS and outcome == "target") else f"[{model}{'' if outcome == 'target' else ', ' + outcome}] "
    prim = primary and model == FOCUS and outcome == "target"
    b1 = Contrast(f"{tag}B1", f"{outcome.upper()}: D(episode) = [T(forbidden,+0.50) - T(forbidden,0)] - "
                  f"[T(permitted,+0.50) - T(permitted,0)]", _D(outcome, model, "episode"), tuple(directions), prim,
                  "B", "perm_did", (("model", model), ("frame", "episode"), ("outcome", outcome)))
    b2 = Contrast(f"{tag}B2", f"{outcome.upper()}: D(episode) - D(ordinary)",
                  _D(outcome, model, "episode") + _D(outcome, model, "ordinary", -1.0), tuple(directions), prim,
                  "B", "perm_frame_ddd", (("model", model), ("frame", "episode-ordinary"), ("outcome", outcome)))
    return [b1, b2]


def model_diff(c3: Contrast, c5: Contrast, cid: str) -> Contrast:
    terms = tuple(c3.terms) + tuple((-coef, k) for coef, k in c5.terms)
    return Contrast(cid, f"{c3.name} :: Qwen 3.8 minus Qwen 3.5", terms, c3.strata, False, c3.group,
                    c3.kind + "_model_diff", (("model", "3.8-3.5"),) + tuple(m for m in c3.meta if m[0] != "model"))


def secondary_A(families: dict = FAMILIES, conds_present: set | None = None) -> list[Contrast]:
    out = []
    for model in MODELS:
        if model != FOCUS:
            out += contrasts_A(model, primary=False, families=families)
        for fam, subs in families.items():
            for frame in FRAMES:
                if frame == "ordinary":
                    out.append(Contrast(f"[{model}] {fam}: ordinary gap", f"{FAMILY_SHORT[fam]}: ordinary, "
                               "rate(+0.50) - rate(+0.05)", _gap_terms("violation", model, frame, "na"), subs, False,
                               fam, "gap_effect", (("model", model), ("frame", frame))))
                for hi, lo, kind in (("+0.50", "+0.00", "gap_vs_tie"), ("+0.00", "-0.50", "tie_vs_neg"),
                                     ("none", "+0.00", "nohist_vs_tie")):
                    out.append(Contrast(f"[{model}] {fam}: {frame} {hi} vs {lo}",
                               f"{FAMILY_SHORT[fam]}: {frame}, rate({hi}) - rate({lo})",
                               _gap_terms("violation", model, frame, "na", hi, lo), subs, False, fam, kind,
                               (("model", model), ("frame", frame))))
            # per subtype
            for s in subs:
                for frame in FRAMES:
                    out.append(Contrast(f"[{model}] {s}: {frame} gap", f"{s}: {frame}, rate(+0.50) - rate(+0.05)",
                               _gap_terms("violation", model, frame, "na"), (s,), False, s, "subtype_gap_effect",
                               (("model", model), ("frame", frame), ("family", fam))))
                    out.append(Contrast(f"[{model}] {s}: {frame} none vs tie", f"{s}: {frame}, rate(none) - "
                               "rate(+0.00)", _gap_terms("violation", model, frame, "na", "none", "+0.00"), (s,),
                               False, s, "subtype_nohist_vs_tie", (("model", model), ("frame", frame), ("family", fam))))
                out.append(Contrast(f"[{model}] {s}: frame DiD", f"{s}: [episode(+0.50 - +0.05)] - "
                           "[ordinary(+0.50 - +0.05)]", _gap_terms("violation", model, "episode", "na")
                           + _gap_terms("violation", model, "ordinary", "na", sign=-1.0), (s,), False, s,
                           "subtype_frame_did", (("model", model), ("frame", "episode-ordinary"), ("family", fam))))
    # model comparison of the primary contrasts
    p38 = {c.id: c for c in contrasts_A(FOCUS, False, families)}
    p35 = {c.id.split("] ")[1]: c for c in contrasts_A(COMPARE, False, families)}
    for cid, c in p38.items():
        out.append(model_diff(c, p35[cid], f"[3.8-3.5] {cid}"))
    return out


def secondary_B(directions=DIRECTIONS) -> list[Contrast]:
    out = []
    out += contrasts_B(COMPARE, primary=False, directions=directions)
    for model in MODELS:
        out += contrasts_B(model, primary=False, directions=directions, outcome="source")
    p38 = {c.id: c for c in contrasts_B(FOCUS, False, directions)}
    p35 = {c.id.split("] ")[1]: c for c in contrasts_B(COMPARE, False, directions)}
    for cid, c in p38.items():
        out.append(model_diff(c, p35[cid], f"[3.8-3.5] {cid}"))
    for model in MODELS:
        for outcome in ("target", "source"):
            for frame in FRAMES:
                for perm in PERMISSIONS:
                    terms = _gap_terms(outcome, model, frame, perm, "+0.50", "+0.00")
                    out.append(Contrast(f"[{model}] {outcome} {frame} {perm}: +0.50 vs 0",
                               f"{outcome.upper()}: {frame}, {perm}, rate(+0.50) - rate(0)", terms, tuple(directions),
                               False, "B", "simple_change", (("model", model), ("frame", frame),
                                                              ("permission", perm), ("outcome", outcome))))
                    for d in directions:
                        out.append(Contrast(f"[{model}] {d} {outcome} {frame} {perm}: +0.50 vs 0",
                                   f"{d} {outcome.upper()}: {frame}, {perm}, rate(+0.50) - rate(0)", terms, (d,),
                                   False, d, "direction_simple_change",
                                   (("model", model), ("frame", frame), ("permission", perm), ("outcome", outcome))))
                    # no-history vs tie within permission (if a no-history cell exists)
                    out.append(Contrast(f"[{model}] {outcome} {frame} {perm}: none vs 0",
                               f"{outcome.upper()}: {frame}, rate(none) - rate({perm}, 0)",
                               ((1.0, (outcome, model, frame, "none", "none")),
                                (-1.0, (outcome, model, frame, perm, "+0.00"))), tuple(directions), False, "B",
                               "nohist_vs_tie", (("model", model), ("frame", frame), ("permission", perm),
                                                 ("outcome", outcome))))
            for d in directions:
                for cc in contrasts_B(model, False, (d,), outcome):
                    base = cc.id.split("] ")[-1] if "] " in cc.id else cc.id
                    out.append(Contrast(f"[{model}, {outcome}] {d}: {base}", f"{d}: {cc.name}", cc.terms, (d,), False,
                                        d, "direction_" + cc.kind, cc.meta))
    # dedupe by id
    seen, res = set(), []
    for c in out:
        if c.id not in seen:
            seen.add(c.id)
            res.append(c)
    return res


# ----------------------------------------------------------------------------------------------------------------
# batched sign-flip for simulation (same statistic, shared Monte Carlo sign matrix)

def signflip_p_batch(values: np.ndarray, weights: np.ndarray, draws: int = MC_DRAWS, seed: int = BASE_SEED,
                     chunk: int = 250) -> np.ndarray:
    """values: (reps, B) block values with NaN for missing; weights computed per rep from `weights` strata ids.

    `weights` here is an int array (B,) of stratum ids; per rep the weight of a non-missing block in stratum s is
    1 / (S_used * n_s_used). Returns two-sided Monte Carlo p-values (reps,)."""
    reps, B = values.shape
    strata = weights
    ids = np.unique(strata)
    ok = ~np.isnan(values)
    W = np.zeros_like(values)
    n_used_strata = np.zeros(reps)
    for s in ids:
        m = strata == s
        ns = ok[:, m].sum(1)
        n_used_strata += ns > 0
        with np.errstate(divide="ignore", invalid="ignore"):
            W[:, m] = np.where(ok[:, m], 1.0 / np.maximum(ns, 1)[:, None], 0.0)
    W /= np.maximum(n_used_strata, 1)[:, None]
    A = np.where(ok, values, 0.0) * W
    T = np.abs(A.sum(1))
    rng = np.random.default_rng(seed)
    signs = (rng.integers(0, 2, size=(draws, B), dtype=np.int8) * 2 - 1).astype(np.float64)
    hits = np.zeros(reps)
    for i in range(0, reps, chunk):
        Tstar = np.abs(signs @ A[i:i + chunk].T)      # (draws, chunk)
        hits[i:i + chunk] = (Tstar >= (T[i:i + chunk] - 1e-9)[None, :]).sum(0)
    p = (1 + hits) / (draws + 1)
    p[T < 1e-12] = 1.0
    return p
