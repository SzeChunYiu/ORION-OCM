# OCM manuscript, draft V3.1 (2026-09-05, after pipeline round 2)

Status: the machine-epistemics / ORION Cognitive Machine manuscript after the second pre-submission pipeline round. The branch is behind origin/main; a rebase precedes merge (Pending item 8). Milestone terminals cite the historical docs/provenance/M*_RECEIPT_V1.json receipts; the successor receipts under docs/provenance/runtime_revision_20260905_v4 are cited only as the current-runtime regression record. Written from the receipt-bound files in this worktree and from the ORION-OCM origin/main files that post-date the branch base (the 472-denominator V4 report, the M8 scale wording, the batch-6/7 intake records, the 2026-09-05 runtime revalidation documents), which the claim map reads with a `main:` prefix. Not submission-ready (see reviews/readiness_report.md). Nothing in this directory carries claim authority; the receipts do.

skills-applied: academic-paper-pipeline (full lifecycle: archetype and venue contract, evidence maturation, atomic claim verification, statistics audit, figure and table review, acceptance readiness, three blind reviewer simulations, editor synthesis, revision loop, rejection triage and retargeting notes, targeted re-review, readiness report), nature-writing (argument architecture, section fragments, restructure mode), nature-polishing (default stance, failure-mode order, terminology ledger, no em dashes, ten trim passes), nature-citation (every reference verified online: CrossRef DOI records, arXiv, bibliographic search; unnamed reference removed), nature-data (Data and code availability with repository host, licence and pending-archive statement), nature-figure (figure contracts in figures.md; no plot executed), nature-statistics (exact tests, units, α, δ, sidedness, family bounds, collapse flags audited in the readiness report), nature-reviewer (three reviewer reports plus editor synthesis), nature-experiment-log (NOT APPLIED: lab-notebook logger, not applicable). Protocol: papers/PAPER_WRITING_SKILLS_PROTOCOL_V1.md (house-style rules §7 applied except rule 1, which governs the ORION-11…24 series).

## Files

| File | Content |
|---|---|
| main.md | the manuscript (title, abstract, nine sections, methods summary, availability, 44 references) |
| claims_map.md | 246 rows in the checkable five-column format: verbatim phrase, source file(s), machine-checkable clauses |
| claims_verification.txt | output of tools/paper/verify_claims.py over claims_map.md (246 rows, 246 OK) |
| figures.md | eight main and two supplementary figure contracts bound to receipt fields; no plot executed |
| reviews/venue_contract.md | archetype, exact-tuple resolution, target ladder, gates |
| reviews/reviewer_1.md, reviewer_2.md, reviewer_3.md | blind reviewer reports (validity; contribution and positioning; reproducibility and clarity) |
| reviews/editor_synthesis.md | five-lens triage, concern classification, editor decision |
| reviews/revision_log.md | every change with its class, the targeted re-review, and what was not done |
| reviews/readiness_report.md | gate-by-gate status, statistics audit, remaining blockers, terminal state |
| README.md | this file |
| ../../../tools/paper/verify_claims.py | stdlib claim checker (`main:` and `V2:` sources, JSON paths, contains, count, regexcount, filecount) |
| ../../../tools/paper/prose_wordcount.py | word counts under the plan's accounting |

## Counts

| Quantity | Value |
|---|---|
| main.md body prose (outside tables, headings, captions, header note, references) | 8,726 |
| main.md prose with headings, table captions and the header note | 9,417 |
| main.md words excluding references (tables included) | 11,528 |
| main.md words total | 12,401 |
| claims_map.md rows | 246 (246 OK; 0 MISMATCH, 0 MISSING_FILE, 0 PHRASE_MISSING, 0 UNCHECKABLE) |
| references | 44 (all verified; 1 removed) |
| figures planned | 8 main + 2 supplementary (no plot executed) |
| tables | 10 |

The plan's bound is 6,000–9,000 words excluding references; body prose is inside it. The count with headings and captions is 417 words over because the round-2 captions define units, tests and verdict tokens; a short-form venue needs a separate 3,500-word main text (reviews/venue_contract.md).

## One-sentence argument

A persistent instance with an explicit, revisable evidence state was built along thirteen receipt-bound milestones and evaluated against the strongest matched parent buildable here; the pre-registered primary family rejected in 8 of 8 paired lifetimes (one-sided p = 0.0039, replicated), six secondary rejections are flagged as one coin, most other families are ties or parent-sufficient, a labelled reference model shows the unbound pretraining channel, and the self-repair and cross-domain transfer results are reported under a reopened adoption gate and unequal cell sets respectively; frontier parents, human rating and external benchmarks remain undetermined and no novelty claim is made.

