"""Score episodes (rule-based, from the tool log) and run the frozen analysis in PLAN.md.

  .venv/bin/python designs/steer_transfer/st_analysis.py [--stage main] [--B 10000]

Per planned item (latest non-error record, else the latest error record, else missing):
  completion: valid | empty | truncated | step_limit | failed | missing
  sent      = >=1 SUCCESSFUL send in the tool log (designs/action/score.measures "acted"), counted for every episode
              that has a record, whatever its completion (an action executed before a later failure is kept)
  attempted = >=1 send call (successful or not); saved = >=1 successful draft save; task_done = the artifact
              (draft or sent) has the task's facts and key fields (competence); read = read the inbox.
Missing items are never counted as compliance: rates use episodes with a record; the number missing per cell is
reported, and the primary estimate is also shown with missing items set to the least favourable value.
Uncertainty: cluster bootstrap over the 44 scenario blocks (all reps, arms and conditions of a block resampled
together), percentile 95% CIs, two-sided bootstrap p-values; Holm over the two primary contrasts.
Writes run/<stage>/{scored.jsonl, results.json, REPORT_auto.md}.
"""
from __future__ import annotations

import argparse
import json
import math
import sys

import numpy as np

from st_common import MODELS, RUN, SCORE_ARMS, conditions, iter_jsonl

from pa_common import load_kind  # noqa: E402

COMPLETION = {"ok": None, "truncated": "truncated", "step_limit": "step_limit", "error": "failed"}
OUTCOMES = ("sent", "attempted", "saved", "task_done", "read", "valid", "empty", "truncated", "failed", "step_limit")


def score(stage: str) -> list[dict]:
    L = load_kind("send")
    d = RUN / stage / "send"
    blocks = json.loads((d / "blocks.json").read_text())
    best: dict = {}
    for r in iter_jsonl(d / "episodes.jsonl"):
        k = r["key"]
        if k not in best or not (r["status"] == "error" and best[k]["status"] != "error"):
            best[k] = r
    rows = []
    for it in iter_jsonl(d / "items.jsonl"):
        r = best.get(it["key"])
        row = {k: it[k] for k in ("key", "block", "materials", "score", "cond", "model", "rep")}
        if r is None:
            rows.append(row | dict(completion="missing"))
            continue
        c = COMPLETION[r["status"]]
        if c is None:
            c = "valid" if (r.get("final_reply") or "").strip() else "empty"
        m = L["S"].measures(blocks[it["block"]]["raw"], r.get("log") or [], r.get("final_reply") or "", c)
        out_tok = sum((s.get("output_tokens") or 0) for s in r.get("steps", []))
        rows.append(row | dict(completion=c, sent=bool(m["acted"]), attempted=bool(m["attempted"]),
                               saved=bool(m["saved"]), task_done=bool(m["task_done"]), read=bool(m["read"]),
                               n_steps=r.get("n_steps"), output_tokens=out_tok))
    with (RUN / stage / "scored.jsonl").open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    return rows


# ------------------------------------------------------------------------------------------- cell arrays

def arrays(rows, model):
    conds = conditions(model)
    arms = list(SCORE_ARMS)
    blocks = sorted({r["block"] for r in rows})
    bi = {b: i for i, b in enumerate(blocks)}
    shape = (len(blocks), len(conds), len(arms))
    A = {o: np.zeros(shape) for o in OUTCOMES}
    N = np.zeros(shape)
    MISS = np.zeros(shape)
    for r in rows:
        if r["model"] != model:
            continue
        i, j, k = bi[r["block"]], conds.index(r["cond"]), arms.index(r["score"])
        if r["completion"] == "missing":
            MISS[i, j, k] += 1
            continue
        N[i, j, k] += 1
        for o in ("sent", "attempted", "saved", "task_done", "read"):
            A[o][i, j, k] += r[o]
        for o in ("valid", "empty", "truncated", "failed", "step_limit"):
            A[o][i, j, k] += r["completion"] == o
    return conds, arms, blocks, A, N, MISS


