"""Stateful simulated tools (adapted from designs/action/env.py). In-memory only: nothing is sent or published.

SimEnv(family, mode, scorer):
  - two tools, save and commit, with identical fields and identical validation;
  - `mode` ("external" | "local") selects the commit tool's documentation and result text (families.py);
  - `scorer`, optional: a deterministic function of the env state, evaluated by `final_score()` and logged
    separately from user compliance (used by the score_update experiment);
  - `frozen = True` (set by the episode loop for the post-action follow-up): calls are logged as `blocked` and
    NOT executed, so a follow-up question can never cause an action.
Every call is logged as {name, kind, args, ok, result, phase}.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from .families import FAMILIES, MODES, tool_specs


def _s(v) -> str:
    if isinstance(v, (list, tuple)):
        return ", ".join(_s(x) for x in v)
    return "" if v is None else str(v)


@dataclass
class SimEnv:
    family: str
    mode: str = "external"
    scorer: Callable[["SimEnv"], float] | None = None
    log: list = field(default_factory=list)
    drafts: list = field(default_factory=list)
    committed: list = field(default_factory=list)
    frozen: bool = False
    phase: str = "act"
    _n: int = 0

    def __post_init__(self):
        assert self.family in FAMILIES and self.mode in MODES

    @property
    def fam(self) -> dict:
        return FAMILIES[self.family]

    def tools(self) -> list[dict]:
        return tool_specs(self.family, self.mode)

    def kind(self, name: str) -> str:
        return {self.fam["save"][0]: "save", self.fam["commit"][0]: "commit"}.get(name, "unknown")

    def call(self, name: str, args, parse_error: str | None = None) -> str:
        args = {k: _s(v) for k, v in args.items()} if isinstance(args, dict) else {}
        kind, ok = self.kind(name), False
        if self.frozen:
            result = "error: tools are not available for this message."
            kind = f"blocked_{kind}"
        elif parse_error:
            result = f"error: could not parse the tool call arguments ({parse_error[:200]})"
        elif kind == "unknown":
            result = f"error: unknown tool '{name}'"
        else:
            missing = [k for k in self.fam["fields"] if not args.get(k, "").strip()]
            unknown = [k for k in args if k not in self.fam["fields"]]
            if missing or unknown:
                result = (f"error: missing required field(s): {', '.join(missing)}. " if missing else "") + \
                         (f"error: unknown field(s): {', '.join(unknown)}. " if unknown else "") + \
                         "Nothing was saved or sent."
            else:
                self._n += 1
                clean = {k: args[k] for k in self.fam["fields"]}
                ident = f"{'d' if kind == 'save' else 'c'}-{1000 + self._n}"
                tpl = self.fam["save_result"] if kind == "save" else self.fam["commit_result"][self.mode]
                result = tpl.format(id=ident, **clean)
                (self.drafts if kind == "save" else self.committed).append(clean)
                ok = True
        self.log.append(dict(name=name, kind=kind, args=args, ok=ok, result=result, phase=self.phase))
        return result

    def final_score(self) -> float | None:
        return None if self.scorer is None else float(self.scorer(self))
