"""Steering transfer on the scored-example formatting tasks: constants and the condition grid.

Reuses designs/steer_transfer unchanged: its vectors (run/vectors/manifest.json + GGUFs), its condition naming and
steering spec (st_generate.steering_extra), and the presentation ablation's renderer, materials, episode loop and
rule-based formatting scorers (read-only imports). Frozen in PLAN.md before any steered generation.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PA = ROOT / "designs" / "presentation_ablation"
ST = ROOT / "designs" / "steer_transfer"
RUN = HERE / "run"
MOCK = HERE / "run_mock"            # synthetic data only (tests); never mixed with run/
sys.path[:0] = [str(PA), str(ST)]

from st_common import (MODELS, RANDOM_STRENGTH, STRENGTHS,  # noqa: E402,F401
                       iter_jsonl, jhash, parse_condition, sha)

# Directions per TARGET model (reverse-transfer revision, PLAN.md): every target gets unsteered, its own direction
# (`native`), the other model's direction (`xfer`) and the two seed-20261030 random directions. GGUFs live in
# designs/steer_transfer/run/vectors/<target>/<name>.gguf (3.8's xfer/random from st_reverse_vectors.py); the applied
# scale is always strength x A_36(TARGET) (st_generate.steering_extra).
DIRECTIONS = {m: ("xfer", "native", "random0", "random1") for m in MODELS}


def conditions(model: str) -> list[str]:
    out = ["none"]
    for d in DIRECTIONS[model]:
        for s in ((RANDOM_STRENGTH,) if d.startswith("random") else STRENGTHS):
            out += [f"{d}_+{s:g}", f"{d}_-{s:g}"]
    return out

# Task families. A family = one formatting feature; titles and sign-offs share scenarios (the archived "titles" task
# has two subs) but are DIFFERENT features and are analysed separately, never pooled into one headline.
#   key: (presentation-ablation task, sub or None)
FAMILIES = {
    "title": ("titles", "title"),       # bracketed title line, e.g. "[Quiz night: Thursday]"
    "signoff": ("titles", "signoff"),   # fixed team sign-off last line, e.g. "— Events Team"
    "bullets": ("bullets", None),       # >=2 bullet / numbered lines
}
MATERIALS = ("orig", "fresh")           # every archived arm-B block: titles 6+16 scenarios, bullets 6+32
ARM = "B"                               # old bundle presentation = the primary replication (as in steer_transfer)

# Same score arms as steer_transfer. g = gap passed to the renderer: featured (user-dispreferred, score-favoured)
# record score 0.5+g/2, plain (requested) record 0.5-g/2.
SCORE_ARMS = {"conflict": 0.5, "reversed": -0.5, "tied": 0.0, "nohist": None}

# Samples per scenario per cell (prespecified; PLAN.md "Sample size"). Distinct scenarios: title 22, signoff 22,
# bullets 38. Full design ~176-190 generations per cell; reduced design halves the reps.
REPS = {"full": {"title": 8, "signoff": 8, "bullets": 5},
        "reduced": {"title": 4, "signoff": 4, "bullets": 3}}

# Generation: identical to the presentation ablation / steer_transfer (temperature 0.7, top_p 0.95, top_k 20,
# max_tokens 32768; Qwen 3.8 reasoning_effort=medium); text tasks: one model call (MAX_STEPS 3 as archived).
MAX_STEPS = 3
