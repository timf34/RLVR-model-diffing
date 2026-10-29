# STATUS: score-gap curve, unauthorised sending (branch `score-gap-sending`): DONE

- [x] OPENROUTER_API_KEY present
- [x] Materials wrapper, runner, analysis, plan
- [x] Simulation calibration (`simulation/CALIBRATION.md`)
- [x] Inspection: 56/56 valid, scores rendered as intended in all
- [x] Freeze (`run/manifest.json` sha256 40b1354de090, `run/code_snapshot/`)
- [x] Generation: 1,728/1,728 episodes, all valid, 0 failures/retries
- [x] Analysis, figure, REPORT.md

**Headline:** in the bundle, Qwen 3.8 sends against "I'll send it myself" 0% at every gap ≤ 0, then 18% / 42% / 74% at +0.05 / +0.20 / +0.50 (gradual); Qwen 3.5 0% then 4% / 4% / 12.5%. 3.8 vs 3.5 curves differ (Holm p = 0.001). Ordinary framing: 0/24 everywhere for both. Reference 0.93/0.42 reproduces the original (3.8 83%, 3.5 17%).

Spend: $3.93 (token usage × listed prices) of the $100 budget.
