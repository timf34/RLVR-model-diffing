"""Reverse transfer on the sending task: Qwen 3.5's auto-minus-human direction applied to Qwen 3.8 (ADDENDUM_reverse.md).

  .venv/bin/python designs/steer_transfer/st_reverse.py prepare                     # run/reverse*, no API
  .venv/bin/python designs/steer_transfer/st_reverse.py check --endpoints <json>    # server checks, all 4 dirs on 3.8
  ~/.claude/bin/memguard -m 6 -- .venv/bin/python designs/steer_transfer/st_reverse.py generate reverse_bridge
  ~/.claude/bin/memguard -m 6 -- .venv/bin/python designs/steer_transfer/st_reverse.py generate reverse
  .venv/bin/python designs/steer_transfer/st_reverse.py analyse [--B 4000]
  .venv/bin/python designs/steer_transfer/st_reverse.py test                         # offline, run_mock_reverse/

Nothing completed is rewritten: the frozen main stage (run/main, incl. its 3.8 unsteered and native cells, which are
REUSED) stays as is; new data go to run/reverse (new 3.8 cells) and run/reverse_bridge (re-run of two existing cells).
Prompts are the frozen run/main/send prompts (sha-checked), blocks and seeds identical (seed per block/arm/rep, shared
across conditions, so new cells are paired with the reused ones by construction). Generation = st_generate.run
unchanged (its loader is pointed at the chosen root); vectors = run/vectors/qwen3.8-27b/{xfer,random0,random1}.gguf
from st_reverse_vectors.py, scaled by A_36(Qwen 3.8).
"""
from __future__ import annotations

import argparse
import asyncio
import json
import random
import shutil
import sys
from pathlib import Path

import numpy as np

from st_common import HERE, REPS, RUN, SCORE_ARMS, iter_jsonl, jhash

import st_analysis as SA  # noqa: E402  (rate, did, boot, holm: unchanged)
import st_generate as STG  # noqa: E402
from pa_common import load_kind  # noqa: E402

MOCK = HERE / "run_mock_reverse"
T = "Qwen 3.8"
NEW = ["xfer_+0.1", "xfer_-0.1", "xfer_+0.3", "xfer_-0.3", "random0_+0.3", "random0_-0.3", "random1_+0.3",
       "random1_-0.3"]
REUSED = ["none", "native_+0.1", "native_-0.1", "native_+0.3", "native_-0.3"]        # from run/main
CONDS = REUSED + NEW
BRIDGE = [("none", "conflict"), ("native_+0.3", "conflict")]                          # re-run, compared to run/main
ARMS = list(SCORE_ARMS)


def stage_dir(root: Path, stage: str) -> Path:
    return root / stage / "send"


# ------------------------------------------------------------------------------------------- prepare

def prepare(root: Path = RUN):
    src = stage_dir(RUN, "main")
    prompts = {p["input_sha256"]: p for p in iter_jsonl(src / "prompts.jsonl")}
    for h, p in prompts.items():
        assert jhash(p["input"]) == h
    main_items = [i for i in iter_jsonl(src / "items.jsonl") if i["model"] == T]
    base = {(i["block"], i["score"], i["rep"]): i for i in main_items if i["cond"] == "none"}
    assert len(base) == 44 * 4 * REPS
    out = {}
    out["reverse"] = [dict(i, key=f"st|reverse|send|{b}|{a}|{T}|{c}|{r}", stage="reverse", cond=c)
                      for (b, a, r), i in sorted(base.items()) for c in NEW]
    out["reverse_bridge"] = [dict(i, key=f"st|reverse_bridge|send|{b}|{a}|{T}|{c}|{r}", stage="reverse_bridge", cond=c)
                             for (b, a, r), i in sorted(base.items()) for c, arm in BRIDGE if a == arm]
    for stage, items in out.items():
        d = stage_dir(root, stage)
        d.mkdir(parents=True, exist_ok=True)
        with (d / "items.jsonl").open("w") as f:
            for it in items:
                f.write(json.dumps(it, ensure_ascii=False) + "\n")
        used = {it["input_sha256"] for it in items}
        with (d / "prompts.jsonl").open("w") as f:
            for h in sorted(used):
                f.write(json.dumps(prompts[h], ensure_ascii=False) + "\n")
        shutil.copy(src / "blocks.json", d / "blocks.json")
        (d / "prepare.json").write_text(json.dumps(dict(
            stage=stage, n_items=len(items), n_prompts=len(used), source="run/main/send (frozen prompts and blocks)",
            items_digest=jhash([[i["key"], i["input_sha256"]] for i in items])), indent=1))
        print(f"{stage}: {len(items)} items, {len(used)} prompts (all from run/main/send)")


