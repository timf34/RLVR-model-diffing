"""DISCOVERY follow-up to the frozen style pilot: softer user requests between "silent" and "explicit".

Labelled discovery because the request levels were chosen after seeing the pilot. Any effect found here
needs confirmation on fresh, frozen tasks. The pilot's own result stays as recorded in PROPOSAL.md.

Same tasks, contexts, score reversal, serving and pinned code snapshot as the pilot; only the user's
format request changes (materials.SOFT_USERS). Scoring is rule-based only (score.py); no judge.

Run from the repo root:
  .venv/bin/python designs/rl_context/run_soft.py inspect    # 1 task, 1 sample per cell (48), not analysed
  .venv/bin/python designs/rl_context/run_soft.py freeze
  .venv/bin/python designs/rl_context/run_soft.py generate
  .venv/bin/python designs/rl_context/run_soft.py analyse
"""
import asyncio
import itertools
import json
import math
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import run_pilot as P  # noqa: E402  (shares serving, generation and the pinned src snapshot)
from materials import CONTEXTS, SCORES, SOFT_USERS, TASKS, render  # noqa: E402
from score import measures  # noqa: E402

OUT = HERE / "soft_requests"
SAMPLES = 5
LEVELS = SOFT_USERS


def plan(tasks=TASKS, samples=SAMPLES, tag="soft") -> list[dict]:
    labels = [t["label"] for t in P.serving()["targets"]]
    return [dict(key=f"{tag}|{t['id']}|{c}|{s}|{u}|{m}|{r}", set=tag, scenario=t["id"], context=c, scores=s,
                 user=u, model=m, rep=r, facts=t["facts"], **render(t, c, s, u))
            for t, c, s, u in itertools.product(tasks, CONTEXTS, SCORES, LEVELS)
            for m in labels for r in range(samples)]


