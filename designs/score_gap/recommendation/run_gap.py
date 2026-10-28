"""EXPLORATORY score-gap response curve on the recommendation task (see ANALYSIS_PLAN.md).

Run from the repo root:
  .venv/bin/python designs/score_gap/recommendation/run_gap.py check
  .venv/bin/python designs/score_gap/recommendation/run_gap.py inspect           # setup check only
  .venv/bin/python designs/score_gap/recommendation/run_gap.py freeze
  .venv/bin/python designs/score_gap/recommendation/run_gap.py generate "Qwen 3.6" 64
  .venv/bin/python designs/score_gap/recommendation/run_gap.py judge             # ambiguous openings only
  .venv/bin/python designs/score_gap/recommendation/run_gap.py analyse
Reuses designs/recommendation (rec_materials, rec_score, run_rec judge) and designs/rl_context (run_pilot,
run_confirm serving and generation) read-only; their hashes are recorded in the manifest.
"""
import asyncio
import hashlib
import itertools
import json
import shutil
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
REC = HERE.parents[1] / "recommendation"
RL = HERE.parents[1] / "rl_context"
sys.path[:0] = [str(HERE), str(REC), str(RL)]
import run_confirm as R  # noqa: E402
import run_pilot as P  # noqa: E402
from score import completion  # noqa: E402  (rl_context/score.py)
import rec_materials as M  # noqa: E402
from rec_score import measures  # noqa: E402
import run_rec as RR  # noqa: E402  (judge_many, judge prompt, validated before the recommendation freeze)
import gap_materials as G  # noqa: E402
import gap_analysis as A  # noqa: E402

OUT = HERE / "run"
INSPECT_OUT = HERE / "inspection"
SAMPLES = 3
CODE = ["gap_materials.py", "gap_analysis.py", "run_gap.py", "simulate.py", "ANALYSIS_PLAN.md",
        "simulation/CALIBRATION.md"]
DEPS = [REC / f for f in ("rec_materials.py", "rec_score.py", "run_rec.py")] + \
       [RL / f for f in ("run_pilot.py", "run_confirm.py", "score.py")]
MODELS = ("Qwen 3.5", "Qwen 3.6", "Qwen 3.8")
MODEL_PAIRS = (("Qwen 3.8", "Qwen 3.5"), ("Qwen 3.6", "Qwen 3.5"), ("Qwen 3.8", "Qwen 3.6"))
PANEL_PAIRS = (("episode", "chat"), ("bundle", "episode"), ("bundle", "chat"))


def scenario(sid):
    return next(s for s in M.SCENARIOS + M.INSPECTION if s["id"] == sid)


def plan(scenarios=M.SCENARIOS, samples=SAMPLES, tag="gap", gaps=G.GAPS):
    out = []
    for si, s in enumerate(scenarios):
        for fmt, g in G.conditions():
            if (g is not None and g != G.REF and g not in gaps) or (g == G.REF and tag != "gap"):
                continue
            prompt = G.render(s, si, fmt, g)
            lab = "none" if g is None else (G.REF if g == G.REF else G.gap_label(g))
            for m, r in itertools.product(R.labels(), range(samples)):
                out.append(dict(key=f"{tag}|{s['id']}|{fmt}|{lab}|{m}|{r}", set=tag, scenario=s["id"], context=fmt,
                                scores=lab, user=G.WORDING, model=m, rep=r, gap=g, facts=[], **prompt))
    return out


def inspection_plan():
    return plan(M.INSPECTION[:1], 1, "inspect", gaps=(-0.5, 0.0, 0.5))


def scored(items, out_dir, judge=None):
    """Valid rows get y = upsell. Action: strict rule parse, else the judge's pick (unparsed until judged)."""
    by_key, judge = {i["key"]: i for i in items}, judge or {}
    rows = R.load_records(out_dir, items)
    for r in rows:
        r["gap"] = by_key[r["key"]]["gap"]
        c = completion(r["reply"], r["status"])
        r["completion"], r["m"] = c, {}
        if c != "valid":
            continue
        j = judge.get(r["key"], {})
        m = measures(r["reply"], scenario(r["scenario"]), judge_action=j.get("recommended"))
        r["m"] = m
        if not m["parsed"]:
            r["completion"] = "unparsed"
    return rows


def judge_ambiguous(rows, path):
    cases = [(r["key"], M.message(scenario(r["scenario"]), G.WORDING), r["reply"]) for r in rows
             if r["completion"] in ("valid", "unparsed") and r["m"].get("ambiguous")]
    asyncio.run(RR.judge_many(cases, path))


