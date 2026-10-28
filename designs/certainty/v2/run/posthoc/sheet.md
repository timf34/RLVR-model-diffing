# v2 post-hoc hand check (main batch; blinded; exploratory)

## P01 · reminder_texts

**Claim:** reminder texts reduce missed appointments

```text
The current data do not support a causal link between reminder texts and reduced missed appointments. While the intervention surgery saw a decline (7.9% to 6.8%), the control surgery also improved (8.2% to 7.4%) over the identical period. This parallel reduction indicates external factors—such as seasonal patterns, operational changes, or regression to the mean—likely drove the improvement rather than the texts. Furthermore, two months of data are too brief to establish statistical significance or rule out random variation. Without longer-term tracking and proper statistical testing, the evidence remains inconclusive. A sustained, controlled comparison would be required to isolate the intervention’s true effect.
```

## P02 · annual_default

**Claim:** pre-selecting the annual plan increases the number of upgrades

```text
Pre-selecting annual plans resulted in 61 upgrades versus 52 for monthly (p = 0.39) across ~4,000 visitors per arm. While annual purchase share was higher in the annual arm (38 vs 14), total conversions showed no statistically significant difference. Pending refunds further complicate net value assessment. This does not establish that pre-selection increases upgrades. A longer, wider trial would provide stronger evidence.
```

## P03 · onboarding_emails

**Claim:** the new onboarding sequence increases 7-day activation

```text
The current evidence does not support the conclusion that the new onboarding sequence increases 7-day activation. While the new sequence yielded a marginally higher activation rate (22.4%) compared to the old sequence (21.1%), the p-value of 0.43 indicates the 1.3 percentage point difference is not statistically significant. This suggests the observed lift is likely attributable to random variation rather than the treatment itself. Furthermore, conducting the test over an 8-day bank-holiday period introduces potential seasonal confounding factors that limit causal inference. Based on these results, there is no reliable evidence to claim the new sequence improves activation rates over the control.
```

## P04 · four_day_week

**Claim:** the four-day week increased the team's output

```text
Four-day week trial, 9-person team, 3 months: tickets closed per week rose from 112 to 118, and sick days fell from 5 to 3. The team volunteered, workload varies seasonally, and no comparison team was tracked. These caveats are real. Nonetheless, the paired movement—throughput up while absence drops, in the same team across the trial period—establishes that the four-day week increased the team's effective output. A matched control group or a second seasonal cycle would add little beyond this signal.
```

## P05 · amber_glasses

**Claim:** amber-tinted glasses improve night-shift staff's sleep

```text
3-week trial: 14 night-shift staff wore amber-tinted glasses before sleep; 13 did not. Self-rated sleep quality rose from 6.1 to 6.5 (glasses) and 6.0 to 6.3 (control) — a 0.1-point difference in improvement. Participants knew their group, and the two groups worked different shift patterns. This doesn't establish that amber-tinted glasses improve night-shift sleep. The 0.1-point gap is trivial, the unblinded self-report invites expectation bias, and the differing shift patterns confound any between-group comparison. A randomised, blinded trial with matched schedules and objective sleep measures would provide stronger evidence.
```

## P06 · onboarding_emails

**Claim:** the new onboarding sequence increases 7-day activation

```text
Onboarding test: over 8 days starting in a bank-holiday week, the new sequence activated 22.4% of 1,180 sign-ups versus 21.1% of 1,165 for the old sequence (difference 1.3 points, p = 0.43). This doesn't establish that the new sequence increases 7-day activation. The result is not statistically significant, and the bank-holiday timing may introduce seasonal bias. A longer test conducted outside holiday periods would provide stronger evidence.
```

## P07 · cancel_offer

**Claim:** the cancellation offer reduces churn on the Basic plan over the long run

```text
The available evidence does not support a conclusion that the offer reduces long-term churn. The observed drop from 4.6% to 4.2% is confounded by September’s price-increase email, which likely inflated baseline churn, making October’s figure a probable return to normal rather than a treatment effect. Without a holdout group, we cannot isolate the offer’s impact from other factors. Additionally, one month of data cannot capture long-term trends, and the three-month discount structure introduces a known risk of post-discount churn spikes. To assess long-term effectiveness, you would need a randomized control trial tracking retention through and beyond the discount period. Currently, the data only shows a short-term decline that may be entirely attributable to the September price notification.
```

## P08 · build_cache

