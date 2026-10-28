"""Run one Bloom behaviour against each Qwen target with the same seeds.

Each target gets its own Inspect task (same scenarios, auditor and judge), so
per-scenario judge scores can be compared afterwards with compare.py.

Usage:
  python run_audit.py ./evaluator_over_user --limit 2 --epochs 1
  python run_audit.py ./evaluator_over_user --epochs 3
"""

import argparse

from dotenv import load_dotenv
from inspect_ai import eval, task_with
from inspect_ai.model import GenerateConfig, get_model
from petri_bloom import bloom_audit

load_dotenv("../.env")

ANTHROPIC = {"provider": {"only": ["anthropic"], "allow_fallbacks": False}}
# Same targets, providers and sampling settings as experiment.grading.35v38.json.
QWEN_SAMPLING = dict(temperature=0.7, top_p=0.95, max_tokens=8192, extra_body={"top_k": 20})
TARGETS = {
    "qwen35_27b": dict(
        model="openrouter/qwen/qwen3.5-27b",
        provider={"only": ["novita/bf16"], "allow_fallbacks": False},
        config=GenerateConfig(**QWEN_SAMPLING),
    ),
    "qwen38_27b": dict(
        model="openrouter/qwen/qwen3.8-27b",
        provider={"only": ["deepinfra/bf16"], "allow_fallbacks": False},
        config=GenerateConfig(**QWEN_SAMPLING, reasoning_effort="medium"),
    ),
}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("behavior")
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--sample-id", action="append", default=None)
    p.add_argument("--epochs", type=int, default=1)
    p.add_argument("--max-turns", type=int, default=8)
    p.add_argument("--max-samples", type=int, default=6)
    p.add_argument("--log-dir", default="logs")
    p.add_argument("--auditor", default="openrouter/anthropic/claude-sonnet-5.5")
    p.add_argument("--judge", default="openrouter/anthropic/claude-sonnet-5.5")
    args = p.parse_args()

    auditor = get_model(args.auditor, **ANTHROPIC)
    judge = get_model(args.judge, **ANTHROPIC)

    tasks = []
    for name, t in TARGETS.items():
        target = get_model(t["model"], config=t["config"], provider=t["provider"])
        tasks.append(
            task_with(
                bloom_audit(behavior=args.behavior, max_turns=args.max_turns),
                name=f"bloom_{name}",
                model_roles={"auditor": auditor, "target": target, "judge": judge},
                epochs=args.epochs,
            )
        )

    eval(
        tasks,
        model=auditor,
        limit=args.limit,
        sample_id=args.sample_id,
        max_samples=args.max_samples,
        max_tasks=len(tasks),
        log_dir=args.log_dir,
        cache_prompt=False,
        display="plain",
    )


if __name__ == "__main__":
    main()
