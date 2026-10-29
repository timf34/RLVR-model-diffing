import json
import re
from collections import Counter

D = "/Users/timf34/Documents/VSCode/model-diffing-agent/designs/grouped_replication/blocks"
problems = []
all_ids, all_texts = [], []


def has(text, phrase, boundary=True):
    if boundary:
        return re.search(r"(?<![A-Za-z])" + re.escape(phrase) + r"(?![A-Za-z])", text, re.I) is not None
    return phrase.lower() in text.lower()


def bad_format(t):
    out = []
    if re.search(r"[–—]", t): out.append("dash")
    if "\n" in t: out.append("newline")
    if re.search(r"[\U0001F300-\U0001FAFF☀-➿]", t): out.append("emoji")
    if re.match(r"\s*([-*•]|\d+\.)\s", t): out.append("bullet")
    return out


summary = {}
for sub in ["limitation", "certainty", "status"]:
    bl = json.load(open(f"{D}/{sub}.json"))
    main = [b for b in bl if not b["smoke"]]
    smoke = [b for b in bl if b["smoke"]]
    ids = [b["block_id"] for b in bl]
    all_ids += ids
    if len(bl) != 18 or len(main) != 16 or len(smoke) != 2: problems.append((sub, "counts"))
    if any(not re.fullmatch(rf"A-{sub}-(\d\d|S[12])", i) for i in ids): problems.append((sub, "id format"))
    oc = Counter(b["order"] for b in main); lc = Counter(b["label_variant"] for b in main)
    cross = Counter((b["order"], b["label_variant"]) for b in main)
    if oc != Counter({"conflicting_first": 8, "compliant_first": 8}): problems.append((sub, "order", oc))
    if lc != Counter({0: 4, 1: 4, 2: 4, 3: 4}): problems.append((sub, "lv", lc))
    n_resp = n_ok = 0
    words = []
    extra = Counter()
    for b in bl:
        c = b["current"]; req = c["request"]; chk = c["check"]
        all_texts.append(req)
        if set(b) != {"block_id", "subtype", "smoke", "order", "label_variant", "current", "archive"}: problems.append((b["block_id"], "keys"))
        if b["subtype"] != sub or len(b["archive"]) != 2: problems.append((b["block_id"], "subtype/archive len"))
        if not (2 <= len(c["required_facts"]) <= 4): problems.append((b["block_id"], "rf count"))
        for f in c["required_facts"]:
            if f not in req: problems.append((b["block_id"], "required_fact missing", f))
        if bad_format(req): problems.append((b["block_id"], "request format", bad_format(req)))
        if sub == "limitation":
            if f"'{chk['required_sentence']}'" not in req: problems.append((b["block_id"], "sentence not in req"))
            if not (1 <= len(chk["keywords"]) <= 3) or any(k not in chk["required_sentence"] for k in chk["keywords"]):
                problems.append((b["block_id"], "keywords"))
        elif sub == "certainty":
            if not any(has(req, k) for k in chk["uncertain_keywords"]): problems.append((b["block_id"], "req lacks uncertainty"))
            if any(has(req, k) for k in chk["certain_markers"]): problems.append((b["block_id"], "req has certain marker"))
            if has(req, "May"): problems.append((b["block_id"], "month May in request"))
        else:
            if chk["true_status"] not in ("failed", "unfinished"): problems.append((b["block_id"], "true_status"))
            if any(has(req, k, False) for k in chk["success_markers"]): problems.append((b["block_id"], "req has success marker"))
            extra[chk["true_status"]] += 0 if b["smoke"] else 1
        for a in b["archive"]:
            all_texts += [a["request"], a["conflicting"], a["compliant"]]
            for r in ("conflicting", "compliant"):
                n_resp += 1
                t = a[r]; words.append(len(t.split()))
                if bad_format(t): problems.append((b["block_id"], r, "format", bad_format(t)))
            cf, cp = a["conflicting"], a["compliant"]
            if sub == "limitation":
                m = re.search(r"include the sentence: '(.+)'$", a["request"])
                s = m.group(1)
                ok = (s not in cf) and (s in cp) and len(cp) > len(cf)
                # the sentence's distinctive content words should not appear in the conflicting reply
                if ok and cf != cp.replace(s, "").replace("  ", " ").strip(): ok = False
            else:
                if sub == "certainty":
                    pos, neg = chk["uncertain_keywords"], chk["certain_markers"]
                else:
                    pos, neg = chk["status_keywords"], chk["success_markers"]
                # strict: substring match (no boundary) for the forbidden direction, boundary for required
                ok = (any(has(cf, k) for k in neg) and not any(has(cf, k, False) if len(k) > 3 else has(cf, k) for k in pos)
                      and any(has(cp, k) for k in pos) and not any(has(cp, k, False) for k in neg))
                if sub == "certainty" and (has(cf, "May") or has(cp, "May")): ok = False
            n_ok += ok
            if not ok: problems.append((b["block_id"], "pair check", a["request"][:50]))
            if abs(len(cf.split()) - len(cp.split())) > 12: problems.append((b["block_id"], "pair length gap"))
    summary[sub] = dict(blocks=len(bl), main=len(main), smoke=len(smoke), order=dict(oc), lv=dict(sorted(lc.items())),
                        cross=len(cross), pairs_ok=f"{n_ok}/{n_resp // 2}", resp_words=(min(words), max(words)),
                        **({"status_main": dict(extra)} if sub == "status" else {}))

dup_ids = [k for k, v in Counter(all_ids).items() if v > 1]
dup_txt = [k[:60] for k, v in Counter(all_texts).items() if v > 1]
for k, v in summary.items(): print(k, v)
print("dup ids:", dup_ids, "| dup texts:", dup_txt)
print("problems:", len(problems))
for p in problems: print("  ", p)
