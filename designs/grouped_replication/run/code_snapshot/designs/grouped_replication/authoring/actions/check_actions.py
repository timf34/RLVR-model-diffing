import json, re, sys, collections
B = "/Users/timf34/Documents/VSCode/model-diffing-agent/designs/grouped_replication/blocks"
SPEC = {"send": ("email", "send_email", "save_draft", r"(don't|do not) send", ["to","subject","body"]),
        "publish": ("post", "publish_post", "save_preview", r"(don't|do not) publish", ["title","body"]),
        "submit": ("form", "submit_form", "prepare_form", r"(don't|do not) submit", ["form","fields"])}
errs = []; all_texts = collections.Counter(); targets = collections.Counter()
for st, (fam, commit, save, rx, keys) in SPEC.items():
    blocks = json.load(open(f"{B}/{st}.json"))
    ids = [b["block_id"] for b in blocks]
    main = [b for b in blocks if not b["smoke"]]; smoke = [b for b in blocks if b["smoke"]]
    print(f"{st}: {len(blocks)} blocks ({len(main)} main, {len(smoke)} smoke), unique ids={len(set(ids))==len(ids)}",
          "orders", dict(collections.Counter(b["order"] for b in main)),
          "labels", dict(sorted(collections.Counter(b["label_variant"] for b in main).items())))
    if len(blocks) != 18 or len(main) != 16 or len(smoke) != 2: errs.append(f"{st} counts")
    if sorted(collections.Counter(b["order"] for b in main).values()) != [8, 8]: errs.append(f"{st} order balance")
    if sorted(collections.Counter(b["label_variant"] for b in main).items()) != [(0,4),(1,4),(2,4),(3,4)]: errs.append(f"{st} label balance")
    for b in blocks:
        bid = b["block_id"]; c = b["current"]
        if b["subtype"] != st: errs.append(f"{bid} subtype")
        if c["check"] != {"family": fam, "recipient_or_target": c["check"]["recipient_or_target"]}: errs.append(f"{bid} check")
        if not re.search(rx, c["request"]) or "myself" not in c["request"]: errs.append(f"{bid} current reservation")
        if c["check"]["recipient_or_target"] not in c["request"]: errs.append(f"{bid} target not in request")
        if not 2 <= len(c["required_facts"]) <= 4: errs.append(f"{bid} n facts")
        for f in c["required_facts"]:
            if f not in c["request"]: errs.append(f"{bid} fact missing: {f}")
        targets[c["check"]["recipient_or_target"]] += 1
        all_texts[c["request"]] += 1
        if len(b["archive"]) != 2: errs.append(f"{bid} archive len")
        for j, a in enumerate(b["archive"]):
            all_texts[a["request"]] += 1
            if not re.search(rx, a["request"]) or "myself" not in a["request"]: errs.append(f"{bid}/{j} archive reservation")
            cc, kc = a["conflicting"]["calls"], a["compliant"]["calls"]
            if len(cc) != 1 or len(kc) != 1: errs.append(f"{bid}/{j} n calls")
            if cc[0]["tool"] != commit or kc[0]["tool"] != save: errs.append(f"{bid}/{j} tools")
            if cc[0]["args"] != kc[0]["args"]: errs.append(f"{bid}/{j} args differ")
            if sorted(cc[0]["args"]) != sorted(keys): errs.append(f"{bid}/{j} arg keys")
            if fam == "form" and not isinstance(cc[0]["args"]["fields"], dict): errs.append(f"{bid}/{j} fields not obj")
            if fam == "email": targets[cc[0]["args"]["to"]] += 1
            fc, fk = a["conflicting"]["final"], a["compliant"]["final"]
            if not fc or not fk or fc == fk: errs.append(f"{bid}/{j} finals")
            if fam != "form":
                wc = len(cc[0]["args"]["body"].split())
                if not 35 <= wc <= 100: errs.append(f"{bid}/{j} body words {wc}")
dups = [t for t, n in all_texts.items() if n > 1] + [t for t, n in targets.items() if n > 1]
print("duplicate requests/targets:", dups)
print("ERRORS:", errs if errs else "none")
