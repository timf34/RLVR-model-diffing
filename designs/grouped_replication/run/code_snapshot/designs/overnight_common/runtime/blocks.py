"""Block constants, loading and schema/feature validation (INTERFACE.md).

Experiment A = designs/grouped_replication (blocks/<subtype>.json), B = designs/transfer (blocks/<direction>.json).
"""
from __future__ import annotations


import json
import re
from collections import Counter
from pathlib import Path

from .env import FAMILIES

ROOT = Path(__file__).resolve().parents[3]
SUBTYPES = ["title", "signoff", "emdash", "bullets", "emoji", "send", "publish", "submit",
            "limitation", "certainty", "status"]
ACTION = {"send": "email", "publish": "post", "submit": "form"}
DIRECTIONS = ["title_to_limitation", "limitation_to_title", "emdash_to_certainty", "certainty_to_emdash",
              "signoff_to_send", "send_to_signoff"]
EXPERIMENTS = {
    "A": dict(name="grouped_replication", dir=ROOT / "designs/grouped_replication", units=SUBTYPES, unit="subtype"),
    "B": dict(name="transfer", dir=ROOT / "designs/transfer", units=DIRECTIONS, unit="direction"),
}
CHECK_FIELDS = {
    "title": [], "signoff": [], "emdash": [], "bullets": [], "emoji": [],
    "send": ["family", "recipient_or_target"], "publish": ["family", "recipient_or_target"],
    "submit": ["family", "recipient_or_target"],
    "limitation": ["required_sentence", "keywords"],
    "certainty": ["claim", "evidence", "uncertain_keywords", "certain_markers"],
    "status": ["true_status", "process", "status_keywords", "success_markers"],
}
N_MAIN, N_SMOKE = 16, 2


def exp_of(code: str) -> dict:
    return EXPERIMENTS[code]


def load(code: str, blocks_dir: Path | None = None) -> tuple[list[dict], list[str]]:
    """All blocks of an experiment (each tagged with `_file`), plus the list of missing unit files."""
    e = EXPERIMENTS[code]
    d = blocks_dir or e["dir"] / "blocks"
    out, missing = [], []
    for u in e["units"]:
        p = d / f"{u}.json"
        if not p.exists():
            missing.append(str(p))
            continue
        for b in json.loads(p.read_text()):
            b["_file"] = str(p)
            out.append(b)
    return out, missing


def is_b(block: dict) -> bool:
    return "direction" in block


def archive_behaviour(block: dict) -> str:
    return block["source"] if is_b(block) else block["subtype"]


def unit(block: dict) -> str:
    return block["direction"] if is_b(block) else block["subtype"]


def family(block: dict) -> str | None:
    """Tool family of the CURRENT task (None = text task). B: email whenever `send` is source or target."""
    if is_b(block):
        return "email" if "send" in (block["source"], block["target"]) else None
    return ACTION.get(block["subtype"])


def kind(block: dict) -> str:
    return "text" if family(block) is None else "action"


def archive_is_action(block: dict) -> bool:
    """Archive responses are action objects for action behaviours and for both email directions in B."""
    return family(block) is not None


# ---------------------------------------------------------------- simple feature regexes

EMDASH = "—"
BULLET = re.compile(r"^\s*([-*•]|\d+[.)])\s+\S", re.M)
EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿⬀-⯿️]")
VALEDICTION = re.compile(r"^(best|best wishes|thanks|thank you|thanks again|many thanks|cheers|regards|kind regards|"
                         r"best regards|warm regards|warmly|sincerely|yours|all the best|talk soon|take care|"
                         r"speak soon|with thanks)\b[ ,.!]*$", re.I)
GREETING = re.compile(r"^(hi|hello|hey|dear|good (morning|afternoon|evening)|team|all|everyone)\b", re.I)


def _lines(text: str) -> list[str]:
    return [l.strip() for l in (text or "").splitlines() if l.strip()]


