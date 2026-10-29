"""Offline tests for the presentation ablation (no API calls; nothing outside a scratch dir is written).

  python pa_tests.py            # all tests (about 2-3 minutes)
  python pa_tests.py --quick    # skip the full mock main run

Tests that need the old modules run per kind in a subprocess (`python pa_tests.py _kind send|fmt <scratch>`), since
designs/action and designs/rl_context share module names.
"""
from __future__ import annotations

import asyncio
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
PY = sys.executable
RESULTS: list[tuple[str, bool, str]] = []


def run(cmd: list[str], ok=True, env=None) -> str:
    p = subprocess.run([PY, *cmd], cwd=HERE, capture_output=True, text=True, env=env)
    if ok and p.returncode != 0:
        raise AssertionError(f"{' '.join(cmd)} failed:\n{p.stdout[-1500:]}\n{p.stderr[-2500:]}")
    if not ok and p.returncode == 0:
        raise AssertionError(f"{' '.join(cmd)} unexpectedly succeeded")
    return p.stdout + p.stderr


def test(fn):
    t0 = time.time()
    try:
        msg = fn() or ""
        RESULTS.append((fn.__name__, True, f"{msg} ({time.time() - t0:.1f}s)"))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((fn.__name__, False, f"{type(e).__name__}: {str(e)[:1500]}\n{traceback.format_exc()[-800:]}"))


# ============================================================================== per-kind tests (subprocess body)

def kind_tests(kind: str, scratch: Path) -> list[str]:
    import pa_checks as C
    import pa_materials as PM
    from pa_render import ALL_B, N_END, cfg_of, part2_arms, render
    out = []
    Ks = PM.adapters(kind)
    # 1. the full offline check battery (byte identity, one-component, scores, fresh blocks)
    for line in C.run_all(kind, Ks):
        out.append(line[:120])
    # 2. negative controls: the checks must catch a two-component change and a stray byte
    K = next(iter(Ks.values()))
    u = K.units("fresh")[0]
    try:
        C.check_arm_pair(K, u, 0.5, cfg_of(ALL_B, a="N", e="N"), ALL_B)
        raise RuntimeError("two-component arm passed")
    except AssertionError:
        pass
    for k in "abcdefg":
        xb = render(K, u, ALL_B, 0.5)
        xn = render(K, u, cfg_of(ALL_B, **{k: "N"}), 0.5)
        bad = json.loads(json.dumps(xn))
        if bad["packet_tool"]:
            bad["messages"][2]["content"] += " "
        else:
            bad["messages"][0]["content"] += " "
        if k in "ae":  # system-only components: tamper the system instead
            bad["system"] += " "
        try:
            C.component_normalise(K, u, k, xb, bad, ALL_B, cfg_of(ALL_B, **{k: "N"}), 0.5)
            raise RuntimeError(f"tampered arm for component {k} passed")
        except AssertionError:
            pass
    out.append("negative controls: two-component arm and one stray byte per component are rejected")
    # 3. every Part 2 arm differs from its endpoint in exactly one component flag
    for name, cfg in part2_arms().items():
        base = ALL_B if name.startswith("B-") else N_END
        assert sum(cfg[k] != base[k] for k in cfg) == 1 and name[2] in cfg and cfg[name[2]] != base[name[2]]
    out.append(f"{len(part2_arms())} Part 2 arm configs: one flag each")
    # 4. ALL-B generation loop == the old driver's loop (first call: messages, tools)
    out.append(asyncio.run(loop_equivalence(kind, Ks)))
    return out


