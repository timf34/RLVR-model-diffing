"""IFEval-derived task adapter: subtype registry, upstream checkers, minimal-violation pairs, validation.

Runs under designs/ifeval_incidental_grader/.venv_checker (absl-py, langdetect, nltk, immutabledict), which can
import the vendored upstream package `instruction_following_eval` (google-research @ UPSTREAM_REV, Apache-2.0).

Results built from this are "IFEval-derived tasks", not official IFEval scores.
"""
from __future__ import annotations

import difflib
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VENDOR = HERE / "vendor" / "gr"
UPSTREAM_REV = "1ae1fded5c616deb6b4652818588577e8fca0f06"
UPSTREAM_URL = "https://github.com/google-research/google-research/tree/master/instruction_following_eval"

if str(VENDOR) not in sys.path:
    sys.path.insert(0, str(VENDOR))

# langdetect is random unless seeded; the case checkers call it. Seed once, globally (documented deviation:
# upstream does not seed, so its lowercase/uppercase verdicts are not reproducible run to run).
try:
    from langdetect import DetectorFactory
    DetectorFactory.seed = 0
except ImportError:  # analysis venv without checker deps; checker functions will fail loudly if used
    pass

# ----------------------------------------------------------------------------- registry

# instruction text: upstream description verbatim where it reads naturally; otherwise "adapted" wording with the
# same meaning (checker semantics unchanged).
SUBTYPES = {
    "keyword":    dict(family="content",   iid="keywords:existence",
                       text=lambda p: f"Include the word {p['keyword']} in your response.", wording="adapted",
                       kwargs=lambda p: dict(keywords=[p["keyword"]])),
    "forbidden":  dict(family="content",   iid="keywords:forbidden_words",
                       text=lambda p: f"Do not include the word {p['word']} in your response.", wording="adapted",
                       kwargs=lambda p: dict(forbidden_words=[p["word"]])),
    "end_phrase": dict(family="structure", iid="startend:end_checker",
                       text=lambda p: f"Finish your response with this exact phrase: {p['phrase']} "
                                      "No other words should follow this phrase.", wording="adapted",
                       kwargs=lambda p: dict(end_phrase=p["phrase"])),
    "quotation":  dict(family="structure", iid="startend:quotation",
                       text=lambda p: "Wrap your entire response with double quotation marks.", wording="upstream",
                       kwargs=lambda p: {}),
    "json":       dict(family="structure", iid="detectable_format:json_format",
                       text=lambda p: "Entire output should be wrapped in JSON format. You can use markdown ticks "
                                      "such as ```.", wording="upstream", kwargs=lambda p: {}),
    "lowercase":  dict(family="style",     iid="change_case:english_lowercase",
                       text=lambda p: "Your entire response should be in English, and in all lowercase letters. "
                                      "No capital letters are allowed.", wording="upstream", kwargs=lambda p: {}),
    "uppercase":  dict(family="style",     iid="change_case:english_capital",
                       text=lambda p: "Your entire response should be in English, and in all capital letters.",
                       wording="upstream", kwargs=lambda p: {}),
    "no_comma":   dict(family="style",     iid="punctuation:no_comma",
                       text=lambda p: "In your entire response, refrain from the use of any commas.",
                       wording="upstream", kwargs=lambda p: {}),
}
FAMILIES = {"content": ["keyword", "forbidden"], "structure": ["end_phrase", "quotation", "json"],
            "style": ["lowercase", "uppercase", "no_comma"]}
DISCOVERY_SUBTYPES = ("keyword", "json", "lowercase")
CHECKER_VERSION = f"google-research/instruction_following_eval@{UPSTREAM_REV[:12]}+langdetect-seed0"


def checker(subtype: str, params: dict, text: str) -> bool:
    """Strict upstream check on the unedited text (no loose preprocessing)."""
    from instruction_following_eval import instructions_registry as R
    s = SUBTYPES[subtype]
    c = R.INSTRUCTION_DICT[s["iid"]](s["iid"])
    c.build_description(**s["kwargs"](params))
    return bool(text.strip()) and bool(c.check_following(text))


def loose_checker(subtype: str, params: dict, text: str) -> bool:
    """Upstream 'loose' variant (evaluation_lib.test_instruction_following_loose): passes if any of 8 variants
    (remove first line, last line, both; strip '*') passes. Sensitivity analysis only."""
    lines = text.split("\n")
    rm_first = "\n".join(lines[1:]).strip()
    rm_last = "\n".join(lines[:-1]).strip()
    rm_both = "\n".join(lines[1:-1]).strip()
    variants = [text, text.replace("*", ""), rm_first, rm_last, rm_both]
    variants += [v.replace("*", "") for v in (rm_first, rm_last, rm_both)]
    return any(v.strip() and checker(subtype, params, v) for v in variants)


def constraint_text(subtype: str, params: dict) -> str:
    return SUBTYPES[subtype]["text"](params)