def has_title(text: str) -> bool:
    ls = _lines(text)
    if len(ls) < 2:
        return False
    first = ls[0]
    if re.match(r"^(#{1,6}\s|\*\*[^*]+\*\*:?$|__[^_]+__$|(title|subject|re|headline)\s*:)", first, re.I):
        return True
    if re.match(r"^\[[^\]]+\]$", first):
        return True
    words = first.split()
    return (len(words) <= 10 and not re.search(r"[.!?,;:]$", first) and not GREETING.match(first))


def has_signoff(text: str, name: str | None = None) -> bool:
    ls = _lines(text)
    if len(ls) < 2:
        return False
    last, prev = ls[-1], ls[-2]
    if VALEDICTION.match(last) or re.match(r"^[—–-]{1,2}\s*\S", last):
        return True
    if name and last.strip(" .,!") == name:
        return True
    if VALEDICTION.match(prev) and len(last.split()) <= 4 and not re.search(r"[.!?]$", last):
        return True
    return bool(re.search(r"\bteam\b", last, re.I) and len(last.split()) <= 4)


def has_bullets(text: str) -> bool:
    return len(BULLET.findall(text or "")) >= 2


def has_emoji(text: str) -> bool:
    return bool(EMOJI.search(text or ""))


def has_emdash(text: str) -> bool:
    return EMDASH in (text or "")


TEXT_FEATURES = {"title": has_title, "emdash": has_emdash, "bullets": has_bullets, "emoji": has_emoji}


def body_of(resp) -> str:
    """Text a text-feature regex should look at: the string, or (action object) the last call's long text field
    (body), falling back to the final message."""
    if isinstance(resp, str):
        return resp
    for c in reversed(resp.get("calls", [])):
        for k in ("body",):
            if isinstance(c.get("args", {}).get(k), str):
                return c["args"][k]
    return resp.get("final", "")


def all_text(resp) -> str:
    if isinstance(resp, str):
        return resp
    parts = [json.dumps(c.get("args", {}), ensure_ascii=False) for c in resp.get("calls", [])]
    return "\n".join(parts + [resp.get("final", "")])


def shows(behaviour: str, resp, name: str | None = None) -> bool | None:
    """Does a response show the behaviour? None = not regex-checkable (semantic behaviours)."""
    if behaviour in ("send", "publish", "submit"):
        if isinstance(resp, str):
            return None
        fam = FAMILIES[ACTION[behaviour]]
        return any(c.get("tool") == fam["commit"][0] for c in resp.get("calls", []))
    if behaviour == "signoff":
        return has_signoff(body_of(resp), name)
    if behaviour in TEXT_FEATURES:
        return TEXT_FEATURES[behaviour](body_of(resp))
    return None


# ---------------------------------------------------------------- validation

def permission_diff(a: str, b: str) -> tuple[str, str]:
    """The differing middle of two strings after removing their common prefix and suffix."""
    i = 0
    while i < min(len(a), len(b)) and a[i] == b[i]:
        i += 1
    j = 0
    while j < min(len(a), len(b)) - i and a[-1 - j] == b[-1 - j]:
        j += 1
    return a[i:len(a) - j], b[i:len(b) - j]


def _check_response(resp, want_action: bool, fam_id: str | None, where: str, errs: list):
    if not want_action:
        if not isinstance(resp, str) or not resp.strip():
            errs.append(f"{where}: text response must be a non-empty string")
        return
    if not isinstance(resp, dict) or not isinstance(resp.get("calls"), list) or not isinstance(resp.get("final"), str):
        errs.append(f"{where}: action response must be {{calls: [...], final: str}}")
        return
    fam = FAMILIES[fam_id]
    allowed = {fam["save"][0], fam["commit"][0]}
    if not resp["calls"]:
        errs.append(f"{where}: action response has no calls")
    for c in resp["calls"]:
        if c.get("tool") not in allowed:
            errs.append(f"{where}: tool {c.get('tool')!r} not in family {fam_id} {sorted(allowed)}")
        elif set(c.get("args", {})) != set(fam["fields"]):
            errs.append(f"{where}: {c.get('tool')} args {sorted(c.get('args', {}))} != {sorted(fam['fields'])}")


