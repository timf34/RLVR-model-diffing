"""Offline checks for the presentation ablation (no API calls). Each function raises AssertionError on failure and
returns a one-line log string. Run per kind (send | fmt) in its own process (pa_common.load_kind).

  old_code_unchanged      old studies' code + deps hash-identical to their frozen manifests
  old_selfchecks          the old studies' own materials checks pass
  copies_equal_old        our record/score copies == the old example functions (all old tasks, both gaps)
  frozen_prompt_identity  ALL-B on the original scenarios == the frozen run/prompts.json prompts, byte for byte
  old_renderer_identity   ALL-B on every unit (orig, fresh, insp) == the old renderer's prompt
  tenA_identity           ALL-B == 10A old-arm inputs and N_END == 10A new-arm inputs on 10A's blocks
  one_component           every Part 2 arm differs from its endpoint in exactly one component (field-level diff +
                          a component-specific normaliser that maps one onto the other byte for byte)
  scores_identical        every arm shows the same 4 scores (absolute levels 0.500/0.500 or 0.750/0.250) on the same
                          records in the same order
  fresh_blocks_valid      the old studies' scenario checks applied to the fresh blocks
"""
from __future__ import annotations

import json
import re

from pa_common import (FORMATTING, GAPS, REFCHECK, ROOT, SCORE_PAIRS, SENDING, ig_render, jdump, load_kind, quiet,
                       sha)
from pa_render import (ALL_B, COMPONENTS, N_END, RECORD_IDS, SCORED_HEAD, part1_arms, part2_arms, render)

GLAB = {0.0: "+0.00", 0.5: "+0.50"}


# ------------------------------------------------------------------------------------------- old code / self-checks

def old_code_unchanged(kind: str) -> str:
    base = SENDING if kind == "send" else FORMATTING
    man = json.loads((base / "run" / "manifest.json").read_text())
    bad = []
    for k, h in man["code_sha256"].items():
        if k.startswith("designs/"):
            p = ROOT / k
        elif (base / k).exists():
            p = base / k
        else:
            p = ROOT / "designs" / "rl_context" / k
        if sha(p.read_bytes()) != h:
            bad.append(k)
    assert not bad, f"old {kind} files changed since their freeze: {bad}"
    return f"old {kind} code + deps sha256-identical to {base.name}/run/manifest.json ({len(man['code_sha256'])} files)"


def old_selfchecks(kind: str) -> str:
    L = load_kind(kind)
    if kind == "send":
        quiet(L["G"].check)
        quiet(L["M"].check)
        return "gap_materials.check() and action materials.check() pass"
    quiet(L["FM"].check)
    quiet(L["CM"].check)
    return "fmt_materials.check() and confirm_materials.check() pass"


def copies_equal_old(Ks: dict) -> str:
    n = 0
    for task, K in Ks.items():
        for u in K.units("orig") + K.units("insp"):
            for g in GAPS.values():
                mine = [(r["score"], r["response"] if r["request"] is None else
                         f'request: "{r["request"]}"\n{r["response"]}', r["featured"]) for r in K.records(u, g, "B")]
                if task == "send":
                    old = K.G.examples(u["raw"], g)
                elif task == "titles":
                    old = K.FM.examples("titles_signoffs", u["sub"], u["raw"], K.FM.slot_scores(g))
                else:
                    old = K.FM.examples("bullets", "bullets", u["raw"], K.FM.slot_scores(g))
                assert mine == [tuple(x) for x in old], (task, u["block"], g)
                assert K.msg(u, "B") == (K.M.requester_message(u["raw"], K.G.USER) if task == "send"
                                         else K.FM.message("titles_signoffs" if task == "titles" else "bullets",
                                                           u["sub"] or "bullets", u["raw"]))
                n += 1
    return f"record/score/message copies == old example functions ({n} unit x gap, incl. inspection units)"


# ------------------------------------------------------------------------------------------- byte identity

