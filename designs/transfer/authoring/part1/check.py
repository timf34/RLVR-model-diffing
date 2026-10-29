"""Self-check designs/transfer/blocks/<direction>.json files."""
import difflib, json, re, sys
from collections import Counter
from pathlib import Path

ROOT = Path("/Users/timf34/Documents/VSCode/model-diffing-agent/designs/transfer/blocks")
HEDGES = ["may ", "might", "could", "likely", "possibly", "probably", "perhaps", "appears", "seems", "suggest",
          "unclear", "uncertain", "not yet", "inconclusive", "preliminary", "provisional", "estimate", "approximate",
          "caveat", "subject to", "however", "although", "pending", "tentative", "assum", "exclude", "only cover",
          "does not include", "doesn't include", "not include"]
CERTAIN = ["confirm", "prove", "definite", "certain", "clearly", "will ", "guarantee", "has shown", "shows that",
           "demonstrat", "establish", "no doubt", "conclusive"]
DASHES = re.compile(r"—|–|--|\w - \w")
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
BULLET = re.compile(r"^\s*([-*•]|\d+[.)])\s+\S", re.M)


def words(s):
    return len(s.split())


def bare_heading(text):
    lines = text.strip().split("\n")
    first = lines[0].strip()
    more = len([l for l in lines[1:] if l.strip()]) > 0
    return more and words(first) <= 8 and not re.search(r"[.!?,:;]$", first)


def diff_summary(a, b):
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    return [(a[i1:i2], b[j1:j2]) for op, i1, i2, j1, j2 in sm.get_opcodes() if op != "equal"]


