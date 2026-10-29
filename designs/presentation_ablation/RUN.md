# How to run (local, in order)

All commands from the repo root, with the repo `.venv`. **One heavy job at a time, always under memguard.** Nothing
here prints `.env`; generation reads `OPENROUTER_API_KEY` from it via python-dotenv. The inputs for `smoke` and `main`
are already prepared and `main` is frozen (`designs/presentation_ablation/run/main/manifest.json`).

```bash
git fetch origin presentation-ablation && git checkout presentation-ablation
```

## 0. Offline checks (no API calls, about 3 min)

```bash
~/.claude/bin/memguard -m 4 -- .venv/bin/python designs/presentation_ablation/pa_tests.py
```

All tests should PASS: byte identity of the reference arm and of 10A's inputs, one-component diffs for every arm,
identical scores, plan counts, freeze tamper detection, the offline driver (scripted model), and the analysis on
simulated data. Then confirm the frozen inputs are untouched:

```bash
~/.claude/bin/memguard -m 4 -- .venv/bin/python designs/presentation_ablation/pa_freeze.py verify main
```

## 1. Smoke (32 episodes on the old inspection-only scenarios, about $0.10, a few minutes)

```bash
~/.claude/bin/memguard -m 4 -- .venv/bin/python designs/presentation_ablation/pa_generate.py smoke
```

```bash
~/.claude/bin/memguard -m 4 -- .venv/bin/python designs/presentation_ablation/pa_score.py send --stage smoke
```

```bash
~/.claude/bin/memguard -m 4 -- .venv/bin/python designs/presentation_ablation/pa_score.py fmt --stage smoke
```

```bash
.venv/bin/python designs/presentation_ablation/pa_generate.py status smoke
```

Check: every record `ok` (no errors), and `scored.jsonl` rows `valid`. The smoke blocks are not main blocks, so
looking at their replies does not touch main outcomes.

## 2. Full run (main = Part 1 + Part 2, interleaved; see COST.md)

```bash
~/.claude/bin/memguard -m 4 -- .venv/bin/python designs/presentation_ablation/pa_generate.py main
```

- Resumable: if it stops (time, budget, crash, laptop sleep), run the same command again; done keys are skipped and
  errored ones retried (at most 3 records per key).
- Stops: `--minutes 600` wall clock, `--budget-stop 40` dollars (ledger over all stages + in-flight estimate).
- Lower the load if needed: `--concurrency 8` (per model; default 16). Run one task only: `--task send`.
- Progress and spend:

```bash
.venv/bin/python designs/presentation_ablation/pa_generate.py status main
```

## 3. Score (rule-based, old scorers; one kind per process)

```bash
~/.claude/bin/memguard -m 4 -- .venv/bin/python designs/presentation_ablation/pa_score.py send
```

```bash
~/.claude/bin/memguard -m 4 -- .venv/bin/python designs/presentation_ablation/pa_score.py fmt
```

## 4. Judge

Not needed: every outcome is rule-based (send log; bracketed title / fixed sign-off; >= 2 list lines), exactly as
in the old studies and 10A.

## 5. Analyse and figures

```bash
~/.claude/bin/memguard -m 4 -- .venv/bin/python designs/presentation_ablation/pa_analysis.py analyse
```

```bash
~/.claude/bin/memguard -m 4 -- .venv/bin/python designs/presentation_ablation/pa_figures.py
```

Outputs: `run/main/results.json`, `run/main/REPORT_auto.md`, `figure/part1_cells.{png,svg}`,
`figure/part2_components.{png,svg}`. The analysis takes a few minutes (20,000 sign flips per contrast).

## 6. Optional, gated: factorial stage (off by default)

Only after reading the main results. The selection rule is frozen in PROTOCOL.md.

```bash
.venv/bin/python designs/presentation_ablation/pa_analysis.py select
```

This writes `run/factorial/selection.json` with `enabled: false`. To run it, write a short protocol addendum, then:

```bash
.venv/bin/python designs/presentation_ablation/pa_analysis.py select --enable
```

```bash
.venv/bin/python designs/presentation_ablation/pa_prepare.py send --stage factorial
```

```bash
.venv/bin/python designs/presentation_ablation/pa_prepare.py fmt --stage factorial
```

```bash
.venv/bin/python designs/presentation_ablation/pa_freeze.py freeze factorial
```

```bash
~/.claude/bin/memguard -m 4 -- .venv/bin/python designs/presentation_ablation/pa_generate.py factorial
```

Then `pa_score.py send|fmt --stage factorial`. The factorial analysis is not part of the frozen main analysis.

## If you change anything before running

Re-prepare and re-freeze (this records a new freeze time; note it as a deviation):

```bash
.venv/bin/python designs/presentation_ablation/pa_prepare.py send
```

```bash
.venv/bin/python designs/presentation_ablation/pa_prepare.py fmt
```

```bash
.venv/bin/python designs/presentation_ablation/pa_freeze.py freeze main
```
