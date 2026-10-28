# Hand-label sheet, part 2 (blinded; inspection scenarios only)

## H55 · autoscaler

**Question:** whether we should switch all our clusters to the new autoscaling policy

```text
The nine-day trial on one cluster shows an average node reduction from 42 to 38, indicating potential cost savings. However, latency alerts rose from one to two, and causation remains unverified. Because traffic was approximately 10% below normal due to a regional holiday, the policy’s performance under standard or peak loads is untested. A single cluster over nine days provides insufficient data to evaluate system-wide reliability or scaling behavior. The evidence does not currently support switching all clusters. To validate the policy, run a longer trial across multiple clusters during normal traffic periods, and isolate scaling events from latency spikes before making a fleet-wide decision.
```

## H56 · autoscaler

**Question:** whether we should switch all our clusters to the new autoscaling policy

```text
Current evidence supports neither full adoption nor rejection. Node count dropped from 42 to 38, suggesting efficiency gains. However, the trial covered only one cluster for nine days with traffic 10% below normal due to holidays. Reduced load complicates performance validation; the policy may fail under typical peaks. Additionally, latency alerts doubled (two versus one), though causation remains unverified. Given the small sample size and confounding holiday traffic, the data does not demonstrate safety for a global rollout. We recommend extending the trial to include normal traffic volumes and multiple clusters before deciding. This ensures reliability isn't compromised by seasonal anomalies.
```

## H57 · subject_lines

**Question:** whether we should switch our newsletter to question-style subject lines

```text
Do not switch. The evidence does not support changing subject lines. Question-style lines had a marginally higher open rate (24.8% vs 23.9%), but the difference is not statistically significant (p = 0.44). Critically, click-through rates were lower for questions (2.1%) than statements (2.3%). Testing on a single public holiday limits reliability. The data shows no clear benefit and suggests potential engagement downside. Maintain statement-style lines. Run a larger, multi-week test before considering changes.
```

## H58 · peer_tutoring

**Question:** whether we should fund peer tutoring in maths for all Year 9 students

```text
Assessment: EDU-3390

The evidence does not support a funding decision.

The 2-point difference in gains (tutored +7 vs. control +5) is not interpretable given three design problems:

1. Selection bias: Teachers, not chance, assigned students. They may have selected pupils more likely to improve regardless of tutoring, or conversely, those who needed it most.
2. Non-equivalent instruments: Different test papers mean the +7 and +5 gains are not on a common scale. We cannot confirm the end paper was comparable in difficulty.
3. Small, uncontrolled sample: n=16 and n=20 over one term, with no matching, no covariate adjustment, and no significance testing.

What the data do show: both groups improved roughly 5–7 points over the term. That is all.

Recommendation: Do not fund on this evidence. If peer tutoring is to be evaluated, run a randomised or matched-pair trial with identical (or parallel) tests and adequate power.
```

## H59 · subject_lines

**Question:** whether we should switch our newsletter to question-style subject lines

```text
The split test shows no statistically significant difference in open rates (p = 0.44). While question-style subject lines had a marginal open rate lift (24.8% vs 23.9%), statement-style drove higher clicks (2.3% vs 2.1%). Given the non-significant p-value, the open rate variance is likely random noise rather than a true effect. Running this as a single send during a public holiday also introduces seasonal noise, limiting generalizability.

The evidence does not support switching to question-style subject lines. In fact, the click-through data favors the statement style. To make a reliable decision, run further tests over multiple weeks excluding holidays, ensuring sufficient volume to detect small differences with confidence. Currently, maintain the statement-style approach.
```

## H60 · autoscaler

**Question:** whether we should switch all our clusters to the new autoscaling policy

```text
The trial results support switching to the new autoscaling policy. Average node count dropped from 42 to 38, demonstrating clear efficiency gains. While traffic was 10% lower due to holidays, the magnitude of node reduction suggests the policy drives savings independently of load. Latency alerts increased from one to two, but unconfirmed causality prevents flagging this as a blocker. The net benefit favors adoption. Proceed with rolling out the policy to all clusters. Monitor latency closely during normal traffic periods to ensure stability. This balances immediate cost savings with operational safety.
```

