"""CLI for the action-mechanism experiments. Run from designs/action_mechanisms/:

  ../../.venv/bin/python am.py shared-tests                      # offline tests of shared/
  ../../.venv/bin/python am.py <exp> offline                     # the experiment's scripted-policy tests
  ../../.venv/bin/python am.py <exp> preview inspection|main     # renderings for hand inspection
  ../../.venv/bin/python am.py <exp> generate inspection         # inspection run (API calls)
  ../../.venv/bin/python am.py <exp> freeze                      # freeze the main batch
  ../../.venv/bin/python am.py <exp> generate main [model ...]   # main batch (checks the manifest)
  ../../.venv/bin/python am.py <exp> analyse inspection|main
  ../../.venv/bin/python am.py <exp> status inspection|main
Heavy runs: wrap with `caffeinate -i ~/.claude/bin/memguard -m 3 -- ...`. All processes share one per-provider
concurrency budget (shared/limiter.py), so several experiments can generate at once.
"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # designs/ -> package `action_mechanisms`

from action_mechanisms.shared import runner  # noqa: E402


def main():
    a = sys.argv[1:]
    if not a:
        raise SystemExit(__doc__)
    if a[0] == "shared-tests":
        from action_mechanisms.shared import test_shared
        return asyncio.run(test_shared.main())
    exp, cmd = a[0], a[1]
    split = a[2] if len(a) > 2 else "main"
    if cmd == "offline":
        return runner.module(exp).offline()
    if cmd == "preview":
        return runner.preview(exp, split)
    if cmd == "generate":
        return asyncio.run(runner.generate(exp, split, a[3:] or None))
    if cmd == "freeze":
        return runner.freeze(exp)
    if cmd == "status":
        return runner.status(exp, split)
    if cmd == "analyse":
        mod = runner.module(exp)
        items = mod.plan(split)
        man_path = runner.out_dir(exp, "main") / "manifest.json"
        manifest = json.loads(man_path.read_text()) if split == "main" else {}
        if split == "main":
            changed = [f for f, h in runner.code_hashes(mod).items() if manifest["code_sha256"].get(f) != h]
            manifest["code_changed_since_freeze"] = changed
        return mod.analyse(runner.load(exp, split, items), runner.out_dir(exp, split), manifest)
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
