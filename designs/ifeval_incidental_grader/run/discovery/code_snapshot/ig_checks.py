"""Pre-freeze implementation checks (stdlib + checker venv):  .venv_checker/bin/python ig_checks.py"""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ig_render as R, ifeval_adapter as A

B = json.loads((HERE / "registry/blocks.json").read_text())
fails = []
def chk(c, msg):
    if not c: fails.append(msg)

for b in B:
    if b["split"] == "dev":
        continue
    pv = b["pair_validation"]
    chk(pv["compliant_passes"] and not pv["violating_passes"], f"{b['block_id']}: pair labels")
    chk(b["pair_content_check"], f"{b['block_id']}: pair content check")
    convs = {(f, e): R.render(b, f, e) for f in R.FRAMES for e in R.EVIDENCE}
    users = {c["messages"][0]["content"] for c in convs.values()}
    chk(len(users) == 1 and users == {b["request"]}, f"{b['block_id']}: user request varies")
    for (f, e), c in convs.items():
        chk(c["system"] == f"{R.COMMON_SYSTEM}\n\n{R.FRAMES[f]}", f"{b['block_id']}: system")
        chk([m["role"] for m in c["messages"]] == ["user", "assistant", "tool"], "roles")
        p = json.loads(c["messages"][2]["content"])
        chk(p["task_data"] == b["current"]["facts"], f"{b['block_id']}: task facts vary")
        # tool payload identical across frames
        chk(c["messages"][2]["content"] == convs[("ordinary", e)]["messages"][2]["content"], "payload varies by frame")
        d = p.get("diagnostics")
        chk((d is None) == (e == "no_grader"), f"{b['block_id']}: diag presence {e}")
        if e in R.SCORED:
            gap = R.EVIDENCE[e]
            for r in d["recent_records"]:
                which = "violating" if r["response"] == b["pair"]["violating"] else "compliant"
                want = 0.5 + gap / 2 if which == "violating" else 0.5 - gap / 2
                chk(abs(r["score"] - want) < 1e-9, f"{b['block_id']}: score map {e}")
            chk(c["messages"][2]["content"].count('"score": 0.') + c["messages"][2]["content"].count('"score": 1.') == 2, "precision")
        if d and "recent_records" in d:
            ids = [r["record_id"] for r in d["recent_records"]]
            chk(ids == ["candidate_a", "candidate_b"], "labels")
            first = d["recent_records"][0]["response"]
            chk((first == b["pair"]["violating"]) == (b["order"] == "violating_first"), "order")
            chk(all(r["request"] == b["history_request"] for r in d["recent_records"]), "hist request")
    # only scores differ between scored conditions
    base = convs[("rl", "tied")]["messages"][2]["content"]
    import re
    strip = lambda s: re.sub(r'"score": [0-9.]+', '"score": X', s)
    for e in R.SCORED:
        chk(strip(convs[("rl", e)]["messages"][2]["content"]) == strip(base), f"{b['block_id']}: non-score diff {e}")
    chk(strip(base).replace(',\n        "score": X', '') == convs[("rl", "unscored")]["messages"][2]["content"], f"{b['block_id']}: unscored != scored minus scores")
    # no evaluated answer / current facts leaked into archive
    hist = (b["history_request"] + b["pair"]["compliant"] + b["pair"]["violating"]).lower()
    for rf in b["current"]["required_facts"]:
        chk(rf.lower() not in hist, f"{b['block_id']}: current fact {rf!r} in archive")
    if b["split"] == "applicability":
        for a in R.APPLICABILITY:
            p = json.loads(R.applicability_payload(b, "conflict_p050", a))
            same = p["runtime"]["current_evaluator_id"] == p["diagnostics"]["evaluator_id"]
            chk(same == (a == "match"), "applic ids")
        pm = R.applicability_payload(b, "tied", "match"); pmm = R.applicability_payload(b, "tied", "mismatch")
        chk(len(pm) == len(pmm), "applic payload length differs")
# counterbalance
from collections import Counter
for s in A.SUBTYPES:
    for sp in ("main", "applicability", "discovery"):
        c = Counter(b["order"] for b in B if b["subtype"] == s and b["split"] == sp)
        if c: chk(abs(c["violating_first"] - c["compliant_first"]) <= 0, f"order balance {s}/{sp}: {dict(c)}")
evc = Counter(R.evaluator_ids(b["block_id"])[0] < R.evaluator_ids(b["block_id"])[1] for b in B if b["split"] == "applicability")
print("applicability id-order balance:", dict(evc))
print(f"{len(fails)} failures"); [print(" -", f) for f in fails[:30]]
b = next(x for x in B if x["block_id"] == "keyword-main-01")
c = R.render(b, "rl", "conflict_p050")
print("SYSTEM:", c["system"]); print("USER:", c["messages"][0]["content"]); print("TOOL:", c["messages"][2]["content"])
