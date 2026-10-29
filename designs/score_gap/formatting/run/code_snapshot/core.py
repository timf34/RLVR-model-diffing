"""Matched, bounded experiments. No provider metadata or reasoning enters investigator-visible results."""
from __future__ import annotations

import asyncio
import random
from dataclasses import asdict, dataclass, field
from typing import Awaitable, Callable

MAX_CONTEXTS = 3


@dataclass(frozen=True)
class Reply:
    text: str
    status: str = "ok"
    # Researcher-only details (token usage, raw stop reason). Never shown to the investigator.
    meta: dict = field(default_factory=dict)


Generate = Callable[[list[dict[str, str]]], Awaitable[Reply]]


@dataclass
class Target:
    label: str
    generate: Generate


@dataclass
class Sample:
    model: str
    condition: str
    replicate: int
    messages: list[dict[str, str]]
    status: str
    private: list[dict] = field(default_factory=list)  # one entry per generation attempt


@dataclass
class Probe:
    id: str
    phase: str
    turns: list[str]
    conditions: dict[str, str]  # condition name -> system context ("" for baseline)
    samples: list[Sample] = field(default_factory=list)

    def public(self, private: bool = False) -> dict:
        data = asdict(self)
        if not private:
            for sample in data["samples"]:
                sample.pop("private")
        return data


def _script_key(turns: list[str]) -> tuple:
    return tuple(t.strip() for t in turns)


async def converse(generate: Generate, turns: list[str], *, system: str = "", timeout: float,
                   semaphore: asyncio.Semaphore) -> tuple[list[dict[str, str]], str, list[dict]]:
    """Play a fixed user script against one target, keeping its own replies. Returns (messages, status, private)."""
    messages: list[dict[str, str]] = [{"role": "system", "content": system}] if system else []
    status, private = "ok", []
    for turn in turns:
        messages.append({"role": "user", "content": turn})
        try:
            async with semaphore:
                reply = await asyncio.wait_for(generate([dict(m) for m in messages]), timeout)
            if not isinstance(reply, Reply):
                raise TypeError("Target adapter must return Reply")
            status = reply.status
            private.append(dict(reply.meta))
            messages.append({"role": "assistant", "content": reply.text})
            if status != "ok":
                break
        except Exception as error:
            # Provider errors can reveal target identity: researcher-only record.
            status = "error"
            private.append({"error": f"{type(error).__name__}: {str(error)[:300]}"})
            break
    return messages, status, private


class Experiment:
    def __init__(self, targets: list[Target], *, blind: bool = False, seed: int = 0,
                 max_calls: int = 240, concurrency: int = 6, timeout: float = 120):
        if len(targets) < 2 or len({t.label for t in targets}) != len(targets):
            raise ValueError("At least two uniquely labelled targets are required")
        if max_calls < 1 or concurrency < 1 or timeout <= 0:
            raise ValueError("Budgets, concurrency and timeout must be positive")
        ordered = list(targets)
        if blind:
            random.Random(seed).shuffle(ordered)
        self.targets = {f"Model {i+1}" if blind else t.label: t for i, t in enumerate(ordered)}
        self.mapping = {label: target.label for label, target in self.targets.items()}
        self.max_calls = max_calls
        self.calls = 0
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(concurrency)
        self.probes: list[Probe] = []
        self.lock = asyncio.Lock()

    async def probe(self, turns: list[str], *, context: str = "", contexts: list[str] | None = None,
                    samples: int = 3, phase: str = "discovery", forbidden: set[tuple] | None = None) -> dict:
        """Run `turns` on every target under baseline plus each context (c1, c2, ...)."""
        if not 1 <= len(turns) <= 6 or not all(isinstance(t, str) and t.strip() for t in turns):
            raise ValueError("Provide 1–6 nonempty user turns")
        if not 1 <= samples <= 5:
            raise ValueError("samples must be between 1 and 5")
        if context and contexts:
            raise ValueError("Pass either context or contexts, not both")
        contexts = list(contexts or ([context] if context else []))
        if len(contexts) > MAX_CONTEXTS or not all(isinstance(c, str) and c.strip() for c in contexts):
            raise ValueError(f"Provide 0–{MAX_CONTEXTS} nonempty contexts")
        # Held-out validation must use new user scripts; a new context on an old script is not fresh.
        if forbidden and _script_key(turns) in forbidden:
            raise ValueError("Validation must use a fresh scenario, not a discovery prompt")
        conditions = {"baseline": ""} | {f"c{i+1}": c for i, c in enumerate(contexts)}
        cost = len(self.targets) * samples * len(turns) * len(conditions)
        async with self.lock:
            if self.calls + cost > self.max_calls:
                raise ValueError(f"Target-call budget exhausted ({self.calls}/{self.max_calls} used, "
                                 f"this probe needs {cost}); shorten the probe or finish")
            self.calls += cost  # reserve before concurrent jobs; failed attempts consume budget
            probe = Probe(f"p{len(self.probes)+1:04d}", phase, list(turns), conditions)
            self.probes.append(probe)

        async def rollout(label: str, target: Target, condition: str, replicate: int) -> Sample:
            messages, status, private = await converse(target.generate, turns, system=conditions[condition],
                                                       timeout=self.timeout, semaphore=self.semaphore)
            return Sample(label, condition, replicate, messages, status, private)

        probe.samples = await asyncio.gather(*[
            rollout(label, target, condition, replicate)
            for label, target in self.targets.items()
            for condition in conditions
            for replicate in range(samples)
        ])
        return probe.public() | {"budget": {"this_probe": cost, "used": self.calls,
                                            "remaining": self.max_calls - self.calls}}

    def fingerprints(self, phase: str) -> set[tuple]:
        return {_script_key(p.turns) for p in self.probes if p.phase == phase}

    def validate_evidence(self, ids: list[str], phase: str) -> None:
        allowed = {p.id for p in self.probes if p.phase == phase and
                   p.samples and all(s.status == "ok" for s in p.samples)}
        if not ids or not set(ids) <= allowed:
            raise ValueError("Evidence must cite completed, non-truncated probes from this phase")

    def usage(self) -> dict:
        """Researcher-only per-model totals: tokens, stop reasons, errors."""
        totals: dict[str, dict] = {}
        for probe in self.probes:
            for sample in probe.samples:
                t = totals.setdefault(self.mapping[sample.model], dict(
                    generations=0, input_tokens=0, output_tokens=0, reasoning_tokens=0,
                    stop_reasons={}, errors=0, incomplete_samples=0))
                t["incomplete_samples"] += sample.status == "incomplete"
                for entry in sample.private:
                    if "error" in entry:
                        t["errors"] += 1
                        continue
                    t["generations"] += 1
                    for key in ("input_tokens", "output_tokens", "reasoning_tokens"):
                        t[key] += entry.get(key) or 0
                    reason = entry.get("stop_reason", "unknown")
                    t["stop_reasons"][reason] = t["stop_reasons"].get(reason, 0) + 1
        return totals
