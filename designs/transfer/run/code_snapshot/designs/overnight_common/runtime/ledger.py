"""Cost ledger: listed OpenRouter prices x returned usage (reasoning tokens are part of output tokens).

ledger.jsonl rows (append-only, one per API call or interrupted-call estimate):
  {kind: "call" | "interrupt_estimate", key, model, step, usage{input,output,reasoning}, cost_usd, at}
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

PRICES = {"Qwen 3.5": (0.26, 2.6), "Qwen 3.8": (0.039, 1.25)}   # $/M tokens (input, output), listed
# Prior per-ITEM cost before any record exists (INSPECTION.md section 7, rounded up generously).
PRIOR_ITEM = {("Qwen 3.5", "text"): 0.012, ("Qwen 3.5", "action"): 0.006,
              ("Qwen 3.8", "text"): 0.002, ("Qwen 3.8", "action"): 0.002}


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def norm_usage(u: dict | None) -> dict:
    u = u or {}
    g = lambda *ks: next((u[k] for k in ks if u.get(k) is not None), 0) or 0  # noqa: E731
    return dict(input=int(g("input", "input_tokens")), output=int(g("output", "output_tokens")),
                reasoning=int(g("reasoning", "reasoning_tokens")))


def cost(model: str, usage: dict | None) -> float:
    u = norm_usage(usage)
    pin, pout = PRICES[model]
    return u["input"] * pin / 1e6 + u["output"] * pout / 1e6


def add(a: dict, b: dict) -> dict:
    a, b = norm_usage(a), norm_usage(b)
    return {k: a[k] + b[k] for k in a}


class Ledger:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def rows(self) -> list[dict]:
        if not self.path.exists():
            return []
        return [json.loads(l) for l in self.path.read_text().splitlines() if l.strip()]

    def total(self) -> float:
        return sum(r.get("cost_usd", 0.0) for r in self.rows())

    def by_model(self) -> dict:
        out: dict = {}
        for r in self.rows():
            out[r["model"]] = out.get(r["model"], 0.0) + r.get("cost_usd", 0.0)
        return out

    def mean_call_cost(self, model: str) -> float:
        cs = [r["cost_usd"] for r in self.rows() if r["model"] == model and r["kind"] == "call"]
        return sum(cs) / len(cs) if cs else PRIOR_ITEM[(model, "text")] / 2

    def write(self, row: dict) -> float:
        with self.path.open("a") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        return row.get("cost_usd", 0.0)

    def call(self, key: str, model: str, step: int, usage: dict) -> float:
        u = norm_usage(usage)
        return self.write(dict(kind="call", key=key, model=model, step=step, usage=u,
                               cost_usd=round(cost(model, u), 8), at=now()))

    def interrupt(self, key: str, model: str, est: float) -> float:
        return self.write(dict(kind="interrupt_estimate", key=key, model=model, step=None, usage=None,
                               cost_usd=round(est, 8), at=now()))
