"""Reverse transfer vectors: Qwen 3.5's direction (and the random controls) as payloads for Qwen 3.8.

  ../grader-shifts-persona-space/.venv/bin/python designs/steer_transfer/st_reverse_vectors.py   # needs gguf

Adds files only (never rewrites run/vectors/manifest.json or any existing vector):
  run/vectors/qwen3.8-27b/xfer.{npy,gguf}     = unit(qwen3.5-27b original_pre_L36_auto_minus_human), the SAME unit
                                                vector as run/vectors/qwen3.5-27b/native.npy (asserted)
  run/vectors/qwen3.8-27b/random{0,1}.{npy,gguf} = the SAME seed-20261030 unit vectors used on 3.5 (asserted)
  run/vectors/reverse_manifest.json            = provenance, sha256s, dims, cosines, target scaling
Applied on 3.8 = signed strength x A_36(Qwen 3.8) = x 52.256 (3.8's own norm, NOT 3.5's), our layer 36 = EasySteer
layer 35, prompt + generated tokens: st_generate.steering_extra picks the TARGET model's norm and GGUF directory.
"""
from __future__ import annotations

import json

import numpy as np

from st_common import GS, RUN, sha
from st_vectors import write_gguf

V = RUN / "vectors"


def main():
    man = json.loads((V / "manifest.json").read_text())
    src = GS / "outputs/qwen3.5-27b/analysis/vectors/original_pre_L36_auto_minus_human.npy"
    raw = np.load(src)
    assert raw.shape == (5120,) and np.isfinite(raw).all() and raw.dtype == np.float32
    v = raw.astype(np.float64)
    u = (v / np.linalg.norm(v)).astype(np.float32)          # st_vectors' exact construction
    n35 = np.load(V / "qwen3.5-27b/native.npy")
    assert np.array_equal(u, n35), "3.5 source unit vector differs from the one steered on 3.5"
    u = n35                                                   # use the very file that was steered on 3.5
    assert sha(src.read_bytes()) == man["models"]["Qwen 3.5"]["directions"]["native"]["file_sha256"]
    out = V / "qwen3.8-27b"
    units = {"xfer": u}
    for k in ("random0", "random1"):
        units[k] = np.load(V / "qwen3.5-27b" / f"{k}.npy")
    rec = {}
    for name, vec in units.items():
        for f in (f"{name}.npy", f"{name}.gguf"):
            assert not (out / f).exists() or name != "native", "never overwrite the native 3.8 vector"
        np.save(out / f"{name}.npy", vec)
        write_gguf(vec, out / f"{name}.gguf")
        rec[name] = dict(unit_sha256=sha(vec.tobytes()), gguf=f"qwen3.8-27b/{name}.gguf", dim=int(vec.size),
                         norm=float(np.linalg.norm(vec)))
    rec["xfer"].update(source=str(src.relative_to(GS / "outputs")), file_sha256=sha(src.read_bytes()),
                       raw_norm=float(np.linalg.norm(raw)), identical_to="qwen3.5-27b/native.npy")
    for k in ("random0", "random1"):
        rec[k].update(source="isotropic normal, seed 20261030", identical_to=f"qwen3.5-27b/{k}.npy")
    n38 = np.load(out / "native.npy").astype(np.float64)
    names = ["native", "xfer", "random0", "random1"]
    U = np.stack([n38] + [units[k].astype(np.float64) for k in names[1:]])
    rm = dict(target="Qwen 3.8", layer=36, easysteer_layer=35, activation_norm=man["models"]["Qwen 3.8"]["activation_norm"],
              activation_norm_source=man["models"]["Qwen 3.8"]["activation_norm_source"],
              formula="applied = signed_strength * A_36(Qwen 3.8) * unit(direction); prompt and generated tokens",
              directions=rec, cosine=dict(names=names, cos=(U @ U.T).round(4).tolist()))
    (V / "reverse_manifest.json").write_text(json.dumps(rm, indent=1))
    print(json.dumps(dict(A_36_target=rm["activation_norm"], cos=rm["cosine"]), indent=0))


if __name__ == "__main__":
    main()
