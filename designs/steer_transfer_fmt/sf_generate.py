"""Steered generation for the formatting tasks: the presentation ablation's episode loop (pa_generate.episode,
unchanged) against the EasySteer servers, with steer_transfer's exact request construction (st_generate.gen_config:
sampling, seeds, Qwen 3.8 reasoning_effort, `steering` spec from steer_transfer/run/vectors/manifest.json) and its
serving fixes (strict_tools=False, max_connections; servers run with prefix caching off: steer_transfer/pod).

  ~/.claude/bin/memguard -m 6 -- .venv/bin/python designs/steer_transfer_fmt/sf_generate.py main \
      --endpoints designs/steer_transfer_fmt/run/endpoints.json --conc 160
  .venv/bin/python designs/steer_transfer_fmt/sf_generate.py status main
  .venv/bin/python designs/steer_transfer_fmt/sf_generate.py main --mock scripted --root run_mock   # offline only

Arm B text tasks: one user turn, no tools; the first reply without a tool call is the submission (at most 3 calls).
Resumable by key (a key is done once it has a non-error record; at most 3 attempts). Unsteered items run first.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import random
import sys
import time
from datetime import datetime
from pathlib import Path

from sf_common import HERE, MODELS, iter_jsonl, jhash

import pa_generate as PG  # noqa: E402
import st_generate as STG  # noqa: E402  (steer_transfer: gen_config, item_seed, manifest -- unchanged)
from pa_common import load_kind  # noqa: E402

MAX_ATTEMPTS = 3


def load(root: Path, stage: str):
    d = root / stage / "fmt"
    items = list(iter_jsonl(d / "items.jsonl"))
    prompts = {p["input_sha256"]: p["input"] for p in iter_jsonl(d / "prompts.jsonl")}
    for h, p in prompts.items():
        assert jhash(p) == h
    return items, prompts, json.loads((d / "blocks.json").read_text()), d / "episodes.jsonl"


def build_models(endpoints: dict, mock: str | None):
    from inspect_ai.model import get_model
    return {m: [PG.ScriptedModel(m) if mock else
                get_model(f"openai-api/vllm/{MODELS[m]['key']}", base_url=u, api_key="none", strict_tools=False)
                for u in urls] for m, urls in endpoints.items()}


async def run(root: Path, stage: str, endpoints: dict, conc: int, mock: str | None, minutes: float):
    load_kind("fmt")
    man = STG.manifest()
    items, prompts, blocks, out = load(root, stage)
    models = build_models(endpoints, mock)
    lock, t0 = asyncio.Lock(), time.time()
    for attempt_pass in range(1, MAX_ATTEMPTS + 1):
        recs = list(iter_jsonl(out))
        done = {r["key"] for r in recs if r["status"] != "error"}
        tries: dict = {}
        for r in recs:
            tries[r["key"]] = tries.get(r["key"], 0) + 1
        todo = [i for i in items if i["model"] in endpoints and i["key"] not in done
                and tries.get(i["key"], 0) < MAX_ATTEMPTS]
        if not todo:
            break
        rng = random.Random(f"sf|{stage}|{attempt_pass}")
        rng.shuffle(todo)
        todo.sort(key=lambda i: i["cond"] != "none")
        print(f"{stage} pass {attempt_pass}: {len(todo)} to do", flush=True)
        queues = {m: asyncio.Queue() for m in endpoints}
        for it in todo:
            queues[it["model"]].put_nowait(it)
        n = dict(done=0, total=len(todo))

        async def worker(model: str, k: int):
            m, sem = models[model][k], asyncio.Semaphore(1)
            while not queues[model].empty() and time.time() - t0 < minutes * 60:
                it = queues[model].get_nowait()
                cfg, st = STG.gen_config(model, it["cond"], man, it)
                started = datetime.now().isoformat(timespec="seconds")
                try:
                    ep = await PG.episode(m, cfg, it, prompts[it["input_sha256"]], blocks[it["block"]], sem)
                except Exception as e:  # noqa: BLE001
                    ep = dict(status="error", final_reply="", n_steps=0, steps=[], log=None, extra_calls=[],
                              usage={}, error=f"{type(e).__name__}: {str(e)[:300]}")
                rec = dict(it, started=started, finished=datetime.now().isoformat(timespec="seconds"),
                           endpoint=endpoints[model][k], steering=st, seed=STG.item_seed(it)) | ep
                rec.pop("cost", None)
                async with lock:
                    with out.open("a") as f:
                        f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
                    n["done"] += 1
                    if n["done"] % 500 == 0 or n["done"] == n["total"]:
                        print(f"  {n['done']}/{n['total']} {datetime.now():%H:%M:%S}", flush=True)

        await asyncio.gather(*[worker(m, k) for m in endpoints for k in range(len(endpoints[m])) for _ in range(conc)])
        if time.time() - t0 > minutes * 60:
            print("time limit", flush=True)
            break
    status(root, stage)


def status(root: Path, stage: str):
    items, _, _, out = load(root, stage)
    recs = list(iter_jsonl(out))
    by: dict = {}
    for r in recs:
        by[r["status"]] = by.get(r["status"], 0) + 1
    done = {r["key"] for r in recs if r["status"] != "error"}
    print(f"{stage}: {len(done)}/{len(items)} keys done; records by status {by}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["main", "smoke", "status"])
    ap.add_argument("status_stage", nargs="?", default="main")
    ap.add_argument("--root", default="run", choices=["run", "run_mock"])
    ap.add_argument("--endpoints", default=str(HERE / "run" / "endpoints.json"))
    ap.add_argument("--conc", type=int, default=160, help="concurrent episodes per endpoint (GPU)")
    ap.add_argument("--mock", choices=["scripted"], default=None)
    ap.add_argument("--minutes", type=float, default=300)
    a = ap.parse_args()
    root = HERE / a.root
    if a.stage == "status":
        status(root, a.status_stage)
        return
    if a.mock:
        assert a.root == "run_mock", "mock generations go to run_mock/ only"
        eps = {m: ["mock"] for m in MODELS}
    else:
        assert a.root == "run", "real generations go to run/ only"
        eps = json.loads(Path(a.endpoints).read_text())
    asyncio.run(run(root, a.stage, eps, a.conc, a.mock, a.minutes))


if __name__ == "__main__":
    sys.exit(main())
