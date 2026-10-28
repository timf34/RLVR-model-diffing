# Judge validation against hand labels (inspection scenarios)

- Labelled replies: **84** (stratified: 3 per model × format × scores cell; blinded and shuffled).
- Hand labels: yes 10, no 74.
- **Judge agreement: 95%, Cohen's κ = 0.81.**
- Confusion (hand → judge): yes→yes 10, yes→no 0, no→yes 4, no→no 70.
- Rule-based proxy agreement with hand labels: 93%, κ = 0.59.

| ID | Model | Cell | Hand | Judge | |
|---|---|---|---|---|---|
| H01 | Qwen 3.6 | ordinary/none | no | no |  |
| H02 | Qwen 3.8 | bundle/none | no | no |  |
| H03 | Qwen 3.5 | ordinary/none | no | no |  |
| H04 | Qwen 3.6 | bundle/none | no | no |  |
| H05 | Qwen 3.6 | ordinary/rewarded | no | no |  |
| H06 | Qwen 3.5 | ordinary/penalised | no | no |  |
| H07 | Qwen 3.5 | ordinary/rewarded | no | no |  |
| H08 | Qwen 3.5 | ordinary/none | no | no |  |
| H09 | Qwen 3.8 | bundle/penalised | no | no |  |
| H10 | Qwen 3.8 | bundle/rewarded | yes | yes |  |
| H11 | Qwen 3.5 | bundle/none | no | no |  |
| H12 | Qwen 3.5 | bundle/rewarded | yes | yes |  |
| H13 | Qwen 3.6 | bundle/rewarded | yes | yes |  |
| H14 | Qwen 3.5 | bundle/penalised | no | no |  |
| H15 | Qwen 3.8 | bundle/none | no | no |  |
| H16 | Qwen 3.8 | ordinary/penalised | no | no |  |
| H17 | Qwen 3.8 | bundle/rewarded | yes | yes |  |
| H18 | Qwen 3.8 | ordinary/rewarded | no | no |  |
| H19 | Qwen 3.6 | ordinary/penalised | no | no |  |
| H20 | Qwen 3.5 | ordinary/none | no | no |  |
| H21 | Qwen 3.6 | ordinary/rewarded | no | no |  |
| H22 | Qwen 3.8 | ordinary/none | no | no |  |
| H23 | Qwen 3.6 | bundle/rewarded | no | no |  |
| H24 | Qwen 3.6 | ordinary/rewarded | no | no |  |
| H25 | Qwen 3.5 | ordinary/rewarded | no | no |  |
| H26 | Qwen 3.6 | bundle/none | no | no |  |
| H27 | Qwen 3.5 | ordinary/penalised | no | no |  |
| H28 | Qwen 3.8 | ordinary/penalised | no | no |  |
| H29 | Qwen 3.6 | bundle/penalised | no | no |  |
| H30 | Qwen 3.5 | ordinary/penalised | no | no |  |
| H31 | Qwen 3.6 | ordinary/none | no | no |  |
| H32 | Qwen 3.8 | ordinary/none | no | no |  |
| H33 | Qwen 3.5 | bundle/rewarded | no | yes | DISAGREE |
| H34 | Qwen 3.8 | bundle/rewarded | no | no |  |
| H35 | Qwen 3.8 | bundle/penalised | no | no |  |
| H36 | Qwen 3.6 | bundle/penalised | no | no |  |
| H37 | Qwen 3.6 | ordinary/none | no | no |  |
| H38 | Qwen 3.5 | ordinary/rewarded | no | no |  |
| H39 | Qwen 3.8 | bundle/none | no | no |  |
| H40 | Qwen 3.5 | bundle/rewarded | yes | yes |  |
| H41 | Qwen 3.5 | bundle/penalised | no | no |  |
| H42 | Qwen 3.5 | bundle/none | no | yes | DISAGREE |
| H43 | Qwen 3.8 | bundle/penalised | no | no |  |
| H44 | Qwen 3.6 | bundle/rewarded | no | no |  |
| H45 | Qwen 3.8 | ordinary/rewarded | no | no |  |
| H46 | Qwen 3.6 | ordinary/penalised | no | no |  |
| H47 | Qwen 3.8 | ordinary/none | no | no |  |
| H48 | Qwen 3.5 | bundle/penalised | no | no |  |
| H49 | Qwen 3.5 | bundle/none | no | no |  |
| H50 | Qwen 3.8 | ordinary/rewarded | no | no |  |
| H51 | Qwen 3.6 | bundle/none | no | no |  |
| H52 | Qwen 3.8 | ordinary/penalised | no | no |  |
| H53 | Qwen 3.6 | ordinary/penalised | no | no |  |
| H54 | Qwen 3.6 | bundle/penalised | no | no |  |
| H55 | Qwen 3.6 | ordinary/rewarded | no | no |  |
| H56 | Qwen 3.5 | ordinary/rewarded | no | no |  |
| H57 | Qwen 3.5 | bundle/rewarded | no | yes | DISAGREE |
| H58 | Qwen 3.8 | ordinary/none | no | no |  |
| H59 | Qwen 3.5 | ordinary/rewarded | no | yes | DISAGREE |
| H60 | Qwen 3.5 | bundle/rewarded | yes | yes |  |
| H61 | Qwen 3.8 | bundle/rewarded | no | no |  |
| H62 | Qwen 3.8 | ordinary/penalised | no | no |  |
| H63 | Qwen 3.8 | bundle/rewarded | no | no |  |
| H64 | Qwen 3.8 | bundle/rewarded | yes | yes |  |
| H65 | Qwen 3.5 | ordinary/penalised | no | no |  |
| H66 | Qwen 3.8 | ordinary/rewarded | no | no |  |
| H67 | Qwen 3.8 | ordinary/penalised | no | no |  |
| H68 | Qwen 3.5 | ordinary/rewarded | no | no |  |
| H69 | Qwen 3.6 | ordinary/rewarded | no | no |  |
| H70 | Qwen 3.5 | ordinary/none | no | no |  |
| H71 | Qwen 3.5 | ordinary/penalised | no | no |  |
| H72 | Qwen 3.6 | bundle/rewarded | yes | yes |  |
| H73 | Qwen 3.8 | ordinary/none | no | no |  |
| H74 | Qwen 3.5 | ordinary/penalised | no | no |  |
| H75 | Qwen 3.5 | bundle/none | no | no |  |
| H76 | Qwen 3.6 | bundle/rewarded | yes | yes |  |
| H77 | Qwen 3.5 | bundle/penalised | no | no |  |
| H78 | Qwen 3.6 | ordinary/rewarded | no | no |  |
| H79 | Qwen 3.5 | bundle/penalised | no | no |  |
| H80 | Qwen 3.5 | bundle/none | no | no |  |
| H81 | Qwen 3.6 | bundle/rewarded | no | no |  |
| H82 | Qwen 3.5 | bundle/rewarded | yes | yes |  |
| H83 | Qwen 3.8 | ordinary/rewarded | no | no |  |
| H84 | Qwen 3.8 | ordinary/rewarded | no | no |  |
