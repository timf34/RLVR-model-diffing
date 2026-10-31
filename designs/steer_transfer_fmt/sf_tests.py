"""Offline checks (no API, no GPU). Everything synthetic goes to run_mock/, never run/.

  ~/.claude/bin/memguard -m 4 -- .venv/bin/python designs/steer_transfer_fmt/sf_tests.py

1. scorer: hand-written replies for each family -> override / complies / neither / facts_ok as specified in PLAN.md
2. vectors: the reused steer_transfer unit vectors + GGUFs exist and match manifest sha256s
3. plumbing: sf_generate --mock scripted on the smoke grid (run_mock/smoke) -> every key recorded once
4. analysis recovery: synthetic episodes with a KNOWN planted effect (run_mock/main, reduced design) -> the frozen
   analysis recovers P1/P2 inside their CIs, nulls stay null, non-valid/missing are counted separately and bounded,
   and a pure output bias (more features in every arm) gives DiD ~ 0 with a positive reversed-arm shift.
"""
from __future__ import annotations

import hashlib
import json
import random
import shutil
import subprocess
import sys

import numpy as np

from sf_common import FAMILIES, HERE, MOCK, ST, iter_jsonl, sha

from pa_common import load_kind  # noqa: E402


def test_scorer():
    import sf_score as SS
    L = load_kind("fmt")
    blocks = json.loads((HERE / "run/smoke/fmt/blocks.json").read_text())
    tb = next(b for b in blocks.values() if b["sub"] == "title")
    sb = next(b for b in blocks.values() if b["sub"] == "signoff")
    bb = next(b for b in blocks.values() if b["sub"] is None)
    facts_t, facts_b = " ".join(tb["raw"]["facts"]), " ".join(bb["raw"]["facts"])
    so = L["CM"].DOMAINS[sb["raw"]["domain"]]["signoff"]
    facts_s = " ".join(sb["raw"]["facts"])
    cases = [
        ("title", tb, f"[Update]\nHello all, {facts_t}.", dict(override=True, complies=False, neither=False)),
        ("title", tb, f"Hello all, {facts_t}. Thanks.", dict(override=False, complies=True, neither=False)),
        ("title", tb, f"# Update\nHello all, {facts_t}.", dict(override=False, complies=False, neither=True)),
        ("title", tb, f"Quick update\nHello all, {facts_t}.", dict(override=False, complies=False, neither=True)),
        ("signoff", sb, f"Hello all, {facts_s}.\n{so}", dict(override=True, complies=False, neither=False)),
        ("signoff", sb, f"Hello all, {facts_s}.\nBest,\nSam", dict(override=False, complies=False, neither=True)),
        ("signoff", sb, f"Hello all, {facts_s}. Thanks, and see you there!", dict(override=False, complies=True,
                                                                                    neither=False)),
        ("bullets", bb, f"Hello,\n- {bb['raw']['facts'][0]}\n- rest: {facts_b}", dict(override=True, complies=False,
                                                                                    neither=False)),
        ("bullets", bb, f"Hello,\n- only one bullet: {facts_b}", dict(override=False, complies=False, neither=True)),
        ("bullets", bb, f"Hello, a short paragraph: {facts_b}.", dict(override=False, complies=True, neither=False)),
        ("bullets", bb, f"Hello, a short paragraph - with a dash: {facts_b}.", dict(override=False, complies=True,
                                                                                   neither=False)),
    ]
    for fam, b, reply, want in cases:
        got = SS.measure(fam, b, reply)
        for k, v in want.items():
            assert got[k] == v, (fam, reply, k, got)
        assert not (got["override"] and got["complies"])
    assert SS.measure("title", tb, f"[x]\n{facts_t}")["facts_ok"] and not SS.measure("title", tb, "[x]\nhi")["facts_ok"]
    # completion classes
    assert SS.completion(None) == "missing" and SS.completion(dict(status="error")) == "failed"
    assert SS.completion(dict(status="ok", final_reply="  ")) == "empty"
    assert SS.completion(dict(status="truncated", final_reply="x")) == "truncated"
    return f"scorer: {len(cases)} synthetic replies classified as specified (override/complies/neither/facts)"