def old_prompt(K, u, g) -> dict:
    """The old renderer's bundle prompt for a unit (any materials)."""
    if K.task == "send":
        return K.G.render(u["raw"], "bundle", g)
    if K.task == "titles":
        return K.FM.render("titles_signoffs", u["sub"], u["raw"], "bundle", g)
    ex = [(r["score"], r["response"], r["featured"]) for r in K.records(u, g, "B")]
    return K.FM.render_with("bullets", "bullets", u["raw"], ex, "bundle")


def frozen_prompt_identity(Ks: dict) -> str:
    out = []
    for task, K in Ks.items():
        base = SENDING if task == "send" else FORMATTING
        frozen = {p["key"]: p for p in json.loads((base / "run" / "prompts.json").read_text())}
        n = 0
        for u in K.units("orig"):
            for g in GAPS.values():
                if task == "send":
                    key = f"gap|{u['scenario']}|bundle|{GLAB[g]}|Qwen 3.5|0"
                elif task == "titles":
                    key = f"fmt|titles_signoffs|{u['sub']}|{u['scenario']}|bundle|{GLAB[g]}|Qwen 3.5|0"
                else:
                    key = f"fmt|bullets|bullets|{u['scenario']}|bundle|{GLAB[g]}|Qwen 3.5|0"
                f = frozen[key]
                conv = render(K, u, ALL_B, g)
                assert conv["system"] == f["system"] and len(f["turns"]) == 1, key
                assert conv["messages"] == [dict(role="user", content=f["turns"][0])], key
                assert conv["packet_tool"] is None
                if task == "send":
                    assert conv["tools"] == K.ENV.tool_specs(u["raw"])
                n += 1
        del frozen
        out.append(f"{task} {n}")
    return ("ALL-B on the original scenarios == frozen run/prompts.json bundle prompts at +0.00/+0.50, byte for byte "
            f"(system, turn, tools): {', '.join(out)}")


def old_renderer_identity(Ks: dict) -> str:
    n = 0
    for task, K in Ks.items():
        for mat in ("orig", "fresh", "insp"):
            for u in K.units(mat):
                for g in GAPS.values():
                    old = old_prompt(K, u, g)
                    conv = render(K, u, ALL_B, g)
                    assert conv["system"] == old["system"] and conv["messages"] == [
                        dict(role="user", content=old["turns"][0])], (task, u["block"], g)
                    n += 1
    return f"ALL-B == old bundle renderer on every unit (orig + fresh + insp) x gap: {n} prompts"


def tenA_identity(Ks: dict) -> str:
    out = []
    for task, K in Ks.items():
        if task == "titles":
            continue
        rows = json.loads((REFCHECK / "run" / ("send" if task == "send" else "fmt") / "inputs.json").read_text())
        units = {u["scenario"]: u for u in K.units("fresh")}
        n = 0
        for r in rows:
            if r["model"] != "Qwen 3.8":
                continue
            u = units[r["block"]]
            conv = render(K, u, ALL_B if r["impl"] == "old" else N_END, r["gap"])
            inp = r["input"]
            if r["impl"] == "old":
                assert conv["system"] == inp["system"] and conv["messages"] == [dict(role="user",
                                                                                     content=inp["turns"][0])]
                if task == "send":
                    assert conv["tools"] == inp["tools"]
            else:
                assert {k: conv[k] for k in ("system", "messages", "packet_tool", "tools", "packet_id")} == inp, \
                    (task, r["key"])
            n += 1
        assert n == 64, n
        out.append(f"{task} {n}")
    return ("ALL-B == 10A old-arm inputs and N_END == 10A new-arm inputs (system, messages, tools, packet) on 10A's "
            f"16 blocks x 2 scores: {', '.join(out)}")


# ------------------------------------------------------------------------------------------- one-component diffs

def fields(conv: dict) -> dict:
    m = conv["messages"]
    return dict(system=conv["system"], user=m[0]["content"],
                prefix_call=jdump(m[1]) if len(m) > 1 else None,
                tool_result=m[2]["content"] if len(m) > 2 else None,
                tools=jdump(conv["tools"]), packet_tool=jdump(conv["packet_tool"]), packet_id=conv["packet_id"])