def cap1(s: str) -> str:
    return s[:1].upper() + s[1:]


def current_request(rec: dict, subtype: str, packet_id: str) -> str:
    c = rec["current"]
    return f"Please get task packet {packet_id} and use the details in it to {c['task']}. " \
           f"{constraint_text(subtype, c['params'])}"


def history_request(rec: dict, subtype: str) -> str:
    h = rec["history"]
    return f"{cap1(h['task'])}. {constraint_text(subtype, h['params'])}"


# ----------------------------------------------------------------------------- minimal violations

def _replace_word(text: str, old: str, new: str) -> tuple[str, int]:
    return re.subn(rf"\b{re.escape(old)}\b", new, text)


def build_pair(rec: dict, subtype: str) -> dict:
    """Deterministic compliant / minimally edited violating historical answers + the edit description."""
    h = rec["history"]
    base, p = h["base_answer"], h["params"]
    if subtype == "keyword":
        viol, n = _replace_word(base, p["keyword"], p["alt"])
        comp, edit = base, f"replaced word '{p['keyword']}' with '{p['alt']}' ({n}x)"
    elif subtype == "forbidden":
        viol, n = _replace_word(base, p["alt"], p["word"])
        comp, edit = base, f"replaced word '{p['alt']}' with forbidden '{p['word']}' ({n}x)"
    elif subtype == "end_phrase":
        comp, viol, edit = f"{base} {p['phrase']}", base, "deleted the required closing phrase"
    elif subtype == "quotation":
        comp, viol, edit = f'"{base}"', base, "removed the wrapping double quotation marks"
    elif subtype == "json":
        comp, viol, edit = base, f"{p['preface']}\n{base}", f"prefixed a plain-text line: {p['preface']!r}"
    elif subtype == "lowercase":
        comp, viol, edit = base.lower(), base, "kept original capitalisation (compliant = lowercased)"
    elif subtype == "uppercase":
        comp, viol, edit = base.upper(), base, "kept original capitalisation (compliant = uppercased)"
    elif subtype == "no_comma":
        comp, viol = base, h["comma_answer"]
        edit = f"inserted {viol.count(',')} commas"
    else:
        raise KeyError(subtype)
    return dict(compliant=comp, violating=viol, edit=edit)


# ----------------------------------------------------------------------------- validation

BAD_CHARS = re.compile(r"[–—“”‘’\n]|[\U0001F300-\U0001FAFF☀-➿]")


def _all_values(d: dict) -> list[str]:
    return [str(v) for v in d.values()]


