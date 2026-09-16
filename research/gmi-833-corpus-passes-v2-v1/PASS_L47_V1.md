# PASS-L47 — assumptions introduced after observing outcomes (post-hoc)

**Screen (mechanical, git add-order over 231 packages):** freeze vs RESULT/RECEIPT vs
executor first-add orderings. Flags: 2 RESULT_PRECEDES_FREEZE, 18 TIGHT_GAP_EXECUTOR
(<=120 s), 45 SINGLE_COMMIT_FREEZE_RESULT; 17 PROSPECTIVE_ORDERED unflagged; 149
NO_FREEZE_ARTIFACT (no prospective-ness claim to audit).

**Adjudication:** the 2 RESULT_PRECEDES exhaustively read; stratified 30 of 63 of the
remainder (9 tight / 21 single, proportional, random.Random(833212)); 33 flagged packages
SCREENED-NOT-ADJUDICATED. Verdict vocabulary per frozen protocol: a custody gap is NOT a
defect.

| verdict | n | note |
|---|---|---|
| POST_HOC_SUSPECT (confirmed) | **1** | gmi-novel-intelligence-w4-v1 — see below |
| TYPED_POST_HOC | 2 | morphogenesis (screen FP: typed post-execution manifest); aj10 (typed post-freeze heldout +16 s) |
| CUSTODY_NON_DEMONSTRABLE | 18 | gap states incl. 5 NEW tight-gap occurrences of the registered class |
| PROSPECTIVE_DEMONSTRABLE | 11 | single-commit squashes whose surviving source refs show >120 s separation |

**The one confirmed defect (double-verified: reader + owner independent git evidence):**
`gmi-novel-intelligence-w4-v1` — RESULT_V1.json ("all_w4_boxes_green") committed
`08c4d206` 2026-09-15T16:54:44+02:00; FREEZE_V1.md committed `7ce73e5d` 18:23:27+02:00,
89 minutes later; `git merge-base --is-ancestor` confirms the result commit is a true
ancestor of the freeze commit; the freeze's own line 3 claims "Frozen **before**
family-member search on this branch." Mitigating (recorded, does not clear): the freeze
SEED literal + sha256 pre-existed inside the WIP executor (`novel_intelligence_w4_v1.py:29`);
the freeze DOCUMENT did not. Flagged for the owning lane; not edited here.

**Registered instance:** INSTANCE-CONFIG-FREEZE-SEPARATION (#931 E2; AJ9b/c/d
12 s/10 s/13 s) reproduced exactly and not double-counted. NEW same-class occurrences:
AJ9e 10 s, AJ9h +14 s (post-freeze config), AJ12 12 s, g0-interaction-channels 103 s,
useful-descendant 49 s.

**Claim:** post-hoc identification at frozen scope: 1 confirmed suspect, 5 new
registered-class occurrences, 18 custody gaps, 2 typed-legitimate, 11 clean; screen
false-positive class recorded (typed post-execution manifests named FREEZE*).