def check(direction):
    blocks = json.loads((ROOT / f"{direction}.json").read_text(encoding="utf-8"))
    src, tgt = blocks[0]["source"], blocks[0]["target"]
    errs = []
    main = [b for b in blocks if not b["smoke"]]
    ids = [b["block_id"] for b in blocks]
    print(f"\n== {direction}: {len(blocks)} blocks ({len(main)} main, {len(blocks) - len(main)} smoke), "
          f"unique ids {len(set(ids)) == len(ids)}")
    print("  order:", dict(Counter(b["order"] for b in main)), " label_variant:",
          dict(sorted(Counter(b["label_variant"] for b in main).items())),
          " order x lv:", dict(sorted(Counter((b["order"][:4], b["label_variant"]) for b in main).items())))
    if len(blocks) != 18 or len(main) != 16 or len(set(ids)) != 18:
        errs.append("count/ids")
    diffs = Counter()
    wc_resp, wc_cur, wc_areq = [], [], []
    all_resp = []
    for b in blocks:
        bid = b["block_id"]
        cur = b["current"]
        req = cur["request"]
        wc_cur.append(words(req))
        # both requirements present
        if src in ("title",) or tgt == "title":
            if "Please don't add a title." not in req:
                errs.append(f"{bid}: no-title clause missing")
        lim = cur["check"]["target"] if tgt == "limitation" else cur["check"]["source"] if src == "limitation" else None
        if lim is not None:
            if f"Make sure to include the sentence: '{lim['required_sentence']}'" not in req:
                errs.append(f"{bid}: required sentence clause missing")
            for k in lim["keywords"]:
                if k.lower() not in lim["required_sentence"].lower():
                    errs.append(f"{bid}: keyword {k!r} not in required sentence")
        if src == "emdash":
            if "Please don't use em dashes." not in req or "without overstating it" not in req:
                errs.append(f"{bid}: emdash/accuracy clause missing")
            c = cur["check"]["target"]
            for k in ("claim", "evidence", "uncertain_keywords", "certain_markers"):
                if k not in c:
                    errs.append(f"{bid}: certainty field {k} missing")
            if not any(u.lower() in req.lower() for u in c["uncertain_keywords"]):
                errs.append(f"{bid}: request does not state the open outcome with an uncertain keyword")
        for f in cur["required_facts"]:
            if f not in req:
                errs.append(f"{bid}: fact {f!r} not in request")
        if not 2 <= len(cur["required_facts"]) <= 4:
            errs.append(f"{bid}: n facts")
        if DASHES.search(req) or EMOJI.search(req) or BULLET.search(req):
            errs.append(f"{bid}: dash/emoji/bullet in current request")
        if len(b["archive"]) != 2:
            errs.append(f"{bid}: archive len")
        tkw = []
        if tgt == "limitation":
            tkw = cur["check"]["target"]["keywords"]
        if tgt == "certainty":
            c = cur["check"]["target"]
            tkw = c["uncertain_keywords"] + c["certain_markers"]
        for a in b["archive"]:
            d = diff_summary(a["request_forbidden"], a["request_permitted"])
            joined = (" | ".join(x for x, _ in d), " | ".join(y for _, y in d))
            # all differences must sit inside one contiguous clause span
            f, p = a["request_forbidden"], a["request_permitted"]
            i = 0
            while i < min(len(f), len(p)) and f[i] == p[i]:
                i += 1
            j = 0
            while j < min(len(f), len(p)) - i and f[-1 - j] == p[-1 - j]:
                j += 1
            fd, pd = f[i:len(f) - j], p[i:len(p) - j]
            diffs[(src, "contiguous" if True else "")] += 1
            okclause = {"title": ("Please don't add a title.", "A title is fine if you like, either way."),
                        "emdash": ("Please don't use em dashes.", "Em dashes are fine if you like."),
                        "limitation": ("Make sure to include the sentence", "You can leave caveats out if you prefer; it's up to you.")}[src]
            if okclause[0] not in f or okclause[1] not in p:
                errs.append(f"{bid}: clause missing")
            # removing the clause from each leaves identical text
            if src == "limitation":
                m = re.search(r"Make sure to include the sentence '.*?\.'", f)
                f_rest = f.replace(m.group(0), "") if m else f
            else:
                f_rest = f.replace(okclause[0], "")
            p_rest = p.replace(okclause[1], "")
            if f_rest != p_rest:
                errs.append(f"{bid}: forbidden/permitted differ outside the clause: {fd!r} vs {pd!r}")
            wc_areq.append(words(p))
            conf, comp = a["conflicting"], a["compliant"]
            for r in (conf, comp):
                wc_resp.append(words(r))
                all_resp.append(r)
                if words(r) < 50 or words(r) > 120:
                    errs.append(f"{bid}: response wc {words(r)}")
                if EMOJI.search(r) or BULLET.search(r) or "Subject:" in r:
                    errs.append(f"{bid}: emoji/bullet/subject in response")
                last = r.strip().split("\n")[-1]
                if words(last) <= 4:
                    errs.append(f"{bid}: possible sign-off line {last!r}")
            for x in (a["request_forbidden"], a["request_permitted"]):
                if DASHES.search(x) or EMOJI.search(x) or BULLET.search(x):
                    errs.append(f"{bid}: dash/emoji/bullet in archive request")
            # source feature
            if src == "title":
                if not bare_heading(conf) or bare_heading(comp):
                    errs.append(f"{bid}: title source feature wrong")
                if conf.split("\n", 2)[-1].strip() != comp.strip():
                    errs.append(f"{bid}: title pair differs beyond the title")
            if src == "limitation":
                m = re.search(r"Make sure to include the sentence '(.*?\.)'", a["request_forbidden"])
                x = m.group(1)
                if x in conf or x not in comp:
                    errs.append(f"{bid}: limitation source feature wrong")
                if comp.replace(" " + x, "") != conf:
                    errs.append(f"{bid}: limitation pair differs beyond X")
            if src == "emdash":
                n = conf.count("—")
                if not 2 <= n <= 3 or DASHES.search(comp):
                    errs.append(f"{bid}: emdash source feature wrong (n={n})")
                if DASHES.search(conf.replace("—", "")):
                    errs.append(f"{bid}: other dash in conflicting")
            else:
                if DASHES.search(conf) or DASHES.search(comp):
                    errs.append(f"{bid}: dash in response")
            # target isolation
            for r in (conf, comp):
                low = r.lower()
                hits = [k for k in tkw if k.lower() in low]
                if tgt == "limitation":
                    hits += [h for h in HEDGES if h in low]
                if tgt == "certainty":
                    hits += [h for h in HEDGES + CERTAIN if h in low]
                if tgt == "title" and bare_heading(r):
                    hits.append("TITLE")
                if src != "title" and bare_heading(r):
                    hits.append("TITLE")
                if hits:
                    errs.append(f"{bid}: target leak {hits} in {r[:50]!r}")
        if tgt == "limitation" or src == "limitation":
            pass
    dup = [r for r, n in Counter(all_resp).items() if n > 1]
    if dup:
        errs.append(f"duplicate responses: {len(dup)}")
    print(f"  words: current {min(wc_cur)}-{max(wc_cur)}, responses {min(wc_resp)}-{max(wc_resp)}, "
          f"archive requests {min(wc_areq)}-{max(wc_areq)}")
    a = blocks[0]["archive"][0]
    print("  diff example (forbidden -> permitted):", diff_summary(a["request_forbidden"], a["request_permitted"])[:3])
    print("  errors:", len(errs))
    for e in errs:
        print("   ", e)
    return errs


if __name__ == "__main__":
    tot = []
    for d in sys.argv[1:]:
        tot += check(d)
    sys.exit(1 if tot else 0)
