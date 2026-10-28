"""Serving settings shared by all four experiments (adapted from designs/action/run.py; targets pinned in
experiment.grading.3way.json). Import as `from action_mechanisms.shared import serving`."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SERVING_CONFIG = ROOT / "experiment.grading.3way.json"
MAX_TOKENS = 32768          # per turn, same cap for every model (Qwen 3.6 reasons for a long time)
TIMEOUT = 1200              # seconds per model call
TEMPERATURE = 0.7
JUDGE_MODEL = "openrouter/anthropic/claude-sonnet-5.5"
JUDGE_ARGS = {"provider": {"only": ["anthropic"], "allow_fallbacks": False}}
SERVING_NOTES = {
    "Qwen 3.5": "novita/bf16; default thinking (no reasoning_effort parameter on any 3.5 host)",
    "Qwen 3.6": "alibaba (first-party; precision not stated; no bf16 host on OpenRouter); default thinking",
    "Qwen 3.8": "deepinfra/bf16; reasoning_effort=medium",
}
# Listed OpenRouter prices, $ per million tokens (input, output). Used for cost estimates only.
PRICES = {"Qwen 3.5": (0.26, 2.6), "Qwen 3.6": (0.45, 2.7), "Qwen 3.8": (0.039, 1.25), "judge": (2.0, 10.0)}
# One shared per-provider budget across ALL experiments and processes (enforced by limiter.py).
CAPS = {"Qwen 3.5": 48, "Qwen 3.6": 64, "Qwen 3.8": 48, "judge": 32}


def serving() -> dict:
    s = json.loads(SERVING_CONFIG.read_text())
    targets = [{k: v for k, v in t.items() if k != "serving_note"} for t in s["targets"]]
    return dict(targets=targets, target_generate=s["target_generate"], temperature=TEMPERATURE,
                target_max_tokens=MAX_TOKENS, timeout=TIMEOUT, judge=JUDGE_MODEL, judge_args=JUDGE_ARGS)


def labels() -> list[str]:
    return [t["label"] for t in serving()["targets"]]


def get_target(label: str):
    """(inspect Model, GenerateConfig) for a target label."""
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    from dotenv import load_dotenv
    from inspect_ai.model import get_model

    from model_diffing.petri_task import generation_config
    load_dotenv(ROOT / ".env")
    srv = serving()
    t = next(t for t in srv["targets"] if t["label"] == label)
    cfg = generation_config(srv, t)
    cfg = cfg.merge(type(cfg)(max_connections=CAPS[label]))  # never let inspect's default throttle below the cap
    return get_model(t["model"], **t.get("model_args", {})), cfg


def get_judge():
    from dotenv import load_dotenv
    from inspect_ai.model import get_model
    load_dotenv(ROOT / ".env")
    return get_model(JUDGE_MODEL, **JUDGE_ARGS)


def cost(usage: dict, label: str) -> float:
    pin, pout = PRICES.get(label, (0, 0))
    return (usage.get("input_tokens") or 0) * pin / 1e6 + (usage.get("output_tokens") or 0) * pout / 1e6
