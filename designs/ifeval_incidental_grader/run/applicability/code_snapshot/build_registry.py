"""Compile authored records into the frozen adapter registry (run under .venv_checker).

    .venv_checker/bin/python build_registry.py            # writes registry/blocks.json + registry/REGISTRY.md

Each block gets: block_id, provenance, subtype/family, instruction id + params, checker version, current request,
packet id, historical request, compliant/violating pair, edit, pair validation, archive order and prompt hashes.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ifeval_adapter as A  # noqa: E402
import ig_render as R  # noqa: E402

AUTH = HERE / "authoring"
OUT = HERE / "registry"
AUTHOR_MODEL = "claude-opus-5-5 (Claude Code subagent, offline, no target-model outputs seen)"


def build() -> list[dict]:
    blocks, problems = [], []
    for sub in A.SUBTYPES:
        path = AUTH / f"{sub}.json"
        if not path.exists():
            problems.append(f"missing {path.name}")
            continue
        recs = json.loads(path.read_text())["records"]
        by_split: dict[str, list] = {}
        for r in recs:
            by_split.setdefault(r["split"], []).append(r)
        for split, rs in by_split.items():
            orders = R.balanced_orders(len(rs), f"order|{sub}|{split}|2026-10-29")
            for i, r in enumerate(rs, 1):
                errs = A.validate_record(r, sub)
                if errs:
                    problems += [f"{sub}/{split}/{i}: {e}" for e in errs]
                    continue
                bid = f"{sub}-{split}-{i:02d}"
                c = r["current"]
                b = dict(
                    block_id=bid, split=split, subtype=sub, family=A.SUBTYPES[sub]["family"],
                    provenance=dict(kind="newly_authored", author=AUTHOR_MODEL, upstream_repo=A.UPSTREAM_URL,
                                    upstream_revision=A.UPSTREAM_REV, source_item=None,
                                    note="fresh simple instance built around an upstream IFEval instruction type"),
                    scenario_id=bid, template_id=bid, domain=r.get("domain"), task_kind=r.get("task_kind"),
                    instruction_id=A.SUBTYPES[sub]["iid"], instruction_wording=A.SUBTYPES[sub]["wording"],
                    params=c["params"], checker_kwargs=A.SUBTYPES[sub]["kwargs"](c["params"]),
                    checker_version=A.CHECKER_VERSION,
                    current=c, packet_id=None,
                )
                if split != "dev":
                    h = r["history"]
                    b["history"] = h
                    b["history_request"] = A.history_request(r, sub)
                    pr = A.build_pair(r, sub)
                    b["pair"] = dict(compliant=pr["compliant"], violating=pr["violating"])
                    b["violation_edit"] = pr["edit"]
                    b["pair_validation"] = A.pair_validation(r, sub)
                    b["order"] = orders[i - 1]
                    # content-validity check: both candidates carry the same history facts (case-insensitive)
                    b["pair_content_check"] = all(
                        (v.lower() in pr["compliant"].lower()) == (v.lower() in pr["violating"].lower())
                        for v in h["facts"].values())
                else:
                    b["order"] = None
                blocks.append(b)
    # unique packet ids from a seeded sample (hash-derived ids collided)
    import random as _r
    pool = _r.Random("packet-ids|2026-10-29").sample(range(10000, 100000), len(blocks))
    for b, n in zip(sorted(blocks, key=lambda x: x["block_id"]), pool):
        b["packet_id"] = f"TP-{n}"
        sub = b["subtype"]
        rec = dict(current=b["current"], history=b.get("history"))
        b["request"] = A.current_request(rec, sub, b["packet_id"])
    # leak check: no current request text / facts in its own archive (validated per record) + uniqueness of ids
    ids = Counter(b["block_id"] for b in blocks)
    problems += [f"duplicate id {k}" for k, n in ids.items() if n > 1]
    pids = Counter(b["packet_id"] for b in blocks)
    problems += [f"duplicate packet id {k}" for k, n in pids.items() if n > 1]
    return blocks, problems


def main():
    blocks, problems = build()
    OUT.mkdir(exist_ok=True)
    if problems:
        print(f"{len(problems)} problems"); [print(" -", p) for p in problems[:60]]
        sys.exit(1)
    for b in blocks:
        if b["split"] == "dev":
            b["prompt_sha256"] = {"ordinary|no_grader": R.conv_hash(R.render_dev(b))}
        else:
            b["prompt_sha256"] = {f"{f}|{e}": R.conv_hash(R.render(b, f, e)) for f in R.FRAMES for e in R.EVIDENCE}
            if b["split"] == "discovery":
                b["prompt_sha256"] = {f"{f}|{e}": R.conv_hash(R.render_discovery(b, f, e))
                                      for f in R.FRAMES for e in R.DISCOVERY_EVIDENCE}
    (OUT / "blocks.json").write_text(json.dumps(blocks, indent=1, ensure_ascii=False) + "\n")
    cnt = Counter((b["subtype"], b["split"]) for b in blocks)
    lines = ["# Adapter registry (IFEval-derived tasks)", "",
             f"Upstream: {A.UPSTREAM_URL} @ `{A.UPSTREAM_REV}` (Apache-2.0; see vendor/gr/LICENSE).",
             f"Checker: `{A.CHECKER_VERSION}`. All items are newly authored simple instances of upstream "
             "instruction types; none is an original IFEval prompt.", "",
             "| subtype | family | instruction_id | wording | smoke | dev | main | discovery |", "|---|---|---|---|---|---|---|---|"]
    for s, d in A.SUBTYPES.items():
        lines.append(f"| {s} | {d['family']} | `{d['iid']}` | {d['wording']} | " +
                     " | ".join(str(cnt.get((s, sp), 0)) for sp in ("smoke", "dev", "main", "discovery")) + " |")
    lines += ["", "Instruction text per subtype (params from each record):", ""]
    ex = {"keyword": {"keyword": "update"}, "forbidden": {"word": "meeting"},
          "end_phrase": {"phrase": "Let me know if you have any questions."}}
    for s in A.SUBTYPES:
        lines.append(f"- `{s}`: {A.constraint_text(s, ex.get(s, {}))}")
    (OUT / "REGISTRY.md").write_text("\n".join(lines) + "\n")
    print(f"ok: {len(blocks)} blocks; " + ", ".join(f"{k[0]}/{k[1]}={v}" for k, v in sorted(cnt.items())))


if __name__ == "__main__":
    main()
