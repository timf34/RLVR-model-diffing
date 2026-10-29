"""EXPLORATORY records-vs-prose run on the recommendation task (see ANALYSIS_PLAN.md).

Run from the repo root (every Python process under memguard):
  M="$HOME/.claude/bin/memguard -m 4 -- .venv/bin/python designs/rec_mechanisms/records/run_records.py"
  $M check | inspect | freeze
  timeout 560 $M generate        # repeat until "all items done" (resumable by item key; ~9-minute chunks)
  $M judge                        # blind judge for ambiguous openings only (as in the score-gap run)
  $M analyse                      # run/results.json, run/REPORT_auto.md, figure/records_vs_prose.png
Serving and the generation call are those of the score-gap run (designs/rl_context run_confirm.serving and the
pinned src snapshot's generation_config/adapter), wrapped here only to (a) store the reasoning text and token usage,
(b) run both models in one interleaved queue with a 32-request semaphore per model, and (c) stop cleanly inside a
chunk. Scoring: rec_score.measures (rule) + run_rec.judge_many for ambiguous openings, both imported read-only.
"""
import asyncio
import hashlib
import itertools
import json
import os
import random
import shutil
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
REC = ROOT / "designs" / "recommendation"
GAPD = ROOT / "designs" / "score_gap" / "recommendation"
RL = ROOT / "designs" / "rl_context"
sys.path[:0] = [str(HERE), str(GAPD), str(REC), str(RL)]
import run_confirm as R  # noqa: E402  (serving; imports run_pilot, which pins the src snapshot on sys.path)
import run_pilot as P  # noqa: E402
from score import completion  # noqa: E402  (rl_context/score.py)
import rec_materials as M  # noqa: E402
from rec_score import measures  # noqa: E402
import run_rec as RR  # noqa: E402  (judge_many)
import rec_records_materials as X  # noqa: E402
import rr_analysis as A  # noqa: E402
from copying import copy_measures  # noqa: E402

OUT = HERE / "run"
INSPECT_OUT = HERE / "inspection"
SAMPLES = 3
MODELS = ("Qwen 3.5", "Qwen 3.8")
CONCURRENCY = 32
LAUNCH_S, HARD_S = 400, 525   # per chunk: stop starting new requests / cancel in-flight ones
ABANDON_S = 1800              # cumulative in-flight time without a completion -> abandoned (failed)
MAX_ERRORS = 3                # first attempt + 2 retry passes
BUDGET = 60.0
# OpenRouter list prices of the pinned endpoints, USD per token (fetched 2026-10-29 from /api/v1/models/.../endpoints)
PRICE = {"Qwen 3.5": (0.30e-6, 2.40e-6), "Qwen 3.8": (0.15e-6, 1.875e-6)}
JUDGE_COST_PER_CALL = 0.01    # upper-end estimate for one Sonnet judge call (~2k in, ~100 out tokens)
CODE = ["rec_records_materials.py", "copying.py", "rr_analysis.py", "simulate.py", "run_records.py",
        "ANALYSIS_PLAN.md", "simulation/CALIBRATION.md"]
DEPS = [REC / f for f in ("rec_materials.py", "rec_score.py", "run_rec.py")] + \
       [GAPD / f for f in ("gap_materials.py",)] + [RL / f for f in ("run_pilot.py", "run_confirm.py", "score.py")]
COLORS = {"Qwen 3.5": "#2a78d6", "Qwen 3.8": "#eb6834"}


def scenario(sid):
    return next(s for s in M.SCENARIOS + M.INSPECTION if s["id"] == sid)


def serving():
    s = R.serving()
    s["targets"] = [t for t in s["targets"] if t["label"] in MODELS]
    return s


