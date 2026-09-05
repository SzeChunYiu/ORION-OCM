# Machine Epistemics lifelong-scaling programme V1

Owner: ORION-OCM issue #50. Parent roadmap: #42. Corrected evaluation gate: #38.

This directory turns the research thesis into executable measurement and a preregistered decision path. It intentionally does **not** close the scientific question with historical or synthetic results.

## What landed

- `ME_RESEARCH_THESIS_SPEC_V1.md` — D1 definitions of `N`, `k`, acquisition/query cost, revision cone, reuse and resource vector.
- `src/ocm/evaluation/lifetime_metrics.py` — D2 reusable runtime receipt/counter objects plus KSO state adapter and comparator-parity checks.
- `ME_LIFETIME_RECEIPT_SCHEMA_V1.json` — D2 machine-readable common receipt schema.
- `calibration.py` + `ME_SYNTHETIC_CALIBRATION_V1.json` — D3 exact planted acquisition/scaling/revision worlds and D6 pilot A/B/C/E/F outputs; Figure D correctly returns CANNOT_CHECK rather than inventing a cost scalar.
- `tests/test_lifetime_metrics.py` — hostile/no-alarm/CANNOT_CHECK tests for the meters.
- `ME_LIFETIME_BENCHMARK_V0.md` — D4 frozen lifetime topology/orders/scales; protected instance hashes remain gated on N3/N5.
- `ME_COMPARATOR_MANIFEST_V1.md` — D5 strongest-parent contract and explicit finding that the current simple matched parent is not strong enough for all #50 hypotheses.
- `ME_CONFIRMATORY_PREREGISTRATION_V0.md` — D7 analysis rules frozen prospectively; V1 cannot bind task hashes while N3/N5 are locked.
- `ME_PAPER_ARGUMENT_LEDGER_V1.md` — D8 Principle→Mechanism→Prediction→Evidence→alternative→terminal map.

## Exact calibration result

Run:

```bash
PYTHONPATH=src python research/machine-epistemics-lifetime-v1/calibration.py
python -m unittest discover -s tests -p 'test_lifetime_metrics.py' -v
```

V1 local authoring replay: 9/9 tests GREEN.

The synthetic pilot terminal is:

`PARTIAL_SIGNATURE_ONLY_SYNTHETIC_METERS_CALIBRATED`

The confirmatory terminal is:

`CANNOT_CHECK_N3_N5_LOCKED_AND_FRESH_MATCHED_LIFETIMES_NOT_RUN`

## Important findings already forced by the four-reviewer process

1. **Amortized acquisition is not unique by itself.** An explicit skill-library parent reproduces the toy declining acquisition curve exactly.
2. **Sparse retrieval is not unique by itself.** A strong indexed parent can avoid global corpus scans too.
3. **Local exact revision is not unique by itself.** TMS/ATMS-style reason maintenance is the strongest parent family and must be subtracted.
4. **The current `navigation_sparse.py` is adjacency-sparse but not yet evidence for `O(k)` task cost.** Its fixed-point iteration still updates every state row, so #50's `k` meter must expose rather than hide that work.
5. **The current historical matched parent is not a universal #50 parent.** It deliberately omits several tested powers; the confirmatory study requires the composite P6 contract.
6. **Historical M12 V4 cannot be recycled as confirmation.** #38 prospectively reopened the lifetime matching/persistence inference, so those outcomes are calibration/background only.

These are constructive negative findings: they sharpen the paper from "OCM has several nice mechanisms" into a test of whether their *joint governed lifelong coupling* produces a distinct regime.

## Exit discipline

Do not close #50 as supported until the N3/N5-era fresh protected lifetime exists and the P6 comparator is actually instantiated. If the project must stop before then, close with the explicit `CANNOT_CHECK_...` terminal rather than converting design completion into scientific support.
