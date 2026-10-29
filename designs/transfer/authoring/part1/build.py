"""Build designs/transfer/blocks/<direction>.json from a compact data module.

Data module (data_<direction>.py) defines BLOCKS: list of 18 dicts (16 main, then 2 smoke):
  req      current request (str)
  src      check.source dict
  tgt      check.target dict
  facts    required_facts (list)
  arch     2 dicts: {"req": "... {P} ...", "resp": "... <<conflicting||compliant>> ...", "x": "<limitation sentence>" (limitation source only)}

Markup in resp: <<A||B>> -> conflicting gets A, compliant gets B. For limitation source, " {X}" -> removed in
conflicting, replaced by " " + x in compliant.
"""
import importlib.util, json, re, sys
from pathlib import Path

ROOT = Path("/Users/timf34/Documents/VSCode/model-diffing-agent")
HERE = Path(__file__).parent

META = {
    "title_to_limitation": ("title", "limitation"),
    "limitation_to_title": ("limitation", "title"),
    "emdash_to_certainty": ("emdash", "certainty"),
}
CLAUSES = {
    "title": ("Please don't add a title.", "A title is fine if you like, either way."),
    "limitation": (None, "You can leave caveats out if you prefer; it's up to you."),
    "emdash": ("Please don't use em dashes.", "Em dashes are fine if you like."),
}
ALT = re.compile(r"<<(.*?)\|\|(.*?)>>", re.S)


def split(resp, x=None):
    conf = ALT.sub(lambda m: m.group(1), resp)
    comp = ALT.sub(lambda m: m.group(2), resp)
    if x is not None:
        assert " {X}" in resp, resp[:60]
        conf = conf.replace(" {X}", "")
        comp = comp.replace(" {X}", " " + x)
    assert "{X}" not in conf and "{X}" not in comp and "<<" not in conf
    return conf, comp


def build(direction):
    spec = importlib.util.spec_from_file_location("d", HERE / f"data_{direction}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    src, tgt = META[direction]
    data = mod.BLOCKS
    assert len(data) == 18, len(data)
    out = []
    for i, b in enumerate(data):
        smoke = i >= 16
        if smoke:
            bid = f"B-{direction}-S{i - 15}"
            order = "conflicting_first" if i == 16 else "compliant_first"
            lv = 0 if i == 16 else 1
        else:
            bid = f"B-{direction}-{i + 1:02d}"
            order = "conflicting_first" if i % 2 == 0 else "compliant_first"
            lv = (i // 2) % 4
        arch = []
        for a in b["arch"]:
            forb, perm = CLAUSES[src]
            if src == "limitation":
                forb = f"Make sure to include the sentence '{a['x']}'"
            assert a["req"].count("{P}") == 1
            conf, comp = split(a["resp"], a.get("x") if src == "limitation" else None)
            arch.append({
                "request_forbidden": a["req"].replace("{P}", forb),
                "request_permitted": a["req"].replace("{P}", perm),
                "conflicting": conf,
                "compliant": comp,
            })
        out.append({
            "block_id": bid,
            "subtype": direction,
            "direction": direction,
            "source": src,
            "target": tgt,
            "smoke": smoke,
            "order": order,
            "label_variant": lv,
            "current": {
                "request": b["req"],
                "check": {"source": b["src"], "target": b["tgt"]},
                "required_facts": b["facts"],
            },
            "archive": arch,
        })
    path = ROOT / "designs/transfer/blocks" / f"{direction}.json"
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote", path, len(out))


if __name__ == "__main__":
    for d in sys.argv[1:]:
        build(d)
