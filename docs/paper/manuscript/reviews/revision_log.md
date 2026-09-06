# Revision log (pipeline round 2, 2026-09-05)

One row per change to main.md, claims_map.md, figures.md or tools/paper, with the change class from the pipeline's freeze-delta vocabulary (new evidence, reanalysis, correction, figure/table redesign, explanation/structure repair, reporting repair, limitation added, claim narrowed, claim removed, target/article type changed). Concern ids refer to reviews/reviewer_*.md and reviews/editor_synthesis.md; "pre-review" marks repairs made from the claim audit and the repository state before the reviewer round.

## Round 2a: pre-review repairs (claim audit and repository state)

| # | Surface | Change | Class | Evidence |
|---|---|---|---|---|
| 1 | tools/paper/verify_claims.py | the inherited script expected a five-column claim table while claims_map.md was a four-column table, so it checked 0 rows; claims_map.md was rewritten in the five-column checkable format (246 rows); the script gained `main:` sources (files read from origin/main), `count` and `regexcount` clauses | reporting repair | claims_verification.txt: 246 rows, 246 OK; planted-defect run: one wrong number, one wrong phrase, one missing file and one wrong string all caught (MISMATCH ×2, PHRASE_MISSING, MISSING_FILE, exit 1) |
| 2 | main.md §6, Table 9 | four-class grading denominator 480 replaced by 472 (Yes/UNKNOWN-licensed questions; the one unverified-source question per stream excluded), matching the V4 report on origin/main | correction | claims rows 202, 8 |
| 3 | main.md abstract, §5.5, Table 1, §5.1 | "10^5 atoms" removed from the organisation result; M8 is parent-sufficient at the evaluated scale (four regions of eight atoms; 167-atom stream); the 10⁵-atom row is named as the M2 runtime scaling baseline | correction, claim narrowed | claims rows 7, 85, 118 |
| 4 | main.md Table 10, §8 | theory batch 7 stated as merged to the ORION-V2 main branch (pull request 349, 2026-09-05) | correction | claims row 221 (the batch file is read from origin/main) |
| 5 | main.md §5.11 | V4 primary-family parent range 0.593–0.611 (was 0.574–0.611 in the superseded report) | correction | claims row 188 |
| 6 | main.md §8 | intake record restated at its batch-7 revision: 15 intakes (11 defect-found, 2 discharged, 2 open), 2 exports, read from origin/main | correction | claims row 222 |
| 7 | main.md §5.8, Table 5, §5.9, §5.11, §9, §3, abstract | runtime revalidation of 2026-09-05 reported: adoption gate keyed by machine, seven M11 cells and three M12 V2 phase-G cells reopened, engineering replay reproduces the descriptive summary without renewing a protected result, current programme labels for M11 and M12; interval-persistence, dialogue-promotion and coverage-certificate defects listed | limitation added, claim narrowed | claims rows 10, 151–153, 232–234 |
| 8 | main.md §5.9, Table 6, §5.11 | cross-domain transfer family reported as unequal cell sets (6 machine cells vs 4 parent cells) and undetermined as a comparison, per the current evaluation on origin/main | claim narrowed | claims rows 157, 158, 194 |
| 9 | main.md §6 | the two graders' disagreement on the reference arm's honest unknowns (summary grader 7 vs four-class grader 3, four items in two streams) reported instead of silently reconciled | reporting repair | claims row 203 |
| 10 | main.md §4 | "55 facts for every language arm" corrected to 55 for the machine and matched parent, 52 for the template floor | correction | claims row 76 |
| 11 | main.md Table 9 | V2-suite decision-arm columns relabelled as the fresh M7 V2 arms (the lifetime instance's per-step lesson counts differ by carried state); always-attempts row sourced and derived explicitly | reporting repair | claims rows 198, 201 |
| 12 | main.md references | reference [1] (Bommasani et al., foundation models) removed and the sentence rewritten to cite nothing, because no repository document names it; remaining 44 references verified online (CrossRef for 37 DOIs, arXiv for the Qwen2.5 report, bibliographic search for the Biba report, the Kemeny–Snell and Kish books and the Bar-Hillel–Perles–Shamir article; the UD 2.14 handle resolved to LINDAT by redirect but the landing page timed out twice); Biba and Kemeny–Snell entries given their edition details; all in-text citations renumbered | correction | reviews/readiness_report.md, reference table |
| 13 | main.md whole | prose trimmed from 9,662 to 8,522 body-prose words (10 passes), keeping every receipt-bound number | explanation/structure repair | tools/paper/prose_wordcount.py |
| 14 | figures.md | Figure 1, 5, 6, 7, 8 and S2 recipes updated for the reopened cells, the 472 denominator, the grader disagreement, rows S37–S38 and the M8 scale; display-budget note added | figure/table redesign (plan only; no plot executed) | — |

## Round 2b: repairs from the reviewer round (editor decisions in editor_synthesis.md)

| # | Concern | Surface | Change | Class |
|---|---|---|---|---|
| 15 | R1-1 | §5.11 | the two-value structure of the primary family's differences stated (parent 0.611 in six lifetimes, 0.593 in two; differences 0.370 and 0.389) | claim recalibration |
| 16 | R1-2 | §5.8, §5.10 | self-repair counts marked as frozen receipt values under the reopened gate; V3 self-repair sentence names the shared harness | claim narrowed |
| 17 | R1-3 | Table 8 | E row verdict carries "unequal cell sets, undetermined as a comparison" | reporting repair |
| 18 | R1-4 | Table 9 caption, §6 | grader named per surface; 240 − 237 = 3 spelled out | reporting repair |
| 19 | R1-5 | §4 | exact size 65/256 of the n = 54 item-level test under blocks of six added | statistics reporting |
| 20 | R1-6, R1 minor | Table 3 caption, Methods | "inconclusive" defined; interval shape explained; rounding rule and reproduced checker set named | reporting repair |
| 21 | R1 minor | §6 | "answered from pretraining" replaced by "asserted an answer"; the pretraining attribution stays as interpretation in the G7 paragraph | claim recalibration |
| 22 | R2-2, R3-2 | abstract | contribution restated as a comparison discipline plus one replicated residual; "parent-sufficient" glossed | claim recalibration |
| 23 | R2-4 | §1 | methodological significance claim stated once; parent-subtraction tables and the reference arm named as the only comparison surfaces for contemporary systems | explanation repair |
| 24 | R3-3 | Tables 6, 7, 8 captions | unit, test, α, family role and verdict tokens defined | reporting repair |
| 25 | R3-6 | Data availability | repository host and code licence named; archived release stated as pending | compliance (partial) |
| 26 | claims map | rows 242–246 | new rows for the round-2b numbers | reporting repair |

Not done in this round (recorded, not dropped): R2-1 (contemporary-systems positioning with verified citations; needs a literature pass, out of this round's web scope), R2-3 (venue-specific 3,500-word form; a target decision), R2-5 (theory loop as a worked result or companion paper), R3-1 and R3-4 (full identifier and register rewrite; deferred to the venue-specific rewrite), R3-6 archive (a pre-submission action), header note removal (at submission).

## Targeted re-review

Re-review packets were sent to the original concern owners with the changed surfaces only.

| Concern | Owner | Re-review outcome |
|---|---|---|
| R1-1 | reviewer 1 | closed: the two-value structure is stated and the collapse flag's binary nature is explained |
| R1-2 | reviewer 1 | closed as narrowing; the protected re-evaluation stays open as author evidence |
| R1-3, R1-4, R1-5, R1-6 | reviewer 1 | closed |
| R2-2, R2-4 | reviewer 2 | closed |
| R2-1 | reviewer 2 | closed 2026-09-06 (round 2): the seven-family positioning with verified references is Section 1.1 of main.md; assimilation-first, receipt-field per difference, no novelty or superiority sentence |
| R3-2, R3-3, R3-5 | reviewer 3 | closed |
| R3-6 | reviewer 3 | partially closed; archive pending |

Post-revision consistency checks: claim verification re-run (246 rows OK, exit 0); word count re-run (body prose 8,726; 9,417 with headings, captions and the header note); no new numbers without a claim row; reference numbering contiguous 1–44 with every entry cited.

## Pipeline round 2 (2026-09-06, in progress)

Opened with R2-1 closed. Remaining round-2 items wait for their receipts to reach main: the V4-R re-evaluation under the corrected adoption gate (decision label CANNOT_CHECK_CURRENT_SCIENTIFIC_PROMOTION with the historical rule kept as diagnostic), the matched transfer cells for E, the batch-8 intake (commitment-gate epoch refusal) and the N1 open-vocabulary results. Claim verification after the merge: 246 rows OK, exit 0.

### Round-2 reviewer items

| Item | Reviewer | Disposition |
|---|---|---|
| R1-r2-1 / R3-r2-1 | 1, 3 | accepted: 5.10 reports proportions over the sentences reached; load-free re-run scheduled as receipt of record |
| R1-r2-2 | 1 | applied: ORION-V2 batch-8 commit named in data availability |
| R2-r2-1 | 2 | closed: the 51 positioning references not already in the list are folded into the numbered References (45–95) and every author–year key in Section 1.1 is replaced by its number (46 citations); positioning_refs.md stays as the verification record |
| R2-r2-2 | 2 | applied: reopened-gate qualification moved forward |
| R3-r2-2 | 3 | applied: identifier proxy label named in data availability |
| R3-r2-3 | 3 | applied: release package list extended |

### V5 intake (2026-09-06)

Section 5.9 gains the V5 paragraph (study of record for the lifetime residual on the corrected runtime); Section 6 gains the V5 reference-arm sentence; Section 9's revalidation paragraph now names V5 as the corrected runtime's terminal. Claims rows 258–267 read the V5 evaluation, receipt, replication receipt, manifest and reference-arm file.

### Round 3 (2026-09-06)

| Item | Reviewer | Disposition |
|---|---|---|
| R1-r3-1 / R2-r3-2 | 1, 2 | applied: V5 described as the pre-registered study beside the acceptance label; 'study of record' dropped |
| R1-r3-2 | 1 | applied: attribution declared-not-ablated in 5.9 and limitations; OCM−Δ arm named as next study |
| R2-r3-1 | 2 | applied: 'closes the programme's gap list (first version)' |
| R3-r3-1 | 3 | applied: current engineering pointer and frozen V4 successors named in data availability |
| R3-r3-2 | 3 | applied: superseded-fields note in claims_map.md |
| R3-r3-3 | 3 | open: persistent identifier (pre-submission action) |

