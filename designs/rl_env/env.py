"""Compatibility shim: the environment now lives in model_diffing.rlenv.env."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from model_diffing.rlenv.env import *  # noqa: E402,F401,F403