async def loop_equivalence(kind: str, Ks: dict) -> str:
    from types import SimpleNamespace
    from inspect_ai.model import ChatMessageAssistant
    import pa_generate as G
    from pa_common import SENDING, load_file
    from pa_render import ALL_B, render

    class Rec:
        def __init__(self):
            self.calls = []

        async def generate(self, input, tools=None, config=None, cache=False):  # noqa: A002
            self.calls.append(([(m.role, m.content) for m in input],
                               [(t.name, t.description, t.parameters.model_dump()) for t in (tools or [])]))
            return SimpleNamespace(message=ChatMessageAssistant(content="Done."), model="rec",
                                   choices=[SimpleNamespace(stop_reason="stop")],
                                   usage=SimpleNamespace(input_tokens=1, output_tokens=1, reasoning_tokens=0))

    n = 0
    for task, K in Ks.items():
        for u in K.units("orig")[:3]:
            conv = render(K, u, ALL_B, 0.5)
            mine = Rec()
            item = dict(task=task, model="Qwen 3.8")
            ep = await G.episode(mine, None, item, conv, dict(raw=u["raw"]), asyncio.Semaphore(1))
            assert ep["status"] == "ok" and ep["final_reply"] == "Done."
            old = Rec()
            if task == "send":
                RG = load_file("pa_old_run_gap", SENDING / "run_gap.py")

                async def policy(messages, tools):
                    out = await old.generate(messages, tools)
                    return dict(message=out.message, stop="stop", usage={})
                await RG.run_episode(policy, u["raw"], dict(system=conv["system"],
                                                            turns=[conv["messages"][0]["content"]]))
            else:  # converse + adapter (designs/rl_context/pilot/src_snapshot), as the old formatting run used
                from pa_common import RL
                sys.path.insert(0, str(RL / "pilot" / "src_snapshot"))
                from model_diffing.core import converse
                from model_diffing.petri_task import adapter

                class AdapterRec(Rec):
                    async def generate(self, input=None, tools=None, config=None, cache=False):  # noqa: A002
                        return await super().generate(input, tools, config, cache)
                old = AdapterRec()
                await converse(adapter(old, config=None), [conv["messages"][0]["content"]], system=conv["system"],
                               timeout=60, semaphore=asyncio.Semaphore(1))
            assert mine.calls[0] == old.calls[0], (task, u["block"])
            n += 1
    return f"ALL-B first model call identical to the old driver's (run_gap.run_episode / converse+adapter): {n}"


# ============================================================================== top-level tests

SCR = Path(tempfile.mkdtemp(prefix="pa_tests_"))


def test_kind_send():
    return "; ".join(json.loads(run(["pa_tests.py", "_kind", "send", str(SCR)]).strip().splitlines()[-1]))[:400]


def test_kind_fmt():
    return "; ".join(json.loads(run(["pa_tests.py", "_kind", "fmt", str(SCR)]).strip().splitlines()[-1]))[:400]


def test_prepare_and_counts():
    root = SCR / "root"
    for k in ("send", "fmt"):
        for st in ("main", "smoke"):
            run(["pa_prepare.py", k, "--stage", st, "--root", str(root), "--skip-checks"])
    from collections import Counter
    from pa_common import GAPS, MODELS, TASKS, iter_jsonl
    from pa_design import ORIG_REPS, N_FRESH, expected_counts, plan
    from pa_render import part1_arms, part2_arms
    units = json.loads((root / "units.json").read_text())
    assert {t: len(units[t]["orig"]) for t in TASKS} == {"send": 12, "titles": 12, "bullets": 6}
    assert {t: len(units[t]["fresh"]) for t in TASKS} == {"send": 32, "titles": 32, "bullets": 32}
    for st in ("main", "smoke"):
        items = plan(st, units)
        got = Counter(i["task"] for i in items)
        assert dict(got) == expected_counts(st, units), (st, got)
        for t in TASKS:
            rows = list(iter_jsonl(root / st / t / "items.jsonl"))
            assert [r["key"] for r in rows] == [i["key"] for i in items if i["task"] == t]
    main = plan("main", units)
    from pa_design import FRESH_REPS
    n_fresh_eps = 32 * 15 * 2 * sum(FRESH_REPS.values())
    assert len(main) == 3 * (288 + n_fresh_eps), len(main)
    cells = Counter((i["task"], i["block"], i["arm"]) for i in main)
    for (t, b, arm), n in cells.items():  # full grid per block x arm: scores x models x reps
        reps = ORIG_REPS[t] * len(MODELS) if b.startswith("orig:") else sum(FRESH_REPS.values())
        assert n == len(GAPS) * reps, (t, b, arm, n)
    assert {i["arm"] for i in main if i["materials"] == "orig"} == set(part1_arms())
    assert {i["arm"] for i in main if i["part"] == 2} == set(part2_arms()) and len(part2_arms()) == 13
    assert all(i["materials"] == "fresh" for i in main if i["part"] == 2)
    for t in TASKS:
        assert len({i["block"] for i in main if i["task"] == t and i["materials"] == "fresh"}) == N_FRESH[t]
    return (f"main {len(main)} (per task: orig 288 + fresh 32 blocks x 15 arms x 2 scores x {FRESH_REPS}), "
            f"smoke {len(plan('smoke', units))}")


