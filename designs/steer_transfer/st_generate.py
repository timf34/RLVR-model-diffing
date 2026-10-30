"""Steered episode driver: the presentation ablation's own episode loop (pa_generate.episode, unchanged) against
self-hosted EasySteer vLLM servers, one OpenAI-compatible endpoint per GPU.

  ~/.claude/bin/memguard -m 4 -- .venv/bin/python designs/steer_transfer/st_generate.py main \
      --endpoints designs/steer_transfer/run/endpoints.json [--conc 64] [--only-none] [--mock scripted]
  .venv/bin/python designs/steer_transfer/st_generate.py status main

endpoints.json: {"Qwen 3.5": ["http://localhost:18000/v1", ...], "Qwen 3.8": [...]} (ssh tunnels to the pods).
Every request carries the same sampling settings as the ablation's API serving (temperature 0.7, top_p 0.95,
top_k 20, max_tokens 32768; Qwen 3.8 chat_template_kwargs reasoning_effort=medium) and, for steered conditions,
extra_body.steering = EasySteer `direct` spec at layer 35 (our 36), applied to ALL prompt tokens and ALL generated
tokens of EVERY model call in the episode (each tool turn is a new request, so steering covers every turn).
Seeds: per (block, score arm, rep), shared across steering conditions (common random numbers).
Resumable: a key is done once it has a non-error record; at most 3 attempts. Unsteered items run first.
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

from st_common import (MAX_TOKENS, MODELS, RUN, TEMPERATURE, TOP_K, TOP_P, iter_jsonl, jhash, parse_condition, sha)

import pa_generate as PG  # noqa: E402  (episode loop; read-only)
from pa_common import load_kind  # noqa: E402

MAX_ATTEMPTS = 3
GGUF_ROOT = "/workspace/steer_transfer/run/vectors"   # where the pods hold the payloads


def manifest() -> dict:
    return json.loads((RUN / "vectors" / "manifest.json").read_text())


def steering_extra(model: str, cond: str, man: dict) -> dict | None:
    d, s = parse_condition(cond)
    if d is None:
        return None
    scale = s * man["models"][model]["activation_norm"]
    return {"vectors": [{"source": f"{GGUF_ROOT}/{MODELS[model]['key']}/{d}.gguf", "algorithm": "direct",
                         "scale": float(scale), "layers": [man["easysteer_layer"]],
                         "apply": {"prompt": "all", "generation": "all"}}], "conflict": "sequential"}


def item_seed(it: dict) -> int:
    return int(sha(f"st|{it['block']}|{it['score']}|{it['rep']}")[:8], 16) & 0x7FFFFFFF


def gen_config(model: str, cond: str, man: dict, it: dict):
    from inspect_ai.model import GenerateConfig
    extra = {"top_k": TOP_K}
    if MODELS[model]["chat_template_kwargs"]:
        extra["chat_template_kwargs"] = dict(MODELS[model]["chat_template_kwargs"])
    st = steering_extra(model, cond, man)
    if st is not None:
        extra["steering"] = st
    return GenerateConfig(temperature=TEMPERATURE, top_p=TOP_P, max_tokens=MAX_TOKENS, seed=item_seed(it),
                          extra_body=extra, max_retries=2, timeout=1200, max_connections=256), st


def load(stage: str):
    d = RUN / stage / "send"
    items = list(iter_jsonl(d / "items.jsonl"))
    prompts = {p["input_sha256"]: p["input"] for p in iter_jsonl(d / "prompts.jsonl")}
    for h, p in prompts.items():
        assert jhash(p) == h
    blocks = json.loads((d / "blocks.json").read_text())
    return items, prompts, blocks, d / "episodes.jsonl"


def build_models(endpoints: dict, mock: str | None):
    from inspect_ai.model import get_model
    out = {}
    for model, urls in endpoints.items():
        if mock:
            out[model] = [PG.ScriptedModel(model) for _ in urls]
        else:
            # strict_tools=False: inspect's default strict tool schemas switch on vLLM constrained decoding, under
            # which Qwen 3.5 keeps generating after its tool call until max_tokens (AMENDMENTS 2). The archived
            # OpenRouter runs had no such constraint.
            out[model] = [get_model(f"openai-api/vllm/{MODELS[model]['key']}", base_url=u, api_key="none",
                                    strict_tools=False) for u in urls]
    return out


async def run(stage: str, endpoints: dict, conc: int, only_none: bool, mock: str | None, minutes: float):
    load_kind("send")
    man = manifest()
    items, prompts, blocks, out = load(stage)
    models = build_models(endpoints, mock)
    lock = asyncio.Lock()
    t0 = time.time()
    for attempt_pass in range(1, MAX_ATTEMPTS + 1):
        recs = list(iter_jsonl(out))
        done = {r["key"] for r in recs if r["status"] != "error"}
        tries: dict = {}
        for r in recs:
            tries[r["key"]] = tries.get(r["key"], 0) + 1
        todo = [i for i in items if i["model"] in endpoints and i["key"] not in done
                and tries.get(i["key"], 0) < MAX_ATTEMPTS and (not only_none or i["cond"] == "none")]
        if not todo:
            break
        rng = random.Random(f"st|{stage}|{attempt_pass}")
        rng.shuffle(todo)
        todo.sort(key=lambda i: i["cond"] != "none")          # unsteered first (bridge readout)
        print(f"{stage} pass {attempt_pass}: {len(todo)} to do", flush=True)
        queues = {m: asyncio.Queue() for m in endpoints}
        for it in todo:
            queues[it["model"]].put_nowait(it)
        n = dict(done=0, total=len(todo))

        async def worker(model: str, k: int):
            m = models[model][k]
            sem = asyncio.Semaphore(1)
            while not queues[model].empty():
                if time.time() - t0 > minutes * 60:
                    return
                it = queues[model].get_nowait()
                cfg, st = gen_config(model, it["cond"], man, it)
                started = datetime.now().isoformat(timespec="seconds")
                try:
                    ep = await PG.episode(m, cfg, it, prompts[it["input_sha256"]], blocks[it["block"]], sem)
                except Exception as e:  # noqa: BLE001
                    ep = dict(status="error", final_reply="", n_steps=0, steps=[], log=None, extra_calls=[],
                              usage={}, cost=0.0, error=f"{type(e).__name__}: {str(e)[:300]}")
                rec = dict(it, started=started, finished=datetime.now().isoformat(timespec="seconds"),
                           endpoint=endpoints[model][k], steering=st, seed=item_seed(it)) | ep
                rec.pop("cost", None)
                async with lock:
                    with out.open("a") as f:
                        f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
                    n["done"] += 1
                    if n["done"] % 200 == 0 or n["done"] == n["total"]:
                        print(f"  {n['done']}/{n['total']} {datetime.now():%H:%M:%S}", flush=True)

        ws = [worker(m, k) for m in endpoints for k in range(len(endpoints[m])) for _ in range(conc)]
        await asyncio.gather(*ws)
        if time.time() - t0 > minutes * 60:
            print("time limit", flush=True)
            break
    status(stage)


def status(stage: str):
    items, _, _, out = load(stage)
    recs = list(iter_jsonl(out))
    done = {r["key"] for r in recs if r["status"] != "error"}
    by: dict = {}
    for r in recs:
        by[r["status"]] = by.get(r["status"], 0) + 1
    print(f"{stage}: {len(done)}/{len(items)} done; records by status {by}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["main", "smoke", "bridge", "status"])
    ap.add_argument("status_stage", nargs="?", default="main")
    ap.add_argument("--endpoints", default=str(RUN / "endpoints.json"))
    ap.add_argument("--conc", type=int, default=64, help="concurrent episodes per endpoint (GPU)")
    ap.add_argument("--only-none", action="store_true")
    ap.add_argument("--mock", choices=["scripted"], default=None)
    ap.add_argument("--minutes", type=float, default=240)
    ap.add_argument("--models", default=None)
    a = ap.parse_args()
    if a.stage == "status":
        status(a.status_stage)
        return
    eps = json.loads(Path(a.endpoints).read_text()) if not a.mock else {m: ["mock"] for m in MODELS}
    if a.models:
        eps = {m: v for m, v in eps.items() if m in a.models.split(",")}
    asyncio.run(run(a.stage, eps, a.conc, a.only_none, a.mock, a.minutes))


if __name__ == "__main__":
    sys.exit(main())
