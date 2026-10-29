"""Score, judge and analyse one experiment.

    analyse.py A|B [--no-judge] [--judge-factual all|unsure] [--run-dir DIR] [--smoke] [--judge-budget USD]

Inputs : <exp>/blocks/*.json, <run>/gen/<Model>/generations.jsonl (latest valid record per key, else latest).
Outputs: <run>/scored.jsonl, <run>/results.json, <exp>/REPORT_tables.md (or <run>/REPORT_tables.md when --run-dir
         or --smoke is given), plus the judge cache / ledger in <run>/.

Labels: only `valid` trials are scored. Rules first (scorers.py); the judge (judge.py) labels items the rules mark
needs_judge and, with --judge-factual all (default), every limitation / certainty / status item except an exact
required-sentence match (those are semantic; the keyword rules are kept as diagnostics and agreement is reported).
--no-judge leaves judge-needing items `unclear` (dry run, no API calls).

Holm runs over the 8 primary tests (A1-A6, B1-B2). Each run recomputes it from both experiments' results.json; a
primary test not yet available is treated as p = 1 (conservative) and the report says so.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import judge as J  # noqa: E402
import scorers as SC  # noqa: E402
import stats as ST  # noqa: E402

ROOT = HERE.parents[2]
EXPS = {"A": ROOT / "designs" / "grouped_replication", "B": ROOT / "designs" / "transfer"}
PRIMARY_IDS = ("A1", "A2", "A3", "A4", "A5", "A6", "B1", "B2")


# ----------------------------------------------------------------------------------------------------------------
# loading

def load_blocks(exp_dir: Path, smoke: bool = False) -> dict:
    out = {}
    for p in sorted((exp_dir / "blocks").glob("*.json")):
        for b in json.loads(p.read_text()):
            if bool(b.get("smoke")) == smoke:
                out[b["block_id"]] = b
    return out


def load_generations(run_dir: Path) -> list[dict]:
    recs = collections.defaultdict(list)
    for p in sorted((run_dir / "gen").glob("*/*.jsonl")):
        if p.name not in ("generations.jsonl", "episodes.jsonl"):
            continue
        for line in p.read_text().splitlines():
            if line.strip():
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if "key" in r:
                    recs[r["key"]].append(r)
    out = []
    for k, rs in recs.items():
        valid = [r for r in rs if r.get("status") == "valid"]
        out.append(valid[-1] if valid else rs[-1])
    return out


def model_label(m: str) -> str:
    return (m or "").replace("_", " ")


def roles(exp: str, block: dict) -> list[tuple[str, str, dict]]:
    chk = block["current"]["check"]
    if exp == "A":
        return [("violation", block["subtype"], chk)]
    return [("source", block["source"], chk["source"]), ("target", block["target"], chk["target"])]


def stratum(exp: str, block: dict) -> str:
    return block["subtype"] if exp == "A" else block["direction"]


# ----------------------------------------------------------------------------------------------------------------
# scoring

def score_records(exp: str, blocks: dict, gens: list[dict], judge_mode: str, use_judge: bool,
                  run_dir: Path, judge_budget: float) -> tuple[list[dict], dict]:
    scored, judge_items = [], []
    skipped = collections.Counter()
    for g in gens:
        b = blocks.get(g.get("block_id"))
        if b is None:
            skipped["block_not_in_set"] += 1
            continue
        valid = g.get("status") == "valid"
        rec = dict(key=g["key"], block_id=b["block_id"], stratum=stratum(exp, b), model=model_label(g.get("model")),
                   frame=g.get("frame"), history=g.get("history"), gap=g.get("gap"),
                   permission=g.get("permission") if exp == "B" else None,
                   cond=ST.cond_of(g.get("history"), g.get("gap")), status=g.get("status"),
                   cost_usd=g.get("cost_usd"), text_tool_calls=g.get("text_tool_calls"), outcomes={})
        if exp == "A":
            rec["subtype"] = b["subtype"]
        else:
            rec.update(direction=b["direction"], source=b["source"], target=b["target"])
        for role, beh, chk in roles(exp, b):
            if not valid:
                rec["outcomes"][role] = dict(behaviour=beh, label="nonvalid", rule=None)
                continue
            r = SC.score(beh, g.get("reply") or "", g.get("tool_log"), chk, g.get("text_tool_calls"))
            o = dict(behaviour=beh, rule_label=r["label"], **{k: v for k, v in r.items() if k != "label"})
            want = r["needs_judge"] or (judge_mode == "all" and beh in SC.FACTUAL_BEHAVIOURS
                                        and r["rule"] != "exact_sentence")
            o["judge_wanted"] = bool(want and beh in J.RUBRICS)
            if o["judge_wanted"]:
                body = bool(SC.drafted_body(g.get("tool_log"))[0])
                item = dict(behaviour=beh, request=b["current"]["request"],
                            text=SC.judged_text(beh, g.get("reply") or "", g.get("tool_log")), check=chk,
                            what=("the assistant's drafted message and its final reply" if body
                                  else "the assistant's reply"), _ref=(len(scored), role))
                judge_items.append(item)
            rec["outcomes"][role] = o
        if valid:
            rec["completion"] = SC.completion(g.get("reply") or "", g.get("tool_log"),
                                              b["current"].get("required_facts") or [])
            rec["completion_detail"] = SC.completion_detail(g.get("reply") or "", g.get("tool_log"),
                                                            b["current"].get("required_facts") or [])
        scored.append(rec)

    cache = {}
    if judge_items and use_judge:
        cache = J.judge_sync(judge_items, run_dir, budget_usd=judge_budget)
    elif judge_items:
        for it in judge_items:   # still compute keys / redaction counts for the record
            p, n = J.build_prompt(it["behaviour"], it["request"], it["text"], it["check"], it["what"])
            it["cache_key"], it["redactions"] = J.cache_key(p), n
        cache = J.load_cache(run_dir / "judge_cache.jsonl")   # reuse labels from earlier judged runs, if any
    for it in judge_items:
        i, role = it["_ref"]
        o = scored[i]["outcomes"][role]
        o["judge_cache_key"], o["redactions"] = it["cache_key"], it["redactions"]
        j = cache.get(it["cache_key"])
        if j and not j.get("judge_failed"):
            o.update(judged=True, judge_label=j["label"], judge_reason=j["reason"], judge_failed=False)
        else:
            o.update(judged=False, judge_label=None, judge_failed=bool(j and j.get("judge_failed")))
    for rec in scored:
        for o in rec["outcomes"].values():
            if o.get("label") == "nonvalid":
                continue
            if o.get("judged"):
                o["label"], o["label_source"] = o["judge_label"], "judge"
            elif o.get("judge_wanted") and o.get("needs_judge"):
                o["label"], o["label_source"] = "unclear", "not_judged"
            else:
                o["label"], o["label_source"] = o["rule_label"], "rule"
    return scored, dict(skipped=dict(skipped), n_judge_items=len(judge_items))


# ----------------------------------------------------------------------------------------------------------------
# panel and summaries

def build_panel(exp: str, blocks: dict, scored: list[dict]) -> dict:
    panel = {bid: {"stratum": stratum(exp, b), "cells": {}} for bid, b in blocks.items()}
    for r in scored:
        perm = "na" if exp == "A" else (r["permission"] or "none")
        for role, o in r["outcomes"].items():
            panel[r["block_id"]]["cells"][(role, r["model"], r["frame"], perm, r["cond"])] = o["label"]
    return panel


def strata_groups(exp: str, blocks: dict) -> dict:
    present = sorted({stratum(exp, b) for b in blocks.values()})
    if exp == "A":
        g = {f: tuple(s for s in subs if s in present) for f, subs in ST.FAMILIES.items()}
        g = {f: s for f, s in g.items() if s}
        for s in present:
            g[s] = (s,)
        return g
    g = {"all directions": tuple(d for d in ST.DIRECTIONS if d in present) or tuple(present)}
    for d in present:
        g[d] = (d,)
    return g


def cells_table(exp: str, panel: dict, groups: dict) -> list[dict]:
    keys = sorted({k for b in panel.values() for k in b["cells"]})
    out = []
    for key in keys:
        for gname, strata in groups.items():
            c = ST.cell_summary(panel, key, strata)
            if c["n_planned"] == 0 or (c["n"] + c["n_unclear"] + c["n_nonvalid"]) == 0:
                continue
            c["group"] = gname
            c["level"] = ("family" if gname in ST.FAMILIES else "pooled" if gname == "all directions"
                          else "direction" if exp == "B" else "subtype")
            out.append(c)
    return out


def denominators(exp: str, blocks: dict, scored: list[dict]) -> list[dict]:
    planned_per_stratum = collections.Counter(stratum(exp, b) for b in blocks.values())
    agg = {}
    for r in scored:
        k = (r["model"], r["frame"], r["permission"] or "na", r["cond"], r["stratum"])
        d = agg.setdefault(k, dict(model=k[0], frame=k[1], permission=k[2], cond=k[3], stratum=k[4],
                                   planned=planned_per_stratum[k[4]], generated=0, valid=0, statuses={},
                                   unclear={}, judged={}, rule_unclear={}))
        d["generated"] += 1
        d["statuses"][r["status"]] = d["statuses"].get(r["status"], 0) + 1
        d["valid"] += r["status"] == "valid"
        for role, o in r["outcomes"].items():
            d["unclear"][role] = d["unclear"].get(role, 0) + (o["label"] == "unclear")
            d["judged"][role] = d["judged"].get(role, 0) + bool(o.get("judged"))
            d["rule_unclear"][role] = d["rule_unclear"].get(role, 0) + (o.get("rule_label") == "unclear")
    return sorted(agg.values(), key=lambda d: (d["model"], d["frame"], d["permission"], d["cond"], d["stratum"]))


def completion_table(exp: str, scored: list[dict], groups: dict) -> list[dict]:
    out = []
    acc = collections.defaultdict(lambda: [0, 0])
    for r in scored:
        if r["status"] != "valid":
            continue
        for gname, strata in groups.items():
            if r["stratum"] in strata:
                k = (gname, r["model"], r["frame"], r["permission"] or "na", r["cond"])
                acc[k][0] += bool(r.get("completion"))
                acc[k][1] += 1
    for (g, m, f, p, c), (k, n) in sorted(acc.items()):
        out.append(dict(group=g, model=m, frame=f, permission=p, cond=c, k=k, n=n, rate=k / n if n else None))
    return out


def judge_summary(scored: list[dict], run_dir: Path) -> dict:

    agree = collections.Counter()
    by_beh = collections.defaultdict(collections.Counter)
    for r in scored:
        for o in r["outcomes"].values():
            if o.get("judged"):
                by_beh[o["behaviour"]][o["judge_label"]] += 1
                if o.get("rule_label") in ("violates", "complies"):
                    agree["agree" if o["rule_label"] == o["judge_label"] else "disagree"] += 1
    return dict(judge_model=J.JUDGE_MODEL, judge_version=J.JUDGE_VERSION, ledger=J.ledger_summary(run_dir),
                labels_by_behaviour={k: dict(v) for k, v in by_beh.items()},
                rule_clear_vs_judge=dict(agree),
                n_judged=sum(sum(v.values()) for v in by_beh.values()),
                n_judge_failed=sum(bool(o.get("judge_failed")) for r in scored for o in r["outcomes"].values()),
                n_not_judged=sum(o.get("label_source") == "not_judged" for r in scored for o in r["outcomes"].values()),
                redacted_items=sum(bool(o.get("redactions")) for r in scored for o in r["outcomes"].values()))


# ----------------------------------------------------------------------------------------------------------------
# contrasts

def all_contrasts(exp: str, blocks: dict) -> list[ST.Contrast]:
    present = {stratum(exp, b) for b in blocks.values()}
    if exp == "A":
        fams = {f: tuple(s for s in subs if s in present) or subs for f, subs in ST.FAMILIES.items()}
        return ST.contrasts_A(ST.FOCUS, True, fams) + ST.secondary_A(fams)
    dirs = tuple(d for d in ST.DIRECTIONS if d in present) or ST.DIRECTIONS
    return ST.contrasts_B(ST.FOCUS, True, dirs) + ST.secondary_B(dirs)


def run_contrasts(exp: str, panel: dict, blocks: dict) -> list[dict]:
    out = []
    for c in all_contrasts(exp, blocks):
        r = ST.evaluate(panel, c)
        if c.primary or r["n_blocks_used"] > 0:
            out.append(r)
    return out


def update_holm(exps=("A", "B"), run_dirs: dict | None = None) -> dict:
    """Holm over the 8 primary tests across both experiments' results.json; missing tests count as p = 1."""
    files = {e: (run_dirs or {}).get(e, EXPS[e] / "run") / "results.json" for e in exps}
    res = {e: json.loads(f.read_text()) for e, f in files.items() if f.exists()}
    ps, avail = {}, []
    for e, r in res.items():
        for c in r["contrasts"]:
            if c["primary"] and c["id"] in PRIMARY_IDS:
                ps[c["id"]] = c["p"] if c["p"] is not None else 1.0
                if c["p"] is not None:
                    avail.append(c["id"])
    for pid in PRIMARY_IDS:
        ps.setdefault(pid, 1.0)
    adj = ST.holm(ps)
    info = dict(tests=list(PRIMARY_IDS), available=sorted(avail),
                note=("Holm over the 8 primary tests; tests not yet analysed count as p = 1 (conservative)"
                      if len(avail) < 8 else "Holm over the 8 primary tests"))
    for e, r in res.items():
        for c in r["contrasts"]:
            if c["primary"] and c["id"] in adj:
                c["p_holm"] = adj[c["id"]]
        r["holm"] = info
        files[e].write_text(json.dumps(r, indent=1))
        rep = Path(r["report_path"]) if r.get("report_path") else None
        if rep:
            rep.write_text(render_tables(r))
    return info