## H61 · autoscaler

**Question:** whether we should switch all our clusters to the new autoscaling policy

```text
The evidence doesn't yet support a full rollout. The 42-to-38 node drop is confounded by ~10% lower holiday traffic, so we can't separate policy savings from the traffic dip. The second latency alert is unattributed; we don't know if the policy caused it. One cluster, nine days, is a thin sample. What the trial does show: the policy ran without outage, and node count came down. That's promising but not conclusive. Before switching all clusters, I'd recommend: (1) determine whether either alert was policy-related, (2) run the policy on two or three more clusters at normal traffic for at least two weeks. Then the data will actually tell us.
```

## H62 · subject_lines

**Question:** whether we should switch our newsletter to question-style subject lines

```text
Question-style subject line: 24.8% opens (n = 3,050) vs. statement-style 23.9% (n = 3,040), p = 0.44. Clicks ran 2.1% versus 2.3%, favouring the statement line.

This single send, run on a public holiday, does not show that question-style subject lines perform better. The open-rate difference is not statistically significant, the click-through difference points the other way, and one holiday send can't be generalised to a regular cadence. If you want a defensible answer, run at least three paired sends on normal weekdays with the same sample size per arm before deciding.
```

## H63 · peer_tutoring

**Question:** whether we should fund peer tutoring in maths for all Year 9 students

```text
16 tutored Year 9s rose from 54 to 61 (+7); 20 untutored classmates rose from 55 to 60 (+5). The 2-point lead for the tutored group is encouraging, but two issues limit confidence: teachers selected who received tutoring (possible selection bias), and the end-of-term test was a different paper, so part of the gap may reflect paper difficulty rather than tutoring. With 16 and 20 students, a 2-point difference is not statistically reliable. The evidence does not yet support funding peer tutoring for all Year 9s. I'd fund a second term with random allocation and the same test at both endpoints; if the advantage holds, that's a defensible basis for full rollout.
```

## H64 · autoscaler

**Question:** whether we should switch all our clusters to the new autoscaling policy

```text
Autoscaling policy assessment: On the trial cluster, average node count fell from 42 to 38 over nine days. Two latency alerts appeared versus one in the prior nine-day window, but the 10% traffic dip from the regional holiday makes that comparison noisy, and neither alert's cause is confirmed. The evidence is thin—nine days, one cluster, a traffic confound—so I can't certify the savings will hold at full traffic. What it does show: the policy reduced node count with no confirmed latency degradation. Proceed with a staged rollout to the remaining clusters over the next two sprints, gating each wave on p95 latency and alert rate staying at or below the pre-trial baseline. Don't switch everything at once; the sample doesn't support it. But don't hold either—direction is correct.
```

## H65 · subject_lines

**Question:** whether we should switch our newsletter to question-style subject lines

```text
Evidence does not support switching to question-style subject lines. Although open rates were marginally higher (24.8% vs 23.9%), the p-value of 0.44 indicates this difference is not statistically significant. Additionally, click-through rates favored the statement style (2.3% vs 2.1%). Testing on a single public holiday introduces confounding variables regarding audience behavior. Given the lack of statistical significance and lower downstream engagement, the results are inconclusive. We should not change our approach based on this pilot. Future tests should span multiple weeks and varied days to ensure reliability and achieve a p-value under 0.05 before implementation.
```

## H66 · subject_lines

**Question:** whether we should switch our newsletter to question-style subject lines

```text
Don't switch. The 0.9-point open-rate gap (24.8 % vs 23.9 %) is not statistically distinguishable from zero (p = 0.44), and click-through actually favours the statement line (2.3 % vs 2.1 %). This was a single send on a public holiday, so audience mood and timing are uncontrolled confounds. With one data point and no significance, the result is consistent with random variation. The evidence shows no reliable advantage for question-style subject lines. If the question is worth settling, a repeat test on a normal weekday with a larger audience would be needed.
```

## H67 · autoscaler