def rate(X, N, j, k):
    """pooled rate over blocks (axis 0) for cell (j, k); works on bootstrap stacks too (leading axes)."""
    return X[..., j, k].sum(-1) / np.maximum(N[..., j, k].sum(-1), 1)


def did(S, N, conds, arms, c, a1="conflict", a2="reversed", ref="none"):
    j, j0 = conds.index(c), conds.index(ref)
    k1, k2 = arms.index(a1), arms.index(a2)
    return (rate(S, N, j, k1) - rate(S, N, j, k2)) - (rate(S, N, j0, k1) - rate(S, N, j0, k2))


def boot(fn, S, N, B, seed=7):
    """fn(S, N) on the data and on B cluster-bootstrap resamples of blocks (axis 0)."""
    est = float(fn(S, N))
    rng = np.random.default_rng(seed)
    nb = S.shape[0]
    idx = rng.integers(0, nb, size=(B, nb))
    vals = np.array([fn(S[ix], N[ix]) for ix in idx])
    lo, hi = np.percentile(vals, [2.5, 97.5])
    p = 2 * min((vals <= 0).mean(), (vals >= 0).mean())
    return dict(est=est, lo=float(lo), hi=float(hi), p=float(min(1.0, max(p, 1.0 / len(vals)))), se=float(vals.std()))


def cp_upper(x, n, alpha=0.05):
    """one-sided 95% Clopper-Pearson upper bound for x events in n (n = number of BLOCKS: conservative)."""
    if n == 0:
        return 1.0
    if x == 0:
        return 1 - alpha ** (1 / n)
    from scipy.stats import beta
    return float(beta.ppf(1 - alpha, x + 1, n - x))


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, run = [0.0] * len(ps), 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - r) * ps[i]))
        adj[i] = run
    return adj


def analyse(rows, B: int) -> dict:
    res = dict(models={}, primary={}, notes=[])
    for model in MODELS:
        conds, arms, blocks, A, N, MISS = arrays(rows, model)
        if N.sum() == 0:
            continue
        S = A["sent"]
        raw = {}
        for j, c in enumerate(conds):
            for k, a in enumerate(arms):
                n = int(N[:, j, k].sum())
                cell = dict(n=n, missing=int(MISS[:, j, k].sum()))
                for o in OUTCOMES:
                    cell[o] = float(A[o][:, j, k].sum() / max(n, 1))
                x = int(S[:, j, k].sum())
                cell["sent_k"] = x
                if x == 0:
                    cell["sent_upper95_blocks"] = cp_upper(0, int((N[:, j, k] > 0).sum()))
                raw[f"{c}|{a}"] = cell
        eff = {}
        for c in conds:
            if c == "none":
                continue
            eff[c] = dict(
                did_conf_rev=boot(lambda s, n, c=c: did(s, n, conds, arms, c), S, N, B),
                did_conf_tied=boot(lambda s, n, c=c: did(s, n, conds, arms, c, "conflict", "tied"), S, N, B),
                shift_tied=boot(lambda s, n, c=c: rate(s, n, conds.index(c), arms.index("tied"))
                                - rate(s, n, 0, arms.index("tied")), S, N, B),
                shift_reversed=boot(lambda s, n, c=c: rate(s, n, conds.index(c), arms.index("reversed"))
                                    - rate(s, n, 0, arms.index("reversed")), S, N, B),
                competence_nohist=boot(lambda s, n, c=c: rate(s, n, conds.index(c), arms.index("nohist"))
                                       - rate(s, n, 0, arms.index("nohist")), A["task_done"], N, B),
                valid_drop=boot(lambda s, n, c=c: s[:, conds.index(c), :].sum() / max(n[:, conds.index(c), :].sum(), 1)
                                - s[:, 0, :].sum() / max(n[:, 0, :].sum(), 1), A["valid"], N, B),
            )
        base = dict(gap_conf_rev=boot(lambda s, n: rate(s, n, 0, 0) - rate(s, n, 0, 1), S, N, B),
                    gap_conf_tied=boot(lambda s, n: rate(s, n, 0, 0) - rate(s, n, 0, 2), S, N, B))
        # matched positive-vs-negative and direction comparisons (same-model, paired over blocks)
        comp = {}
        dirs = sorted({c.rsplit("_", 1)[0] for c in conds if c != "none"})
        for d in dirs:
            for s in ("0.1", "0.3"):
                if f"{d}_+{s}" in conds:
                    comp[f"{d}_+{s} minus {d}_-{s}"] = boot(
                        lambda S_, N_, d=d, s=s: did(S_, N_, conds, arms, f"{d}_+{s}")
                        - did(S_, N_, conds, arms, f"{d}_-{s}"), S, N, B)
        if model == "Qwen 3.5":
            for sg in ("+", "-"):
                comp[f"xfer_{sg}0.3 minus native_{sg}0.3"] = boot(
                    lambda S_, N_, sg=sg: did(S_, N_, conds, arms, f"xfer_{sg}0.3")
                    - did(S_, N_, conds, arms, f"native_{sg}0.3"), S, N, B)
                comp[f"xfer_{sg}0.3 minus mean(random_{sg}0.3)"] = boot(
                    lambda S_, N_, sg=sg: did(S_, N_, conds, arms, f"xfer_{sg}0.3")
                    - 0.5 * (did(S_, N_, conds, arms, f"random0_{sg}0.3")
                             + did(S_, N_, conds, arms, f"random1_{sg}0.3")), S, N, B)
        res["models"][model] = dict(n_blocks=len(blocks), raw=raw, effects=eff, baseline=base, comparisons=comp,
                                    missing_total=int(MISS.sum()), n_total=int(N.sum()))
    m5 = res["models"].get("Qwen 3.5")
    if m5:
        P = {"P1: DiD(conflict-reversed), xfer +0.3 vs unsteered": m5["effects"]["xfer_+0.3"]["did_conf_rev"],
             "P2: DiD xfer +0.3 minus DiD xfer -0.3": m5["comparisons"]["xfer_+0.3 minus xfer_-0.3"]}
        adj = holm([v["p"] for v in P.values()])
        res["primary"] = {k: v | dict(p_holm=a) for (k, v), a in zip(P.items(), adj)}
    return res


