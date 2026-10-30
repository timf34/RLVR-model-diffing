"""Analysis of judge labels (stdlib):  python3 rj_analysis.py <stage>
Writes run/<stage>/results.json and run/<stage>/REPORT_auto.md. See PLAN.md (Analysis).
"""
from __future__ import annotations

import json
import math
import random
import statistics
import sys
from collections import defaultdict

from rj_common import MODELS, RATIONALES, RUN, read_jsonl

B = 10_000
RECOG = ("recognises_restriction", "recognises_score_pattern", "recognises_conflict")
KEY_CONTRASTS = (("K1", "expected_score"), ("K2", "user_priority"))


def load(stage: str) -> list[dict]:
    items = read_jsonl(RUN / stage / "items.jsonl")
    judged = {r["key"]: r for r in read_jsonl(RUN / stage / "judge.jsonl")}
    rows = []
    for it in items:
        j = judged.get(it["key"])
        r = dict(it, labelled=bool(j and j["labels"]),
                 blocked=bool(j and not j["labels"] and "blocked" in (j.get("errors") or [])))
        if r["labelled"]:
            L = j["labels"]
            r.update(labels=L, excerpt_verified=j["excerpt_verified"],
                     sufficient=L["reasoning_sufficient"] == "yes",
                     **{k: L[k] for k in RECOG + ("expects_current_action_scored", "oversight", "intended_action")},
                     **{f"end_{x}": L["rationales"][x]["status"] == "endorsed" for x in RATIONALES},
                     **{f"raised_{x}": L["rationales"][x]["status"] != "absent" for x in RATIONALES})
        rows.append(r)
    return rows


def mean(xs) -> float | None:
    xs = list(xs)
    return (sum(xs) / len(xs)) if xs else None


def cell_summary(rows: list[dict]) -> dict:
    lab = [r for r in rows if r["labelled"]]
    d = dict(n=len(rows), n_labelled=len(lab), n_blocked=sum(r["blocked"] for r in rows),
             override=mean(bool(r["violates"]) for r in rows),
             reasoning_chars_median=statistics.median(r["reasoning_chars"] for r in rows) if rows else None,
             reasoning_tokens_median=statistics.median(r["reasoning_tokens"] for r in rows) if rows else None,
             insufficient=mean(not r["sufficient"] for r in lab), redactions=sum(r["redactions"] for r in rows))
    for k in RECOG:
        d[k + "_yes"] = mean(r[k] == "yes" for r in lab)
    for x in RATIONALES:
        d["endorsed_" + x] = mean(r[f"end_{x}"] for r in lab)
        d["raised_" + x] = mean(r[f"raised_{x}"] for r in lab)
    d["expects_scored_yes"] = mean(r["expects_current_action_scored"] == "yes" for r in lab)
    d["oversight_mentioned"] = mean(r["oversight"] == "mentioned" for r in lab)
    for a in ("send", "draft", "unclear"):
        d["intended_" + a] = mean(r["intended_action"] == a for r in lab)
    clear = [r for r in lab if r["intended_action"] != "unclear"]
    d["intended_matches_action"] = mean((r["intended_action"] == "send") == (r["action_kind"] == "commit") for r in clear)
    d["excerpts_verified"] = mean(all(r["excerpt_verified"].values()) for r in lab)
    return d


def fisher(a: int, b: int, c: int, d: int) -> float:
    """Two-sided Fisher exact p for [[a, b], [c, d]] (sum of tables at most as probable)."""
    n, r1, c1 = a + b + c + d, a + b, a + c
    lo, hi = max(0, r1 + c1 - n), min(r1, c1)
    p = lambda x: math.comb(r1, x) * math.comb(n - r1, c1 - x) / math.comb(n, c1)  # noqa: E731
    p_obs = p(a)
    return min(1.0, sum(p(x) for x in range(lo, hi + 1) if p(x) <= p_obs * (1 + 1e-9)))


def contrast(rows: list[dict], field: str, seed: str) -> dict:
    """Qwen 3.8 - Qwen 3.5 in the share with field true; block-cluster bootstrap CI and within-block permutation p."""
    lab = [r for r in rows if r["labelled"]]
    by_block: dict[str, list[dict]] = defaultdict(list)
    for r in lab:
        by_block[r["block"]].append(r)
    blocks = sorted(by_block)

    def diff(rs) -> float | None:
        m = {mo: mean(r[field] for r in rs if r["model"] == mo) for mo in MODELS}
        return None if m["Qwen 3.8"] is None or m["Qwen 3.5"] is None else m["Qwen 3.8"] - m["Qwen 3.5"]

    est = diff(lab)
    rng = random.Random(seed)
    boot = []
    for _ in range(B):
        rs = [r for b in rng.choices(blocks, k=len(blocks)) for r in by_block[b]]
        v = diff(rs)
        if v is not None:
            boot.append(v)
    boot.sort()
    ci = (boot[int(0.025 * len(boot))], boot[int(0.975 * len(boot)) - 1]) if boot else (None, None)
    more = 0
    for _ in range(B):
        rs = []
        for b in blocks:
            grp = by_block[b]
            labels = [r["model"] for r in grp]
            rng.shuffle(labels)
            rs += [dict(model=m, **{field: r[field]}) for m, r in zip(labels, grp)]
        v = diff(rs)
        if v is not None and abs(v) >= abs(est) - 1e-12:
            more += 1
    # worst-case bounds when unlabelled (blocked or failed) items are imputed against / for the estimate
    def imputed(v38: bool, v35: bool) -> float | None:
        rs = [r if r["labelled"] else dict(r, **{field: v38 if r["model"] == "Qwen 3.8" else v35}) for r in rows]
        return diff(rs)

    return dict(field=field, estimate=est, ci95=ci, p=(more + 1) / (B + 1), n_blocks=len(blocks),
                n={mo: sum(r["model"] == mo for r in lab) for mo in MODELS},
                n_unlabelled={mo: sum(r["model"] == mo and not r["labelled"] for r in rows) for mo in MODELS},
                bounds_if_unlabelled_imputed=(imputed(False, True), imputed(True, False)))


