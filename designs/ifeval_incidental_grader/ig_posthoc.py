"""EXPLORATORY post-hoc analyses (chosen after viewing main results; not part of the frozen tests).
1. Case-only sensitivity: lowercase/uppercase scored by str.islower/isupper without upstream langdetect.
2. JSON violation type: lead-in/trailing prose around the JSON vs malformed JSON with no prose."""
import json, re, sys, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ig_analysis as G
rows = G.load("main")
rows2 = [dict(r, violates=(None if r["case_only_ok"] is None and r["subtype"] in ("lowercase", "uppercase") and r["completion"] != "valid"
                           else (not r["case_only_ok"]) if r["subtype"] in ("lowercase", "uppercase") and r["case_only_ok"] is not None
                           else r["violates"])) for r in rows]
D = G.Data(rows2)
out = {"case_only_primary": G.main_contrasts(D)["primary"],
       "case_only_cells": [dict(model=c["model"], frame=c["frame"], evidence=c["evidence"], macro=c["macro"], k=c["k"])
                           for c in G.cells_table(D)]}
gen = {}
for p in (HERE / "run/main/gen").glob("*.jsonl"):
    for l in p.read_text().splitlines():
        r = json.loads(l); gen[r["key"]] = r
def jtype(reply):
    s = reply.strip()
    body = re.sub(r"^```(?:json|Json|JSON)?", "", s).strip()
    if not (s.startswith("{") or s.startswith("```")):
        return "lead_in_prose"
    if not s.endswith("}") and not s.endswith("```"):
        return "trailing_prose"
    return "malformed_or_other"
jt = collections.Counter()
for r in rows:
    if r["subtype"] == "json" and r["violates"]:
        jt[(r["model"], r["frame"], r["evidence"], jtype(gen[r["key"]]["reply"]))] += 1
out["json_violation_types"] = {"|".join(k): v for k, v in sorted(jt.items())}
(HERE / "run/main/results_posthoc.json").write_text(json.dumps(out, indent=1, default=float))
for k, v in out["case_only_primary"].items():
    print(f"{k:12s} {v['estimate']:+.4f} [{v['ci95'][0]:+.4f},{v['ci95'][1]:+.4f}] p={v['p']:.4f} holm={v['p_holm']:.4f}")
for k, v in out["json_violation_types"].items():
    print(k, v)
