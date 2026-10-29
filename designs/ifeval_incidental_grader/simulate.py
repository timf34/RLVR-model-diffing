"""Rough power assessment for the frozen primary contrasts (assumptions, not variance estimates).
Baseline violation rate p0 per block drawn on the logit scale (mean logit(p0), sd 1.5 across blocks);
an effect delta (absolute, on the macro rate) added only in the RL x +0.50 cell (for A) . alpha: Holm worst case
0.05/8. Sign-flip test as in ig_analysis. 8 subtypes x n blocks."""
import sys, numpy as np
sys.path.insert(0, '.')
import ig_analysis as G
G.N_FLIP = 4000; G.N_BOOT = 10
subs = ["keyword","forbidden","end_phrase","quotation","json","lowercase","uppercase","no_comma"]
def sim(n, p0, delta, reps=200, seed=0):
    rng = np.random.default_rng(seed); hits = 0
    terms = G.T((1,"Qwen 3.8","rl","conflict_p050"),(-1,"Qwen 3.8","rl","tied"),(-1,"Qwen 3.8","ordinary","conflict_p050"),(1,"Qwen 3.8","ordinary","tied"))
    for r in range(reps):
        rows = []
        for s in subs:
            for i in range(n):
                off = rng.normal(np.log(p0/(1-p0)), 1.5)
                pb = 1/(1+np.exp(-off))
                for f, e in [("rl","conflict_p050"),("rl","tied"),("ordinary","conflict_p050"),("ordinary","tied")]:
                    p = min(1, pb + (delta if (f, e) == ("rl","conflict_p050") else 0))
                    rows.append(dict(block_id=f"{s}-{i}", subtype=s, model="Qwen 3.8", frame=f, evidence=e, violates=bool(rng.random() < p)))
        D = G.Data(rows)
        hits += D.signflip(terms, seed=r) < 0.05/8
    return hits/reps
out = ["| blocks/subtype | baseline p0 | delta (RL x +0.50 only) | power (alpha=0.05/8) |", "|---|---|---|---|"]
for n in (24, 48):
    for p0 in (0.02, 0.10):
        for d in (0.03, 0.05, 0.10):
            out.append(f"| {n} | {p0} | {d} | {sim(n, p0, d):.2f} |")
open("simulation/POWER.md","w").write("# Rough power (simulation; assumptions in simulate.py docstring)\n\n" + "\n".join(out) + "\n")
print("\n".join(out))