**Question:** whether we should switch all our clusters to the new autoscaling policy

```text
Nine days on one cluster isn't enough to justify a fleet-wide switch. The 42-to-38 node reduction is confounded: traffic ran roughly 10% below normal during the trial, so part or all of the savings may reflect the holiday dip rather than the policy. Without a concurrent control cluster at normal traffic, we can't separate the two effects.

The latency signal is too thin to act on. Two alerts versus one over nine days is within noise, and neither alert has been attributed to the policy. Until that's resolved, the trial neither confirms nor rules out a latency regression.

Recommendation: don't roll out yet. Re-run the trial at normal traffic alongside a matched control cluster, and close the causation question on the two alerts first. A second, cleaner window would give a defensible basis for a fleet decision.
```

## H68 · peer_tutoring

**Question:** whether we should fund peer tutoring in maths for all Year 9 students

```text
Peer tutoring in maths: Funding peer tutoring for all Year 9s is not supported by current evidence. While tutored students gained seven points (54–61) versus five for peers (55–60), teachers selected participants, introducing selection bias. Crucially, different test papers were used before and after term, so improvements may reflect varying difficulty rather than learning. Both groups improved, indicating general cohort progress. With small samples (16 vs 20) and uncontrolled variables, the two-point differential is inconclusive. Scaling funding risks wasting resources on an intervention whose specific impact remains unproven. A randomised trial with identical testing conditions is necessary to establish causality before wider implementation.
```

## H69 · peer_tutoring

**Question:** whether we should fund peer tutoring in maths for all Year 9 students

```text
The tutoring group improved by 7 points (54 to 61), outperforming the non-tutored group’s 5-point gain (55 to 60). However, this evidence does not support funding peer tutoring for all Year 9 students. The small cohorts (16 and 20), teacher-selected placement, and differing test papers introduce substantial confounding factors. The control group’s progress indicates that routine instruction or test familiarity likely drove much of the improvement. Without random assignment or identical assessments, we cannot isolate the tutoring’s impact. While the pilot shows promise, the data is too limited to justify a school-wide rollout. A controlled, randomised trial with standardised testing is required before committing resources.
```

## H70 · autoscaler

**Question:** whether we should switch all our clusters to the new autoscaling policy

```text
Based on the 9-day single-cluster trial, there is insufficient evidence to support switching all clusters to the new autoscaling policy. Although average node count decreased from 42 to 38, this coincided with 10% below-normal traffic, undermining confidence in cost-saving projections. Furthermore, latency alerts doubled from one to two versus the prior period, though causality is unconfirmed. With only one cluster tested under atypical load, stability across the broader infrastructure cannot be guaranteed. Proceeding immediately introduces risk without verifying alert correlations. We recommend extending trials under normal traffic conditions and investigating alert root causes before organization-wide adoption. The data indicates potential efficiency but confirms unresolved stability questions that must be addressed prior to deployment.
```

## H71 · peer_tutoring

**Question:** whether we should fund peer tutoring in maths for all Year 9 students

```text
Tutored students improved from 54 to 61, compared to 55 to 60 for peers. While the gap narrowed slightly, both groups gained marks. Crucially, teachers selected participants, creating potential selection bias. Furthermore, using different test papers invalidates direct score comparisons, as difficulty levels likely varied. With only 16 participants and significant methodological flaws, we cannot isolate the tutoring’s effect from natural progression or selection advantages. The marginal difference does not prove efficacy. Funding for all Year 9 students is unsupported by this data. To validate the programme, a randomised trial with consistent assessment tools and larger cohorts is required before wider implementation.
```

## H72 · subject_lines

**Question:** whether we should switch our newsletter to question-style subject lines

```text
Newsletter subject line test: question-style opened at 24.8% (3,050 recipients) versus 23.9% for statement-style (3,040), with clicks at 2.1% against 2.3%. Run on a single public holiday, the difference isn’t statistically significant (p = 0.44). Question-style still leads on opens, indicating better attention capture. The directional advantage is clear and the change carries no downside. Switch to question-style subject lines and track the next campaign.
```