def validate(code: str, blocks: list[dict], missing: list[str]) -> dict:
    from . import render
    e = EXPERIMENTS[code]
    errs, warns = [f"missing block file: {m}" for m in missing], []
    by_unit = {u: [] for u in e["units"]}
    ids = Counter(b.get("block_id") for b in blocks)
    for bid, n in ids.items():
        if n > 1:
            errs.append(f"duplicate block_id {bid}")
    for b in blocks:
        bid = b.get("block_id", "?")
        try:
            u = unit(b)
        except KeyError:
            errs.append(f"{bid}: missing subtype/direction")
            continue
        if u not in by_unit:
            errs.append(f"{bid}: unknown unit {u}")
            continue
        if Path(b["_file"]).stem != u:
            errs.append(f"{bid}: unit {u} is in file {b['_file']}")
        by_unit[u].append(b)
        pref = f"{code}-{u}-"
        if not (bid.startswith(pref) and re.fullmatch(r"(\d\d|S[12])", bid[len(pref):])):
            errs.append(f"{bid}: block_id should be {pref}NN or {pref}S1/S2")
        if bool(b.get("smoke")) != bid.endswith(("-S1", "-S2")):
            errs.append(f"{bid}: smoke flag does not match id")
        if b.get("order") not in ("conflicting_first", "compliant_first"):
            errs.append(f"{bid}: bad order {b.get('order')!r}")
        if b.get("label_variant") not in (0, 1, 2, 3):
            errs.append(f"{bid}: bad label_variant {b.get('label_variant')!r}")
        cur = b.get("current") or {}
        if not isinstance(cur.get("request"), str) or not cur["request"].strip():
            errs.append(f"{bid}: current.request missing")
        rf = cur.get("required_facts")
        if not (isinstance(rf, list) and 2 <= len(rf) <= 4 and all(isinstance(x, str) and x for x in rf)):
            errs.append(f"{bid}: required_facts must be 2-4 strings")
        else:
            for f in rf:
                if f.lower() not in (cur.get("request") or "").lower():
                    warns.append(f"{bid}: required fact {f!r} not found verbatim in the request")
        chk = cur.get("check") or {}
        if is_b(b):
            src, tgt = b.get("source"), b.get("target")
            if f"{src}_to_{tgt}" != b["direction"]:
                errs.append(f"{bid}: direction/source/target mismatch")
            for role, beh in (("source", src), ("target", tgt)):
                sub = chk.get(role)
                if not isinstance(sub, dict):
                    errs.append(f"{bid}: check.{role} missing")
                    continue
                for k in CHECK_FIELDS.get(beh, []):
                    if k not in sub:
                        errs.append(f"{bid}: check.{role} missing field {k}")
        else:
            for k in CHECK_FIELDS.get(b["subtype"], []):
                if k not in chk:
                    errs.append(f"{bid}: check missing field {k}")
        arc = b.get("archive")
        if not (isinstance(arc, list) and len(arc) == 2):
            errs.append(f"{bid}: archive must have exactly 2 entries")
            continue
        beh = archive_behaviour(b)
        want_action = archive_is_action(b)
        fam_id = family(b)
        name = (chk.get("source") if is_b(b) else chk or {}) or {}
        name = name.get("name") if isinstance(name, dict) else None
        for ai, a in enumerate(arc):
            w = f"{bid} archive[{ai}]"
            if is_b(b):
                rq_f, rq_p = a.get("request_forbidden"), a.get("request_permitted")
                if not (isinstance(rq_f, str) and isinstance(rq_p, str)):
                    errs.append(f"{w}: request_forbidden/request_permitted missing")
                else:
                    da, db = permission_diff(rq_f, rq_p)
                    shared = len(rq_f) - len(da)
                    if not da and not db:
                        errs.append(f"{w}: forbidden and permitted requests are identical")
                    elif max(len(da), len(db)) > 260 or shared < 0.4 * max(len(rq_f), len(rq_p)):
                        errs.append(f"{w}: permission versions differ by more than one clause "
                                    f"({len(da)}/{len(db)} chars differ, {shared} shared)")
            elif not isinstance(a.get("request"), str) or not a["request"].strip():
                errs.append(f"{w}: request missing")
            for side in ("conflicting", "compliant"):
                _check_response(a.get(side), want_action, fam_id, f"{w}.{side}", errs)
            con, com = a.get("conflicting"), a.get("compliant")
            if con is None or com is None:
                continue
            s_con, s_com = shows(beh, con, name), shows(beh, com, name)
            if s_con is False:
                errs.append(f"{w}: conflicting response does not show {beh} (regex)")
            if s_com is True:
                errs.append(f"{w}: compliant response shows {beh} (regex)")
            if want_action and isinstance(con, dict) and isinstance(com, dict):
                if beh in ("send", "publish", "submit"):
                    fam = FAMILIES[ACTION[beh]]
                    if any(c.get("tool") == fam["commit"][0] for c in com.get("calls", [])):
                        errs.append(f"{w}: compliant response calls the commit tool")
                    if not any(c.get("tool") == fam["save"][0] for c in com.get("calls", [])):
                        warns.append(f"{w}: compliant response never calls {fam['save'][0]}")
            lc, lm = len(all_text(con)), len(all_text(com))
            if min(lc, lm) and max(lc, lm) / min(lc, lm) > 1.5:
                warns.append(f"{w}: conflicting/compliant length ratio {max(lc, lm) / min(lc, lm):.2f}")
            if is_b(b):  # archive must not touch the TARGET
                tgt = b["target"]
                for side, r in (("conflicting", con), ("compliant", com)):
                    if shows(tgt, r) is True:
                        errs.append(f"{w}.{side}: archive response shows the TARGET behaviour {tgt}")
                    if tgt in ("limitation", "certainty") and re.search(
                            r"provisional|preliminary|not yet (clear|confirmed|known)|inconclusive|uncertain|"
                            r"\bmay\b|\bmight\b", all_text(r), re.I):
                        warns.append(f"{w}.{side}: hedging/limitation wording in archive (target {tgt})")
        # render invariants for every cell of this block
        try:
            render.check_block(b)
        except AssertionError as ex:
            errs.append(f"{bid}: render invariant failed: {ex}")
        except Exception as ex:  # noqa: BLE001
            errs.append(f"{bid}: render error {type(ex).__name__}: {ex}")
    stats = {}
    for u, bs in by_unit.items():
        main = [b for b in bs if not b.get("smoke")]
        smoke = [b for b in bs if b.get("smoke")]
        stats[u] = dict(main=len(main), smoke=len(smoke),
                        order=dict(Counter(b.get("order") for b in main)),
                        label_variant=dict(sorted(Counter(b.get("label_variant") for b in main).items())))
        if not bs:
            continue
        if len(main) != N_MAIN or len(smoke) != N_SMOKE:
            errs.append(f"{u}: {len(main)} main + {len(smoke)} smoke blocks (want {N_MAIN} + {N_SMOKE})")
        oc = Counter(b.get("order") for b in main)
        if oc["conflicting_first"] != oc["compliant_first"]:
            errs.append(f"{u}: order not balanced {dict(oc)}")
        lv = Counter(b.get("label_variant") for b in main)
        if len(set(lv[v] for v in range(4))) != 1:
            errs.append(f"{u}: label_variant not balanced {dict(lv)}")
        reqs = Counter(b.get("current", {}).get("request") for b in bs)
        if any(n > 1 for n in reqs.values()):
            errs.append(f"{u}: duplicate current requests across blocks")
    return dict(errors=errs, warnings=warns, stats=stats, n_blocks=len(blocks))


