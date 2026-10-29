"""Post-run helper (descriptive): draws the hand-coding sample of upsell reasoning traces (fixed seed, about 20 prose +
20 records per model) and writes excerpts for reading. Also a keyword tally over ALL upsell traces (not a planned
measure). Run: ~/.claude/bin/memguard -m 4 -- .venv/bin/python designs/rec_mechanisms/records/handcode_sample.py OUTFILE
"""
import json, random, re, sys
from collections import Counter
from pathlib import Path
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import run_records as RS  # noqa: E402
rows = RS.scored(RS.plan(), RS.OUT, RS.P.load(RS.OUT / "judge.jsonl"))
ups = [r for r in rows if r["completion"] == "valid" and r["m"]["upsell"]]
KW = re.compile(r"[^.\n]*\b(score|scores|scored|reward|rewards|0\.\d{3}|example|examples|previous|history|pattern|grader|"
                r"scorer|higher-scored|archive|quality checker)\b[^.\n]*[.\n]", re.I)
rng = random.Random(20261029)
sample = []
for m in RS.MODELS:
    for fm in ("prose", "records"):
        pool = sorted([r for r in ups if r["model"] == m and r["format"] == fm], key=lambda r: r["key"])
        sample += rng.sample(pool, min(20, len(pool)))
tally = Counter()
for r in ups:
    t = " ".join(x["text"] for x in r.get("reasoning") or [])
    tally[(r["model"], r["format"], "n")] += 1
    tally[(r["model"], r["format"], "mentions score/reward")] += bool(re.search(r"\b(score|scored|reward|0\.\d{3})", t, re.I))
    tally[(r["model"], r["format"], "mentions example/history/pattern")] += bool(
        re.search(r"\b(example|examples|previous|history|pattern|archive)\b", t, re.I))
with open(sys.argv[1], "w") as f:
    for i, r in enumerate(sample):
        t = " ".join(x["text"] for x in r.get("reasoning") or [])
        kw = [k.group(0).strip()[:220] for k in KW.finditer(t)][:12]
        f.write(f"=== {i} {r['key']} | chars={len(t)}\nKW: " + " || ".join(kw) + f"\nEND: {t[-900:]}\nREPLY: {r['reply'].strip()[:300]}\n\n")
print(len(sample), "sampled;", {f"{k[0]}|{k[1]}|{k[2]}": v for k, v in sorted(tally.items())})
