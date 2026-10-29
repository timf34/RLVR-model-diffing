"""New reference replication, 2026-10-29: re-runs the reference cells (original 0.93/0.42 and 0.90/0.39 scores) of
three frozen score-gap runs, with new generations. Does not modify the original results.

  sending     designs/score_gap/sending     bundle panel, level "ref"   (run_gap.py, gap_materials.py; designs/action)
  formatting  designs/score_gap/formatting  bundle panel, scores "ref"  (run_fmt.py, fmt_materials.py; rl_context)
  omission    designs/score_gap/omission    rl panel, scores "ref"      (run_gap.py, gap_materials.py; rl judge)

The original runners are imported read-only; items, prompts, serving, per-call timeout, generation code and scorers
are theirs. Only the item keys change (prefixed "ref2|") and the output folder (this folder). One process per
environment (their modules share names), both models concurrently, at most 16 in flight per model.

Run from the repo root (each env in its own process):
  .venv/bin/python designs/grouped_replication/reference/ref_run.py plan <env>       # verify + <env>/plan.json
  .venv/bin/python designs/grouped_replication/reference/ref_run.py planmd           # PLAN.md (stdlib)
  .venv/bin/python designs/grouped_replication/reference/ref_run.py generate <env>   # resumable, ~9 min max
  .venv/bin/python designs/grouped_replication/reference/ref_run.py score <env>      # (omission: judges unsure)
  .venv/bin/python designs/grouped_replication/reference/ref_run.py report           # REPORT.md, results.json
"""
import asyncio
import hashlib
import json
import math
import random
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SG = ROOT / "designs" / "score_gap"
ENVS = ("sending", "formatting", "omission")
MODELS = ("Qwen 3.5", "Qwen 3.8")
PREFIX = "ref2|"
CONCURRENCY = 16          # per model
RETRY_PASSES = 2          # attempts per item <= 1 + RETRY_PASSES
LAUNCH_STOP = 400         # s: no new item starts after this
HARD_STOP = 525           # s: unfinished in-flight items are cancelled (not recorded; redone on the next call)
BUDGET, BUDGET_STOP = 15.0, 13.5
# Conservative $/token for budget tracking: the higher of the price tables the three runs used
# (sending: 3.5 0.26/2.6, 3.8 0.039/1.25 per M; formatting & omission: 3.5 0.30/2.40, 3.8 0.15/1.875 per M).
PRICES = {"Qwen 3.5": (0.30e-6, 2.60e-6), "Qwen 3.8": (0.15e-6, 1.875e-6)}
JUDGE_COST_PER_CALL = 0.02  # omission run's estimate for one Sonnet judge call
LABEL = "new reference replication, 2026-10-29; does not modify the original results"


def psha(system, turns) -> str:
    return hashlib.sha256(json.dumps(dict(system=system, turns=turns), sort_keys=True,
                                     ensure_ascii=False).encode()).hexdigest()


def gen_path(env, model) -> Path:
    return HERE / env / "gen" / model.replace(" ", "_") / ("episodes.jsonl" if env == "sending"
                                                            else "generations.jsonl")


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()] if path.exists() else []


def usage_of(env, rec) -> tuple[int, int]:
    if env == "sending":
        u = rec.get("usage") or {}
        return u.get("input_tokens") or 0, u.get("output_tokens") or 0
    i = o = 0
    for u in rec.get("private") or []:
        i += u.get("input_tokens") or 0
        o += u.get("output_tokens") or 0
    return i, o


def rec_cost(env, rec) -> float:
    i, o = usage_of(env, rec)
    pi, po = PRICES[rec["model"]]
    return i * pi + o * po


def spent_total() -> dict:
    out = {}
    for env in ENVS:
        c = sum(rec_cost(env, r) for m in MODELS for r in read_jsonl(gen_path(env, m)))
        nj = len(read_jsonl(HERE / env / "judge.jsonl"))
        cancelled = read_jsonl(HERE / env / "cancelled.jsonl")
        out[env] = dict(targets=c, judge=nj * JUDGE_COST_PER_CALL, judge_calls=nj, cancelled=len(cancelled))
    out["total"] = sum(v["targets"] + v["judge"] for v in out.values())
    return out


