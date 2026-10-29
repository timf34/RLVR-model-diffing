"""Stateful simulated workplace tools. Pure Python state, no external effects.

Each episode exposes three tools for its scenario's family: one read tool, one save tool (draft only) and one commit
tool (send / submit / publish / merge). Save and commit take identical fields and both validate the same way, so
completing the action is no harder than saving it. Every call is logged with its arguments, result and whether it
succeeded; scoring (score.py) reads only this log and the final message.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import materials as M


def tool_specs(task: dict) -> list[dict]:
    """JSON-schema tool specs (name, description, parameters), identical in every condition for a scenario."""
    fam = M.FAMILIES[task["family"]]
    rname, rdesc, rfields = fam["read"]
    props = lambda fs: {k: {"type": "string", "description": d} for k, d in fs.items()}  # noqa: E731
    return [
        dict(name=rname, description=rdesc, parameters=dict(type="object", properties=props(rfields),
                                                            required=list(rfields))),
        dict(name=fam["save"][0], description=fam["save"][1],
             parameters=dict(type="object", properties=props(fam["fields"]), required=list(fam["fields"]))),
        dict(name=fam["commit"][0], description=fam["commit"][1],
             parameters=dict(type="object", properties=props(fam["fields"]), required=list(fam["fields"]))),
    ]


def _s(v) -> str:
    if isinstance(v, (list, tuple)):
        return ", ".join(_s(x) for x in v)
    return "" if v is None else str(v)


@dataclass
class ActionEnv:
    task: dict
    log: list = field(default_factory=list)     # dicts: name, kind, args, ok, result
    drafts: list = field(default_factory=list)  # successful saves (args)
    committed: list = field(default_factory=list)  # successful commits (args)
    _n: int = 0

    @property
    def fam(self) -> dict:
        return M.FAMILIES[self.task["family"]]

    def kind(self, name: str) -> str:
        return {self.fam["read"][0]: "read", self.fam["save"][0]: "save", self.fam["commit"][0]: "commit"}.get(
            name, "unknown")

    def call(self, name: str, args: dict | None, parse_error: str | None = None) -> str:
        args = {k: _s(v) for k, v in (args or {}).items()} if isinstance(args, dict) else {}
        kind = self.kind(name)
        ok, result = False, ""
        if parse_error:
            result = f"error: could not parse the tool call arguments ({parse_error[:200]})"
        elif kind == "unknown":
            result = f"error: unknown tool '{name}'"
        elif kind == "read":
            fields = self.fam["read"][2]
            if "number" in fields and args.get("number", "").lstrip("#").strip() != self.task.get("pr"):
                result = f"error: pull request {args.get('number', '')!r} not found. Open pull requests: #{self.task['pr']}"
            else:
                ok, result = True, self.task["context"]
        else:
            missing = [k for k in self.fam["fields"] if not args.get(k, "").strip()]
            unknown = [k for k in args if k not in self.fam["fields"]]
            if missing:
                result = f"error: missing required field(s): {', '.join(missing)}. Nothing was saved or sent."
            elif unknown:
                result = f"error: unknown field(s): {', '.join(unknown)}. Nothing was saved or sent."
            else:
                self._n += 1
                clean = {k: args[k] for k in self.fam["fields"]}
                ident = f"{'d' if kind == 'save' else 'c'}-{1000 + self._n}"
                template = self.fam["save_result"] if kind == "save" else self.fam["commit_result"]
                result = template.format(id=ident, **clean)
                (self.drafts if kind == "save" else self.committed).append(clean)
                ok = True
        self.log.append(dict(name=name, kind=kind, args=args, ok=ok, result=result))
        return result
