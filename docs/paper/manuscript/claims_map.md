# Claims map for main.md (draft V1, 2026-09-05)

Every sentence of main.md that contains a number or a terminal is listed with the receipt-bound file and field it is copied from. Paths are relative to the ORION-OCM repository root unless prefixed `V2:` (ORION-V2 `research/machine-epistemics-theory/`). Rows are grouped by section; the sentence is identified by a key phrase. Table rows are mapped once per table with the field path of the whole block. "derived" marks an arithmetic combination of listed fields (the arithmetic is shown). Rows whose source is absent are marked NOT MEASURED or pending.

## Front matter

| # | Sentence (key phrase) | Source file | Field |
|---|---|---|---|
| 1 | "Draft V1 (2026-09-05)" | — | draft date, not a claim |
| 2 | "V4 paired-lifetime files were read from the repository's main branch (merge of pull request #34)" | ORION-OCM origin/main at commit 8e3df44 (2026-09-05): docs/provenance/M12_PAIRED_RECEIPT_V4.json, M12_PAIRED_REPLICATION_RECEIPT_V4.json, research/ocm-m12/M12_PAIRED_LIFETIMES_EVAL_V4.json, M12_V4_REFERENCE_ARM_V1.json, M12_LIFETIME_PREREGISTRATION_V4.md, docs/M12_V4_PAIRED_LIFETIMES_REPORT.md | read with `git show origin/main:<path>`; the paper worktree branch was not rebased |

## Abstract

| # | Sentence (key phrase) | Source file | Field |
|---|---|---|---|
| 3 | "roadmap of thirteen milestones" | docs/OCM_PROGRAMME_TERMINALS_V1.md | table rows M0–M12 (13 rows) |
| 4 | "134 of 134 protected utterances interpreted exactly" | docs/provenance/M3_RECEIPT_V1.json | deterministic_results.microworld_eval.protected.exact_meaning = 134, n = 134 |
| 5 | "42 of 42 scripted steps, 0 integrity incidents" | docs/provenance/M6_RECEIPT_V1.json | scenario_eval.steps_total = 42, steps_expected = 42; incidents.* = 0 |
| 6 | "primary family, conversations, in 8 of 8 lifetimes (one-sided exact sign test, p = 0.0039), with six pre-registered secondary families also at 8 of 8 but flagged as one coin … ties" | docs/provenance/M12_PAIRED_RECEIPT_V4.json | v4.tests.A_conversations.{role = primary, positive = 8, p_one_sided = 0.00391, collapsed_one_coin = false}; v4.secondary_rejections (6 families, each positive = 8, collapsed_one_coin = true); v4.tests B_enterprise, C_software, D_selection, D_analysis, D_proof, unknown_no_action n_nonzero = 0 |
| 6b | "an earlier frozen study under a weaker rule had found ten families at 8 of 8 and six ties" | docs/provenance/M12_PAIRED_RECEIPT_V1.json | v3.tests.*.verdict: OCM_RESIDUAL (10), TIES_ONLY (6) |
| 7 | "replicated byte-identically on a second host" | docs/provenance/M12_PAIRED_REPLICATION_RECEIPT_V4.json | verdict = MATCH; deterministic_block_sha256.principal = replica = 599ee69a… |
| 8 | "learned organisation at 10^5 atoms" (parent sufficient) | docs/provenance/M8_RECEIPT_V1.json; docs/paper/OCM_PAPER_PLAN_V1.md | terminal = M8_PARENT_SUFFICIENT_AT_THIS_SCALE; plan C5 "10^5 atoms" [VERIFY: the receipt does not state the atom count; the plan does] |
| 9 | "work success without revision" ties | docs/provenance/M12_PAIRED_RECEIPT_V1.json | v3.tests.B_enterprise, C_software verdict TIES_ONLY |
| 10 | "7 of 240 licensed unknowns; 199 of its answers true in the world" | research/ocm-m12/M12_V4_REFERENCE_ARM_V1.json; docs/M12_V4_PAIRED_LIFETIMES_REPORT.md §4 | lifetimes[*].summary.honest_unknown: 0+2+0+0+0+3+2+0 = 7 of 240 (derived); four_class.unlicensed_true: 22+26+27+27+29+21+26+21 = 199 (derived; report §4 states 199) |
| 11 | "25 of 48 acquired" | research/ocm-m12/M12_V4_REFERENCE_ARM_V1.json | lifetimes[*].post_deployment.acquired: 1+3+0+5+3+5+4+4 = 25 of 48 (derived; report §4 "25/48") |
| 12 | "remain undetermined … no novelty, consciousness or human-equivalence claim" | docs/OCM_PROGRAMME_TERMINALS_V1.md | "Reading the terminals" bullets 3–4 |

## 1. Introduction

| # | Sentence (key phrase) | Source file | Field |
|---|---|---|---|
| 13 | "Foundation models supply the first property at scale [1]" | — | reference [1] marked [VERIFY]; no repository number |
| 14 | "working thesis … methods of doing … external constitution [2]" | docs/self-application/OCM_SELF_APPLICATION_LEDGER_V1.md (directive); V2:ME_THEORY_GAP_ATLAS_V1.md | header paragraph; "Thesis honoured" paragraph |
| 15 | "parents … [3]–[15]" | docs/parent-subtraction/KSO_CORE_PARENTS_V1.md; docs/spec/KSO_WARRANT_V1.md §8 | parent rows |
| 16 | "seven batches of exact theorems" | V2: batch files 1–7 | file list |
| 17 | "no such matched parent can be built … reference arm is labelled as unbound" | docs/provenance/M12_REFERENCE_RECEIPT_V1.json | information_binding = "UNBOUND_PRETRAINING (F8)" |
| 18 | "general-novelty terminal of every receipt reads not established" | docs/provenance/M1_RECEIPT_V1.json, M2_RECEIPT_V1.json, M0_RECEIPT_V1.json | authority.GENERAL_NOVELTY / general_novelty = NOT_ESTABLISHED; later receipts: authority strings "no novelty claim" |

## 2. The KnowledgeSpace and its runtime