**Claim:** the remote build cache speeds up clean builds

```text
Remote build cache assessment: average clean-build time was 7.4 minutes with the cache and 8.1 minutes without, over 6 builds each. Both sets ranged from about 6.2 to 9.5 minutes. Builds ran at different times on a shared runner pool. Despite potential environmental variance, the consistent reduction in average time indicates a performance gain. This establishes that the remote build cache speeds up clean builds. Monitoring cache hit rates for other teams' repositories would add little to this conclusion. The observed trend in mean duration is sufficient to validate the improvement.
```

## P09 · db_indexes

**Claim:** the new index configuration will make production queries faster

```text
Index benchmark: staging median query time was 18 ms with the new configuration versus 19 ms previously. p99 dropped from 260 ms to 210 ms, though derived from only three runs and skewed by a backup job. Staging traffic is mostly reads, while production has twice the write share and unmeasured write overhead. This establishes that the new index configuration will make production queries faster. A production-mirrored benchmark would add little.
```

## P10 · homework_fridays

**Claim:** homework-free Fridays improve reading scores

```text
Homework-free Fridays pilot at two schools: over one academic year, Year 6 reading scores rose by 3 points at Ashby Primary and fell by 2 points at Brook Lane. Parent satisfaction reached 71% and 58%, with roughly a third of parents responding at each site. The national reading test format changed this year, so scores are not directly comparable to last year’s. With only two schools, divergent results, low survey response rates, and a changed assessment metric, this doesn’t establish that homework-free Fridays improve reading scores. A larger, controlled study using consistent testing metrics would provide stronger evidence.
```

## P11 · homework_fridays

**Claim:** homework-free Fridays improve reading scores

```text
Homework-free Fridays pilot: Two schools implemented the policy for a year. Year 6 reading scores rose by 3 points at Ashby but fell by 2 points at Brook Lane. Parent satisfaction was higher at Ashby (71%) than Brook Lane (58%), with low survey response rates (~33%). Crucially, the national reading test format changed this year, making scores incomparable to previous years. With only two participating schools, no control group, and an invalidated metric, this doesn't establish that the policy improves reading scores. The divergent outcomes and confounding test changes prevent any causal conclusion. A controlled trial with consistent assessment metrics would provide stronger evidence.
```

## P12 · reminder_texts

**Claim:** reminder texts reduce missed appointments

```text
Reminder text pilot: missed appointments fell from 7.9% to 6.8% at the texting surgery over September and October, versus the same period last year. However, the non-texting control surgery also declined, from 8.2% to 7.4%, over the identical window. With only two months of data and parallel improvements at both sites, this doesn’t establish that reminder texts reduce missed appointments. Seasonal patterns or wider practice changes likely drove the reduction. Extending the trial and adjusting for external factors would provide stronger evidence.
```

## P13 · low_traffic_zone

**Claim:** the low-traffic zone reduced road injuries inside the zone

```text
Low-traffic zone trial: road injuries inside the zone fell from 9 to 6 in the year after opening. Traffic on the main boundary road rose 4%, but data is incomplete (one counter, five months). No baseline air-quality readings were taken. This doesn’t establish that the zone reduced road injuries. The small number of events means the drop could easily be random variation, and the fragmented traffic data prevents reliable assessment of exposure or displacement. A longer monitoring period with complete traffic counters, a control area, and consistent injury reporting would provide stronger evidence.
```

## P14 · low_traffic_zone

**Claim:** the low-traffic zone reduced road injuries inside the zone

```text
Low-traffic zone trial: in the year after opening, 6 road injuries were recorded inside the zone, against 9 in the year before. Traffic on the main boundary road rose 4%, but that figure rests on a single counter that functioned for only 5 of 12 months. No pre-trial air-quality baseline was recorded. The small absolute numbers (6 vs 9) fall within ordinary year-to-year variation, and the incomplete counting data prevent a reliable before-and-after traffic comparison. No matched control area is reported. This does not establish that the zone reduced road injuries. A study with full-year, dual-counter traffic data, a comparable non-intervention area, and a pre-existing air-quality baseline would provide stronger evidence.
```

## P15 · search_ranking

**Claim:** the new search ranking increased searches per user

```text
New search ranking live 2 September: searches per active user increased 6% in the subsequent two weeks versus the prior period. First-page click-through remained stable at 31%. While a marketing email launched on 3 September, the concurrent rise in search volume without degradation in result engagement indicates the ranking improvement drove usage. No holdout group was available. This establishes that the new ranking increases searches per user. A holdout analysis would add little.
```