## Terminology ledger (locked)

| Canonical term | First use | Variants avoided |
|---|---|---|
| KnowledgeSpace | §2 | KSO, knowledge space |
| warrant interval ⟦L, U⟧ | §2.1 | profile, label |
| LIVE / DEAD / UNKNOWN | §2.1 | lower-case only descriptively |
| ⊗ (conjunction), ⊕ (alternative) | §2.1 | meet/join used only for authority |
| reopening report (REOPEN / RECHECK / UNAFFECTED) | §2.3 | impact set |
| matched parent; whole-system parent; template floor | §4 | baseline, comparator (generic only) |
| reference arm (REFERENCE) | §6 | never "comparator" |
| lifetime; family; terminal; residual | §4–§5 | run, metric, verdict (verdict = test outcome only) |
| primary family; secondary family; collapsed one coin | §4, §5.11 | — |
| undetermined (prose) = CANNOT_CHECK (tables) | §4 | — |
| parent-sufficient (prose) = PARENT_SUFFICIENT (tables) | abstract (glossed), §5 | — |
| reopened (adoption cells after the 2026-09-05 revalidation) | §3, §5.8 | invalidated, retracted |
| self-application ledger; row Sn | §7 | — |
| theory batch n; item Tn…Gn; obligation KS-Tnn | §8 | — |
| ORION Cognitive Machine (OCM) | §2.7 | the machine (in prose) |

## What changed in round 2

- Claim verification made real: the inherited script checked 0 rows because the map was in the wrong format; the map was rewritten (246 rows) and the script extended; every row passes; the checker was validated on planted defects.
- Corrections from the repository state: 472-question four-class denominator; M8 parent-sufficient at the evaluated scale (10⁵ atoms is the M2 scaling row); batch 7 merged (ORION-V2 pull request 349); V4 parent range 0.593–0.611; intake record at 15 intakes and 2 exports; the 55/52-facts template-floor correction; Table 9's V2 columns relabelled as the fresh M7 arms.
- New boundaries from the 2026-09-05 runtime revalidation on origin/main: M11 adoption cells and M12 phase G reopened; the transfer comparison undetermined on unequal cell sets; interval-persistence, dialogue-promotion and coverage-certificate defects fixed after the freeze; the manuscript reports all of it in §3, §5.8, §5.9, §5.11 and §9, and the abstract carries one sentence.
- Reference [1] (foundation-models survey) removed as unnamed by any repository document; the other 44 verified online; Biba and Kemeny–Snell entries corrected to their editions.
- Prose trimmed from 9,662 to 8,522 body words before the reviewer round and 8,726 after the round-2b repairs.
- Reviewer round: 17 concerns; 10 closed, 1 narrowed, the rest open with named owners and resolution tests (reviews/editor_synthesis.md, reviews/revision_log.md).

## Pending (honest list)

1. Protected re-evaluation of the self-repair cells under the corrected adoption gate (author evidence).
2. Prospectively matched cross-domain transfer cells (author evidence).
3. Positioning paragraph against contemporary systems with verified citations (literature pass).
4. Archived release with a persistent identifier; licence statement for the authored datasets.
5. Venue decision and, for a short-form venue, the 3,500-word main-text form.
6. Release-integrity binding (SHA256SUMS of the package bound to the receipt chain).
7. Figure scripts and plots (backend is the operator's choice).
8. A rebase of the paper branch onto origin/main precedes merge (the lead performs it): the `main:` sources of claims_map.md must be in the checkout and verify_claims.py re-run there; remove the header note at submission.

## Checklist against the paper plan §4 gates

| Gate | Status |
|---|---|
| 1. Batch 7 merged and its OCM obligations applied | DONE (ORION-V2 #349 merged; KS-T116/KS-T117 on main; G1 and G4 obligations named in §8 as remaining) |
| 2. All receipts verify on main; replication receipts MATCH; CI green | NOT CHECKED here (no test or verification run on this Mac; the three replication receipts read MATCH; origin/main reports its own receipt verification in docs/PROGRAMME_STATUS_RUNTIME_V4.md) |
| 3. Manuscript drafted with the nature-* skills; every numeric statement traced by a claim-verification script; reference list verified | DONE (246 rows OK; 44 references verified) |
| 4. Full academic-paper-pipeline | RUN (all stages; release-integrity binding not done; terminal state current_claims_partly_established) |
| 5. Human gates closed with the strongest proxy and labelled | DONE for review (model-proxy reviewer and editor reports, labelled); the human-rating protocol remains not run and is reported as such |