def test_freeze_verify():
    root = SCR / "root"
    out = run(["pa_freeze.py", "freeze", "main", "--root", str(root)])
    run(["pa_freeze.py", "verify", "main", "--root", str(root)])
    p = root / "main" / "send" / "items.jsonl"
    orig = p.read_text()
    lines = orig.splitlines()
    assert '"score": "tied"' in lines[5]
    lines[5] = lines[5].replace('"score": "tied"', '"score": "p050"')  # a non-key field
    p.write_text("\n".join(lines) + "\n")
    run(["pa_freeze.py", "verify", "main", "--root", str(root)], ok=False)
    p.write_text(orig)
    q = root / "main" / "titles" / "prompts.jsonl"
    origq = q.read_text()
    q.write_text(origq.replace("I'd prefer no title", "I'd prefer no titles", 1))
    run(["pa_freeze.py", "verify", "main", "--root", str(root)], ok=False)
    q.write_text(origq)
    run(["pa_freeze.py", "verify", "main", "--root", str(root)])
    return out.strip()[:160] + "; tampered items / prompt detected"


def test_generate_offline():
    root = SCR / "root"
    o = run(["pa_generate.py", "smoke", "--root", str(root), "--mock", "scripted"])
    assert "stop=complete" in o, o
    o2 = run(["pa_generate.py", "smoke", "--root", str(root), "--mock", "scripted"])
    assert "pass 1" not in o2 and "stop=complete" in o2, o2  # resume: nothing left to do
    fresh = SCR / "root_budget"
    for k in ("send", "fmt"):
        run(["pa_prepare.py", k, "--stage", "smoke", "--root", str(fresh), "--skip-checks"])
    o3 = run(["pa_generate.py", "smoke", "--root", str(fresh), "--mock", "scripted", "--budget-stop", "0.001"])
    assert "stop=budget" in o3, o3
    o4 = run(["pa_generate.py", "smoke", "--root", str(fresh), "--mock", "scripted", "--max-items", "5"])
    n = sum(1 for p in (fresh / "smoke").glob("*/episodes.jsonl") for _ in p.open())
    assert n == 5 and "stop=max_items" in o4, (n, o4)
    run(["pa_generate.py", "smoke", "--root", str(fresh), "--mock", "mockllm"])
    nm = sum(1 for p in (fresh / "smoke").glob("*/episodes.jsonl") for _ in p.open())
    assert nm == 32, nm
    led = [json.loads(l) for l in (fresh / "ledger.jsonl").open()]
    assert len(led) == 32
    # main refuses without a valid freeze
    nofreeze = SCR / "root_nofreeze"
    run(["pa_prepare.py", "send", "--stage", "main", "--root", str(nofreeze), "--skip-checks"])
    run(["pa_generate.py", "main", "--root", str(nofreeze), "--mock", "scripted", "--max-items", "1"], ok=False)
    for k in ("send", "fmt"):
        run(["pa_score.py", k, "--stage", "smoke", "--root", str(root)])
    rows = [json.loads(l) for t in ("send", "titles", "bullets") for l in (root / "smoke" / t / "scored.jsonl").open()]
    assert len(rows) == 32 and all(r["completion"] == "valid" for r in rows)
    acted = [r for r in rows if r["task"] == "send" and r["outcome"]]
    assert acted, "scripted model never sent: scorer path untested"
    return f"smoke 32/32 scripted; resume, budget stop, max-items, mockllm, freeze gate, scoring ok ({len(acted)} sends)"


