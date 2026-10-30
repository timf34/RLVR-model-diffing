"""One line per judged item, hidden metadata beside the labels (stdlib):  python3 rj_peek.py <stage> [filter]
filter: substring of the key, or 'send' / 'draft' for the real action."""
import json
import sys

from rj_common import RATIONALES, RUN, read_jsonl

stage = sys.argv[1]
flt = sys.argv[2] if len(sys.argv) > 2 else ""
I = {it["key"]: it for it in read_jsonl(RUN / stage / "items.jsonl")}
J = list({r["key"]: r for r in read_jsonl(RUN / stage / "judge.jsonl")}.values())   # last record per key wins
AB = {"absent": ".", "considered": "c", "rejected": "r", "endorsed": "E"}
keys = list(I)
short = [r[:4] for r in RATIONALES]
print(f"{'idx':>4} {'model':8} {'arm':9} {'score':5} {'act':5} {'chars':>5} | suf restr score conf | {' '.join(f'{s:4}' for s in short)} | expS ovs intend | verified")
n_bad = 0
for r in sorted(J, key=lambda r: keys.index(r["key"])):
    it = I[r["key"]]
    act = "SEND" if it["violates"] else "draft"
    if flt and flt not in r["key"] and flt != act.lower():
        continue
    L = r["labels"]
    if not L:
        n_bad += 1
        print(f"{keys.index(r['key']):4} {it['model']:8} {it['arm']:9} {it['score']:5} {act:5} {it['reasoning_chars']:5} | UNLABELLED {r['errors']}")
        continue
    R = L["rationales"]
    bad = [k for k, v in r["excerpt_verified"].items() if not v]
    print(f"{keys.index(r['key']):4} {it['model']:8} {it['arm']:9} {it['score']:5} {act:5} {it['reasoning_chars']:5} | "
          f"{L['reasoning_sufficient']:3} {L['recognises_restriction'][:5]:5} {L['recognises_score_pattern'][:5]:5} "
          f"{L['recognises_conflict'][:4]:4} | {' '.join(f'{AB[R[x]['status']]:4}' for x in RATIONALES)} | "
          f"{L['expects_current_action_scored'][:3]:4} {L['oversight'][:3]:3} {L['intended_action']:6} | "
          f"{'ok' if not bad else bad}")
print(f"\n(. absent, c considered, r rejected, E endorsed; columns {list(RATIONALES)}); unlabelled: {n_bad}")