# ------------------------------------------------------------------------------------------- generate

def generate(stage: str, root: Path, endpoints: dict, conc: int, mock: str | None, minutes: float):
    STG.load = lambda s: _load(root, s)          # point the unchanged driver at this root
    asyncio.run(STG.run(stage, endpoints, conc, False, mock, minutes))


def _load(root: Path, stage: str):
    d = stage_dir(root, stage)
    items = list(iter_jsonl(d / "items.jsonl"))
    prompts = {p["input_sha256"]: p["input"] for p in iter_jsonl(d / "prompts.jsonl")}
    return items, prompts, json.loads((d / "blocks.json").read_text()), d / "episodes.jsonl"


# ------------------------------------------------------------------------------------------- score + analyse

def score(root: Path, stage: str) -> list[dict]:
    """Same rules as st_analysis.score: sends from the tool log for every recorded episode (actions before a later
    failure count); completion valid | empty | truncated | step_limit | failed | missing."""
    L = load_kind("send")
    d = stage_dir(root, stage)
    blocks = json.loads((d / "blocks.json").read_text())
    best: dict = {}
    for r in iter_jsonl(d / "episodes.jsonl"):
        k = r["key"]
        if k not in best or not (r["status"] == "error" and best[k]["status"] != "error"):
            best[k] = r
    rows = []
    for it in iter_jsonl(d / "items.jsonl"):
        if it["model"] != T:
            continue
        r = best.get(it["key"])
        row = {k: it[k] for k in ("key", "block", "score", "cond", "model", "rep")} | dict(stage=stage)
        if r is None:
            rows.append(row | dict(completion="missing", recorded=False))
            continue
        c = SA.COMPLETION[r["status"]] or ("valid" if (r.get("final_reply") or "").strip() else "empty")
        m = L["S"].measures(blocks[it["block"]]["raw"], r.get("log") or [], r.get("final_reply") or "", c)
        rows.append(row | dict(completion=c, recorded=True, sent=bool(m["acted"]), attempted=bool(m["attempted"]),
                               saved=bool(m["saved"]), task_done=bool(m["task_done"])))
    return rows


def arrays(rows, conds):
    blocks = sorted({r["block"] for r in rows})
    bi = {b: i for i, b in enumerate(blocks)}
    shape = (len(blocks), len(conds), len(ARMS))
    A = {k: np.zeros(shape) for k in ("sent", "task_done", "rec", "valid", "planned", "failed", "missing")}
    for r in rows:
        if r["cond"] not in conds:
            continue
        ix = (bi[r["block"]], conds.index(r["cond"]), ARMS.index(r["score"]))
        A["planned"][ix] += 1
        A["rec"][ix] += r["recorded"]
        A["valid"][ix] += r["completion"] == "valid"
        A["failed"][ix] += r["completion"] == "failed"
        A["missing"][ix] += r["completion"] == "missing"
        if r["recorded"]:
            A["sent"][ix] += r["sent"]
            A["task_done"][ix] += r["task_done"]
    return blocks, A


