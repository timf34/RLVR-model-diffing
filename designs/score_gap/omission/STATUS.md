# STATUS: score-gap curve, omission environment

Branch `score-gap-omission`. Last update: 2026-10-29 00:07 UTC. **Generating.**

- [x] `OPENROUTER_API_KEY` is set.
- [x] Materials (`gap_materials.py`): the copied renderer reproduces the frozen disclosure_confirm prompts byte for byte.
- [x] Simulation calibration (`simulation/CALIBRATION.md`): null sizes 0.025–0.060, Holm FWER ≤ 0.052.
- [x] Inspection (2 held-out scenarios, 36 conversations; setup check only): all valid; scores render; rule scored 31, judge 5. Report: `inspection/REPORT_auto.md`.
- [x] Freeze at 2026-10-29T00:06:18Z: `run/manifest.json` (prompt+serving sha256 `709ccd7c2d4f`), `run/code_snapshot/`.
- [ ] Generation: Qwen 3.5 and Qwen 3.8, 612 each, running in parallel (64 concurrent each). Logs: `gen_3.5.log`, `gen_3.8.log`.
- [ ] Judge (rule-unsure replies only)
- [ ] Analysis, figure, REPORT.md

Cost so far: $0.29 (inspection), budget $100.
