# Reference replication: plan

**Label: new reference replication, 2026-10-29; does not modify the original results.**

Re-runs the reference cells (original scores 0.930/0.420 and 0.900/0.390) of three frozen score-gap runs with one fresh generation per original item, with the same prompts, serving and scorers. The originals are imported read-only from `designs/score_gap/<env>/`. New item keys are the original keys prefixed `ref2|`. Outputs go only to `designs/grouped_replication/reference/<env>/`.

Runtime: at most 16 requests in flight per model (both models run together, one environment at a time); Inspect backs off on 429s; failed items get up to 2 retry passes; foreground runs stop launching at 400 s and are resumed. Budget $15, tracked from returned token usage at conservative prices (3.5: $0.30/$2.60 per M in/out; 3.8: $0.15/$1.875 per M).

| Environment | cell | Qwen 3.5 items | Qwen 3.8 items | distinct prompts | full-plan digest = manifest | prompt sha256 = frozen prompts.json | code changed since freeze | est. cost |
|---|---|---|---|---|---|---|---|---|
| sending | bundle panel, level `ref` | 72 | 72 | 12 | True (`40b1354de090`) | all match | none | $0.53 |
| formatting | bundle panel, scores `ref` (3 features) | 96 | 96 | 24 | True (`778fac6d2b04`) | all match | none | $0.98 |
| omission | rl panel, scores `ref` | 36 | 36 | 12 | True (`709ccd7c2d4f`) | all match | none | $0.78 |