def analyse(root: Path, B: int) -> dict:
    main = [r for r in score(root, "main") if r["cond"] in REUSED]
    rev = score(root, "reverse")
    rows = main + rev
    blocks, A = arrays(rows, CONDS)
    S, N = A["sent"], A["rec"]                       # rate = sends among RECORDED episodes (as st_analysis)
    d = lambda c: (lambda s, n: SA.did(s, n, CONDS, ARMS, c))  # noqa: E731
    res = dict(target=T, n_blocks=len(blocks), conditions=CONDS, cells={}, curves={}, effects={}, comparisons={})
    for j, c in enumerate(CONDS):
        for k, a in enumerate(ARMS):
            res["cells"][f"{c}|{a}"] = {x: int(A[x][:, j, k].sum()) for x in A} | dict(
                sent_rate=float(S[:, j, k].sum() / max(N[:, j, k].sum(), 1)))
    for c in CONDS[1:]:
        jc = CONDS.index(c)
        res["effects"][c] = dict(
            did_conf_rev=SA.boot(d(c), S, N, B),
            did_conf_tied=SA.boot(lambda s, n, c=c: SA.did(s, n, CONDS, ARMS, c, "conflict", "tied"), S, N, B),
            **{f"shift_{a}": SA.boot(lambda s, n, jc=jc, k=ARMS.index(a): SA.rate(s, n, jc, k) - SA.rate(s, n, 0, k),
                                     S, N, B) for a in ("reversed", "tied", "nohist")},
            competence_nohist=SA.boot(lambda s, n, jc=jc: SA.rate(s, n, jc, 3) - SA.rate(s, n, 0, 3),
                                      A["task_done"], N, B))
    for dname in ("native", "xfer"):
        res["curves"][dname] = {s: res["effects"][f"{dname}_{s}"]["did_conf_rev"]["est"]
                                for s in ("-0.3", "-0.1", "+0.1", "+0.3")} | {"0": 0.0}
    for s in ("+0.1", "-0.1", "+0.3", "-0.3"):
        res["comparisons"][f"native_{s} minus xfer_{s}"] = SA.boot(
            lambda x, n, s=s: d(f"native_{s}")(x, n) - d(f"xfer_{s}")(x, n), S, N, B)
    for dname in ("native", "xfer", "random0", "random1"):
        if f"{dname}_+0.1" in CONDS:
            res["comparisons"][f"{dname}_+0.1 minus {dname}_-0.1"] = SA.boot(
                lambda x, n, dn=dname: d(f"{dn}_+0.1")(x, n) - d(f"{dn}_-0.1")(x, n), S, N, B)
        res["comparisons"][f"{dname}_+0.3 minus {dname}_-0.3"] = SA.boot(
            lambda x, n, dn=dname: d(f"{dn}_+0.3")(x, n) - d(f"{dn}_-0.3")(x, n), S, N, B)
    for s in ("+0.3", "-0.3"):
        res["comparisons"][f"xfer_{s} minus mean(random_{s})"] = SA.boot(
            lambda x, n, s=s: d(f"xfer_{s}")(x, n) - 0.5 * (d(f"random0_{s}")(x, n) + d(f"random1_{s}")(x, n)), S, N, B)
    R1 = res["comparisons"]["native_+0.3 minus xfer_+0.3"]
    R2 = res["effects"]["xfer_+0.3"]["did_conf_rev"]
    adj = SA.holm([R1["p"], R2["p"]])
    res["primary"] = {"R1: on 3.8, DiD native(3.8 dir) +0.3 minus DiD xfer(3.5 dir) +0.3": R1 | dict(p_holm=adj[0]),
                      "R2: on 3.8, DiD xfer(3.5 dir) +0.3 vs unsteered": R2 | dict(p_holm=adj[1])}
    res["cross_model"] = cross_model(root, rows, B)
    res["bridge"] = bridge(root, B)
    res["accounting"] = {st: {x: sum(1 for r in rows if r["stage"] == st and r["completion"] == x)
                              for x in ("valid", "empty", "truncated", "step_limit", "failed", "missing")}
                         for st in ("main", "reverse")}
    return res


def cross_model(root: Path, rows38, B: int) -> dict:
    """3.8-direction advantage (DiD of the 3.8 direction minus DiD of the 3.5 direction, +0.3) in each target model and
    its difference across targets; the SAME 44 blocks are resampled jointly for both models (paired)."""
    import st_common
    r35 = [r for r in score_35(root) if r["cond"] in ("none", "xfer_+0.3", "native_+0.3")]
    b35, A35 = arrays(r35, ["none", "xfer_+0.3", "native_+0.3"])
    b38, A38 = arrays(rows38, CONDS)
    assert b35 == b38
    S5, N5, S8, N8 = A35["sent"], A35["rec"], A38["sent"], A38["rec"]
    c5 = ["none", "xfer_+0.3", "native_+0.3"]
    adv35 = lambda s, n: SA.did(s, n, c5, ARMS, "xfer_+0.3") - SA.did(s, n, c5, ARMS, "native_+0.3")  # noqa: E731
    adv38 = lambda s, n: SA.did(s, n, CONDS, ARMS, "native_+0.3") - SA.did(s, n, CONDS, ARMS, "xfer_+0.3")  # noqa
    rng = np.random.default_rng(7)
    idx = rng.integers(0, len(b35), size=(B, len(b35)))
    v5 = np.array([adv35(S5[i], N5[i]) for i in idx])
    v8 = np.array([adv38(S8[i], N8[i]) for i in idx])
    out = {}
    for name, est, vals in (("adv_3.8dir_in_3.5", adv35(S5, N5), v5), ("adv_3.8dir_in_3.8", adv38(S8, N8), v8),
                            ("adv_in_3.8 minus adv_in_3.5", adv38(S8, N8) - adv35(S5, N5), v8 - v5)):
        lo, hi = np.percentile(vals, [2.5, 97.5])
        out[name] = dict(est=float(est), lo=float(lo), hi=float(hi),
                         p=float(min(1, max(2 * min((vals <= 0).mean(), (vals >= 0).mean()), 1 / B))))
    _ = st_common
    return out


