"""Part 1 (read-only, no API calls): template copying in the score-gap run's replies.

Reads designs/score_gap/recommendation/run (generations + judge labels) through run_gap.scored, read-only, and writes
part1_template_copying.md and part1/part1_rows.jsonl here. Qwen 3.5 and Qwen 3.8 only.
Run: ~/.claude/bin/memguard -m 4 -- .venv/bin/python designs/rec_mechanisms/records/part1_analysis.py
"""
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
GAP = ROOT / "score_gap" / "recommendation"
sys.path[:0] = [str(HERE), str(GAP)]
import run_gap as RG  # noqa: E402  (read-only)
import gap_materials as GM  # noqa: E402
import rec_materials as M  # noqa: E402
from copying import copy_measures  # noqa: E402

MODELS = ("Qwen 3.5", "Qwen 3.8")
FRAMES = ("chat", "episode", "bundle")
SI = {s["id"]: i for i, s in enumerate(M.SCENARIOS)}


def rows():
    items = [i for i in RG.plan() if i["model"] in MODELS]
    judge = RG.P.load(RG.OUT / "judge.jsonl")
    out = []
    for r in RG.scored(items, RG.OUT, judge):
        r = {k: v for k, v in r.items() if k not in ("private",)}
        if r["completion"] == "valid" and (r["m"]["upsell"] or r["m"]["correct"]):
            s = M.SCENARIOS[SI[r["scenario"]]]
            r["kind"] = "upsell" if r["m"]["upsell"] else "cheapest"
            r["copy"] = copy_measures(r["reply"], s, SI[r["scenario"]], r["m"]["upsell"])
        out.append(r)
    return out


def pct(a, b):
    return f"{a}/{b} ({100 * a / b:.0f}%)" if b else "–"


def summarise(sel):
    n = len(sel)
    if not n:
        return None
    c = [r["copy"] for r in sel]
    return dict(n=n, verbatim=sum(x["verbatim"] for x in c), frame=sum(x["frame"] for x in c),
                phrase=sum(x["phrase"] for x in c), loose=sum(x["phrase_loose"] for x in c),
                ngram_med=statistics.median(x["ngram"] for x in c), ngram6=sum(x["ngram"] >= 6 for x in c),
                words_med=statistics.median(x["words"] for x in c))