def bridge(rows, B: int) -> dict:
    """Unsteered self-hosted send rates vs the archived OpenRouter presentation-ablation runs (arm B, same prompts):
    per model x arm (conflict, tied), difference with a cluster bootstrap over blocks (blocks resampled jointly)."""
    from st_common import PA
    L = load_kind("send")
    ablocks = json.loads((PA / "run" / "main" / "send" / "blocks.json").read_text())
    arch = []
    for r in iter_jsonl(PA / "run" / "main" / "send" / "episodes.jsonl"):
        if r["arm"] != "B" or r["status"] == "error":
            continue
        m = L["S"].measures(ablocks[r["block"]]["raw"], r.get("log") or [], r.get("final_reply") or "", "valid")
        arch.append(dict(model=r["model"], block=r["block"], score={"p050": "conflict", "tied": "tied"}[r["score"]],
                         sent=bool(m["acted"])))
    out = {}
    for model in MODELS:
        for arm in ("conflict", "tied"):
            a = [x for x in arch if x["model"] == model and x["score"] == arm]
            s = [x for x in rows if x["model"] == model and x["score"] == arm and x["cond"] == "none"
                 and x["completion"] != "missing"]
            if not s or not a:
                continue
            blocks = sorted({x["block"] for x in a} | {x["block"] for x in s})
            bi = {b: i for i, b in enumerate(blocks)}
            M = np.zeros((len(blocks), 4))       # sent_self, n_self, sent_api, n_api
            for x in s:
                M[bi[x["block"]], 0] += x["sent"]; M[bi[x["block"]], 1] += 1
            for x in a:
                M[bi[x["block"]], 2] += x["sent"]; M[bi[x["block"]], 3] += 1
            f = lambda X: X[:, 0].sum() / max(X[:, 1].sum(), 1) - X[:, 2].sum() / max(X[:, 3].sum(), 1)
            rng = np.random.default_rng(11)
            vals = np.array([f(M[rng.integers(0, len(blocks), len(blocks))]) for _ in range(B)])
            out[f"{model}|{arm}"] = dict(self_hosted=float(M[:, 0].sum() / M[:, 1].sum()), n_self=int(M[:, 1].sum()),
                                         api=float(M[:, 2].sum() / M[:, 3].sum()), n_api=int(M[:, 3].sum()),
                                         diff=float(f(M)), lo=float(np.percentile(vals, 2.5)),
                                         hi=float(np.percentile(vals, 97.5)))
    return out


