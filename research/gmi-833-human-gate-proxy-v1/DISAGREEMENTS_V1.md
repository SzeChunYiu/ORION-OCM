# DISAGREEMENTS_V1 — where the lane disagrees with a proxy verdict

Rule (FREEZE_V1.md §3): a verdict is never edited or re-prompted; disagreement is recorded beside it
and the verdict stands. Every item below leaves the proxy's verdict and the row's status unchanged.

| proxy | verdict item | lane position | consequence |
|---|---|---|---|
| PX-Z18-EXP | OBJ-9 (R07/R08 "appear in no readable registration artifact") | The registration exists in `FREEZE_V3_ADDENDUM.md` (outside the reviewer's permitted set). The residual point — registered after the V2 outcomes — is conceded (`DG-C1-TRANCHE`). | verdict stands; disposition RESOLVED in RESPONSES_V1.md, accepted by the editor "for the permitted-set half only" |
| PX-Z18-EXP | OBJ-14 (no outcome artifact for heldout-20) | The artifact exists (`RESULT_V1.json` of that package). The editor reclassified the disposition to DOWNGRADED via `DG-C1-20CASES` because rule 2 bars crediting a GREEN field; the lane accepts the reclassification. | no change |
| PX-Z18-STAT | OBJ-S8 (no receipts for unlicensed systems) | `REAL_RUNS/R01…R12` exist in the receipts package. | verdict stands; accepted by the editor with the caveat that the editor could not open them |
| PX-Z18-STAT | OBJ-S20 (A12 null uncharacterised) | The null family is characterised in the grammar-growth package; the blind-set characterisation is not. The editor reclassified to OPEN; the lane accepts. | `RV-C5-A12-NULL` |
| PX-Z18-EDIT | reopen of "RESPONSES_V1.md §8 summary table" | Correct: the table totals 72 where the verdict blocks carry 78 `material: yes` lines and mis-files two LIT objections. Corrected in `RESPONSES_V1_ERRATA.md`; `RESPONSES_V1.md` is left as the editor read it. | honoured in `REOPENED_GATES_V1.json` |
| PX-Z9-T2 (batch 2 note on B2-E07) | "Any prediction of PERSISTENT_STATE here, at either price, is a false positive." | The exact outcome at lambda = 1/100 is PERSISTENT_STATE (E_stateless = 1/20, E_onebit = 0, lambda* = 1/20 > 1/100), as PX-Z9-P2 predicted; the test team's control note was wrong, the prediction right. | outcome recorded; the environment stays in the batch as authored |
| PX-AA41 | AA41 NOT_SATISFIED partly because "every branch bottoms out in bound artifacts Rule 1 forbids opening" | The brief's read restriction, not the artifacts, produced part of the UNVERIFIABLE leaves. A second sweep with a wider permitted set is the revival lever; the verdict is not contested. | row stays open; lever registered in CLAIM_DOWNGRADES_V1.json (`RV-C5-SUPPLEMENT`) |

No proxy verdict was found to rest on a misreading that would change a row's status.