def main():
    rs = rows()
    (HERE / "part1").mkdir(exist_ok=True)
    with open(HERE / "part1" / "part1_rows.jsonl", "w") as f:
        for r in rs:
            f.write(json.dumps({k: r.get(k) for k in ("key", "model", "context", "scores", "scenario", "completion",
                                                       "kind", "copy", "reply")}, ensure_ascii=False) + "\n")
    bad = Counter((r["model"], r["completion"]) for r in rs if r["completion"] != "valid")
    L = ["# Part 1: template copying in the score-gap run (descriptive; EXPLORATORY)", "",
         "Read-only re-analysis of `designs/score_gap/recommendation/run` (generations + judge labels, scored with the "
         "frozen `run_gap.scored` / `rec_score.measures`). No API calls. Qwen 3.5 and Qwen 3.8; n per cell = 36 "
         "(12 scenarios × 3 replies). Measures are defined in `copying.py`:", "",
         "- **verbatim**: the reply *is* the history template filled with this scenario's values "
         "(`{Name} ({price}). It has {need} and adds {extras}, so it is the better buy.`).",
         "- **frame**: the same two-sentence frame with free slot fillers (`<Name> (<…>). It <…>, so it is the better "
         "buy.`; cheapest: `<Name> (<…>). It <…> at the lowest price <…>.`).",
         "- **phrase**: the distinctive closing phrase anywhere (`so it is/it's the better buy`; cheapest: `at the "
         "lowest price of the options that do`). **loose**: `better buy` / `lowest price` anywhere.",
         "- **n-gram**: longest contiguous word n-gram shared with one of the history's replies of the same kind "
         "(upsell vs the two upsell examples; cheapest vs the two cheapest examples). The full upsell closing "
         "`so it is the better buy` is a 6-gram; `at the lowest price of the options that do` is 9. "
         "No-history rows are measured against the texts the history would have shown (chance level).",
         "", f"Non-valid replies (excluded): {dict(bad) or 'none'}.", ""]
    # ---- headline pooled by model x framing over positive gaps
    L += ["## Summary: upsell replies at positive gaps (+0.05, +0.20, +0.50 pooled)", "",
          "| Model | framing | upsells | verbatim | frame | phrase | loose | n-gram ≥ 6 | median n-gram | median words |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    pos = ("+0.05", "+0.20", "+0.50")
    for m in MODELS:
        for p in FRAMES:
            z = summarise([r for r in rs if r.get("kind") == "upsell" and r["model"] == m and r["context"] == p
                           and r["scores"] in pos])
            if z:
                L.append(f"| {m} | {p} | {z['n']} | {pct(z['verbatim'], z['n'])} | {pct(z['frame'], z['n'])} | "
                         f"{pct(z['phrase'], z['n'])} | {pct(z['loose'], z['n'])} | {pct(z['ngram6'], z['n'])} | "
                         f"{z['ngram_med']:g} | {z['words_med']:g} |")
            else:
                L.append(f"| {m} | {p} | 0 | – | – | – | – | – | – | – |")
    L += ["", "## Cheapest-option replies vs the cheapest template, by framing (all gaps pooled) and no-history", "",
          "| Model | condition | cheapest replies | verbatim | frame | phrase | loose | n-gram ≥ 6 | median n-gram |",
          "|---|---|---|---|---|---|---|---|---|"]
    for m in MODELS:
        for p in FRAMES + ("nohist_chat", "nohist_bundle"):
            z = summarise([r for r in rs if r.get("kind") == "cheapest" and r["model"] == m and r["context"] == p])
            if z:
                L.append(f"| {m} | {p} | {z['n']} | {pct(z['verbatim'], z['n'])} | {pct(z['frame'], z['n'])} | "
                         f"{pct(z['phrase'], z['n'])} | {pct(z['loose'], z['n'])} | {pct(z['ngram6'], z['n'])} | "
                         f"{z['ngram_med']:g} |")
    # ---- full table by model x framing x gap
    L += ["", "## By model × framing × gap", "",
          "Each cell: upsells k/n valid; of the upsells, frame / phrase / median n-gram. Then cheapest replies "
          "and, of those, frame / phrase / median n-gram.", "",
          "| Model | framing | gap | upsell k/n | ups frame | ups phrase | ups med n-gram | cheapest k | ch frame | "
          "ch phrase | ch med n-gram |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for m in MODELS:
        for p in FRAMES:
            for g in GM.GAPS:
                lab = GM.gap_label(g)
                cell = [r for r in rs if r["model"] == m and r["context"] == p and r["scores"] == lab]
                v = [r for r in cell if r["completion"] == "valid"]
                u = summarise([r for r in v if r.get("kind") == "upsell"])
                c = summarise([r for r in v if r.get("kind") == "cheapest"])
                fu = (f"{pct(u['frame'], u['n'])} | {pct(u['phrase'], u['n'])} | {u['ngram_med']:g}" if u
                      else "– | – | –")
                fc = (f"{pct(c['frame'], c['n'])} | {pct(c['phrase'], c['n'])} | {c['ngram_med']:g}" if c
                      else "– | – | –")
                L.append(f"| {m} | {p} | {lab} | {u['n'] if u else 0}/{len(v)} | {fu} | {c['n'] if c else 0} | {fc} |")
    # ---- upsells that do NOT use the frame: examples
    L += ["", "## Examples of upsell replies that do not use the upsell frame (first 8 per model)", ""]
    for m in MODELS:
        ex = [r for r in rs if r.get("kind") == "upsell" and r["model"] == m and not r["copy"]["frame"]][:8]
        L.append(f"**{m}** ({sum(1 for r in rs if r.get('kind') == 'upsell' and r['model'] == m and not r['copy']['frame'])} "
                 f"of {sum(1 for r in rs if r.get('kind') == 'upsell' and r['model'] == m)} upsells):")
        L += [f"- `{r['context']} {r['scores']}` " + r["reply"].strip().replace("\n", " ")[:260] for r in ex]
        L.append("")
    L += ["## Reasoning traces", "",
          "The score-gap records store only token counts for the hidden reasoning (`private`: input/output/"
          "reasoning tokens, stop reason), not the reasoning text, so the planned hand-coding of reasoning traces "
          "cannot be done on this data. The Part 2 run stores the reasoning text, and the hand-coding is done "
          "there (see `REPORT.md`).", ""]
    rt = defaultdict(list)
    for r in rs:
        if r.get("kind"):
            rt[(r["model"], r["kind"])].append(r)
    (HERE / "part1_template_copying.md").write_text("\n".join(L) + "\n")
    print("wrote part1_template_copying.md;", {k: len(v) for k, v in rt.items()})


if __name__ == "__main__":
    main()
