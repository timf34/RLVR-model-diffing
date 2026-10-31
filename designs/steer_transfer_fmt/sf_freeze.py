"""Record sha256 hashes of the design, code, prompts, item grid and reused vectors (run/freeze.json).

  .venv/bin/python designs/steer_transfer_fmt/sf_freeze.py            # write (refuses if run/main has episodes)
  .venv/bin/python designs/steer_transfer_fmt/sf_freeze.py --verify   # check nothing changed since freezing
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone

from sf_common import HERE, PA, ST

FILES = (["PLAN.md", "sf_common.py", "sf_prepare.py", "sf_generate.py", "sf_score.py", "sf_analysis.py",
          "sf_tests.py", "sf_power.py", "run/main/fmt/items.jsonl", "run/main/fmt/prompts.jsonl",
          "run/main/fmt/prepare.json", "run/smoke/fmt/items.jsonl"],
         [ST / f for f in ("st_common.py", "st_generate.py", "st_checks.py", "pod/serve_multi.sh", "pod/setup_pod.sh",
                           "run/vectors/manifest.json", "run/vectors/reverse_manifest.json",
                           "st_reverse.py", "st_reverse_vectors.py", "run/vectors/qwen3.8-27b/xfer.gguf",
                           "run/vectors/qwen3.8-27b/random0.gguf", "run/vectors/qwen3.8-27b/random1.gguf")]
         + [PA / "pa_generate.py", PA / "pa_render.py", PA / "pa_materials.py"])


def digests() -> dict:
    out = {}
    for f in FILES[0]:
        out[f] = hashlib.sha256((HERE / f).read_bytes()).hexdigest()
    for p in FILES[1]:
        out[str(p.relative_to(HERE.parents[1]))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args()
    fz = HERE / "run" / "freeze.json"
    if a.verify:
        old = json.loads(fz.read_text())["files"]
        bad = [k for k, v in digests().items() if old.get(k) != v]
        print("FREEZE OK" if not bad else f"!! changed since freeze: {bad}")
        return 1 if bad else 0
    ep = HERE / "run" / "main" / "fmt" / "episodes.jsonl"
    if ep.exists() and ep.stat().st_size > 0:
        print("!! run/main already has episodes; freezing now would not be a pre-generation freeze")
        return 1
    design = json.loads((HERE / "run/main/fmt/prepare.json").read_text())["design"]
    fz.write_text(json.dumps(dict(frozen_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                  design=design, files=digests()), indent=1))
    print(f"frozen ({design} design): {len(FILES[0]) + len(FILES[1])} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