# ---------------------------------------------------------------- environment adapters (read-only imports)

def load_env(env):
    """Returns a namespace with: R (runner module), orig_items, items, prompt(i), manifest, frozen_prompts."""
    d = SG / env
    sys.path.insert(0, str(d))
    manifest = json.loads((d / "run" / "manifest.json").read_text())
    frozen = {p["key"]: p for p in json.loads((d / "run" / "prompts.json").read_text())}
    if env == "sending":
        import run_gap as R
        full = R.plan()
        orig = [i for i in full if i["panel"] == "bundle" and i["level"] == R.G.REF]
        prompt = R.prompt_for
        full_digest = R.digest(full)
        # prompts.json holds rep 0 of the first model only; the prompt does not depend on model or rep
        frozen_key = lambda i: f"gap|{i['scenario']}|{i['panel']}|{i['level']}|{MODELS[0]}|0"  # noqa: E731
    elif env == "formatting":
        import run_fmt as R
        full = R.plan()
        orig = [i for i in full if i["context"] == "bundle" and i["scores"] == R.G.REF]
        prompt = lambda i: dict(system=i["system"], turns=i["turns"])  # noqa: E731
        full_digest = R.P.digest(full, R.serving())
        frozen_key = lambda i: i["orig_key"]  # noqa: E731
    else:
        import run_gap as R
        full = R.plan()
        orig = [i for i in full if i["context"] == "rl" and i["scores"] == R.G.REF]
        prompt = lambda i: dict(system=i["system"], turns=i["turns"])  # noqa: E731
        full_digest = R.P.digest(full, R.serving())
        frozen_key = lambda i: i["orig_key"]  # noqa: E731
    items = [dict(i, key=PREFIX + i["key"], orig_key=i["key"]) for i in orig]
    for i in items:
        p = prompt(i)
        i["prompt_sha256"] = psha(p["system"], p["turns"])
        f = frozen.get(frozen_key(i))
        i["frozen_sha256"] = psha(f["system"], f["turns"]) if f else None
    code_now = R.code_hashes()
    code_changed = sorted(k for k, v in manifest["code_sha256"].items() if code_now.get(k) != v)
    return dict(R=R, env=env, orig=orig, items=items, prompt=prompt, manifest=manifest,
                digest_ok=full_digest == manifest["sha256"], code_changed=code_changed)


def cmd_plan(env):
    E = load_env(env)
    items = E["items"]
    mism = [i["key"] for i in items if i["prompt_sha256"] != i["frozen_sha256"]]
    keep = ("key", "orig_key", "model", "rep", "scenario", "panel", "level", "context", "scores", "feature", "sub",
            "prompt_sha256", "frozen_sha256")
    out = dict(env=env, label=LABEL, n=len(items), counts=dict(Counter(i["model"] for i in items)),
               full_plan_digest_matches_manifest=E["digest_ok"], manifest_sha256=E["manifest"]["sha256"],
               code_files_changed_since_freeze=E["code_changed"], prompt_hash_mismatches=mism,
               distinct_prompts=len({i["prompt_sha256"] for i in items}),
               serving=E["R"].serving(), items=[{k: i[k] for k in keep if k in i} for i in items])
    (HERE / env).mkdir(parents=True, exist_ok=True)
    (HERE / env / "plan.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(f"{env}: {len(items)} items {out['counts']}; distinct prompts {out['distinct_prompts']}; "
          f"full-plan digest == manifest: {E['digest_ok']}; prompt-hash mismatches: {len(mism)}; "
          f"code changed since freeze: {E['code_changed'] or 'none'}")


# ---------------------------------------------------------------- PLAN.md (stdlib only)

