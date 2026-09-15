# GMI capability calibration V2

Child issue: #766. Parent ledger: #602 Section M.

This capsule adds an exact finite-population error-risk certificate to the existing architecture-name-free F4 capability predictor. It intentionally calibrates only the predictor's frozen **determinate frame**; abstained cells remain outside the error-rate population and their loss of coverage is reported explicitly.

V1 (#764) is retained as `ASSAY_DEFECT_NONDETERMINATE_SAMPLING_FRAME`: it sampled before freezing the selective frame and was not rescued post hoc.

V2 custody order:

1. `FREEZE_V2.md` — theorem, predictor identity, grid, sample sizes, deltas, threshold, controls and falsifiers;
2. `build_determinate_frame_v2.py` + `DETERMINATE_FRAME_SHARED_V2.csv` / `DETERMINATE_FRAME_V2.json` — predictor-output-only frame, no oracle correctness;
3. `AUDIT_SAMPLE_V2.json` — 48/64 ids per coordinate drawn uniformly without replacement with OS entropy, committed before scorer/result;
4. `capability_calibration_v2.py` — exact hypergeometric inversion, post-custody scoring, census verification and hostiles;
5. `RESULT_V2.json` — deterministic receipt;
6. `FORMALIZATION_V2.md` — CAL-1..CAL-3 proofs and claim boundary.

Registered result: zero sampled errors on all four coordinates gives exact upper finite-population error rate `3/64` at per-coordinate failure budget `1/80`; four-coordinate simultaneous coverage lower bound is `19/20`. The post-certificate full-frame census has 0/64 errors for each coordinate. Candidate-grid determinate coverage is only `1/16` and is a material limitation.

Claim ceiling:

`EXACT_FINITE_POPULATION_CAPABILITY_ERROR_CALIBRATION_AT_REGISTERED_DETERMINATE_FRAME`

No per-example probability calibration, iid generalization, future-domain calibration or universal G6 claim is made.
