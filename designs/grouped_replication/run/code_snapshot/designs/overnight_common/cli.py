"""Overnight batch CLI. Experiment A = designs/grouped_replication, B = designs/transfer.

Run from the repo root, always under memguard:
  M="$HOME/.claude/bin/memguard -m 4 -- .venv/bin/python designs/overnight_common/cli.py"
  $M A validate                      schema, balance, permission-clause and regex feature checks + render invariants
  $M A preview 2 [--payload]         2 prompts per condition -> <exp>/preview/PREVIEW.md (with sha256)
  $M A plan [--blocks N] [--with-005]
  $M A smoke [--budget 1]            paid; smoke blocks only, ~2 items per subtype/direction -> <exp>/smoke/
  $M A pilot [--budget 3]            paid; ~60 smoke-block items; repeat until done; writes <exp>/pilot/ESTIMATE.md
  $M A freeze [--blocks N] [--with-005]   -> <exp>/run/manifest.json, plan.json, code_snapshot/ (refuses if frozen)
  $M A generate --budget USD [--concurrency 32]   verifies the manifest, runs ONE ~9-min chunk; repeat until done
  $M A status
  $M A connect                       2 real calls on a fake block (1 text, 1 tool turn) -> runtime/connectivity/
Exit codes (smoke/pilot/generate/connect): 0 all done, 3 items remain (run again), 4 budget stop, 2 refused.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import shutil
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # designs/

from overnight_common.runtime import blocks as B  # noqa: E402
from overnight_common.runtime import generate as G  # noqa: E402
from overnight_common.runtime import items as I  # noqa: E402
from overnight_common.runtime import render as R  # noqa: E402
from overnight_common.runtime import serving as S  # noqa: E402
from overnight_common.runtime.ledger import PRIOR_ITEM, Ledger  # noqa: E402

ROOT = B.ROOT
SKIP_DIRS = {"run", "smoke", "pilot", "preview", "__pycache__", "connectivity", "code_snapshot", "review",
             "figure", "figures"}


def sha_file(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rel(p: Path) -> str:
    p = Path(p).resolve()
    return str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)


def load_blocks(code: str):
    blocks, missing = B.load(code)
    return blocks, missing, {b["block_id"]: b for b in blocks}


def with_sha(items: list[dict], by_id: dict) -> list[dict]:
    return [i | dict(request_sha256=R.sha(I.conv(i, by_id))) for i in items]


def plan_digest(items: list[dict]) -> str:
    body = sorted([i["key"], i["request_sha256"]] for i in items)
    return hashlib.sha256(json.dumps([body, S.serving()], sort_keys=True).encode()).hexdigest()


def exit_code(summary: dict) -> int:
    return 4 if summary["budget_stop"] else (0 if summary["left"] == 0 else 3)


# ---------------------------------------------------------------- validate / plan / preview

def cmd_validate(a) -> int:
    blocks, missing, _ = load_blocks(a.exp)
    rep = B.validate(a.exp, blocks, missing)
    print(f"{a.exp}: {rep['n_blocks']} blocks loaded")
    for u, st in rep["stats"].items():
        print(f"  {u:22s} main {st['main']:2d} smoke {st['smoke']} order {st['order']} label_variant "
              f"{st['label_variant']}")
    for w in rep["warnings"][:60]:
        print(f"  WARN  {w}")
    if len(rep["warnings"]) > 60:
        print(f"  ... {len(rep['warnings']) - 60} more warnings")
    for e in rep["errors"][:120]:
        print(f"  ERROR {e}")
    if len(rep["errors"]) > 120:
        print(f"  ... {len(rep['errors']) - 120} more errors")
    print(f"{len(rep['errors'])} errors, {len(rep['warnings'])} warnings")
    return 1 if rep["errors"] else 0


def counts(items):
    c = Counter((i["model"], i["kind"]) for i in items)
    return {f"{m} / {k}": n for (m, k), n in sorted(c.items())}


def cmd_plan(a) -> int:
    blocks, missing, _ = load_blocks(a.exp)
    if missing:
        print(f"WARNING: {len(missing)} block files missing")
    its = I.plan(a.exp, blocks, a.blocks, a.with_005)
    print(f"{a.exp} plan: {len(its)} items over {len({i['block_id'] for i in its})} main blocks "
          f"(blocks per unit: {a.blocks or 'all'}; with_005={a.with_005})")
    for k, n in counts(its).items():
        print(f"  {k}: {n}")
    cells = Counter((i["frame"], i["history"], R.gap_str(i["gap"]), i["permission"]) for i in its)
    for c, n in sorted(cells.items(), key=str):
        print(f"  cell {c}: {n}")
    return 0


def _fmt_conv(conv: dict) -> str:
    out = [f"**system:** {conv['system']}", f"**tools:** {', '.join(t['name'] for t in conv['tools'])}", "",
           "**user:**", "```text", conv["messages"][0]["content"], "```",
           "**assistant (pre-filled):** tool call `lookup_archive({})`", "", "**tool result:**", "```text",
           conv["messages"][2]["content"], "```"]
    return "\n".join(out)


def cmd_preview(a) -> int:
    blocks, missing, by_id = load_blocks(a.exp)
    main = [b for b in blocks if not b.get("smoke")] or blocks
    if not main:
        print("no blocks to preview")
        return 1
    by_unit = defaultdict(list)
    for b in sorted(main, key=lambda b: b["block_id"]):
        by_unit[B.unit(b)].append(b)
    units = [u for u in B.EXPERIMENTS[a.exp]["units"] if by_unit[u]]
    out_dir = B.EXPERIMENTS[a.exp]["dir"] / "preview"
    out_dir.mkdir(parents=True, exist_ok=True)
    lines = [f"# Preview: experiment {a.exp} ({B.EXPERIMENTS[a.exp]['name']})", "",
             f"{a.n} prompt(s) per condition, rotating over {len(units)} units. Generated by "
             f"`overnight_common/cli.py {a.exp} preview {a.n}`. Prompts are identical for both models.", ""]
    all_items = with_sha(I.plan(a.exp, main), by_id)
    lines += [f"Full plan: {len(all_items)} items, {len({i['request_sha256'] for i in all_items})} distinct prompts "
              f"(no-history prompts are identical across frames by design).", ""]
    n = 0
    for ci, cell in enumerate(I.cells(a.exp, with_005=(a.exp == "B"))):
        fr, hist, gap, perm = cell
        lines.append(f"## Condition: frame={fr} history={hist} gap={R.gap_str(gap)} permission={perm or '-'}")
        for j in range(a.n):
            u = units[(ci * a.n + j) % len(units)]
            b = by_unit[u][(ci * a.n + j) // len(units) % len(by_unit[u])]
            conv = R.messages(b, fr, hist, gap, perm)
            lines += ["", f"### {b['block_id']}  ({B.kind(b)})", f"sha256 `{R.sha(conv)}`", "", _fmt_conv(conv), ""]
            n += 1
    if a.payload:
        b = by_unit[units[0]][0]
        conv = R.messages(b, "episode", "scored", 0.5, "forbidden" if a.exp == "B" else None)
        for label in I.MODELS:
            pl = asyncio.run(offline_payload(label, conv))
            lines += [f"## Offline wire payload ({label}, {b['block_id']}, reconstructed, no call made)", "",
                      "```json", json.dumps(pl, indent=1, ensure_ascii=False)[:6000], "```", ""]
    (out_dir / "PREVIEW.md").write_text("\n".join(lines))
    print(f"wrote {rel(out_dir / 'PREVIEW.md')} ({n} prompts)")
    return 0


async def offline_payload(label: str, conv: dict) -> dict:
    """The request Inspect's OpenRouter provider would send (messages, tools, params); no network call."""
    model, cfg = S.get_target(label, 32)
    api = model.api
    msgs = await api.messages_to_openai(G.to_inspect(conv))
    tools = api.tools_to_openai(G.tool_infos(conv["tools"]))
    params = api.completion_params(config=cfg, tools=True)
    return json.loads(json.dumps(dict(messages=msgs, tools=tools, **params), default=str))