ORIG_COST = {  # original reference cells' returned token usage (input, output), summed over all items
    ("sending", "Qwen 3.5"): (397401, 74233), ("sending", "Qwen 3.8"): (360276, 85037),
    ("formatting", "Qwen 3.5"): (44976, 286284), ("formatting", "Qwen 3.8"): (44976, 112754),
    ("omission", "Qwen 3.5"): (24816, 182063), ("omission", "Qwen 3.8"): (24816, 49033)}
CELL = {"sending": "bundle panel, level `ref`", "formatting": "bundle panel, scores `ref` (3 features)",
        "omission": "rl panel, scores `ref`"}


def cmd_planmd():
    L = [f"# Reference replication: plan", "", f"**Label: {LABEL}.**", "",
         "Re-runs the reference cells (original scores 0.930/0.420 and 0.900/0.390) of three frozen score-gap runs "
         "with one fresh generation per original item, with the same prompts, serving and scorers. The originals are imported "
         "read-only from `designs/score_gap/<env>/`. New item keys are the original keys prefixed `ref2|`. "
         "Outputs go only to `designs/grouped_replication/reference/<env>/`.", "",
         f"Runtime: at most {CONCURRENCY} requests in flight per model (both models run together, one environment at "
         f"a time); Inspect backs off on 429s; failed items get up to {RETRY_PASSES} retry passes; foreground runs "
         f"stop launching at {LAUNCH_STOP} s and are resumed. Budget ${BUDGET:.0f}, tracked from returned token usage "
         f"at conservative prices (3.5: $0.30/$2.60 per M in/out; 3.8: $0.15/$1.875 per M).", "",
         "| Environment | cell | Qwen 3.5 items | Qwen 3.8 items | distinct prompts | full-plan digest = manifest | "
         "prompt sha256 = frozen prompts.json | code changed since freeze | est. cost |", "|---|---|---|---|---|---|---|---|---|"]
    tot, details = 0.0, []
    for env in ENVS:
        p = json.loads((HERE / env / "plan.json").read_text())
        est = sum(ORIG_COST[(env, m)][0] * PRICES[m][0] + ORIG_COST[(env, m)][1] * PRICES[m][1] for m in MODELS)
        if env == "omission":
            est += 10 * JUDGE_COST_PER_CALL  # allowance for rule-unsure replies
        tot += est
        ok = "all match" if not p["prompt_hash_mismatches"] else f"{len(p['prompt_hash_mismatches'])} MISMATCH"
        L.append(f"| {env} | {CELL[env]} | {p['counts'].get('Qwen 3.5', 0)} | {p['counts'].get('Qwen 3.8', 0)} | "
                 f"{p['distinct_prompts']} | {p['full_plan_digest_matches_manifest']} (`{p['manifest_sha256'][:12]}`) | "
                 f"{ok} | {', '.join(p['code_files_changed_since_freeze']) or 'none'} | ${est:.2f} |")
        by_prompt = {}
        for i in p["items"]:
            by_prompt.setdefault(i["prompt_sha256"], []).append(i)
        details += ["", f"### {env}", "", "| original item (key without model/rep) | items (models × reps) | "
                    "prompt sha256 (12) |", "|---|---|---|"]
        for h, its in by_prompt.items():
            base = "|".join(k for k in its[0]["orig_key"].split("|")[:-2])
            details.append(f"| `{base}` | {len(its)} ({', '.join(f'{m} {c}' for m, c in sorted(Counter(x['model'] for x in its).items()))}) | `{h[:12]}` |")
    L += ["", f"**Estimated cost: ${tot:.2f}** (the original reference cells' returned token usage at the "
          f"conservative prices above, plus a judge allowance for omission). Total items: "
          f"{sum(json.loads((HERE / e / 'plan.json').read_text())['n'] for e in ENVS)}.", "",
          "Scoring: sending, `acted` among valid episodes (designs/action/score.py via run_gap.run_episode); "
          "formatting, `adopted` among valid replies (fmt_materials.measures; titles_signoffs pools its title and "
          "sign-off sub-features); omission, omits/denies among valid replies (frozen rule, Sonnet judge for "
          "rule-unsure replies, as in run_gap.scored). Non-valid replies are excluded and counted.", "",
          "Comparison: new k/n vs the original reference k/n from each run's `run/results.json`; two-sided Fisher "
          "exact test. Full per-item hashes are in `<env>/plan.json`.", "", "## Items by prompt"] + details
    (HERE / "PLAN.md").write_text("\n".join(L) + "\n")
    print(f"Wrote {HERE / 'PLAN.md'} (estimated ${tot:.2f})")


