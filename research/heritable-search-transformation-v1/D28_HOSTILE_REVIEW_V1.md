# D28 Hostile Review V1 (fresh-context)

Lane D28 of SzeChunYiu/ORION-OCM#233. Reviewed head `a70c2f7a`. Machine-readable record:
`D28_HOSTILE_REVIEW_V1.json` (this file is its distilled view; the JSON is authoritative).

**Verdict: PASS_WITH_FINDINGS** (3 MEDIUM, 4 LOW, 2 INFO).

The review hunted specifically for: claims exceeding registered ceilings, post-freeze edits,
dropped negatives, and checkers that never ran. None of those four defect classes was found.
What was found is structural: the freeze chain binds statements but not evidence artifacts.

## What passed
- Freeze chain VERIFIED at the reviewed head (20 checks, exit 0); selftest green.
- All five core docs byte-match their newest recorded amendments; no frozen statement silently edited.
- Registries append-only since freeze.
- Negatives retained everywhere they were earned (D20 PARENT_SUFFICIENT, RV_B1 self-refutation with
  the wrong original text kept verbatim, D21 denominator correction with original numbers retained).
- Every results file carries an explicit P2 claim ceiling; no P2-to-P1 inflation.

## Findings
| id | severity | one-line |
|----|----------|----------|
| F1 | MEDIUM | No freeze manifest names any of the 8 `exact/results/*.json`; post-landing edits to landed results are invisible to the chain (two real, disclosed instances: `905a7200`, `97b38de2`). |
| F2 | MEDIUM | `RV_B1_RESULTS.json` is not byte-reproducible from its emitter: `exact/rv_b1.py:630` still writes the original overclaiming summary that the committed file's hand-added `correction_C1` replaced. |
| F3 | MEDIUM | Provenance anchor `freeze_commit 11d165b7` (cited in `d19.py`, `d20.py`, both D19/D20 results) is unreachable from every ref; resolvable only in long-lived clones. |
| F4 | LOW | H-D19b and H-D20b live only inside `D19_D20_PROTOCOL_V1.json`; HOSTILE_REGISTRY census stays 27 vs ground truth 29. |
| F5 | LOW | THEOREM_REGISTRY statuses all OPEN although 14 rows are PROVED_LOCAL since #275. |
| F6 | LOW | Receipts implement 7 of the 13 frozen receipt field families; the B_exec vector is absent from every receipt. |
| F7 | LOW | `IN_FLIGHT_COORDINATE_MAP_V1.json` still shows D21/D22 as IN_FLIGHT though both landed (#289, #285). |
| F8 | INFO | Two coexisting legal freeze patterns (standalone lane freeze vs core amendment). |
| F9 | INFO | `oracles_d17.py` T72 default flip was disclosed in-commit but would have been chain-enforced had emitters been hash-bound. |

## Fix levers (cheapest first)
1. Append-only status amendment: 14 rows OPEN -> PROVED_LOCAL(D17) (F5); hostile registry +2 rows (F4).
2. Retarget four `freeze_commit` references to main-reachable commits (F3).
3. Fold the RV_B1 correction into its emitter and regenerate (F2).
4. Bind results + emitter hashes in lane freezes at landing time (F1/F9; staged hook to #221).

## Hooks
Staged in the JSON (`hook_plan`), NOT posted: registry rule says hooks only AFTER review.
