# Editor synthesis (pipeline round 2, 2026-09-05)

Inputs: manuscript draft V3, the three frozen reviewer reports (reviews/reviewer_1.md, reviewer_2.md, reviewer_3.md), the claim verification run (claims_verification.txt: 241 rows, 241 OK), the venue contract (reviews/venue_contract.md) and the repository's current programme status on origin/main. Arguments are weighed, not votes counted.

## Editorial triage (five lenses, frozen before synthesis)

| Lens | Assessment |
|---|---|
| scope / article type | methods-and-evaluation paper; long-form as drafted (8,522 body-prose words, 10 tables); a 3,500-word Article form does not yet exist; scope fit is venue-dependent (see venue contract) |
| contribution / positioning | recoverable: a matched-comparison discipline with hash-bound pre-registration and one replicated lifetime-level residual on one family; positioning against the mathematical parents is complete, positioning against contemporary systems is absent (R2-1) |
| evidence maturity | L2 (protected synthetic holdout inside one authored world); replication on a second host; self-repair families reopened after the freeze by a runtime defect in the adoption gate; cross-domain transfer family has unequal cell sets |
| readership / objective | cross-domain AI engineers and researchers who evaluate systems; the paper's honesty is its readership value; a selective broad-interest venue's novelty gate is a target-objective mismatch, not a manuscript defect |
| routing clarity | clear: knowledge representation, provenance and revocation semantics, evaluation methodology, exact finite statistics, governed self-modification; reviewers need expertise in truth maintenance, exact tests and pre-registered evaluation |

Triage state: **repair_before_review** for a selective venue (target form does not exist); **send_to_review** for a long-form venue after the must-address repairs below.

## Concern classification

| ID | Origin | Class | Decision | Closure route | Status after revision |
|---|---|---|---|---|---|
| R1-1 two-value structure of primary differences | reviewer 1 | claim recalibration | must address | clarify (state the two values and the two parent scores in 5.11) | closed in V3.1 |
| R1-2 self-repair counts in results voice under a reopened gate | reviewer 1 | technical blocker for the self-repair claims | must address | narrow (every self-repair result reads as a frozen receipt value under a reopened gate) plus author evidence (protected re-run) | narrowed in V3.1; protected re-run remains blocked_on_author_evidence |
| R1-3 Table 8 E row more favourable than the text | reviewer 1 | reporting | must address | correct the verdict cell | closed in V3.1 |
| R1-4 two graders disagree on 4 items | reviewer 1 | reporting / measurement validity | must address | state grader per surface; V5 grader choice is a design decision for the authors | reporting closed in V3.1; grader choice open (design) |
| R1-5 block-dependence size of the n = 54 test | reviewer 1 | statistics reporting | must address | add the exact size (65/256 at block 6) from batch 6 | closed in V3.1 |
| R1-6 "inconclusive" vs "CANNOT_CHECK (n < 40)" | reviewer 1 | clarity | must address | define once in the Table 3 caption | closed in V3.1 |
| R1 minor (ci_90 shape, rounding rule, pretraining attribution wording, checker names) | reviewer 1 | surface / reporting | address | caption and Methods edits | closed in V3.1 |
| R2-1 nearest contemporary systems not named | reviewer 2 | publication-criteria concern (fair positioning) | must address before a selective venue; partially addressable now | literature research with verified citations is required; this round's web access was limited to bibliographic verification of existing references, so no new references were added; the manuscript now states the boundary (parent-subtraction tables carry per-mechanism comparison; learned agents enter only via the reference arm) | open: needs a literature pass with verified sources |
| R2-2 contribution statement | reviewer 2 | claim recalibration | must address | abstract's closing sentences restated | closed in V3.1 |
| R2-3 venue mismatch as drafted | reviewer 2 | target fit | must address as a decision | venue contract ladder; readiness report names the form per rung | decision recorded, not a manuscript edit |
| R2-4 significance boundary in one place | reviewer 2 | claim recalibration | must address | one sentence in Section 1 | closed in V3.1 |
| R2-5 theory loop as result or companion | reviewer 2 | optional enrichment / target decision | non-essential for the long-form route; a companion paper is the alternative | recorded in venue contract |
| R3-1 internal identifiers in prose | reviewer 3 | clarity | address partially; ids are the objects in Sections 2 and 8 | first-use glosses added; full replacement deferred to the venue-specific rewrite | partially closed |
| R3-2 abstract glosses | reviewer 3 | clarity (standalone surface) | must address | glosses for parent-sufficient and one coin | closed in V3.1 |
| R3-3 table captions without unit and test | reviewer 3 | reporting | must address | captions of Tables 3, 6, 7, 8 | closed in V3.1 |
| R3-4 results register (question first, meaning last) | reviewer 3 | clarity | address in the venue-specific rewrite; the word bound constrains it now | deferred |
| R3-5 revalidation told in five places | reviewer 3 | clarity | address | Section 9 carries the full paragraph; other mentions are one clause each | closed (already the V3 structure; verified) |
| R3-6 no persistent identifier, licence, archive | reviewer 3 | compliance | must address before submission | repository host and licence named; archive pending stated | partially closed; archived release is a pre-submission action |
| R3 minor (header note, token glosses in Table 1, separators, rounding, 240 − 237) | reviewer 3 | surface | address | 240 − 237 spelled out; rounding rule in Methods; header note stays while the file is a draft and is listed for removal at submission | partially closed |

## Editor decision

The central inferential case (the primary-family lifetime residual) is established at its stated scope and correctly bounded. Two results are not established as written and are now reported as such: the self-repair families (reopened gate) and the cross-domain transfer family (unequal cell sets). No manuscript edit can close either; the first needs a protected re-evaluation under the corrected gate, the second needs prospectively matched cells.

Publication-criteria blockers remaining: (1) positioning against contemporary systems with verified citations (R2-1); (2) an archived release with a persistent identifier (R3-6); (3) a venue-specific manuscript form for any short-form target (R2-3). Technical blockers remaining: the protected re-evaluation of the self-repair cells (R1-2) and matched transfer cells (R1-3), both `blocked_on_author_evidence`.

Terminal state for this round: **current_claims_partly_established, decision-ready for a long-form venue after R2-1 and R3-6 are closed; not submission-ready**. Uncontrollable editorial context (overlapping submissions, reviewer availability, editorial disagreement on interest) is not assessed and is outside this synthesis.

## Moving-goalpost note

Every concern above was raised in round 1 of this pipeline pass; none is a late addition. A future round may open a new blocking concern only for one of the five listed reasons (new evidence, regression, previously unassessable material, expertise gap, incompletely scoped original concern).
