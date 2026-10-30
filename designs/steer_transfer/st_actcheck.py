"""Downstream activation check (HF transformers, on a pod GPU; independent neutral prompts, no task prompts).

  PYTHONPATH=/workspace/grader-shifts-persona-space/src $ES_VENV/bin/python st_actcheck.py "Qwen 3.5"

Teacher-forces NEUTRAL_PROMPTS with and without the steering vector (strength x A_36 x unit, added with
gshift.hooks.add_to_residual = OUTPUT of block 35 = INPUT of block 36, the EasySteer layer-35 site) and reads the
last-prompt-token residual at layers 36 (injection site), 40, 48, 56. Per direction and sign at strength 0.3:
  * injected check at 36: cos(mean delta, sign x unit) ~ 1 and ||mean delta|| ~ 0.3 x A_36 (sign + scale + layer);
  * downstream: ||mean delta||, cos(mean delta_L, the model's natural auto-minus-human direction at L) (the natural
    directions are the Q1 analysis vectors; for Qwen 3.5 these are 3.5's own), compared with the random directions.
This says how the injected vector propagates in the target model. It is not evidence of semantic equivalence.
Writes run/checks/actcheck_<model>.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
NEUTRAL_PROMPTS = [
    "Explain how photosynthesis works.", "What are good habits for learning a language?",
    "Summarise the plot of a heist movie you invent.", "How do I convert Celsius to Fahrenheit?",
    "Give three tips for a job interview.", "Why is the sky blue?", "Describe a typical day of a lighthouse keeper.",
    "What is the difference between a list and a tuple in Python?", "Write a short poem about rain.",
    "How do vaccines train the immune system?", "Plan a three-day trip to Lisbon.", "What causes inflation?",
    "Explain recursion to a ten-year-old.", "What should I pack for a camping trip?",
    "How does a refrigerator keep food cold?", "Describe the rules of chess briefly.",
]
LAYERS = [36, 40, 48, 56]


def main(model_label: str):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    from gshift.hooks import add_to_residual, capture_residual
    sys.path.insert(0, str(HERE))
    from st_common import MODELS
    man = json.loads((HERE / "run/vectors/manifest.json").read_text())
    spec = MODELS[model_label]
    mm = man["models"][model_label]
    A = mm["activation_norm"]
    tok = AutoTokenizer.from_pretrained(spec["hf"], revision=spec["rev"])
    model = AutoModelForCausalLM.from_pretrained(spec["hf"], revision=spec["rev"], dtype=torch.bfloat16,
                                                 device_map="cuda:0")
    model.eval()
    texts = [tok.apply_chat_template([{"role": "user", "content": p}], add_generation_prompt=True, tokenize=False,
                                     **spec["chat_template_kwargs"]) for p in NEUTRAL_PROMPTS]
    ids = [list(tok(t, add_special_tokens=False)["input_ids"]) for t in texts]

    def read(hook_vec=None):
        out = []
        for i in ids:
            x = torch.tensor([i], device="cuda:0")
            with capture_residual(model, LAYERS) as st, torch.no_grad():
                if hook_vec is None:
                    model(x)
                else:
                    with add_to_residual(model, 36, hook_vec):
                        model(x)
            out.append(np.stack([st[L][0, -1].float().cpu().numpy() for L in LAYERS]))
        return np.stack(out).astype(np.float64)                                       # [N, nL, H]

    base = read()
    nat = {}
    for L in LAYERS:
        p = HERE / "run/vectors" / spec["key"] / f"natural_L{L}.npy"
        if p.exists():
            v = np.load(p).astype(np.float64)
            nat[L] = v / np.linalg.norm(v)
    res = dict(model=model_label, A_36=A, strength=0.3, layers=LAYERS, n_prompts=len(ids), directions={})
    for d in mm["directions"]:
        u = np.load(HERE / "run/vectors" / spec["key"] / f"{d}.npy").astype(np.float64)
        for sign in (1, -1):
            v = torch.tensor(sign * 0.3 * A * u, dtype=torch.float32)
            delta = (read(v) - base).mean(0)
            r = {"inj_cos_with_signed_unit": float(delta[0] @ (sign * u) / np.linalg.norm(delta[0])),
                 "inj_norm": float(np.linalg.norm(delta[0])), "expected_norm": 0.3 * A}
            for li, L in enumerate(LAYERS[1:], 1):
                r[f"L{L}_norm"] = float(np.linalg.norm(delta[li]))
                r[f"L{L}_rel_to_base_norm"] = float(np.linalg.norm(delta[li]) / np.linalg.norm(base[:, li], axis=1).mean())
                if L in nat:
                    r[f"L{L}_cos_natural"] = float(delta[li] @ nat[L] / np.linalg.norm(delta[li]))
            res["directions"][f"{d}_{'+' if sign > 0 else '-'}0.3"] = r
            print(d, sign, {k: round(x, 3) for k, x in r.items()}, flush=True)
    (HERE / "run/checks").mkdir(parents=True, exist_ok=True)
    (HERE / "run/checks" / f"actcheck_{spec['key']}.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
