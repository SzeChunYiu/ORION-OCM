# gmi-833-af-barrier-context-v1

This package closes **issue #833 AF0–AF3 only** at the registered formal/finite scope. It introduces the developmental response object `Gamma`, provenance-tagged null-experience semantics, and typed barrier-context/displacement records while importing the strongest parent results instead of renaming them.

Read in this order:

1. `FREEZE_V1.md` — pre-implementation authority and frozen fixtures.
2. `GMI_BARRIER_PARENT_LEDGER_V1.json` — parent ownership and exact pins.
3. `FORMALIZATION_V1.md` — AF0–AF3 definitions/proofs/scope.
4. `af_barrier_context_v1.py` — deterministic finite exact checker.
5. `independent_oracle_v1.py` — independent reconstruction.
6. `test_af_barrier_context_v1.py` — fail-closed hostile tests.
7. `RESULT_V1.json` / `ORACLE_RESULT_V1.json` — committed deterministic receipts.
8. `OPEN_GAPS_V1.json` — AF4+ and empirical residuals.

Run from this directory:

```bash
python3 -I -B af_barrier_context_v1.py
python3 -I -O -B af_barrier_context_v1.py --output /tmp/af-opt.json
cmp RESULT_V1.json /tmp/af-opt.json
python3 -I -B independent_oracle_v1.py
python3 -I -O -B independent_oracle_v1.py --output /tmp/oracle-opt.json
cmp ORACLE_RESULT_V1.json /tmp/oracle-opt.json
python3 -I -B test_af_barrier_context_v1.py
python3 -I -O -B test_af_barrier_context_v1.py
```

Expected finite witnesses include: same current capability but different `Gamma`; different current capability but the same post-development machine envelope; independent random novelty with `I(target;random)=0`; oracle advice with one bit target information and mandatory imported provenance; target-correlated nonuniform/arbitrary-real initialization classified as imported information/advice; and the mandatory-overhead reversal `8 -> -4` that blocks unconditional resource monotonicity.

Claim ceiling: `GMI_AF0_AF3_DEVELOPMENTAL_RESPONSE_PROVENANCE_AND_BARRIER_CONTEXT_FORMALIZED_AT_REGISTERED_FINITE_SCOPE`.