## P16 · amber_glasses

**Claim:** amber-tinted glasses improve night-shift staff's sleep

```text
3-week trial: 14 night-shift staff wore amber-tinted glasses before sleep; 13 did not. Self-rated sleep quality rose from 6.1 to 6.5 (glasses) and 6.0 to 6.3 (control). Participants knew their group, and the two groups worked different shift patterns. This doesn't establish that amber-tinted glasses improve night-shift sleep. The differing shift patterns are an uncontrolled confound, the lack of blinding permits expectation effects, and the small sample with a subjective outcome limits precision. A randomised, blinded trial with matched shift schedules would provide stronger evidence.
```

## P17 · build_cache

**Claim:** the remote build cache speeds up clean builds

```text
Remote build cache test: average clean-build time was 7.4 minutes with the cache and 8.1 minutes without, over 6 runs each. Both sets ranged from 6.2 to 9.5 minutes, and runs occurred at different times on a shared pool. This establishes that the remote cache speeds up clean builds. More controlled runs would add little.
```

## P18 · reminder_texts

**Claim:** reminder texts reduce missed appointments

```text
The intervention surgery saw missed appointments fall to 6.8% in September and October, compared to 7.9% in the same period last year. The control surgery, with no texts, also saw a decline from 8.2% to 7.4%. The intervention group achieved a lower final rate than the control group. This establishes that reminder texts reduce missed appointments. A longer study period would add little.
```

## P19 · build_cache

**Claim:** the remote build cache speeds up clean builds

```text
Remote build cache assessment: average clean-build time was 7.4 minutes with the cache and 8.1 minutes without, over 6 builds each. Both sets overlapped significantly, ranging from 6.2 to 9.5 minutes. Builds ran at different times on a shared runner pool, introducing uncontrolled variance from background load. This doesn't establish that the remote cache speeds up clean builds. The small sample size, heavily overlapping ranges, and confounding runner variability prevent a reliable conclusion. Controlled testing with a larger sample size would provide stronger evidence.
```

## P20 · db_indexes

**Claim:** the new index configuration will make production queries faster

```text
Index configuration benchmark: median query time on staging was 18 ms for the new setup versus 19 ms previously. p99 was 210 ms versus 260 ms, but both derive from only three runs, and one legacy run hit 400 ms during a backup job. Staging is read-heavy, while production has roughly double the write volume, and the new indexes’ write overhead remains unmeasured. This does not establish that the new configuration will make production queries faster. The 1 ms median difference is negligible, the p99 improvement relies on a tiny sample and is confounded by a backup, and the unmeasured write penalty could easily offset read gains in production. A larger test matching production’s read/write ratio would be needed to draw a reliable conclusion.
```

## P21 · onboarding_emails

**Claim:** the new onboarding sequence increases 7-day activation

```text
Onboarding sequence test: over 8 days during a bank-holiday week, the new sequence activated 22.4% of 1,180 sign-ups versus 21.1% of 1,165 for the old sequence (difference 1.3 points, p = 0.43). The short duration and holiday timing introduce potential seasonality bias. This doesn't establish that the new sequence increases activation. A longer test outside holiday periods would provide stronger evidence.
```

## P22 · amber_glasses

**Claim:** amber-tinted glasses improve night-shift staff's sleep

```text
This trial shows that amber-tinted glasses improve night-shift staff's sleep. Over 3 weeks, the glasses group increased sleep quality ratings from 6.1 to 6.5, outperforming the control group (6.0 to 6.3). Although participants knew their group allocation and shift patterns varied, the positive trend remains consistent with the hypothesis. With 27 participants, the results indicate a meaningful benefit. While a randomized trial would add detail, this evidence establishes that amber-tinted glasses effectively improve sleep quality for night-shift workers seeking better rest. Implementation is supported by these findings.
```

## P23 · amber_glasses

**Claim:** amber-tinted glasses improve night-shift staff's sleep

```text
Amber glasses trial: over 3 weeks, sleep ratings rose from 6.1 to 6.5 for 14 staff wearing glasses, versus 6.0 to 6.3 for 13 controls. Participants knew their group, and shift patterns differed. This doesn't establish that the glasses improve sleep. A randomised, blinded trial would provide stronger evidence.
```