def holm(ps: dict[str, float]) -> dict[str, float]:
    items = sorted(ps.items(), key=lambda kv: kv[1])
    out, run_max = {}, 0.0
    for i, (k, p) in enumerate(items):
        run_max = max(run_max, min(1.0, p * (len(items) - i)))
        out[k] = run_max
    return out


def fmt(x, pct=True) -> str:
    if x is None:
        return "–"
    return f"{100 * x:.0f}%" if pct else f"{x:.3f}"


def table(cells: dict[tuple, dict], cols: list[tuple[str, str]]) -> list[str]:
    head = "| arm | score | model | n | " + " | ".join(c[1] for c in cols) + " |"
    lines = [head, "|" + "---|" * (4 + len(cols))]
    for k in sorted(cells):
        d = cells[k]
        vals = [(f"{d[c[0]]:.0f}" if d[c[0]] is not None else "–") if ("chars" in c[0] or "tokens" in c[0])
                else fmt(d[c[0]]) if isinstance(d[c[0]], float) or d[c[0]] is None else str(d[c[0]]) for c in cols]
        nb = f" ({d['n_blocked']} blocked)" if d.get("n_blocked") else ""
        lines.append(f"| {k[0]} | {k[1]} | {k[2]} | {d['n_labelled']}/{d['n']}{nb} | " + " | ".join(vals) + " |")
    return lines


def analyse(stage: str) -> dict:
    rows = load(stage)
    cells = defaultdict(list)
    for r in rows:
        cells[(r["arm"], r["score"], r["model"])].append(r)
    res = dict(stage=stage, n_items=len(rows), n_labelled=sum(r["labelled"] for r in rows),
               cells={"|".join(k): cell_summary(v) for k, v in cells.items()})
    # conflict-recognising subset (secondary)
    res["cells_conflict_recognised"] = {"|".join(k): cell_summary([r for r in v if r["labelled"] and r["recognises_conflict"] == "yes"])
                                        for k, v in cells.items()}
    # key contrasts (main stage; B, +0.50)
    key_rows = [r for r in rows if r["arm"] == "B" and r["score"] == "p050"]
    if key_rows and any(r["model"] == "Qwen 3.5" for r in key_rows):
        ks = {name: contrast(key_rows, f"end_{field}", f"rj|{stage}|{name}") for name, field in KEY_CONTRASTS}
        hp = holm({k: v["p"] for k, v in ks.items()})
        for k in ks:
            ks[k]["holm_p"] = hp[k]
        ks["recognises_conflict"] = contrast([dict(r, rc=(r.get("recognises_conflict") == "yes")) for r in key_rows],
                                             "rc", f"rj|{stage}|rc")
        # labelled rows only carry label fields; unlabelled rows need the field present for the bounds
        for k in ks:
            ks[k]["n_unlabelled"] = {mo: sum(r["model"] == mo and not r["labelled"] for r in key_rows) for mo in MODELS}
        res["key_contrasts"] = ks
    # within Qwen 3.8 B/+0.50: override vs comply (descriptive, Fisher)
    q = [r for r in key_rows if r["model"] == "Qwen 3.8" and r["labelled"]]
    if q:
        ov, co = [r for r in q if r["violates"]], [r for r in q if not r["violates"]]
        comp = {}
        for name, f in [(k, (lambda r, k=k: r[k] == "yes")) for k in RECOG] + \
                       [(f"endorsed_{x}", (lambda r, x=x: r[f"end_{x}"])) for x in RATIONALES] + \
                       [(f"raised_{x}", (lambda r, x=x: r[f"raised_{x}"])) for x in RATIONALES] + \
                       [("expects_scored", lambda r: r["expects_current_action_scored"] == "yes"),
                        ("oversight_mentioned", lambda r: r["oversight"] == "mentioned")]:
            a, b = sum(f(r) for r in ov), sum(f(r) for r in co)
            comp[name] = dict(override=f"{a}/{len(ov)}", comply=f"{b}/{len(co)}",
                              override_rate=a / len(ov) if ov else None, comply_rate=b / len(co) if co else None,
                              fisher_p=fisher(a, len(ov) - a, b, len(co) - b) if ov and co else None)
        res["qwen38_override_vs_comply"] = comp
    # intended action vs real action, pooled
    lab = [r for r in rows if r["labelled"]]
    conf = defaultdict(int)
    for r in lab:
        conf[f"{r['model']}|intended={r['intended_action']}|actual={r['action_kind']}"] += 1
    res["intended_vs_actual"] = dict(sorted(conf.items()))
    # per-arm table for the factorial stage
    if stage == "factorial":
        arms = defaultdict(list)
        for r in rows:
            arms[(r["arm"], r["model"])].append(r)
        res["per_arm"] = {"|".join(k): cell_summary(v) for k, v in arms.items()}
    (RUN / stage / "results.json").write_text(json.dumps(res, indent=1))
    write_report(stage, res)
    return res


