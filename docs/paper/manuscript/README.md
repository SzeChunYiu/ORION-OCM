# OCM manuscript, draft V1 (2026-09-05, updated for M12 V4)

Status: first complete draft of the machine-epistemics / ORION Cognitive Machine manuscript, written from the receipt-bound files in this worktree, the ORION-V2 theory batches, and the M12 V4 files read from ORION-OCM origin/main (commit 8e3df44, merge of pull request #34) with `git show origin/main:<path>`. The worktree branch `paper/ocm-manuscript` was not rebased onto main, so the V4 files are not in this checkout; every V4 citation names its path on main. Not submission-ready. Nothing in this directory carries claim authority; the receipts do.

skills-applied: nature-writing (core stance, workflow steps 1–8, methods and algorithmic paper-type playbooks, section fragments for title, abstract, intro, related-work, method, experiments, discussion, conclusion; journal generic; language en), nature-polishing (default stance, failure-mode order, terminology ledger, no em dashes), nature-citation (core principles and workflow applied as a manual pass: numbered references limited to works named in repository documents, every unverified bibliographic detail marked [VERIFY], nothing invented), nature-data (Data and code availability drafted from the custody manifests and receipts; no DOI or accession invented), nature-figure (figure contract per figure in figures.md; backend not chosen, no plot executed), nature-experiment-log (NOT APPLIED: the skill is a Chinese-language lab-notebook logger for Feishu/Obsidian and does not apply to this manuscript; recorded so the omission is explicit). The `_shared/` core files (reader workflow, paper-type taxonomy, ethics, terminology ledger) were loaded. Protocol: papers/PAPER_WRITING_SKILLS_PROTOCOL_V1.md (house-style rules §7 applied except rule 1, which governs the ORION-11…24 series and not this whole-programme paper).

## Files

| File | Content |
|---|---|
| main.md | the manuscript (title, abstract, ten sections, methods summary, availability, 45 references) |
| claims_map.md | 217 rows: every numeric or terminal-bearing sentence of main.md with its source file and field |
| figures.md | eight main figures and two supplementary figures, each with data file, exact fields and a plotting recipe |
| README.md | this file |

## Counts

| Quantity | Value |
|---|---|
| main.md words, prose only (excluding tables and references) | 9,704 |
| main.md words excluding references (tables included) | 11,756 |
| main.md words total | 12,871 |
| claims_map.md rows | 217 |
| references | 45 (23 marked [VERIFY]) |
| figures planned | 8 main + 2 supplementary |

The plan's target was 6,000–9,000 words excluding references. The prose is 704 words over that band after the V4 section (5.11, about 500 words) was added. Candidate trims for the next pass: §2.2–2.6 could lose about 250 words of parent attribution that the registry already carries; §5.5 and §5.7 could each lose about 100 words of secondary numbers by pointing to the receipts; §6 could lose the V3 grading discussion (about 120 words) now that V4 carries the four-class result.

## One-sentence argument (nature-writing step 1)

In machine reasoning, we show that one persistent instance with an explicit, revisable evidence state carries language, work, science, transfer, revision and governed self-repair through a lifetime, using a KnowledgeSpace whose semantics are exact theorems with checkers, supported by pre-registered matched comparisons against the strongest parent buildable here (a lifetime-level residual on the pre-registered primary family, six secondary rejections flagged as one coin, and ties where the parent suffices), with the boundary that frontier parents, human rating and external benchmarks remain undetermined.

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
| primary family; secondary family; collapsed one coin | §4, §5.11 | — |
| undetermined (prose) = CANNOT_CHECK (tables) | §4 | — |
| parent-sufficient (prose) = PARENT_SUFFICIENT (tables) | §5 | — |
| DEV_CALIBRATION / PROTECTED | §4 | pilot, final |
| self-application ledger; row Sn | §7 | — |
| theory batch n; item Tn/Bn/Cn/Dn/En/Fn/Gn; obligation KS-Tnn | §8 | — |
| ORION Cognitive Machine (OCM) | §2.7 | the machine (in prose) |

## What changed in the V4 update

- Abstract: the lifetime sentence now states the V4 primary-family result (8 of 8, one-sided p = 0.0039), the six collapsed secondaries and the ties, with V3 as the earlier frozen record; the reference sentence now uses the V4 four-class numbers.
- Table 1: V4 row added.
- §3.3 and §4: V4 design and the S37 rule defect.
- §5.10: V3 kept as the frozen record with its S37 caveat; the "pending" paragraph replaced.
- §5.11 (new): V4 result, Table 8, collapse flags, self-repair and revision counts, the S38 label defect, replication (SHA-256 prefix 599ee69a), decision.
- §6: Table 9 gains V4 columns; the four-class grading paragraph added; V3 grading discussion kept as the motivation.
- §7: 38 ledger rows; S37 and S38 in the list of evaluation-changing rows.
- §8: KS-T116 and KS-T117; batch-7 obligations now split into discharged and remaining; Table 9 renumbered to Table 10.
- §9: the one-coin paragraph now reports the V4 collapse flags as a result and names the next design.
- §10: rewritten; nothing V4-related is pending.
- Data and code availability: V4 files listed.
- Registry counts: 123 rows (87 proved-class, 25 finite calibration, 3 parent-owned, 6 open, 2 undetermined).

## Pending

1. **Theory batch 7 merge.** Batch 7 is on the ORION-V2 branch kso/theory-batch-7 and not on origin/main at drafting time; Table 10 says so. Update the row when merged and add the PR number.
2. **academic-paper-pipeline gate.** Not run. Required before "submission-ready": archetype and venue contract, atomic claim verification (claims_map.md is the input), reference verification (23 [VERIFY] entries), statistics audit (exact tests, n, δ, α as pre-registered; the collapse flags; the Bonferroni reading of V3), reviewer simulation, editor synthesis, revision loop, release-integrity binding (paper SHA256SUMS to the receipt chain).
3. **Claim-verification script.** Plan gate 3 asks for a script that traces every numeric statement to a receipt; claims_map.md is the hand-built table it should be checked against; tools/paper/ does not exist yet.
4. **Figure scripts.** figures.md gives data files, fields and recipes; no script and no plot exist. Backend (Python or R) is the operator's choice under the nature-figure gate.
5. **References [1] and [45].** No repository document names a specific foundation-model paper or a Qwen2.5 model report; both entries must be chosen and verified, or the sentences rewritten to cite nothing.
6. **Word count.** 704 prose words over the plan's upper bound; trims listed above.
7. **Rebase.** The paper branch should be rebased onto main so that the V4 files are in the checkout before the claim-verification script runs.

## Numbers that no file contains, or that do not reconcile (marked in main.md or claims_map.md)

| Place | Statement | Marking |
|---|---|---|
| Table 2, E4 curricula | held-out exact per curriculum | [NOT MEASURED] (the M5 receipt has no held_out field under E4) |
| Table 9, last row | "answered where unknown was licensed" for the parent in V3, and for the machine and parent in V4 | [NOT MEASURED in V3 file] / [NOT MEASURED in V4 file] (the paired receipts have no always_attempts block) |
| Abstract, "10^5 atoms" | scale of the M8 organisation study | the number comes from the paper plan (C5), not from the M8 receipt or report; flagged [VERIFY] in claims_map row 8 |
| claims_map row 95 | frozen-system held-out baseline 0 of 97 | the receipt records held-out 0/97 under E2 and E3, not under a separate frozen field; wording flagged [VERIFY] |
| §6 four-class grading | 233 + 199 + 38 + 2 = 472, while the V4 report says "the 480 factual questions" | quoted as the report states; flagged [VERIFY] in claims_map row 177b for the generator's author |
| §8 | the paper plan's "48 theorems/obligations" and "11 theory-reported defects" | not used; the draft counts 63 batch items (T1–T11, B1–B8, C1–C8, D1–D8, E1–E8, R1–R3, F1–F8, G1–G9) plus the 6 obligations of the warrant note, and 16 ledger-counted defects over batches 1–6 (the plan's 11 are the batch 5 and 6 intakes only) plus S37 and S38 from batch 7; recorded here for the plan's author |