# ---------------------------------------------------------------- generation

def is_error(env, rec) -> bool:
    return rec["status"] in ("failed", "abandoned") if env == "sending" else rec["status"] == "error"


async def cmd_generate(env):
    from dotenv import load_dotenv
    from inspect_ai.model import GenerateConfig, get_model
    E = load_env(env)
    if not E["digest_ok"] or any(i["prompt_sha256"] != i["frozen_sha256"] for i in E["items"]):
        raise SystemExit("Prompt/serving check failed; not generating")
    R, items = E["R"], E["items"]
    load_dotenv(ROOT / ".env")
    srv = R.serving()
    t0 = time.monotonic()
    state = dict(spent=spent_total()["total"], n=0, cancelled=0)
    print(f"{env}: spend so far (all envs) ${state['spent']:.2f}", flush=True)

    workers = {}
    for m in MODELS:
        t = next(x for x in srv["targets"] if x["label"] == m)
        model = get_model(t["model"], **t.get("model_args", {}))
        if env == "sending":
            from model_diffing.petri_task import generation_config
            cfg = generation_config(srv, t)
            cfg = cfg.merge(type(cfg)(max_connections=CONCURRENCY))
            policy = R.model_policy(model, cfg)

            async def work(i, policy=policy):
                rec = await R.run_episode(policy, R.M.ALL_TASKS[i["scenario"]], R.prompt_for(i))
                return {k: v for k, v in i.items() if k not in ("prompt_sha256", "frozen_sha256")} | rec
        else:
            from model_diffing.core import converse
            from model_diffing.petri_task import adapter, generation_config
            cfg = generation_config(srv, t).merge(GenerateConfig(max_connections=CONCURRENCY))
            gen = adapter(model, config=cfg)
            timeout = R.R.TIMEOUT  # run_confirm.TIMEOUT (1200 s per call), as in both runs
            inner = asyncio.Semaphore(10 ** 6)

            async def work(i, gen=gen, timeout=timeout, inner=inner):
                messages, status, private = await converse(gen, i["turns"], system=i["system"], timeout=timeout,
                                                           semaphore=inner)
                reply = messages[-1]["content"] if messages and messages[-1]["role"] == "assistant" else ""
                rec = {k: i[k] for k in ("key", "set", "scenario", "context", "scores", "user", "model", "rep")}
                return rec | dict(orig_key=i["orig_key"], status=status, private=private, reply=reply)
        workers[m] = work

    lock = asyncio.Lock()
    for m in MODELS:
        gen_path(env, m).parent.mkdir(parents=True, exist_ok=True)

    def todo_list():
        out = []
        for m in MODELS:
            hist = {}
            for r in read_jsonl(gen_path(env, m)):
                hist.setdefault(r["key"], []).append(r)
            for i in items:
                if i["model"] != m:
                    continue
                h = hist.get(i["key"], [])
                if not h or (is_error(env, h[-1]) and len(h) <= RETRY_PASSES):
                    out.append((i, len(h)))
        return out

    sems = {m: asyncio.Semaphore(CONCURRENCY) for m in MODELS}

    async def one(i, attempt, total):
        async with sems[i["model"]]:
            if time.monotonic() - t0 > LAUNCH_STOP or state["spent"] >= BUDGET_STOP:
                return
            started = datetime.now(timezone.utc).isoformat(timespec="seconds")
            try:
                rec = await workers[i["model"]](i)
            except asyncio.CancelledError:
                async with lock:
                    with (HERE / env / "cancelled.jsonl").open("a") as f:
                        f.write(json.dumps(dict(key=i["key"], started=started, reason="hard stop")) + "\n")
                    state["cancelled"] += 1
                raise
            except Exception as e:  # noqa: BLE001
                rec = {k: i[k] for k in ("key", "model", "rep", "scenario")} | dict(
                    orig_key=i["orig_key"], status="failed" if env == "sending" else "error",
                    error=f"{type(e).__name__}: {str(e)[:300]}", measures={}, usage={}, private=[], reply="")
            rec |= dict(attempt=attempt, started=started, finished=datetime.now(timezone.utc).isoformat(timespec="seconds"))
            rec["cost"] = rec_cost(env, rec)
            async with lock:
                with gen_path(env, i["model"]).open("a") as f:
                    f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
                state["spent"] += rec["cost"]
                state["n"] += 1
                if state["n"] % 10 == 0 or state["n"] == total:
                    print(f"  [{state['n']}/{total}] {time.monotonic() - t0:.0f}s ${state['spent']:.2f}", flush=True)

    while time.monotonic() - t0 < LAUNCH_STOP and state["spent"] < BUDGET_STOP:
        todo = todo_list()
        if not todo:
            break
        random.Random(len(todo)).shuffle(todo)
        state["n"] = 0
        print(f"{env}: launching {len(todo)} ({dict(Counter(i['model'] for i, _ in todo))})", flush=True)
        tasks = [asyncio.create_task(one(i, a, len(todo))) for i, a in todo]
        done, pending = await asyncio.wait(tasks, timeout=max(1, HARD_STOP - (time.monotonic() - t0)))
        if pending:
            for p in pending:
                p.cancel()
            await asyncio.gather(*pending, return_exceptions=True)
            print(f"{env}: hard stop, {len(pending)} unfinished (not recorded)", flush=True)
            break
    left = todo_list()
    print(f"{env}: {len(left)} items still to do; {time.monotonic() - t0:.0f}s; spend (all envs) "
          f"${spent_total()['total']:.2f}", flush=True)


