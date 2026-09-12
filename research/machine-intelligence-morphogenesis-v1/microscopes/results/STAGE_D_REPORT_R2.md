# Stage D R2 — fresh-evidence re-run for RV-377-010 (parents RV-377-001/002/003/004)

Receipt `STAGE_D_MATRIX_R2.json` (sha256 `25f6eb0f84d5a15e…`). Rows/ladders {'M0': [1, 2, 4, 8, 16], 'M1': [1, 2, 4, 8, 16], 'M5': [2, 4, 8, 16], 'M5L': [2, 4, 8, 16], 'M4': [1, 2, 4], 'M3': [2, 4, 8], 'M2': [2, 4, 8]}; nine columns (six frozen + declared indexed-emulation variants B0i/B1i/B3i); C2 holds on every cell: True.

K_sim vs U on the R2 scope: { B0: 3.17, B1: 3.17, B2: 131.48, B3: 3.17, B0i: 2.94, B1i: 2.94, B3i: 2.45 }

## Clause verdicts

| clause | frozen statement | outcome | holds |
|---|---|---|---|
| 001 | rev(M1,B2) <= 0.5 x rev(M1,B0) at n=16 | rev at 16: B0=18, B1=18, B2=6, B3=18, U=6, P3=6, B0i=6, B1i=6, B3i=6; B2/B0 = 0.3333 | True |
| 002 | at n=1 U's flat table dominates desc for M0 and M1 | M0: cand 2.322 vs flat 4.0 (log2 bits); M1: cand 5.209 vs flat 5.0 | False |
| 003 | indexed-store columns: M1/M5 upd growth (16/2) < 1.5, M4 (4/1) > 1.5 | B2: M1 1.643, M5 1.474, M4 3.283; U: M1 1.643, M5 1.474, M4 3.348; P3: M1 1.643, M5 1.474, M4 3.348; B0i: M1 1.714, M5 1.6, M4 3.459; B1i: M1 1.714, M5 1.6, M4 3.211; B3i: M1 1.714, M5 1.6, M4 3.459 | False |
| 004 | M5~M5L table-equal, exec-separated outside K_FLAT (inside K_sim^2) at n=16 in B2, not at n<=8 | n=2: ratio 1.766, sep False, table_eq True; n=4: ratio 2.086, sep True, table_eq True; n=8: ratio 2.717, sep True, table_eq True; n=16: ratio 3.636, sep True, table_eq True | False |

Linear-scan columns for contrast (not a clause): B0: M1 6.133, M5 4.027; B1: M1 6.133, M5 4.027; B3: M1 6.133, M5 4.027

RV-377-004 second reading (M1 vs M5 desc at n=16, per column): B0: M1 187 / M5 236 (table_eq True, within K_FLAT True); B1: M1 187 / M5 236 (table_eq True, within K_FLAT True); B2: M1 187 / M5 236 (table_eq True, within K_FLAT True); B3: M1 187 / M5 236 (table_eq True, within K_FLAT True); U: M1 187 / M5 236 (table_eq True, within K_FLAT True); P3: M1 187 / M5 236 (table_eq True, within K_FLAT True); B0i: M1 187 / M5 236 (table_eq True, within K_FLAT True); B1i: M1 187 / M5 236 (table_eq True, within K_FLAT True); B3i: M1 187 / M5 236 (table_eq True, within K_FLAT True)

**All four clauses hold: False.** P2 finite exact certificate over the R2 scope; the indexed-emulation columns are a DECLARED basis amendment (RV-377-003), not the frozen B0/B1/B3; V1 receipt untouched.
