# Foundation closure V1 — review package

**Terminal: SCOPED_FOUNDATIONS_AND_INDEX_CALIBRATED; FULL_OCM_NOT_ADMITTED.**

This is an additive contribution to #165, not a new architecture lane. It supplies eight conditional foundation results, a frozen-profile liveness index, finite counterexamples and a 31-obligation G1–G8 evidence map. It does not modify historical theory files, receipts, frozen G2 studies or production runtime call sites. Learned routing remains gated.

## Contents

The main argument is in `docs/spec/OCM_FOUNDATIONS_CLOSURE_V1.md`. `GAP_LEDGER.json` maps each obligation to its required closing evidence. `calibration.py` produces the committed `CALIBRATION.json`; the logarithmic calculations are floating-point research references, not numerical admission certificates. Repair ordering and lifecycle identities use exact rational arithmetic.

`src/ocm/kso/warrant_liveness_index.py` adds an optional, epoch-bound index over existing canonical warrant intervals. It shares support clauses and maintains both lower and upper liveness counts. It preserves LIVE / DEAD / UNKNOWN under final-state revoke/reinstate batches. Missing identities and stale epochs raise CANNOT_CHECK. It is not a new admission authority, a durable transaction, or an integrated runtime optimization.

## Reproduce from a repository checkout

```sh
PYTHONPATH=src python -m unittest discover -s tests/foundations -p 'test_*.py' -v
python research/foundations-closure-v1/calibration.py > /tmp/ocm-foundation-calibration.json
```

The suite compares generated and committed calibration: exact fields must agree exactly, and floating-point fields use relative/absolute tolerance 1e-12 for platform math-library rounding. Byte identity is expected only in the same numerical environment. Python 3.11 or later is required by the project. No additional test dependency is required for this focused unittest command. An installed wheel without the repository research directory cannot run these checkout-only research tests.

## Actual local validation

51 focused tests passed: 27 index tests and 24 theory-calibration tests. The index tests include all 168 warrant intervals over three evidence variables and all 64 ordered revocation transitions (10,752 comparisons), plus 80 profiles across 300 deterministic randomized mixed batches (24,000 comparisons). The repair-order test exhausts 729 three-candidate settings against every permutation. Tests include planted lower-only-incidence and Boolean-blocker mistakes, upper-only evidence, alternate versus conjunctive support, mixed swaps, stale epochs, immutable results and 5,000 unrelated profiles.

The local environment contained the exact retrieved `warrant.py` source and the additive files, not a full clone. Its Git blob hash was verified as `6cf431adb2e7e45fe5e23122a482262e45e11211`, matching the branch. Full repository tests, installed distribution checks, integrated runtime replays and remote CI are **not included in this local result**. Test runtime is not a benchmark. `VALIDATION.json` records artifact identities and this scope.

## Important findings

The information cap for adaptive diagnosis must hold conditional on prior history; the XOR counterexample gives two zero-information marginals with one bit jointly. An expected stopping-time lower bound is not rounded up like a deterministic integer horizon.

Shannon effective repair count is not expected repair work. The committed rare-tail example has an effective count below 2.5 but an expected 26,215.425 unit-cost checks. Under the declared one-correct-repair model, decreasing probability/test-cost ratio is optimal; its assumptions do not cover information-rich failures or shared testing.

A common safe action is not necessarily a common optimal action, and a one-step information test can miss useful multi-step probes. Useful reuse is not lifetime payback when acquisition, invalidation and maintenance consume the savings. Current navigation equivalence is not a certificate for future operators. Repeated protected evaluation needs a valid time-uniform or error-spending design and the correct replication unit.

These are conditional mathematical results and authored finite calibrations, not evidence that the machine already achieves developmental intelligence.

## Runtime adoption gate

Before enabling the index in serving: bind its epoch to the actual committed field/operator/scope/authority identity; shadow-compare direct answers on actual runtime transitions; rebuild or invalidate after profile changes; test interrupted commits, restart and replay; preserve owner serialization; and measure build/storage/update costs against the current index or direct parent. Do not promote the logical operation count to a physical speedup. General KS-T12 remains open outside the proven frozen-profile sub-obligation.

## Scientific continuation gate

The preserved G2 length-scaling and utility-aware tournament results are negative at the branch base. Do not tune their frozen families again. A materially different acquisition/search mechanism requires its own prospective registration, fresh task identity, actual method-consumption trace, live/removed/revoked controls and an ordinary persistent parent with the same method. Independent protected evaluation and a heterogeneous persistent lineage remain separate requirements. This package does not renew historical M11/M12 claims or close #165.

The ten bibliographic parents and their ownership boundaries are recorded in the foundation document. No independent expert review or independent replication is claimed by this single-author review package.