# ---------------------------------------------------------------- scoring

def cmd_score(env):
    E = load_env(env)
    R, items = E["R"], E["items"]
    out = HERE / env
    res = dict(env=env, label=LABEL, cells={})
    if env == "sending":
        recs = R.latest(out, items)
        for r in recs:
            r["completion"] = R.completion(r)
        for m in MODELS:
            mine = [r for r in recs if r["model"] == m]
            valid = [r for r in mine if r["completion"] == "valid"]
            res["cells"][f"sending|{m}"] = dict(
                k=sum(bool(r["measures"]["acted"]) for r in valid), n=len(valid), planned=sum(i["model"] == m for i in items),
                present=len(mine), nonvalid=dict(Counter(r["completion"] for r in mine if r["completion"] != "valid")),
                acted_among_nonvalid=sum(bool((r.get("measures") or {}).get("acted")) for r in mine if r["completion"] != "valid"),
                task_done=sum(bool(r["measures"].get("task_done")) for r in valid))
    elif env == "formatting":
        rows = R.scored(items, out)
        for f in R.G.FEATURES:
            for m in MODELS:
                mine = [r for r in rows if r["model"] == m and r["feature"] == f]
                valid = [r for r in mine if r["completion"] == "valid"]
                res["cells"][f"formatting:{f}|{m}"] = dict(
                    k=sum(r["adopted"] for r in valid), n=len(valid), planned=len(mine),
                    present=sum(r["status"] != "missing" for r in mine),
                    nonvalid=dict(Counter(r["completion"] for r in mine if r["completion"] != "valid")),
                    violates=sum(r["violates"] for r in valid), facts_ok=sum(r["facts_ok"] for r in valid))
        for s in ("title", "signoff"):
            for m in MODELS:
                valid = [r for r in rows if r["model"] == m and r["sub"] == s and r["completion"] == "valid"]
                res.setdefault("subfeatures", {})[f"{s}|{m}"] = dict(k=sum(r["adopted"] for r in valid), n=len(valid))
    else:
        rows = R.scored(items, out)
        if any(r["completion"] == "unjudged" for r in rows):
            asyncio.run(R.judge_unsure(rows, out / "judge.jsonl"))
            rows = R.scored(items, out)
        present = {r["key"] for r in rows}
        for m in MODELS:
            mine = [r for r in rows if r["model"] == m]
            valid = [r for r in mine if r["completion"] == "valid"]
            nv = Counter(r["completion"] for r in mine if r["completion"] != "valid")
            nv["missing"] = sum(1 for i in items if i["model"] == m and i["key"] not in present)
            res["cells"][f"omission|{m}"] = dict(
                k=sum(r["y"] for r in valid), n=len(valid), planned=sum(i["model"] == m for i in items),
                present=len(mine), nonvalid={k: v for k, v in nv.items() if v},
                sources=dict(Counter(r["source"] for r in valid)), labels=dict(Counter(r["label"] for r in valid)))
    (out / "scored.json").write_text(json.dumps(res, indent=1) + "\n")
    for k, v in res["cells"].items():
        print(f"{k}: {v['k']}/{v['n']} (planned {v['planned']}, non-valid {v['nonvalid'] or 'none'})")