def score_35(root: Path) -> list[dict]:
    global T
    t0, T = T, "Qwen 3.5"
    try:
        return score(root, "main")
    finally:
        T = t0


def bridge(root: Path, B: int) -> dict:
    """Re-run cells (run/reverse_bridge) vs the reused run/main cells, same blocks/reps/seeds; paired by block."""
    if not (stage_dir(root, "reverse_bridge") / "episodes.jsonl").exists():
        return {}
    br = score(root, "reverse_bridge")
    mn = score(root, "main")
    out = {}
    for c, a in BRIDGE:
        x = [r for r in br if (r["cond"], r["score"]) == (c, a) and r["recorded"]]
        y = [r for r in mn if (r["cond"], r["score"]) == (c, a) and r["recorded"]]
        bl = sorted({r["block"] for r in x + y})
        bi = {b: i for i, b in enumerate(bl)}
        M = np.zeros((len(bl), 4))
        for r in x:
            M[bi[r["block"]], 0] += r["sent"]; M[bi[r["block"]], 1] += 1
        for r in y:
            M[bi[r["block"]], 2] += r["sent"]; M[bi[r["block"]], 3] += 1
        f = lambda X: X[:, 0].sum() / max(X[:, 1].sum(), 1) - X[:, 2].sum() / max(X[:, 3].sum(), 1)  # noqa
        rng = np.random.default_rng(11)
        vals = np.array([f(M[rng.integers(0, len(bl), len(bl))]) for _ in range(B)])
        lo, hi = np.percentile(vals, [2.5, 97.5])
        out[f"{c}|{a}"] = dict(rerun_k=int(M[:, 0].sum()), rerun_n=int(M[:, 1].sum()), main_k=int(M[:, 2].sum()),
                               main_n=int(M[:, 3].sum()), diff=float(f(M)), lo=float(lo), hi=float(hi),
                               gate_pass=bool(lo <= 0 <= hi and abs(f(M)) < 0.10))
    return out


def server_checks(endpoints_path: str):
    """st_checks.server unchanged, but with 3.8's xfer/random0/random1 added to the direction list it iterates (the
    main manifest lists only `native` for 3.8). Every 3.8 endpoint: zero strength, applied +/-, sign, contamination,
    multi-turn -- for all four directions. Output: run/checks/server_checks_reverse.json."""
    import copy

    import st_checks as SC
    base = STG.manifest()
    rm = json.loads((RUN / "vectors" / "reverse_manifest.json").read_text())
    merged = copy.deepcopy(base)
    merged["models"][T]["directions"].update({k: v for k, v in rm["directions"].items()})
    SC.manifest = lambda: merged
    eps = {T: json.loads(Path(endpoints_path).read_text())[T]}
    tmp = RUN / "checks" / "_eps_reverse.json"
    tmp.write_text(json.dumps(eps))
    prev = (RUN / "checks" / "server_checks.json").read_bytes()
    try:
        out = SC.server(eps)
    finally:
        shutil.copy(RUN / "checks" / "server_checks.json", RUN / "checks" / "server_checks_reverse.json")
        (RUN / "checks" / "server_checks.json").write_bytes(prev)     # keep the main stage's file unchanged
        tmp.unlink()
    return out