# ---------------------------------------------------------------- analysis

def analyse(items, out_dir=OUT, manifest=None):
    judge = P.load(out_dir / "judge.jsonl")
    rows = scored(items, out_dir, judge)
    valid = [r for r in rows if r["completion"] == "valid"]
    bad = Counter((r["model"], r["context"], r["completion"]) for r in rows if r["completion"] != "valid")
    obs = {(m, p): [dict(scenario=r["scenario"], gap=r["gap"], y=int(r["m"]["upsell"])) for r in valid
                    if r["model"] == m and r["context"] == p and r["gap"] not in (None, G.REF)]
           for m in MODELS for p in G.PANELS}
    res = {"cells": {}, "trend": {}, "compare": {}, "baseline": {}, "reference": {}}
    for (m, p), o in obs.items():
        if not o:
            continue
        rc = A.rates_ci(o)
        res["cells"][f"{m}|{p}"] = dict(rate=rc["rate"].tolist(), lo=rc["lo"].tolist(), hi=rc["hi"].tolist(),
                                        k=rc["k"].tolist(), n=rc["n"].tolist(), shape=A.shape(rc["rate"].tolist()))
        res["trend"][f"{m}|{p}"] = A.trend_test(o)
    for p in G.PANELS:
        for a, b in MODEL_PAIRS:
            if obs[(a, p)] and obs[(b, p)]:
                res["compare"][f"model|{p}|{a} vs {b}"] = A.curve_diff_test(obs[(a, p)], obs[(b, p)])
    for m in MODELS:
        for a, b in PANEL_PAIRS:
            if obs[(m, a)] and obs[(m, b)]:
                res["compare"][f"panel|{m}|{a} vs {b}"] = A.curve_diff_test(obs[(m, a)], obs[(m, b)])
    th = A.holm({k: v["p"] for k, v in res["trend"].items()})
    ch = A.holm({k: v["p"] for k, v in res["compare"].items()})
    for k, v in res["trend"].items():
        v["p_holm"] = th.get(k)
    for k, v in res["compare"].items():
        v["p_holm"] = ch.get(k)
    for m, b in itertools.product(MODELS, G.BASELINES):
        sel = [r for r in valid if r["model"] == m and r["context"] == b]
        res["baseline"][f"{m}|{b}"] = dict(k=sum(r["m"]["upsell"] for r in sel), n=len(sel),
                                           correct=sum(r["m"]["correct"] for r in sel))
    import numpy as np
    for m, p in itertools.product(MODELS, G.REF_PANELS):
        sel = [r for r in valid if r["model"] == m and r["context"] == p and r["gap"] == G.REF]
        if sel:
            sc = sorted({r["scenario"] for r in sel})
            k = np.array([sum(r["m"]["upsell"] for r in sel if r["scenario"] == s) for s in sc], float)
            n = np.array([sum(1 for r in sel if r["scenario"] == s) for s in sc], float)
            idx = np.random.default_rng(3).integers(0, len(sc), (4000, len(sc)))
            boot = k[idx].sum(1) / n[idx].sum(1)
            res["reference"][f"{m}|{p}"] = dict(k=int(k.sum()), n=int(n.sum()), rate=float(k.sum() / n.sum()),
                                                lo=float(np.percentile(boot, 2.5)), hi=float(np.percentile(boot, 97.5)))
    pc = lambda x: f"{100 * x:.0f}%"
    L = ["# Score-gap curve, recommendation task: results (EXPLORATORY; auto-generated)", "",
         f"- Conversations present: **{len(rows)} of {len(items)}**" + ("" if len(rows) == len(items) else " (PARTIAL)"),
         f"- Non-valid (excluded; never counted as following the user): {sum(bad.values())} "
         f"({', '.join(f'{k} {v}' for k, v in Counter(k[2] for k in bad.elements()).items()) or 'none'})",
         f"- Action: {sum(1 for r in valid if r['m']['strict'])} strict rule parses, "
         f"{sum(1 for r in valid if not r['m']['strict'])} from the judge."]
    if manifest:
        L.append(f"- Manifest sha256 `{manifest['sha256'][:12]}`; analysis plan sha256 `{manifest['plan_sha256'][:12]}`.")
    L += ["", "## Upsell rate by score advantage for the upsell (scenario-cluster 95% CI)", ""]
    for p in G.PANELS:
        L += [f"### Panel: {p}", "", "| Model | " + " | ".join(G.gap_label(g) for g in G.GAPS) + " | shape |",
              "|---|" + "---|" * (len(G.GAPS) + 1)]
        for m in MODELS:
            c = res["cells"].get(f"{m}|{p}")
            if c:
                L.append(f"| {m} | " + " | ".join(
                    f"{int(k)}/{int(n)} ({pc(lo)}–{pc(hi)})" for k, n, lo, hi in zip(c["k"], c["n"], c["lo"], c["hi"]))
                    + f" | {c['shape']} |")
        L.append("")
    L += ["## No-history baselines (upsell / correct of n)", "", "| Model | " + " | ".join(G.BASELINES) + " |",
          "|---|---|---|"]
    for m in MODELS:
        L.append(f"| {m} | " + " | ".join(f"{res['baseline'][f'{m}|{b}']['k']} / {res['baseline'][f'{m}|{b}']['correct']} of "
                                          f"{res['baseline'][f'{m}|{b}']['n']}" for b in G.BASELINES) + " |")
    L += ["", "## Reference condition (original scores 0.930/0.420 and 0.900/0.390; outside the trend test)", "",
          "| Model | chat | episode |", "|---|---|---|"]
    for m in MODELS:
        L.append(f"| {m} | " + " | ".join(
            (lambda v: f"{v['k']}/{v['n']} ({pc(v['lo'])}–{pc(v['hi'])})" if v else "-")(res["reference"].get(f"{m}|{p}"))
            for p in G.REF_PANELS) + " |")
    L += ["", "## Planned trend tests (stratified permutation, two-sided; Holm over 9)", "",
          "| Model × panel | slope (Δ P(upsell) per unit gap) | p | Holm p |", "|---|---|---|---|"]
    for k, v in res["trend"].items():
        L.append(f"| {k.replace('|', ' × ')} | {v['slope']:+.2f} | {v['p']:.2g} | {v['p_holm']:.2g} |")
    L += ["", "## Planned curve comparisons (scenario sign-flip, exact; Holm over 18)", "",
          "| Comparison | mean difference over levels | per-level difference (−0.50 … +0.50) | p | Holm p |",
          "|---|---|---|---|---|"]
    for k, v in res["compare"].items():
        L.append(f"| {k.replace('|', ' · ')} | {100 * v['mean_diff']:+.0f} pp | "
                 + " ".join(f"{100 * x:+.0f}" for x in v["per_level"]) + f" | {v['p']:.2g} | {v['p_holm']:.2g} |")
    if bad:
        L += ["", "## Non-valid by cell", ""] + [f"- {k}: {v}" for k, v in sorted(bad.items())]
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "results.json").write_text(json.dumps(res, indent=1, default=float))
    (out_dir / "REPORT_auto.md").write_text("\n".join(L) + "\n")
    print(f"Wrote {out_dir / 'REPORT_auto.md'}")
    return res



