# A2 signature programme extension — result V1

Ticket `REV-L50-A2-SIGNATURE-PROGRAMME` (#833). Freeze `FREEZE_V1.md` + Amendments A1–A5, all committed pre-execution. Screen `a2_extension_v1.py`, receipt `A2_EXTENDED_SCREEN_V1.json` (sha256 `e816752c15c1037248f7ed4a98b42d887181c9359f049113eb795eb533cab501`), executed on billy-laptop 2026-09-17; adjudication `A2_ADJUDICATION_V1.json`. The frozen #855 matcher is imported and used unchanged; the #974 screen is untouched.

## Coverage before → after

- **Before**: 3 registered fingerprint families (attention-aggregate, shared-local-kernel, recurrent-state), covering 12 of the 31 D2 denylist classes semantically; the other 19 classes (neural/MLP/backprop, Bayes, genetic, planner/sygus, self-modify/Gödel/rewrite, retrieval, and more) were catchable only lexically — a neutral-named macro from those families passed A2.
- **After**: 6 new mechanism-grounded families — `dense_feedforward_aggregate`, `stochastic_belief_update`, `population_selection_crossover`, `program_synthesis_search_macro`, `self_modification_macro`, `external_content_retrieval` — completing the mapping: all 31 D2 classes now have a semantic fingerprint (receipt field `d2_mapping_complete`). Derived signatures are name-blind (tested by the P2 neutral-rename plants).

## Validation (checker bar; all green before any corpus candidate was emitted)

- P1 known-same synthetic recall 6/6; P2 neutral-rename recall 6/6 (the semantic-collision test).
- P3 no-alarm: the #974 five-primitive basis and the corpus clean grammar (neutral_machine c/r/b/i dispatcher) flag 0. aj9b's basis is prose-declared (0 extractable blocks) — reported, not gated.
- P4 sampled no-alarm: 200 tagless blocks → 0 flags. This control caught one real over-fire (a local-accumulator read as state) which was fixed pre-execution as Amendment A5.
- P5 census anchors: aj9b IN, af-barrier OUT, robustness-controls covered (programmatically verified) — PASS. Operationalized census 107/106/1 vs the registered 109/108/1; the registered composition was never materialized, so the screen population is the PROVABLE SUPERSET (first-pass 138 ∪ operationalized unaudited = 148 packages), strictly covering the registered population (Amendment A4).
- P6 existing-family regression: the three #974 controls still fire — the extension does not disturb the merged standard.

## Corpus screen

148 packages screened, 1607 primitive blocks extracted and signed, 36 flags across 10 packages: dense-feedforward 21, recurrent-state 13, program-synthesis 1, shared-local-kernel 1. Bayes, genetic, self-modify, retrieval, attention families: 0 flags.

## Adjudication (all 36 individually; rule frozen in section 6 of the freeze)

**0 CONFIRMED semantic collisions.** All flags are `CONTEXT_NOT_GRAMMAR`:

| class | n | cause |
|-------|---|-------|
| A_MD_RESULT_ROW_DENSE_LABEL | 21 | markdown result/registry rows where `DENSE` is the corpus morphology-memory class label (DENSE/KVSTORE/PROGRAM/TABLE), not a dense-layer operator; `softmax` appears in parent-literature microfeature-registry prose |
| B_EXECUTOR_VM_INFRA | 9 | the shared `Machine`/`execute` program executor (state cells + charged ops) every searcher runs on — ecology infrastructure, not a searched-grammar primitive |
| B_EVALUATOR_INFRA | 2 | the package `evaluate`/`opcode_contract` verification routines |
| C_ANALYSIS_OR_HARNESS | 4 | solver/census/harness functions (`solve`, `closure_depth`, `run_candidate`, `synthesize`) |

Recorded detector false-positive causes (for the next iteration of the standard): the `dense` lexicon token collides with the corpus's own DENSE class label in markdown tables; executor/evaluator classes structurally match recurrent-state/synthesis signatures because the VM legitimately holds state and calls the verifier — grammar membership is exactly what adjudication adds.

## Disposition

At extended-A2 signature level, across the 148-package superset population (⊇ the registered 108): **no package's searched grammar encodes a banned-family macro under a neutral name** — refining L48/L50 for this population from "cannot exclude" to a signature-level screened disposition, with the detector limitations above registered. The one registered grammar-target instance (INSTANCE-AJ9-NOSMUGGLING-SCOPE, aj-lane) remains untouched by this screen's scope.

```text
A2_SIGNATURE_PROGRAMME_EXTENSION_V1_DELIVERED
ALL_31_D2_CLASSES_SEMANTICALLY_MAPPED_9_FAMILIES
NAME_BLIND_DERIVATION_VALIDATED_ON_PLANTS
148_PACKAGES_1607_BLOCKS_SCREENED_0_CONFIRMED_COLLISIONS
NO_CHANGE_TO_855_STANDARD_OR_974_SCREEN
```