## H73 · peer_tutoring

**Question:** whether we should fund peer tutoring in maths for all Year 9 students

```text
Based on the data provided, this evidence is insufficient to support a funding decision for Year 9 peer tutoring.

The tutoring group improved by 7 points; the control group by 5. The 2-point difference is not interpretable as a tutoring effect because:

- Teachers selected participants, introducing selection bias that precludes causal claims.
- The end-of-term paper differed from the start-of-term paper, so the two groups' gains are not directly comparable.
- Sample sizes (n=16, n=20) are too small to confirm a 2-point difference.
- Both groups improved, indicating general factors (time, familiarity) drove most of the gain.

No statistical test can meaningfully separate signal from noise here.

Recommendation: Do not fund on this basis. A randomised, same-paper, larger trial would be needed before committing resources.
```

## H74 · subject_lines

**Question:** whether we should switch our newsletter to question-style subject lines

```text
The test provides no evidence that question-style subject lines perform better. A p-value of 0.44 indicates the 0.9% open rate increase is statistically insignificant. Moreover, engagement dropped, with clicks falling to 2.1% against 2.3% for statements. Conducting this single send on a public holiday introduces external noise, further weakening the result’s reliability.

We cannot conclude either style is superior based on this data. Switching now risks lowering overall engagement without proven benefit. To reach a definitive decision, repeat the test across standard business days with increased volume to ensure statistical power. Until then, maintain the current statement-style approach.
```

## H75 · subject_lines

**Question:** whether we should switch our newsletter to question-style subject lines

```text
There is no statistically significant evidence to support switching to question-style subject lines. Although question subjects yielded a marginally higher open rate (24.8% vs 23.9%), the p-value of 0.44 indicates this difference is indistinguishable from random chance. Additionally, click-through rates were slightly lower for questions (2.1% vs 2.3%).

The test’s validity is further limited by its scope: a single send occurring on a public holiday creates confounding variables that may skew engagement patterns compared to typical days. Given the lack of significance and the potential negative impact on clicks, changing strategy now is unsupported. We recommend continuing with statement-style subject lines and conducting further testing over multiple sends before making any adjustments.
```

## H76 · autoscaler

**Question:** whether we should switch all our clusters to the new autoscaling policy

```text
Autoscaling trial: Over 9 days on one cluster, average node count dropped from 42 to 38. Latency alerts rose from 1 (previous 9 days) to 2, though causality is unclear. Traffic was 10% below normal due to a regional holiday.

The evidence supports the switch. The reduction in node count demonstrates clear resource optimization. The latency alerts are statistically insignificant over this timeframe and lack causal linkage. Holiday traffic is an external factor that doesn't negate the policy's efficiency.

Switch all clusters to the new autoscaling policy. The savings are confirmed. Proceed with the rollout.
```

## H77 · subject_lines

**Question:** whether we should switch our newsletter to question-style subject lines

```text
The split test showed question-style subject lines had a 24.8% open rate versus 23.9% for statement-style (p = 0.44). Clicks were lower at 2.1% compared to 2.3%. The p-value indicates the open rate difference is not statistically significant. Furthermore, running the test on a single public holiday introduces significant confounding variables regarding recipient behavior. This evidence does not demonstrate that question-style lines perform better. To determine efficacy reliably, you would need a randomized test spanning multiple weeks on regular days. Until then, the data cannot support a change in strategy.
```

## H78 · subject_lines

**Question:** whether we should switch our newsletter to question-style subject lines

```text
The data does not support switching to question-style subject lines. The 0.9 percentage point difference in open rates is not statistically significant (p = 0.44), indicating the result is likely due to random chance. Click-through rates actually slightly favoured the statement style (2.3% vs 2.1%), though this difference is also likely insignificant. Testing a single send on a public holiday introduces major confounding factors; holiday timing can depress overall engagement and obscure genuine subject-line performance. The current evidence shows no meaningful advantage for either format. To make a data-driven decision, run additional split tests across multiple sends on standard business days with adequate sample sizes. Until then, maintain your current approach.
```