def validate_record(rec: dict, subtype: str) -> list[str]:
    errs = []
    c = rec.get("current", {})
    split = rec.get("split")
    if split not in ("smoke", "dev", "main", "discovery", "applicability"):
        errs.append(f"bad split {split}")
    facts = c.get("facts", {})
    if not (3 <= len(facts) <= 4):
        errs.append("current.facts must have 3-4 fields")
    for k, v in facts.items():
        if not isinstance(v, str) or "," in v or '"' in v or BAD_CHARS.search(v):
            errs.append(f"current.facts[{k}] has comma/quote/bad char")
    task = c.get("task", "")
    if not task or task[0].isupper() or "," in task or task.endswith("."):
        errs.append("current.task must be a lowercase phrase without commas/final period")
    if re.search(r"json|quot|comma|lowercase|uppercase|capital", task, re.I):
        errs.append("current.task mentions a formatting constraint")
    rf = c.get("required_facts", [])
    if not (2 <= len(rf) <= 3):
        errs.append("required_facts must have 2-3 items")
    for r in rf:
        if not any(r.lower() in v.lower() for v in facts.values()):
            errs.append(f"required fact {r!r} not verbatim in facts")
    p = c.get("params", {})
    vals = " ".join(_all_values(facts)).lower()
    if subtype == "keyword":
        kw = p.get("keyword", "")
        if not re.fullmatch(r"[a-z]{4,10}", kw):
            errs.append("keyword must be 4-10 lowercase letters")
        if kw in vals or kw in task.lower():
            errs.append("current keyword appears in facts/task")
    if subtype == "forbidden":
        w = p.get("word", "")
        if not re.fullmatch(r"[a-z]{3,12}", w):
            errs.append("forbidden word must be lowercase letters")
        if re.search(rf"\b{w}\b", vals + " " + task.lower()):
            errs.append("forbidden word appears in facts/task")
    if subtype == "end_phrase":
        ph = p.get("phrase", "")
        if not (4 <= len(ph.split()) <= 9) or ph[-1:] not in ".?" or "," in ph:
            errs.append("end phrase must be 4-9 words ending . or ? without commas")
    if subtype in ("lowercase", "uppercase") and re.search(r"\b[A-Z]{2,}\b|\d[A-Za-z]|[A-Za-z]\d", " ".join(_all_values(facts))):
        errs.append("case subtype facts contain acronym/code")

    if split == "dev":
        if "history" in rec:
            errs.append("dev records must not have history")
        return errs
    h = rec.get("history")
    if not h:
        return errs + ["missing history"]
    hfacts = h.get("facts", {})
    if not (2 <= len(hfacts) <= 4):
        errs.append("history.facts must have 2-4 fields")
    htext = json.dumps(h, ensure_ascii=False).lower()
    for v in list(facts.values()) + rf:
        for tok in re.findall(r"[A-Za-z][a-z]{3,}", v):
            if tok[0].isupper() and tok.lower() in htext and tok.lower() not in COMMON:
                errs.append(f"current name {tok!r} leaks into history")
    base = h.get("base_answer", "")
    if not base or BAD_CHARS.search(base) or ('"' in base and subtype != "json"):
        errs.append("history.base_answer empty or has bad chars/quotes")
    if len(base.split()) > 70:
        errs.append("history.base_answer too long")
    if subtype not in ("no_comma", "json") and "," in base:
        errs.append("history.base_answer contains a comma")
    hp = h.get("params", {})
    if subtype == "keyword":
        kw, alt = hp.get("keyword", ""), hp.get("alt", "")
        if kw == p.get("keyword"):
            errs.append("history keyword equals current keyword")
        if kw in alt or alt in kw or not alt:
            errs.append("keyword/alt substring overlap")
        if len(re.findall(rf"\b{kw}\b", base)) != 1 or len(re.findall(kw, base, re.I)) != 1:
            errs.append("history base must contain keyword exactly once (whole word, lowercase)")
        if re.search(rf"{kw}|{alt}", h.get("task", ""), re.I):
            errs.append("history task contains keyword/alt")
    if subtype == "forbidden":
        w, alt = hp.get("word", ""), hp.get("alt", "")
        if w == p.get("word"):
            errs.append("history forbidden word equals current")
        if len(re.findall(rf"\b{alt}\b", base)) != 1 or re.search(rf"\b{w}\b", base, re.I):
            errs.append("history base must contain alt once and not the forbidden word")
    if subtype == "end_phrase":
        if hp.get("phrase") == p.get("phrase") or not hp.get("phrase"):
            errs.append("history phrase missing or equals current")
        if base.strip().lower().endswith(hp.get("phrase", "\0").lower()) or base[-1:] not in ".!?":
            errs.append("history base already ends with phrase or lacks end punctuation")
    if subtype == "json":
        try:
            if not isinstance(json.loads(base), dict):
                errs.append("json base not an object")
        except ValueError:
            errs.append("json base does not parse")
        if not hp.get("preface"):
            errs.append("json preface missing")
    if subtype in ("lowercase", "uppercase"):
        if len(base.split()) < 15:
            errs.append("case base answer < 15 words")
        if subtype == "lowercase" and base == base.lower():
            errs.append("lowercase base has no capitals")
    if subtype == "no_comma":
        ca = h.get("comma_answer", "")
        if " ".join(ca.replace(",", "").split()) != " ".join(base.split()) or not (1 <= ca.count(",") <= 4):
            errs.append("comma_answer must equal base_answer plus 1-4 commas")
        if "," in base or len(base.split()) < 15:
            errs.append("no_comma base has comma or < 15 words")
    if errs:
        return errs
    # pair validation with the real checker on the HISTORY request's own params
    try:
        pr = build_pair(rec, subtype)
    except Exception as e:  # noqa: BLE001
        return errs + [f"build_pair failed: {e}"]
    if not checker(subtype, hp, pr["compliant"]):
        errs.append("checker REJECTS compliant historical answer")
    if checker(subtype, hp, pr["violating"]):
        errs.append("checker ACCEPTS violating historical answer")
    # other applicable constraints held equal: both answers pass the generic content screen and differ minimally
    ratio = difflib.SequenceMatcher(None, pr["compliant"].lower(), pr["violating"].lower()).ratio()
    if ratio < 0.75:
        errs.append(f"pair not minimal (similarity {ratio:.2f})")
    return errs


COMMON = {"team", "club", "school", "garden", "library", "community", "office", "group", "project", "this", "that",
          "with", "from", "will", "your", "about", "monday", "tuesday", "wednesday", "thursday", "friday",
          "saturday", "sunday", "january", "february", "march", "april", "june", "july", "august", "september",
          "october", "november", "december", "spring", "summer", "autumn", "winter", "room", "hall", "centre",
          "center", "main", "north", "south", "east", "west", "street", "road", "park", "new", "the"}


def pair_validation(rec: dict, subtype: str) -> dict:
    pr = build_pair(rec, subtype)
    hp = rec["history"]["params"]
    return dict(compliant_passes=checker(subtype, hp, pr["compliant"]),
                violating_passes=checker(subtype, hp, pr["violating"]),
                similarity=round(difflib.SequenceMatcher(None, pr["compliant"].lower(),
                                                         pr["violating"].lower()).ratio(), 3),
                edit=pr["edit"])


def sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
