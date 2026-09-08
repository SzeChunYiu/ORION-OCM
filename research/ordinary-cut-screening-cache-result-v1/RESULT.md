# Complete registered screening

The [accepted counts](review/outcome/COUNTS.json) and [exact result](records/result/RESULT.json)
cover all 76 original ordered occurrences, including two repeated canonical IDs
(74 distinct IDs), and the unchanged ordered P1: 4,223 theorems and 100 axioms.

| Recorded outcome | Rows | Witnesses |
|---|---:|---:|
| ALIAS_FOUND_PROOF_READY | 44 | 48 |
| SCREENED_NEGATIVE_IN_DOMAIN | 32 | 0 |
| UNKNOWN | 0 | 0 |

All 76 rows report complete grammar/query coverage and 4,323 parent visits:
328,548 visits in total. The 48 witnesses contain 192 proof labels. Each SCREEN
file equals its corresponding RESULT row; all 77 regular outputs are in RAW.

A negative means no alias in the registered single-logical-assertion model,
with ordered premise reuse/omission and the supported syntax grammar. It does
not rule out multi-step derivations, other aliases, or more expressive interfaces.
The 32 rows are candidates for further work, not established novel theorems.

Proof-ready aliases have structural syntax evidence from the accepted producer.
This attempt made **zero native calls and zero new native admissions**. Neither
this package nor its retained-data review rechecks the witness proofs.

The source-bound telemetry reports 5,444,438 syntax requests: 5,422,830 hits and
21,608 misses/entries. Returned statuses total 5,274,205 registered-grammar
nonmembership results and 170,233 proved results. There was no recorded
UNKNOWN/refusal/bypass or exhausted matcher work; 1,773,758 states were used
within the registered 2,000,000-state domain.

The cache removed enough repeated parsing work to complete this population.
The [review](review/outcome/REVIEW.json) does not claim a new algorithm, acquisition,
held-out utility, or a matched-work speedup.