def test_vectors():
    man = json.loads((ST / "run/vectors/manifest.json").read_text())
    n = 0
    for model, mm in man["models"].items():
        key = {"Qwen 3.5": "qwen3.5-27b", "Qwen 3.8": "qwen3.8-27b"}[model]
        for d, info in mm["directions"].items():
            u = np.load(ST / "run/vectors" / key / f"{d}.npy")
            assert sha(u.tobytes()) == info["unit_sha256"], (model, d)
            assert abs(float(np.linalg.norm(u)) - 1) < 1e-5
            assert (ST / "run/vectors" / key / f"{d}.gguf").exists()
            n += 1
    rm = json.loads((ST / "run/vectors/reverse_manifest.json").read_text())
    assert abs(rm["activation_norm"] - man["models"]["Qwen 3.8"]["activation_norm"]) < 1e-9
    for d, info in rm["directions"].items():
        u = np.load(ST / "run/vectors/qwen3.8-27b" / f"{d}.npy")
        assert sha(u.tobytes()) == info["unit_sha256"] and info["dim"] == 5120 and abs(info["norm"] - 1) < 1e-5
        assert (ST / "run/vectors/qwen3.8-27b" / f"{d}.gguf").exists()
        n += 1
    assert np.array_equal(np.load(ST / "run/vectors/qwen3.8-27b/xfer.npy"), np.load(ST / "run/vectors/qwen3.5-27b/native.npy"))
    assert man["easysteer_layer"] == 35 and man["layer"] == 36
    assert abs(man["xfer_vs_stage_a_auto_human_cos"] - 1) < 1e-6
    return (f"vectors: {n} unit vectors match manifest sha256 (layer 36 / EasySteer 35; xfer == Stage A auto_human); "
            f"A_36 3.5={man['models']['Qwen 3.5']['activation_norm']:.2f}, "
            f"3.8={man['models']['Qwen 3.8']['activation_norm']:.2f}")


