# Machine Epistemics lifelong-scaling programme V1

Owner: ORION-OCM issue #50. Parent roadmap: #42. Corrected evaluation gate: #38. Language-first steering: #52.

This directory turns the research thesis into executable measurement and a preregistered decision path. It intentionally does **not** close the scientific question with historical or synthetic results.

The instrumentation is intentionally kept in this **prospective research lane** rather than `src/ocm`: adding it to the canonical runtime would rewrite already-sealed engineering source inventories from earlier milestones. N1–N5 should absorb the contract only through their own new receipts when those mechanisms are authorized. The calibration tests also remain in this research directory rather than the sealed root `tests/` inventory for the same reason.

## What landed

- `ME_RESEARCH_THESIS_SPEC_V1.md` — D1 definitions of `N`, `k`, acquisition/query cost, revision cone, reuse and resource vector.
- `lifetime_metrics.py` — D2 reusable prospective receipt/counter objects plus KSO state adapter and comparator-parity checks.
- `ME_LIFETIME_RECEIPT_SCHEMA_V1.json` — D2 machine-readable common receipt schema.
- `calibration.py` + `ME_SYNTHETIC_CALIBRATION_V1.json` — D3 exact planted acquisition/scaling/revision worlds and D6 pilot A/B/C/E/F outputs; Figure D correctly returns CANNOT_CHECK rather than inventing a cost scalar.
- `test_lifetime_metrics.py` — research-lane hostile/no-alarm/CANNOT_CHECK tests for the meters, including denominator padding and hidden-global-scan attacks.
- `ME_LANGUAGE_ACQUISITION_PROGRAM_V1.md` — makes learned communication from a minimal substrate the first domain-level H1/Figure A-E experiment, aligned with #52/#53/#54/#55 and ORION-V2#361.
- `ME_LIFETIME_BENCHMARK_V0.md` — D4 frozen lifetime topology/orders/scales; protected instance hashes remain gated on N3/N5.
- `ME_COMPARATOR_MANIFEST_V1.md` — D5 strongest-parent contract and explicit finding that the current simple matched parent is not strong enough for all #50 hypotheses.
- `ME_CONFIRMATORY_PREREGISTRATION_V0.md` — D7 analysis rules frozen prospectively; V1 cannot bind task hashes while N3/N5 are locked.
- `ME_PAPER_ARGUMENT_LEDGER_V1.md` — D8 Principle→Mechanism→Prediction→Evidence→alternative→terminal map.

## Exact calibration result

Run:

```bash
python research/machine-epistemics-lifetime-v1/calibration.py
python -m unittest research/machine-epistemics-lifetime-v1/test_lifetime_metrics.py -v
```

V1 local authoring replay after reviewer hardening: **12/12 tests GREEN**.

The synthetic pilot terminal is:

`PARTIAL_SIGNATURE_ONLY_SYNTHETIC_METERS_CALIBRATED`

The confirmatory terminal is:

`CANNOT_CHECK_N3_N5_LOCKED_AND_FRESH_MATCHED_LIFETIMES_NOT_RUN`

## Important findings already forced by the four-reviewer process

1. **Amortized acquisition is not unique by itself.** An explicit skill-library parent reproduces the toy declining acquisition curve exactly.
2. **Sparse retrieval is not unique by itself.** A strong indexed parent can avoid global corpus scans too.
3. **Local exact revision is not unique by itself.** TMS/ATMS-style reason maintenance is the strongest parent family and must be subtracted.
4. **The current `navigation_sparse.py` is adjacency-sparse but not yet evidence for `O(k)` task cost.** Its fixed-point iteration still updates every state row, so #50's `k` meter must expose rather than hide that work.
5. **`N` cannot be padded by untouchable aggregate counts.** Identity-bearing object counts define the denominator; aggregates such as current warrant-set cardinality are auxiliary until aligned identity-level touch instrumentation exists.
6. **The current historical matched parent is not a universal #50 parent.** It deliberately omits several tested powers; the confirmatory study requires the composite P6 contract.
7. **Historical M12 V4 cannot be recycled as confirmation.** #38 prospectively reopened the lifetime matching/persistence inference, so those outcomes are calibration/background only.
8. **Prospective measurement must not invalidate historical receipts.** The first CI pass correctly caught canonical-source inventory drift when the meter was placed under `src/ocm` and when the new hostile test lived under root `tests/`; V1 now preserves the old sealed runtime/test inventory and leaves absorption to future milestone receipts.
9. **Language should be the first substantive amortized-acquisition domain.** The time-zero language substrate must be minimized and counted, compositionality must be protected, and later-family acquisition savings must survive persistent grammar/skill/memory/adaptation parents before being called language meta-learning.

These are constructive negative findings: they sharpen the paper from "OCM has several nice mechanisms" into a test of whether their *joint governed lifelong coupling* produces a distinct regime.

## Exit discipline

Do not close #50 as supported until the N3/N5-era fresh protected lifetime exists and the P6 comparator is actually instantiated. Language can earn its own earlier terminal under #52/#53, but it does not by itself establish the cross-domain thesis. If the project must stop before the confirmatory lifetime exists, close with the explicit `CANNOT_CHECK_...` terminal rather than converting design completion into scientific support.