# ----------------------------------------------------------------------------------------------------------------
# report

def fmt_rate(c: dict) -> str:
    if c.get("rate") is None:
        return "–"
    if c["k"] == 0:
        return f"0/{c['n']} (≤{c['hi']:.2f})"
    if c["k"] == c["n"]:
        return f"{c['n']}/{c['n']} (≥{c['lo']:.2f})"
    return f"{c['rate']:.2f} [{c['lo']:.2f}, {c['hi']:.2f}] ({c['k']}/{c['n']})"


def fmt_p(p) -> str:
    return "–" if p is None else ("<0.001" if p < 0.001 else f"{p:.3f}")


def fmt_ci(c: dict) -> str:
    if c.get("ci") is None:
        return "–"
    lo, hi = c["ci"]
    s = f"[{lo:+.2f}, {hi:+.2f}]"
    return s + ("†" if c.get("degenerate") else "")


def _est(c):
    return "–" if c.get("estimate") is None else f"{c['estimate']:+.3f}"


def _miss(c):
    m = c["n_missing"]
    return f"{m['nonvalid']}/{m['unclear']}/{m['absent']}"


def _sens(c):
    a, b = c.get("sens_unclear_violates"), c.get("sens_unclear_complies")
    lo, hi = (c.get("sens_bounds") or [None, None])
    f = lambda x: "–" if x is None else f"{x:+.2f}"  # noqa: E731
    return f"{f(a)} / {f(b)}; [{f(lo)}, {f(hi)}]"


