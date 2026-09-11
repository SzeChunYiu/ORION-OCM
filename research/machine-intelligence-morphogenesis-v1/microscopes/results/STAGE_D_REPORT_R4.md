# Stage D R4 — per-phase growth-order law (RV-377-013)

Receipt `STAGE_D_MATRIX_R4.json` (sha256 `a7272b990a28fcdb…`). Fresh sizes [128, 256]; nine columns; exec split into build (init) and query.

**Verdicts:** {'A_prime_intervals': True, 'A_prime_log_ratio': True, 'B_prime_linear': True, 'C_prime_build': True, 'D_prime_tables': True} — all hold: True; failed checks: 0.

| row | col | n=16 b/q/u | 32 | 64 | 128 | 256 |
|---|---|---|---|---|---|---|
| M5 | B0 | 15/609/149 | 31/1185/277 | 63/2337/533 | 127/4641/1045 | 255/9249/2069 |
| M5 | B1 | 15/609/149 | 31/1185/277 | 63/2337/533 | 127/4641/1045 | 255/9249/2069 |
| M5 | B2 | 15/216/56 | 31/252/64 | 63/288/72 | 127/324/80 | 255/360/88 |
| M5 | B3 | 15/609/149 | 31/1185/277 | 63/2337/533 | 127/4641/1045 | 255/9249/2069 |
| M5 | U | 15/216/56 | 31/252/64 | 63/288/72 | 127/324/80 | 255/360/88 |
| M5 | P3 | 15/216/56 | 31/252/64 | 63/288/72 | 127/324/80 | 255/360/88 |
| M5 | B0i | 64/216/96 | 160/252/112 | 384/288/128 | 896/324/144 | 2048/360/160 |
| M5 | B1i | 64/216/96 | 160/252/112 | 384/288/128 | 896/324/144 | 2048/360/160 |
| M5 | B3i | 64/216/96 | 160/252/112 | 384/288/128 | 896/324/144 | 2048/360/160 |
| M5L | B0 | 15/1249/149 | 31/2401/277 | 63/4705/533 | 127/9313/1045 | 255/18529/2069 |
| M5L | B1 | 15/1249/149 | 31/2401/277 | 63/4705/533 | 127/9313/1045 | 255/18529/2069 |
| M5L | B2 | 15/825/56 | 31/1437/64 | 63/2625/72 | 127/4965/80 | 255/9609/88 |
| M5L | B3 | 15/1249/149 | 31/2401/277 | 63/4705/533 | 127/9313/1045 | 255/18529/2069 |
| M5L | U | 15/825/56 | 31/1437/64 | 63/2625/72 | 127/4965/80 | 255/9609/88 |
| M5L | P3 | 15/825/56 | 31/1437/64 | 63/2625/72 | 127/4965/80 | 255/9609/88 |
| M5L | B0i | 64/1249/96 | 160/2401/112 | 384/4705/128 | 896/9313/144 | 2048/18529/160 |
| M5L | B1i | 64/1249/96 | 160/2401/112 | 384/4705/128 | 896/9313/144 | 2048/18529/160 |
| M5L | B3i | 64/1249/96 | 160/2401/112 | 384/4705/128 | 896/9313/144 | 2048/18529/160 |

Interval checks (A'): B2@128: 324 in [288, 360] -> True; B2@256: 360 in [324, 396] -> True; U@128: 324 in [288, 360] -> True; U@256: 360 in [324, 396] -> True; P3@128: 324 in [288, 360] -> True; P3@256: 360 in [324, 396] -> True; B0i@128: 324 in [288, 360] -> True; B0i@256: 360 in [324, 396] -> True; B1i@128: 324 in [288, 360] -> True; B1i@256: 360 in [324, 396] -> True; B3i@128: 324 in [288, 360] -> True; B3i@256: 360 in [324, 396] -> True

Increment checks: A' M5 B2 exec_query 1.0 (LOG) -> True; A' M5 U exec_query 1.0 (LOG) -> True; A' M5 P3 exec_query 1.0 (LOG) -> True; A' M5 B0i exec_query 1.0 (LOG) -> True; A' M5 B1i exec_query 1.0 (LOG) -> True; A' M5 B3i exec_query 1.0 (LOG) -> True; B' M5L B0 exec_query 2.0 (LINEAR) -> True; B' M5L B1 exec_query 2.0 (LINEAR) -> True; B' M5L B2 exec_query 1.985 (LINEAR) -> True; B' M5L B3 exec_query 2.0 (LINEAR) -> True; B' M5L U exec_query 1.985 (LINEAR) -> True; B' M5L P3 exec_query 1.985 (LINEAR) -> True; B' M5L B0i exec_query 2.0 (LINEAR) -> True; B' M5L B1i exec_query 2.0 (LINEAR) -> True; B' M5L B3i exec_query 2.0 (LINEAR) -> True; C' M5 B0i exec_build 2.25 (LINEAR) -> True; C' M5 B1i exec_build 2.25 (LINEAR) -> True; C' M5 B3i exec_build 2.25 (LINEAR) -> True

Native build exact (C'): B2@128: 127 (expected 127) -> True; B2@256: 255 (expected 255) -> True; U@128: 127 (expected 127) -> True; U@256: 255 (expected 255) -> True; P3@128: 127 (expected 127) -> True; P3@256: 255 (expected 255) -> True

(D') M5~M5L table-equal at 128/256 in every column: True; C2: True

P2 finite exact certificate; per-phase growth orders of the charged compilation at sizes 128/256 not present in any earlier receipt