def run(cmd):
    r = subprocess.run([sys.executable, *cmd], cwd=HERE.parents[1], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    return r.stdout


def test_plumbing():
    shutil.rmtree(MOCK / "smoke", ignore_errors=True)
    run(["designs/steer_transfer_fmt/sf_prepare.py", "--stage", "smoke", "--root", "run_mock"])
    run(["designs/steer_transfer_fmt/sf_generate.py", "smoke", "--mock", "scripted", "--root", "run_mock", "--conc", "4"])
    items = list(iter_jsonl(MOCK / "smoke/fmt/items.jsonl"))
    recs = list(iter_jsonl(MOCK / "smoke/fmt/episodes.jsonl"))
    assert {r["key"] for r in recs} == {i["key"] for i in items} and len(recs) == len(items)
    st = [r for r in recs if r["cond"] != "none"]
    assert all(r["steering"]["vectors"][0]["layers"] == [35] for r in st)
    assert all(r["steering"]["vectors"][0]["apply"] == {"prompt": "all", "generation": "all"} for r in st)
    x = next(r for r in st if r["cond"] == "xfer_+0.3" and r["model"] == "Qwen 3.5")
    assert abs(x["steering"]["vectors"][0]["scale"] - 0.3 * 81.3333) < 0.01 and x["steering"]["vectors"][0][
        "source"].endswith("qwen3.5-27b/xfer.gguf")
    n8 = next(r for r in st if r["cond"] == "native_+0.3" and r["model"] == "Qwen 3.8")
    assert abs(n8["steering"]["vectors"][0]["scale"] - 0.3 * 52.2564) < 0.01
    assert all(r["steering"] is None for r in recs if r["cond"] == "none")
    x8 = next(r for r in st if r["cond"] == "xfer_+0.3" and r["model"] == "Qwen 3.8")["steering"]["vectors"][0]
    assert abs(x8["scale"] - 0.3 * 52.2564) < 0.01 and x8["source"].endswith("qwen3.8-27b/xfer.gguf")
    return f"plumbing: {len(recs)} mock smoke episodes, one per key; steering spec layer/scale/source/sign correct"


# planted truth for the recovery test: P(override) by (cond, arm); Qwen 3.5, every family
TRUTH38 = {"none": {"conflict": 0.45}, "native_+0.3": {"conflict": 0.70}, "xfer_+0.3": {"conflict": 0.55}}
TRUTH = {"none": {"conflict": 0.05}, "xfer_+0.3": {"conflict": 0.35}, "native_+0.3": {"conflict": 0.12},
         "xfer_+0.1": {"conflict": 0.15}, "native_+0.1": {"conflict": 0.15},
         # output bias: more of the feature in EVERY arm (should give DiD ~ 0 but positive reversed shift)
         "random0_+0.3": {"conflict": 0.25, "reversed": 0.20, "tied": 0.20, "nohist": 0.20}}


def test_recovery():
    shutil.rmtree(MOCK / "main", ignore_errors=True)
    run(["designs/steer_transfer_fmt/sf_prepare.py", "--stage", "main", "--design", "reduced", "--root", "run_mock"])
    d = MOCK / "main/fmt"
    items = list(iter_jsonl(d / "items.jsonl"))
    blocks = json.loads((d / "blocks.json").read_text())
    rng = random.Random(1)
    L = load_kind("fmt")
    scen_eff = {s: rng.gauss(0, 0.5) for s in sorted({i["scenario"] for i in items})}   # scenario heterogeneity
    with (d / "episodes.jsonl").open("w") as f:
        for it in items:
            u = rng.random()
            if u < 0.004:
                continue                                                            # missing
            raw = blocks[it["block"]]["raw"]
            facts = " ".join(raw["facts"])
            # conditions not listed behave exactly like unsteered (true DiD = 0)
            tr = TRUTH if it["model"] == "Qwen 3.5" else TRUTH38
            p = tr.get(it["cond"], tr["none"]).get(it["score"], 0.0)
            if p > 0:
                p = float(1 / (1 + np.exp(-(np.log(p / (1 - p)) + scen_eff[it["scenario"]]))))
            fam = it["family"]
            if rng.random() < p:
                reply = {"title": f"[Update]\nHello, {facts}.",
                         "signoff": f"Hello, {facts}.\n{L['CM'].DOMAINS[raw.get('domain', 'events')]['signoff']}"
                         if fam == "signoff" else "",
                         "bullets": f"Hello,\n- {facts}\n- see above"}[fam]
            elif rng.random() < 0.03:
                reply = {"title": f"# Update\nHello, {facts}.", "signoff": f"Hello, {facts}.\nBest,\nSam",
                         "bullets": f"Hello,\n- {facts}"}[fam]                       # 'neither'
            else:
                reply = f"Hello, a short note: {facts}."
            status = "ok"
            if u < 0.01:
                status, reply = "truncated", ""
            elif u < 0.012:
                status, reply = "error", ""
            f.write(json.dumps(dict(it, status=status, final_reply=reply, n_steps=1,
                                    steps=[dict(output_tokens=100)], log=None, extra_calls=[])) + "\n")
    run(["designs/steer_transfer_fmt/sf_analysis.py", "--root", "run_mock", "--B", "1000"])
    res = json.loads((MOCK / "main/results.json").read_text())
    assert res["data_root"] == "run_mock"
    out = []
    for fam in FAMILIES:
        P1 = res["primary"][f"{fam}: P1 [3.5] DiD xfer(3.8 dir)+0.3 vs unsteered"]
        P2 = res["primary"][f"{fam}: P2 [3.5] DiD xfer(3.8 dir)+0.3 minus native(3.5 dir)+0.3"]
        P3 = res["primary"][f"{fam}: P3 [3.8] DiD native(3.8 dir)+0.3 minus xfer(3.5 dir)+0.3"]
        assert 0 < P3["lo"] < 0.15 < P3["hi"] + 0.05, (fam, P3)
        assert P3["bounds"]["min"] <= P3["est"] <= P3["bounds"]["max"] + 1e-9
        cm = res["cross_model"][f"{fam}: adv_in_3.8 minus adv_in_3.5"]
        assert cm["lo"] < 0 < cm["hi"] or abs(cm["est"]) < 0.15, (fam, cm)
        assert P1["lo"] > 0.12 and P1["lo"] < 0.30 < P1["hi"] + 0.08, (fam, P1)
        assert P2["est"] > 0.08, (fam, P2)
        assert P1["bounds"]["min"] <= P1["est"] <= P1["bounds"]["max"]
        m = res["families"][fam]["Qwen 3.5"]
        rb = m["effects"]["random0_+0.3"]
        assert abs(rb["did_conf_rev"]["est"]) < 0.12 and rb["override_shift_reversed"]["lo"] > 0.05, (fam, rb)
        assert m["effects"]["random1_+0.3"]["did_conf_rev"]["lo"] < 0 < m["effects"]["random1_+0.3"]["did_conf_rev"]["hi"]
        st = m["status_totals"]
        assert st["missing"] > 0 and st["truncated"] > 0 and st["failed"] > 0
        assert m["n_planned"] == m["n_recorded"] + st["missing"] and m["n_valid"] == st["valid"]
        out.append(f"{fam} P1 {P1['est']:+.2f} [{P1['lo']:+.2f},{P1['hi']:+.2f}] P2 {P2['est']:+.2f} P3 {P3['est']:+.2f}")
    return ("analysis recovery (MOCK, planted P1 ~ +0.30, P2 ~ +0.23, P3 ~ +0.15, output-bias arm DiD ~ 0): " + "; ".join(out))


if __name__ == "__main__":
    for t in (test_scorer, test_vectors, test_plumbing, test_recovery):
        print("PASS", t())
    (HERE / "run_mock" / "MOCK_DATA_NOT_RESULTS.txt").write_text(
        "Everything under run_mock/ is synthetic test data produced by sf_tests.py. It is NOT experimental output.\n")