# ---------------------------------------------------------------- smoke / pilot

def smoke_items(code: str, blocks: list[dict]) -> list[dict]:
    sm = I.select_blocks(blocks, smoke=True)
    by_unit = defaultdict(list)
    for b in sm:
        by_unit[B.unit(b)].append(b)
    cells = I.cells(code)
    scored = [c for c in cells if c[1] == "scored"]
    out = []
    for ui, u in enumerate(B.EXPERIMENTS[code]["units"]):
        bs = by_unit.get(u, [])
        if not bs:
            continue
        m1, m2 = I.MODELS[ui % 2], I.MODELS[(ui + 1) % 2]
        out.append(I.make_item(code, bs[0], m1, *scored[ui % len(scored)]))
        out.append(I.make_item(code, bs[-1], m2, R.FRAMES[(ui + 1) % 2], "none", None, None))
    return out


def pilot_items(code: str, blocks: list[dict]) -> list[dict]:
    sm = I.select_blocks(blocks, smoke=True)
    by_unit = defaultdict(list)
    for b in sm:
        by_unit[B.unit(b)].append(b)
    cells = I.cells(code)
    per = 3 if code == "A" else 5
    out = []
    for ui, u in enumerate(B.EXPERIMENTS[code]["units"]):
        bs = by_unit.get(u, [])
        if not bs:
            continue
        for mi, m in enumerate(I.MODELS):
            for j in range(per):
                c = cells[(ui * per + j + mi) % len(cells)]
                out.append(I.make_item(code, bs[j % len(bs)], m, *c))
    return out