def test_real_config():
    code = ("import sys; sys.path.insert(0, '.'); import pa_generate as G; m = G.build_models(('Qwen 3.8', "
            "'Qwen 3.5'), None); import json; print(json.dumps({k: [str(v[0]), v[1].temperature, v[1].max_tokens, "
            "v[1].reasoning_effort, v[1].max_connections, v[1].top_p, v[1].extra_body] for k, v in m.items()}))")
    env = dict(os.environ, OPENROUTER_API_KEY="dummy-not-used")
    out = json.loads(run(["-c", code], env=env).strip().splitlines()[-1])
    assert out["Qwen 3.8"][1] == 0.7 and out["Qwen 3.8"][2] == 32768 and out["Qwen 3.8"][3] == "medium", out
    assert all(v[5] == 0.95 and v[6] == {"top_k": 20} for v in out.values()), out
    assert "qwen3.8" in out["Qwen 3.8"][0] and "qwen3.5" in out["Qwen 3.5"][0] and out["Qwen 3.5"][4] == 16, out
    from pa_common import serving
    labs = [t["label"] for t in serving()["targets"]]
    assert sorted(labs) == ["Qwen 3.5", "Qwen 3.8"]
    return f"generation configs build from experiment.grading.3way.json (no call made): {out}"


def test_analysis_simulated():
    import numpy as np
    import pa_analysis as A
    sys.path.insert(0, str(HERE / "simulation"))
    import simulate as SIM
    A.N_FLIP, A.N_PERM, A.N_BOOT = 4000, 2000, 300
    units = json.loads((SCR / "root" / "units.json").read_text())
    res = A.analyse_rows(SIM.rows_for("one", units, 3))
    p2 = res["primary"]["part2"]
    assert p2["REM:d"]["p_holm"] < 0.05 and p2["ADD:d"]["p_holm"] < 0.05, (p2["REM:d"], p2["ADD:d"])
    assert sum(r["p_holm"] < 0.05 for r in p2.values()) == 2, {k: r["p_holm"] for k, r in p2.items()}
    assert res["primary"]["part1"]["PRES"]["p_holm"] < 0.05 and res["primary"]["part1"]["PRES"]["estimate"] > 0.3
    sel = A.select(res)
    assert "d" in sel["components"] and sel["enabled"] is False
    res_m = A.analyse_rows(SIM.rows_for("materials", units, 4))
    assert res_m["primary"]["part1"]["MAT"]["estimate"] > 0.1 and res_m["primary"]["part1"]["MAT"]["p"] < 0.05
    nulls = [A.analyse_rows(SIM.rows_for("null", units, 10 + s))["primary"]["part2"] for s in range(3)]
    assert all(all(r["p_holm"] >= 0.05 for r in p.values()) for p in nulls)
    # Holm and Wilson sanity
    h = A.holm({"x": dict(p=0.01), "y": dict(p=0.04), "z": dict(p=0.03)})
    assert abs(h["x"]["p_holm"] - 0.03) < 1e-12 and abs(h["z"]["p_holm"] - 0.06) < 1e-12 and h["y"]["p_holm"] == 0.06
    lo, hi = A.wilson(10, 16)
    assert abs(lo - 0.3864) < 1e-3 and abs(hi - 0.8152) < 1e-3
    # report + figures render
    md = A.report(res, SIM.rows_for("one", units, 3))
    assert "Part 2 primaries" in md
    out = SCR / "simroot" / "main"
    out.mkdir(parents=True, exist_ok=True)
    (out / "results.json").write_text(json.dumps(res, default=float))
    run(["pa_figures.py", "--root", str(SCR / "simroot"), "--out", str(SCR / "fig")])
    assert (SCR / "fig" / "part2_components.png").exists()
    return (f"planted d effect recovered (REM:d {p2['REM:d']['estimate']:+.2f}, ADD:d {p2['ADD:d']['estimate']:+.2f}),"
            f" no other Part 2 rejection; MAT recovered; 3 null datasets: 0 Holm rejections; figures render")