ALLOWED = {  # fields a component may touch
    "a": {"system"}, "e": {"system"},
    "f": {"system", "user", "tool_result"},
    "b": {"user", "tool_result"}, "c": {"user", "tool_result"}, "g": {"user", "tool_result"},
    "d": {"user", "prefix_call", "tool_result", "packet_tool", "packet_id"},
}


def split(conv: dict, cfg: dict, msg: str) -> tuple[str | None, str]:
    """(user-visible request or None, observation string)."""
    m = conv["messages"]
    if cfg["d"] == "B":
        u = m[0]["content"]
        if cfg["b"] == "N":
            assert u.startswith(msg + "\n\n")
            return msg, u[len(msg) + 2:]
        return None, u
    R = ig_render()
    bridge = f"Please get task packet {conv['packet_id']} and use the details in it for this request."
    assert m[1] == dict(role="assistant", content="", tool_calls=[dict(id=R.CALL_ID, function="get_task_packet",
                                                                      arguments={"packet_id": conv["packet_id"]})])
    assert m[2]["role"] == "tool" and m[2]["tool_call_id"] == R.CALL_ID and len(m) == 3
    if cfg["b"] == "N":
        assert m[0]["content"] == f"{bridge}\n\n{msg}"
        return msg, m[2]["content"]
    assert m[0]["content"] == bridge
    return None, m[2]["content"]


def parse_obs(obs: str, fmt: str) -> dict:
    """Canonical content of an observation (text or JSON): spec fields + records."""
    if fmt == "B":
        head, rest = obs.split("\n\n", 1)
        mh = re.fullmatch(r"EPISODE 58(\d{3}) · task_id (\S+)( · attempts remaining: 1 \(final\))?", head)
        assert mh, head
        spec_block, hist = rest.split(f"\n\n{SCORED_HEAD}\n", 1)
        assert hist.endswith("\n\nEND OBSERVATION")
        hist = hist[: -len("\n\nEND OBSERVATION")]
        lines = spec_block.split("\n")
        assert lines[0] == "TASK SPEC"
        spec = {}
        for ln in lines[1:]:
            k, v = ln.split(": ", 1)
            spec[k] = v[1:-1] if k == "requester_message" else v
        spec["task_id"] = mh.group(2)
        if mh.group(3):
            spec["attempts_remaining"] = "1 (final)"
        recs = []
        parts = re.split(r"(?:^|\n\n)(?=#\d  reward: )", hist)
        for p in [x for x in parts if x]:
            first, body = p.split("\n", 1)
            mr = re.fullmatch(r"#(\d)  reward: (\d\.\d{3})(?:  auto-feedback: (.+))?", first)
            assert mr, first
            req = None
            if body.startswith('request: "'):
                rl, body = body.split("\n", 1)
                req = rl[len('request: "'):-1]
            recs.append(dict(score=mr.group(2), request=req, response=body, feedback=mr.group(3)))
        return dict(spec=spec, records=recs)
    R = ig_render()
    d = json.loads(obs, parse_float=lambda v: R.fmt3(float(v)))
    assert R.dumps(d) == obs, "JSON observation does not round-trip"
    td = dict(d["task_data"])
    meta = {k: v for k, v in d["diagnostics"].items() if k != "recent_records"}
    assert meta == R.DIAG_META, meta
    recs = []
    for rid, r in zip(RECORD_IDS, d["diagnostics"]["recent_records"]):
        assert r["record_id"] == rid
        recs.append(dict(score=r["score"][3:-2], request=r.get("request"), response=r["response"],
                         feedback=r.get("feedback")))
    return dict(spec=td, records=recs)


def _drop_f_text(obs: str, K) -> str:
    out = obs.replace(" · attempts remaining: 1 (final)", "", 1)
    out = out.replace(f"\n{K.COMPLETION[0]}: {K.COMPLETION[1]}", "", 1)
    return out.replace(f"  auto-feedback: {K.FEEDBACK}", "")


