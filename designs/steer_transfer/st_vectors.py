"""Build the steering set: unit vectors + EasySteer GGUF payloads + manifest with applied scales.

  .venv/bin/python designs/steer_transfer/st_vectors.py      # -> run/vectors/{manifest.json, <model>/<dir>.npy|.gguf}

applied vector = signed strength x A_L(TARGET model) x unit(direction), at our layer 36 (= EasySteer layer 35).
A_L is the target model's mean residual norm at layer 36 from its Betley-reproduction extraction
(grader-shifts-persona-space outputs/<model>/betley_repro/report.json, per_layer_mean_activation_norm[36]): the
prompts are Betley et al.'s contrast prompts, separate from the sending task. Same estimator as Stage A.
Random directions: isotropic normal, seed 20261030, unit norm, so norm-matched to every other direction.
Source vector files are only read (sha256 recorded).
"""
from __future__ import annotations

import json

import numpy as np

from st_common import DIRECTIONS, EASYSTEER_LAYER, GS, LAYER, MODELS, RANDOM_SEED, RUN, sha

OUT = RUN / "vectors"


def activation_norm(key: str) -> float:
    r = json.loads((GS / "outputs" / key / "betley_repro" / "report.json").read_text())
    return float(r["per_layer_mean_activation_norm"][LAYER])


def write_gguf(unit: np.ndarray, path) -> None:
    import gguf  # same layout as gshift.steer.engine.write_direction_gguf
    w = gguf.GGUFWriter(str(path), arch="steer")
    w.add_tensor(f"direction.{EASYSTEER_LAYER}", np.asarray(unit, dtype=np.float32).reshape(-1))
    w.write_header_to_file()
    w.write_kv_data_to_file()
    w.write_tensors_to_file()
    w.close()


def build() -> dict:
    man = dict(layer=LAYER, easysteer_layer=EASYSTEER_LAYER,
               convention="our layer L = residual input of block L = EasySteer output of block L-1",
               formula="applied = signed_strength * A_L(target) * unit(direction); prompt and generated tokens",
               models={})
    rng = np.random.default_rng(RANDOM_SEED)
    rand = [rng.normal(size=5120) for _ in range(2)]
    for model, spec in MODELS.items():
        d = OUT / spec["key"]
        d.mkdir(parents=True, exist_ok=True)
        m = dict(activation_norm=activation_norm(spec["key"]),
                 activation_norm_source=f"{spec['key']}/betley_repro/report.json per_layer_mean_activation_norm[36]",
                 directions={})
        units = {}
        for name, src in DIRECTIONS[model].items():
            if name.startswith("random"):
                v = rand[int(name[-1])]
                info = dict(source=src)
            else:
                p = GS / "outputs" / src
                raw = np.load(p)
                assert raw.shape == (5120,) and np.isfinite(raw).all(), (p, raw.shape)
                v = raw.astype(np.float64)
                info = dict(source=src, file_sha256=sha(p.read_bytes()), raw_norm=float(np.linalg.norm(v)),
                            dtype=str(raw.dtype))
            u = (v / np.linalg.norm(v)).astype(np.float32)
            units[name] = u
            np.save(d / f"{name}.npy", u)
            write_gguf(u, d / f"{name}.gguf")
            info.update(unit_sha256=sha(u.tobytes()), gguf=f"{spec['key']}/{name}.gguf")
            m["directions"][name] = info
        names = list(units)
        U = np.stack([units[n] for n in names]).astype(np.float64)
        m["cosine"] = dict(names=names, cos=(U @ U.T).round(4).tolist())
        man["models"][model] = m
    # Stage A consistency: the 3.8 source is the vector Stage A steered with (its stored unit vector)
    stage_a = np.load(GS / "outputs/qwen3.8-27b/steering/vectors/auto_human.npy").astype(np.float64)
    x = np.load(OUT / "qwen3.5-27b" / "xfer.npy").astype(np.float64)
    man["xfer_vs_stage_a_auto_human_cos"] = float(x @ stage_a / np.linalg.norm(stage_a))
    sa = json.loads((GS / "outputs/qwen3.8-27b/steering/vectors.json").read_text())
    man["stage_a_auto_human_source"] = sa["directions"]["auto_human"]["source"]
    man["stage_a_activation_norm_3.8"] = sa["activation_norm"]
    assert abs(man["xfer_vs_stage_a_auto_human_cos"] - 1) < 1e-5
    assert abs(sa["activation_norm"] - man["models"]["Qwen 3.8"]["activation_norm"]) < 1e-9
    (OUT / "manifest.json").write_text(json.dumps(man, indent=1))
    return man


def scale(man: dict, model: str, direction: str, signed_strength: float) -> float:
    return float(signed_strength) * man["models"][model]["activation_norm"]


if __name__ == "__main__":
    m = build()
    for model, mm in m["models"].items():
        print(model, "A_36 =", round(mm["activation_norm"], 3), "cos:", mm["cosine"])
    print("xfer == Stage A auto_human:", m["xfer_vs_stage_a_auto_human_cos"])
