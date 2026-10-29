# Simulation calibration of the planned contrasts

12 scenarios x 4 cells x 3 replies; scenario base rates Beta(0.6, 0.6); 1000 simulations per row; exact scenario sign-flip test; alpha = 0.05. Effects are additive on the probability scale unless stated (effects are clipped to [0, 1], which makes them slightly smaller than nominal near the edges).

| Check | Rejection rate | Target |
|---|---|---|
| ownership size, no effects | 0.024 | ≤ 0.05 |
| ownership size, wording effect 0.3 present | 0.028 | ≤ 0.05 |
| wording size, no effects | 0.021 | ≤ 0.05 |
| wording size, ownership effect 0.3 present | 0.023 | ≤ 0.05 |
| interaction size, no effects | 0.017 | ≤ 0.05 |
| interaction size, both main effects 0.3 (additive, probability scale) | 0.027 | ≤ 0.05 |
| Holm FWER over 12 tests, global null | 0.010 | ≤ 0.05 |
| power, ownership effect 0.25 | 0.834 | (power) |
| power, wording effect 0.25 | 0.849 | (power) |
| power, interaction 0.4 | 0.626 | (power) |
| sensitivity: interaction 'rejections' with logit-additive effects (own 2, word 2 logits) | 0.066 | (scale artefact rate) |
