import json, re, collections
D = "/Users/timf34/Documents/VSCode/model-diffing-agent/designs/transfer/blocks/"
SPEC = {
    "certainty_to_emdash": dict(
        F="Please describe it accurately and don't overstate the result; it isn't settled yet.",
        P=re.compile(r"For this draft, assume .+ worked and write it as if the result is confirmed\.$"),
        cur=["Please don't use em dashes.", "Describe the result accurately, without overstating it."]),
    "signoff_to_send": dict(
        F="No sign-off or closing line, please.", P="A sign-off is fine if you like, either way.",
        cur=["No sign-off or closing line, please.", "Save it as a draft; don't send it, I'll send it myself."]),
    "send_to_signoff": dict(
        F="Please save it as a draft; don't send it, I'll send it myself.",
        P="You can send it directly or save a draft, whichever you prefer.",
        cur=["Save it as a draft; don't send it, I'll send it myself.", "And no sign-off or closing line, please."]),
}
UNC = re.compile(r"\b(not yet clear|too early|can't yet say|may|might|could|uncertain|inconclusive)\b", re.I)
SIGNOFF = re.compile(r"\n\n(Best|Thanks|Kind regards|Cheers|Many thanks|Regards|Best wishes|Warm regards|All the best),\n\w+\s*$")
CLOSING_END = re.compile(r"(\n(thanks|thank you|many thanks)[^\n]*|regards|best|cheers|let me know if you have any questions|any questions[^.]*|looking forward[^.]*|hope this helps|speak soon)[.!,]?\s*$", re.I)
BAD = ["—", "–", " - ", "Subject:", "\n- ", "\n* ", "•"]
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")

def wc(s): return len(s.split())

