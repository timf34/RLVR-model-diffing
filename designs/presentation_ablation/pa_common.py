"""Shared constants, paths and read-only loaders for the presentation ablation (stdlib only).

The old studies' modules share names (`materials`, `score`) between designs/action and designs/rl_context, so a
process loads exactly one KIND: "send" (designs/action + score_gap/sending) or "fmt" (designs/rl_context +
score_gap/formatting; serves the titles/sign-offs and bullets tasks). Loading the other kind in the same process
raises. Nothing outside designs/presentation_ablation/ is ever written.
"""
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import sys
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DESIGNS = ROOT / "designs"
RUN = HERE / "run"
SENDING = DESIGNS / "score_gap" / "sending"
FORMATTING = DESIGNS / "score_gap" / "formatting"
ACTION = DESIGNS / "action"
RL = DESIGNS / "rl_context"
IG = DESIGNS / "ifeval_incidental_grader"
REFCHECK = IG / "reference_check"
SERVING_CONFIG = ROOT / "experiment.grading.3way.json"

TASKS = ("send", "titles", "bullets")
KIND = {"send": "send", "titles": "fmt", "bullets": "fmt"}
PRIMARY_TASKS = ("send", "titles")          # required tasks; pooled primaries use these (bullets = secondary task)
MODELS = ("Qwen 3.8", "Qwen 3.5")           # 3.8 primary, 3.5 descriptive contrast; no Qwen 3.6
PRIMARY_MODEL = "Qwen 3.8"
GAPS = {"tied": 0.0, "p050": 0.5}           # the score-gap studies' exact pairs: 0.500/0.500 and 0.750/0.250
SCORE_PAIRS = {"tied": ("0.500", "0.500"), "p050": ("0.750", "0.250")}  # (user-conflicting, user-requested)
PRICES = {"Qwen 3.5": (0.26, 2.6), "Qwen 3.8": (0.039, 1.25)}  # $/M (in, out), as 10A / IFEval
MAX_STEPS = {"send": 8, "titles": 3, "bullets": 3}   # 10A: send 8 (old study); text tasks 3 (IFEval study)
MAX_TOKENS, TIMEOUT, TEMPERATURE = 32768, 1200, 0.7


def sha(b: bytes | str) -> str:
    return hashlib.sha256(b.encode() if isinstance(b, str) else b).hexdigest()


def jdump(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False)


def jhash(obj) -> str:
    return sha(jdump(obj))


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def rel(p: Path) -> str:
    return str(Path(p).resolve().relative_to(ROOT))


def load_file(name: str, path: Path):
    """Import a file under a unique module name (read-only use)."""
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def ig_render():
    """The IFEval study's renderer constants (system frames, DIAG_META, TOOL_PACKET, fmt3/dumps, packet_id)."""
    return load_file("pa_ig_render", IG / "ig_render.py")


def ref_blocks():
    """10A's 16 + 16 fresh blocks (designs/ifeval_incidental_grader/reference_check/ref_blocks.py)."""
    return load_file("pa_ref_blocks", REFCHECK / "ref_blocks.py")


_LOADED: dict = {}


def quiet(fn, *a, **k):
    """Run an old self-check, swallowing its stdout (keeps tool output small); returns what it printed."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        fn(*a, **k)
    return buf.getvalue().strip()


def load_kind(kind: str) -> dict:
    """Old modules for one kind, imported read-only. Returns a namespace dict."""
    if _LOADED:
        assert _LOADED["kind"] == kind, f"kind {_LOADED['kind']} already loaded in this process; run {kind} separately"
        return _LOADED
    if kind == "send":
        sys.path[:0] = [str(SENDING), str(ACTION)]
        import gap_materials as G  # noqa: E402
        import materials as M  # noqa: E402  (designs/action)
        import score as S  # noqa: E402  (designs/action)
        import env as ENV  # noqa: E402  (designs/action)
        assert Path(M.__file__).resolve().parent == ACTION and Path(S.__file__).resolve().parent == ACTION
        _LOADED.update(kind=kind, G=G, M=M, S=S, ENV=ENV)
    elif kind == "fmt":
        sys.path[:0] = [str(FORMATTING), str(RL), str(RL / "domains")]
        import fmt_materials as FM  # noqa: E402
        import confirm_materials as CM  # noqa: E402
        import structure as ST  # noqa: E402
        import confirm_score as CS  # noqa: E402
        import score as RS  # noqa: E402  (designs/rl_context/score.py: completion)
        assert Path(RS.__file__).resolve().parent == RL
        _LOADED.update(kind=kind, FM=FM, CM=CM, ST=ST, CS=CS, RS=RS)
    else:
        raise ValueError(kind)
    _LOADED["R"] = ig_render()
    _LOADED["RB"] = ref_blocks()
    import pa_blocks as PB  # noqa: E402
    _LOADED["PB"] = PB
    return _LOADED


def serving() -> dict:
    """experiment.grading.3way.json targets for Qwen 3.5 / 3.8 (3.6 excluded), as ig_generate.serving()."""
    s = json.loads(SERVING_CONFIG.read_text())
    targets = [{k: v for k, v in t.items() if k != "serving_note"} for t in s["targets"] if t["label"] in MODELS]
    assert sorted(t["label"] for t in targets) == sorted(MODELS), [t["label"] for t in targets]
    return dict(targets=targets, target_generate=s["target_generate"], temperature=TEMPERATURE,
                target_max_tokens=MAX_TOKENS, timeout=TIMEOUT)


def cost(model: str, usage: dict) -> float:
    pin, pout = PRICES[model]
    return (usage.get("input_tokens") or 0) * pin / 1e6 + (usage.get("output_tokens") or 0) * pout / 1e6


def read_jsonl(p: Path) -> list[dict]:
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]


def iter_jsonl(p: Path):
    if p.exists():
        with p.open() as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)
