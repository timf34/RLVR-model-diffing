"""Simulation calibration of the planned contrasts (run before freezing; writes simulation/CALIBRATION.md).

Design simulated = the frozen design at one gap level: 12 scenarios x 4 cells x 3 replies per cell.
The contrasts are defined on the probability scale, so nulls are simulated with effects that are additive on the
probability scale and heterogeneous scenario base rates (Beta(0.6, 0.6): many scenarios near 0 or 1, as observed).
  - size of each contrast when its effect is absent but the other effects are present (and when all are absent);
  - Holm family-wise error over 12 tests under the global null;
  - power for a 0.25 ownership effect, a 0.25 wording effect and a 0.4 interaction;
  - sensitivity: effects additive on the LOGIT scale (no logit interaction) induce a probability-scale interaction;
    the rejection rate for "interaction" in that setting is reported so a significant interaction is read with care.
Run: ~/.claude/bin/memguard -m 3 -- .venv/bin/python designs/rec_mechanisms/ownership/simulate.py
"""
from pathlib import Path

import numpy as np

import own_analysis as A

HERE = Path(__file__).parent
NS, NR, SIMS = 12, 3, 1000
CELLS = ("chat/team", "chat/independent", "episode/team", "episode/independent")


def draw(rng, own=0.0, word=0.0, inter=0.0, logit=False):
    base = rng.beta(0.6, 0.6, NS)
    r = {}
    for c in CELLS:
        t = c.endswith("team")
        e = c.startswith("episode")
        if logit:
            lb = np.log(np.clip(base, 0.02, 0.98) / (1 - np.clip(base, 0.02, 0.98)))
            p = 1 / (1 + np.exp(-(lb + own * t + word * e)))
        else:
            p = base + own * (t - 0.5) + word * (e - 0.5) + inter * ((t - 0.5) * (0.5 - e))
            p = np.clip(p, 0, 1)
        r[c] = rng.binomial(NR, p) / NR
    return A.contrast_values(r)


def rej(rng, contrast, **kw):
    return np.mean([A.signflip_test(draw(rng, **kw)[contrast]) < 0.05 for _ in range(SIMS)])


def main():
    rng = np.random.default_rng(20261029)
    L = ["# Simulation calibration of the planned contrasts", "",
         f"{NS} scenarios x 4 cells x {NR} replies; scenario base rates Beta(0.6, 0.6); {SIMS} simulations per row; "
         "exact scenario sign-flip test; alpha = 0.05. Effects are additive on the probability scale unless stated "
         "(effects are clipped to [0, 1], which makes them slightly smaller than nominal near the edges).", "",
         "| Check | Rejection rate | Target |", "|---|---|---|"]
    L.append(f"| ownership size, no effects | {rej(rng, 'ownership'):.3f} | ≤ 0.05 |")
    L.append(f"| ownership size, wording effect 0.3 present | {rej(rng, 'ownership', word=0.3):.3f} | ≤ 0.05 |")
    L.append(f"| wording size, no effects | {rej(rng, 'wording'):.3f} | ≤ 0.05 |")
    L.append(f"| wording size, ownership effect 0.3 present | {rej(rng, 'wording', own=0.3):.3f} | ≤ 0.05 |")
    L.append(f"| interaction size, no effects | {rej(rng, 'interaction'):.3f} | ≤ 0.05 |")
    L.append(f"| interaction size, both main effects 0.3 (additive, probability scale) | "
             f"{rej(rng, 'interaction', own=0.3, word=0.3):.3f} | ≤ 0.05 |")

    def fwer():
        ps = {(m, g, c): A.signflip_test(v) for m in range(2) for g in range(2)
              for c, v in draw(rng).items()}
        return min(A.holm(ps).values()) < 0.05
    L.append(f"| Holm FWER over 12 tests, global null | {np.mean([fwer() for _ in range(SIMS // 2)]):.3f} | ≤ 0.05 |")
    L.append(f"| power, ownership effect 0.25 | {rej(rng, 'ownership', own=0.25):.3f} | (power) |")
    L.append(f"| power, wording effect 0.25 | {rej(rng, 'wording', word=0.25):.3f} | (power) |")
    L.append(f"| power, interaction 0.4 | {rej(rng, 'interaction', inter=0.4):.3f} | (power) |")
    L.append(f"| sensitivity: interaction 'rejections' with logit-additive effects (own 2, word 2 logits) | "
             f"{rej(rng, 'interaction', own=2.0, word=2.0, logit=True):.3f} | (scale artefact rate) |")
    out = HERE / "simulation"
    out.mkdir(exist_ok=True)
    (out / "CALIBRATION.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
