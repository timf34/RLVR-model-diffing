"""Steering transfer (Qwen 3.8 grader direction -> Qwen 3.5): shared constants and the condition grid.

Frozen in PLAN.md before any steered generation. Stdlib only (numpy where vectors are read).
The episode loop, materials, renderer and scorers are the presentation ablation's, imported read-only.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                                   # model-diffing-agent
PA = ROOT / "designs" / "presentation_ablation"
GS = ROOT.parent / "grader-shifts-persona-space"         # vectors + activation norms (read-only)
RUN = HERE / "run"
sys.path[:0] = [str(PA)]

LAYER = 36                    # our layer L = residual input of decoder block 36 = EasySteer output of block 35
EASYSTEER_LAYER = LAYER - 1

MODELS = {
    "Qwen 3.5": dict(key="qwen3.5-27b", hf="Qwen/Qwen3.5-27B", rev="fc05daec18b0a78c049392ed2e771dde82bdf654",
                     chat_template_kwargs={}),
    "Qwen 3.8": dict(key="qwen3.8-27b", hf="Qwen/Qwen3.8-27B", rev="1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0",
                     chat_template_kwargs={"reasoning_effort": "medium"}),
}

# unit directions (built by st_vectors.py into run/vectors/<model>/<name>.npy + .gguf)
DIRECTIONS = {
    "Qwen 3.5": {
        "xfer": "qwen3.8-27b/analysis/vectors/original_pre_L36_auto_minus_human.npy",    # direct coordinate transfer
        "native": "qwen3.5-27b/analysis/vectors/original_pre_L36_auto_minus_human.npy",  # 3.5's own direction
        "random0": "random seed 20261030 #0",
        "random1": "random seed 20261030 #1",
    },
    "Qwen 3.8": {
        "native": "qwen3.8-27b/analysis/vectors/original_pre_L36_auto_minus_human.npy",  # source-model control
    },
}
RANDOM_SEED = 20261030
STRENGTHS = (0.1, 0.3)        # Stage A's fixed strengths; applied = s x A_L(target model) x unit
RANDOM_STRENGTH = 0.3


def conditions(model: str) -> list[str]:
    out = ["none"]
    for d in DIRECTIONS[model]:
        ss = (RANDOM_STRENGTH,) if d.startswith("random") else STRENGTHS
        for s in ss:
            out += [f"{d}_+{s:g}", f"{d}_-{s:g}"]
    return out


def parse_condition(c: str) -> tuple[str | None, float]:
    if c == "none":
        return None, 0.0
    d, s = c.rsplit("_", 1)
    return d, float(s)


# score arms: (gap g passed to the renderer; conflicting record score, requested record score)
#   conflict: 0.750 / 0.250 (the ablation's p050), reversed: 0.250 / 0.750 (numbers swapped only),
#   tied: 0.500 / 0.500, nohist: no scored records shown (competence control)
SCORE_ARMS = {"conflict": 0.5, "reversed": -0.5, "tied": 0.0, "nohist": None}
ARM = "B"                     # the old bundle presentation (all components at the bundle level)
MATERIALS = ("orig", "fresh")
REPS = 4

# generation: the presentation ablation's serving settings (pa_common + experiment.grading.3way.json)
TEMPERATURE, TOP_P, TOP_K, MAX_TOKENS = 0.7, 0.95, 20, 32768
MAX_STEPS = 8


def sha(b: bytes | str) -> str:
    return hashlib.sha256(b.encode() if isinstance(b, str) else b).hexdigest()


def jhash(obj) -> str:
    return sha(json.dumps(obj, sort_keys=True, ensure_ascii=False))


def iter_jsonl(p: Path):
    if not Path(p).exists():
        return
    with open(p) as f:
        for line in f:
            if line.strip():
                yield json.loads(line)