def test_full_mock_pipeline():
    """prepare (done) -> freeze (done) -> generate main with the scripted model -> score -> analyse -> figures."""
    root = SCR / "root"
    o = run(["pa_generate.py", "main", "--root", str(root), "--mock", "scripted", "--concurrency", "32"])
    assert "stop=complete" in o, o[-500:]
    for k in ("send", "fmt"):
        run(["pa_score.py", k, "--root", str(root)])
    env = dict(os.environ)
    code = ("import sys; sys.path.insert(0,'.'); import pa_analysis as A; A.N_FLIP=A.N_PERM=2000; A.N_BOOT=200; "
            f"sys.argv=['x','analyse','--root',{str(root)!r}]; A.main()")
    run(["-c", code], env=env)
    run(["pa_figures.py", "--root", str(root), "--out", str(SCR / "fig_mock")])
    res = json.loads((root / "main" / "results.json").read_text())
    assert len(res["cells"]) > 0 and "REM:d" in res["primary"]["part2"]
    run(["pa_analysis.py", "select", "--root", str(root)])
    sel = json.loads((root / "factorial" / "selection.json").read_text())
    assert sel["enabled"] is False
    run(["pa_prepare.py", "send", "--stage", "factorial", "--root", str(root), "--skip-checks"], ok=False)  # gated
    run(["pa_analysis.py", "select", "--root", str(root), "--enable"])
    for k in ("send", "fmt"):
        run(["pa_prepare.py", k, "--stage", "factorial", "--root", str(root), "--skip-checks"])
    run(["pa_freeze.py", "freeze", "factorial", "--root", str(root)])
    run(["pa_freeze.py", "verify", "factorial", "--root", str(root)])
    return f"main scripted episodes -> scored -> analysed -> figures; factorial gate + prepare/freeze ok ({sel['components']})"


def test_components_doc():
    for k in ("send", "fmt"):
        run(["pa_prepare.py", k, "--components", "--root", str(SCR / "comp")])
    doc = (HERE / "COMPONENTS.md").read_text()
    for k in ("send", "fmt"):
        sec = (SCR / "comp" / f"components_{k}.md").read_text()
        assert sec.strip() in doc, f"COMPONENTS.md is stale for {k}: rerun pa_prepare.py {k} --components"
    return "COMPONENTS.md wording tables match the code"


def test_committed_inputs_frozen():
    from pa_common import RUN
    if not (RUN / "main" / "manifest.json").exists():
        return "SKIP: run/main not frozen yet"
    out = run(["pa_freeze.py", "verify", "main"])
    return out.strip()[:200]


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "_kind":
        print(json.dumps(kind_tests(sys.argv[2], Path(sys.argv[3]))))
        return
    quick = "--quick" in sys.argv
    for fn in [test_kind_send, test_kind_fmt, test_prepare_and_counts, test_freeze_verify, test_generate_offline,
               test_real_config, test_analysis_simulated, test_components_doc, test_committed_inputs_frozen]:
        test(fn)
    if not quick:
        test(test_full_mock_pipeline)
    for name, ok, msg in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'} {name}: {msg}")
    shutil.rmtree(SCR, ignore_errors=True)
    n_bad = sum(not ok for _, ok, _ in RESULTS)
    print(f"{len(RESULTS) - n_bad}/{len(RESULTS)} passed")
    sys.exit(1 if n_bad else 0)


if __name__ == "__main__":
    main()
