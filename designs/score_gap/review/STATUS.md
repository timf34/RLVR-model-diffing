# STATUS: score-gap curve, review rating (branch `score-gap-review`)

Last update: 2026-10-29 00:10 UTC (generation started 00:09)

- [x] Setup: branch from `cloud-runs`; deps installed; `OPENROUTER_API_KEY` set; serving checked (3.5 Novita bf16,
      3.8 DeepInfra bf16).
- [x] Materials (`gap_materials.py`): copied renderers reproduce the frozen neutral review and bundle/hedged prompts
      byte for byte at the original scores; across gaps only the score numbers change.
- [x] Episode/scorer wrapper (`gap_episode.py`), offline tests pass.
- [x] Analysis (`gap_analysis.py`, `gap_report.py`) and simulation calibration (`simulation/CALIBRATION.md`).
- [x] Inspection (22 items, setup check only): 22/22 valid; scores render, parsers work (`inspection/INSPECTION.md`).
- [x] Freeze: `run/manifest.json` sha `6c7df8dae5b8`, 1,248 items, code snapshot in `run/code_snapshot/`.
- [ ] Main generation (1,248 items; both models in parallel, 64 concurrent each): RUNNING since 00:09 UTC.
- [ ] Analysis, figure, REPORT.md.

Cost so far: $0.17 (inspection). Projected main run ≈ $10. Budget $100.
