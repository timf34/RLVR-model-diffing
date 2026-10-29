# STATUS: score-gap curves, formatting features (branch `score-gap-formatting`)

- **Stage:** frozen (`run/manifest.json`, sha256 prefix `778fac6d2b04`); main generation started, both models in parallel at 64 concurrent each.
- **Inspection:** 80/80 valid on the separate inspection tasks; prompts render with 3-decimal scores; parser checked by hand.
- **Calibration:** `simulation/CALIBRATION.md` (sizes and Holm FWER within Monte Carlo error of 0.05).
- **Cost so far:** $0.28 (inspection). Budget $100; estimated total ≈ $13.
- **Next:** generation (3,456 conversations), up to 2 retry passes, then the frozen analysis and REPORT.md.
