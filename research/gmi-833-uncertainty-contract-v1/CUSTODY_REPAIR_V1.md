# CI custody repair after failed PR run — v1

**Issue:** #851  
**PR:** #852  
**Failed run:** `35013395447`  
**Failed exact/hostile jobs:** normal `104530677632`, optimized `104530677633`

## Failure retained

The first PR run failed closed after freeze custody passed. The exact/hostile suite raised `FileNotFoundError` for:

`research/gmi-capability-calibration-v2/RESULT_V2.json`

while auditing the fourth strongest-parent receipt.

This failure is preserved as evidence. No checkbox was moved and no claim ceiling was raised.

## Diagnosis

The frozen scientific registration was not stale:

- the canonical path exists on current `main`;
- it exists on immutable PR head `c448ba1c93dcc1bd24ef6545aaf3288f1b838ef8`;
- it exists on the synthetic PR merge commit;
- all three map that path to the frozen Git blob
  `278845962ef2a573d3664fc3a400591e440ed313`.

Thus the defect is a checkout/worktree materialization discrepancy, not a scientific parent-selection or blob-identity error.

## Repair

The workflow now verifies each strongest-parent authority in the canonical Git tree before tests:

1. `git rev-parse HEAD:<path>` must equal the frozen expected blob;
2. if the working-tree path is absent, materialize exactly `git show HEAD:<path>`;
3. `git hash-object <materialized file>` must still equal the frozen expected blob;
4. the Python parent audit then rechecks blob content, claim ceiling, and a load-bearing semantic field.

This strengthens rather than weakens custody: a missing worktree file may be reconstructed only from the exact registered Git object already present at the checked-out commit. A missing Git-tree path, wrong path→blob binding, wrong content, claim-ceiling drift, or semantic drift still fails closed.

## Scientific effect

None.

The freeze commit remains immutable; theorem statements, parent logical authorities, expected scientific receipt, exact rational results, and #833 reconciliation scope are unchanged.
