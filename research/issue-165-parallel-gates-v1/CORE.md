# Issue #165 parallel remaining-gate campaign

Coordinator for
[issue #165](https://github.com/SzeChunYiu/ORION-OCM/issues/165).
PR: [#206](https://github.com/SzeChunYiu/ORION-OCM/pull/206).

Locked successors (L2/L3, MATH-2/3, #73 flagship, G4.4 ML, E4/fresh-host)
stay locked unless their entry receipts exist. Negative terminals are
first-class. Where a first mechanism failed, the conversion is a different
acquisition/serving rule, not a salt retune. `PARENT_SUFFICIENT` is not
programme failure.

Do not overwrite frozen `RESULT.json` files. Do not edit production `src/`
in these capsules. Worker branches are unique `cursor/<name>-cf8f` and must
not push this remaining-gates branch.

## Wave 0 capsules (already on this branch)

| lane | directory | terminal |
|---|---|---|
| G3.2 | `research/g3-failure-memory-v1/` | `FAILURE_MEMORY_USEFUL_AT_SCOPE` |
| G3.3 | `research/g3-representation-v1/` | `PARENT_SUFFICIENT` (v2: `REPRESENTATION_CHANGE_CAUSALLY_USEFUL`) |
| G3.4 | `research/g3-representation-diagnosis-v1/` | `REPRESENTATION_INSUFFICIENCY_DIAGNOSIS_SUPPORTED_AT_SCOPE` |
| G5.2 | `research/g5-packed-field-v1/` | `FACTORIZED_KNOWLEDGE_SPACE_SUPPORTED` |
| G5.3 | `research/g5-factored-warrant-v1/` | `FACTORED_WARRANT_VALUE_SUPPORTED` |
| G5.3 BDD | `research/g5-bdd-warrant-v2/` | `BDD_PARENT_N3_PARITY_SUPPORTED` (ZDD still OPEN) |
| G5.4 | `research/g5-consolidation-v1/` | `EPISTEMICALLY_SAFE_COMPRESSION_SUPPORTED` |
| G2.5 v1 | `research/g2-strong-parents-v1/` | `HARMFUL_TRANSFER_LIMIT` (frozen) |
| G2.5 v2 | `research/g2-utility-gated-parents-v2/` | `UTILITY_GATED_LIBRARY_BEATS_PRIMITIVE` |
| G1.2 / G1.3 | `research/g1-controller-growth-v1/` | `COMPACT_VESSEL_PARTIAL` |
| G1.3.2 | `research/g1-fo-competence-v2/` | `COMPETENCE_IN_FO_STATE_AT_MICRO_SCOPE` |
| G6 | `research/g6-intervention-lab-v1/` | `SELF_EVOLUTION_SUPPORTED_BOUNDED` |
| MATH-1 | `research/math-n4-lemma-reuse-v1/` | `CAUSAL_PROOF_METHOD_REUSE_SUPPORTED_AT_MINIATURE_SCOPE` |
| MATH-1 v2 | `research/math-n4-subgoal-v2/` | `CAUSAL_SUBGOAL_LEMMA_INTRODUCTION_SUPPORTED_AT_MINIATURE_SCOPE` |
| L1 v1 | `research/l1-linguistic-g2-v1/` | `COMPOSITIONAL_LANGUAGE_LEARNING_ONLY` |
| L1 v2 | `research/l1-linguistic-g2-v2/` | `COMPOSITIONAL_LANGUAGE_LEARNING_ONLY` |
| G7 D1 | `research/g7-lineage-v1/` | `PHASED_COGNITIVE_DEVELOPMENT` |
| G7 D2 | `research/g7-lineage-d2-v2/` | `PHASED_COGNITIVE_DEVELOPMENT` |
| G7 D3 | `research/g7-lineage-d3-v3/` | `PHASED_COGNITIVE_DEVELOPMENT` |
| H3 | `research/h3-local-revision-v1/` | `PARENT_SUFFICIENT_AT_PLANTED_KSO_SCOPE` |
| §7 | `research/cross-domain-transfer-v1/` | `CROSS_DOMAIN_TRANSFER_SUPPORTED_AT_REGISTERED_SCOPE` |
| §3 | `research/cinv-audit-v1/` | `CONSTITUTIONAL_INVARIANTS_PRESERVED_AT_SCOPE` |
| §15 v1 | `research/publication-constitution-v1/` | `PUBLICATION_CONSTITUTION_FROZEN_WITH_GAPS` |
| §15 v2 | `research/publication-constitution-v2/` | harvest; E4/fresh-host still `CANNOT_CHECK` |

## Wave 2 capsules (this integration)

| lane | directory | terminal |
|---|---|---|
| H4 | `research/h4-exact-revocation-v1/` | `PARENT_SUFFICIENT_AT_PLANTED_EXACT_REVOCATION_SCOPE` |
| H1 v1 | `research/h1-amortized-acquisition-v1/` | `NO_AMORTIZED_ACQUISITION_LATER_NOT_CHEAPER` |
| H1 v2 | `research/h1-amortized-rewrite-v2/` | `LIBRARY_ACQUISITION_EXCEEDS_LATER_SAVINGS` (later compute falls; capital unrecouped) |
| H2 | `research/h2-sparse-cognition-v1/` | `PARENT_SUFFICIENT_AT_PLANTED_INDEX_SCOPE` |
| G7 D4 | `research/g7-lineage-d4-v4/` | `PHASED_COGNITIVE_DEVELOPMENT` (T4 rewrite) |
| G7 D5 | `research/g7-lineage-d5-v5/` | `PHASED_COGNITIVE_DEVELOPMENT` (T5 selector) |
| G7 D6 | `research/g7-lineage-d6-v6/` | `PHASED_COGNITIVE_DEVELOPMENT` (T6 governed repair) |
| L1 v3 | `research/l1-linguistic-g2-v3/` | `COMPOSITIONAL_LANGUAGE_LEARNING_ONLY` (SOV earned; `NO_CROSS_FAMILY_TRANSFER`) |
| G6 parents | `research/g6-intervention-parents-v2/` | `PARENT_SUFFICIENT` (ATMS/change-impact; BO `CANNOT_CHECK`) |
| #93 / GEF | `research/kso-general-field-v1/` | `CURRENT_KSO_ALREADY_GENERAL_ENOUGH` |
| #93 N/k | `research/kso-general-field-nk-v2/` | `CURRENT_KSO_ALREADY_GENERAL_ENOUGH` |
| G2.4 restart | `research/g2-process-restart-v1/` | `OS_PROCESS_RESTART_HELD_OUT_SOLVE_SUPPORTED` |
| P1 | `research/p1-causal-reuse-v1/` | `P1_CAUSAL_REUSE_SUPPORTED_AT_POLYNOMIAL_MICROSCOPE` |
| G1.1.6 | `research/g1-duplicate-cores-v1/` | `SINGLE_CORE_AT_SCOPE` (measurement, not deletion) |
| G2 acq | `research/g2-acquisition-economics-v1/` | `CHEAP_SEARCH_AWARE_SELECTION_REPRODUCES_THE_TOURNAMENT_CHOICE` |

## Still locked / honest OPEN

L2/L3 entire. MATH-2/3 entire. #73 prototype + P7. G4.4 all nine (do not train ML).
E4 / fresh-host / independent authorship. Programme-wide close.
Architecture “Π remains small” still PARTIAL until a dedicated measurement lands.
Corpus-scale N1. UD at corpus. Meaning graphs beyond bound. G5.3 production
adoption. `PHYSICAL_DENOMINATOR_CLEAN`. G1.1.6 **deletion**. H1 full vector
(library capital still exceeds later saving after rewrite). Neural/Transformer
`CANNOT_CHECK_NO_NN_LIBRARY`.