## Checklist against the paper plan §4 gates

| Gate | Status |
|---|---|
| 1. Batch 7 merged and its OCM obligations applied | PARTIAL (batch 7 unmerged in ORION-V2; its G5/G7/G8 obligations are applied on ORION-OCM main as KS-T116/KS-T117 and V4; G1 and G4 obligations named in §8 as remaining) |
| 2. All receipts verify on main; replication receipts MATCH; CI green | NOT CHECKED in this draft (no test or verification was run; replication receipts V1 and V4 read MATCH in the files) |
| 3. Manuscript drafted with the nature-* skills; every numeric statement traced by a claim-verification script; reference list verified | PARTIAL: drafted with the skills (this file); claims traced by hand in claims_map.md (217 rows); no script; 23 references unverified |
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
| C10 lifetime-level residual: V4 primary 8/8 at one-sided p = 0.0039, six secondaries collapsed, replication MATCH; V3 as the earlier frozen record (10 families 8/8, p = 0.0078, six ties) with the S37 caveat | §5.10, Table 7; §5.11, Table 8 | M12 paired receipts V1 and V4; paired replication receipts V1 and V4 |
| C11 reference arm: V2 0/20 honest unknown; V4 four-class 233/199/38/2, lessons 25/48 | §6, Table 9 | M12 reference receipt; V3 and V4 reference-arm JSON |
| C12 38 ledger rows; theory batches; defects fixed | §7, §8 | ledger; intake.py; registry rows KS-T116/117 |
| T1 theory batches 1–7 with exact checkers | §8, Table 10 | ORION-V2 batch files |
| Not claimable (frontier parent, human usefulness, external benchmarks, natural-language generality, novelty) | §1 last paragraph, §9 | — |
