"""Presentation-only wrapper (outside the frozen, hashed code): re-renders a frozen figure with its long title
wrapped onto two lines. Data, layout and everything else come unchanged from the frozen figure() function.
Run: .venv/bin/python designs/score_gap/haiku/figure_wrap.py upsell|sending
"""
import sys
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib.figure import Figure  # noqa: E402

_orig = Figure.suptitle


def _wrapped(self, t, **kw):
    return _orig(self, "\n".join(textwrap.wrap(t, 190)), **kw)


Figure.suptitle = _wrapped
which = sys.argv[1]
HERE = Path(__file__).parent
sys.argv = ["x"]
sys.path.insert(0, str(HERE / which))
mod = __import__("haiku_gap" if which == "upsell" else "haiku_send")
mod.figure(mod.OUT)