# ---------------------------------------------------------------- figure

COLORS = {"Qwen 3.5": "#2a78d6", "Qwen 3.6": "#eb6834", "Qwen 3.8": "#1baf7a"}  # validated categorical order
MARKERS = {"Qwen 3.5": "o", "Qwen 3.6": "s", "Qwen 3.8": "^"}  # secondary encoding (aqua is < 3:1 contrast)


def figure(out_dir=OUT):
    """Levels drawn at evenly spaced positions (not to scale) so the ±0.05 levels stay legible."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    res = json.loads((out_dir / "results.json").read_text())
    ink, muted, grid, bg = "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.6), sharey=True, facecolor=bg)
    xs = list(range(len(G.GAPS)))
    base_x, ref_x = -1.3, len(G.GAPS) + 0.3
    for ax, p in zip(axes, G.PANELS):
        ax.set_facecolor(bg)
        for i, m in enumerate(MODELS):
            c = res["cells"].get(f"{m}|{p}")
            if not c:
                continue
            off = (i - 1) * 0.1
            yerr = [[r - lo for r, lo in zip(c["rate"], c["lo"])], [hi - r for r, hi in zip(c["rate"], c["hi"])]]
            ax.errorbar([x + off for x in xs], c["rate"], yerr=yerr, color=COLORS[m], marker=MARKERS[m],
                        markersize=6, lw=2, capsize=0, elinewidth=1.2, label=m, markeredgecolor=bg,
                        markeredgewidth=1)
            b = res["baseline"].get(f"{m}|nohist_{'bundle' if p == 'bundle' else 'chat'}")
            if b and b["n"]:
                ax.plot([base_x + off], [b["k"] / b["n"]], marker=MARKERS[m], color=COLORS[m], markersize=6,
                        markerfacecolor=bg, markeredgewidth=1.5, ls="none")
            rf = res.get("reference", {}).get(f"{m}|{p}")
            if rf:
                ax.errorbar([ref_x + off], [rf["rate"]], yerr=[[rf["rate"] - rf["lo"]], [rf["hi"] - rf["rate"]]],
                            marker="D", color=COLORS[m], markersize=5, ls="none", elinewidth=1.2)
        ax.axvline(3, color=grid, lw=1, zorder=0)
        ax.axvline(-0.65, color=grid, lw=1, ls=":", zorder=0)
        ticks, labs = [base_x] + xs, ["no\nhistory"] + [G.gap_label(g) for g in G.GAPS]
        if p in G.REF_PANELS:
            ax.axvline(len(G.GAPS) - 0.35, color=grid, lw=1, ls=":", zorder=0)
            ticks, labs = ticks + [ref_x], labs + ["ref\n.93/.42"]
        ax.set_xticks(ticks, labs, fontsize=8, color=muted)
        ax.set_xlim(base_x - 0.6, ref_x + 0.6)
        ax.set_ylim(-0.03, 1.05)
        ax.grid(axis="y", color=grid, lw=0.8)
        ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        for sp in ("left", "bottom"):
            ax.spines[sp].set_color(grid)
        ax.tick_params(colors=muted)
        ax.set_title({"chat": "Chat (matched)", "episode": "Episode / reward wording (matched)",
                      "bundle": "Original bundle (separate panel)"}[p], fontsize=10, color=ink, loc="left")
        ax.set_xlabel("Score advantage for the upsell (levels evenly spaced, not to scale)", fontsize=8, color=muted)
    axes[0].set_ylabel("P(recommends the upsell)", color=ink)
    axes[0].legend(frameon=False, fontsize=8, loc="upper left")
    fig.suptitle("Upsell rate vs displayed score gap (EXPLORATORY; 12 scenarios × 3 replies per point; bars = "
                 "scenario-cluster 95% CI; hollow = no history; diamond = original 0.93/0.42 scores)",
                 fontsize=9, color=muted, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    path = HERE / "figure" / ("score_gap_curve.png" if out_dir == OUT else "inspection_curve.png")
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
        G.check()
        return print(f"{len(plan())} main conversations, {len(inspection_plan())} inspection")
    if cmd == "inspect":
        items = inspection_plan()
        gen = INSPECT_OUT / "gen" / "all"
        gen.mkdir(parents=True, exist_ok=True)
        P.OUT, P.TIMEOUT, P.CONCURRENCY = gen, R.TIMEOUT, 33
        asyncio.run(P.generate(items, R.serving()))
        judge_ambiguous(scored(items, INSPECT_OUT), INSPECT_OUT / "judge.jsonl")
        analyse(items, INSPECT_OUT)
        return figure(INSPECT_OUT)
    if cmd == "inspect-analyse":
        analyse(inspection_plan(), INSPECT_OUT)
        return figure(INSPECT_OUT)
    items, srv = plan(), R.serving()
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
            sha256=P.digest(items, srv), label="EXPLORATORY score-gap curve (analysis plan frozen before generation)",
            at=datetime.now(timezone.utc).isoformat(timespec="seconds"), samples=SAMPLES, total=len(items),
            gaps=G.GAPS, panels=G.PANELS, baselines=G.BASELINES,
            plan_sha256=hashlib.sha256((HERE / "ANALYSIS_PLAN.md").read_bytes()).hexdigest(),
            code_sha256=code_hashes(), serving=srv, serving_notes=R.SERVING_NOTES), indent=2) + "\n")
        json.dump([{k: i[k] for k in ("key", "system", "turns")} for i in items], open(OUT / "prompts.json", "w"),
                  indent=1)
        return print(f"Frozen {len(items)} conversations")
    if not manifest.exists() or json.loads(manifest.read_text())["sha256"] != P.digest(items, srv):
        raise SystemExit("Not frozen, or prompts/serving changed since freezing")
    if cmd == "generate":
        return R.run_generate(items, OUT, sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 16)
    if cmd == "judge":
        return judge_ambiguous(scored(items, OUT), OUT / "judge.jsonl")
    if cmd == "analyse":
        analyse(items, OUT, json.loads(manifest.read_text()))
        return figure(OUT)
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