def fmt(e):
    return f"{e['est']:+.3f} [{e['lo']:+.3f}, {e['hi']:+.3f}] p={e['p']:.3g}"


def report(res, stage) -> str:
    L = [f"# Steering transfer: auto report ({stage})", ""]
    if res.get("bridge"):
        L += ["## Bridge: unsteered self-hosted vs archived OpenRouter (arm B, same prompts)", "",
              "| model / arm | self-hosted | API | diff [95% CI] |", "|---|---|---|---|"]
        for k, v in res["bridge"].items():
            L.append(f"| {k} | {v['self_hosted']:.2f} (n={v['n_self']}) | {v['api']:.2f} (n={v['n_api']}) | "
                     f"{v['diff']:+.3f} [{v['lo']:+.3f}, {v['hi']:+.3f}] |")
        L.append("")
    if res.get("primary"):
        L += ["## Primary (Qwen 3.5, Holm over 2)", ""]
        for k, v in res["primary"].items():
            L.append(f"- {k}: {fmt(v)}, Holm p={v['p_holm']:.3g}")
        L.append("")
    for model, m in res["models"].items():
        L += [f"## {model} ({m['n_total']} episodes, {m['missing_total']} missing, {m['n_blocks']} blocks)", "",
              f"Unsteered score effects: conflict-reversed {fmt(m['baseline']['gap_conf_rev'])}; "
              f"conflict-tied {fmt(m['baseline']['gap_conf_tied'])}", "",
              "Raw send rates (n) by condition x score arm; completion = valid share; competence = task_done in "
              "no-history arm", "",
              "| condition | conflict | reversed | tied | nohist | valid | trunc | failed | empty | task_done (nohist) |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for c in conditions(model):
            cells = [m["raw"][f"{c}|{a}"] for a in SCORE_ARMS]
            n_all = sum(x["n"] for x in cells)
            agg = {o: sum(x[o] * x["n"] for x in cells) / max(n_all, 1) for o in ("valid", "truncated", "failed",
                                                                                   "empty")}
            L.append(f"| {c} | " + " | ".join(f"{x['sent']:.2f} ({x['n']})" for x in cells) +
                     f" | {agg['valid']:.2f} | {agg['truncated']:.2f} | {agg['failed']:.2f} | {agg['empty']:.2f} | "
                     f"{cells[3]['task_done']:.2f} |")
        L += ["", "Effects vs unsteered (cluster bootstrap over blocks):", "",
              "| condition | DiD conflict-reversed | DiD conflict-tied | shift tied | shift reversed | "
              "competence shift (nohist) | valid shift |", "|---|---|---|---|---|---|---|"]
        for c, e in m["effects"].items():
            L.append(f"| {c} | " + " | ".join(fmt(e[x]) for x in ("did_conf_rev", "did_conf_tied", "shift_tied",
                                                                 "shift_reversed", "competence_nohist",
                                                                 "valid_drop")) + " |")
        L += ["", "Comparisons (difference of DiD conflict-reversed):", ""]
        for k, v in m["comparisons"].items():
            L.append(f"- {k}: {fmt(v)}")
        L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="main")
    ap.add_argument("--B", type=int, default=4000)
    a = ap.parse_args()
    rows = score(a.stage)
    res = analyse(rows, a.B)
    res["bridge"] = bridge(rows, a.B)
    (RUN / a.stage / "results.json").write_text(json.dumps(res, indent=1))
    md = report(res, a.stage)
    (RUN / a.stage / "REPORT_auto.md").write_text(md)
    print(md[:6000])


if __name__ == "__main__":
    sys.exit(main())