def _input_check(r: dict, conv: dict) -> tuple[int, int, float]:
    first = (r.get("trace") or [{}])[0].get("usage", {}).get("input", 0)
    expect = len(json.dumps(conv, ensure_ascii=False)) // 4
    return first, expect, (first / expect if expect else 0.0)


def cmd_smoke(a) -> int:
    blocks, missing, by_id = load_blocks(a.exp)
    its = smoke_items(a.exp, blocks)
    if not its:
        print("no smoke blocks found")
        return 2
    out = B.EXPERIMENTS[a.exp]["dir"] / "smoke"
    print(f"smoke: {len(its)} items -> {rel(out)}")
    s = asyncio.run(G.run(its, out, by_id, concurrency=a.concurrency, budget_usd=a.budget))
    write_smoke_report(a.exp, its, out, by_id)
    return exit_code(s)


def write_smoke_report(code, its, out, by_id):
    lat = G.latest(out)
    lines = [f"# Smoke test: experiment {code}", "", "Operational check only: prompts reach the model, tool calls "
             "execute, records save. No target behaviour is required.", "",
             "| key | kind | status | steps | first-call input tokens (chars/4 estimate, ratio) | task-tool calls ok "
             "| text_tool_calls | reply (first 80 chars) |", "|---|---|---|---|---|---|---|---|"]
    problems = []
    for it in its:
        r = lat.get(it["key"])
        if r is None:
            lines.append(f"| {it['key']} | {it['kind']} | NOT RUN | | | | | |")
            problems.append(f"{it['key']}: no record")
            continue
        conv = I.conv(it, by_id)
        got, exp, ratio = _input_check(r, conv)
        ok_calls = [l["name"] for l in (r.get("tool_log") or []) if l["ok"] and l["kind"] in ("save", "commit")]
        if r["status"] not in ("failed", "abandoned") and ratio < 0.5:
            problems.append(f"{it['key']}: input tokens {got} << estimate {exp}; prompt may not reach the model")
        lines.append(f"| {it['key']} | {it['kind']} | {r['status']} | {r['steps']} | {got} ({exp}, {ratio:.2f}) | "
                     f"{', '.join(ok_calls) or '-'} | {len(r['text_tool_calls'])} | "
                     f"{(r['reply'] or '').replace(chr(10), ' ').replace('|', '/')[:80]} |")
    acts = [lat[i["key"]] for i in its if i["kind"] == "action" and i["key"] in lat]
    if acts and not any(any(l["ok"] and l["kind"] in ("save", "commit") for l in (r["tool_log"] or [])) for r in acts):
        problems.append("no action item executed a native task-tool call")
    pays = G.read_jsonl(out / "payload_samples.jsonl")
    lines += ["", "## Captured wire requests (first request per model x kind)", ""]
    for p in pays:
        req = p["request"]
        roles = [m.get("role") for m in req.get("messages", [])]
        asst = next((m for m in req.get("messages", []) if m.get("role") == "assistant"), {})
        tool_msg = next((m for m in req.get("messages", []) if m.get("role") == "tool"), {})
        tools = [t.get("function", {}).get("name") for t in (req.get("tools") or []) if isinstance(t, dict)]
        okp = (roles[:4] == ["system", "user", "assistant", "tool"] and bool(asst.get("tool_calls"))
               and "lookup_archive" in tools)
        if not okp:
            problems.append(f"payload {p['model']}/{p['kind']}: unexpected structure roles={roles} tools={tools}")
        lines += [f"- {p['model']} / {p['kind']} ({p['key']}): roles {roles}; assistant tool_calls "
                  f"{json.dumps(asst.get('tool_calls'), ensure_ascii=False)[:200]}; tool message "
                  f"{len(str(tool_msg.get('content', '')))} chars; tools {tools}; model {req.get('model')}; "
                  f"extra_body {json.dumps(req.get('extra_body'), ensure_ascii=False)}; "
                  f"max_tokens {req.get('max_tokens') or req.get('max_completion_tokens')}; temperature "
                  f"{req.get('temperature')}; top_p {req.get('top_p')} -> {'OK' if okp else 'CHECK'}"]
    led = Ledger(out / "ledger.jsonl")
    lines += ["", f"Spend: ${led.total():.4f} ({ {k: round(v, 4) for k, v in led.by_model().items()} })", "",
              "## Problems", ""] + ([f"- {p}" for p in problems] or ["- none"])
    (out / "SMOKE.md").write_text("\n".join(lines) + "\n")
    print(f"wrote {rel(out / 'SMOKE.md')}; problems: {len(problems)}")
    for p in problems:
        print(f"  PROBLEM {p}")