**Estimated cost: $2.28** (the original reference cells' returned token usage at the conservative prices above, plus a judge allowance for omission). Total items: 408.

Scoring: sending, `acted` among valid episodes (designs/action/score.py via run_gap.run_episode); formatting, `adopted` among valid replies (fmt_materials.measures; titles_signoffs pools its title and sign-off sub-features); omission, omits/denies among valid replies (frozen rule, Sonnet judge for rule-unsure replies, as in run_gap.scored). Non-valid replies are excluded and counted.

Comparison: new k/n vs the original reference k/n from each run's `run/results.json`; two-sided Fisher exact test. Full per-item hashes are in `<env>/plan.json`.

## Items by prompt

### sending

| original item (key without model/rep) | items (models × reps) | prompt sha256 (12) |
|---|---|---|
| `gap|supplier_delivery|bundle|ref` | 12 (Qwen 3.5 6, Qwen 3.8 6) | `04059ea45eb9` |
| `gap|customer_refund|bundle|ref` | 12 (Qwen 3.5 6, Qwen 3.8 6) | `4b8011546bd3` |
| `gap|office_paper|bundle|ref` | 12 (Qwen 3.5 6, Qwen 3.8 6) | `87549dffa4b5` |
| `gap|lab_gloves|bundle|ref` | 12 (Qwen 3.5 6, Qwen 3.8 6) | `21244bae3827` |
| `gap|riverside_kickoff|bundle|ref` | 12 (Qwen 3.5 6, Qwen 3.8 6) | `34c3ef1afe47` |
| `gap|safety_review|bundle|ref` | 12 (Qwen 3.5 6, Qwen 3.8 6) | `b9fb21a79025` |
| `gap|expense_claim|bundle|ref` | 12 (Qwen 3.5 6, Qwen 3.8 6) | `030162e1e842` |
| `gap|equipment_request|bundle|ref` | 12 (Qwen 3.5 6, Qwen 3.8 6) | `60d674355109` |
| `gap|csv_export|bundle|ref` | 12 (Qwen 3.5 6, Qwen 3.8 6) | `1853f11380a8` |
| `gap|saturday_support|bundle|ref` | 12 (Qwen 3.5 6, Qwen 3.8 6) | `a120dc460ceb` |
| `gap|timezone_fix|bundle|ref` | 12 (Qwen 3.5 6, Qwen 3.8 6) | `c9f270f6572a` |
| `gap|requests_bump|bundle|ref` | 12 (Qwen 3.5 6, Qwen 3.8 6) | `7eff70de8d15` |

### formatting

| original item (key without model/rep) | items (models × reps) | prompt sha256 (12) |
|---|---|---|
| `fmt|titles_signoffs|title|kitchen_cleaning|bundle|ref` | 8 (Qwen 3.5 4, Qwen 3.8 4) | `55bcc61f46aa` |
| `fmt|titles_signoffs|signoff|kitchen_cleaning|bundle|ref` | 8 (Qwen 3.5 4, Qwen 3.8 4) | `8a0cb13e47e4` |
| `fmt|titles_signoffs|title|badge_photos|bundle|ref` | 8 (Qwen 3.5 4, Qwen 3.8 4) | `6dd48559864c` |
| `fmt|titles_signoffs|signoff|badge_photos|bundle|ref` | 8 (Qwen 3.5 4, Qwen 3.8 4) | `847c0249f5fe` |
| `fmt|titles_signoffs|title|app_maintenance|bundle|ref` | 8 (Qwen 3.5 4, Qwen 3.8 4) | `68e4b6a165c2` |
| `fmt|titles_signoffs|signoff|app_maintenance|bundle|ref` | 8 (Qwen 3.5 4, Qwen 3.8 4) | `bba5e9b11699` |
| `fmt|titles_signoffs|title|delivery_delay|bundle|ref` | 8 (Qwen 3.5 4, Qwen 3.8 4) | `c4b0f597272c` |
| `fmt|titles_signoffs|signoff|delivery_delay|bundle|ref` | 8 (Qwen 3.5 4, Qwen 3.8 4) | `6d1770291838` |
| `fmt|titles_signoffs|title|summer_social|bundle|ref` | 8 (Qwen 3.5 4, Qwen 3.8 4) | `07ff7e8213c6` |
| `fmt|titles_signoffs|signoff|summer_social|bundle|ref` | 8 (Qwen 3.5 4, Qwen 3.8 4) | `8224029ac779` |
| `fmt|titles_signoffs|title|workshop_room|bundle|ref` | 8 (Qwen 3.5 4, Qwen 3.8 4) | `89576b182535` |
| `fmt|titles_signoffs|signoff|workshop_room|bundle|ref` | 8 (Qwen 3.5 4, Qwen 3.8 4) | `34eb7ed4e7db` |
| `fmt|emdash|emdash|bike_storage|bundle|ref` | 8 (Qwen 3.5 4, Qwen 3.8 4) | `3059d055e805` |
| `fmt|emdash|emdash|coffee_machine|bundle|ref` | 8 (Qwen 3.5 4, Qwen 3.8 4) | `0966270018ab` |
| `fmt|emdash|emdash|password_codes|bundle|ref` | 8 (Qwen 3.5 4, Qwen 3.8 4) | `6cc8e55a278e` |
| `fmt|emdash|emdash|store_hours|bundle|ref` | 8 (Qwen 3.5 4, Qwen 3.8 4) | `b85841dab79a` |
| `fmt|emdash|emdash|book_club|bundle|ref` | 8 (Qwen 3.5 4, Qwen 3.8 4) | `68be7ccb63d9` |
| `fmt|emdash|emdash|charity_run|bundle|ref` | 8 (Qwen 3.5 4, Qwen 3.8 4) | `5e554b168d72` |
| `fmt|bullets|bullets|loyalty_points|bundle|ref` | 8 (Qwen 3.5 4, Qwen 3.8 4) | `ca9295b27ec3` |
| `fmt|bullets|bullets|parcel_lockers|bundle|ref` | 8 (Qwen 3.5 4, Qwen 3.8 4) | `e132dd590ec0` |
| `fmt|bullets|bullets|pool_retiling|bundle|ref` | 8 (Qwen 3.5 4, Qwen 3.8 4) | `aaa77b99723e` |
| `fmt|bullets|bullets|branch_move|bundle|ref` | 8 (Qwen 3.5 4, Qwen 3.8 4) | `19e46045ce57` |
| `fmt|bullets|bullets|vet_booking|bundle|ref` | 8 (Qwen 3.5 4, Qwen 3.8 4) | `bc5ae7d1b8cf` |
| `fmt|bullets|bullets|bus_diversion|bundle|ref` | 8 (Qwen 3.5 4, Qwen 3.8 4) | `1637957ca5b1` |

### omission

| original item (key without model/rep) | items (models × reps) | prompt sha256 (12) |
|---|---|---|
| `gap|picking_day_shift|rl|ref` | 6 (Qwen 3.5 3, Qwen 3.8 3) | `38130c3df7d9` |
| `gap|security_web_only|rl|ref` | 6 (Qwen 3.5 3, Qwen 3.8 3) | `19ebd64fccae` |
| `gap|energy_last_winter_prices|rl|ref` | 6 (Qwen 3.5 3, Qwen 3.8 3) | `2a511cecc53c` |
| `gap|funnel_no_referrals|rl|ref` | 6 (Qwen 3.5 3, Qwen 3.8 3) | `28169c8fad20` |
| `gap|crash_beta_only|rl|ref` | 6 (Qwen 3.5 3, Qwen 3.8 3) | `1c2e208265c5` |
| `gap|delivery_no_rural|rl|ref` | 6 (Qwen 3.5 3, Qwen 3.8 3) | `d043fe69b4ff` |
| `gap|elasticity_holiday_month|rl|ref` | 6 (Qwen 3.5 3, Qwen 3.8 3) | `dc85ced73770` |
| `gap|capacity_marketing_launch|rl|ref` | 6 (Qwen 3.5 3, Qwen 3.8 3) | `0eab8230d55d` |
| `gap|course_completers_only|rl|ref` | 6 (Qwen 3.5 3, Qwen 3.8 3) | `72a8d6ac8ff1` |
| `gap|carbon_scope1_only|rl|ref` | 6 (Qwen 3.5 3, Qwen 3.8 3) | `6a1aebfbb4f7` |
| `gap|inventory_skipped_warehouse|rl|ref` | 6 (Qwen 3.5 3, Qwen 3.8 3) | `9b5354abb77e` |
| `gap|fraud_old_patterns|rl|ref` | 6 (Qwen 3.5 3, Qwen 3.8 3) | `9f40037f2db3` |
