"""CLI entry point. API credentials stay in environment variables."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Run a black-box multi-model investigation")
    parser.add_argument("config", type=Path)
    parser.add_argument("--log-dir", default="logs")
    args = parser.parse_args()
    settings = json.loads(args.config.read_text())
    if "REPLACE_WITH_" in json.dumps(settings):
        parser.error("Replace the example model IDs with actual Inspect provider/model identifiers")
    # Load .env from the config's folder or the working directory, and fail early (non-zero) without keys.
    import os

    from dotenv import find_dotenv, load_dotenv
    load_dotenv(args.config.resolve().parent / ".env")
    load_dotenv(find_dotenv(usecwd=True))
    if "openrouter/" in json.dumps(settings) and not os.environ.get("OPENROUTER_API_KEY"):
        raise SystemExit("OPENROUTER_API_KEY is not set (checked the environment and .env); nothing was run")
    from inspect_ai import eval
    from inspect_ai.model import get_model
    from .core import TOOL_OUTPUT_LIMIT
    from .petri_task import model_diff

    # `*_model_args` pins provider routing for the investigator models, as `model_args` does for targets.
    auditor = get_model(settings["auditor"], **settings.get("auditor_model_args", {}))
    validator = get_model(settings.get("validator", settings["auditor"]),
                          **settings.get("validator_model_args", settings.get("auditor_model_args", {})))
    first = settings["targets"][0]
    logs = eval(model_diff(str(args.config)), model=auditor,
                model_roles={"auditor": auditor, "validator": validator,
                             # Petri requires this role even though custom probes call all targets.
                             "target": get_model(first["model"], **first.get("model_args", {}))},
                log_dir=args.log_dir,
                # Each seed is an independent investigation; one failure should not cancel the rest.
                max_samples=settings.get("max_parallel_investigations", 2), fail_on_error=False,
                # Above the probe/sample result budgets in core.py, so tool results are never cut silently.
                max_tool_output=TOOL_OUTPUT_LIMIT)
    if not logs or any(log.status != "success" for log in logs):
        raise SystemExit("Investigation failed; inspect the eval log for details")
    failed = [s.id for log in logs for s in (log.samples or []) if s.error]
    if failed:
        print(f"Warning: {len(failed)} investigation(s) errored: {failed}")
    print(f"Completed. Review with: model-diff-export {logs[0].location}\n"
          f"or browse with: inspect view --log-dir {args.log_dir}")


if __name__ == "__main__":
    main()
