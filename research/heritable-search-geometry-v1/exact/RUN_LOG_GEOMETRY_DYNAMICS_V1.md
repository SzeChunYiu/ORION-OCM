# Run log — geometry_dynamics_check_v1.py (lane F, rungs R4/R5)

- Host: billy-laptop (ssh), python3 (3.8.x). Mac did edits only.
- Transfer: scp; md5 identical both sides for the script
  (`effed34fc8ea80081a3eb2bd0cdb05ac`) and for every retrieved artifact
  (11 witness/hostile JSONs + run log; each verified MD5_OK).
- Result: exit 0 — `SUMMARY pass=11 fail_or_unchecked=0`. Full console log in
  `run_v1.log` (byte-identical to the laptop-side run.log, md5 119b5d6e…fae3).
- Exactness: exact-Fraction arithmetic for C1–C9, C11; C10 (KL/Fisher) is float
  and flagged so in its witness ("arithmetic": "float …").
- Witness scope: every JSON certifies its finite specialization only; no JSON is
  a rung verdict (freeze step A6).

## History (one earlier run, retained for honesty)

First run (script md5 c48aba…): 6 PASS, 5 aborts. Diagnosis and fixes — all five
were defects in MY draft claims/code, which is the checker doing its job:

1. C1: my draft claim "deterministic U cannot amplify TV" is FALSE for
   state-dependent U (U reads Σ; the transport map differs per state). Verdict
   for G09 R4 corrected to LIFT_CONDITIONAL (state-shared transport), with the
   falsification kept as the witness's substantive content.
2. C1: hand-arithmetic slip δ(Q) = 1/2 (actual 3/4).
3. C4: mirror case constructed wrong (affected node inside the ball).
4. C5: scalarization weights wrong (w=(1/20,1) does not evict; w=(2,1) does).
5. C6: dict lookup missed reversed key order.
6. C10: tolerance/order mismatch (Jeffreys O(δ) remainder needs δ ≤ 2^-8).
7. C7: no math defect — the alarming printed value was a giant unreduced-looking
   Fraction ≈ 1/800 (transient tail at T=400); note now prints a float.

Second run (md5 0b3e29…): 9 PASS (C1, C5 remaining — the two arithmetic slips).
Third and final run (md5 effed3…): 11/11 PASS, exit 0. Laptop tmp cleaned.