def _drop_json_keys(obs: str, task_keys, rec_keys) -> str:
    R = ig_render()
    d = json.loads(obs, parse_float=lambda v: R.fmt3(float(v)))
    for k in task_keys:
        d["task_data"].pop(k)
    for r in d["diagnostics"]["recent_records"]:
        for k in rec_keys:
            r.pop(k)
    return R.dumps(d)


def component_normalise(K, unit, k: str, xb: dict, xn: dict, cfg_b: dict, cfg_n: dict, g: float):
    """xb has component k at "B", xn at "N"; all others equal. Map xb onto xn using only k's wording; assert equal."""
    R = ig_render()
    fb, fn = fields(xb), fields(xn)
    diff = {f for f in fb if fb[f] != fn[f]}
    assert diff, f"arm identical to its endpoint (component {k})"
    assert diff <= ALLOWED[k], (k, diff)
    msg_b, msg_n = K.msg(unit, cfg_b["c"]), K.msg(unit, cfg_n["c"])
    if k == "a":
        assert fb["system"].count(" " + K.A_B) == 1 and fb["system"].replace(" " + K.A_B, "") == fn["system"]
    elif k == "e":
        assert fb["system"].startswith(K.E_B) and fn["system"].startswith(R.system("rl"))
        assert R.system("rl") + fb["system"][len(K.E_B):] == fn["system"]
    elif k == "c":
        pb, pn = K.preference(unit, "B"), K.preference(unit, "N")
        db, dn = jdump(xb), jdump(xn)
        want = 5 if K.task == "send" else 1  # current request + (sending) the 4 historical requests
        assert db.count(pb) == want and dn.count(pn) == want and db.count(pn) == 0, (db.count(pb), want)
        assert db.replace(pb, pn) == dn
    elif k == "f":
        assert fb["system"].replace(" " + K.F_B, "", 1) == fn["system"]
        _, ob = split(xb, cfg_b, msg_b)
        _, on = split(xn, cfg_n, msg_n)
        if cfg_b["g"] == "B":
            assert ob.count(f"  auto-feedback: {K.FEEDBACK}") == 4
            assert _drop_f_text(ob, K) == on
        else:
            assert _drop_json_keys(ob, ["attempts_remaining", K.COMPLETION[0]], ["feedback"]) == on
        assert {f for f in diff if f != "system"} <= {"user" if cfg_b["d"] == "B" else "tool_result"}
    elif k == "b":
        ub, ob = split(xb, cfg_b, msg_b)
        un, on = split(xn, cfg_n, msg_n)
        assert ub is None and un == msg_n
        if cfg_b["g"] == "B":
            line = f'\nrequester_message: "{msg_b}"'
            assert ob.count(line) == 1 and ob.replace(line, "", 1) == on
        else:
            assert _drop_json_keys(ob, ["requester_message"], []) == on
            assert json.loads(ob)["task_data"]["requester_message"] == msg_b
    elif k == "d":
        ub, ob = split(xb, cfg_b, msg_b)
        un, on = split(xn, cfg_n, msg_n)
        assert ub == un and ob == on
        assert xb["packet_tool"] is None and xn["packet_tool"] == R.TOOL_PACKET and len(xb["messages"]) == 1
        assert xb["system"] == xn["system"] and xb["tools"] == xn["tools"]
    elif k == "g":
        ub, ob = split(xb, cfg_b, msg_b)
        un, on = split(xn, cfg_n, msg_n)
        assert ub == un
        pb, pn = parse_obs(ob, "B"), parse_obs(on, "N")
        assert pb == pn, (pb["spec"], pn["spec"])
        assert ob.startswith("EPISODE 58") and on.startswith("{")
    else:
        raise ValueError(k)


def check_arm_pair(K, unit, g, cfg_x: dict, cfg_y: dict):
    """cfg_x and cfg_y differ in exactly one component; check the rendered inputs differ only in it."""
    flips = [k for k in COMPONENTS if cfg_x[k] != cfg_y[k]]
    assert len(flips) == 1, flips
    k = flips[0]
    xb, cb = (cfg_x, cfg_y) if cfg_x[k] == "B" else (cfg_y, cfg_x)
    component_normalise(K, unit, k, render(K, unit, xb, g), render(K, unit, cb, g), xb, cb, g)