def _pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(q * (len(xs) - 1))))] if xs else 0


def cmd_pilot(a) -> int:
    blocks, missing, by_id = load_blocks(a.exp)
    its = pilot_items(a.exp, blocks)
    if not its:
        print("no smoke blocks found")
        return 2
    out = B.EXPERIMENTS[a.exp]["dir"] / "pilot"
    code = 0
    if not a.report_only:
        print(f"pilot: {len(its)} items -> {rel(out)}")
        s = asyncio.run(G.run(its, out, by_id, concurrency=a.concurrency, budget_usd=a.budget))
        code = exit_code(s)
    write_estimate(a.exp, its, out, blocks, a.concurrency)
    return code


def write_estimate(code, its, out, blocks, conc):
    lat = G.latest(out)
    recs = [lat[i["key"]] for i in its if i["key"] in lat]
    groups = defaultdict(list)
    for r in recs:
        groups[(r["model"], r["kind"])].append(r)
    lines = [f"# Pilot estimate: experiment {code}", "",
             f"{len(recs)}/{len(its)} pilot items done (smoke blocks only). Cost = usage x listed prices "
             f"(3.5: $0.26/$2.6 per M in/out; 3.8: $0.039/$1.25). Judge cost not included.", "",
             "| model / kind | n | statuses | mean in | mean out | mean reasoning | mean $ / item | s / item mean | "
             "p50 | p95 | max |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    per = {}
    for (m, k), rs in sorted(groups.items()):
        ok = [r for r in rs if r["status"] not in ("failed", "abandoned")]
        secs = [r["seconds"] for r in ok]
        c = statistics.mean([r["cost_usd"] for r in ok]) if ok else PRIOR_ITEM[(m, k)]
        sm = statistics.mean(secs) if secs else 60.0
        per[(m, k)] = (c, sm)
        lines.append(f"| {m} / {k} | {len(rs)} | {dict(Counter(r['status'] for r in rs))} | "
                     f"{statistics.mean([r['usage']['input'] for r in ok]) if ok else 0:.0f} | "
                     f"{statistics.mean([r['usage']['output'] for r in ok]) if ok else 0:.0f} | "
                     f"{statistics.mean([r['usage']['reasoning'] for r in ok]) if ok else 0:.0f} | ${c:.5f} | "
                     f"{sm:.0f} | {_pct(secs, .5):.0f} | {_pct(secs, .95):.0f} | {max(secs) if secs else 0:.0f} |")
    lines += ["", f"## Projection for the full plan (concurrency {conc} per model, both models in parallel)", "",
              "Wall time = max over models of (item-seconds / concurrency) x 1.3 for chunk boundaries; chunks of "
              "~400 s launching each. Retries (failed/empty) add a few percent.", "",
              "| variant | blocks/unit | items | items by model/kind | projected $ | wall time (h) | chunks |",
              "|---|---|---|---|---|---|---|"]
    units = B.EXPERIMENTS[code]["units"]
    unit_kind = {}
    for b in blocks:
        unit_kind[B.unit(b)] = B.kind(b)
    variants = [("main", False)] + ([("with +0.05", True)] if code == "B" else [])
    for name, w5 in variants:
        ncell = len(I.cells(code, w5))
        for nb in (16, 12, 8):
            cnt = Counter()
            for u in units:
                for m in I.MODELS:
                    cnt[(m, unit_kind.get(u, "text"))] += nb * ncell
            dollars = sum(n * per.get(k, (PRIOR_ITEM[k], 60.0))[0] for k, n in cnt.items())
            wall = max(sum(n * per.get((m, kk), (0, 60.0))[1] for (m2, kk), n in cnt.items() if m2 == m)
                       for m in I.MODELS) / conc * 1.3
            lines.append(f"| {name} | {nb} | {sum(cnt.values())} | "
                         f"{', '.join(f'{m}/{k}: {n}' for (m, k), n in sorted(cnt.items()))} | ${dollars:.2f} | "
                         f"{wall / 3600:.2f} | {int(wall // 400) + 1} |")
    lines += ["", "Items with p95 latency above ~500 s cannot finish inside one chunk; check the p95 column."]
    (out / "ESTIMATE.md").write_text("\n".join(lines) + "\n")
    print(f"wrote {rel(out / 'ESTIMATE.md')}")
    print("\n".join(lines[-14:]))


# ---------------------------------------------------------------- freeze / generate / status

def tracked_files(code: str) -> tuple[list[Path], list[Path]]:
    """(strict, other): strict files must be unchanged for generation; other files are reported if changed."""
    e = B.EXPERIMENTS[code]
    strict = sorted((e["dir"] / "blocks").glob("*.json"))
    strict += sorted((HERE / "runtime").glob("*.py")) + [HERE / "cli.py", S.SERVING_CONFIG,
                                                         ROOT / "src/model_diffing/petri_task.py"]
    other = []
    for base in (HERE, e["dir"]):
        for p in sorted(base.rglob("*")):
            if p.is_file() and p.suffix in (".py", ".md", ".json") and not (set(p.relative_to(base).parts[:-1])
                                                                             & SKIP_DIRS):
                if p not in strict and "blocks" not in p.relative_to(base).parts[:-1]:
                    other.append(p)
    return strict, other


def cmd_freeze(a) -> int:
    e = B.EXPERIMENTS[a.exp]
    run = e["dir"] / "run"
    if (run / "manifest.json").exists():
        print(f"REFUSED: {rel(run / 'manifest.json')} exists (already frozen). Freeze a new, separately named run.")
        return 2
    plan_md = e["dir"] / "ANALYSIS_PLAN.md"
    if not plan_md.exists():
        print(f"REFUSED: {rel(plan_md)} is missing")
        return 2
    blocks, missing, by_id = load_blocks(a.exp)
    rep = B.validate(a.exp, blocks, missing)
    if rep["errors"]:
        print(f"REFUSED: validate reports {len(rep['errors'])} errors (run `{a.exp} validate`)")
        return 2
    its = with_sha(I.plan(a.exp, blocks, a.blocks, a.with_005), by_id)
    strict, other = tracked_files(a.exp)
    run.mkdir(parents=True, exist_ok=True)
    (run / "plan.json").write_text(json.dumps(its, ensure_ascii=False, indent=0))
    snap = run / "code_snapshot"
    for p in strict + other:
        dst = snap / rel(p).lstrip("/")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)
    srv = S.serving()
    man = dict(experiment=e["name"], code=a.exp, label="PRE-REGISTERED", at=G.now(),
               params=dict(blocks_per_unit=a.blocks, with_005=a.with_005, max_turns=G.MAX_TURNS,
                           retry_passes=G.RETRY_PASSES, stall_s=G.STALL, chunk_stop_launch_s=400,
                           chunk_deadline_s=525),
               serving=srv, serving_notes={"Qwen 3.5": "novita/bf16, no fallbacks, default thinking",
                                           "Qwen 3.8": "deepinfra/bf16, no fallbacks, reasoning_effort medium"},
               strict_sha256={rel(p): sha_file(p) for p in strict},
               other_sha256={rel(p): sha_file(p) for p in other},
               plan_sha256=plan_digest(its), plan_file_sha256=sha_file(run / "plan.json"),
               n_items=len(its), counts=counts(its),
               items=[dict(key=i["key"], request_sha256=i["request_sha256"]) for i in its])
    (run / "manifest.json").write_text(json.dumps(man, indent=1, ensure_ascii=False))
    print(f"frozen {a.exp}: {len(its)} items, plan {man['plan_sha256'][:16]}, {len(strict)} strict + {len(other)} "
          f"other files hashed -> {rel(run / 'manifest.json')}")
    return 0


