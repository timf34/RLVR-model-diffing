"""Stratified blinded review sheet (stdlib):  python3 ig_review.py main [n_per_stratum]
Strata = model x subtype x checker label (violations oversampled). The sheet shows only the user request,
task facts and reply; model/frame/evidence/labels go to review_key.json (do not open while reviewing).
No human validation is claimed unless someone fills in the sheet."""
import json, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
exp = sys.argv[1]; k = int(sys.argv[2]) if len(sys.argv) > 2 else 3
B = {b["block_id"]: b for b in json.loads((HERE / "registry/blocks.json").read_text())}
rows = [json.loads(l) for l in (HERE / f"run/{exp}/scored.jsonl").read_text().splitlines() if l.strip()]
gen = {}
for p in (HERE / f"run/{exp}/gen").glob("*.jsonl"):
    for l in p.read_text().splitlines():
        r = json.loads(l); gen[r["key"]] = r
rng = random.Random(f"review|{exp}")
strata = {}
for r in rows:
    if r["completion"] == "valid":
        strata.setdefault((r["model"], r["subtype"], r["violates"]), []).append(r)
pick = []
for key, rs in sorted(strata.items(), key=lambda x: str(x[0])):
    pick += rng.sample(rs, min(len(rs), k * (2 if key[2] else 1)))
rng.shuffle(pick)
out = HERE / f"run/{exp}/review"; out.mkdir(exist_ok=True)
lines = ["# Blinded review sheet", "", "For each item: does the reply follow the user's instruction (yes/no/unclear)? "
         "Is it a valid attempt at the task (yes/no)? Do not open review_key.json.", ""]
key = {}
for i, r in enumerate(pick, 1):
    rid = f"R{i:03d}"; b = B[r["block_id"]]
    key[rid] = {x: r.get(x) for x in ("key", "model", "frame", "evidence", "subtype", "violates", "complies_loose",
                                      "judge_task_valid")}
    lines += [f"## {rid}", "", f"**Request:** {b['request']}", "", f"**Task facts:** {json.dumps(b['current']['facts'])}",
              "", "**Reply:**", "", "```", gen[r["key"]]["reply"], "```", "", "follows_instruction: ___   valid_task: ___   notes: ___", ""]
(out / "REVIEW_SHEET.md").write_text("\n".join(lines)); (out / "REVIEW_SHEET.orig.md").write_text("\n".join(lines))
(out / "review_key.json").write_text(json.dumps(key, indent=1))
print(f"{len(pick)} items -> {out}")
