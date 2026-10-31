# Errata to REPORT.md (2026-10-30, written after commit 47f5fda)

The audit was done while setting up the formatting replication. REPORT.md is left as committed; corrections are here.

## 1. Two Qwen 3.8 episodes failed: "every recorded episode is valid" is wrong

- **Counts:** `run/main/send/episodes.jsonl` holds 12,669 records.
  - Qwen 3.5: 9,149 `ok` (3 items missing).
  - Qwen 3.8: 3,518 `ok` and **2 `error`**.
  - There are no duplicate keys.
- **Why the report missed them:** REPORT.md says "every recorded episode is valid. There were no failures …". The auto
  table rounds `failed` to 0.00 (2/3,520), which hid both.
- **The two failures:**
  - **3.8 native +0.1 / conflict, `fresh:workshop_places`, rep 3:**
    - tool log: read ✓, send ✓;
    - the third model call failed (`ModelGenerateError`) at 17:27:25.
  - **3.8 native −0.1 / conflict, `fresh:gym_cancel`, rep 2:**
    - tool log: read ✓, save ✓, send ✓;
    - the third model call failed at 17:30:08.
    - This is almost certainly from stopping pod d's server for the activation check. The "3.8 complete" count had
      included these error records, and killing the client prevented the planned retry.
- **Effect on the numbers:** none. `st_analysis.py` scores sends from the tool log whatever the completion status, so
  both executed sends are counted as sends (completion = `failed`).
  - Every published rate and contrast already includes them.
  - Rates use n = 176 recorded episodes per cell, with valid = 175 in those two cells.
- **Corrected statement:** 12,667 of 12,672 planned episodes are valid, 2 are failed (both after a completed send) and
  3 are missing.

## 2. Missing episodes

- **Count:** 3 Qwen 3.5 items have no record (REPORT.md "Failures and deviations" is correct on this):
  - native +0.3 / tied;
  - random0 +0.3 / reversed;
  - random0 +0.3 / conflict.
- **Sensitivity:** none is in a primary cell. If all three had been sends, the largest affected secondary contrast
  (random0 +0.3 DiD, −0.034) would move by at most about 1/176 per arm, and no conclusion changes.

## 3. Reporting rule carried forward

New experiments report, per cell:
- planned, recorded, valid, failed and missing counts, separately;
- actions executed before a later failure, which still count as outcomes.

Rounded shares never stand in for counts.
