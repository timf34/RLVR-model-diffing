"""Other-model addendum: replay the frozen Qwen 3.5 Part 1 items (strong vs weak RL framing; sending, titles/sign-offs,
bullets) on other model families, so every model sees identical prompts. Two groups:
- RL-heavy reasoning models: OpenAI o3, Kimi K2-thinking / K2.5 / K2.6.
- Same-base pairs (less vs much more RL): DeepSeek V3-0324 -> R1-0528, Qwen3-235B Instruct-2507 -> Thinking-2507,
  Kimi K2-0905 -> K2-thinking, MiniMax-01 -> M1; and release trends GLM-4.5/4.6/4.7, MiniMax M2/M2.1/M2.5/M2.7.
Reasoning is switched on for every model that has it, so the chain of thought is logged (o3 returns only summaries).

Each model gets its own root, run_extra/<slug>/, so runs can go in parallel without sharing files:

  python pa_extra.py prepare                          # clone 3.5 Part 1 items for every model in MODELS
  memguard -m 4 -- python pa_extra.py generate o3     # one process per model; safe to run several at once
  python pa_extra.py status
  python pa_score.py send|fmt --stage main --root designs/presentation_ablation/run_extra/<slug>

Same episode loop, max tokens, timeout and item design as Qwen 3.5/3.6/3.8 (pa_generate / pa_common, imported
unchanged). Sampling: the Qwen settings (temperature 0.7, top_p 0.95, top_k 20) for the open models; OpenAI reasoning models
take no sampling parameters, so o3 runs at its defaults with reasoning_effort medium (as Qwen 3.8).
o1 is not run: OpenRouter no longer serves it. Kimi K2 (July) and the K2.7-code fine-tune are left out.
Strong RL framing (arm B) only, tied and +0.50 scores, original + fresh scenarios: 136 episodes per task.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pa_common as C  # noqa: E402

SOURCE = "Qwen 3.5"
ARMS = ("B",)   # strong RL framing only (the user's scope); weak framing (N) can be added later
EXTRA = HERE / "run_extra"
# slug: (label, OpenRouter id, allowed hosts, own generate settings, $/M (in, out) of the dearest allowed host,
#        $ per in-flight episode for the budget guard, sampling params allowed?)
R = {"extra_body": {"reasoning": {"enabled": True}}}
OAI = {"reasoning_effort": "medium"}
MODELS = {
    "o3": ("o3", "openrouter/openai/o3", ["openai"], {"reasoning_effort": "medium"}, (2.0, 8.0), 0.08, False),
    "kimi-k2-thinking": ("Kimi K2-thinking", "openrouter/moonshotai/kimi-k2-thinking", ["novita/bf16"], {},
                         (0.6, 2.5), 0.03, True),
    "kimi-k2.5": ("Kimi K2.5", "openrouter/moonshotai/kimi-k2.5", ["atlas-cloud/int4", "siliconflow/int4"], {},
                  (0.5, 2.5), 0.03, True),
    "kimi-k2.6": ("Kimi K2.6", "openrouter/moonshotai/kimi-k2.6", ["parasail/int4", "inceptron/int4"], {},
                  (0.75, 3.5), 0.03, True),
    # Same-base pairs and release trends (2026-10-31). Reasoning switched on wherever the model has it, so CoT is logged.
    "deepseek-v3-0324": ("DeepSeek V3-0324", "openrouter/deepseek/deepseek-chat-v3-0324", ["siliconflow/fp8"], {},
                         (0.25, 1.0), 0.01, True),
    "deepseek-r1-0528": ("DeepSeek R1-0528", "openrouter/deepseek/deepseek-r1-0528", ["siliconflow/fp8"], R,
                         (0.5, 2.18), 0.03, True),
    "qwen3-235b-instruct": ("Qwen3-235B Instruct-2507", "openrouter/qwen/qwen3-235b-a22b-2507",
                            ["deepinfra/fp8", "parasail/fp8"], {}, (0.14, 0.8), 0.01, True),
    "qwen3-235b-thinking": ("Qwen3-235B Thinking-2507", "openrouter/qwen/qwen3-235b-a22b-thinking-2507", ["venice/fp8"],
                            R, (0.45, 3.5), 0.04, True),
    "kimi-k2-0905": ("Kimi K2-0905", "openrouter/moonshotai/kimi-k2-0905", ["novita/fp8"], {}, (0.6, 2.5), 0.01, True),
    "minimax-01": ("MiniMax-01", "openrouter/minimax/minimax-01", ["minimax"], {}, (0.2, 1.1), 0.01, True),
    "minimax-m1": ("MiniMax-M1", "openrouter/minimax/minimax-m1", ["novita/bf16"], R, (0.55, 2.2), 0.03, True),
    "glm-4.5": ("GLM-4.5", "openrouter/z-ai/glm-4.5", ["z-ai/fp8"], R, (0.6, 2.2), 0.03, True),
    "glm-4.6": ("GLM-4.6", "openrouter/z-ai/glm-4.6", ["novita/bf16"], R, (0.55, 2.2), 0.03, True),
    "glm-4.7": ("GLM-4.7", "openrouter/z-ai/glm-4.7", ["novita/fp8"], R, (0.54, 1.98), 0.03, True),
    "minimax-m2": ("MiniMax-M2", "openrouter/minimax/minimax-m2", ["minimax/fp8"], R, (0.26, 1.02), 0.02, True),
    "minimax-m2.1": ("MiniMax-M2.1", "openrouter/minimax/minimax-m2.1", ["minimax"], R, (0.3, 1.2), 0.02, True),
    "minimax-m2.5": ("MiniMax-M2.5", "openrouter/minimax/minimax-m2.5", ["minimax", "novita/fp8"], R, (0.3, 1.2), 0.02,
                     True),
    "minimax-m2.7": ("MiniMax-M2.7", "openrouter/minimax/minimax-m2.7", ["minimax", "novita/fp8"], R, (0.3, 1.2), 0.02,
                     True),
    # OpenAI around o3 (2026-11-01). o3-mini / o4-mini are batch-only on OpenRouter (no chat calls), so not run. Lineage is not published; GPT-4o is the reported base of the o-series.
    "gpt-4o": ("GPT-4o (2024-11-20)", "openrouter/openai/gpt-4o-2024-11-20", ["openai"], {}, (2.5, 10.0), 0.02, True),
    "gpt-4.1": ("GPT-4.1", "openrouter/openai/gpt-4.1", ["openai"], {}, (2.0, 8.0), 0.02, True),
    "gpt-5": ("GPT-5", "openrouter/openai/gpt-5", ["openai/default"], OAI, (1.25, 10.0), 0.08, False),
    "gpt-5.1": ("GPT-5.1", "openrouter/openai/gpt-5.1", ["openai"], OAI, (1.25, 10.0), 0.08, False),
    "gpt-5.2": ("GPT-5.2", "openrouter/openai/gpt-5.2", ["openai"], OAI, (1.75, 14.0), 0.1, False),
    "gpt-oss-120b": ("gpt-oss-120b", "openrouter/openai/gpt-oss-120b", ["deepinfra/bf16", "coreweave/fp4"], OAI,
                     (0.04, 0.17), 0.01, True),
    "gpt-oss-20b": ("gpt-oss-20b", "openrouter/openai/gpt-oss-20b", ["deepinfra/bf16", "coreweave/fp4"], OAI,
                    (0.03, 0.14), 0.01, True),
    # DeepSeek after R1 (2026-11-01): V3.2-Exp / V3.2 share the V3 base (hybrid, thinking on); V4 is a new base.
    # fp8 hosts (DeepSeek's native precision), plus DeepSeek's own API for V4-Pro-0813. V3.1 / V3.1-Terminus are not run:
    # they cannot call tools in thinking mode (V3.1 returns blank replies; Terminus silently drops thinking).
    "deepseek-v3.2-exp": ("DeepSeek V3.2-Exp", "openrouter/deepseek/deepseek-v3.2-exp", ["siliconflow/fp8"], R,
                          (0.27, 0.41), 0.02, True),
    "deepseek-v3.2": ("DeepSeek V3.2", "openrouter/deepseek/deepseek-v3.2", ["siliconflow/fp8", "atlas-cloud/fp8"], R,
                      (0.26, 0.8), 0.02, True),
    "deepseek-v4-flash": ("DeepSeek V4-Flash", "openrouter/deepseek/deepseek-v4-flash", ["deepinfra/fp8", "gmicloud/fp8"],
                          R, (0.09, 0.18), 0.01, True),
    "deepseek-v4-flash-0731": ("DeepSeek V4-Flash-0731", "openrouter/deepseek/deepseek-v4-flash-0731",
                               ["deepinfra/fp8", "baidu/fp8"], R, (0.06, 0.18), 0.01, True),
    "deepseek-v4-pro": ("DeepSeek V4-Pro", "openrouter/deepseek/deepseek-v4-pro", ["siliconflow/fp8", "gmicloud/fp8"], R,
                        (1.0, 3.14), 0.04, True),
    "deepseek-v4-pro-0813": ("DeepSeek V4-Pro-0813", "openrouter/deepseek/deepseek-v4-pro-0813",
                             ["deepseek", "streamlake"], R, (0.66, 1.98), 0.03, True),
    "deepseek-v4.1-flash": ("DeepSeek V4.1-Flash", "openrouter/deepseek/deepseek-v4.1-flash", ["morph/fp8", "baidu/fp8"],
                            R, (0.05, 0.19), 0.01, True),
    "deepseek-v4.1-flash-1017": ("DeepSeek V4.1-Flash-1017", "openrouter/deepseek/deepseek-v4.1-flash-1017",
                                 ["morph/fp8"], R, (0.05, 0.19), 0.01, True),
}
# MiniMax-01 has no tool-calling host on OpenRouter, so it cannot do the sending task.
TASKS_FOR = {"minimax-01": ("titles", "bullets")}

# --more: extra repeats on the fresh scenarios (reps 1 and 2; the main run has rep 0), in run_more/<slug>, for the models
# that show the behaviour. Qwen 3.5 / 3.6 / 3.8 are served exactly as in experiment.grading.3way.json.
MORE = HERE / "run_more"
MORE_REPS = (1, 2)
# --more-orig: matching extra repeats on the ORIGINAL scenarios (run_more_orig/<slug>), so original and fresh scenarios
# contribute about equally to each pooled bar (~96 runs each per score condition). Qwen 3.8's main run already had a
# second fresh rep, so it gets more original repeats to match.
MORE_ORIG = HERE / "run_more_orig"
ORIG_EXTRA = {"send": 5, "titles": 5, "bullets": 10}            # extra reps per original scenario
ORIG_EXTRA_BY_MODEL = {"Qwen 3.8": {"send": 8, "titles": 8, "bullets": 16}}
BASE = EXTRA
QWEN_PRICES = {"Qwen 3.5": (0.26, 2.6), "Qwen 3.6": (0.45, 2.7), "Qwen 3.8": (0.039, 1.25)}


def _qwen_entries():
    s = json.loads(C.SERVING_CONFIG.read_text())
    out = {}
    for t in s["targets"]:
        if t["label"] in QWEN_PRICES:
            out["qwen" + t["label"].split()[-1]] = (t["label"], t["model"], t["model_args"]["provider"]["only"],
                                                    t.get("generate", {}), QWEN_PRICES[t["label"]], 0.03, True)
    return out


MODELS.update(_qwen_entries())   # qwen3.5 / qwen3.6 / qwen3.8: --more only (their main runs live in run/ and run_q36/)


def root(slug: str) -> Path:
    return BASE / slug


def clone_items(task: str, label: str) -> list[dict]:
    out = []
    for it in C.iter_jsonl(C.RUN / "main" / task / "items.jsonl"):
        if it["model"] != SOURCE or it.get("part") != 1 or it["arm"] not in ARMS:
            continue
        if BASE == MORE_ORIG:   # original scenarios only, new reps after the source's last one
            if it["materials"] != "orig" or it["rep"] != 0:
                continue
            last = max(i["rep"] for i in C.iter_jsonl(C.RUN / "main" / task / "items.jsonl")
                       if i["model"] == SOURCE and i["block"] == it["block"] and i["arm"] == it["arm"]
                       and i["score"] == it["score"] and i.get("part") == 1)
            extra = ORIG_EXTRA_BY_MODEL.get(label, ORIG_EXTRA)[task]
            for r in range(last + 1, last + 1 + extra):
                k = it["key"][:-2].replace(f"|{SOURCE}", f"|{label}") + f"|{r}"
                out.append(dict(it, model=label, rep=r, key=k))
            continue
        if BASE == MORE:   # fresh scenarios only, one copy per extra rep
            if it["materials"] != "fresh":
                continue
            assert it["rep"] == 0 and it["key"].endswith("|0")
            for r in MORE_REPS:
                k = it["key"][:-2].replace(f"|{SOURCE}", f"|{label}") + f"|{r}"
                out.append(dict(it, model=label, rep=r, key=k))
            continue
        it = dict(it, model=label, key=it["key"].replace(f"|{SOURCE}|", f"|{label}|"))
        assert label in it["key"]
        out.append(it)
    return out


def prepare(slugs):
    for slug in slugs:
        label = MODELS[slug][0]
        r = root(slug)
        man = dict(at=C.now(), label=f"{label}: Qwen 3.5 Part 1 items replayed", model=MODELS[slug][1],
                   hosts=MODELS[slug][2], tasks={}, code_sha256=C.sha((HERE / "pa_extra.py").read_bytes()),
                   source_manifest_sha256=C.sha((C.RUN / "main" / "manifest.json").read_bytes()))
        r.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(C.RUN / "units.json", r / "units.json")
        for task in TASKS_FOR.get(slug, C.TASKS):
            src, dst = C.RUN / "main" / task, r / "main" / task
            dst.mkdir(parents=True, exist_ok=True)
            items = clone_items(task, label)
            need = {i["input_sha256"] for i in items}
            n = 0
            with (dst / "prompts.jsonl").open("w") as f:
                for line in (src / "prompts.jsonl").open():
                    p = json.loads(line)
                    if p["input_sha256"] in need:
                        assert C.jhash(p["input"]) == p["input_sha256"]
                        f.write(line if line.endswith("\n") else line + "\n")
                        n += 1
            assert n == len(need), (task, n, len(need))
            with (dst / "items.jsonl").open("w") as f:
                for it in items:
                    f.write(json.dumps(it) + "\n")
            shutil.copyfile(src / "blocks.json", dst / "blocks.json")
            man["tasks"][task] = dict(n_items=len(items), n_prompts=n, items_digest=C.jhash(items),
                                      blocks_sha256=C.sha((dst / "blocks.json").read_bytes()))
        (r / "manifest.json").write_text(json.dumps(man, indent=1))
        print(f"{slug}: " + ", ".join(f"{t} {v['n_items']}" for t, v in man["tasks"].items()))


def patch(slug: str):
    """Point the unchanged generator at one model (serving entry, price, budget estimate, verify)."""
    import pa_freeze
    import pa_generate as G
    label, model, hosts, own, price, est, sampling = MODELS[slug]
    C.PRICES[label] = price
    G.EST_INFLIGHT[label] = est

    def verify(stage, r):
        man = json.loads((root(slug) / "manifest.json").read_text())
        assert C.sha((C.RUN / "main" / "manifest.json").read_bytes()) == man["source_manifest_sha256"], "source changed"
        for task, v in man["tasks"].items():
            assert C.jhash(list(C.iter_jsonl(r / stage / task / "items.jsonl"))) == v["items_digest"]
        return man
    pa_freeze.verify = verify
    s = json.loads(C.SERVING_CONFIG.read_text())
    tgt = [dict(label=label, model=model, model_args=dict(provider=dict(only=hosts, allow_fallbacks=False)),
                generate=own)]
    G.serving = lambda: dict(targets=tgt, target_generate=s["target_generate"] if sampling else {},
                             temperature=C.TEMPERATURE if sampling else None,
                             target_max_tokens=C.MAX_TOKENS, timeout=C.TIMEOUT)
    return G, label


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["prepare", "generate", "status"])
    ap.add_argument("slug", nargs="?", default="all")
    ap.add_argument("--task", default="all")
    ap.add_argument("--concurrency", type=int, default=16)
    ap.add_argument("--minutes", type=float, default=900)
    ap.add_argument("--budget-stop", type=float, default=40.0)
    ap.add_argument("--max-items", type=int, default=None)
    ap.add_argument("--more", action="store_true", help="extra fresh-scenario repeats in run_more/")
    ap.add_argument("--more-orig", action="store_true", help="extra original-scenario repeats in run_more_orig/")
    a = ap.parse_args()
    global BASE
    if a.more:
        BASE = MORE
    if a.more_orig:
        BASE = MORE_ORIG
    slugs = list(MODELS) if a.slug == "all" else a.slug.split(",")
    tasks = C.TASKS if a.task == "all" else tuple(a.task.split(","))
    if len(slugs) == 1 and slugs[0] in TASKS_FOR:
        tasks = tuple(t for t in tasks if t in TASKS_FOR[slugs[0]])
    if a.cmd == "prepare":
        prepare(slugs)
        return
    if a.cmd == "status":
        for slug in slugs:
            G, _ = patch(slug)
            print(f"== {slug}")
            G.status("main", root(slug), tasks)
        return
    assert len(slugs) == 1, "generate one model per process"
    G, label = patch(slugs[0])
    asyncio.run(G.run("main", root(slugs[0]), tasks, (label,), a.concurrency, a.minutes, a.budget_stop,
                      a.max_items, None))


if __name__ == "__main__":
    main()
