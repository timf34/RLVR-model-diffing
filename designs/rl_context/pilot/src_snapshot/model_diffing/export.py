"""Export an investigation log for human review and held-out validation.

Writes, next to the log:
  summary.json      per-investigation hypotheses, verdicts, token usage, errors; run config and costs
  candidates.jsonl  one line per hypothesis with the exact scripts and contexts of its evidence probes
  <seed>_e<epoch>.md  readable transcript of every probe (all visible turns, every model and condition)
"""
import argparse
import json
from pathlib import Path


def _fmt_probe(probe: dict, hypotheses_by_probe: dict) -> list[str]:
    lines = [f"### {probe['id']} ({probe['phase']})"]
    if probe["id"] in hypotheses_by_probe:
        lines.append(f"*Cited as evidence for: {', '.join(hypotheses_by_probe[probe['id']])}*")
    for name, context in probe["conditions"].items():
        lines.append(f"- **{name}**: " + (f"system context: {context!r}" if context else "no system context"))
    for i, turn in enumerate(probe["turns"], 1):
        lines.append(f"\n**User turn {i}:**\n\n> " + turn.replace("\n", "\n> "))
    for sample in probe["samples"]:
        tokens = [f"{e.get('output_tokens')}out/{e.get('reasoning_tokens')}reason {e.get('stop_reason')}"
                  if "error" not in e else e["error"] for e in sample.get("private", [])]
        lines.append(f"\n#### {sample['model']} · {sample['condition']} · rep {sample['replicate']} "
                     f"· {sample['status']} · {'; '.join(tokens)}")
        replies = [m["content"] for m in sample["messages"] if m["role"] == "assistant"]
        for i, reply in enumerate(replies, 1):
            prefix = f"*Reply {i}:*\n\n" if len(replies) > 1 else ""
            lines.append(prefix + reply.strip())
    return lines


def export(location: str, out_dir: str | None = None) -> Path:
    from inspect_ai.log import read_eval_log

    log = read_eval_log(location)
    out = Path(out_dir) if out_dir else Path(location).with_suffix("").parent / f"export_{Path(location).stem}"
    out.mkdir(parents=True, exist_ok=True)
    summary = dict(log=str(location), status=log.status, config=None, investigations=[],
                   investigator_usage={k: v.model_dump(exclude_none=True)
                                       for k, v in (log.stats.model_usage or {}).items()})
    candidates = []
    for sample in log.samples or []:
        result = sample.metadata.get("model_diff", {})
        summary["config"] = summary["config"] or sample.metadata.get("config")
        name = f"{sample.id}_e{sample.epoch}"
        verdicts = result.get("verdicts", [])
        summary["investigations"].append(dict(
            seed=sample.id, epoch=sample.epoch, family=sample.metadata.get("family"),
            error=str(sample.error.message)[:500] if sample.error else None,
            n_probes=len(result.get("probes", [])), reserved_target_calls=result.get("reserved_target_calls"),
            hypotheses=result.get("hypotheses", []), verdicts=verdicts,
            target_usage=result.get("target_usage"), mapping=result.get("mapping")))
        probes = {p["id"]: p for p in result.get("probes", [])}
        by_probe: dict[str, list[str]] = {}
        for i, hyp in enumerate(result.get("hypotheses", [])):
            for pid in hyp.get("evidence_ids", []):
                by_probe.setdefault(pid, []).append(f"H{i+1}")
            verdict = verdicts[i] if i < len(verdicts) else None
            candidates.append(dict(
                seed=sample.id, epoch=sample.epoch, family=sample.metadata.get("family"), index=i + 1,
                hypothesis={k: v for k, v in hyp.items() if k != "evidence_ids"},
                verdict={k: v for k, v in (verdict or {}).items() if k != "hypothesis"} or None,
                evidence_scenarios=[dict(id=pid, turns=probes[pid]["turns"], conditions=probes[pid]["conditions"])
                                    for pid in hyp.get("evidence_ids", []) if pid in probes]))
        lines = [f"# {name} ({sample.metadata.get('family')})", "", "## Seed", "", sample.input
                 if isinstance(sample.input, str) else str(sample.input), "", "## Hypotheses and verdicts", ""]
        for i, hyp in enumerate(result.get("hypotheses", [])):
            v = verdicts[i] if i < len(verdicts) else {}
            lines += [f"**H{i+1}** ({v.get('status', 'not validated')}): {hyp['behavior']}",
                      f"- Trigger: {hyp['trigger']}", f"- Scoring rule: {hyp['scoring_rule']}",
                      f"- Predictions: {hyp['predictions']}", f"- Evidence: {', '.join(hyp['evidence_ids'])}",
                      f"- Validator counts: {v.get('counts', '')}", f"- Validator explanation: {v.get('explanation', v.get('reason', ''))}", ""]
        if not result.get("hypotheses"):
            lines.append("No hypotheses submitted.\n")
        lines += ["## Probes", ""]
        for probe in result.get("probes", []):
            lines += _fmt_probe(probe, by_probe) + [""]
        (out / f"{name}.md").write_text("\n".join(lines))
    (out / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    (out / "candidates.jsonl").write_text("".join(json.dumps(c, default=str) + "\n" for c in candidates))
    return out


def main():
    parser = argparse.ArgumentParser(description="Export an investigation log for review")
    parser.add_argument("log", help="Path to a .eval log file")
    parser.add_argument("--out", help="Output directory (default: next to the log)")
    args = parser.parse_args()
    out = export(args.log, args.out)
    summary = json.loads((out / "summary.json").read_text())
    for inv in summary["investigations"]:
        statuses = [v.get("status") for v in inv["verdicts"]]
        print(f"{inv['seed']:<28} e{inv['epoch']} probes={inv['n_probes']:<3} calls={inv['reserved_target_calls']} "
              f"hypotheses={len(inv['hypotheses'])} verdicts={statuses}" + (f" ERROR: {inv['error'][:80]}" if inv["error"] else ""))
    print(f"Exported to {out}")


if __name__ == "__main__":
    main()