# ---------------------------------------------------------------- report (stdlib only)

def fisher_two_sided(k1, n1, k2, n2) -> float:
    """Two-sided Fisher exact p (sum of tables no more probable than the observed one)."""
    K, N = k1 + k2, n1 + n2
    if n1 == 0 or n2 == 0:
        return float("nan")
    pr = lambda a: math.comb(n1, a) * math.comb(n2, K - a) / math.comb(N, K)  # noqa: E731
    lo, hi = max(0, K - n2), min(n1, K)
    p0 = pr(k1)
    return min(1.0, sum(pr(a) for a in range(lo, hi + 1) if pr(a) <= p0 * (1 + 1e-7)))


def original_cells() -> dict:
    out = {}
    s = json.loads((SG / "sending/run/results.json").read_text())
    f = json.loads((SG / "formatting/run/results.json").read_text())
    o = json.loads((SG / "omission/run/results.json").read_text())
    for m in MODELS:
        out[f"sending|{m}"] = s["reference"][f"{m}|bundle"]
        for feat in ("titles_signoffs", "emdash", "bullets"):
            out[f"formatting:{feat}|{m}"] = f["reference"][f"{feat}|{m}|bundle"]
        out[f"omission|{m}"] = o["reference"][f"{m}|rl"]
    return {k: dict(k=v["k"], n=v["n"]) for k, v in out.items()}


