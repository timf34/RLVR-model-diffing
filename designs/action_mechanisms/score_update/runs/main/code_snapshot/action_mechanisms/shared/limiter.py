"""Cross-process concurrency limiter: ONE per-provider budget shared by every experiment process.

Each provider has CAPS[label] slot files under shared/.slots/<label>/. A call holds an exclusive flock on one slot
file for the duration of the API request. flock locks belong to the open file description, so they exclude both
other processes and other coroutines in the same process, and they are released automatically if a process dies.
"""
from __future__ import annotations

import asyncio
import contextlib
import fcntl
import os
import random
from pathlib import Path

from .serving import CAPS

SLOTS = Path(__file__).resolve().parent / ".slots"


def _try(path: Path):
    fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fd
    except OSError:
        os.close(fd)
        return None


@contextlib.asynccontextmanager
async def slot(label: str, cap: int | None = None):
    cap = cap or CAPS[label]
    d = SLOTS / label.replace(" ", "_")
    d.mkdir(parents=True, exist_ok=True)
    order = list(range(cap))
    fd = None
    while fd is None:
        random.shuffle(order)
        for i in order:
            fd = _try(d / f"{i}.lock")
            if fd is not None:
                break
        if fd is None:
            await asyncio.sleep(0.3 + random.random() * 0.7)
    try:
        yield
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def in_use(label: str) -> int:
    """How many slots are currently held (diagnostic)."""
    d = SLOTS / label.replace(" ", "_")
    n = 0
    for p in d.glob("*.lock") if d.exists() else []:
        fd = _try(p)
        if fd is None:
            n += 1
        else:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
    return n