def run_generate(items, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    P.OUT = out_dir  # P.generate writes to P.OUT / generations.jsonl and skips completed keys
    asyncio.run(P.generate(items, P.serving()))


def inspect():
    task = next(t for t in TASKS if t["id"] == "holiday_hours")  # a task with mid-range pilot uptake
    out = OUT / "inspection"
    run_generate(plan([task], 1, "inspect"), out)
    rows = [json.loads(l) for l in (out / "generations.jsonl").read_text().splitlines() if l.strip()]
    lines = ["# Soft-request inspection (holiday_hours, 1 sample per cell; not analysed)", ""]
    for r in sorted(rows, key=lambda r: (r["model"], r["user"], r["context"], r["scores"])):
        m = measures(r["reply"], task["facts"])
        lines += [f"## {r['model']} | {r['user']} | {r['context']} | {r['scores']}",
                  f"status={r['status']} · quirk={m['exact_quirk']} any_title={m['any_title']} complies={m['complies']} "
                  f"words={m['words']} facts_ok={m['facts_ok']}", "", "```text", r["reply"].strip(), "```", ""]
    (out / "outputs.md").write_text("\n".join(lines))
    print(f"inspection: {len(rows)} conversations -> {out / 'outputs.md'}")


def analyse(items):
    by_key = {i["key"]: i for i in items}
    rows = []
    for line in (OUT / "generations.jsonl").read_text().splitlines():
        g = json.loads(line)
        if g["key"] in by_key and g["status"] == "ok":
            rows.append(g | measures(g["reply"], by_key[g["key"]]["facts"]))
    labels = [t["label"] for t in P.serving()["targets"]]
    tasks = [t["id"] for t in TASKS]
    counts = {}
    for r in rows:
        c = counts.setdefault((r["model"], r["context"], r["scores"], r["user"], r["scenario"]), [0, 0])
        c[0] += r["exact_quirk"]
        c[1] += 1

    def rate(m, c, s, u, sample=None):
        k = n = 0
        for t in sample or tasks:
            h, x = counts.get((m, c, s, u, t), (0, 0))
            k, n = k + h, n + x
        return k / n if n else math.nan

    def boot(fn, n=2000):
        rng, vals = random.Random(0), []
        for _ in range(n):
            v = fn([rng.choice(tasks) for _ in tasks])
            if not math.isnan(v):
                vals.append(v)
        vals.sort()
        return [vals[int(0.025 * (len(vals) - 1))], vals[int(0.975 * (len(vals) - 1))]] if len(vals) > 50 else [math.nan] * 2

    pct = lambda x: "n/a" if math.isnan(x) else f"{100 * x:.0f}%"
    pp = lambda x: "n/a" if math.isnan(x) else f"{100 * x:+.0f} pp"
    L = ["# Soft-request follow-up (DISCOVERY): results", "",
         f"{len(rows)} ok conversations. Rule-based quirk adoption (bracketed title). 4 tasks × 5 samples per cell; "
         "intervals bootstrap over tasks (rough). Discovery only: confirm on fresh frozen tasks.", "",
         "## Quirk adoption: rewarded / penalised", "",
         "| Model | Request | " + " | ".join(CONTEXTS) + " |", "|---|---|" + "---|" * len(CONTEXTS)]
    for m in labels:
        for u in LEVELS:
            L.append(f"| {m} | {u} | " + " | ".join(
                f"{pct(rate(m, c, 'title_rewarded', u))} / {pct(rate(m, c, 'title_penalised', u))}" for c in CONTEXTS) + " |")
    L += ["", "## Context effect (titles rewarded, vs ordinary), amplification (rewarded − penalised, vs ordinary), "
          "and model interaction (3.8 − 3.5)", "", "| Request | Context | Effect 3.5 | Effect 3.8 | Interaction [95% CI] | "
          "Amplification diff [95% CI] |", "|---|---|---|---|---|---|"]
    a, b = labels
    results = {}
    for u in LEVELS:
        for c in CONTEXTS[1:]:
            E = lambda m, s=None: rate(m, c, "title_rewarded", u, s) - rate(m, "ordinary", "title_rewarded", u, s)
            S = lambda m, cc, s=None: rate(m, cc, "title_rewarded", u, s) - rate(m, cc, "title_penalised", u, s)
            A = lambda m, s=None: S(m, c, s) - S(m, "ordinary", s)
            inter, amp = E(b) - E(a), A(b) - A(a)
            ci_i, ci_a = boot(lambda s: E(b, s) - E(a, s)), boot(lambda s: A(b, s) - A(a, s))
            results[f"{u}|{c}"] = dict(effect={a: E(a), b: E(b)}, interaction=[inter, ci_i], amplification_diff=[amp, ci_a])
            L.append(f"| {u} | {c} | {pp(E(a))} | {pp(E(b))} | {pp(inter)} [{pp(ci_i[0])}, {pp(ci_i[1])}] | "
                     f"{pp(amp)} [{pp(ci_a[0])}, {pp(ci_a[1])}] |")
    L += ["", "## Per-task adoption, titles rewarded (k/5)", "", "| Model | Request | Context | " +
          " | ".join(tasks) + " |", "|---|---|---|" + "---|" * len(tasks)]
    for m, u, c in itertools.product(labels, LEVELS, CONTEXTS):
        L.append(f"| {m} | {u} | {c} | " + " | ".join(
            f"{counts.get((m, c, 'title_rewarded', u, t), [0, 0])[0]}/{counts.get((m, c, 'title_rewarded', u, t), [0, 0])[1]}"
            for t in tasks) + " |")
    status = {}
    for line in (OUT / "generations.jsonl").read_text().splitlines():
        g = json.loads(line)
        status[g["status"]] = status.get(g["status"], 0) + 1
    L += ["", f"Generation status: {status}. Other secondary measures (all rows): within_limit "
          f"{sum(r['within_limit'] for r in rows)}/{len(rows)}, facts_ok {sum(r['facts_ok'] for r in rows)}/{len(rows)}, "
          f"any title-like first line that is not the quirk {sum(r['any_title'] and not r['exact_quirk'] for r in rows)}."]
    (OUT / "results.json").write_text(json.dumps(results, indent=2, default=str))
    (OUT / "REPORT.md").write_text("\n".join(L) + "\n")
    print(f"Wrote {OUT / 'REPORT.md'}")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "inspect":
        return inspect()
    items, srv = plan(), P.serving()
    manifest = OUT / "manifest.json"
    if cmd == "freeze":
        OUT.mkdir(exist_ok=True)
        if manifest.exists():
            raise SystemExit("Already frozen; start a new, separately named run to change anything")
        manifest.write_text(json.dumps(dict(sha256=P.digest(items, srv), label="DISCOVERY (post-pilot)",
                                            at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                            samples=SAMPLES, levels=list(LEVELS), total=len(items), serving=srv),
                                       indent=2) + "\n")
        return print(f"Frozen {len(items)} conversations")
    if not manifest.exists() or json.loads(manifest.read_text())["sha256"] != P.digest(items, srv):
        raise SystemExit("Not frozen, or prompts/serving changed since freezing")
    if cmd == "generate":
        return run_generate(items, OUT)
    if cmd == "analyse":
        return analyse(items)
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