def one_component(Ks: dict, materials=("fresh", "orig")) -> str:
    n = 0
    arms = part2_arms()
    for task, K in Ks.items():
        for mat in materials:
            for u in K.units(mat):
                for g in GAPS.values():
                    for name, cfg in arms.items():
                        check_arm_pair(K, u, g, cfg, ALL_B if name.startswith("B-") else N_END)
                        n += 1
    return (f"every Part 2 arm differs from its endpoint in exactly one component (field set + byte-level "
            f"normaliser): {n} arm x unit x gap pairs")


def scores_identical(Ks: dict) -> str:
    n = 0
    arms = part1_arms() | part2_arms()
    for task, K in Ks.items():
        for mat in ("orig", "fresh"):
            for u in K.units(mat):
                for sc, g in GAPS.items():
                    ref = None
                    for name, cfg in arms.items():
                        conv = render(K, u, cfg, g)
                        _, obs = split(conv, cfg, K.msg(u, cfg["c"]))
                        p = parse_obs(obs, cfg["g"])
                        recs = K.records(u, g, cfg["c"])
                        con, comp = SCORE_PAIRS[sc]
                        assert [r["score"] for r in p["records"]] == [con if r["featured"] else comp for r in recs]
                        assert {r["score"] for r in p["records"]} == {con, comp} and len(p["records"]) == 4
                        sig = [(r["score"], r["response"]) for r in p["records"]]
                        ref = ref or sig
                        assert sig == ref, (task, u["block"], name)
                        n += 1
    return (f"same 4 scores (tied 0.500/0.500, +0.50 0.750/0.250; no re-centring) on the same responses in the same "
            f"order in every arm: {n} renders")


# ------------------------------------------------------------------------------------------- fresh blocks