def allows(c: dict) -> str:
    if c.get("ci") is None:
        return "no data"
    lo, hi = c["ci"]
    if lo > 0 or hi < 0:
        return f"excludes 0; effect between {lo:+.2f} and {hi:+.2f}"
    return f"compatible with effects from {lo:+.2f} to {hi:+.2f}"


def contrast_rows(cs: list[dict], holm: bool = False) -> list[str]:
    head = "| id | contrast | estimate | 95% CI | p | " + ("Holm p | " if holm else "") + \
           "blocks used/planned | missing nonvalid/unclear/absent | unclear→viol / →comp; worst-case | " \
           "interval reading |"
    rows = [head, "|" + "---|" * (head.count("|") - 1)]
    for c in cs:
        rows.append(f"| {c['id']} | {c['name']} | {_est(c)} | {fmt_ci(c)} | {fmt_p(c['p'])} | "
                    + (f"{fmt_p(c.get('p_holm'))} | " if holm else "")
                    + f"{c['n_blocks_used']}/{c['n_blocks_planned']} | {_miss(c)} | {_sens(c)} | {allows(c)} |")
    return rows


def render_tables(res: dict) -> str:
    exp = res["experiment"]
    L = [f"# Experiment {exp}: analysis tables (auto-generated)", "",
         f"Generated {res['generated_at']} by `designs/overnight_common/analysis/analyse.py {exp}`. "
         f"Blocks: {res['inputs']['n_blocks']} ({'smoke' if res['settings']['smoke'] else 'main'}); generation records "
         f"used: {res['inputs']['n_records']}. Judge mode: {res['settings']['judge']}.", "",
         "Methods: block-level paired contrasts (one generation per cell). Family / B estimates are equal-weighted "
         "means of subtype / direction means. p: stratified sign-flip permutation of block values (exact when "
         "≤18 non-zero blocks, else 20,000 Monte Carlo draws, fixed seed). CI: cluster bootstrap of blocks within "
         "strata (4000 reps, percentile). † = zero-variation interval replaced by the block-level one-sided 95% bound "
         "1−0.05^(1/n) on each side (never a zero-width interval). Rates: `0/n (≤ub)` = no events, one-sided 95% "
         "upper bound at the block level. Unclear and non-valid cells make that block's contrast missing; the "
         "sensitivity column re-estimates with unclear → violates / → complies, and worst-case bounds. "
         "Non-significant results are not equivalence: the last column states the effects the interval still allows.",
         ""]
    L += ["## Primary contrasts (Qwen 3.8)", "", f"Holm: {res.get('holm', {}).get('note', 'not run')}.", ""]
    L += contrast_rows([c for c in res["contrasts"] if c["primary"]], holm=True)
    L += [""]
    # denominators
    L += ["## Denominators", "", "| model | frame | permission | cond | planned | generated | valid | statuses | "
          "unclear (final) | judged |", "|---|---|---|---|---|---|---|---|---|---|"]
    agg = {}
    for d in res["denominators"]:
        k = (d["model"], d["frame"], d["permission"], d["cond"])
        a = agg.setdefault(k, dict(planned=0, generated=0, valid=0, statuses=collections.Counter(),
                                   unclear=collections.Counter(), judged=collections.Counter()))
        a["planned"] += d["planned"]
        a["generated"] += d["generated"]
        a["valid"] += d["valid"]
        a["statuses"].update(d["statuses"])
        a["unclear"].update(d["unclear"])
        a["judged"].update(d["judged"])
    for k, a in sorted(agg.items(), key=lambda kv: (kv[0][:3], ST.CONDS.index(kv[0][3]) if kv[0][3] in ST.CONDS else 9)):
        st = ", ".join(f"{s} {n}" for s, n in sorted(a["statuses"].items()))
        L.append(f"| {' | '.join(k)} | {a['planned']} | {a['generated']} | {a['valid']} | {st} | "
                 f"{dict(a['unclear'])} | {dict(a['judged'])} |")
    L += [""]
    # cell tables
    conds = [c for c in ST.CONDS if any(x["cond"] == c for x in res["cells"])]
    lv = ("family", "subtype") if exp == "A" else ("pooled", "direction")
    for level in lv:
        L += [f"## Violation rates by {level}", "",
              "| outcome | group | model | frame | permission | " + " | ".join(conds) + " |",
              "|" + "---|" * (5 + len(conds))]
        rows = collections.defaultdict(dict)
        for c in res["cells"]:
            if c["level"] == level:
                rows[(c["outcome"], c["group"], c["model"], c["frame"], c["permission"])][c["cond"]] = c
        for k in sorted(rows):
            L.append("| " + " | ".join(k) + " | " + " | ".join(fmt_rate(rows[k][c]) if c in rows[k] else "–"
                                                                for c in conds) + " |")
        L += [""]
    # secondary contrasts
    kinds = collections.OrderedDict()
    for c in res["contrasts"]:
        if not c["primary"]:
            kinds.setdefault(c["kind"], []).append(c)
    L += ["## Secondary contrasts (unadjusted p; descriptive)", ""]
    for kind, cs in kinds.items():
        L += [f"### {kind}", ""] + contrast_rows(cs) + [""]
    # completion
    L += ["## Task completion (all required facts present; valid trials)", "",
          "| group | model | frame | permission | cond | k/n | rate |", "|---|---|---|---|---|---|---|"]
    for c in res["completion"]:
        if exp == "B" or c["group"] in ST.FAMILIES:
            L.append(f"| {c['group']} | {c['model']} | {c['frame']} | {c['permission']} | {c['cond']} | "
                     f"{c['k']}/{c['n']} | {c['rate']:.2f} |")
    L += ["", "## Judge", "", "```", json.dumps(res["judge"], indent=1), "```", ""]
    return "\n".join(L)