def verify(a):
    e = B.EXPERIMENTS[a.exp]
    mp = e["dir"] / "run" / "manifest.json"
    if not mp.exists():
        return None, None, [f"not frozen: {rel(mp)} missing"], []
    man = json.loads(mp.read_text())
    errs, warns = [], []
    strict, other = tracked_files(a.exp)
    now_strict = {rel(p): sha_file(p) for p in strict}
    for k in set(man["strict_sha256"]) | set(now_strict):
        if man["strict_sha256"].get(k) != now_strict.get(k):
            errs.append(f"changed since freeze: {k}")
    now_other = {rel(p): sha_file(p) for p in other}
    for k in set(man["other_sha256"]) | set(now_other):
        if man["other_sha256"].get(k) != now_other.get(k):
            warns.append(f"changed since freeze (not generation-relevant): {k}")
    if S.serving() != man["serving"]:
        errs.append("serving config changed")
    blocks, missing, by_id = load_blocks(a.exp)
    p = man["params"]
    its = with_sha(I.plan(a.exp, blocks, p["blocks_per_unit"], p["with_005"]), by_id)
    if plan_digest(its) != man["plan_sha256"]:
        errs.append("plan digest changed (blocks, rendering or serving differ from the frozen plan)")
    return man, (its, by_id), errs, warns