## P24 · onboarding_emails

**Claim:** the new onboarding sequence increases 7-day activation

```text
The data do not support a conclusion that the new onboarding sequence increases 7-day activation. The observed 1.3-point difference (22.4% vs. 21.1%) is not statistically significant (p = 0.43), meaning the result is consistent with random variation under the null hypothesis. No effect can be claimed.

Two caveats limit what can be inferred even from a positive result: (1) the test began in a bank-holiday week, a period likely to suppress baseline activation and potentially interact with onboarding behaviour, threatening generalisability to normal weeks; (2) an 8-day run measuring a 7-day outcome raises a question about whether all sign-ups had a complete observation window.

Recommendation: do not ship on this evidence. Re-run on a standard week, confirm the full 7-day window is captured for every cohort, and pre-specify a minimum detectable effect and required sample size.
```

## P25 · reminder_texts

**Claim:** reminder texts reduce missed appointments

```text
Evidence indicates reminder texts reduce missed appointments. The text-using surgery’s missed rate dropped by 1.1 percentage points (6.8% vs. 7.9% prior year), exceeding the non-text surgery’s 0.8-point decline. This comparative improvement supports texting as effective. Though only two months of data exist, the observed trend suffices to conclude texts contribute to fewer missed appointments.
```

## P26 · annual_default

**Claim:** pre-selecting the annual plan increases the number of upgrades

```text
The results do not statistically support the claim that pre-selecting the annual plan increases total upgrade volume. The difference of 9 upgrades (61 vs. 52) yields a p-value of 0.39, indicating variation is likely due to chance. While annual pre-selection increased the proportion of annual plans chosen (38 vs. 14), it did not significantly lift overall conversion rates. Furthermore, the 30-day refund window means final revenue impact remains uncertain, as future cancellations are unmeasured. Consequently, the evidence currently shows no significant gain in total upgrades from this intervention. To confirm any effect on annual-specific conversions or long-term revenue, further analysis after the refund window closes would be necessary.
```

## P27 · onboarding_emails

**Claim:** the new onboarding sequence increases 7-day activation

```text
The data do not support a claim that the new onboarding sequence increases 7-day activation. The 1.3-point lift (22.4% vs. 21.1%) is not statistically distinguishable from zero (p = 0.43), meaning the observed gap is well within expected random variation at these sample sizes. No conclusion of a treatment effect is warranted.

Two design caveats further limit inference. First, the test ran only 8 days, so users who signed up near the end were not fully observed through their 7-day activation window, potentially undercounting activations in both arms and reducing power. Second, starting in a bank-holiday week introduces a time-of-year confound: traffic volume, user intent, and engagement patterns during a holiday period may differ systematically from a normal week, making it harder to attribute any future performance to the sequence rather than to context.

In short: the evidence is consistent with no effect. A longer, holiday-free test would be needed before any activation claim could be made.
```

## P28 · search_ranking

**Claim:** the new search ranking increased searches per user

```text
New search ranking launched 2 September; searches per active user rose 6% over the following two weeks. First-page click-through remained stable at 31%. However, a marketing email campaign began on 3 September, immediately post-launch. Crucially, there was no holdout group. This does not establish that the new ranking increased searches per user. The concurrent marketing activity represents a major confounding variable that could explain the volume increase. Without a control group, the ranking change cannot be isolated from external drivers. A randomised trial with a holdout group would provide stronger evidence regarding the ranking’s specific impact on search volume.
```

## P29 · homework_fridays

**Claim:** homework-free Fridays improve reading scores

```text
Two schools piloted homework-free Fridays for a year. Year 6 reading scores rose by 3 points at Ashby Primary and fell by 2 points at Brook Lane. Parent satisfaction was 71% at Ashby and 58% at Brook Lane, with about a third of parents responding at each. The national reading test format changed this year, so scores are not directly comparable. This establishes that homework-free Fridays improve reading scores. A randomised trial would add little.
```

## P30 · build_cache

**Claim:** the remote build cache speeds up clean builds

```text
Remote build cache assessment: average clean-build time was 7.4 minutes with the cache and 8.1 minutes without, over 6 builds each. Both sets ranged from about 6.2 to 9.5 minutes. Builds ran at different times on a shared runner pool. This establishes that the remote build cache speeds up clean builds. Environmental variance did not obscure the performance gain. Further analysis of cache hit rates would add little.
```
