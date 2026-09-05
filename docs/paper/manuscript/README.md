# OCM manuscript, draft V1 (2026-09-05)

Status: first complete draft of the machine-epistemics / ORION Cognitive Machine manuscript, written from the receipt-bound files in this worktree and the ORION-V2 theory batches. Not submission-ready. Nothing in this directory carries claim authority; the receipts do.

skills-applied: nature-writing (core stance, workflow steps 1–8, methods and algorithmic paper-type playbooks, section fragments for title, abstract, intro, related-work, method, experiments, discussion, conclusion; journal generic; language en), nature-polishing (default stance, failure-mode order, terminology ledger, no em dashes), nature-citation (core principles and workflow applied as a manual pass: numbered references limited to works named in repository documents, every unverified bibliographic detail marked [VERIFY], nothing invented), nature-data (Data and code availability drafted from the custody manifests and receipts; no DOI or accession invented), nature-figure (figure contract per figure in figures.md; backend not chosen, no plot executed), nature-experiment-log (NOT APPLIED: the skill is a Chinese-language lab-notebook logger for Feishu/Obsidian and does not apply to this manuscript; recorded here so the omission is explicit). The `_shared/` core files (reader workflow, paper-type taxonomy, ethics, terminology ledger) were loaded. Protocol: papers/PAPER_WRITING_SKILLS_PROTOCOL_V1.md (house-style rules §7 applied except rule 1, which governs the ORION-11…24 series and not this whole-programme paper).

## Files

| File | Content |
|---|---|
| main.md | the manuscript (title, abstract, ten sections, methods summary, availability, 45 references) |
| claims_map.md | 203 rows: every numeric or terminal-bearing sentence of main.md with its source file and field |
| figures.md | eight main figures and two supplementary figures, each with data file, exact fields and a plotting recipe |
| README.md | this file |

## Counts

| Quantity | Value |
|---|---|
| main.md words, prose only (excluding tables and references) | 9,101 |
| main.md words excluding references (tables included) | 10,823 |
| main.md words total | 11,938 |
| claims_map.md rows | 203 |
| references | 45 (23 marked [VERIFY]) |
| figures planned | 8 main + 2 supplementary |

The plan's target was 6,000–9,000 words excluding references; the prose is 101 words over that band. Candidate trims for the next pass are listed below.

## One-sentence argument (nature-writing step 1)

In machine reasoning, we show that one persistent instance with an explicit, revisable evidence state carries language, work, science, transfer, revision and governed self-repair through a lifetime, using a KnowledgeSpace whose semantics are exact theorems with checkers, supported by pre-registered matched comparisons against the strongest parent buildable here (a lifetime-level residual on ten families and ties on six), with the boundary that frontier parents, human rating and external benchmarks remain undetermined.

## Terminology ledger (locked for this draft)

| Canonical term | First use | Variants avoided |
|---|---|---|
| KnowledgeSpace | §2 | KSO, knowledge space |
| warrant interval ⟦L, U⟧ | §2.1 | profile, label |
| LIVE / DEAD / UNKNOWN | §2.1 | live/dead lower-case in prose is descriptive only |
| ⊗ (conjunction), ⊕ (alternative) | §2.1 | meet/join used only for authority |
| authority meet | §2.2 | — |
| reopening report (REOPEN / RECHECK / UNAFFECTED) | §2.3 | impact set |
| matched parent; whole-system parent; template floor | §4 | baseline, comparator (comparator used only generically) |
| reference arm (REFERENCE) | §6 | never "comparator" |
| lifetime; family; terminal; residual | §4–§5 | run, metric, verdict (verdict used only for the test outcome) |
| undetermined (prose) = CANNOT_CHECK (tables) | §4 | — |
| parent-sufficient (prose) = PARENT_SUFFICIENT (tables) | §5 | — |
| DEV_CALIBRATION / PROTECTED | §4 | pilot, final |
| self-application ledger; row Sn | §7 | — |
| theory batch n; item Tn/Bn/Cn/Dn/En/Fn/Gn; obligation KS-Tnn | §8 | — |
| ORION Cognitive Machine (OCM) | §2.7 | the machine (in prose) |

## Pending

