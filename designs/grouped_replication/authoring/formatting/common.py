import json
import os
import random
import re

OUT = "/Users/timf34/Documents/VSCode/model-diffing-agent/designs/grouped_replication/blocks"


def fill(t, i):
    """Template {conflicting|compliant}: i=0 conflicting, i=1 compliant."""
    return re.sub(r"\{([^{}|]*)\|([^{}|]*)\}", lambda m: m.group(i + 1), t)


def assign(seed):
    # each label variant gets 2 conflicting_first + 2 compliant_first; shuffled across blocks
    pairs = [(o, l) for l in range(4) for o in ("conflicting_first", "compliant_first") for _ in range(2)]
    random.Random(seed).shuffle(pairs)
    return pairs


def build(subtype, raw, seed):
    assert len(raw) == 18, (subtype, len(raw))
    pairs = assign(seed)
    blocks = []
    for i, r in enumerate(raw):
        smoke = i >= 16
        if smoke:
            bid = f"A-{subtype}-S{i - 15}"
            order, lv = ("conflicting_first", 0) if i == 16 else ("compliant_first", 1)
        else:
            bid = f"A-{subtype}-{i + 1:02d}"
            order, lv = pairs[i]
        blocks.append({
            "block_id": bid,
            "subtype": subtype,
            "smoke": smoke,
            "order": order,
            "label_variant": lv,
            "current": {"request": r["req"], "check": r.get("check", {}), "required_facts": r["facts"]},
            "archive": [{"request": q, "conflicting": c, "compliant": p} for (q, c, p) in r["arch"]],
        })
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"{subtype}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(blocks, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("wrote", path, len(blocks))