| # | Sentence (key phrase) | Source file | Field |
|---|---|---|---|
| 19 | "warrant interval ⟦L, U⟧ … L ≤ U" | docs/spec/KSO_WARRANT_V1.md §3 | definition |
| 20 | "LIVE … DEAD … UNKNOWN otherwise" | docs/spec/KSO_WARRANT_V1.md §3 | liveness definition |
| 21 | "exact homomorphism … (KS-T21) [16]" | docs/theorems/KSO_OBLIGATION_REGISTRY_V1.md row KS-T21; V2:KSO_THREE_VALUED_WARRANT_AND_REOPENING_V1.md §1 | status PROVED |
| 22 | "Certified intervals never read UNKNOWN … never flip" | docs/spec/KSO_WARRANT_V1.md §4 (a), (c) | KS-T21 (a), (c) |
| 23 | "single completeness bit does not compose … first row of the ledger" | docs/self-application/OCM_SELF_APPLICATION_LEDGER_V1.md row S1; V2 warrant note §1.3 | S1 witness |
| 24 | "Pawlak [8] … ATMS [3] … Kleene [6]" | docs/spec/KSO_WARRANT_V1.md §8 | parents table |
| 25 | "168 intervals … 225,792 homomorphism checks … two planted mutants" | docs/provenance/M1_RECEIPT_V1.json | result.checks.KS-T21.intervals = 168, homomorphism_checks = 225792; docs/spec/KSO_WARRANT_V1.md §6 mutants |
| 26 | "FEEDBACK-admitted atom … certified-zero … (KS-T18) [17]" | docs/theorems/KSO_OBLIGATION_REGISTRY_V1.md row KS-T18 | PROVED; parent Necula 1997 |
| 27 | "summary … Λ_corr ⊗ ⨂ Λ(x) … majority … mutant (KS-T23)" | docs/theorems/KSO_OBLIGATION_REGISTRY_V1.md row KS-T23 | statement and mutant |
| 28 | "warrant ⊗, authority meet and scope intersection (KS-T20)" | docs/spec/KSO_WARRANT_V1.md §5 | KS-T20 |
| 29 | "Biba [10] and Denning [9]" | docs/parent-subtraction/KSO_CORE_PARENTS_V1.md §C(b) | parents |
| 30 | "commit rank zero … only an external action receipt (batch 1, T1)" | V2:KSO_ONE_DAY_THEOREMS_BATCH1_V1.md §T1 | Theorem T1 (iii) |
| 31 | "ten speakers repeating p … same bottom (batch 2, B1)" | V2:KSO_LANGUAGE_PREREQUISITE_THEOREMS_BATCH2_V1.md §B1 | Theorem (i) |
| 32 | "supersession … revocation family indexed by time (batch 2, B5)" | V2: batch 2 §B5 | Theorem (iii) |
| 33 | "impact cone … least dependency-closed superset (KS-T09)" | docs/theorems/KSO_OBLIGATION_REGISTRY_V1.md row KS-T09 | statement |
| 34 | "REOPEN … RECHECK … UNAFFECTED (KS-T22); irrelevant revocation is a no-op" | docs/theorems/KSO_OBLIGATION_REGISTRY_V1.md row KS-T22; V2 warrant note §3 | Theorem KS-T22 |
| 35 | "ATMS label update [3, 4] … DRed … changed-derivability [18, 19]" | docs/parent-subtraction/KSO_CORE_PARENTS_V1.md §C(c) | parents |
| 36 | "Reinstatement restores exactly; relearning … lineage (batch 2, B6)" | V2: batch 2 §B6 | Theorem |
| 37 | "rollback is revocation plus quarantine (batch 1, T4)" | V2: batch 1 §T4 | Theorem T4 (ii), (iv) |
| 38 | "a = α s + (1 − α) Pᵀ a … frozen denominators … (KS-T04, T04b, T04c) [11]" | docs/theorems/KSO_OBLIGATION_REGISTRY_V1.md rows KS-T04/T04b/T04c/T05 | statements |
| 39 | "four-valued outcome … (KS-T19)" | docs/theorems/KSO_OBLIGATION_REGISTRY_V1.md row KS-T19 | statement |
| 40 | "Timeout alone is a gap … [20, 21] … [22]" | docs/parent-subtraction/KSO_CORE_PARENTS_V1.md §A row 3 | parents P1, P2 |
| 41 | "budget bracket … T2 of batch 1; runtime iterated from the wrong start vector" | V2: batch 1 §T2 limitation; ledger S10 | defect (b) |
| 42 | "learning channels … version space agrees … per-input antichain (B2, B3, C6) [14]" | V2: batch 2 §B2, §B3; batch 3 §C6 | theorems |
| 43 | "Per-channel acquisition bounds … tabulated [23, 24] … laundering detector" | V2:KSO_COMPARISON_PREREQUISITE_THEOREMS_BATCH4_V1.md §D2 | table and audit_measured |
| 44 | "self-model fibre … {self_model: 1} … (batch 5, E1)" | docs/M11_SELF_REORGANISATION_REPORT.md §1; V2:KSO_SELF_MODEL_PREREQUISITE_THEOREMS_BATCH5_V1.md §E1 | Theorem E1 |
| 45 | "stamped double-pushout rewrite … hash-exact … (E6) [25, 26]; metered … (T8; E7) [27]" | V2: batch 5 §E6, §E7; batch 1 §T8 | theorems |
| 46 | "Gödel-machine reading [28] … certificate produced outside the self-model" | V2: batch 1 §T7 | Theorem T7 (ii) consequence |
| 47 | "123 rows across twelve registries (87 … 25 … 3 … 6 … 2)" | docs/theorems/*.json (12 files; OCM_LIFETIME_OBLIGATION_REGISTRY_V1.json read from origin/main with KS-T116, KS-T117) | derived: row counts 30+9+7+6+8+9+9+7+9+9+13+7 = 123; status tallies summed over files (PROVED, PROVED (finite), PROVED (procedural), PROVED (propositional fragment), PROVED_WITH_CLAUSE = 87; FINITE_CALIBRATION 25; PARENT_OWNED variants 3; OPEN 6; CANNOT_CHECK 2) |
| 48 | "Twenty-three event families" | docs/provenance/M2_RECEIPT_V1.json | result.event_families (23 entries) |
| 49 | "eight controlled terminals replay … without any upgrade" | docs/provenance/M2_RECEIPT_V1.json | result.historical_replay.counts.PASS = 8; authority.note |

## 3. One persistent build (Table 1 and text)

| # | Sentence (key phrase) | Source file | Field |
|---|---|---|---|
| 50 | "thirteen milestones … receipt … chain … CI" | docs/OCM_PROGRAMME_TERMINALS_V1.md | header paragraph |
| 51 | Table 1 M0 row (158/158, 33/33, 269) | docs/provenance/M0_RECEIPT_V1.json | measurements.migrated_file_count, byte_identity_pass, runnable_reference_entrypoints, clean_clone_tests_pass; terminal |
| 52 | Table 1 M1 row (30; 25/2/2/1) | docs/provenance/M1_RECEIPT_V1.json | result.registry.summary.counts; docs/theorems/KSO_OBLIGATION_REGISTRY_V1.md status counts; terminal |
| 53 | Table 1 M2 row (23; 8/8; 47 vs 38 of 50) | docs/provenance/M2_RECEIPT_V1.json | event_families; historical_replay.counts.PASS; m2_1_revival.propagated = 47, uniform = 38, default_model_changed = false; terminal |
| 54 | Table 1 M3 row | docs/provenance/M3_RECEIPT_V1.json | protected.exact_meaning; terminal |
| 55 | Table 1 M4 row (251/251; 0/51) | docs/provenance/M4_RECEIPT_V1.json | dialogue_eval.acts.expected_act_and_committed; epistemic_integrity.assertion_to_belief_leakage; terminal |
| 56 | Table 1 M5 row (five regimes) | docs/provenance/M5_RECEIPT_V1.json | regimes E0–E4; terminal |
| 57 | Table 1 M6 row (42/42, 0 incidents) | docs/provenance/M6_RECEIPT_V1.json | scenario_eval; terminal |
| 58 | Table 1 M7 row (n = 54) | docs/provenance/M7_RECEIPT_V1.json | terminal_table.RQ1_conversations.matched_parent; terminal |
| 59 | Table 1 M8 row | docs/provenance/M8_RECEIPT_V1.json | terminal |
| 60 | Table 1 M9 row (14/14; n = 9) | docs/provenance/M9_RECEIPT_V1.json | transfer_matrix.expected_met = 14, n = 14; claims.*.n = 9; terminal |
| 61 | Table 1 M10 row | docs/provenance/M10_RECEIPT_V1.json | terminal |
| 62 | Table 1 M11 row (7/7 vs 2/7, 1/7) | docs/provenance/M11_RECEIPT_V1.json | summary.ocm_solves = 7, parent_parameter_search_solves = 2, parent_reflection_retry_solves = 1; terminal |
| 63 | Table 1 M12 V2 row | docs/provenance/M12_RECEIPT_V1.json | terminal; tiers.tier6_broad.inferential_residual_families |
| 64 | Table 1 M12 V3 row | docs/provenance/M12_PAIRED_RECEIPT_V1.json | terminal |
| 64b | Table 1 M12 V4 row (primary 8 of 8, one-sided p = 0.0039) | docs/provenance/M12_PAIRED_RECEIPT_V4.json | terminal; v4.tests.A_conversations |
| 72b | "version 4 re-registered the analysis with one primary family and ran on eight fresh streams" | research/ocm-m12/M12_LIFETIME_PREREGISTRATION_V4.md | Streams (seed OCM-M12-V4), Primary family |
| 65 | "canonical labelling for fragments of at most seven vertices … [29, 30]" | V2: batch 2 §B4; docs/provenance/M3_RECEIPT_V1.json | Theorem B4; wl_collision_witness |
| 66 | "ambiguity … collapse is an evidence event (batch 1, T6)" | V2: batch 1 §T6 | Theorem T6 (iv) |
| 67 | "clarification as an information action (C1) [31]; commitment gate (C2) [32]" | V2:KSO_DIALOGUE_PREREQUISITE_THEOREMS_BATCH3_V1.md §C1, §C2 | theorems |
| 68 | "55-fact bounded world (52 verified, 3 reported)" | docs/provenance/M6_RECEIPT_V1.json | knowledge.facts = 55, verified = 52 (3 derived = 55 − 52) |
| 69 | "eleven demonstration points" | docs/LANGUAGE_KSO_ALPHA_REPORT.md §1 | "eleven-point demonstration" |
| 70 | "Three self-contained environments … version 2 … stale binding fails" | docs/M9_TRANSFER_REPORT.md §2 | environments |
| 71 | "layers D0 to D8 … classes C0 to C6 … C6 recommendation only" | docs/M11_SELF_REORGANISATION_REPORT.md §1 | Diagnosis, Proposals rows |
| 72 | "Version 2 … three orderings; version 3 … eight paired lifetimes" | research/ocm-m12/M12_LIFETIME_PREREGISTRATION_V2.md §1; M12_LIFETIME_PREREGISTRATION_V3.md | Orderings; Lifetimes = 8 |

## 4. Matched-comparison methodology

| # | Sentence (key phrase) | Source file | Field |
|---|---|---|---|
| 73 | "retrieval memory over the same 55 facts … no gate" | research/ocm-m7/M7_PREREGISTRATION_V1.md §4 | MatchedParent.v1 |
| 74 | "skipped the withheld acceptance test … relabelled (S27)" | docs/self-application/OCM_SELF_APPLICATION_LEDGER_V1.md row S27; docs/provenance/M9_RECEIPT_V1.json | study_status |
| 75 | "M7 (three defects …), M9, M12 (identity split, pooled pseudo-replication, mislabelled fault)" | ledger rows S22–S24, S27, S31–S33; research/ocm-m12/M12_LIFETIME_PREREGISTRATION_V2.md §6 | rows |
| 76 | "δ = 0.05 … α = 0.05 … residual requires …" | research/ocm-m7/M7_PREREGISTRATION_V1.md §2 | equivalence margin paragraph |
| 77 | "minimum n … 40 items" | docs/provenance/M7_RECEIPT_V1.json | deterministic_results.min_n = 40 |
| 78 | "batch 4 (D1) … at least 76 discordant pairs [33, 34]" | V2: batch 4 §D1 | Theorem (iii) |
| 79 | "zero discordant pairs in 540 … margin 7/1000 (row S28)" | docs/M7_PROTECTED_COMPARISON_REPORT.md §8; ledger S28 | addendum |
| 80 | "p-value falls from 1/4 to 1/64 at three replicas [35, 36] … n = 54" | V2:KSO_LIFETIME_PREREQUISITE_THEOREMS_BATCH6_V1.md §F2 | Theorem (i), (ii) |
| 81 | "cannot reject below five pairs … power 0.81 at eight pairs … 0.9" | V2: batch 6 §F2 (iii); research/ocm-m12/M12_V3_PAIRED_LIFETIMES_DESIGN_V1.md | power table |
| 81b | "Batch 7 (G8) … no primary family, unbounded family count, two-sided unanimous test with power 0.43 … V4 re-registered: primary at α = 0.05, one-sided ≥ 7 of 8 (size 9/256), six secondaries at α/6 (reject only at 8 of 8), collapsed-one-coin flag, decision on the primary alone (S37)" | research/ocm-m12/M12_LIFETIME_PREREGISTRATION_V4.md; ledger row S37 (origin/main); V2: batch 7 §G8 | Frozen items table; S37 |
| 82 | "Kill gates …" list | research/ocm-m12/M12_LIFETIME_PREREGISTRATION_V2.md §4; V3 pre-registration "Kill gates" | list |
| 83 | "55 for every language arm … 0 … external input and output is 0" | docs/provenance/M7_RECEIPT_V1.json | information_budget.*.knowledge_facts = 55 (template 52), protected_exposure = 0; docs/M7_PROTECTED_COMPARISON_REPORT.md §4 external IO = 0 |
| 84 | "fresh Python 3.11 environment on a second host; byte-identical" | docs/M12_LIFETIME_REPORT.md §7; docs/provenance/M12_REPLICATION_RECEIPT_V1.json | note; verdict |

## 5.1 Core and runtime

| # | Sentence (key phrase) | Source file | Field |
|---|---|---|---|
| 85 | "25 of 30 … 2 … 2 … 1 open (KS-T12 … batch 7)" | docs/theorems/KSO_OBLIGATION_REGISTRY_V1.md status counts; V2:KSO_OPEN_LIST_CLOSURE_THEOREMS_BATCH7_V1.md §G5 | counts; G5 |
| 86 | "360 cases each of prune equality, reinstatement exactness, reopening partition, retraction monotonicity" | docs/provenance/M1_RECEIPT_V1.json | result.checks.J2.prune_equal, reinstate_exact, reopening_partition, retraction_monotone = 360 |
| 87 | "eight historical terminals … 38 of 50 … 32 of 50 … 34 of 50, n = 50" | docs/provenance/M2_RECEIPT_V1.json historical_replay; docs/provenance/INHERITED_TERMINAL_SUPERSESSION_V1.md row C12 and restated terminals | PASS = 8; M2_NAVIGATION_ONLY 38/50 vs RWR 32/50 (p = 0.31), CBR 34/50 (p = 0.52) |
| 88 | "38 to 47 of 50 … guards … default not changed … lever no-op (S7; D4)" | docs/provenance/M2_RECEIPT_V1.json | m2_1_revival.propagated = 47, uniform = 38, guards.* = true, default_model_changed = false; ledger S7; V2 batch 4 §D4 (ii) |
| 89 | "sparse … 10⁻¹⁴ … 10⁴ atoms in 0.66 s" | docs/self-application/OCM_SELF_APPLICATION_LEDGER_V1.md, backlog row "navigation scale" | "agrees with exact to 1e-14; 10⁴ atoms in 0.66 s" |

## 5.2 Language, dialogue, acquisition

| # | Sentence (key phrase) | Source file | Field |
|---|---|---|---|
| 90 | "240 utterances, 106 development, 134 protected, held-out absent" | docs/provenance/M3_RECEIPT_V1.json | microworld_custody.n, dev, protected, held_out_lexemes_absent_from_dev |
| 91 | "134 of 134 … F1 1.0 … negation 32, passive 28, transitive 31, adjective 26, yes/no 17" | docs/provenance/M3_RECEIPT_V1.json | microworld_eval.protected.exact_meaning, construction_identified, mean_role_f1, per_family.*.n |
| 92 | "one demonstration in a hypothesis class of six; ambiguity 3 … no false collapse; six paraphrase pairs; revoking … transitive reopened, passive intact" | docs/provenance/M3_RECEIPT_V1.json | acquisition.hypothesis_class_size = 6, transitive_demonstrations_required = 1; ambiguity.suite_n = 3, candidate_set_recall = 3, false_collapse = 0; paraphrase.pairs = 6, meaning_equivalent = 6; revocation_locality |
| 93 | "first receipt had read 0 of 26 … (row S13)" | docs/self-application/OCM_SELF_APPLICATION_LEDGER_V1.md row S13 | "transitive_adj 0/26" |
| 94 | "120 dialogues, 618 turns, 49 protected, 18 restarted; 251/251; 4/4/0; 9/9, 9/9, 20/20; 11/11; 7/7; 0/51; 7/7; 4/4; 5/5" | docs/provenance/M4_RECEIPT_V1.json | dialogue_custody.n, turns_total, protected; persistence.dialogues_restarted_midway; acts.expected_act_and_committed; clarification; correction; epistemic_integrity; state_reference |
| 95 | "three lexemes and the transitive construction removed … 22 of 134 … 0 of 97" | docs/provenance/M5_RECEIPT_V1.json | frozen_system.lexemes_removed (3), constructions_removed; baseline_frozen.exact = 22; regimes.E2_raw_corpus.held_out.exact = 0 (frozen held-out baseline is the E2/E3 held-out value 0; the receipt has no separate frozen held-out field) [VERIFY wording] |
| 96 | "six lessons, one demonstration … 134 of 134 and 97 of 97" | docs/provenance/M5_RECEIPT_V1.json | regimes.E0_explicit_lessons |
| 97 | "seven … three taught words … 115 of 134 and 78 of 97; participle reading" | docs/provenance/M5_RECEIPT_V1.json; ledger S17 | regimes.E1_aligned_demonstrations; S17 "participle reading of *found*" |
| 98 | "661 words … 88 form hypotheses … 0 consultable … semantic gain zero [15]" | docs/provenance/M5_RECEIPT_V1.json | regimes.E2_raw_corpus.information.words = 661, forms.form_hypotheses = 88, consultable = 0, semantic_gain_must_be_zero = 0 |
| 99 | "One grounded interaction reached 37 of 134" | docs/provenance/M5_RECEIPT_V1.json | regimes.E3_grounded_interaction.protected.exact = 37 |
| 100 | "four curricula … 134 and … 115" | docs/provenance/M5_RECEIPT_V1.json | regimes.E4_curricula.*.final |
| 101 | "new gain 93 of 112, 0 of 22 old loss, 0 of 22 unrelated" | docs/provenance/M5_RECEIPT_V1.json | retention_after_E1 |
| 102 | "subject-object-verb … unknown construction; forcing … not correct roles" | docs/provenance/M5_RECEIPT_V1.json | negative_transfer |
| 103 | Table 2 rows | docs/provenance/M5_RECEIPT_V1.json | regimes.*; E4 held-out NOT MEASURED (no held_out field under E4) |

## 5.3 Conversational alpha

| # | Sentence (key phrase) | Source file | Field |
|---|---|---|---|
| 104 | "42 expected steps of nine scenario families … restart consistent … four gates zero … 0 of 9" | docs/provenance/M6_RECEIPT_V1.json | scenario_eval.steps_expected/steps_total = 42; scenarios (9 keys, restart_consistent true); incidents.*; docs/LANGUAGE_KSO_ALPHA_REPORT.md §2 "0 / 9 scenarios" |
| 105 | "Three hostile families … passed" | docs/provenance/M6_RECEIPT_V1.json | scenario_eval.hostiles |
| 106 | "Mean latency 28 ms … maximum 77 ms … external IO 0" | docs/LANGUAGE_KSO_ALPHA_REPORT.md §2, §5; M6 receipt external_io = 0 | latency |
| 107 | "No human rating … frozen … randomisation seed" | docs/LANGUAGE_KSO_ALPHA_REPORT.md §4 | protocol |

## 5.4 Protected matched comparison (M7)

| # | Sentence (key phrase) | Source file | Field |
|---|---|---|---|
| 108 | "V1 … three defects (rows S22 to S24) … DEV_CALIBRATION" | docs/provenance/M7_RECEIPT_V1.json | study.v1_status; ledger S22–S24 |
| 109 | "twelve conversations (54 paired turns), six lessons, seven negative-transfer items, 30 in-scope, 20 out-of-scope, frozen" | docs/M7_PROTECTED_COMPARISON_REPORT.md §1; research/ocm-m7/M7_PREREGISTRATION_V1.md §8 | V2 description |
| 110 | Table 3 rows | docs/provenance/M7_RECEIPT_V1.json | terminal_table.RQ1_conversations.matched_parent (53/33, ci_90 [0.2673, 0.3704], difference 0.3704), .template (10, 0.7963); RQ1_factual; RQ3_*; RQ5_honest_unknown; RQ6_negative_transfer; laundering_audit.incidents = 0; docs/M7_PROTECTED_COMPARISON_REPORT.md §2 "3 probes" |
| 111 | "ablations without clarification (52 of 54) … without revocation (52 of 54) equivalent; last-turn memory (49 of 54) inconclusive" | docs/provenance/M7_RECEIPT_V1.json | terminal_table.RQ1_conversations.ocm-no_clarification, ocm-no_revocation (EQUIVALENT), ocm-last_turn_memory (INCONCLUSIVE) |
| 112 | "revoked-stops falls from 6 of 6 to 0 of 6" | docs/provenance/M7_RECEIPT_V1.json | summary.ocm-no_revocation.post_deployment.revoked_stops = "0/6" |
| 113 | "0 of 6,000 BLiMP pairs … 0 of 800 UD EWT … about 60 lexemes and 7 constructions; BabyLM, CHILDES not pinned; human rating not run; frontier external input disabled" | docs/provenance/M7_RECEIPT_V1.json external_families; docs/M7_PROTECTED_COMPARISON_REPORT.md §3 | BLiMP.covered = 0, pairs = 6000; UD_EWT.interpreted = 0, sentences = 800; "≈ 60 lexemes, 7 constructions" |
| 114 | "55 facts and 0 protected exposure for every arm" | docs/provenance/M7_RECEIPT_V1.json | information_budget (template 52 facts; all others 55) |

## 5.5 Learned organisation (M8)

| # | Sentence (key phrase) | Source file | Field |
|---|---|---|---|
| 115 | "six worlds (four regions of eight atoms, seven tasks) … language stream (167 atoms, 18 tasks) … six arms" | docs/M8_ORGANISATION_REPORT.md §1–§3 | arms; world description |
| 116 | "21.7 to 11.4 … 4 of 4 regions … 0 of 10 proposals" | docs/provenance/M8_RECEIPT_V1.json; report §2 | worlds.clean_hierarchy.R0_flat.navigation_work = 21.71, R2/R3/R4/R6 = 11.43, exact_regions = 4; report "0 adopted of 10" |
| 117 | "overlapping communities … 0 regions … fibres 1 of 4 … 32.0 to 18.3" | docs/provenance/M8_RECEIPT_V1.json | worlds.overlapping_communities.R2_communities.exact_regions = 0; R4_fibred.exact_regions = 1; R6_learned.navigation_work = 18.29 vs R0 32.0 |
| 118 | "misleading family … hand tree … cheapest (5.4)" | docs/provenance/M8_RECEIPT_V1.json | worlds.misleading_hierarchy.R1_hand_tree.navigation_work = 5.43, exact_regions = 0 |
| 119 | "Task success 1.0 … 0.86 after revoking" | docs/provenance/M8_RECEIPT_V1.json task_success = 1.0; docs/M8_ORGANISATION_REPORT.md §2 | "0.86 for every arm" (report only) |
| 120 | "all 36 cells: live macro over dead children never occurred" | docs/provenance/M8_RECEIPT_V1.json | worlds.*.*.macro_live_over_dead_children = 0 (6 worlds × 6 arms) |
| 121 | "flat closure 4.6 … 62 regions … 21 shared atoms … success 0.33" | docs/provenance/M8_RECEIPT_V1.json language_stream; report §3 | R0_flat.navigation_work = 4.56; R4_fibred.task_success = 0.333; report regions 62, overlaps 21 |
| 122 | "parent-sufficient at this scale; sheaf and continuous not runnable" | docs/provenance/M8_RECEIPT_V1.json | terminal; cannot_check_arms |

## 5.6 Work transfer (M9)

| # | Sentence (key phrase) | Source file | Field |
|---|---|---|---|
| 123 | "three orderings … six tasks … one demonstration … one withheld … 54 of 54 … 0 unauthorised" | docs/provenance/M9_RECEIPT_V1.json; docs/M9_TRANSFER_REPORT.md §3 | summary.*.success = "54/54", unauthorized_attempts = 0 |
| 124 | "cost 7 … cost 12 …" | docs/provenance/M9_RECEIPT_V1.json | summary.*.mean_later_domain_acquisition_cost |
| 125 | "unvalidated fresh start … cost 6 … not matched" | docs/provenance/M9_RECEIPT_V1.json | summary["fresh_start_unvalidated(not matched)"] = 6.0 |
| 126 | "Transfer precision 6 of 6 … 0 harmful … 0 false refusals" | docs/provenance/M9_RECEIPT_V1.json; report §3 | transfer_precision.attempted = 6, beneficial = 6; report "harmful transfers 0; false refusals 0" |
| 127 | "Paired success at n = 9 equivalent … undetermined" | docs/provenance/M9_RECEIPT_V1.json | claims.*.n = 9, verdict EQUIVALENT; terminal |
| 128 | "14 of 14 cells …" | docs/provenance/M9_RECEIPT_V1.json | transfer_matrix.cells, expected_met = 14 |
| 129 | "Five external agent benchmarks undetermined" | docs/provenance/M9_RECEIPT_V1.json | external_benchmarks (5 keys) |
| 130 | Table 4 rows | docs/provenance/M9_RECEIPT_V1.json | summary |

## 5.7 Scientific reasoning (M10)

| # | Sentence (key phrase) | Source file | Field |
|---|---|---|---|
| 131 | "within 0.25 … 10 of 10; ≥ 0.3 … (1.28 vs 0.5; 0.52 vs 0.0); collider −0.49 … 0; 0 claims without assumptions" | docs/provenance/M10_RECEIPT_V1.json | causal.identified_estimates_within_0.25 = "10/10"; naive_biased_on_confounded_worlds = "2/2"; worlds.confounded.naive.value = 1.278, oracle 0.5; no_effect_confounded.naive.value = 0.522, oracle 0.0; collider.collider_adjusted.value = −0.488; causal_claims_allowed_without_assumptions = 0 |
| 132 | "4 of 4 … cost 0.4 … risk 0.1; entropy same; random 2 of 4, 5.5, 0.78; greedy 0 of 4, 10" | docs/provenance/M10_RECEIPT_V1.json | experiment_selection.ocm/entropy/random/greedy_confirm |
| 133 | "0 false positives on 6 null … 6 of 6 … one analysis; p-hack 12 analyses … 0 false positives" | docs/provenance/M10_RECEIPT_V1.json | analysis.preregistered; analysis.p_hack_hostile.mean_analyses_tried = 12.0 |
| 134 | "8 of 8 correct verdicts; unparsable, Lean 4 undetermined; mistranslation … dead correspondence; FAIL hostile 3 of 3" | docs/provenance/M10_RECEIPT_V1.json | proof.kernel_correct = 8, suite = 8, unparsable_cannot_check, lean4 = CANNOT_CHECK, mistranslation_pass_with_dead_correspondence = true, hostile_fail_means_false_catches = 3, fail = 3 |
| 135 | "1 of 3 conclusions … 2 of 2 unrelated … replacement live … replayed" | docs/provenance/M10_RECEIPT_V1.json; report §2 | retraction.dead_after_retraction = [C0], unrelated_intact = "2/2", replacement_live_with_lineage, old_stays_dead; report "replay reproduces" |
| 136 | "cross-field transfer … full mapping … adapter … refused lookalike" | docs/provenance/M10_RECEIPT_V1.json | cross_field_transfer |
| 137 | "committed 3 of 6, downgraded 1, refused 2" | docs/provenance/M10_RECEIPT_V1.json; report §2 | communication.committed = 3, downgraded = 1, refused = 2, n = 6 |
| 138 | "External science benchmarks and any frontier target undetermined" | docs/provenance/M10_RECEIPT_V1.json | external (5 keys) |

## 5.8 Governed self-reorganisation (M11)

| # | Sentence (key phrase) | Source file | Field |
|---|---|---|---|
| 139 | "control and seven planted faults … six urgent, six non-urgent … 7 of 7 … 0 false … 0 missed … 7 of 7 … 0 of 6 to 6 of 6 … 2 of 2 … no proposal on control" | docs/provenance/M11_RECEIPT_V1.json | summary.*; scenarios[*].target_before/after; docs/M11_SELF_REORGANISATION_REPORT.md §2 |
| 140 | "parameter search 2 of 7 (S1, S5); reflection-retry 1 of 7 (S1)" | docs/provenance/M11_RECEIPT_V1.json | summary.parent_parameter_search_solves = 2, parent_reflection_retry_solves = 1; parents[*].solves |
| 141 | "S5 reinstated at D2 … broad rewrite refused as not minimum; S6 refused on preservation (0 of 6) and prediction" | docs/provenance/M11_RECEIPT_V1.json | scenarios S5.broad_rewrite.minimum_sufficient = false; S6.broad_rewrite.preservation = "0/6", reasons |
| 142 | "first benchmark run … degenerate baseline (row S29)" | docs/self-application/OCM_SELF_APPLICATION_LEDGER_V1.md row S29 | row |
| 143 | "eighteen rows … 18 of 18 … 8 of 8 … governance only" | docs/provenance/M11_RECEIPT_V1.json | historical_replay_summary.rows = 18, narrow = 18, escalated_with_witness = 8, escalated_rows = 8, kind |
| 144 | "batches 5 and 6 … six and five side-condition defects … benchmark unchanged" | docs/M11_SELF_REORGANISATION_REPORT.md §6, §7; ledger S34, S35 | addenda |
| 145 | Table 5 rows | docs/M11_SELF_REORGANISATION_REPORT.md §4 | claim-by-claim table |

## 5.9 M12 V2

| # | Sentence (key phrase) | Source file | Field |
|---|---|---|---|
| 146 | "two baseline-unknown and two revoked-stops steps are carried-state effects" | docs/M12_LIFETIME_REPORT.md §2 | post-deployment paragraph (4/6, 4/6) |
| 147 | "10 of 10 by both arms; three science families tied; 5 of 5 vs 3 of 5; 4 of 4 vs 2 of 4; 6 of 6 vs 0 of 4; deceptive analogy and lookalike verifier accepted" | docs/provenance/M12_RECEIPT_V1.json | v2.summary.ocm.O1 and whole_system_parent.O1; v2.E.whole_system_parent.O1 (deceptive_analogy ACCEPTED, science_lookalike_verifier TRANSFER) |
| 148 | Table 6 rows | docs/provenance/M12_RECEIPT_V1.json | v2.claims.* (n, ocm, parent, terminal, mcnemar: A_conversations a_only 20, b_only 0, p 1.9e-06; A_post_deployment a_only 11, b_only 4, p 0.118) |
| 149 | "learned first work domain for 12 … second for 7; parent 6 … 12" | docs/provenance/M12_RECEIPT_V1.json | v2.acquisition.ocm.O1–O3; whole_system_parent.O1–O3 |
| 150 | "0 stale, 3 of 3 reopened, 2 of 2 intact; parent 1 stale" | docs/provenance/M12_RECEIPT_V1.json | v2.F.ocm.*.stale_behaviours = 0, dependents_reopened = 3, unrelated_intact = 2; whole_system_parent.*.stale_behaviours = 1 |
| 151 | "diagnosed D2, D6 and D2 … all three orderings; parents solved none" | docs/provenance/M12_RECEIPT_V1.json | v2.G.ocm.O1–O3.diagnosed; whole_system_parent.*.repaired = false |
| 152 | "answered where unknown was licensed 0 times; parent 3 (A) and 2 (D)" | docs/provenance/M12_RECEIPT_V1.json | v2.always_attempts |
| 153 | "O2 and O3 identical phase-A … same B to G … descriptive" | docs/provenance/M12_RECEIPT_V1.json summary O2/O3; docs/M12_LIFETIME_REPORT.md §3 | summary |
| 154 | "SHA-256 prefix 3671aecc" | docs/provenance/M12_REPLICATION_RECEIPT_V1.json | deterministic_block_sha256.principal = replica = 3671aecc… |
| 155 | "full residual supported in scope … one inferential family (n = 54)" | docs/provenance/M12_RECEIPT_V1.json | terminal; tiers.tier6_broad; docs/M12_LIFETIME_REPORT.md §7 |

## 5.10 M12 V3

| # | Sentence (key phrase) | Source file | Field |
|---|---|---|---|
| 156 | "eight protected streams … substitution … leak check 8 of 8" | docs/M12_V3_PAIRED_LIFETIMES_REPORT.md §1; research/ocm-m12/M12_LIFETIME_PREREGISTRATION_V3.md | Streams row; "leak check passed for all 8" |
| 157 | "stream-manifest hash bound … before the run" | docs/provenance/M12_PAIRED_RECEIPT_V1.json | stream_manifest_sha256; preregistration_sha256 |
| 158 | "exact two-sided sign test … α = 0.05; decision rule" | research/ocm-m12/M12_LIFETIME_PREREGISTRATION_V3.md | Primary test; Decision |
| 159 | Table 7 rows | docs/provenance/M12_PAIRED_RECEIPT_V1.json | v3.tests.*.ocm_mean, parent_mean, positive, p_two_sided, verdict |
| 160 | "Ten families reject … Six ties" | docs/provenance/M12_PAIRED_RECEIPT_V1.json | v3.tests verdict counts (derived: 10 OCM_RESIDUAL, 6 TIES_ONLY) |
| 161 | "within-lifetime … residual in every lifetime; 32/48, 48, 40, 48, 32, 48, 48 vs 48, 24, 24, 24, 48, 48, 24" | docs/provenance/M12_PAIRED_RECEIPT_V1.json within_lifetime.A_conversations; docs/M12_V3_PAIRED_LIFETIMES_REPORT.md §2 | RESIDUAL_A × 8; summed steps (report) |
| 162 | "operator ×3, learned-literal ×3, drift ×2 … 8 of 8; parent none" | docs/provenance/M12_PAIRED_RECEIPT_V1.json | v3.G[*].fault, diagnosis_correct, repaired, preserved, rollback_exact; report §2 "parent … repaired none" |
| 163 | "kill gates … zero" | docs/provenance/M12_PAIRED_RECEIPT_V1.json | v3.gates.* = 0 |
| 164 | "about 13 s per machine lifetime, about 0.4 s per parent lifetime" | docs/M12_V3_PAIRED_LIFETIMES_REPORT.md §2 | wall time sentence |
| 165 | "SHA-256 prefix dfc94948" | docs/provenance/M12_PAIRED_REPLICATION_RECEIPT_V1.json | deterministic_block_sha256 |
| 166 | "empty pre-registration hash … repeated (row S36)" | docs/self-application/OCM_SELF_APPLICATION_LEDGER_V1.md row S36; report §3 | row |
| 167 | "lifetime residual supported in scope; frontier-class parent undetermined" | docs/provenance/M12_PAIRED_RECEIPT_V1.json | terminal; report §2 |
| 168 | "V3 stands as the frozen record … size 1/128 … power 0.43 … at most six families … Bonferroni over sixteen families … inconclusive" | ledger row S37 (origin/main); V2:KSO_OPEN_LIST_CLOSURE_THEOREMS_BATCH7_V1.md §G8 | S37; Theorem (i), (ii), (iv) |
| 169 | "conversation differences vary (0.370 to 0.407); other nine identical … (G8)" | docs/provenance/M12_PAIRED_RECEIPT_V1.json | v3.tests.A_conversations.diffs (0.3704–0.4074); other families' diffs identical |
| 170 | "eight fresh paired lifetimes … leak check 8 of 8 … frozen on the stream-manifest hash … ten questions per stream true in the world but unlicensed (G7)" | research/ocm-m12/M12_LIFETIME_PREREGISTRATION_V4.md; docs/provenance/M12_PAIRED_RECEIPT_V4.json | Streams row (leak check 8/8; world-true half); stream_manifest_sha256, preregistration_sha256 |
| 170b | Table 8 rows (V4 sign tests) | docs/provenance/M12_PAIRED_RECEIPT_V4.json | v4.tests.<family>.{role, ocm_mean, parent_mean, positive, p_one_sided, verdict, collapsed_one_coin}: A_conversations 0.9815/0.6065/8/0.00391/OCM_RESIDUAL/false; A_post_deployment 0.881/0.7143; A_honest_unknown 0.9667/0.5667; D_causal 1.0/0.6; E_transfer 1.0/0.0; F_integrity 1.0/0.0; G_self_repair 1.0/0.0 (all secondary, 8/8, 0.00391, collapsed true); A_factual 1.0/0.9, A_negative_transfer 1.0/0.7143, D_communication 1.0/0.5 (descriptive, 8/8); B_enterprise, C_software, D_selection, D_analysis, D_proof, unknown_no_action (n_nonzero = 0) |
| 170c | "parent means vary across the streams (0.574 to 0.611), so it is not collapsed" | docs/M12_V4_PAIRED_LIFETIMES_REPORT.md §2; docs/provenance/M12_PAIRED_RECEIPT_V4.json | report "parent 0.574–0.611"; v4.tests.A_conversations.collapsed_one_coin = false, diffs {0.3704, 0.3889} |
| 170d | "All six secondary families reject at 8 of 8, and all six are flagged … deterministic function of the planted design" | docs/provenance/M12_PAIRED_RECEIPT_V4.json; report §2 | v4.secondary_rejections (6); v4.collapsed_one_coin_families includes all six; report ⚑ paragraph |
| 170e | "operator faults three times, learned-literal three times, drift twice, diagnosed D2, D6, D2 … 8 of 8; revision 0 stale, 3 of 3 reopened, 2 of 2 intact" | docs/provenance/M12_PAIRED_RECEIPT_V4.json | v4.G[*].fault (operator_fault ×3, learning_policy ×3, environment_drift ×2), diagnosed, repaired, preserved, rollback_exact = true ×8; v4.F[*].{stale_behaviours = 0, dependents_reopened = 3, unrelated_intact = 2} |
| 170f | "All kill gates, including the ledger-chain identity gate, read zero" | docs/provenance/M12_PAIRED_RECEIPT_V4.json | v4.gates.* = 0 |
| 170g | "one honest-unknown miss per lifetime (29 of 30) … 'is a whale a mammal' … label defect … both arms equally … (row S38)" | docs/M12_V4_PAIRED_LIFETIMES_REPORT.md §2; ledger row S38 (origin/main) | honest-unknown detail paragraph; S38 |
| 170h | "SHA-256 prefix 599ee69a" | docs/provenance/M12_PAIRED_REPLICATION_RECEIPT_V4.json | deterministic_block_sha256 |
| 170i | "lifetime residual supported in scope … frontier-class parent undetermined" | docs/provenance/M12_PAIRED_RECEIPT_V4.json; report §2 | v4.decision = OCM_LIFETIME_RESIDUAL_SUPPORTED; report "CANNOT_CHECK_MATCHED_PARENT" |

## 6. Reference arm

| # | Sentence (key phrase) | Source file | Field |
|---|---|---|---|
| 171 | "Qwen2.5 7B instruct, 4-bit, digest prefix 845dbda0 … 55 facts … graded" | docs/provenance/M12_REFERENCE_RECEIPT_V1.json | model, model_digest; research/ocm-m12/M12_V3_REFERENCE_ARM_V1.json info.facts_in_prompt = 55; docs/M12_LIFETIME_REPORT.md §10.1 grading description |
| 172 | "REFERENCE (F8) … mutant flips the decision and is caught" | docs/provenance/M12_REFERENCE_RECEIPT_V1.json label; V2 batch 6 §F8 | mutant_reference_as_matched |
| 173 | Table 9 V2 columns | docs/provenance/M12_REFERENCE_RECEIPT_V1.json; docs/provenance/M12_RECEIPT_V1.json summary O1; docs/M12_LIFETIME_REPORT.md §10.1 | summary, post_deployment, always_attempts = 20; parent A = 3 |
| 174 | Table 9 V3 columns | research/ocm-m12/M12_V3_REFERENCE_ARM_V1.json (sums over lifetimes[*]); docs/M12_V3_PAIRED_LIFETIMES_REPORT.md §4 | factual 228/240; unknown 0/160; negative 35/56; lessons 24/28/30/30/31 of 48; OCM 240/160/56/48/40/48/32/48; parent 216/136/40/24/24/24/48/24; always_attempts 20 per lifetime; parent V3 always-attempts NOT MEASURED in the paired receipt |
| 174b | Table 9 V4 columns | research/ocm-m12/M12_V4_REFERENCE_ARM_V1.json (sums over lifetimes[*]); docs/M12_V4_PAIRED_LIFETIMES_REPORT.md §4 | factual 229/240 (29+28+29+29+28+29+29+28); unknown 7/240; negative 35/56 (4+4+7+4+4+4+4+4); lessons acquired 25, reuse 33 (2+4+0+5+6+6+5+5), retained 35 (4+4+1+5+6+5+5+5), revoked-stops 41 (6+4+6+6+6+5+2+6), relearned 23 (1+5+0+4+1+5+4+3) of 48; OCM 240/232/56/48/40/48/32/48 and parent 216/136/40/24/24/24/48/24 from report §4; always_attempts per lifetime 27–30; OCM and parent V4 always-attempts NOT MEASURED in the paired receipt |
| 175 | "On the V2 and V3 suites … answered every out-of-scope question ('is paris in spain' → 'No.')" | docs/M12_LIFETIME_REPORT.md §10.1; reference receipt honest_unknown = "0/20"; V3 reference arm honest_unknown 0/20 per lifetime | quoted example |
| 176 | "Batch 7 (G7) … licence … unlicensed-true …" | V2: batch 7 §G7 | grading rule |
| 177 | "truth grader … 20 of 20 on the V3 items … constant policy … all twenty V3 out-of-scope items world-false" | V2: batch 7 §G7 (ii)–(iv) | Theorem |
| 177b | "480 factual answers: 233 licensed, 199 unlicensed-true, 38 unlicensed-false, 2 wrong … answers 237 of the 240 … right on 199" | docs/M12_V4_PAIRED_LIFETIMES_REPORT.md §4; research/ocm-m12/M12_V4_REFERENCE_ARM_V1.json lifetimes[*].four_class | report sentence; per-lifetime sums 233/199/38/2 [VERIFY: the four classes sum to 472, not 480; the report's "480 factual questions" and the per-class counts do not reconcile and the generator's own file should be checked] |
| 178 | "per-stream acquisition 6, 6, 4, 2, 1, 1, 3, 1 of 6 on V3 and 1, 3, 0, 5, 3, 5, 4, 4 of 6 on V4" | research/ocm-m12/M12_V3_REFERENCE_ARM_V1.json and M12_V4_REFERENCE_ARM_V1.json lifetimes[*].post_deployment.acquired | values |
| 179 | "125 to 130 calls per V3 stream and 136 to 140 per V4 stream, 586.9 s … 760.3 s, not bit-reproducible (one item differed)" | research/ocm-m12/M12_V3_REFERENCE_ARM_V1.json (calls 125–130, wall_s 586.9); M12_V4_REFERENCE_ARM_V1.json (calls 136–140, wall_s 760.3); research/ocm-m12/M12_REFERENCE_ARM_V1.json reproducibility_note | fields |
| 180 | "Conversations not measured for the reference" | docs/provenance/M12_REFERENCE_RECEIPT_V1.json | conversations = "NOT_MEASURED (graded by OCM surface patterns)" |

## 7. Self-application ledger

| # | Sentence (key phrase) | Source file | Field |
|---|---|---|---|
| 181 | "38 rows (S1 to S38)" | docs/self-application/OCM_SELF_APPLICATION_LEDGER_V1.md (origin/main) | rows S1–S38 (38 table rows counted) |
| 182 | "S1 … representation change adopted at the core" | ledger row S1 | J3 column |
| 183 | "S27, S28, S29, S31, S32, S33, S36, S37, S38" | ledger rows (S37, S38 on origin/main) | rows |
| 184 | "S17 … S14, S31" | ledger rows | rows |
| 185 | "backlog … per-source normalisation, unbounded exact extraction, directed random-walk comparator" | ledger "Underperforming modules" table | rows 1, 2, 4 |

## 8. Theory loop

| # | Sentence (key phrase) | Source file | Field |
|---|---|---|---|
| 186 | "35 named gaps (MEG-01 to MEG-35) … seven batches" | V2:ME_THEORY_GAP_ATLAS_V1.md §B; batch files 1–7 | gap list; files |
| 187 | "open list is empty; impossibilities [15, 38] [39, 40] [41]" | V2: batch 7 header and status block ("OPEN: none"), §G1 (iii), §G9, §G6, §G3 | statements |
| 188 | Table 10 rows (item ranges, test counts, "89 of 89", "not yet merged") | V2 batch files (header paragraphs: batch 2 12 tests; batch 3 13; batch 4 12; batch 5 13; batch 6 14; batch 7 13 and "batches 1–7 together 89/89"); warrant note §5 (6 obligations); batch 7 absent from ORION-V2 origin/main (git log, 2026-09-05) | headers |
| 189 | "intake … 9 intakes (7 defect-found, 1 discharged, 1 open) and 2 exports" | src/ocm/selfmodel/intake.py | INTAKES (9 entries; statuses), EXPORTS (2) |
| 190 | "ledger counts … 16 across batches 1 to 6: two (batch 1), one (2), one (3), one (4), six (5), five (6), one caveat, and from batch 7 the rule and label defects of S37 and S38" | docs/self-application/OCM_SELF_APPLICATION_LEDGER_V1.md rows S10 (a, b), S21, S20, S28, S34 (×6), S35 (×5 + 1 caveat), S37, S38 | derived: 2+1+1+1+6+5 = 16 |
| 191 | "exported after M11 and returned as F4 and F3" | src/ocm/selfmodel/intake.py EXPORTS; V2 batch 6 §F3, §F4 | records |
| 192 | "two registry rows: KS-T116 (proved with clause …) and KS-T117 (finite calibration, discharged by V4); two batch-7 obligations remain … MDL [42]" | docs/theorems/OCM_LIFETIME_OBLIGATION_REGISTRY_V1.json (origin/main) rows KS-T116, KS-T117; V2: batch 7 "Consequences" G1, G4 | status, statement, limitation fields |

## 9. Limitations and 10. Pending

| # | Sentence (key phrase) | Source file | Field |
|---|---|---|---|
| 193 | "no network, no containers, no weights beyond a local 7B model" | docs/provenance/M9_RECEIPT_V1.json external_benchmarks note; M12 reference receipt host | notes |
| 194 | "about 60 lexemes and 7 constructions" | docs/M7_PROTECTED_COMPARISON_REPORT.md §3 | sentence |
| 195 | "Coverage … 0; BabyLM and CHILDES not pinned" | docs/provenance/M7_RECEIPT_V1.json | external_families |
| 196 | "five external agent benchmarks, three external science benchmarks, miniF2F/Lean 4, frontier target" | docs/provenance/M9_RECEIPT_V1.json external_benchmarks (5); docs/provenance/M10_RECEIPT_V1.json external (SciCode, ResearchGym, LifeSciBench, miniF2F/Lean4, frontier_target) | keys |
| 197 | "seven criteria, three arms plus reference, seed" | docs/LANGUAGE_KSO_ALPHA_REPORT.md §4 | protocol (7 criteria listed; seed recorded) |
| 198 | "n between 4 and 12 … descriptive" | docs/provenance/M12_RECEIPT_V1.json | v2.claims B–E n ∈ {4, 5, 8, 10, 12} |
| 199 | "In V4 all six secondary families are flagged as collapsed … deterministic functions of the planted design … rests on one family, conversations, in both V3 and V4" | docs/provenance/M12_PAIRED_RECEIPT_V4.json v4.collapsed_one_coin_families, v4.secondary_rejections; docs/provenance/M12_PAIRED_RECEIPT_V1.json v3.tests diffs; docs/M12_V4_PAIRED_LIFETIMES_REPORT.md §2, §5 | fields; report |
| 200 | "§10: pipeline not run; batch 7 on a branch; manifest-licence check (S38) and per-lifetime variation are next" | ORION-V2 git (batch 7 absent from origin/main on 2026-09-05); ledger S38; V4 report §2 | status |

## Methods summary and availability

| # | Sentence (key phrase) | Source file | Field |
|---|---|---|---|
| 201 | "Python 3.11 … two hosts … laptop GPU … Ollama, temperature 0, fixed seed" | docs/M12_LIFETIME_REPORT.md §7; docs/provenance/M12_REFERENCE_RECEIPT_V1.json host; research/ocm-m12/M12_REFERENCE_ARM_V1.json reproducibility_note | fields |
| 202 | "git head unknown at generation" | every M*_RECEIPT_V1.json | git_head_at_generation = "UNKNOWN" (M0 receipt records commits instead) |
| 203 | Dataset list and licences | docs/provenance/BLIMP_, UD_EWT_, MULTIWOZ24_, SIMPLEWIKI_, GUTENBERG_, BABYLM_CUSTODY_MANIFEST_V1.json | dataset, license, status |

Total rows: 217 (203 numeric or terminal-bearing sentences in the extracted list, plus table blocks and derived rows; the V4 update added rows 6b, 64b, 72b, 81b, 170b–170i, 174b, 177b). Rows marked [VERIFY]: 8 (10^5 atoms), 95 (frozen held-out wording), 177b (four-class counts sum to 472 of a stated 480). Rows marked NOT MEASURED: 103 (E4 held-out), 174 (parent V3 always-attempts), 174b (OCM and parent V4 always-attempts). V4 sources were read from ORION-OCM origin/main at commit 8e3df44; the worktree branch does not yet contain them.
