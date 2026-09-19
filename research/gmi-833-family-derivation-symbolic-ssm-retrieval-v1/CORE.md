# GMI #833 — Symbolic / SSM / Retrieval Derivation

**What this is.** A family-neutral finite-scope derivation package for three Section-H rows: symbolic logic systems (K05), state-space models (M-FAM), and retrieval-augmented systems (K08). The frozen substrate is the post-search-blind neutral battery and `ADD`/`NEG`/`GE_c` basis; family fingerprints are read only by the posthoc adjudicator.

## Outcome

| family | predicted morphology | recovered morphology | terminal | primary result |
|---|---|---|---|---|
| Symbolic logic systems (K05) | compositional term transformation and successor selection | no adjudicated recovery | `NOT_RECOVERED_AT_SCOPE` | T1 champion `[133, 2]`; full-battery error count is unavailable because the search champion did not solve its fitness subset; independent sample errors `148` |
| State-space models (M-FAM) | affine recurrent state with superposition | affine, gate-free subset; delay-degenerate C3 | `RECOVERED_FOR_SUBSET_SEE_LIST` | 231 affine tables; 195 gate-free realizable; 20 sampled machines independently simulate correctly; step-map superposition passes; no sampled superposed-memory witness |
| Retrieval-augmented systems (K08) | persistent stored items, query selection, causal retrieval | no adjudicated recovery | `NOT_RECOVERED_AT_SCOPE` | T3 champion `[8, 1]`, independently verified at 8 errors on 56 episodes; order-fixed twin `[4, 1]` |

The nulls contain 200 seeds for both stochastic tranches. Remint output is blind and present. `REMINT_OUTCOME_V1.json` reports B_EP `[8, 2]` with 8 verified errors, B_CONTR `[133, 2]`, and 146/444 equal-cost B_W2 complement pairs.

## Claim ceiling and forbidden promotions

The claim ceiling is `FDT_SYMBOLIC_SSM_RETRIEVAL_DERIVATION_AT_DECLARED_FINITE_SCOPES`. The package supports only the finite batteries, guards, cell caps, DP/exhaustion bounds, and stochastic budgets recorded in `THEORY.md` and the outcome files. It does not support cross-scope gate composition, M5 or independent-team replication, real-scale claims, learning claims, universal family claims, or promotion of the order-fixed/readout-only negative twins as family recoveries. K05 and K08 are explicitly open; M-FAM is subset-only and delay-degenerate for C3 in the adjudicated sample.

## Reproduce

Compute only on a numpy host such as `billy-laptop`:

```bash
python3 -B run_tranches_v1.py t1
python3 -B run_tranches_v1.py t2
python3 -B run_tranches_v1.py t3
python3 -B run_remint_v1.py
```

The CI-side checks are stdlib-only:

```bash
python3 -B screen_v1.py
python3 -B posthoc_adjudicate_v1.py
python3 -B check_v1.py
python3 -O -B posthoc_adjudicate_v1.py
python3 -O -B check_v1.py
```

Both checker modes produce `RESULT_V1.json` with status `GREEN`; the custody, battery, parent-pin, screen, blind-outcome, recomputation, posthoc self-test, and clause-bijection assertions all pass.

## Custody

The pre-search freeze is commit `98bd9369`; the frozen battery SHA-256 is `5b385f0edfa035b28940f5dd982e0c69991a2ce6e0175e4c693073add26899f0`. Outcomes and adjudication files were created only after implementation and blind runs. See `POSTHOC_RESULT_V1.json`, `CLAIMS_V1.json`, and `RESULT_V1.json` for machine-readable evidence.
