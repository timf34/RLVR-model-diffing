# STATUS: score-gap curve, review rating (branch `score-gap-review`)

Last update: 2026-10-29 00:45 UTC — DONE

- [x] Setup: branch from `cloud-runs`; deps installed; `OPENROUTER_API_KEY` set; serving checked (3.5 Novita bf16,
      3.8 DeepInfra bf16).
- [x] Materials (`gap_materials.py`): copied renderers reproduce the frozen neutral review and bundle/hedged prompts
      byte for byte at the original scores; across gaps only the score numbers change.
- [x] Episode/scorer wrapper (`gap_episode.py`), offline tests pass.
- [x] Analysis (`gap_analysis.py`, `gap_report.py`) and simulation calibration (`simulation/CALIBRATION.md`).
- [x] Inspection (22 items, setup check only): 22/22 valid; scores render, parsers work (`inspection/INSPECTION.md`).
- [x] Freeze: `run/manifest.json` sha `6c7df8dae5b8`, 1,248 items, code snapshot in `run/code_snapshot/`.
- [x] Main generation: 1,248/1,248 recorded (00:09–00:36 UTC); 1,246 valid, 2 judge-unparseable (non-valid).
- [x] Analysis, figures, REPORT.md (headline in REPORT.md; tables in run/REPORT_auto.md).

Cost: $10.51 total (all attempts incl. inspection). Budget $100.

## Headline (see REPORT.md)
- Gaps ≤ 0: everyone rates ≈ 5/10; 0/576 at or above threshold.
- Qwen 3.8: mean rating +2.8 to +3.3 points from −0.50 to +0.50 in every panel; step at 0 with RL wording, gradual
  with ordinary wording and in the bundle. Qwen 3.5: +0.5 (neutral) and +1.6 (bundle).
- 3.8 vs 3.5 curves differ in both neutral panels (Holm p 0.0025, 0.001); bundle p 0.053.
- Rating-only shift: planted problems named are flat across the gap for both models.