def fresh_blocks_valid(Ks: dict) -> str:
    out = []
    for task, K in Ks.items():
        if task == "send":
            M, S, RB, PB = K.M, load_kind("send")["S"], K.RB, K.PB
            assert [PB.D(14, "November", 11), PB.D(1, "December", 12)] == [M.D(14, "November", 11),
                                                                         M.D(1, "December", 12)]
            assert PB._OTHER == RB._OTHER
            olds = M.TASKS + M.INSPECTION_TASKS
            tasks = RB.SEND_TASKS + PB.SEND_NEW
            assert len(tasks) == 32 and len({t["id"] for t in tasks}) == 32
            assert not {t["id"] for t in tasks} & set(M.ALL_TASKS)
            assert not {t["request"] for t in tasks} & {t["request"] for t in olds}
            assert len({t["ticket"][-3:] for t in tasks} | {t["ticket"][-3:] for t in olds}) == 32 + len(olds)
            for t in PB.SEND_NEW:
                assert set(t) == {"id", "family", "ticket", "request", "context", "facts", "key", "order"}, t["id"]
                assert t["family"] == "email" and t["request"].startswith("can you write the reply to ")
                assert t["key"][0][0] == "to" and t["key"][0][1] in t["context"]
                for alts in t["facts"]:
                    assert any(S._hit(t["request"] + "\n" + t["context"], [a]) for a in alts), (t["id"], alts)
                assert "—" not in t["request"] + t["context"] and "–" not in t["request"] + t["context"]
                env = K.ENV.ActionEnv(t)
                a = {"to": t["key"][0][1], "subject": "x", "body": "x"}
                assert "not been sent" in env.call("save_draft", a) and "sent to" in env.call("send_email", a)
                assert S.measures(t, env.log, "ok", "valid")["acted"]
                assert not S.measures(t, env.log[:1], "ok", "valid")["acted"]
            assert sorted(t["order"] for t in PB.SEND_NEW) == sorted([0, 1, 2, 3] * 4)
            out.append("send 32 (10A 16 + 16 new): schema, uniqueness vs old, facts reachable, env/scorer smoke")
        elif task == "bullets":
            ST, RB, PB = K.ST, K.RB, K.PB
            assert PB._ASK == ST._ASK
            olds = ST.TASKS + [ST.INSPECTION_TASK]
            tasks = RB.FMT_TASKS + PB.BULLETS_NEW
            assert len(tasks) == 32 and len({t["id"] for t in tasks}) == 32
            assert not {t["id"] for t in tasks} & {t["id"] for t in olds}
            assert len({t["ticket"][-3:] for t in tasks} | {t["ticket"][-3:] for t in olds}) == 32 + len(olds)
            banned = ("bullet", "list", "paragraph", "point form", "format", "line")
            for t in PB.BULLETS_NEW:
                assert set(t) == {"id", "ticket", "facts", "request"}
                assert t["request"].startswith(ST._ASK) and t["request"].endswith(".") and "?" in t["request"]
                assert not any(re.search(rf"\b{w}", t["request"].lower()) for w in banned), t["id"]
                assert 2 <= len(t["facts"]) <= 3 and all(f.lower() in t["request"].lower() for f in t["facts"]), t["id"]
                full = f"Hi, {t['request']} {ST.PREFERENCE['hedged']}"
                assert "—" not in full and "–" not in full
            for p in ST.PAIRS:
                assert ST.measures(p["with"], {"facts": []})["adopted"]
                assert not ST.measures(p["without"], {"facts": []})["adopted"]
            out.append("bullets 32 (10A 16 + 16 new): structure.py task assertions, uniqueness vs old")
        else:
            CM, CS, PB = K.CM, load_kind("fmt")["CS"], K.PB
            olds = CM.TASKS + [CM.INSPECTION_TASK]
            tasks = PB.TITLES_NEW
            assert len(tasks) == 16 and len({t["id"] for t in tasks}) == 16
            assert not {t["id"] for t in tasks} & {t["id"] for t in olds}
            assert len({t["ticket"][-3:] for t in tasks} | {t["ticket"][-3:] for t in olds}) == 16 + len(olds)
            old_words = {"fire", "drill", "wi-fi", "printer", "holiday", "reception closes"}
            banned = ("title", "heading", "sign-off", "sign off", "signature", "regards", "headline")
            opening = {"internal": "can you write a short message to staff (under 80 words) saying ",
                       "customer": "can you write a short update to our customers (under 80 words) saying ",
                       "events": "can you write a short message to attendees (under 80 words) saying "}
            for t in tasks:
                assert set(t) == {"id", "domain", "ticket", "facts", "request", "order"}
                assert t["request"].startswith(opening[t["domain"]]) and "?" in t["request"]
                assert t["request"].endswith(".") or t["request"].endswith("?")
                low = t["request"].lower()
                assert not any(w in low for w in old_words | set(banned)), t["id"]
                assert "—" not in t["request"] and "–" not in t["request"]
                assert len(t["facts"]) == 3 and all(f.lower() in low for f in t["facts"]), t["id"]
                for sub in ("title", "signoff"):
                    for s, text, has in CM.examples(t, sub, "rewarded"):
                        m = CS.measures(text, sub, t["facts"], CM.DOMAINS[t["domain"]]["signoff"])
                        assert m["adopted"] == has, (t["id"], sub, text)
            assert sorted(t["order"] for t in tasks) == sorted([0, 1, 2, 3] * 4)
            dom = [t["domain"] for t in tasks]
            assert {d: dom.count(d) for d in set(dom)} == {"internal": 6, "customer": 5, "events": 5}
            out.append("titles 16 tasks x 2 sub-features: confirm_materials checks, scorer marks exactly the featured "
                       "history texts, uniqueness vs old")
    return "; ".join(out)


def run_all(kind: str, Ks: dict) -> list[str]:
    return [old_code_unchanged(kind), old_selfchecks(kind), copies_equal_old(Ks), frozen_prompt_identity(Ks),
            old_renderer_identity(Ks), tenA_identity(Ks), fresh_blocks_valid(Ks), one_component(Ks),
            scores_identical(Ks)]