def plan(scenarios=M.SCENARIOS, samples=SAMPLES, tag="rr", conds=None):
    out = []
    for si, s in enumerate(scenarios):
        for f, fm, g in conds or X.conditions():
            prompt = X.render(s, si, f, fm, g)
            lab = "none" if g is None else X.gap_label(g)
            for m, r in itertools.product(MODELS, range(samples)):
                out.append(dict(key=f"{tag}|{s['id']}|{f}|{fm or 'nohist'}|{lab}|{m}|{r}", set=tag, scenario=s["id"],
                                context=f, format=fm or "nohist", scores=lab, gap=g, user=X.WORDING, model=m, rep=r,
                                **prompt))
    return out


def inspection_plan():
    conds = [(f, fm, 0.5) for f in X.FRAMINGS for fm in X.FORMATS] + [("chat", "records", -0.5), ("episode", None, None)]
    return plan(M.INSPECTION[:1], 1, "inspect", conds)


# ---------------------------------------------------------------- generation

def load_lines(path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()] if path.exists() else []


def cost_of(rec):
    pin, pout = PRICE[rec["model"]]
    u = rec.get("usage") or {}
    return (u.get("input_tokens") or 0) * pin + (u.get("output_tokens") or 0) * pout


def spent(out_dir):
    gens = load_lines(out_dir / "generations.jsonl")
    judged = len(load_lines(out_dir / "judge.jsonl"))
    return sum(cost_of(g) for g in gens) + judged * JUDGE_COST_PER_CALL, len(gens), judged


