import json
import re

OUT = "/Users/timf34/Documents/VSCode/model-diffing-agent/designs/grouped_replication/blocks"


def fill(base, slot):
    s = base.replace("{X}", slot)
    s = re.sub(r"  +", " ", s)
    return s.strip()


def assemble(subtype, raw, truncate=False):
    """raw: list of 18 dicts (16 main then 2 smoke) with keys request, check, required_facts,
    archive=[(request, base, conflicting_slot, compliant_slot), ...]."""
    assert len(raw) == 18, len(raw)
    blocks = []
    for i, r in enumerate(raw):
        smoke = i >= 16
        if smoke:
            j = i - 16
            bid = f"A-{subtype}-S{j + 1}"
            order = "conflicting_first" if j == 0 else "compliant_first"
            lv = j
        else:
            bid = f"A-{subtype}-{i + 1:02d}"
            order = "conflicting_first" if i % 2 == 0 else "compliant_first"
            lv = (i // 2) % 4
        arch = []
        for req, base, cslot, kslot in r["archive"]:
            if truncate:
                base = base.split("{X}")[0] + "{X}"
            arch.append({"request": req, "conflicting": fill(base, cslot), "compliant": fill(base, kslot)})
        blocks.append({
            "block_id": bid,
            "subtype": subtype,
            "smoke": smoke,
            "order": order,
            "label_variant": lv,
            "current": {"request": r["request"], "check": r["check"], "required_facts": r["required_facts"]},
            "archive": arch,
        })
    with open(f"{OUT}/{subtype}.json", "w") as f:
        json.dump(blocks, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return blocks
