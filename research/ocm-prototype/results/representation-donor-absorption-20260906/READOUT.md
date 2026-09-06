# Readout

Executed source: `a49195bfe942e3b60660d27a9a7bfbc9d033365e`; core base: `29085f80c727f1cb47d3a76df39837b0b6a585d1`. No production source changed. The actual consumer fixture is the hash-checked existing `tests/m2/test_solve_loop.py`.

## Donor roles

| Module | Actual use |
|---|---|
| ORION #908 router | ADAPT mechanism: exact choose(B2); B0 for full arm. No quantum score/RANK or gold eligibility. |
| V2 F2 | ADOPT mechanism/checker: warranted finite-family certification, exploratory lumpability, quotient/push/exact rational solve. |
| V2 field dynamics | ADOPT checker: existing finite-map identity/split-fibre controls only, no OCM lifecycle authority. |
| Original SV fixture | Unchanged consumer/reference and full fine-vector oracle. |
| informed_parent | Same-SV/donor/checker selection ablation, not independent whole-vessel comparison. |

Archive bytes, contracts and notices are pinned in donors/MANIFEST.json. ORION's Apache-2.0 LICENSE/NOTICE are exact copies. V2's pinned tree has NOTICE with intended Apache-2.0 terms but no root LICENSE; this metadata gap is retained without inventing a grant.

## Actual conditions

Each scenario yields 3 arm records and 2 comparisons against full.

| Scenarios | Count | OCM/parent path | Comparisons |
|---|---:|---|---|
| base, alternative, withdraw_one, withdraw_backup, irrelevant, reinstate | 6 | compact | 12 exact |
| incoming, mixed_warrant, missing_state | 3 | full fallback | 6 exact |
| changed_query, changed_config, changed_state, unregistered, mutated_task, mutated_config, mutated_family | 7 | full fallback | 14 exact |
| withdraw_both, withdraw_rule, withdraw_partial | 3 | compact navigation, inherited consumer ERROR | 6 CANNOT_CHECK |

Totals: 19/57 recorded scenarios/arm records, 16/48 completed, 9 errors, 32 exact and 6 uncheckable comparisons. Matching vectors before an error is not downstream success. This purposive panel is not a statistical accuracy/non-inferiority estimate.

N=14 fine atoms; m=6 quotient states. Merged block: original island plus 8 added zero-incident atoms. Reconstruction preserves each original gated seed and alpha. The background seed remains global 1/14.

Warranted checking covers 8 registered revocation states. Exploratory status is explicitly DYNAMIC_LUMPABILITY_ONLY. Fine reconstruction separately requires zero incoming and outgoing kernel entries for merged atoms. The incoming-edge counterexample passes F2 but selects full because fine reconstruction requires refinement.

Task/config digests and the finite revocation family are detached from mutable caller registration. Changed bindings invalidate compact selection. These are independent snapshots: reinstate means empty revocations, not a fresh-process persistence result. The original full reference runs before candidates; compact eligibility executes no full fine linear solve.

## Descriptive cost

Base OCM/parent each record 3 router/quotient/push/compact-solve API entries. Preparation calls F2 certification once and dynamic lumpability 8 times. There remain 3,136 prepared matrix cells and 42 materialized fine outputs.

Base serialized sizes: field 5,496 B; prepared matrices 24,395 B; decoder partition 174 B. These are not resident-memory measurements. The runtime proxy is separately labeled and unchanged.

Whole capture: 1.272125 s wall; self CPU 1.249171 s user + 0.019971 s system; process high-water RSS 37,188 KiB. Preparation/checks/all arms included; child CPU uncounted; other host work not excluded. No comparative performance or O(k) inference.

One capture at 2026-09-06 09:25:54–09:25:55 UTC, PID 111127 reaped, exit 2. Python 3.13.12 / pytest 8.3.5. No model calls or dependency acquisition.

## Original consumer failure

Unpatched SV errors on both fact supports, rule support and partial support. extract_stage pairs exploratory activation with warranted background; PROPAGATED surprise subtracts an ungated uniform seed, creates a negative background residual (observed -1/42), and encounters a logarithm domain error. See raw/original-consumer-withdrawal.json.

A separate core lane owns channel-matched background repair. It is not in this execution, and the three errors remain unchanged.

## Evidence and reproduction

SOURCE.json binds executed source bytes; PLAN.json binds commit/scenarios; SHA256.json seals raw records. Publication copies retain all bytes. Historical absolute paths are metadata, not relocation instructions.

From this packet: `sha256sum -c SHA256SUMS`. To grade the copied raw archive only, import `representation_donor_grade.grade_archive` from the source-bound prototype directory and pass the copied `raw/functional-v1` path; compare its returned dict with raw/functional-v1-grade.json. The grader imports no actor/router/checker.

Focused laptop controls use Python 3.13.12 / pytest 8.3.5 with source imports:
```sh
PYTHONPATH="$PWD/src:$PWD/research/ocm-prototype" python -m pytest \
  research/ocm-prototype/representation_donor_tests \
  tests/m2/test_solve_loop.py -q
```

The original actor command is in raw/functional-v1-launch.json. Any separately desired reproduction must use the executed commit and a NEW output path. Exit 0 means full parity, 1 mismatch, 2 partial CANNOT. No protected or performance authority is created by exposed-fixture replay.
