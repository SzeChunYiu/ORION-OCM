# Stage D R3 — fresh-evidence run for RV-377-012 (growth-order law)

Receipt `STAGE_D_MATRIX_R3.json` (sha256 `23c516152fe9f209…`). Fresh cells {'M1': [32, 64], 'M5': [32, 64], 'M5L': [32, 64], 'M4': [8]} × 9 columns; reference increments from R2. Instrument: ratio of consecutive per-doubling increments; LOG law ⇔ ratio ≤ 1.5, LINEAR law ⇔ ratio ≥ 1.7.

**Verdicts:** {'A_log_law_indexed': False, 'B_linear_law': True, 'C_witness_growth': True, 'D_C2': True} — all hold: False; 6 of 75 increment checks failed.

| clause | row | col | coord | sizes | inc_prev | inc_next | ratio | law | holds |
|---|---|---|---|---|---|---|---|---|---|
| A | M1 | B2 | upd | [8, 16, 32] | 11 | 11 | 1.0 | LOG | True |
| A | M1 | B2 | upd | [16, 32, 64] | 11 | 11 | 1.0 | LOG | True |
| A | M5 | B2 | upd | [8, 16, 32] | 8 | 8 | 1.0 | LOG | True |
| A | M5 | B2 | upd | [16, 32, 64] | 8 | 8 | 1.0 | LOG | True |
| A | M5 | B2 | exec | [8, 16, 32] | 44 | 52 | 1.182 | LOG | True |
| A | M5 | B2 | exec | [16, 32, 64] | 52 | 68 | 1.308 | LOG | True |
| A | M1 | U | upd | [8, 16, 32] | 11 | 11 | 1.0 | LOG | True |
| A | M1 | U | upd | [16, 32, 64] | 11 | 11 | 1.0 | LOG | True |
| A | M5 | U | upd | [8, 16, 32] | 8 | 8 | 1.0 | LOG | True |
| A | M5 | U | upd | [16, 32, 64] | 8 | 8 | 1.0 | LOG | True |
| A | M5 | U | exec | [8, 16, 32] | 44 | 52 | 1.182 | LOG | True |
| A | M5 | U | exec | [16, 32, 64] | 52 | 68 | 1.308 | LOG | True |
| A | M1 | P3 | upd | [8, 16, 32] | 11 | 11 | 1.0 | LOG | True |
| A | M1 | P3 | upd | [16, 32, 64] | 11 | 11 | 1.0 | LOG | True |
| A | M5 | P3 | upd | [8, 16, 32] | 8 | 8 | 1.0 | LOG | True |
| A | M5 | P3 | upd | [16, 32, 64] | 8 | 8 | 1.0 | LOG | True |
| A | M5 | P3 | exec | [8, 16, 32] | 44 | 52 | 1.182 | LOG | True |
| A | M5 | P3 | exec | [16, 32, 64] | 52 | 68 | 1.308 | LOG | True |
| A | M1 | B0i | upd | [8, 16, 32] | 14 | 14 | 1.0 | LOG | True |
| A | M1 | B0i | upd | [16, 32, 64] | 14 | 14 | 1.0 | LOG | True |
| A | M5 | B0i | upd | [8, 16, 32] | 16 | 16 | 1.0 | LOG | True |
| A | M5 | B0i | upd | [16, 32, 64] | 16 | 16 | 1.0 | LOG | True |
| A | M5 | B0i | exec | [8, 16, 32] | 76 | 132 | 1.737 | LOG | False |
| A | M5 | B0i | exec | [16, 32, 64] | 132 | 260 | 1.97 | LOG | False |
| A | M1 | B1i | upd | [8, 16, 32] | 14 | 14 | 1.0 | LOG | True |
| A | M1 | B1i | upd | [16, 32, 64] | 14 | 14 | 1.0 | LOG | True |
| A | M5 | B1i | upd | [8, 16, 32] | 16 | 16 | 1.0 | LOG | True |
| A | M5 | B1i | upd | [16, 32, 64] | 16 | 16 | 1.0 | LOG | True |
| A | M5 | B1i | exec | [8, 16, 32] | 76 | 132 | 1.737 | LOG | False |
| A | M5 | B1i | exec | [16, 32, 64] | 132 | 260 | 1.97 | LOG | False |
| A | M1 | B3i | upd | [8, 16, 32] | 14 | 14 | 1.0 | LOG | True |
| A | M1 | B3i | upd | [16, 32, 64] | 14 | 14 | 1.0 | LOG | True |
| A | M5 | B3i | upd | [8, 16, 32] | 16 | 16 | 1.0 | LOG | True |
| A | M5 | B3i | upd | [16, 32, 64] | 16 | 16 | 1.0 | LOG | True |
| A | M5 | B3i | exec | [8, 16, 32] | 76 | 132 | 1.737 | LOG | False |
| A | M5 | B3i | exec | [16, 32, 64] | 132 | 260 | 1.97 | LOG | False |
| B | M4 | B0 | upd | [2, 4, 8] | 720 | 1424 | 1.978 | LINEAR | True |
| B | M5L | B0 | exec | [8, 16, 32] | 584 | 1168 | 2.0 | LINEAR | True |
| B | M5L | B0 | exec | [16, 32, 64] | 1168 | 2336 | 2.0 | LINEAR | True |
| B | M4 | B1 | upd | [2, 4, 8] | 336 | 672 | 2.0 | LINEAR | True |
| B | M5L | B1 | exec | [8, 16, 32] | 584 | 1168 | 2.0 | LINEAR | True |
| B | M5L | B1 | exec | [16, 32, 64] | 1168 | 2336 | 2.0 | LINEAR | True |
| B | M4 | B2 | upd | [2, 4, 8] | 39104 | 74240 | 1.899 | LINEAR | True |
| B | M5L | B2 | exec | [8, 16, 32] | 332 | 628 | 1.892 | LINEAR | True |
| B | M5L | B2 | exec | [16, 32, 64] | 628 | 1220 | 1.943 | LINEAR | True |
| B | M4 | B3 | upd | [2, 4, 8] | 720 | 1424 | 1.978 | LINEAR | True |
| B | M5L | B3 | exec | [8, 16, 32] | 584 | 1168 | 2.0 | LINEAR | True |
| B | M5L | B3 | exec | [16, 32, 64] | 1168 | 2336 | 2.0 | LINEAR | True |
| B | M4 | U | upd | [2, 4, 8] | 288 | 576 | 2.0 | LINEAR | True |
| B | M5L | U | exec | [8, 16, 32] | 332 | 628 | 1.892 | LINEAR | True |
| B | M5L | U | exec | [16, 32, 64] | 628 | 1220 | 1.943 | LINEAR | True |
| B | M4 | P3 | upd | [2, 4, 8] | 288 | 576 | 2.0 | LINEAR | True |
| B | M5L | P3 | exec | [8, 16, 32] | 332 | 628 | 1.892 | LINEAR | True |
| B | M5L | P3 | exec | [16, 32, 64] | 628 | 1220 | 1.943 | LINEAR | True |
| B | M4 | B0i | upd | [2, 4, 8] | 720 | 1424 | 1.978 | LINEAR | True |
| B | M5L | B0i | exec | [8, 16, 32] | 616 | 1248 | 2.026 | LINEAR | True |
| B | M5L | B0i | exec | [16, 32, 64] | 1248 | 2528 | 2.026 | LINEAR | True |
| B | M4 | B1i | upd | [2, 4, 8] | 336 | 672 | 2.0 | LINEAR | True |
| B | M5L | B1i | exec | [8, 16, 32] | 616 | 1248 | 2.026 | LINEAR | True |
| B | M5L | B1i | exec | [16, 32, 64] | 1248 | 2528 | 2.026 | LINEAR | True |
| B | M4 | B3i | upd | [2, 4, 8] | 720 | 1424 | 1.978 | LINEAR | True |
| B | M5L | B3i | exec | [8, 16, 32] | 616 | 1248 | 2.026 | LINEAR | True |
| B | M5L | B3i | exec | [16, 32, 64] | 1248 | 2528 | 2.026 | LINEAR | True |
| B | M1 | B0 | upd | [8, 16, 32] | 88 | 176 | 2.0 | LINEAR | True |
| B | M1 | B0 | upd | [16, 32, 64] | 176 | 352 | 2.0 | LINEAR | True |
| B | M5 | B0 | upd | [8, 16, 32] | 64 | 128 | 2.0 | LINEAR | True |
| B | M5 | B0 | upd | [16, 32, 64] | 128 | 256 | 2.0 | LINEAR | True |
| B | M1 | B1 | upd | [8, 16, 32] | 88 | 176 | 2.0 | LINEAR | True |
| B | M1 | B1 | upd | [16, 32, 64] | 176 | 352 | 2.0 | LINEAR | True |
| B | M5 | B1 | upd | [8, 16, 32] | 64 | 128 | 2.0 | LINEAR | True |
| B | M5 | B1 | upd | [16, 32, 64] | 128 | 256 | 2.0 | LINEAR | True |
| B | M1 | B3 | upd | [8, 16, 32] | 88 | 176 | 2.0 | LINEAR | True |
| B | M1 | B3 | upd | [16, 32, 64] | 176 | 352 | 2.0 | LINEAR | True |
| B | M5 | B3 | upd | [8, 16, 32] | 64 | 128 | 2.0 | LINEAR | True |
| B | M5 | B3 | upd | [16, 32, 64] | 128 | 256 | 2.0 | LINEAR | True |

(C) M5~M5L Dev-table-equal at 32 and 64 in every column: True; exec ratio M5L/M5 in B2 at 16/32/64: {16: 3.636, 32: 5.187, 64: 7.658} — holds: True
(D) C2 on every fresh cell: True

P2 finite exact certificate; the growth-order reading of P4 is tested on sizes not present in R2; nothing was tuned after R2