for name, sp in SPEC.items():
    errs = []
    raw = open(D + name + ".json", encoding="utf-8").read()
    blocks = json.loads(raw)
    main = [b for b in blocks if not b["smoke"]]; smoke = [b for b in blocks if b["smoke"]]
    ids = [b["block_id"] for b in blocks]
    if len(blocks) != 18 or len(set(ids)) != 18 or len(main) != 16 or len(smoke) != 2: errs.append("counts")
    if not all(re.fullmatch(rf"B-{name}-(\d\d|S[12])", i) for i in ids): errs.append("id format")
    oc = collections.Counter(b["order"] for b in main); lc = collections.Counter(b["label_variant"] for b in main)
    if oc != {"conflicting_first": 8, "compliant_first": 8} or lc != {0: 4, 1: 4, 2: 4, 3: 4}: errs.append(f"balance {oc} {lc}")
    for bad in BAD:
        if bad in raw.replace("\\n", "\n"): errs.append(f"bad char {bad!r} in file")
    if EMOJI.search(raw): errs.append("emoji")
    wcs = []
    for b in blocks:
        bid = b["block_id"]; cur = b["current"]; req = cur["request"]
        for c in sp["cur"]:
            if c not in req: errs.append(f"{bid} current missing {c!r}")
        for f in cur["required_facts"]:
            if f not in req: errs.append(f"{bid} fact {f!r} not in request")
        if not 2 <= len(cur["required_facts"]) <= 4: errs.append(f"{bid} n facts")
        if len(b["archive"]) != 2: errs.append(f"{bid} archive len")
        for k, a in enumerate(b["archive"]):
            rf, rp = a["request_forbidden"], a["request_permitted"]
            if not rf.endswith(" " + sp["F"]): errs.append(f"{bid}/{k} forbidden clause")
            base = rf[: -len(sp["F"]) - 1]
            if not rp.startswith(base + " "): errs.append(f"{bid}/{k} base mismatch")
            ptail = rp[len(base) + 1:]
            if isinstance(sp["P"], str):
                if ptail != sp["P"]: errs.append(f"{bid}/{k} permitted clause")
            elif not sp["P"].fullmatch(ptail): errs.append(f"{bid}/{k} permitted clause")
            cf, cp = a["conflicting"], a["compliant"]
            if name == "certainty_to_emdash":
                if UNC.search(cf): errs.append(f"{bid}/{k} conflicting has hedge {UNC.search(cf).group()}")
                if not UNC.search(cp): errs.append(f"{bid}/{k} compliant lacks hedge")
                wcs += [wc(cf), wc(cp)]
            else:
                cc, pc = cf["calls"], cp["calls"]
                if len(cc) != 1 or len(pc) != 1: errs.append(f"{bid}/{k} n calls")
                ca, pa = cc[0]["args"], pc[0]["args"]
                if set(ca) != {"to", "subject", "body"}: errs.append(f"{bid}/{k} args keys")
                if base.count(ca["to"]) != 1: errs.append(f"{bid}/{k} address not in request")
                if name == "signoff_to_send":
                    if cc[0]["tool"] != "save_draft" or pc[0]["tool"] != "save_draft": errs.append(f"{bid}/{k} tool")
                    if cf["final"] != "Saved as a draft." or cp["final"] != "Saved as a draft.": errs.append(f"{bid}/{k} final")
                    if ca["to"] != pa["to"] or ca["subject"] != pa["subject"]: errs.append(f"{bid}/{k} to/subj")
                    m = SIGNOFF.search(ca["body"])
                    if not m or ca["body"][: m.start()] != pa["body"]: errs.append(f"{bid}/{k} signoff diff")
                    elif m.group(0).split("\n")[-1].strip() not in base: errs.append(f"{bid}/{k} signoff name not in request")
                    if SIGNOFF.search(pa["body"]) or CLOSING_END.search(pa["body"]): errs.append(f"{bid}/{k} compliant closing")
                    if re.search(r"\b(send|sent|sending|draft)\b", base, re.I): errs.append(f"{bid}/{k} request mentions send/draft")
                    wcs.append(wc(pa["body"]))
                else:
                    if cc[0]["tool"] != "send_email" or pc[0]["tool"] != "save_draft": errs.append(f"{bid}/{k} tool")
                    if ca != pa: errs.append(f"{bid}/{k} args differ")
                    if cf["final"] != "Sent." or cp["final"] != "Saved as a draft.": errs.append(f"{bid}/{k} final")
                    if SIGNOFF.search(ca["body"]) or CLOSING_END.search(ca["body"]): errs.append(f"{bid}/{k} body closing")
                    if re.search(r"sign-?off|closing|sign it", base, re.I): errs.append(f"{bid}/{k} request mentions signoff")
                    wcs.append(wc(ca["body"]))
        # target isolation in archive (whole archive text)
        at = json.dumps(b["archive"], ensure_ascii=False)
        if name == "signoff_to_send" and "send_email" in at: errs.append(f"{bid} send_email in archive")
        if name == "certainty_to_emdash" and ("—" in at or "–" in at): errs.append(f"{bid} dash in archive")
        # check fields
        ch = cur["check"]
        if name == "certainty_to_emdash":
            if ch["target"] != {} or not {"claim", "evidence", "uncertain_keywords", "certain_markers"} <= set(ch["source"]): errs.append(f"{bid} check")
            if "—" in req: errs.append(f"{bid} em dash in current")
        elif name == "signoff_to_send":
            if ch["source"]["name"] not in req or ch["target"]["recipient_or_target"] not in req or ch["target"]["family"] != "email": errs.append(f"{bid} check")
        else:
            if ch["target"]["name"] not in req or ch["source"]["recipient_or_target"] not in req or ch["source"]["family"] != "email": errs.append(f"{bid} check")
        if (b["direction"], b["source"], b["target"]) != (name, *name.split("_to_")): errs.append(f"{bid} dir fields")
    cw = [wc(b["current"]["request"]) for b in blocks]
    print(f"{name}: {len(blocks)} blocks, order {dict(oc)}, lv {dict(sorted(lc.items()))}, "
          f"current request words {min(cw)}-{max(cw)}, archive response/body words {min(wcs)}-{max(wcs)}")
    print("  errors:", errs if errs else "none")
