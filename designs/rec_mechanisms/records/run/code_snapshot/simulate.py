"""Simulation calibration of the planned records-vs-prose contrasts (run before freezing; writes
simulation/CALIBRATION.md). Pattern of designs/score_gap/recommendation/simulate.py.

Design simulated = the frozen design at one level: 12 scenarios x 3 replies per format (prose, records).
Scenario heterogeneity: scenario logit offsets ~ N(0, 1.5).
  1. Size of the paired sign-flip test when prose and records share the population rate, base rate 0.1 / 0.5 /
     0.9, with (a) identical scenario offsets in both formats (the realistic case: same scenarios) and
     (b) independent offsets per format (a harsher case).
  2. Holm family-wise error over 12 contrasts, all null (independent offsets per contrast; per-contrast base rates
     drawn from {0.1, 0.4, 0.9} to mimic the observed spread).
  3. Power: prose 0.9 vs records 0.5 / 0.2; prose 0.4 vs records 0.1; prose 0.9 vs records 0.7.
Run: ~/.claude/bin/memguard -m 4 -- .venv/bin/python designs/rec_mechanisms/records/simulate.py
"""
from pathlib import Path

import numpy as np

import rr_analysis as A

HERE = Path(__file__).parent
NS, NR, SIG, SIMS = 12, 3, 1.5, 1000
G = 0.5


def logit(p):
    return np.log(p / (1 - p))


def draw(rng, base, off):
    p = 1 / (1 + np.exp(-(logit(base) + off)))
    return [dict(scenario=f"s{s:02d}", gap=G, y=int(rng.random() < p[s])) for s in range(NS) for _ in range(NR)]


def main():
    rng = np.random.default_rng(20261029)
    L = ["# Simulation calibration: records vs prose paired contrasts", "",
         f"Design: {NS} scenarios × {NR} replies per format at one level; scenario logit offsets N(0, {SIG}); "
         f"{SIMS} simulations per row; exact sign-flip test over 2^12 scenario flips; alpha = 0.05.", "",
         "| Check | Rejection rate | Target |", "|---|---|---|"]

    def rate(fn, sims=SIMS):
        return float(np.mean([fn() for _ in range(sims)]))

    for base in (0.1, 0.5, 0.9):
        def same():
            off = rng.normal(0, SIG, NS)
            return A.paired_test(draw(rng, base, off), draw(rng, base, off), G)["p"] < 0.05

        def indep():
            return A.paired_test(draw(rng, base, rng.normal(0, SIG, NS)), draw(rng, base, rng.normal(0, SIG, NS)),
                                 G)["p"] < 0.05
        L.append(f"| Size, base {base}, identical scenario offsets | {rate(same):.3f} | ≤ 0.05 |")
        L.append(f"| Size, base {base}, independent scenario offsets | {rate(indep):.3f} | ≤ 0.05 |")

    def fwer():
        ps = {}
        for i in range(12):
            base = rng.choice([0.1, 0.4, 0.9])
            off = rng.normal(0, SIG, NS)
            ps[i] = A.paired_test(draw(rng, base, off), draw(rng, base, off), G)["p"]
        return min(A.holm(ps).values()) < 0.05

    def fwer_indep():
        ps = {}
        for i in range(12):
            base = rng.choice([0.1, 0.4, 0.9])
            ps[i] = A.paired_test(draw(rng, base, rng.normal(0, SIG, NS)), draw(rng, base, rng.normal(0, SIG, NS)),
                                  G)["p"]
        return min(A.holm(ps).values()) < 0.05
    L.append(f"| Holm FWER, 12 null contrasts, identical offsets ({SIMS // 2} sims) | {rate(fwer, SIMS // 2):.3f} "
             "| ≤ 0.05 |")
    L.append(f"| Holm FWER, 12 null contrasts, independent offsets ({SIMS // 2} sims) | "
             f"{rate(fwer_indep, SIMS // 2):.3f} | ≤ 0.05 |")
    for a, b in ((0.9, 0.2), (0.9, 0.5), (0.9, 0.7), (0.4, 0.1)):
        def pw(a=a, b=b):
            off = rng.normal(0, SIG, NS)
            return A.paired_test(draw(rng, a, off), draw(rng, b, off), G)["p"] < 0.05

        def pw_holm(a=a, b=b):  # the same effect, judged at the Holm bound for the first of 12 (alpha/12)
            off = rng.normal(0, SIG, NS)
            return A.paired_test(draw(rng, a, off), draw(rng, b, off), G)["p"] < 0.05 / 12
        L.append(f"| Power, prose {a} vs records {b} (shared offsets), unadjusted | {rate(pw):.3f} | (power) |")
        L.append(f"| Power, prose {a} vs records {b} (shared offsets), at alpha/12 | {rate(pw_holm):.3f} | (power) |")
    L += ["", "Note: the minimum attainable exact p-value with 12 scenarios is 2/4096 ≈ 0.0005, below the Holm bound "
          "0.05/12 ≈ 0.0042, so every contrast can in principle reach significance after adjustment."]
    out = HERE / "simulation"
    out.mkdir(exist_ok=True)
    (out / "CALIBRATION.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