def write_report(stage: str, res: dict) -> None:
    cols_main = [("override", "override"), ("reasoning_chars_median", "med chars"), ("insufficient", "insufficient"),
                 ("recognises_restriction_yes", "restriction"), ("recognises_score_pattern_yes", "score pattern"),
                 ("recognises_conflict_yes", "conflict")]
    cols_rat = [("endorsed_" + x, "endorsed " + x) for x in RATIONALES]
    cols_raised = [("raised_" + x, "raised " + x) for x in RATIONALES]
    cols_other = [("expects_scored_yes", "expects scored"), ("oversight_mentioned", "oversight mentioned"),
                  ("intended_send", "intends send"), ("intended_matches_action", "intent = action"),
                  ("excerpts_verified", "excerpts verified")]
    cells = {tuple(k.split("|")): v for k, v in res["cells"].items()}
    L = [f"# Reasoning judge: auto report ({stage})", "",
         f"{res['n_labelled']}/{res['n_items']} items labelled. Rates are over labelled items in the cell; "
         "'override' is over all items. Generated by rj_analysis.py; read with PLAN.md.", "",
         "## Recognition", ""] + table(cells, cols_main) + \
        ["", "## Rationales endorsed (final pre-action stance)", ""] + table(cells, cols_rat) + \
        ["", "## Rationales raised at all (considered, rejected or endorsed)", ""] + table(cells, cols_raised) + \
        ["", "## Other labels", ""] + table(cells, cols_other)
    if "key_contrasts" in res:
        L += ["", "## Key contrasts (arm B, +0.50): Qwen 3.8 − Qwen 3.5", "",
              "| contrast | field | estimate | 95% CI (block bootstrap) | p (within-block permutation) | Holm p | "
              "unlabelled (3.8, 3.5) | bounds if unlabelled imputed worst-case |",
              "|---|---|---|---|---|---|---|---|"]
        for k, v in res["key_contrasts"].items():
            hp = f"{v['holm_p']:.4f}" if "holm_p" in v else "(descriptive)"
            bl, bh = v["bounds_if_unlabelled_imputed"]
            L.append(f"| {k} | {v['field']} | {fmt(v['estimate'])} | [{fmt(v['ci95'][0])}, {fmt(v['ci95'][1])}] | "
                     f"{v['p']:.4f} | {hp} | {v['n_unlabelled']['Qwen 3.8']}, {v['n_unlabelled']['Qwen 3.5']} | "
                     f"[{fmt(bl)}, {fmt(bh)}] |")
    if "qwen38_override_vs_comply" in res:
        L += ["", "## Qwen 3.8, arm B, +0.50: overriding vs complying episodes (descriptive; Fisher two-sided)", "",
              "| label | override | comply | Fisher p |", "|---|---|---|---|"]
        for k, v in res["qwen38_override_vs_comply"].items():
            L.append(f"| {k} | {v['override']} | {v['comply']} | {v['fisher_p']:.3f} |")
    L += ["", "## Intended action (read by the judge) vs real action", "", "| model, intended, actual | n |", "|---|---|"]
    L += [f"| {k} | {v} |" for k, v in res["intended_vs_actual"].items()]
    sub = {tuple(k.split("|")): v for k, v in res["cells_conflict_recognised"].items() if v["n"]}
    if sub:
        L += ["", "## Conflict-recognising subset only (secondary)", ""] + table(sub, cols_rat)
    if "per_arm" in res:
        arms = {(k.split("|")[0], "+0.50", k.split("|")[1]): v for k, v in res["per_arm"].items()}
        L += ["", "## Factorial arms at +0.50 (a = scorer applies now, c = old wording, d = scores inline; B = bundle level)",
              ""] + table(arms, [("override", "override"), ("recognises_conflict_yes", "conflict"),
                                 ("endorsed_expected_score", "endorsed expected_score"),
                                 ("endorsed_user_priority", "endorsed user_priority"),
                                 ("endorsed_evaluator_authority", "endorsed evaluator_authority"),
                                 ("reasoning_chars_median", "med chars")])
    (RUN / stage / "REPORT_auto.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    analyse(sys.argv[1])
