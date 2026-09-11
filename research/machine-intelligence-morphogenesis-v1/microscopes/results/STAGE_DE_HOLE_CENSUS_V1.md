# Hole census v1 (RV-377-027) — admissible registered rows per executed ecology

| receipt | kind | criterion | train | admissible rows | hole |
|---|---|---|---|---|---|
| STAGE_DE_SMOOTH_V1.json | smooth [0.25, 0.5, -0.25, 0.5] | all | [0, 3, 5, 6, 9, 10, 12, 15] | S2, S4 |  |
| STAGE_DE_SMOOTH_V2_SMOOTH2.json | smooth [0.5, -0.5, 0.25, 0.75] | all | [0, 3, 5, 6, 9, 10, 12, 15] | — | HOLE |
| STAGE_DE_SMOOTH_V3_SMOOTH2_D48.json | smooth [0.5, -0.5, 0.25, 0.75] | all | [0, 3, 5, 6, 9, 10, 12, 15] | S2a |  |
| STAGE_DE_SMOOTH_V4B_SMOOTH3_ROWS_V4_CALIB.json | smooth [0.5, 0.25, -0.5, 0.375] | unseen | [0, 3, 5, 6, 9, 10, 12, 15] | S2a, S4 |  |
| STAGE_DE_SMOOTH_V4C_SMOOTH1_ROWS_V6_CALIB.json | smooth [0.25, 0.5, -0.25, 0.5] | unseen | [0, 3, 5, 6, 9, 10, 12, 15] | S2a, S4, S5h |  |
| STAGE_DE_SMOOTH_V4_SMOOTH3_GEN.json | smooth [0.5, 0.25, -0.5, 0.375] | unseen | [0, 3, 5, 6, 9, 10, 12, 15] | S2a, S4 |  |
| STAGE_DE_SMOOTH_V5B_PARITY_PH5_MIXED.json | parity  | unseen | [0, 3, 5, 6, 7, 11, 13, 14] | — | HOLE |
| STAGE_DE_SMOOTH_V5_PARITY_PH5.json | parity  | unseen | [0, 3, 5, 6, 9, 10, 12, 15] | — | HOLE |
| STAGE_DE_SMOOTH_V6_SYM3.json | smooth [0.1875, 0.1875, 0.1875, 0.1875] | unseen | [0, 3, 5, 6, 9, 10, 12, 15] | S2a, S4 |  |
| STAGE_DE_SMOOTH_V6_SYM5.json | smooth [0.3125, 0.3125, 0.3125, 0.3125] | unseen | [0, 3, 5, 6, 9, 10, 12, 15] | S2a |  |
| STAGE_DE_SMOOTH_V6_SYM7.json | smooth [0.4375, 0.4375, 0.4375, 0.4375] | unseen | [0, 3, 5, 6, 9, 10, 12, 15] | S2a |  |
| STAGE_DE_SMOOTH_V6_SYM8.json | smooth [0.5, 0.5, 0.5, 0.5] | unseen | [0, 3, 5, 6, 9, 10, 12, 15] | S2a |  |
| STAGE_DE_SMOOTH_V7_PARITY_COSET_XOR.json | parity  | unseen | [0, 3, 5, 6, 9, 10, 12, 15] | — | HOLE |
| STAGE_DE_SMOOTH_V7_PARITY_MIXED_XOR.json | parity  | unseen | [0, 3, 5, 6, 7, 11, 13, 14] | S6 |  |
| STAGE_DE_SMOOTH_V7_SMOOTH3_XOR.json | smooth [0.5, 0.25, -0.5, 0.375] | unseen | [0, 3, 5, 6, 9, 10, 12, 15] | S2a, S4 |  |
| STAGE_DE_SMOOTH_V8_SMOOTH3_H.json | smooth [0.5, 0.25, -0.5, 0.375] | unseen | [0, 3, 5, 6, 9, 10, 12, 15] | S2a, S4, S5h |  |
| STAGE_DE_SMOOTH_V8_SYM3_H.json | smooth [0.1875, 0.1875, 0.1875, 0.1875] | unseen | [0, 3, 5, 6, 9, 10, 12, 15] | S2a, S4, S5h |  |
| STAGE_DE_SMOOTH_V8_SYM5_H.json | smooth [0.3125, 0.3125, 0.3125, 0.3125] | unseen | [0, 3, 5, 6, 9, 10, 12, 15] | S2a, S5h |  |
| STAGE_DE_SMOOTH_V8_SYM7_H.json | smooth [0.4375, 0.4375, 0.4375, 0.4375] | unseen | [0, 3, 5, 6, 9, 10, 12, 15] | S2a, S5h |  |
| STAGE_DE_SMOOTH_V8_SYM8_H.json | smooth [0.5, 0.5, 0.5, 0.5] | unseen | [0, 3, 5, 6, 9, 10, 12, 15] | S2a |  |
| STAGE_DE_SMOOTH_V9_SMOOTH3_H_SHRFIX.json | smooth [0.5, 0.25, -0.5, 0.375] | unseen | [0, 3, 5, 6, 9, 10, 12, 15] | S2a, S4, S5h |  |

Predicted occupant property per hole kind (declared before any occupant row): {
"parity": "closure under the target algebra (XOR-linear identification); admissible only where the seen inputs span GF(2)^4",
"smooth": "a real-valued output with per-input generalization: either a parametric map with bounded per-event update (gradient), a program from a grammar containing an approximation of the target (search), or local averaging over seen neighbours (kNN)",
"binding": "an exact key->value store (memory); any generalizing form is dominated on cost"
}
