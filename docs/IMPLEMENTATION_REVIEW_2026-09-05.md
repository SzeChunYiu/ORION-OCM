# Runtime and knowledge-space implementation review — 2026-09-05

The revised runtime fixes concrete correctness defects and removes a measured admission
bottleneck. Its evidence model preserves the old milestone records while explicitly reopening
scientific claims affected by invalid adoption fixtures.

## Changes and their purpose

| Area | Implemented behavior |
|---|---|
| Durable actions | Write intent before external callbacks; preserve pending intent after receipt failure; reject reused IDs and state changes during authority checks |
| Ledger and restart | Bind writes to the replayed head, preserve both UNKNOWN bounds, reject invalid derived-evidence revocation before append, require matching host operator metadata after restart |
| Adoption and rollback | Check actual predecessor and proposal identities, stage installation before evidence, reject callback mutation, use copied rollback snapshots and reverse global adoption order |
| Warrants | Revoke dependencies of derived citations; report any independently warranted alternatives that remain after revoking a named lesson |
| Statistical operators | Keep population guarantees separate from individual truth; only a target-specific exact checker grants LIVE status |
| KnowledgeSpace | Cache immutable structure, construct seeds linearly, and use exact positive matrix support for large admission decisions |
| Sparse navigation | Report an exact residual/error certificate for the represented float system, with explicit precision and iteration failures |
| Receipts and CI | Preserve all original receipts, bind current code through declared successors, reject missing/drifting evidence, and label same-scenario comparisons as reference regressions |

Detailed defect histories and boundaries are in [runtime revalidation](RUNTIME_LIFECYCLE_REVALIDATION_V2.md)
and [the knowledge-space report](KSO_OPTIMIZATION_REPORT_V1.md). The revision started from source
base `f2b83e2849b1afb79c45f12bebc3c929080352c9` and incorporated upstream `368260e` (M2b docs/data
archive only). The immutable receipt configuration retains the original source base.

## Validation

- Baseline full suite: **538 passed**, 335.13 seconds.
- Revised full collected suite: **613 passed**, zero errors/failures/skips, 315.10 seconds.
- Subsequently added receipt custody suite: **17 passed**. Combined receipt/KSO check: 55 passed.
  These focused counts overlap other checks and must not be added as independent experiments.
- Final combined runtime, adoption, revocation, statistics, KSO and custody regression run:
  **92 passed**, 2.14 seconds.
- All twelve `python tools/mN_receipt.py --verify` commands passed. Original milestone receipt
  bytes are unchanged; historical artifact reads and new engineering replays are labelled separately.
- Root review independently checked all 13 changed-source predecessor digests against the Git
  parent, exact source-change inventory and all 13 historical M0–M12 receipt files against Git.
- M4/M6 replay outcomes agree with prior deterministic values; cost/latency are observations.
  M11 reference summary and M12 deterministic block agree after fixture binding corrections.
  Agreement is a regression result, not a renewed protected scientific terminal.
- Separate internal reviewers checked runtime/adoption failure cases, 133 exact sparse-system
  error bounds, 240 support cases and the custody mechanism. Internal review does not supply
  an external independent evaluator.

At 256, 1,024 and 4,096 synthetic atoms, median admission improves **4.35×, 7.31× and 15.92×**.
The certified sparse solve is about **32% slower** at 4,096 atoms; its stronger checking has a
real cost. Cached indexes also consume memory, recorded separately. These measurements are
bounded engineering results, not claims of general organisation or cognitive superiority.

## Current acceptance status

M11 is `M11_REFERENCE_REVALIDATED__HISTORICAL_ADOPTION_CELLS_REOPENED`.
M12 is `M12_REFERENCE_REPLAY__PROTECTED_REEVALUATION_REQUIRED`.
The current [programme index](OCM_PROGRAMME_TERMINALS_V1.md) gives the remaining evaluation work.

Required next mechanisms include independently bound stronger parents, corrected protected
adoption/lifetime evaluations, a second language suite, longer lifetimes, codec/semantic-fidelity
evidence and explicit absorption tests for each V2 theory mechanism. External human/reference
arms remain unavailable in the existing evidence. Host executable identity is host-supplied and
unverified; this revision does not certify arbitrary concurrent effects or unrestricted language.
