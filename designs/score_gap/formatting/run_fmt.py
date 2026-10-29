"""EXPLORATORY score-gap response curves on three formatting features (see ANALYSIS_PLAN.md).

Run from the repo root:
  .venv/bin/python designs/score_gap/formatting/run_fmt.py check
  .venv/bin/python designs/score_gap/formatting/run_fmt.py inspect          # setup check only (inspection tasks)
  .venv/bin/python designs/score_gap/formatting/run_fmt.py freeze
  .venv/bin/python designs/score_gap/formatting/run_fmt.py generate "Qwen 3.5" 64   # one process per model
  .venv/bin/python designs/score_gap/formatting/run_fmt.py progress         # counts, non-valid, cost so far
  .venv/bin/python designs/score_gap/formatting/run_fmt.py analyse
Reuses designs/rl_context (run_pilot generation, run_confirm serving/record loading, the materials and scorers)
read-only; their hashes are recorded in the manifest.
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
RL = HERE.parents[1] / "rl_context"
sys.path[:0] = [str(HERE), str(RL), str(RL / "domains")]
import run_confirm as R  # noqa: E402
import run_pilot as P  # noqa: E402
from score import completion  # noqa: E402  (rl_context/score.py)
import fmt_materials as G  # noqa: E402
import fmt_analysis as A  # noqa: E402

OUT = HERE / "run"
INSPECT_OUT = HERE / "inspection"
SAMPLES = 4
MODELS = ("Qwen 3.5", "Qwen 3.8")
BUDGET_USD = 100.0
RETRY_PASSES = 2
# OpenRouter list prices (USD per token) for the pinned endpoints, read from
# https://openrouter.ai/api/v1/models/qwen/<model>/endpoints on 2026-10-28 before freezing.
PRICES = {"Qwen 3.5": (0.30e-6, 2.40e-6), "Qwen 3.8": (0.15e-6, 1.875e-6)}  # novita/bf16; deepinfra/bf16
CODE = ["fmt_materials.py", "fmt_analysis.py", "run_fmt.py", "simulate.py", "ANALYSIS_PLAN.md",
        "simulation/CALIBRATION.md"]
DEPS = [RL / f for f in ("confirm_materials.py", "confirm_score.py", "emdash_materials.py", "emdash_score.py",
                         "score.py", "run_domains.py", "run_pilot.py", "run_confirm.py", "domains/structure.py",
                         "pilot/src_snapshot/model_diffing/core.py",
                         "pilot/src_snapshot/model_diffing/petri_task.py")]
SUBS = ("title", "signoff")


def serving() -> dict:
    """The pinned 3-way serving with Qwen 3.6 removed (3.6 is excluded from this experiment)."""
    s = R.serving()
    s["targets"] = [t for t in s["targets"] if t["label"] in MODELS]
    assert [t["label"] for t in s["targets"]] == list(MODELS)
    return s


def plan(tag="fmt", samples=SAMPLES, inspection=False, gaps=G.GAPS):
    out = []
    for feature in G.FEATURES:
        tasks = [G.INSPECTION[feature]] if inspection else G.TASKS[feature]
        for task, sub in itertools.product(tasks, G.SUBFEATURES[feature]):
            for fmt, g in G.conditions():
                if g is not None and g != G.REF and g not in gaps:
                    continue
                prompt = G.render(feature, sub, task, fmt, g)
                lab = "none" if g is None else (G.REF if g == G.REF else G.gap_label(g))
                for m, r in itertools.product(MODELS, range(samples)):
                    out.append(dict(key=f"{tag}|{feature}|{sub}|{task['id']}|{fmt}|{lab}|{m}|{r}", set=tag,
                                    feature=feature, sub=sub, scenario=task["id"], context=fmt, scores=lab,
                                    user="hedged", model=m, rep=r, gap=g, facts=task["facts"], **prompt))
    return out


def inspection_plan():
    return plan("inspect", 1, True, gaps=(-0.5, 0.0, 0.5))


def task_of(feature, tid):
    return next(t for t in G.TASKS[feature] + [G.INSPECTION[feature]] if t["id"] == tid)


# ---------------------------------------------------------------- generation

def _patch_connections(n: int):
    """Allow up to n concurrent requests per model in Inspect (static limit; Inspect still backs off and retries
    on 429s). Runtime only: not part of the serving dict or the frozen digest."""
    import model_diffing.petri_task as PT
    base = PT.generation_config

    def cfg(settings, target):
        return base(settings, target).merge(PT.GenerateConfig(max_connections=n))
    PT.generation_config = cfg


def records(out_dir):
    rows = {}
    for path in sorted((out_dir / "gen").glob("*/generations.jsonl")):
        for line in path.read_text().splitlines():
            if line.strip():
                g = json.loads(line)
                rows.setdefault(g["key"], []).append(g)
    return rows


def cost(out_dir=OUT) -> dict:
    """USD from the token usage OpenRouter returned, over every attempt (retries included)."""
    tot, n_unknown = Counter(), 0
    for recs in records(out_dir).values():
        for g in recs:
            u = (g.get("private") or [{}])[0]
            i, o = u.get("input_tokens"), u.get("output_tokens")
            if i is None or o is None:
                n_unknown += 1
                continue
            pi, po = PRICES[g["model"]]
            tot[g["model"]] += i * pi + o * po
    return dict(by_model=dict(tot), total=sum(tot.values()), attempts_without_usage=n_unknown)


def run_generate(items, out_dir, model, concurrency):
    """One model's items -> out_dir/gen/<model>/generations.jsonl. Initial pass plus up to RETRY_PASSES passes
    over errors. Truncated (token limit) replies are final. Stops before a pass if the budget is reached."""
    gen = out_dir / "gen" / model.replace(" ", "_")
    gen.mkdir(parents=True, exist_ok=True)
    P.OUT, P.TIMEOUT, P.CONCURRENCY = gen, R.TIMEOUT, concurrency
    _patch_connections(concurrency)
    mine = [i for i in items if i["model"] == model]
    for p in range(1 + RETRY_PASSES):
        c = cost(out_dir)
        if c["total"] >= BUDGET_USD:
            print(f"BUDGET reached (${c['total']:.2f}); stopping", flush=True)
            return
        latest = {k: v[-1] for k, v in records(out_dir).items()}
        todo = [i for i in mine if i["key"] not in latest or latest[i["key"]]["status"] == "error"]
        print(f"pass {p}: {len(todo)} to do; cost so far ${c['total']:.2f}", flush=True)
        if not todo:
            return
        asyncio.run(P.generate(mine, serving()))


# ---------------------------------------------------------------- scoring

def scored(items, out_dir):
    """One row per planned item. completion: valid | empty | truncated | failed | abandoned (no record).
    Only valid rows carry y (adopted) and violates."""
    latest = {k: v[-1] for k, v in records(out_dir).items()}
    rows = []
    for i in items:
        r = {k: v for k, v in i.items() if k not in ("system", "turns")}
        g = latest.get(i["key"])
        if g is None:
            r |= dict(completion="abandoned", status="missing", reply="")
        else:
            r |= dict(status=g["status"], reply=g["reply"], completion=completion(g["reply"], g["status"]))
        if r["completion"] == "valid":
            r |= G.measures(i["feature"], i["sub"], task_of(i["feature"], i["scenario"]), r["reply"])
        rows.append(r)
    return rows


# ---------------------------------------------------------------- analysis

def groups():
    """Analysis groups: (name, row filter, planned?)."""
    g = [(f, (lambda f: lambda r: r["feature"] == f)(f), True) for f in G.FEATURES]
    g += [(s, (lambda s: lambda r: r["sub"] == s)(s), False) for s in SUBS]
    g += [("pooled", lambda r: True, False)]
    return g


def obs_of(rows, outcome="adopted"):
    return [dict(stratum=f"{r['feature']}|{r['sub']}|{r['scenario']}", cluster=f"{r['feature']}|{r['scenario']}",
                 gap=r["gap"], y=int(r[outcome])) for r in rows]


def cluster_ci(rows, outcome="adopted", reps=4000, seed=3):
    import numpy as np
    cl = sorted({(r["feature"], r["scenario"]) for r in rows})
    if not cl:
        return None
    k = np.array([sum(r[outcome] for r in rows if (r["feature"], r["scenario"]) == c) for c in cl], float)
    n = np.array([sum(1 for r in rows if (r["feature"], r["scenario"]) == c) for c in cl], float)
    idx = np.random.default_rng(seed).integers(0, len(cl), (reps, len(cl)))
    b = k[idx].sum(1) / np.maximum(n[idx].sum(1), 1)
    return dict(k=int(k.sum()), n=int(n.sum()), rate=float(k.sum() / max(n.sum(), 1)),
                lo=float(np.percentile(b, 2.5)), hi=float(np.percentile(b, 97.5)))


def analyse(items, out_dir=OUT, manifest=None):
    rows = scored(items, out_dir)
    valid = [r for r in rows if r["completion"] == "valid"]
    curve = [r for r in valid if r["gap"] not in (None, G.REF)]
    res = {"cells": {}, "violates": {}, "trend": {}, "compare": {}, "baseline": {}, "reference": {},
           "nonvalid": {}, "planned_trend": [], "planned_compare": []}
    for (name, sel, planned), m, p in itertools.product(groups(), MODELS, G.PANELS):
        sub = [r for r in curve if sel(r) and r["model"] == m and r["context"] == p]
        if not sub:
            continue
        key = f"{name}|{m}|{p}"
        rc = A.rates_ci(obs_of(sub))
        res["cells"][key] = dict(rate=rc["rate"].tolist(), lo=rc["lo"].tolist(), hi=rc["hi"].tolist(),
                                 k=rc["k"].tolist(), n=rc["n"].tolist(), shape=A.shape(rc["rate"].tolist()))
        rv = A.rates_ci(obs_of(sub, "violates"))
        res["violates"][key] = dict(rate=rv["rate"].tolist(), k=rv["k"].tolist(), n=rv["n"].tolist())
        res["trend"][key] = A.trend_test(obs_of(sub)) | dict(planned=planned)
        if planned:
            res["planned_trend"].append(key)
    for (name, sel, planned), p in itertools.product(groups(), G.PANELS):
        a = [r for r in curve if sel(r) and r["model"] == "Qwen 3.8" and r["context"] == p]
        b = [r for r in curve if sel(r) and r["model"] == "Qwen 3.5" and r["context"] == p]
        if a and b:
            key = f"{name}|{p}|Qwen 3.8 vs Qwen 3.5"
            res["compare"][key] = A.compare_test(obs_of(a), obs_of(b)) | dict(planned=planned)
            if planned:
                res["planned_compare"].append(key)
    th = A.holm({k: res["trend"][k]["p"] for k in res["planned_trend"]})
    ch = A.holm({k: res["compare"][k]["p"] for k in res["planned_compare"]})
    for k, v in res["trend"].items():
        v["p_holm"] = th.get(k)
    for k, v in res["compare"].items():
        v["p_holm"] = ch.get(k)
    for (name, sel, _), m in itertools.product(groups(), MODELS):
        for bl in G.BASELINES:
            s = [r for r in valid if sel(r) and r["model"] == m and r["context"] == bl]
            res["baseline"][f"{name}|{m}|{bl}"] = dict(k=sum(r["adopted"] for r in s), n=len(s),
                                                       violates=sum(r["violates"] for r in s))
        for p in G.PANELS:
            s = [r for r in valid if sel(r) and r["model"] == m and r["context"] == p and r["gap"] == G.REF]
            res["reference"][f"{name}|{m}|{p}"] = cluster_ci(s)
    bad = Counter((r["model"], r["feature"], r["context"], r["completion"]) for r in rows if r["completion"] != "valid")
    res["nonvalid"] = {"|".join(k): v for k, v in bad.items()}
    res["n_rows"], res["n_items"], res["n_valid"] = sum(r["status"] != "missing" for r in rows), len(items), len(valid)
    res["facts_ok"] = {m: [sum(r["facts_ok"] for r in valid if r["model"] == m),
                           sum(1 for r in valid if r["model"] == m)] for m in MODELS}
    res["cost"] = cost(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "results.json").write_text(json.dumps(res, indent=1, default=float))
    (out_dir / "REPORT_auto.md").write_text(report(res, rows, manifest))
    print(f"Wrote {out_dir / 'REPORT_auto.md'}")
    return res


NAMES = {"titles_signoffs": "Feature 1: titles and sign-offs (pooled)", "emdash": "Feature 2: em dashes",
         "bullets": "Feature 3: bullets vs paragraph", "title": "Feature 1a: titles only (secondary)",
         "signoff": "Feature 1b: sign-offs only (secondary)", "pooled": "All features pooled (secondary)"}


def report(res, rows, manifest):
    pc = lambda x: f"{100 * x:.0f}%"
    nv = Counter(r["completion"] for r in rows if r["completion"] != "valid")
    L = ["# Score-gap curves, formatting features: results (EXPLORATORY; auto-generated)", "",
         f"- Conversations with a record: **{res['n_rows']} of {res['n_items']}**"
         + ("" if res["n_rows"] == res["n_items"] else " (PARTIAL)"),
         f"- Valid: {res['n_valid']}. Non-valid (excluded; never counted as following the user): {sum(nv.values())} "
         f"({', '.join(f'{k} {v}' for k, v in nv.items()) or 'none'}; "
         f"{100 * sum(nv.values()) / max(len(rows), 1):.1f}% of planned).",
         f"- Outcome: rate of the user-conflicting behaviour in its scorer form (bracketed title / fixed sign-off / "
         f"any em dash / ≥2 bullet lines), the same at every level.",
         f"- Cost (token usage × OpenRouter list price, all attempts): ${res['cost']['total']:.2f} "
         f"({', '.join(f'{m} ${v:.2f}' for m, v in res['cost']['by_model'].items())})."]
    if manifest:
        L.append(f"- Manifest sha256 `{manifest['sha256'][:12]}`; analysis plan sha256 `{manifest['plan_sha256'][:12]}`.")
    hdr = "| Model | no history | " + " | ".join(G.gap_label(g) for g in G.GAPS) + " | ref .93/.42 | shape |"
    for name, _, planned in groups():
        L += ["", f"## {NAMES[name]}", ""]
        for p in G.PANELS:
            L += [f"**Panel: {p}** — k/n (cluster-bootstrap 95% CI)", "", hdr, "|---|" + "---|" * (len(G.GAPS) + 3)]
            for m in MODELS:
                c = res["cells"].get(f"{name}|{m}|{p}")
                if not c:
                    continue
                b = res["baseline"][f"{name}|{m}|nohist_{p}"]
                rf = res["reference"].get(f"{name}|{m}|{p}")
                L.append(f"| {m} | {b['k']}/{b['n']} | " + " | ".join(
                    f"{int(k)}/{int(n)} ({pc(lo)}–{pc(hi)})" for k, n, lo, hi in zip(c["k"], c["n"], c["lo"], c["hi"]))
                    + (f" | {rf['k']}/{rf['n']} ({pc(rf['lo'])}–{pc(rf['hi'])})" if rf else " | -")
                    + f" | {c['shape']} |")
            L.append("")
    L += ["## Planned trend tests (within-stratum permutation, two-sided; Holm over the 12 planned)", "",
          "| Feature × model × panel | slope (Δ P per unit gap) | p | Holm p |", "|---|---|---|---|"]
    for k in res["planned_trend"]:
        v = res["trend"][k]
        L.append(f"| {k.replace('|', ' × ')} | {v['slope']:+.2f} | {v['p']:.2g} | {v['p_holm']:.2g} |")
    L += ["", "## Planned curve comparisons, Qwen 3.8 vs Qwen 3.5 (within-task permutation; Holm over the 6 planned)",
          "", "| Feature · panel | mean diff over levels | per level (−0.50 … +0.50), pp | p | Holm p | "
          "task sign-flip p (floor) |", "|---|---|---|---|---|---|"]
    for k in res["planned_compare"]:
        v = res["compare"][k]
        L.append(f"| {k.replace('|', ' · ')} | {100 * v['mean_diff']:+.0f} pp | "
                 + " ".join(f"{100 * x:+.0f}" for x in v["per_level"])
                 + f" | {v['p']:.2g} | {v['p_holm']:.2g} | {v['p_signflip']:.2g} ({v['signflip_floor']:.2g}) |")
    L += ["", "## Secondary tests (sub-features and pooled; unadjusted)", "",
          "| Test | estimate | p | task sign-flip p |", "|---|---|---|---|"]
    for k, v in res["trend"].items():
        if not v["planned"]:
            L.append(f"| trend · {k.replace('|', ' × ')} | slope {v['slope']:+.2f} | {v['p']:.2g} | |")
    for k, v in res["compare"].items():
        if not v["planned"]:
            L.append(f"| compare · {k.replace('|', ' · ')} | {100 * v['mean_diff']:+.0f} pp | {v['p']:.2g} | "
                     f"{v['p_signflip']:.2g} |")
    L += ["", "## Secondary outcome: any version of what the user asked to leave out (violates), k/n", "",
          "| Group × model × panel | " + " | ".join(G.gap_label(g) for g in G.GAPS) + " |", "|---|" + "---|" * len(G.GAPS)]
    for k, v in res["violates"].items():
        L.append(f"| {k.replace('|', ' × ')} | " + " | ".join(f"{int(a)}/{int(b)}" for a, b in zip(v["k"], v["n"])) + " |")
    L += ["", "## Non-valid by model × feature × panel", ""]
    L += [f"- {k.replace('|', ' · ')}: {v}" for k, v in sorted(res["nonvalid"].items())] or ["- none"]
    L += ["", f"Facts included (valid replies): " + "; ".join(f"{m} {a}/{b}" for m, (a, b) in res["facts_ok"].items())]
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- figure

COLORS = {"Qwen 3.5": "#2a78d6", "Qwen 3.8": "#1baf7a"}  # palette from the recommendation figure
MARKERS = {"Qwen 3.5": "o", "Qwen 3.8": "^"}


def figure(out_dir=OUT, names=G.FEATURES, fname="score_gap_curves.png", title_extra=""):
    """Levels at evenly spaced positions (not to scale) so the ±0.05 levels stay legible."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    res = json.loads((out_dir / "results.json").read_text())
    ink, muted, grid, bg = "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"
    fig, axes = plt.subplots(len(names), 2, figsize=(11, 3.4 * len(names)), sharey=True, facecolor=bg,
                             squeeze=False)
    xs = list(range(len(G.GAPS)))
    base_x, ref_x = -1.3, len(G.GAPS) + 0.3
    for row, name in enumerate(names):
        for col, p in enumerate(G.PANELS):
            ax = axes[row][col]
            ax.set_facecolor(bg)
            for i, m in enumerate(MODELS):
                c = res["cells"].get(f"{name}|{m}|{p}")
                if not c:
                    continue
                off = (i - 0.5) * 0.14
                yerr = [[max(r - lo, 0) for r, lo in zip(c["rate"], c["lo"])],
                        [max(hi - r, 0) for r, hi in zip(c["rate"], c["hi"])]]
                ax.errorbar([x + off for x in xs], c["rate"], yerr=yerr, color=COLORS[m], marker=MARKERS[m],
                            markersize=6, lw=2, capsize=0, elinewidth=1.2, label=m, markeredgecolor=bg,
                            markeredgewidth=1)
                b = res["baseline"].get(f"{name}|{m}|nohist_{p}")
                if b and b["n"]:
                    ax.plot([base_x + off], [b["k"] / b["n"]], marker=MARKERS[m], color=COLORS[m], markersize=6,
                            markerfacecolor=bg, markeredgewidth=1.5, ls="none")
                rf = res["reference"].get(f"{name}|{m}|{p}")
                if rf:
                    ax.errorbar([ref_x + off], [rf["rate"]], yerr=[[max(rf["rate"] - rf["lo"], 0)],
                                                                   [max(rf["hi"] - rf["rate"], 0)]],
                                marker="D", color=COLORS[m], markersize=5, ls="none", elinewidth=1.2)
            ax.axvline(3, color=grid, lw=1, zorder=0)
            for v in (-0.65, len(G.GAPS) - 0.35):
                ax.axvline(v, color=grid, lw=1, ls=":", zorder=0)
            ax.set_xticks([base_x] + xs + [ref_x], ["no\nhistory"] + [G.gap_label(g) for g in G.GAPS]
                          + ["ref\n.93/.42"], fontsize=8, color=muted)
            ax.set_xlim(base_x - 0.6, ref_x + 0.6)
            ax.set_ylim(-0.03, 1.05)
            ax.grid(axis="y", color=grid, lw=0.8)
            ax.set_axisbelow(True)
            for sp in ("top", "right"):
                ax.spines[sp].set_visible(False)
            for sp in ("left", "bottom"):
                ax.spines[sp].set_color(grid)
            ax.tick_params(colors=muted)
            ax.set_title(f"{NAMES[name]} · {'bundle (main)' if p == 'bundle' else 'ordinary/direct (control)'}",
                         fontsize=9.5, color=ink, loc="left")
            if row == len(names) - 1:
                ax.set_xlabel("Score advantage for the user-conflicting feature (levels evenly spaced, not to scale)",
                              fontsize=8, color=muted)
            if col == 0:
                ax.set_ylabel("P(adopts the feature)", color=ink)
    axes[0][0].legend(frameon=False, fontsize=8, loc="upper left")
    fig.suptitle("Rate of the user-conflicting feature vs displayed score gap (EXPLORATORY; bars = task-cluster "
                 f"95% CI; hollow = no history; diamond = original 0.93/0.42 scores){title_extra}",
                 fontsize=9, color=muted, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    path = HERE / "figure" / fname
    path.parent.mkdir(exist_ok=True)
    fig.savefig(path, dpi=150, facecolor=fig.get_facecolor())
    print(f"Wrote {path}")


# ---------------------------------------------------------------- main

def code_hashes():
    h = {f: hashlib.sha256((HERE / f).read_bytes()).hexdigest() for f in CODE}
    h |= {str(p.relative_to(RL)): hashlib.sha256(p.read_bytes()).hexdigest() for p in DEPS}
    return h


def progress(out_dir=OUT, items=None):
    items = items or plan()
    rows = scored(items, out_dir)
    c = Counter((r["model"], r["completion"]) for r in rows)
    print(json.dumps({f"{m}|{k}": v for (m, k), v in sorted(c.items())}, indent=1))
    print(json.dumps(cost(out_dir), indent=1))


def preview(items, path):
    L = ["# Prompt preview (inspection tasks; +0.50, 0, no history and reference shown for one sub-feature each)", ""]
    seen = set()
    for i in items:
        k = (i["sub"], i["context"], i["scores"])
        if i["model"] != MODELS[0] or k in seen or i["scores"] not in ("+0.50", "+0.00", "none", "ref"):
            continue
        seen.add(k)
        L += [f"## {i['feature']} / {i['sub']} | {i['context']} | gap {i['scores']}", "", "SYSTEM:", "```text",
              i["system"], "```", "USER:", "```text", i["turns"][0], "```", ""]
    path.write_text("\n".join(L))


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "check":
        G.check()
        return print(f"{len(plan())} main conversations, {len(inspection_plan())} inspection")
    if cmd == "inspect":
        items = inspection_plan()
        INSPECT_OUT.mkdir(exist_ok=True)
        preview(items, INSPECT_OUT / "prompts_preview.md")
        for m in MODELS:
            run_generate(items, INSPECT_OUT, m, 64)
        analyse(items, INSPECT_OUT)
        return progress(INSPECT_OUT, items)
    if cmd == "inspect-analyse":
        return analyse(inspection_plan(), INSPECT_OUT)
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
            sha256=P.digest(items, srv), label="EXPLORATORY score-gap curves, formatting features (analysis plan "
                                               "frozen before generation)",
            at=datetime.now(timezone.utc).isoformat(timespec="seconds"), samples=SAMPLES, total=len(items),
            counts=dict(Counter(i["feature"] for i in items)), gaps=G.GAPS, panels=G.PANELS, baselines=G.BASELINES,
            reference_scores=G.REF_SCORES, models=MODELS, budget_usd=BUDGET_USD, prices_usd_per_token=PRICES,
            runtime=dict(concurrency_per_model=64, inspect_max_connections=64, retry_passes=RETRY_PASSES,
                         per_call_timeout_s=R.TIMEOUT, interleaving="all conditions shuffled (run_pilot.generate)"),
            plan_sha256=hashlib.sha256((HERE / "ANALYSIS_PLAN.md").read_bytes()).hexdigest(),
            code_sha256=code_hashes(), serving=srv, serving_notes={m: R.SERVING_NOTES[m] for m in MODELS}),
            indent=2) + "\n")
        json.dump([{k: i[k] for k in ("key", "system", "turns")} for i in items], open(OUT / "prompts.json", "w"),
                  indent=1)
        return print(f"Frozen {len(items)} conversations")
    if not manifest.exists() or json.loads(manifest.read_text())["sha256"] != P.digest(items, srv):
        raise SystemExit("Not frozen, or prompts/serving changed since freezing")
    if cmd == "generate":
        return run_generate(items, OUT, sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 64)
    if cmd == "progress":
        return progress()
    if cmd == "analyse":
        analyse(items, OUT, json.loads(manifest.read_text()))
        figure(OUT)
        return figure(OUT, SUBS, "score_gap_titles_vs_signoffs.png", " — sub-features, secondary")
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
