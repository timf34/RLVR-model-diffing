# Black-box model-diffing agent

A small research harness built on **Inspect Petri's actual auditor loop and audit solver**, inspired by Diffscope's paired investigation design. Supports **two or more targets**, with named models by default and optional anonymisation. The example configuration has labels for Qwen 3.5, 3.6 and 3.8; endpoint identifiers intentionally remain placeholders.

## First implementation

- One investigator probes all targets on identical user scripts.
- Multi-turn probes retain each model's own replies; no invented assistant prefills.
- Context probes cross every model with baseline/modified system-context conditions.
- Repeated samples, bounded concurrency, timeouts and hard target-call budgets.
- Explicit text-only extraction excludes structured reasoning blocks and model metadata from investigator-visible results.
- A separate validator receives the hypothesis and frozen scoring rule, without discovery transcripts. Exact discovery prompts cannot be reused as validation evidence.
- Reports contain probe IDs, complete visible response records, provisional verdicts and model mappings in Inspect sample metadata.
- Errors and incomplete generations cannot count as positive behavioural evidence.

## Setup

Python 3.12+ and uv:

```sh
uv sync
cp experiment.example.json experiment.json
# Edit experiment.json with exact Inspect provider/model IDs.
# Configure API credentials using your provider's environment variables.
uv run model-diff experiment.json --log-dir logs
uv run inspect view --log-dir logs
```

To use the user's reference checkout instead of the published Petri package, after syncing:

```sh
uv pip install -e ./inspect_petri
```

The sibling `inspect_petri/` and `diffscope/` clones are references and are not modified by this project. This implementation uses public Petri exports rather than copying their source.

Each target is configured as `{"label": "Qwen 3.5", "model": "provider/exact-model-id"}`. Add or remove targets freely (minimum two). Labeling does not imply verified model lineage, size or RLVR training dose. Use `"blind": true` for repeatable shuffled generic labels; mappings are still available to the researcher in logs. Self-identification in the model's visible answer is not redacted.

The auditor and validator may use the same model with separate contexts, or different models. Keep target providers, generation settings and system framing comparable. The current version applies one shared temperature and output token limit to all targets. API response caching is disabled so repetitions are separate generations.

## Investigation and validation

The custom Petri auditor exposes three experiment/report operations plus termination:

1. `probe_models(turns, samples)` runs a shared user script on every target.
2. `test_context(turns, context, samples)` crosses that script with baseline and modified system context.
3. `submit_hypothesis(...)` records an operational scoring rule, predictions and discovery evidence IDs.
4. `end_conversation()` stops discovery.

The separate validator gets the same probing tools and `submit_verdict(...)`. It can report **supported**, **rejected**, or **inconclusive**. A supported verdict must cite at least two distinct fresh scripts with at least three repetitions each. This is a minimum evidence gate, **not a statistical significance test**. Counts and judgments are currently LLM-authored, and should be reviewed against the recorded transcripts.

Inspect's target role is required by Petri's solver; we bind it to the first configured model. Petri's ordinary target coroutine waits while our custom experiment tools query all models using Inspect's provider API. Our tools replace Petri's default target-control tools and prompts. This first version therefore uses Petri's auditor lifecycle and logging, but **does not yet expose its simulated target tools or branching/rollback features**.

## Cost bounds

A probe reserves:

```
models × repetitions × user turns × conditions
```

A context probe with three models, three repetitions and two user turns reserves 36 target calls. Discovery has its own cap, and every accepted hypothesis gets a separate validation cap. Calls are reserved before parallel execution; early failures do not refund reservations. Auditor/validator calls are bounded by their stage turn counts, not the target-call cap. These are call limits, not dollar limits.

## Black-box boundary

The investigator and validator receive only visible assistant text. No weights, activations, gradients, log-probabilities or structured reasoning content are exposed to them. The targets receive their own genuine previous visible answers. The default prompts explicitly prohibit requesting hidden reasoning.

Inspect's researcher-facing raw provider logs can still contain provider-returned reasoning and model names; they are **not passed to the investigator or validator**. Providers that embed reasoning directly in ordinary answer text rather than a separate content block require an additional provider-specific adapter before claiming a strict no-reasoning view.

## Tests

The experiment engine has no third-party dependencies:

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

With Petri installed, the same suite also runs a no-API-key mock integration test and a reasoning-filter adapter test:

```sh
uv run python -m unittest discover -s tests -v
```

## Current verification and limitations

Nine engine tests passed during initial implementation. Two integration tests are included but could not run in the authoring environment: dependency installation failed due to DNS/network restrictions. Syntax compilation passed. No paid API calls or live Qwen investigations have run. Treat the Petri integration as awaiting its first installed-dependency smoke test.

Validation rejects exact reused scripts, but semantic overlap and true held-out task-family independence still need human review. Context effects do not establish the existence of internal personas, or attribute a difference to RLVR. Independent validation does not by itself correct multiple comparisons from adaptive discovery. Identical-model tests here verify the engine, not the investigator's empirical false-positive rate.

Next research checks: run identical-model investigations, recover planted conditional differences, compare blind/named runs, and quantify validated findings per fixed query budget. Add a deterministic scoring interface and held-out scenario banks before making statistical claims. Tool-using target environments can follow after the text-only loop is validated.

## References

- Inspect Petri: https://github.com/meridianlabs-ai/inspect_petri
- Diffscope (archived reference implementation): https://github.com/dtch1997/diffscope
- Chughtai, Engels and Nanda: https://www.lesswrong.com/posts/qi4mNbZYAFDYwfRba/building-and-evaluating-model-diffing-agents
