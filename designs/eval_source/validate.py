"""Judge validation for disclosure labels: hand labels on a stratified sample plus all rule–judge disagreements.

  .venv/bin/python designs/eval_source/validate.py sample main     # -> runs/main/validation/to_label.md (no labels shown)
  # write hand labels to runs/main/validation/hand_labels.json as {"<id>": "discloses|omits|denies", ...}
  .venv/bin/python designs/eval_source/validate.py compare main
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import run as RUN  # noqa: E402


def rows(set_):
    return [r for r in RUN.load_scored(set_) if r["kind"] == "main" and r["behaviour"] == "disclosure"
            and r["completion"] == "valid" and r["judge"]]


def sample(set_, n=40, seed=7):
    rs = rows(set_)
    rng = random.Random(seed)
    dis = [r for r in rs if r["rule"]["label"] != r["judge"]["label"]]
    omit = [r for r in rs if r["judge"]["label"] != "discloses" and r not in dis]
    disc = [r for r in rs if r["judge"]["label"] == "discloses" and r not in dis]
    # every disagreement, plus a sample of n: half judge-accommodating (as far as available), the rest disclosing
    a = rng.sample(omit, min(n // 2, len(omit)))
    pick = dis + a + rng.sample(disc, min(n - len(a), len(disc)))
    rng.shuffle(pick)
    out = HERE / "runs" / set_ / "validation"
    out.mkdir(parents=True, exist_ok=True)
    ids = {f"v{i:02d}": r["key"] for i, r in enumerate(pick)}
    (out / "ids.json").write_text(json.dumps(ids, indent=1))
    L = ["# Disclosure replies to hand-label (labels hidden; model and cell hidden)", ""]
    for vid, key in ids.items():
        r = next(x for x in pick if x["key"] == key)
        L += [f"## {vid}", "", "FACTS: " + RUN.task_of(r)["raw"]["judge_facts"], "", "```text", r["reply"].strip(),
              "```", ""]
    (out / "to_label.md").write_text("\n".join(L) + "\n")
    print(f"{len(ids)} replies ({len(dis)} rule–judge disagreements) -> {out / 'to_label.md'}")


def compare(set_):
    out = HERE / "runs" / set_ / "validation"
    ids = json.loads((out / "ids.json").read_text())
    hand = json.loads((out / "hand_labels.json").read_text())
    by_key = {r["key"]: r for r in rows(set_)}
    agree, L = 0, ["| id | hand | judge | rule | agree |", "|---|---|---|---|---|"]
    for vid, key in ids.items():
        r = by_key[key]
        h, j = hand[vid], r["judge"]["label"]
        a = (h == "discloses") == (j == "discloses")   # the binary used in the analysis
        agree += a
        L.append(f"| {vid} | {h} | {j} | {r['rule']['label']} | {'yes' if a else '**no**'} |")
    allr = list(by_key.values())
    rj = sum(r["rule"]["label"] == r["judge"]["label"] for r in allr)
    summary = (f"Hand vs judge (accommodates = omits/denies): {agree}/{len(ids)}. "
               f"Rule vs judge over all {len(allr)} judged disclosure replies: {rj}/{len(allr)} same label.")
    (out / "VALIDATION.md").write_text("# Judge validation\n\n" + summary + "\n\n" + "\n".join(L) + "\n")
    print(summary)


if __name__ == "__main__":
    {"sample": sample, "compare": compare}[sys.argv[1]](sys.argv[2])