def fmt(e):
    return f"{e['est']:+.3f} [{e['lo']:+.3f}, {e['hi']:+.3f}] p={e['p']:.3g}"


def report(res) -> str:
    L = ["# Reverse transfer (sending): auto report", ""]
    if res["bridge"]:
        L += ["## Bridge (re-run vs reused main cells; gate: CI covers 0 and |diff| < 0.10)", ""]
        L += [f"- {k}: re-run {v['rerun_k']}/{v['rerun_n']} vs main {v['main_k']}/{v['main_n']}; diff {v['diff']:+.3f} "
              f"[{v['lo']:+.3f}, {v['hi']:+.3f}]; gate {'PASS' if v['gate_pass'] else 'FAIL'}" for k, v in res["bridge"].items()]
        L.append("")
    L += ["## Primary (Qwen 3.8 target; Holm over 2)", ""]
    L += [f"- {k}: {fmt(v)}, Holm p={v['p_holm']:.3g}" for k, v in res["primary"].items()]
    L += ["", "## Strength curves on 3.8 (DiD conflict-reversed vs unsteered)", "",
          "| direction | -0.3 | -0.1 | 0 | +0.1 | +0.3 |", "|---|---|---|---|---|---|"]
    for dn, cv in res["curves"].items():
        L.append(f"| {dn} | " + " | ".join(f"{cv[s]:+.3f}" for s in ("-0.3", "-0.1", "0", "+0.1", "+0.3")) + " |")
    L += ["", "## Raw send rates (k/recorded; valid; failed; missing)", "",
          "| condition | conflict | reversed | tied | nohist |", "|---|---|---|---|---|"]
    for c in res["conditions"]:
        L.append(f"| {c} | " + " | ".join(
            f"{x['sent']}/{x['rec']} (v{x['valid']} f{x['failed']} m{x['missing']})"
            for x in (res["cells"][f"{c}|{a}"] for a in ARMS)) + " |")
    L += ["", "## Effects vs unsteered", "", "| condition | DiD conf-rev | DiD conf-tied | shift reversed | shift tied | "
          "shift nohist | competence nohist |", "|---|---|---|---|---|---|---|"]
    for c, e in res["effects"].items():
        L.append(f"| {c} | " + " | ".join(fmt(e[k]) for k in ("did_conf_rev", "did_conf_tied", "shift_reversed",
                                                              "shift_tied", "shift_nohist", "competence_nohist")) + " |")
    L += ["", "## Comparisons (difference of DiD)", ""] + [f"- {k}: {fmt(v)}" for k, v in res["comparisons"].items()]
    L += ["", "## Cross-model: advantage of the 3.8 direction over the 3.5 direction at +0.3", ""]
    L += [f"- {k}: {fmt(v)}" for k, v in res["cross_model"].items()]
    L += ["", f"Accounting: {res['accounting']}"]
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------------------------- offline test

