"""Serving for the overnight batch: experiment.grading.3way.json targets Qwen 3.5 and Qwen 3.8 (Qwen 3.6 dropped).

Qwen 3.5  openrouter/qwen/qwen3.5-27b, provider only novita/bf16, no fallbacks, default thinking
Qwen 3.8  openrouter/qwen/qwen3.8-27b, provider only deepinfra/bf16, no fallbacks, reasoning_effort medium
both      temperature 0.7, top_p 0.95, top_k 20 (extra_body), max_tokens 32768, 1200 s per call (asyncio.wait_for)
GenerateConfig is built by src/model_diffing/petri_task.generation_config (imported read-only) and merged with
max_connections=<concurrency>, because Inspect otherwise caps every model at 10 connections (pitfall 1).
"""
from __future__ import annotations

import json
import sys

from .blocks import ROOT
from .items import MODELS

SERVING_CONFIG = ROOT / "experiment.grading.3way.json"
MAX_TOKENS, TIMEOUT, TEMPERATURE = 32768, 1200, 0.7
EXPECTED = {
    "Qwen 3.5": dict(model="openrouter/qwen/qwen3.5-27b",
                     model_args={"provider": {"only": ["novita/bf16"], "allow_fallbacks": False}}),
    "Qwen 3.8": dict(model="openrouter/qwen/qwen3.8-27b",
                     model_args={"provider": {"only": ["deepinfra/bf16"], "allow_fallbacks": False}},
                     generate={"reasoning_effort": "medium"}),
}


def serving() -> dict:
    s = json.loads(SERVING_CONFIG.read_text())
    targets = [{k: v for k, v in t.items() if k != "serving_note"} for t in s["targets"] if t["label"] in MODELS]
    for t in targets:
        exp = EXPECTED[t["label"]]
        assert t["model"] == exp["model"] and t["model_args"] == exp["model_args"], t
        assert t.get("generate", {}) == exp.get("generate", {}), t
    assert s["target_generate"] == {"top_p": 0.95, "extra_body": {"top_k": 20}}
    return dict(targets=targets, target_generate=s["target_generate"], temperature=TEMPERATURE,
                target_max_tokens=MAX_TOKENS, timeout=TIMEOUT)


def generate_config(label: str, concurrency: int):
    if str(ROOT / "src") not in sys.path:
        sys.path.insert(0, str(ROOT / "src"))
    from model_diffing.petri_task import generation_config
    srv = serving()
    t = next(t for t in srv["targets"] if t["label"] == label)
    cfg = generation_config(srv, t)
    cfg = cfg.merge(type(cfg)(max_connections=concurrency))
    assert cfg.max_tokens == MAX_TOKENS and cfg.temperature == TEMPERATURE and cfg.top_p == 0.95
    assert cfg.extra_body == {"top_k": 20} and cfg.max_connections == concurrency
    assert cfg.reasoning_effort == EXPECTED[label].get("generate", {}).get("reasoning_effort")
    return cfg


def get_target(label: str, concurrency: int):
    """(inspect Model, GenerateConfig). Loads .env (never printed)."""
    from dotenv import load_dotenv
    from inspect_ai.model import get_model
    load_dotenv(ROOT / ".env")
    t = next(t for t in serving()["targets"] if t["label"] == label)
    return get_model(t["model"], **t.get("model_args", {})), generate_config(label, concurrency)
