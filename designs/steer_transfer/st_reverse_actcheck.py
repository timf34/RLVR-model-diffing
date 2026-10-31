"""HF activation check for ALL four directions on Qwen 3.8 (native, xfer = 3.5's direction, random0, random1).

  (on a pod) PYTHONPATH=/workspace/grader-shifts-persona-space/src $ES_VENV/bin/python st_reverse_actcheck.py

Runs st_actcheck.main unchanged, pointed at a scratch root whose manifest lists the reverse directions too
(run/vectors/reverse_manifest.json merged into the main manifest; vector files are symlinked, never copied or edited).
Output: run/checks/actcheck_reverse_qwen3.8-27b.json (injection cos/norm vs 0.3 x A_36(3.8), downstream displacement).
"""
from __future__ import annotations

import copy
import json
import shutil
import tempfile
from pathlib import Path

import st_actcheck as A

HERE = Path(__file__).resolve().parent


def main():
    man = json.loads((HERE / "run/vectors/manifest.json").read_text())
    rm = json.loads((HERE / "run/vectors/reverse_manifest.json").read_text())
    merged = copy.deepcopy(man)
    merged["models"]["Qwen 3.8"]["directions"].update(rm["directions"])
    tmp = Path(tempfile.mkdtemp(prefix="st_rev_act_"))
    (tmp / "run/vectors").mkdir(parents=True)
    (tmp / "run/checks").mkdir(parents=True)
    (tmp / "run/vectors/manifest.json").write_text(json.dumps(merged))
    for key in ("qwen3.5-27b", "qwen3.8-27b"):
        (tmp / "run/vectors" / key).symlink_to(HERE / "run/vectors" / key)
    A.HERE = tmp
    A.main("Qwen 3.8")
    (HERE / "run/checks").mkdir(parents=True, exist_ok=True)
    shutil.copy(tmp / "run/checks/actcheck_qwen3.8-27b.json", HERE / "run/checks/actcheck_reverse_qwen3.8-27b.json")
    print("written run/checks/actcheck_reverse_qwen3.8-27b.json")


if __name__ == "__main__":
    main()
