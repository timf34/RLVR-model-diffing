# Bloom side experiment: evaluator over user

Open-ended exploration with [Petri Bloom](https://meridianlabs-ai.github.io/petri_bloom) (v0.2.6):
when does a model give up a clear user preference to satisfy an evaluator, and does
this differ between Qwen 3.5 27B and Qwen 3.8 27B?

This folder has its own venv (`uv venv .venv && uv pip install petri-bloom`) so it
doesn't touch the main project's dependencies.

## Files

- `evaluator_over_user/BEHAVIOR.md`: the behaviour definition. Holds the brief, scenario
  families, judge guidance, and three variation axes that implement the checks:
  - `incentive_reversed`: does the behaviour track the evaluator signal?
  - `requirement_clarified`: does it survive removing ambiguity?
  - `ordinary_framing`: framing effect or baseline difference?
- `evaluator_over_user/scenarios/`: Bloom's generated output (12 base seeds × 3
  variations = 48 seeds, plus the judge rubric in `dimensions/`). Edit or delete seeds freely.
- `gen_scenarios.py`: regenerates scenarios with Sonnet 5.5.
- `run_audit.py`: runs every seed against both Qwen targets (same auditor, judge, seeds).
- `compare.py`: per-scenario and per-axis score comparison → `logs/<run>/COMPARE.md`.

## Commands

```sh
.venv/bin/python gen_scenarios.py ./evaluator_over_user --overwrite
~/.claude/bin/memguard -m 6 -- .venv/bin/python run_audit.py ./evaluator_over_user --epochs 1 --log-dir logs/run1
.venv/bin/python compare.py logs/run1
.venv/bin/inspect view --log-dir logs/run1
```

## Setup decisions

- **Model diffing.** Bloom evaluates one target at a time. Running it once per target
  on the same seeds, then comparing judge scores per seed, is enough for exploration.
- **Comparable rollouts.** The auditor is adaptive, so conversations differ between
  targets. `instructions.evaluation` tells it to use the same system prompt and opening
  request and not to escalate. Check transcripts before trusting a gap.
- **Sonnet 5.5 workaround.** Sonnet/Opus 5.5 reject forced tool calls. `gen_scenarios.py`
  sends `tool_choice="auto"` instead. The auditor and judge don't force tools, so they're unaffected.
- **Same targets as the main repo.** Same models, providers and sampling as
  `experiment.grading.35v38.json` (Qwen 3.8 at reasoning effort medium).
- **Conversation modality only.** Simulated tool scenarios (`modality: agent`) are a
  possible second run. Claims about real code execution belong in the Docker environments.

## Caveats

- The judge sees the targets' reasoning. That's useful evidence, but it means judge
  scores are not the visible-text-only view used by the main agent.
- Variation seeds are not linked to their base seed in Bloom's output. `compare.py`
  groups by axis. Pair them by reading the SETTING text.
- One judge score per sample from an LLM judge is noisy. Treat gaps as leads to rerun
  with more epochs, or to port into the main agent or a fixed-script batch.
