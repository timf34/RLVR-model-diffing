"""Per-label agreement between two label sets (stdlib):
  python3 rj_agreement.py <stage> <other.jsonl>          # e.g. run/main/judge_sonnet55.jsonl (second judge)
  python3 rj_agreement.py <stage> <human_labels.json>    # hand labels: {"R001": {<RUBRIC fields>}, ...} + review_key.json
Reports, for every enum field and every rationale (status, and endorsed-vs-not), the number of items both sets
label, raw agreement and Cohen's kappa. Items either set leaves unlabelled are skipped (and counted)."""
import json
import sys
from collections import Counter

from rj_common import ENUMS, RATIONALES, RUN, read_jsonl

stage, other = sys.argv[1], sys.argv[2]
primary = {r["key"]: r["labels"] for r in read_jsonl(RUN / stage / "judge.jsonl") if r["labels"]}
if other.endswith(".jsonl"):
    second = {r["key"]: r["labels"] for r in read_jsonl(RUN / stage / other if "/" not in other else other) if r["labels"]}
else:
    human = json.loads(open(other).read())
    key = json.loads((RUN / stage / "review" / "review_key.json").read_text())
    second = {key[rid]["key"]: lab for rid, lab in human.items() if lab}
common = sorted(set(primary) & set(second))
print(f"{len(common)} items labelled by both ({len(primary)} primary, {len(second)} other)\n")


def kappa(pairs):
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n ** 2
    return po, (po - pe) / (1 - pe) if pe < 1 else float("nan")


print(f"{'field':40} {'n':>4} {'agree':>6} {'kappa':>6}")
for f in ENUMS:
    po, k = kappa([(primary[c][f], second[c][f]) for c in common])
    print(f"{f:40} {len(common):4} {po:6.2f} {k:6.2f}")
for r in RATIONALES:
    po, k = kappa([(primary[c]["rationales"][r]["status"], second[c]["rationales"][r]["status"]) for c in common])
    po2, k2 = kappa([(primary[c]["rationales"][r]["status"] == "endorsed",
                      second[c]["rationales"][r]["status"] == "endorsed") for c in common])
    print(f"{r + ' (status)':40} {len(common):4} {po:6.2f} {k:6.2f}")
    print(f"{r + ' (endorsed vs not)':40} {len(common):4} {po2:6.2f} {k2:6.2f}")