# ----------------------------------------------------------------------------------------------------------------

def sha_files(paths) -> dict:
    return {str(p.relative_to(ROOT)) if str(p).startswith(str(ROOT)) else str(p):
            hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def analyse(exp: str, use_judge: bool = True, judge_mode: str = "all", run_dir: Path | None = None,
            smoke: bool = False, judge_budget: float = 25.0, exp_dir: Path | None = None,
            report_path: Path | None = None, holm: bool = True) -> dict:
    exp_dir = Path(exp_dir or EXPS[exp])
    default_run = run_dir is None
    run_dir = Path(run_dir or exp_dir / "run")
    blocks = load_blocks(exp_dir, smoke=smoke)
    if not blocks:
        raise SystemExit(f"no {'smoke' if smoke else 'main'} blocks under {exp_dir / 'blocks'}")
    gens = load_generations(run_dir)
    scored, sinfo = score_records(exp, blocks, gens, judge_mode, use_judge, run_dir, judge_budget)
    with (run_dir / "scored.jsonl").open("w") as f:
        for r in scored:
            f.write(json.dumps(r) + "\n")
    panel = build_panel(exp, blocks, scored)
    groups = strata_groups(exp, blocks)
    report_path = Path(report_path or (exp_dir / "REPORT_tables.md" if default_run and not smoke
                                       else run_dir / "REPORT_tables.md"))
    res = dict(experiment=exp, generated_at=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
               settings=dict(judge=("off (--no-judge)" if not use_judge else f"on, factual={judge_mode}"),
                             smoke=smoke, mc_draws=ST.MC_DRAWS, boot_reps=ST.BOOT_REPS, exact_max=ST.EXACT_MAX,
                             base_seed=ST.BASE_SEED, focus=ST.FOCUS, compare=ST.COMPARE),
               inputs=dict(n_blocks=len(blocks), n_records=len(gens), n_scored=len(scored), **sinfo,
                           blocks_sha256=sha_files(sorted((exp_dir / "blocks").glob("*.json"))),
                           generations_sha256=sha_files(sorted((run_dir / "gen").glob("*/generations.jsonl")))),
               strata_groups={k: list(v) for k, v in groups.items()},
               denominators=denominators(exp, blocks, scored),
               cells=cells_table(exp, panel, groups),
               contrasts=run_contrasts(exp, panel, blocks),
               completion=completion_table(exp, scored, groups),
               judge=judge_summary(scored, run_dir),
               report_path=str(report_path))
    (run_dir / "results.json").write_text(json.dumps(res, indent=1))
    if holm and not smoke and default_run:
        update_holm()
        res = json.loads((run_dir / "results.json").read_text())
    else:
        info = update_holm((exp,), {exp: run_dir})
        res = json.loads((run_dir / "results.json").read_text())
        res["holm"] = info
    report_path.write_text(render_tables(res))
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("exp", choices=["A", "B"])
    ap.add_argument("--no-judge", action="store_true", help="dry run: no API calls; judge-needing items stay unclear")
    ap.add_argument("--judge-factual", choices=["all", "unsure"], default="all",
                    help="all (default): judge every limitation/certainty/status item except exact-sentence matches; "
                         "unsure: judge only items the rules mark needs_judge")
    ap.add_argument("--run-dir", type=Path, default=None)
    ap.add_argument("--exp-dir", type=Path, default=None, help="override the experiment folder (tests)")
    ap.add_argument("--smoke", action="store_true", help="analyse the smoke blocks only")
    ap.add_argument("--judge-budget", type=float, default=25.0)
    a = ap.parse_args(argv)
    res = analyse(a.exp, use_judge=not a.no_judge, judge_mode=a.judge_factual, run_dir=a.run_dir, smoke=a.smoke,
                  judge_budget=a.judge_budget, exp_dir=a.exp_dir)
    prim = [c for c in res["contrasts"] if c["primary"]]
    for c in prim:
        print(f"{c['id']}: est={_est(c)} ci={fmt_ci(c)} p={fmt_p(c['p'])} holm={fmt_p(c.get('p_holm'))} "
              f"blocks={c['n_blocks_used']}/{c['n_blocks_planned']}")
    print(f"wrote {res['report_path']} and results.json; judge: {res['judge']['ledger']}")


if __name__ == "__main__":
    main()
