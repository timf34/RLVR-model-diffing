"""Matched, bounded experiments. No provider metadata or reasoning enters investigator-visible results."""
from __future__ import annotations

import asyncio
import json
import random
from dataclasses import asdict, dataclass, field
from typing import Awaitable, Callable

MAX_CONTEXTS = 3
# Agent-visible tool results are built to fit these byte budgets, so Inspect never truncates them silently.
# TOOL_OUTPUT_LIMIT is passed to eval(max_tool_output=...) and must stay above both budgets.
PROBE_RESULT_BYTES = 48_000
SAMPLE_RESULT_BYTES = 200_000
TOOL_OUTPUT_LIMIT = 262_144
MAX_SAMPLES_PER_FETCH = 10


def _size(data) -> int:
    return len(json.dumps(data, ensure_ascii=False).encode())


def _clip(text: str, limit: int, sample_id: str) -> tuple[str, bool]:
    raw = text.encode()
    if len(raw) <= limit:
        return text, False
    kept = raw[:limit].decode(errors="ignore")
    return (f"{kept}\n…[CLIPPED: {len(raw) - len(kept.encode())} more bytes. "
            f"Call get_samples([\"{sample_id}\"]) for the full reply.]"), True


def compact(result: dict, budget: int = PROBE_RESULT_BYTES) -> dict:
    """Investigator view of a probe: the script and conditions once, then each sample's replies by sample_id.

    If the replies don't fit `budget`, the longest are clipped with an explicit marker and the result says
    `complete: false` with the clipped sample ids, so partial evidence is never mistaken for complete evidence.
    """
    samples = [dict(sample_id=f"{result['id']}-s{i + 1:02d}", model=s["model"], condition=s["condition"],
                    replicate=s["replicate"], status=s["status"],
                    replies=[m["content"] for m in s["messages"] if m["role"] == "assistant"])
               for i, s in enumerate(result["samples"])]
    out = {k: result[k] for k in ("id", "phase", "turns", "conditions") if k in result}
    out |= dict(samples=samples, complete=True)
    if "budget" in result:
        out["budget"] = result["budget"]
    if _size(out) <= budget:
        return out
    replies = sum(len(s["replies"]) for s in samples) or 1
    skeleton = _size(out | dict(samples=[s | dict(replies=[""] * len(s["replies"])) for s in samples]))
    per = max(120, (budget - skeleton) // replies - 160)  # 160 bytes of room for each clip marker
    while True:
        clipped, trial = set(), []
        for s in samples:
            new = []
            for text in s["replies"]:
                text, cut = _clip(text, per, s["sample_id"])
                new.append(text)
                if cut:
                    clipped.add(s["sample_id"])
            trial.append(s | dict(replies=new))
        candidate = out | dict(samples=trial, complete=False, clipped_samples=sorted(clipped),
                               note="Some replies were clipped to fit. Fetch full text with get_samples before "
                                    "counting or quoting them.")
        if _size(candidate) <= budget or per <= 40:
            return candidate
        per //= 2


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


def with_planted_system(generate: Generate, planted: str) -> Generate:
    """Positive controls only: put a hidden instruction ahead of any system context for one target.
    The investigator never sees it; probe records keep the visible conversation unchanged."""
    async def wrapped(messages: list[dict[str, str]]) -> Reply:
        messages = [dict(m) for m in messages]
        if messages and messages[0]["role"] == "system":
            messages[0]["content"] = f"{planted}\n\n{messages[0]['content']}"
        else:
            messages.insert(0, {"role": "system", "content": planted})
        return await generate(messages)
    return wrapped


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

    def get_samples(self, sample_ids: list[str], phase: str, budget: int = SAMPLE_RESULT_BYTES) -> dict:
        """Full visible conversations for sample ids from probes of `phase` only (validators can't read discovery)."""
        if not sample_ids or len(sample_ids) > MAX_SAMPLES_PER_FETCH:
            raise ValueError(f"Request 1–{MAX_SAMPLES_PER_FETCH} sample ids")
        index = {}
        for probe in self.probes:
            if probe.phase == phase:
                for i, s in enumerate(probe.samples):
                    index[f"{probe.id}-s{i + 1:02d}"] = s
        unknown = [sid for sid in sample_ids if sid not in index]
        if unknown:
            raise ValueError(f"Unknown sample ids for this phase: {unknown}")
        out = dict(samples=[], complete=True)
        for sid in dict.fromkeys(sample_ids):
            s = index[sid]
            entry = dict(sample_id=sid, model=s.model, condition=s.condition, replicate=s.replicate,
                         status=s.status, messages=[dict(m) for m in s.messages])
            if _size(out | dict(samples=out["samples"] + [entry])) > budget:
                if not out["samples"]:  # a single conversation over budget: clip it, and say so
                    for m in entry["messages"]:
                        m["content"], _ = _clip(m["content"], budget // (2 * len(entry["messages"])), sid)
                    out["samples"].append(entry)
                    out.update(complete=False, clipped_samples=[sid])
                    continue
                out.setdefault("not_returned", []).append(sid)
                out["complete"] = False
                continue
            out["samples"].append(entry)
        if out.get("not_returned"):
            out["note"] = "Result size limit reached; request the not_returned ids in a separate call."
        return out

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