def cmd_report():
    orig = original_cells()
    new, plans, sub = {}, {}, {}
    for env in ENVS:
        sc = json.loads((HERE / env / "scored.json").read_text())
        new |= sc["cells"]
        sub |= sc.get("subfeatures", {})
        plans[env] = json.loads((HERE / env / "plan.json").read_text())
    cost = spent_total()
    pc = lambda k, n: f"{100 * k / n:.0f}%" if n else "–"  # noqa: E731
    rows, res = [], dict(label=LABEL, cells={}, cost=cost, prices_per_token=PRICES)
    for key in orig:
        a, b = new[key], orig[key]
        p = fisher_two_sided(a["k"], a["n"], b["k"], b["n"])
        env, m = key.split("|")
        res["cells"][key] = dict(env=env, model=m, new=dict(k=a["k"], n=a["n"]), original=b, fisher_p=p,
                                 nonvalid_new=a["nonvalid"], planned_new=a["planned"])
        rows.append(f"| {env} | {m} | {a['k']}/{a['n']} ({pc(a['k'], a['n'])}) | {b['k']}/{b['n']} "
                    f"({pc(b['k'], b['n'])}) | {100 * (a['k'] / a['n'] - b['k'] / b['n']):+.0f} pp | {p:.2g} | "
                    f"{', '.join(f'{x} {y}' for x, y in a['nonvalid'].items()) or '0'} |")
    res["subfeatures_new"] = sub
    (HERE / "results.json").write_text(json.dumps(res, indent=1) + "\n")
    L = ["# Reference replication: report", "", f"**{LABEL}.**", "",
         "Each environment's reference cell was generated again with the original scores (0.930/0.420 and "
         "0.900/0.390), with one fresh generation per original item. Prompts, serving (Qwen 3.5 `novita/bf16`, "
         "default thinking; Qwen 3.8 `deepinfra/bf16`, reasoning_effort medium; T 0.7, top_p 0.95, top_k 20, "
         "max_tokens 32768, 1200 s per call), generation code and scorers are the original runs' own, imported "
         "read-only. Original k/n come from each run's frozen `run/results.json`.", "",
         "| Environment | Model | new k/n | original k/n | difference | Fisher p (two-sided) | new non-valid |",
         "|---|---|---|---|---|---|---|"] + rows
    L += ["", "Rates are among valid replies. Non-valid replies (failed, truncated, empty, step limit, missing) are "
          "excluded and never counted as following the user. In the originals all reference items were valid. "
          "Fisher p values are unadjusted (12 tests).", ""]
    if sub:
        L += ["Formatting sub-features (new, secondary): " + "; ".join(f"{k} {v['k']}/{v['n']}" for k, v in sub.items()), ""]
    L += ["## Checks", ""]
    for env in ENVS:
        p = plans[env]
        L.append(f"- **{env}**: {p['n']} items ({', '.join(f'{m} {c}' for m, c in p['counts'].items())}); "
                 f"full-plan digest equals the frozen manifest (`{p['manifest_sha256'][:12]}`): "
                 f"{p['full_plan_digest_matches_manifest']}; prompt sha256 vs frozen `run/prompts.json`: "
                 f"{'all ' + str(p['n']) + ' match' if not p['prompt_hash_mismatches'] else str(len(p['prompt_hash_mismatches'])) + ' MISMATCH'}; "
                 f"code files changed since the freeze: {', '.join(p['code_files_changed_since_freeze']) or 'none'}.")
    L += ["", "## Cost", "",
          f"Total **${cost['total']:.2f}** (budget ${BUDGET:.0f}), from returned token usage at conservative prices "
          f"(Qwen 3.5 $0.30/$2.60 per M in/out, Qwen 3.8 $0.15/$1.875 per M; the higher of the runs' price tables)."]
    for env in ENVS:
        c = cost[env]
        L.append(f"- {env}: targets ${c['targets']:.2f}" + (f", judge {c['judge_calls']} calls ≈ ${c['judge']:.2f}"
                                                            if env == "omission" else "")
                 + (f"; {c['cancelled']} in-flight items cancelled at a run's time limit and regenerated (their "
                    f"partial usage was not returned, so it is not counted)" if c["cancelled"] else ""))
    L += ["", "Files: `PLAN.md`, `ref_run.py`, `<env>/plan.json`, `<env>/gen/<model>/*.jsonl`, `<env>/scored.json`, "
          "`omission/judge.jsonl`, `results.json`."]
    (HERE / "REPORT.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[7:7 + len(rows) + 3]))
    print(f"cost ${cost['total']:.2f}")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    env = sys.argv[2] if len(sys.argv) > 2 else None
    if cmd in ("plan", "generate", "score") and env not in ENVS:
        raise SystemExit(f"env must be one of {ENVS}")
    if cmd == "plan":
        return cmd_plan(env)
    if cmd == "planmd":
        return cmd_planmd()
    if cmd == "generate":
        return asyncio.run(cmd_generate(env))
    if cmd == "score":
        return cmd_score(env)
    if cmd == "report":
        return cmd_report()
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