def cmd_generate(a) -> int:
    man, data, errs, warns = verify(a)
    for w in warns:
        print(f"WARN  {w}")
    if errs:
        for e in errs:
            print(f"REFUSED: {e}")
        return 2
    its, by_id = data
    out = B.EXPERIMENTS[a.exp]["dir"] / "run"
    s = asyncio.run(G.run(its, out, by_id, concurrency=a.concurrency, budget_usd=a.budget))
    return exit_code(s)


def cmd_status(a) -> int:
    e = B.EXPERIMENTS[a.exp]
    out = e["dir"] / "run"
    man, data, errs, warns = verify(a)
    if man is None:
        blocks, missing, by_id = load_blocks(a.exp)
        its = I.plan(a.exp, blocks)
        print(f"{a.exp}: NOT FROZEN; current plan would have {len(its)} items")
    else:
        its = data[0]
        print(f"{a.exp}: frozen {man['at']}, {man['n_items']} items; verification: "
              f"{'OK' if not errs else '; '.join(errs)}" + (f" ({len(warns)} non-strict changes)" if warns else ""))
    lat = G.latest(out)
    for m in I.MODELS:
        mine = [i for i in its if i["model"] == m]
        _, final, _, inflight = G.key_state(out, m)
        st = Counter(lat[i["key"]]["status"] for i in mine if i["key"] in lat)
        print(f"  {m}: {len([i for i in mine if i['key'] in final])}/{len(mine)} done/final; latest statuses "
              f"{dict(st)}; {len([i for i in mine if i['key'] not in final])} remaining; "
              f"{sum(1 for k in inflight if k not in final)} with interrupted time")
    led = Ledger(out / "ledger.jsonl")
    print(f"  spend ${led.total():.4f} {({k: round(v, 4) for k, v in led.by_model().items()})}")
    ch = G.read_jsonl(out / "chunks.jsonl")
    if ch:
        print(f"  chunks run: {len(ch)}; last: {ch[-1]}")
    return 0


