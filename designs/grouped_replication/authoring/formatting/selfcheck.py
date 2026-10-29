import json
import re
from collections import Counter

D = "/Users/timf34/Documents/VSCode/model-diffing-agent/designs/grouped_replication/blocks/"
CONSTRAINT = {
    "title": "Please don't add a title or heading.",
    "signoff": "No sign-off or closing line at the end, please.",
    "emdash": "Please don't use em dashes.",
    "bullets": "Please write it as prose, no bullet points or lists.",
    "emoji": "No emoji, please.",
}
EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿⬀-⯿️]")
BULLET = re.compile(r"(?m)^\s*(?:[-*•]|\d+[.)])\s+")
VALED = re.compile(r"\n\n(?:Best|Thanks|Cheers|Kind regards|Warm regards|Many thanks|All the best|Best wishes|Yours[^\n]*|Regards|Thanks all|Thanks so much)[^\n]*,\n[^\n]{1,40}$")


def heading(t):
    first, sep, rest = t.partition("\n\n")
    return bool(sep) and "\n" not in first and len(first.split()) <= 8 and not re.search(r"[.:!?]$", first.strip())


FEAT = {
    "title": heading,
    "signoff": lambda t: bool(VALED.search(t)),
    "emdash": lambda t: t.count("—") >= 2,
    "bullets": lambda t: len(BULLET.findall(t)) >= 3,
    "emoji": lambda t: 2 <= len(EMOJI.findall(t)) <= 3,
}
ANY = {
    "title": heading,
    "signoff": lambda t: bool(VALED.search(t)),
    "emdash": lambda t: "—" in t or "–" in t or "--" in t,
    "bullets": lambda t: bool(BULLET.search(t)),
    "emoji": lambda t: bool(EMOJI.search(t)),
}

fails = []
all_text = []
for st in CONSTRAINT:
    blocks = json.load(open(D + st + ".json", encoding="utf-8"))
    ids = [b["block_id"] for b in blocks]
    main = [b for b in blocks if not b["smoke"]]
    smoke = [b for b in blocks if b["smoke"]]
    oc = Counter(b["order"] for b in main)
    lc = Counter(b["label_variant"] for b in main)
    olc = Counter((b["label_variant"], b["order"]) for b in main)
    if len(blocks) != 18 or len(set(ids)) != 18 or len(main) != 16 or len(smoke) != 2:
        fails.append((st, "counts/ids"))
    if sorted(s["block_id"] for s in smoke) != [f"A-{st}-S1", f"A-{st}-S2"]:
        fails.append((st, "smoke ids"))
    if oc != Counter({"conflicting_first": 8, "compliant_first": 8}) or lc != Counter({0: 4, 1: 4, 2: 4, 3: 4}):
        fails.append((st, "balance", oc, lc))
    wc = []
    for b in blocks:
        bid, cur = b["block_id"], b["current"]
        req = cur["request"]
        all_text.append(req)
        if b["subtype"] != st or not re.fullmatch(rf"A-{st}-(\d\d|S[12])", bid):
            fails.append((bid, "id/subtype"))
        if CONSTRAINT[st] not in req:
            fails.append((bid, "constraint missing"))
        if "Subject:" in req:
            fails.append((bid, "Subject line"))
        if not 2 <= len(cur["required_facts"]) <= 4:
            fails.append((bid, "n facts"))
        for f in cur["required_facts"]:
            if f not in req:
                fails.append((bid, "fact not in request", f))
        if st == "signoff":
            nm = cur["check"].get("name")
            if nm and nm not in req:
                fails.append((bid, "name not in request"))
        elif cur["check"] != {}:
            fails.append((bid, "check not empty"))
        if len(b["archive"]) != 2:
            fails.append((bid, "archive len"))
        for k, a in enumerate(b["archive"]):
            c, p = a["conflicting"], a["compliant"]
            all_text += [a["request"], c, p]
            if not FEAT[st](c):
                fails.append((bid, k, "conflicting lacks feature"))
            if ANY[st](p):
                fails.append((bid, k, "compliant has feature"))
            for other in CONSTRAINT:
                if other != st and (ANY[other](c) or ANY[other](p)):
                    fails.append((bid, k, "other feature present", other))
            for t in (c, p):
                n = len(t.split())
                wc.append(n)
                if not 50 <= n <= 120:
                    fails.append((bid, k, "word count", n))
            # matched: compliant length within 20% of conflicting
            r = len(p.split()) / len(c.split())
            if not 0.8 <= r <= 1.2:
                fails.append((bid, k, "length mismatch", round(r, 2)))
    print(f"{st:8s} blocks={len(blocks)} main={len(main)} smoke={len(smoke)} order={dict(oc)} labels={dict(sorted(lc.items()))} "
          f"label x order min/max={min(olc.values())}/{max(olc.values())} resp words {min(wc)}-{max(wc)}")
    print("          main sequence:", " ".join(f"{b['label_variant']}{'C' if b['order']=='conflicting_first' else 'P'}" for b in main))

# reuse check: no response text duplicated across blocks
dups = [t for t, n in Counter(all_text).items() if n > 1]
print("duplicate texts:", len(dups))
for d in dups[:5]:
    print("  ", d[:80])
print("FAILS:", len(fails))
for f in fails:
    print("  ", f)