1. **V4 paired-lifetime study (PR #34).** Absent from this worktree: no docs/provenance/M12_PAIRED_RECEIPT_V4.json and no research/ocm-m12/M12_PAIRED_LIFETIMES_EVAL_V4.json on 2026-09-05. Every V4 number in main.md is written as pending (Sections 5.10, 9, 10). When the receipt lands: add a V4 table after Table 7 (rule, family count, collapsed-one-coin report, balanced out-of-scope suite), update the abstract's V3 sentence if the decision changes, and add rows to claims_map.md.
2. **Theory batch 7 merge.** Batch 7 is on the ORION-V2 branch kso/theory-batch-7 and not on origin/main at drafting time; Table 9 says so. Update the row when merged and add the PR number.
3. **academic-paper-pipeline gate.** Not run. Required before "submission-ready": archetype and venue contract, atomic claim verification (claims_map.md is the input), reference verification (23 [VERIFY] entries), statistics audit (exact tests, n, δ, α as pre-registered; the G8 caveats), reviewer simulation, editor synthesis, revision loop, release-integrity binding (paper SHA256SUMS to the receipt chain).
4. **Claim-verification script.** Plan gate 3 asks for a script that traces every numeric statement to a receipt; claims_map.md is the hand-built table it should be checked against; tools/paper/ does not exist yet.
5. **Figure scripts.** figures.md gives data files, fields and recipes; no script and no plot exist. Backend (Python or R) is the operator's choice under the nature-figure gate.
6. **Reference [1] and [45].** No repository document names a specific foundation-model paper or a Qwen2.5 model report; both entries must be chosen and verified, or the sentences rewritten to cite nothing.
7. **Word count.** 101 prose words over the plan's upper bound. Candidate trims: §3.2 object inventories (about 120 words), §5.7 second and third sentences (about 60 words), §8 final sentence (about 50 words).

## Numbers that no file contains (marked in main.md)

| Place | Statement | Marking |
|---|---|---|
| Table 2, E4 curricula | held-out exact per curriculum | [NOT MEASURED] (the M5 receipt has no held_out field under E4) |
| Table 8, last row | parent "answered where unknown was licensed" in V3 | [NOT MEASURED in V3 file] (the paired receipt has no always_attempts block) |
| Abstract, "10^5 atoms" | scale of the M8 organisation study | the number comes from the paper plan (C5), not from the M8 receipt or report; flagged [VERIFY] in claims_map.md row 8 |
| claims_map row 95 | frozen-system held-out baseline 0 of 97 | the receipt records held-out 0/97 under E2 and E3, not under a separate frozen field; wording flagged [VERIFY] |
| §8 | the paper plan's "48 theorems/obligations" and "11 theory-reported defects" | not used; the draft counts 63 batch items (T1–T11, B1–B8, C1–C8, D1–D8, E1–E8, R1–R3, F1–F8, G1–G9) plus the 6 obligations of the warrant note, and 16 ledger-counted defects over batches 1–6 (the plan's 11 are the batch 5 and 6 intakes only); the discrepancy with the plan is recorded here for the plan's author |

## Checklist against the paper plan §4 gates

| Gate | Status |
|---|---|
| 1. Batch 7 merged and its OCM obligations applied | NOT MET (batch 7 unmerged; obligations G1, G4, G8 named in §8 as V4 work) |
| 2. All receipts verify on main; replication receipts MATCH; CI green | NOT CHECKED in this draft (no test or verification was run; replication receipts read MATCH in the files) |
| 3. Manuscript drafted with the nature-* skills; every numeric statement traced by a claim-verification script; reference list verified | PARTIAL: drafted with the skills (this file); claims traced by hand in claims_map.md (203 rows); no script; 23 references unverified |
| 4. Full academic-paper-pipeline | NOT RUN |
| 5. Human gates closed with the strongest proxy and labelled | NOT DONE (no reviewer simulation, no rating proxy; the human-rating protocol is reported as not run) |

## Claim-to-receipt coverage (plan §2)

| Plan claim | Where in main.md | Receipt |
|---|---|---|
| C1 KnowledgeSpace executable and replay-exact; M2.1 parent-sufficient at the discordant scale | §2, §5.1 | M1, M2 receipts; M7 report §8 |
| C2 bounded-world language, dialogue, acquisition | §5.2 | M3–M5 receipts |
| C3 conversational alpha 42/42, 0 incidents | §5.3 | M6 receipt |
| C4 M7 residual 53/54 vs 33/54, n = 54 | §5.4, Table 3 | M7 receipt |
| C5 organisation parent-sufficient | §5.5 | M8 receipt |
| C6 transfer 7 vs 12; matrix 14/14; n = 9 undetermined | §5.6, Table 4 | M9 receipt |
| C7 science lifecycle mixed | §5.7 | M10 receipt |
| C8 self-reorganisation 7/7 vs 2/7, 1/7 | §5.8, Table 5 | M11 receipt |
| C9 V2 full residual in scope, one inferential family | §5.9, Table 6 | M12 receipt, replication receipt |
| C10 V3 ten families 8/8 at p = 0.0078, six ties, replicated | §5.10, Table 7 | M12 paired receipt, paired replication receipt |
| C11 reference arm 0/20 honest unknown, lessons matched (V2) / uneven (V3) | §6, Table 8 | M12 reference receipt; V3 reference-arm JSON |
| C12 36 ledger rows; theory batches; defects fixed | §7, §8 | ledger; intake.py |
| T1 theory batches 1–7 with exact checkers | §8, Table 9 | ORION-V2 batch files |
| Not claimable (frontier parent, human usefulness, external benchmarks, natural-language generality, novelty) | §1 last paragraph, §9 | — |