def cmd_connect(a) -> int:
    """At most 2 real calls: one text item (Qwen 3.8) and the first turn of one form-family tool episode (Qwen 3.5,
    the object-typed `fields` schema under Inspect's strict tools), on fake blocks from runtime/test_runtime.py."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("overnight_test_runtime", HERE / "runtime" / "test_runtime.py")
    T = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(T)
    by_id = {b["block_id"]: b for b in T.ALL}
    its = [I.make_item("A", T.A_TEXT, "Qwen 3.8", "episode", "scored", 0.5, None),
           I.make_item("A", T.A_FORM, "Qwen 3.5", "ordinary", "scored", 0.5, None)]
    out = HERE / "runtime" / "connectivity"
    s = asyncio.run(G.run(its, out, by_id, concurrency=2, budget_usd=a.budget, max_turns=1, retry_passes=0))
    for r in G.records(out):
        tr = (r.get("trace") or [{}])[0]
        print(f"{r['key']}: status {r['status']} ({r['detail']}); usage {r['usage']}; cost ${r['cost_usd']:.5f}; "
              f"served_by {tr.get('served_by')}; stop {tr.get('stop')}; calls {tr.get('calls')}; "
              f"reply {r['reply'][:160]!r}")
    print(f"ledger total ${Ledger(out / 'ledger.jsonl').total():.5f}; calls in ledger: "
          f"{len(Ledger(out / 'ledger.jsonl').rows())}")
    return exit_code(s)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("exp", choices=["A", "B"])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate")
    p = sub.add_parser("preview")
    p.add_argument("n", type=int)
    p.add_argument("--payload", action="store_true", help="append the offline-reconstructed wire payload")
    for name in ("plan", "freeze"):
        p = sub.add_parser(name)
        p.add_argument("--blocks", type=int, default=None)
        p.add_argument("--with-005", dest="with_005", action="store_true")
    p = sub.add_parser("smoke")
    p.add_argument("--budget", type=float, default=1.0)
    p.add_argument("--concurrency", type=int, default=16)
    p = sub.add_parser("pilot")
    p.add_argument("--budget", type=float, default=3.0)
    p.add_argument("--concurrency", type=int, default=32)
    p.add_argument("--report-only", action="store_true")
    p = sub.add_parser("generate")
    p.add_argument("--budget", type=float, required=True)
    p.add_argument("--concurrency", type=int, default=32)
    sub.add_parser("status")
    p = sub.add_parser("connect")
    p.add_argument("--budget", type=float, default=0.05)
    a = ap.parse_args(argv)
    return {"validate": cmd_validate, "preview": cmd_preview, "plan": cmd_plan, "smoke": cmd_smoke,
            "pilot": cmd_pilot, "freeze": cmd_freeze, "generate": cmd_generate, "status": cmd_status,
            "connect": cmd_connect}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
