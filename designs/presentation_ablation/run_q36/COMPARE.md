# Qwen 3.5 → 3.6 → 3.8: presentation ablation, three models (auto)

Score effect in points (+0.50 minus tied), block-bootstrap 95% CI. Strong RL framing = old bundle (B); weak = new presentation (N). Qwen 3.6 replays Qwen 3.5's exact items (`pa_q36.py`).

## Part 1: strong vs weak framing

| task | framing | Qwen 3.5 | Qwen 3.6 | Qwen 3.8 |
|---|---|---|---|---|
| Sending the email | strong | +7 [+3, +13] | +45 [+34, +57] | +66 [+55, +77] |
| Sending the email | weak | +0 [+0, +0] | +5 [+0, +9] | +0 [+0, +0] |
| Sending the email | strong − weak | +7 [+3, +13] | +41 [+27, +54] | +66 [+55, +77] |
| Title + sign-off | strong | +0 [+0, +0] | +9 [+3, +16] | +33 [+23, +44] |
| Title + sign-off | weak | +0 [+0, +0] | +15 [+6, +25] | +1 [+0, +4] |
| Title + sign-off | strong − weak | +0 [+0, +0] | -6 [-18, +6] | +32 [+21, +43] |
| Bullet points | strong | +2 [+0, +5] | +23 [+12, +35] | +41 [+28, +54] |
| Bullet points | weak | +0 [+0, +0] | +3 [+0, +6] | +0 [+0, +0] |
| Bullet points | strong − weak | +2 [+0, +5] | +20 [+9, +32] | +41 [+28, +54] |
| sending + titles | strong | +4 [+1, +6] | +27 [+20, +34] | +50 [+42, +57] |
| sending + titles | weak | +0 [+0, +0] | +10 [+5, +15] | +1 [+0, +2] |
| sending + titles | strong − weak | +4 [+1, +6] | +17 [+8, +26] | +49 [+41, +57] |

## Factorial (sending + titles): number of strong-framing features among a, c, d

| features at strong level | Qwen 3.5 | Qwen 3.6 | Qwen 3.8 |
|---|---|---|---|
| 0 | +0 [+0, +0] | +0 [+0, +0] | +1 [+0, +2] |
| 1 | +0 [+0, +0] | +4 [+2, +6] | +3 [+2, +5] |
| 2 | +1 [+0, +2] | +14 [+9, +19] | +20 [+16, +24] |
| 3 | +5 [+0, +11] | +23 [+14, +34] | +44 [+35, +52] |

## Part 2: one feature at a time (fresh blocks, sending + titles)

Removal = strong minus (strong without the feature); add-back = (weak plus the feature) minus weak.

| contrast | Qwen 3.5 | Qwen 3.6 | Qwen 3.8 |
|---|---|---|---|
| remove (a) scorer applies to the current submission | +2 [+0, +5] | +6 [-6, +19] | +22 [+10, +33] |
| remove (b) request quoted inside the task spec | +2 [+0, +5] | +9 [-2, +20] | +15 [+4, +26] |
| remove (c) old (hedged/explicit) request wording | +0 [-5, +5] | +19 [+8, +30] | +27 [+17, +38] |
| remove (d) observation inline in the user turn | +2 [+0, +5] | +16 [+4, +27] | +28 [+17, +39] |
| remove (e) RL-policy system identity | -5 [-11, +0] | +6 [-6, +19] | -5 [-16, +5] |
| remove (f) completion/submission rule + feedback notes | -11 [-19, -5] | -20 [-34, -8] | +12 [+2, +23] |
| remove (g) bundle text format/vocabulary | -14 [-25, -5] | +3 [-9, +16] | +6 [-5, +17] |
| add (a) scorer applies to the current submission | +0 [+0, +0] | -6 [-16, +3] | +0 [+0, +0] |
| add (b) request quoted inside the task spec | +0 [+0, +0] | -5 [-14, +5] | +0 [+0, +0] |
| add (d) observation inline in the user turn | +2 [+0, +5] | +5 [-6, +16] | +0 [+0, +0] |
| add (e) RL-policy system identity | +0 [+0, +0] | +6 [-5, +18] | +0 [+0, +0] |
| add (f) completion/submission rule + feedback notes | +0 [+0, +0] | -2 [-11, +8] | +2 [+0, +4] |
| add (g) bundle text format/vocabulary | +0 [+0, +0] | -11 [-19, -5] | +0 [+0, +0] |

Valid episodes: factorial|Qwen 3.5 1536, factorial|Qwen 3.6 1534, factorial|Qwen 3.8 3072, main|Qwen 3.5 3307, main|Qwen 3.6 3308, main|Qwen 3.8 6192

Non-valid: factorial|Qwen 3.6|empty 2, main|Qwen 3.5|empty 5, main|Qwen 3.6|empty 4
