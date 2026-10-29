"""Validate an authored subtype file: counts, field rules, and real-checker pair labels.
Usage (repo root): designs/ifeval_incidental_grader/.venv_checker/bin/python designs/ifeval_incidental_grader/authoring/validate_authoring.py <subtype>"""
import json, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ifeval_adapter as A

COUNTS = {"smoke": 2, "dev": 20, "main": 48}

def main(sub):
    path = Path(__file__).parent / f"{sub}.json"
    d = json.loads(path.read_text())
    recs = d["records"]
    want = dict(COUNTS, discovery=16 if sub in A.DISCOVERY_SUBTYPES else 0,
                applicability=24 if sub in A.DISCOVERY_SUBTYPES else 0)
    got = Counter(r.get("split") for r in recs)
    problems = []
    for s, n in want.items():
        if got.get(s, 0) != n:
            problems.append(f"count {s}: {got.get(s, 0)} != {n}")
    seen = set()
    for i, r in enumerate(recs):
        for e in A.validate_record(r, sub):
            problems.append(f"record {i} ({r.get('split')}, {r.get('domain')}): {e}")
        key = json.dumps(r["current"]["facts"], sort_keys=True)
        if key in seen:
            problems.append(f"record {i}: duplicate current facts")
        seen.add(key)
    # current facts must not leak across records' histories (blocks independent)
    print(f"{sub}: {len(recs)} records, {len(problems)} problems")
    for p in problems:
        print(" -", p)
    return 1 if problems else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