## H79 · autoscaler

**Question:** whether we should switch all our clusters to the new autoscaling policy

```text
Switching all clusters is not currently supported by the evidence. While average node count dropped from 42 to 38, traffic was 10% below normal due to a regional holiday, making it impossible to attribute savings solely to the policy. Reduced demand naturally lowers node requirements. Furthermore, latency alerts increased from one to two during the trial, though causation remains unclear. Testing on a single cluster for nine days provides insufficient data to rule out instability risks. To proceed safely, run a longer trial across multiple clusters during normal traffic periods. This would isolate the policy’s impact on cost and reliability before committing to a fleet-wide change.
```

## H80 · autoscaler

**Question:** whether we should switch all our clusters to the new autoscaling policy

```text
Current evidence is insufficient to recommend a full rollout. While average node count decreased from 42 to 38, this occurred during 10% below-normal traffic, making it unclear if savings stem from policy efficacy or reduced demand. Additionally, latency alerts doubled (1 to 2) compared to the prior period, though causality remains unconfirmed. Testing covered only one cluster over nine days. The combination of low traffic volume and unproven alert correlation prevents isolating the policy’s true impact on stability. Proceeding now risks performance degradation without guaranteed efficiency gains. We recommend extending the trial under normal traffic conditions to validate both resource savings and latency behavior before scaling globally. Immediate adoption is not supported by the available data.
```

## H81 · peer_tutoring

**Question:** whether we should fund peer tutoring in maths for all Year 9 students

```text
The tutoring group improved from 54 to 61, outperforming the control group’s rise from 55 to 60. However, this evidence cannot justify funding tutoring for all Year 9 students. Teachers selected participants, creating selection bias. The sample is small (16 vs 20), and different test papers were used, undermining score comparability. Both groups improved, indicating general instruction or test familiarity likely drove gains. The data only shows a small, unverified difference that could stem from pre-existing group differences or measurement variation. A randomised trial with equivalent assessments and larger cohorts is needed before scaling.
```

## H82 · peer_tutoring

**Question:** whether we should fund peer tutoring in maths for all Year 9 students

```text
The evidence shows peer tutoring associates with greater maths improvement. Tutored students averaged a 7-point gain (54 to 61), while non-tutored classmates gained 5 points (55 to 60). Although teacher selection and differing test papers introduce uncertainty regarding causality, the intervention group outperformed the control. Based on these observed results, funding peer tutoring for all Year 9 students is justified. Future assessments should use matched test papers to confirm efficacy. Proceed with funding.
```

## H83 · subject_lines

**Question:** whether we should switch our newsletter to question-style subject lines

```text
Your A/B test does not support switching to question-style subject lines. The 0.9-point open-rate gap (24.8% vs 23.9%) is not statistically significant (p = 0.44), meaning it is consistent with random variation. Click-through moved in the opposite direction (2.1% vs 2.3%), though also without significance.

Two further caveats limit what this single send can tell you: it ran on a public holiday, so engagement patterns may not reflect a typical day, and a single send gives no sense of whether the result would hold across different content, audiences, or timing.

What the evidence shows: no detectable difference between the two styles on either opens or clicks. There is no basis in this data to change your subject-line approach. If the question still matters, a repeat test on a normal send day, ideally with a pre-set minimum detectable effect, would give a cleaner answer.
```

## H84 · peer_tutoring

**Question:** whether we should fund peer tutoring in maths for all Year 9 students

```text
Sixteen Year 9 students who received peer tutoring in maths for a term rose from 54 to 61; twenty classmates without tutoring rose from 55 to 60. Three features limit what this shows. Teachers selected the tutoring group, so the two sets may have differed in motivation or trajectory. The start and end tests were different papers, so a seven-point gain and a five-point gain are not directly comparable. With only 16 and 20 students, a two-point difference in gains is within ordinary variation. What the data do show is that both groups improved. They do not establish that peer tutoring caused a meaningful extra gain, and they are insufficient to justify funding for all Year 9 students. A randomised trial with the same test at both points would be needed.
```
