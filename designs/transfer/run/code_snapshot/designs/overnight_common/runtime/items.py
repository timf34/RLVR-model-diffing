"""Item plan and interleaved queue order (INTERFACE's `queue.py`; named items.py so that a script run from this
folder never shadows the standard-library `queue` module that asyncio imports).

A: subtypes x blocks x 2 frames x 5 histories (none, -0.50, 0, +0.05, +0.50) x 2 models.
B: directions x blocks x 2 frames x ({forbidden, permitted} x {0, +0.50} [+ {+0.05} with with_005] + none) x 2 models.
"""
from __future__ import annotations

import random

from . import blocks as B
from . import render as R

MODELS = ("Qwen 3.5", "Qwen 3.8")
SEED = "overnight-2026-10-29"


def cells(code: str, with_005: bool = False) -> list[tuple]:
    """(frame, history, gap, permission) for one block, in a fixed order."""
    out = []
    for fr in R.FRAMES:
        out.append((fr, "none", None, None))
        if code == "A":
            out += [(fr, "scored", g, None) for g in R.GAPS]
        else:
            gaps = (0.0, 0.05, 0.5) if with_005 else (0.0, 0.5)
            out += [(fr, "scored", g, p) for p in ("forbidden", "permitted") for g in gaps]
    return out


def make_item(code: str, block: dict, model: str, frame: str, history: str, gap, permission) -> dict:
    e = B.EXPERIMENTS[code]
    it = dict(key=R.key(block["block_id"], model, frame, history, gap, permission), experiment=e["name"],
              block_id=block["block_id"])
    if B.is_b(block):
        it |= dict(direction=block["direction"], source=block["source"], target=block["target"])
    else:
        it |= dict(subtype=block["subtype"])
    return it | dict(kind=B.kind(block), family=B.family(block), model=model, frame=frame, history=history,
                     gap=gap, permission=permission, smoke=bool(block.get("smoke")))


def select_blocks(blocks: list[dict], smoke: bool, n_blocks: int | None = None) -> list[dict]:
    """Main (or smoke) blocks; with n_blocks, the first N main blocks per unit in block_id order."""
    chosen = sorted((b for b in blocks if bool(b.get("smoke")) == smoke), key=lambda b: b["block_id"])
    if n_blocks is None:
        return chosen
    out, seen = [], {}
    for b in chosen:
        u = B.unit(b)
        if seen.get(u, 0) < n_blocks:
            out.append(b)
            seen[u] = seen.get(u, 0) + 1
    return out


def plan(code: str, blocks: list[dict], n_blocks: int | None = None, with_005: bool = False,
         smoke: bool = False, models=MODELS) -> list[dict]:
    out = []
    for b in select_blocks(blocks, smoke, n_blocks):
        for c in cells(code, with_005):
            for m in models:
                out.append(make_item(code, b, m, *c))
    return out


def interleave(items: list[dict], seed: str = SEED) -> list[dict]:
    """Randomised block order (fixed seed); all cells of a block adjacent; within a block the cells are shuffled
    (fixed seed) and the two models alternate cell by cell."""
    rng = random.Random(seed)
    by_block: dict[str, list] = {}
    for it in items:
        by_block.setdefault(it["block_id"], []).append(it)
    order = sorted(by_block)
    rng.shuffle(order)
    out = []
    for bid in order:
        its = by_block[bid]
        cell_keys = sorted({(i["frame"], i["history"], R.gap_str(i["gap"]), i["permission"] or "-") for i in its})
        rng.shuffle(cell_keys)
        models = sorted({i["model"] for i in its})
        if rng.random() < 0.5:
            models.reverse()
        idx = {(i["frame"], i["history"], R.gap_str(i["gap"]), i["permission"] or "-", i["model"]): i for i in its}
        for n, ck in enumerate(cell_keys):
            ms = models if n % 2 == 0 else models[::-1]  # alternate which model goes first
            out += [idx[ck + (m,)] for m in ms if ck + (m,) in idx]
    assert len(out) == len(items)
    return out


def conv(item: dict, blocks_by_id: dict) -> dict:
    return R.messages(blocks_by_id[item["block_id"]], item["frame"], item["history"], item["gap"],
                      item["permission"])