def key_usage():
    """Account-level OpenRouter usage (USD). Shared key: an upper bound on this run's spend, never printed with the key."""
    try:
        import httpx
        r = httpx.get("https://openrouter.ai/api/v1/key", timeout=20,
                      headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"})
        return float(r.json()["data"]["usage"])
    except Exception:  # noqa: BLE001
        return float("nan")


def make_adapter(model, config):
    """petri_task.adapter (pinned snapshot) plus the reasoning text. Same request; the returned record is richer."""
    from inspect_ai.model import ChatMessageSystem, ChatMessageUser

    async def gen(system, user):
        out = await model.generate(input=[ChatMessageSystem(content=system), ChatMessageUser(content=user)],
                                   config=config, cache=False)
        content = out.message.content
        text = content if isinstance(content, str) else "\n".join(i.text for i in content if i.type == "text")
        reasoning = [] if isinstance(content, str) else [
            dict(text=getattr(i, "reasoning", "") or "", redacted=bool(getattr(i, "redacted", False)))
            for i in content if i.type == "reasoning"]
        reason = out.choices[0].stop_reason if out.choices else "unknown"
        u = out.usage
        usage = {k: getattr(u, k, None) for k in ("input_tokens", "output_tokens", "reasoning_tokens")} if u else {}
        return text, ("ok" if reason == "stop" else "incomplete"), dict(stop_reason=reason, model=out.model), usage, reasoning
    return gen


async def generate(items, out_dir):
    from dotenv import load_dotenv
    from inspect_ai.model import get_model
    from model_diffing.petri_task import generation_config
    load_dotenv(ROOT / ".env")
    t0 = time.monotonic()
    srv = serving()
    gens = {t["label"]: make_adapter(get_model(t["model"], **t.get("model_args", {})), generation_config(srv, t))
            for t in srv["targets"]}
    out_dir.mkdir(parents=True, exist_ok=True)
    gpath, spath = out_dir / "generations.jsonl", out_dir / "inflight.jsonl"
    recs = load_lines(gpath)
    done = {r["key"] for r in recs if r["status"] != "error"}
    errs = Counter(r["key"] for r in recs if r["status"] == "error")
    abandoned = {r["key"] for r in recs if r.get("abandoned")}
    inflight = defaultdict(float)
    for r in load_lines(spath):
        inflight[r["key"]] += r["seconds"]
    lock = asyncio.Lock()

    def write(rec):
        with gpath.open("a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    base = {k: i for k, i in ((i["key"], i) for i in items)}
    for k in base:
        if k not in done and k not in abandoned and inflight[k] >= ABANDON_S:
            write(dict(meta(base[k]), status="error", abandoned=True, reply="", reasoning=[], usage={},
                       private=[{"error": f"abandoned: no completion after {inflight[k]:.0f}s in flight"}],
                       at=now()))
            abandoned.add(k)
    todo = [i for i in items if i["key"] not in done and i["key"] not in abandoned and errs[i["key"]] < MAX_ERRORS]
    random.Random(len(recs)).shuffle(todo)  # all conditions and both models interleaved
    cost, ng, nj = spent(out_dir)
    print(f"generate: {len(todo)} to do, {len(done)} done, {len(abandoned)} abandoned, "
          f"{sum(1 for k, v in errs.items() if v >= MAX_ERRORS and k not in done)} failed after retries; "
          f"estimated spend so far ${cost:.2f}", flush=True)
    if cost >= BUDGET:
        raise SystemExit("Budget reached; stopping.")
    if not todo:
        print("all items done", flush=True)
        return
    sems = {m: asyncio.Semaphore(CONCURRENCY) for m in MODELS}
    n, spend = [0], [cost]

    async def run(item):
        async with sems[item["model"]]:
            if time.monotonic() - t0 > LAUNCH_S or spend[0] >= BUDGET:
                return
            start = time.monotonic()
            try:
                text, status, priv, usage, reasoning = await asyncio.wait_for(
                    gens[item["model"]](item["system"], item["turns"][0]), R.TIMEOUT)
                rec = dict(meta(item), status=status, private=[priv], usage=usage, reply=text, reasoning=reasoning,
                           at=now())
            except asyncio.CancelledError:
                with spath.open("a") as f:
                    f.write(json.dumps(dict(key=item["key"], seconds=time.monotonic() - start)) + "\n")
                raise
            except Exception as e:  # noqa: BLE001
                rec = dict(meta(item), status="error", private=[{"error": f"{type(e).__name__}: {str(e)[:300]}"}],
                           usage={}, reply="", reasoning=[], at=now())
            async with lock:
                write(rec)
                spend[0] += cost_of(rec)
                n[0] += 1
                if n[0] % 100 == 0:
                    print(f"  {n[0]} written, {time.monotonic() - t0:.0f}s, est. spend ${spend[0]:.2f}", flush=True)

    tasks = [asyncio.create_task(run(i)) for i in todo]
    _, pending = await asyncio.wait(tasks, timeout=max(1, HARD_S - (time.monotonic() - t0)))
    for t in pending:
        t.cancel()
    await asyncio.gather(*pending, return_exceptions=True)
    left = len(todo) - n[0]
    print(f"chunk end: {n[0]} written this chunk, {len(pending)} cancelled in flight, {left} left; "
          f"est. spend ${spend[0]:.2f}", flush=True)


def meta(item):
    return {k: item[k] for k in ("key", "set", "scenario", "context", "format", "scores", "user", "model", "rep")}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------------------------------------------------------------- scoring

def records(out_dir, items):
    by_key, rows = {i["key"]: i for i in items}, {}
    for g in load_lines(out_dir / "generations.jsonl"):
        if g["key"] in by_key:
            old = rows.get(g["key"])
            if old is None or old["status"] == "error":  # a completed record wins over error records
                rows[g["key"]] = {k: v for k, v in by_key[g["key"]].items() if k not in ("system", "turns")} | {
                    k: g.get(k) for k in ("status", "private", "reply", "reasoning", "usage", "at", "abandoned")}
    return list(rows.values())


def scored(items, out_dir, judge=None):
    judge = judge or {}
    rows = records(out_dir, items)
    for r in rows:
        r["completion"], r["m"], r["copy"] = completion(r["reply"], r["status"]), {}, None
        if r["completion"] != "valid":
            continue
        j = judge.get(r["key"], {})
        s = scenario(r["scenario"])
        m = measures(r["reply"], s, judge_action=j.get("recommended"))
        r["m"] = m
        if not m["parsed"]:
            r["completion"] = "unparsed"
        elif m["upsell"] or m["correct"]:
            si = [x["id"] for x in M.SCENARIOS + M.INSPECTION].index(r["scenario"])
            si = si if r["set"] != "inspect" else 0
            r["copy"] = copy_measures(r["reply"], s, si, m["upsell"])
    return rows


def judge_ambiguous(rows, path):
    cases = [(r["key"], M.message(scenario(r["scenario"]), X.WORDING), r["reply"]) for r in rows
             if r["completion"] in ("valid", "unparsed") and r["m"].get("ambiguous")]
    asyncio.run(RR.judge_many(cases, path))


# ---------------------------------------------------------------- analysis

def analyse(items, out_dir=OUT, manifest=None):
    judge = P.load(out_dir / "judge.jsonl")
    rows = scored(items, out_dir, judge)
    valid = [r for r in rows if r["completion"] == "valid"]
    present = {r["key"] for r in rows}
    missing = Counter((i["model"]) for i in items if i["key"] not in present)
    bad = Counter((r["model"], r["context"], r["format"], r["completion"]) for r in rows if r["completion"] != "valid")
    obs = {(m, f, fm): [dict(scenario=r["scenario"], gap=r["gap"], y=int(r["m"]["upsell"])) for r in valid
                        if r["model"] == m and r["context"] == f and r["format"] == fm]
           for m in MODELS for f in X.FRAMINGS for fm in X.FORMATS}
    res = {"gaps": list(X.GAPS), "cells": {}, "baseline": {}, "tests": {}, "copying": {}, "nonvalid": {},
           "n_items": len(items), "n_present": len(rows)}
    for (m, f, fm), o in obs.items():
        if o:
            res["cells"][f"{m}|{f}|{fm}"] = A.rates_ci(o)
    for m, f in itertools.product(MODELS, X.FRAMINGS):
        sel = [r for r in valid if r["model"] == m and r["context"] == f and r["format"] == "nohist"]
        res["baseline"][f"{m}|{f}"] = dict(k=sum(r["m"]["upsell"] for r in sel), n=len(sel),
                                           correct=sum(r["m"]["correct"] for r in sel))
    for m, f, g in itertools.product(MODELS, X.FRAMINGS, A.TEST_GAPS):
        a, b = obs[(m, f, "prose")], obs[(m, f, "records")]
        if a and b:
            res["tests"][f"{m}|{f}|{X.gap_label(g)}"] = A.paired_test(a, b, g)
    hp = A.holm({k: v["p"] for k, v in res["tests"].items()})
    for k, v in res["tests"].items():
        v["p_holm"] = hp.get(k, float("nan"))
    for m, f, fm in itertools.product(MODELS, X.FRAMINGS, X.FORMATS + ("nohist",)):
        for g in (X.GAPS if fm != "nohist" else (None,)):
            sel = [r for r in valid if r["model"] == m and r["context"] == f and r["format"] == fm and r["gap"] == g]
            for kind, want in (("upsell", True), ("cheapest", False)):
                c = [r["copy"] for r in sel if r["copy"] is not None and r["m"]["upsell"] == want]
                res["copying"][f"{m}|{f}|{fm}|{'none' if g is None else X.gap_label(g)}|{kind}"] = dict(
                    n=len(c), frame=sum(x["frame"] for x in c), phrase=sum(x["phrase"] for x in c),
                    verbatim=sum(x["verbatim"] for x in c), ngram6=sum(x["ngram"] >= 6 for x in c),
                    ngram_mean=(sum(x["ngram"] for x in c) / len(c)) if c else None)
    for (m, f, fm, c), v in bad.items():
        res["nonvalid"][f"{m}|{f}|{fm}|{c}"] = v
    res["missing"] = dict(missing)
    res["action_source"] = dict(strict=sum(1 for r in valid if r["m"]["strict"]),
                                judge=sum(1 for r in valid if not r["m"]["strict"]))
    cost, ng, nj = spent(out_dir)
    res["cost_estimate_usd"] = dict(total=cost, records=ng, judge_calls=nj,
                                    by_model={m: sum(cost_of(g) for g in load_lines(out_dir / "generations.jsonl")
                                                     if g["model"] == m) for m in MODELS})
    res["tokens"] = {m: dict(
        output=sum((r.get("usage") or {}).get("output_tokens") or 0 for r in rows if r["model"] == m),
        reasoning_text_present=sum(1 for r in rows if r["model"] == m and any(x["text"] for x in r.get("reasoning") or [])))
        for m in MODELS}
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "results.json").write_text(json.dumps(res, indent=1, default=float))
    report(res, out_dir, manifest)
    return res, rows


def report(res, out_dir, manifest):
    pc = lambda x: f"{100 * x:.0f}%"
    L = ["# Records vs prose history: results (EXPLORATORY; auto-generated)", "",
         f"- Conversations present: **{res['n_present']} of {res['n_items']}**",
         f"- Non-valid (excluded; never counted as following the user): {sum(res['nonvalid'].values())} "
         f"{dict(Counter(k.split('|')[3] for k in res['nonvalid'] for _ in range(res['nonvalid'][k])))}",
         f"- Action source: {res['action_source']['strict']} strict rule parses, {res['action_source']['judge']} judge.",
         f"- Estimated cost: ${res['cost_estimate_usd']['total']:.2f}"]
    if manifest:
        L.append(f"- Manifest sha256 `{manifest['sha256'][:12]}`; analysis plan sha256 `{manifest['plan_sha256'][:12]}`.")
    L += ["", "## Upsell rate (k/n, scenario-cluster 95% CI)", "",
          "| Model | framing | format | " + " | ".join(X.gap_label(g) for g in X.GAPS) + " | no history |",
          "|---|---|---|" + "---|" * (len(X.GAPS) + 1)]
    for m, f, fm in itertools.product(MODELS, X.FRAMINGS, X.FORMATS):
        c = res["cells"].get(f"{m}|{f}|{fm}")
        if not c:
            continue
        b = res["baseline"][f"{m}|{f}"]
        L.append(f"| {m} | {f} | {fm} | " + " | ".join(
            f"{int(k)}/{int(n)} ({pc(lo)}–{pc(hi)})" for k, n, lo, hi in zip(c["k"], c["n"], c["lo"], c["hi"]))
            + f" | {b['k']}/{b['n']} |")
    L += ["", "## Planned contrasts: prose minus records (paired scenario sign-flip, exact; Holm over 12)", "",
          "| Model | framing | level | prose | records | diff (95% CI) | p | Holm p |", "|---|---|---|---|---|---|---|---|"]
    for k, v in res["tests"].items():
        m, f, g = k.split("|")
        L.append(f"| {m} | {f} | {g} | {pc(v['rate_prose'])} | {pc(v['rate_records'])} | "
                 f"{100 * v['diff']:+.0f} pp ({100 * v['lo']:+.0f} to {100 * v['hi']:+.0f}) | {v['p']:.2g} | "
                 f"{v['p_holm']:.2g} |")
    L += ["", "## Template reuse (secondary): upsell replies using the prose upsell frame / phrase", "",
          "| Model | framing | format | " + " | ".join(X.gap_label(g) for g in X.GAPS) + " |",
          "|---|---|---|" + "---|" * len(X.GAPS)]
    for m, f, fm in itertools.product(MODELS, X.FRAMINGS, X.FORMATS):
        cells = [res["copying"][f"{m}|{f}|{fm}|{X.gap_label(g)}|upsell"] for g in X.GAPS]
        L.append(f"| {m} | {f} | {fm} | " + " | ".join(
            f"{c['frame']}/{c['phrase']} of {c['n']}" if c["n"] else "–" for c in cells) + " |")
    L += ["", "Cheapest-option replies using the prose cheapest frame / phrase", "",
          "| Model | framing | format | " + " | ".join(X.gap_label(g) for g in X.GAPS) + " | no history |",
          "|---|---|---|" + "---|" * (len(X.GAPS) + 1)]
    for m, f, fm in itertools.product(MODELS, X.FRAMINGS, X.FORMATS):
        cells = [res["copying"][f"{m}|{f}|{fm}|{X.gap_label(g)}|cheapest"] for g in X.GAPS]
        nb = res["copying"][f"{m}|{f}|nohist|none|cheapest"]
        L.append(f"| {m} | {f} | {fm} | " + " | ".join(
            f"{c['frame']}/{c['phrase']} of {c['n']}" if c["n"] else "–" for c in cells)
            + f" | {nb['frame']}/{nb['phrase']} of {nb['n']} |")
    if res["nonvalid"]:
        L += ["", "## Non-valid by cell", ""] + [f"- {k}: {v}" for k, v in sorted(res["nonvalid"].items())]
    (out_dir / "REPORT_auto.md").write_text("\n".join(L) + "\n")
    print(f"Wrote {out_dir / 'REPORT_auto.md'}")


def figure(out_dir=OUT, name="records_vs_prose.png"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    res = json.loads((out_dir / "results.json").read_text())
    ink, muted, grid, bg = "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.6), sharey=True, facecolor=bg)
    xs = list(range(len(X.GAPS)))
    base_x = -1.2
    titles = {"chat": "Chat", "episode": "Episode / reward wording", "bundle": "Training-style bundle"}
    for ax, f in zip(axes, X.FRAMINGS):
        ax.set_facecolor(bg)
        for i, (m, fm) in enumerate(itertools.product(MODELS, X.FORMATS)):
            c = res["cells"].get(f"{m}|{f}|{fm}")
            if not c:
                continue
            off = (i - 1.5) * 0.07
            yerr = [[r - lo for r, lo in zip(c["rate"], c["lo"])], [hi - r for r, hi in zip(c["rate"], c["hi"])]]
            ax.errorbar([x + off for x in xs], c["rate"], yerr=yerr, color=COLORS[m],
                        marker="o" if fm == "prose" else "s", markersize=5.5, lw=2,
                        ls="-" if fm == "prose" else "--", capsize=0, elinewidth=1.1, label=f"{m}, {fm}",
                        markeredgecolor=bg, markeredgewidth=1, markerfacecolor=COLORS[m] if fm == "prose" else bg)
        for j, m in enumerate(MODELS):
            b = res["baseline"].get(f"{m}|{f}")
            if b and b["n"]:
                ax.plot([base_x + (j - 0.5) * 0.12], [b["k"] / b["n"]], marker="D", color=COLORS[m], markersize=5.5,
                        markerfacecolor=bg, markeredgewidth=1.5, ls="none")
        ax.axvline(1, color=grid, lw=1, zorder=0)
        ax.axvline(-0.6, color=grid, lw=1, ls=":", zorder=0)
        ax.set_xticks([base_x] + xs, ["no\nhistory"] + [X.gap_label(g) for g in X.GAPS], fontsize=8, color=muted)
        ax.set_xlim(base_x - 0.5, len(X.GAPS) - 0.5)
        ax.set_ylim(-0.03, 1.05)
        ax.grid(axis="y", color=grid, lw=0.8)
        ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        for sp in ("left", "bottom"):
            ax.spines[sp].set_color(grid)
        ax.tick_params(colors=muted)
        ax.set_title(titles[f], fontsize=10, color=ink, loc="left")
        ax.set_xlabel("Score advantage for the upsell example (levels evenly spaced, not to scale)", fontsize=8,
                      color=muted)
    axes[0].set_ylabel("P(recommends the upsell)", color=ink)
    axes[0].legend(frameon=False, fontsize=8, loc="upper left")
    fig.suptitle("Upsell rate: history shown as prose answers (solid) vs structured records (dashed). EXPLORATORY; "
                 "12 scenarios × 3 replies per point; bars = scenario-cluster 95% CI; hollow diamond = no history",
                 fontsize=9, color=muted, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    path = HERE / "figure" / name
    path.parent.mkdir(exist_ok=True)
    fig.savefig(path, dpi=160, facecolor=fig.get_facecolor())
    print(f"Wrote {path}")


# ---------------------------------------------------------------- main

def code_hashes():
    h = {f: hashlib.sha256((HERE / f).read_bytes()).hexdigest() for f in CODE}
    h |= {f"{p.parent.name}/{p.name}": hashlib.sha256(p.read_bytes()).hexdigest() for p in DEPS}
    return h


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "check":
        X.check()
        return print(f"{len(plan())} main conversations ({len(plan()) // len(MODELS)} per model), "
                     f"{len(inspection_plan())} inspection")
    if cmd == "inspect":
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
        u0 = key_usage()
        items = inspection_plan()
        asyncio.run(generate(items, INSPECT_OUT))
        rows = scored(items, INSPECT_OUT)
        judge_ambiguous(rows, INSPECT_OUT / "judge.jsonl")
        rows = scored(items, INSPECT_OUT, P.load(INSPECT_OUT / "judge.jsonl"))
        for r in sorted(rows, key=lambda r: r["key"]):
            rs = r.get("reasoning") or []
            print(f"{r['key']}: {r['completion']} strict={r['m'].get('strict')} rec={r['m'].get('recommended')} "
                  f"out_tok={(r.get('usage') or {}).get('output_tokens')} reasoning_chars={sum(len(x['text']) for x in rs)} "
                  f"| {r['reply'][:110]!r}")
        print(f"estimated inspection cost ${spent(INSPECT_OUT)[0]:.3f}; account usage delta (shared key, upper bound) "
              f"${key_usage() - u0:.3f}")
        return
    items, srv = plan(), serving()
    manifest = OUT / "manifest.json"
    if cmd == "freeze":
        OUT.mkdir(exist_ok=True)
        if manifest.exists():
            raise SystemExit("Already frozen")
        snap = OUT / "code_snapshot"
        snap.mkdir(exist_ok=True)
        for f in CODE:
            shutil.copy(HERE / f, snap / Path(f).name)
        for p in DEPS:
            shutil.copy(p, snap / p.name)
        manifest.write_text(json.dumps(dict(
            sha256=P.digest(items, srv), label="EXPLORATORY records vs prose (analysis plan frozen before generation)",
            at=now(), samples=SAMPLES, total=len(items), gaps=X.GAPS, framings=X.FRAMINGS, formats=X.FORMATS,
            models=MODELS, concurrency_per_model=CONCURRENCY, budget_usd=BUDGET, price_per_token=PRICE,
            plan_sha256=hashlib.sha256((HERE / "ANALYSIS_PLAN.md").read_bytes()).hexdigest(),
            code_sha256=code_hashes(), serving=srv, serving_notes={m: R.SERVING_NOTES[m] for m in MODELS}),
            indent=2) + "\n")
        json.dump([{k: i[k] for k in ("key", "system", "turns")} for i in items], open(OUT / "prompts.json", "w"),
                  indent=1)
        return print(f"Frozen {len(items)} conversations")
    if not manifest.exists() or json.loads(manifest.read_text())["sha256"] != P.digest(items, srv):
        raise SystemExit("Not frozen, or prompts/serving changed since freezing")
    if json.loads(manifest.read_text())["code_sha256"] != code_hashes():
        raise SystemExit("Code changed since freezing")
    if cmd == "generate":
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
        u0 = key_usage()
        asyncio.run(generate(items, OUT))
        (OUT / "logs").mkdir(exist_ok=True)
        with (OUT / "logs" / "account_usage.log").open("a") as f:
            f.write(json.dumps(dict(at=now(), account_usage_delta_upper_bound=key_usage() - u0,
                                    est_run_total=spent(OUT)[0])) + "\n")
        return
    if cmd == "judge":
        return judge_ambiguous(scored(items, OUT), OUT / "judge.jsonl")
    if cmd == "analyse":
        analyse(items, OUT, json.loads(manifest.read_text()))
        return figure(OUT)
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