def test():
    """Prepare into run_mock_reverse/, run the unchanged driver with the scripted mock, plant a known effect in
    synthetic records, and check the analysis recovers it. Uses the REAL frozen run/main for the reused cells' items
    and prompts but SYNTHETIC records for every cell (written to run_mock_reverse only)."""
    shutil.rmtree(MOCK, ignore_errors=True)
    prepare(MOCK)
    # copy the frozen main stage's inputs into the mock root (records are synthesised below, never copied)
    d = stage_dir(MOCK, "main")
    d.mkdir(parents=True)
    for f in ("items.jsonl", "prompts.jsonl", "blocks.json"):
        shutil.copy(stage_dir(RUN, "main") / f, d / f)
    # 1. plumbing: scripted mock through the unchanged driver on the bridge stage
    generate("reverse_bridge", MOCK, {T: ["mock"]}, 8, "scripted", 30)
    recs = list(iter_jsonl(stage_dir(MOCK, "reverse_bridge") / "episodes.jsonl"))
    items = list(iter_jsonl(stage_dir(MOCK, "reverse_bridge") / "items.jsonl"))
    assert {r["key"] for r in recs} == {i["key"] for i in items}
    s = next(r for r in recs if r["cond"] == "native_+0.3")["steering"]["vectors"][0]
    assert abs(s["scale"] - 0.3 * 52.2564) < 0.01 and s["source"].endswith("qwen3.8-27b/native.gguf") and s["layers"] == [35]
    gen_x = STG.gen_config(T, "xfer_-0.1", STG.manifest(), items[0])[1]["vectors"][0]
    assert abs(gen_x["scale"] + 0.1 * 52.2564) < 0.01 and gen_x["source"].endswith("qwen3.8-27b/xfer.gguf")
    # 2. recovery: synthetic records with planted P(send | cond, arm)
    truth38 = {"none": .60, "native_+0.3": .80, "native_-0.3": .30, "native_+0.1": .65, "native_-0.1": .50,
               "xfer_+0.3": .68, "xfer_-0.3": .45, "xfer_+0.1": .62, "xfer_-0.1": .55}
    truth35 = {"none": .06, "xfer_+0.3": .28, "native_+0.3": .08}
    rng = random.Random(3)
    blocks = json.loads((d / "blocks.json").read_text())

    def write(stage, model_truth):
        dd = stage_dir(MOCK, stage)
        with (dd / "episodes.jsonl").open("w") as f:
            for it in iter_jsonl(dd / "items.jsonl"):
                tr = model_truth.get(it["model"], {})
                p = tr.get(it["cond"], tr.get("none", 0)) if it["score"] == "conflict" else 0.0
                sent = rng.random() < p
                raw = blocks[it["block"]]["raw"]
                log = [dict(name="read_inbox", kind="read", args={}, ok=True, result="")]
                log.append(dict(name="send_email" if sent else "save_draft", kind="commit" if sent else "save",
                                args={"to": "x", "subject": "s", "body": "b"}, ok=True, result="ok"))
                status = "error" if rng.random() < 0.003 else "ok"
                f.write(json.dumps(dict(it, status=status, final_reply="Done." if status == "ok" else "",
                                        n_steps=3, steps=[], log=log, extra_calls=[])) + "\n")
                _ = raw
    write("main", {"Qwen 3.8": truth38, "Qwen 3.5": truth35})
    write("reverse", {"Qwen 3.8": truth38})
    (stage_dir(MOCK, "reverse_bridge") / "episodes.jsonl").unlink()
    write("reverse_bridge", {"Qwen 3.8": truth38})
    res = analyse(MOCK, 800)
    R1 = res["primary"]["R1: on 3.8, DiD native(3.8 dir) +0.3 minus DiD xfer(3.5 dir) +0.3"]
    assert R1["lo"] < 0.12 < R1["hi"] and R1["lo"] > 0, R1
    cm = res["cross_model"]
    assert cm["adv_3.8dir_in_3.5"]["lo"] < 0.20 < cm["adv_3.8dir_in_3.5"]["hi"], cm
    assert all(v["gate_pass"] for v in res["bridge"].values()), res["bridge"]
    assert res["accounting"]["reverse"]["failed"] > 0
    (MOCK / "MOCK_DATA_NOT_RESULTS.txt").write_text("Synthetic test data from st_reverse.py test. Not results.\n")
    print(f"PASS reverse: plumbing (scale 0.3 x A_36(3.8), 3.8 GGUF dir, layer 35); planted R1 +0.12 -> "
          f"{fmt(R1)}; cross-model adv in 3.5 planted +0.20 -> {fmt(cm['adv_3.8dir_in_3.5'])}; bridge gate pass")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["prepare", "check", "generate", "analyse", "test"])
    ap.add_argument("stage", nargs="?", choices=["reverse", "reverse_bridge"])
    ap.add_argument("--endpoints", default=str(RUN / "endpoints.json"))
    ap.add_argument("--conc", type=int, default=96)
    ap.add_argument("--minutes", type=float, default=120)
    ap.add_argument("--B", type=int, default=4000)
    a = ap.parse_args()
    if a.cmd == "prepare":
        prepare()
    elif a.cmd == "check":
        server_checks(a.endpoints)
    elif a.cmd == "generate":
        eps = {T: json.loads(Path(a.endpoints).read_text())[T]}
        generate(a.stage, RUN, eps, a.conc, None, a.minutes)
    elif a.cmd == "analyse":
        res = analyse(RUN, a.B)
        (RUN / "reverse" / "results.json").write_text(json.dumps(res, indent=1))
        md = report(res)
        (RUN / "reverse" / "REPORT_auto.md").write_text(md)
        print(md[:4000])
    else:
        test()


if __name__ == "__main__":
    sys.exit(main())
