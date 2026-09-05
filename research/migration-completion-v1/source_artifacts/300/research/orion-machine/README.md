# ORION Cognitive Machine research

Umbrella: ORION-V2 #194  
Execution master: ORION-V2 #197  
Governing directive: #194 comment `5539487737` (2026-09-04) — **substrate + constraints, not an architecture**; MNI/MNSI emergent, not specified.

## Current terminal

```text
OBJECT_OF_STUDY                     = SUBSTRATE_AND_CONSTRAINTS (directive 2026-09-04); MNI/MNSI emergent, not specified
SUBSTRATE_SEMANTICS (#203)          = PARENT_OBJECT_ADOPTED (ATMS label + PCC gate + resource vector); FREEZE = CANNOT_CHECK (audit unreturned)
CHANNEL_SUFFICIENCY (a) (#200)      = INTERFACE_HIERARCHY_ONLY; every rung PARENT_OWNED; residual NOT_EARNED__OBSTRUCTION_RESTATED (non-decomposability, not non-rectangularity)
NATURAL_NONRECTANGULAR_CLASS        = EXISTS (every non-affine concept class under version-space warrant; Theorem R); VSW(SINGLETONS_5) non-decomposable, I=1 certified, PARENT_OWNED (Angluin 1988 subset queries)
COMPOSITION_WITH_WARRANT (b)        = PARENT_OWNED (ATMS label combination; S2)
SELF_REVISION_AUTHORITY (c) (#201)  = PARENT_SUFFICIENT (Blackwell/CEGAR/L4; Theorem S4); Godel machine x ATMS owns the constraint
REVOCATION_COMPLETE_LEARNING        = CONSTRAINT_ON_(c); elementary pack = CALIBRATION; RCL-C = NOT_EARNED__NONDECOMPOSABLE_INSTANCE_PARENT_OWNED
SUBSTRATE_COST (#202)               = TRADEOFF_FRONTIER_ONLY; comparator equivalence CANNOT_CHECK
LANGUAGE_BRIDGE (#204)              = FORMAL_ONLY (dissolved into channel encoding)
QUANTUM_OPERATOR (#205)             = NO_ELIGIBLE_OPERATOR (dissolved)
SEPARATION_CLAIM (procedure-learner vs large-exposure approximator) = NOT_ESTABLISHED; test NOT_FROZEN__CONDITION_1_UNSATISFIABLE_CLASS_INDEPENDENT (Theorem N2); freezable only as a restricted-comparator frontier
EXTERNAL_NOVELTY                    = NOT_ESTABLISHED
INDEPENDENT_REVIEW (#199, #245)     = NOT_OBTAINED__DISCLOSED_LIMITATION
MECHANIZATION                       = CANNOT_CHECK (no toolchain)
KSO_M0 (#284; theory/KSO_SUBSTRATE_CONTRACT_V1.md Part I+II, KSO_ARCHITECTURE_V1.md) = FROZEN_V1 (S1-S7 bound on the machine; retraction/hub both directions; obstruction witness a definition; 8 parents run: PARENT_PRODUCT_OWNED)
KSO_M1 (reference/kso_m1_mex1_population_v1.py; results/KSO_M1_POPULATION_RECEIPT_V1.json) = GREEN_DEV_SPLIT (ME-X1, 50 worlds, label == oracle 0 mismatches on 1,344 cells; protected NOT_RUN)
KSO_M2 (reference/kso_m2_solve_v1.py; results/KSO_M2_SOLVE_RECEIPT_V1.json) = NAVIGATION_EXACT 38/50 on the ME-X1 dev split (STORE_EXACT 50/50 is the store's, not the walk's; 12 misses attributed to EXTRACT, M2.1 revival open); two-atomizer invariance 50/50; 0 budget overruns
KSO_M2 comparator (guards lane; results/KSO_M2_COMPARATOR_RECEIPT_V1.json) = PARENT_SUFFICIENT vs the B5 ceiling (50/50 both); navigation-only 38/50 indistinguishable from RWR/PPR 32/50 (p=0.31) and CBR/KG 34/50 (p=0.52) at n=50; null 5/50
KSO_M2b (algebra domain; results/KSO_M2B_ALGEBRA_RECEIPT_V1.json) = P0_OPEN — procedures are code and the discriminant gate is a conditional, so the instruction-channel requirement is NOT met (independent replay, #295 comment 6); V1 kept as M2B_GATING_DEFECT, V2 superseded, V3 fix pending
```

## Start here

1. `theory/OCM_DIRECTIVE_RESCOPE_V1.md` — the programme under the directive: lane restatements, parent subtraction for the five channels / composition / self-revision, what is open and why.
2. `theory/OCM_OPERATIONAL_SEMANTICS_V1.md` + `reference/ocm_reference_semantics.py` — the substrate and its constraints S1–S7.
3. Lane records: `theory/OCM_LANE_200_TERMINAL_V1.md`, `OCM_LANE_201_TERMINAL_V1.md`, `OCM_LANE_202_TERMINAL_V1.md`, `OCM_LANES_204_205_PRECONDITION_RECORD_V1.md`.
4. `theory/OCM_SEPARATION_TEST_DESIGN_V1.md` — the separation claim's registered-test design and why its pre-run audit fails; `theory/OCM_SEPARATION_TEST_REAUDIT_V2.md` — the re-audit against the registered non-rectangular class (Theorem N2: the blocker is the comparator definition, for every class).
4a. `theory/OCM_NONRECTANGULAR_CLASS_V1.md` + `reference/ocm_nonrectangular_class_exact.py` — the lane-200 revival: rectangularity criterion, decomposability, Theorem R (rectangular ⇔ affine), the registered natural non-decomposable instance `VSW(SINGLETONS_5)`.
5. `revocation_complete_learning/` — the RCL pack (`README.md` there), the V1 checker `rcl_checks_v1.py`, and `RCL_KILL_GATE_AUDIT_V1.md` (authoring-side, not the #245 terminal).
6. `OCM_TASK_LEDGER_V1.json`, `OCM_FAILURE_LEDGER.md`, `theory/OCM_FALSIFIER_REGISTER_V1.json`.
7. The knowledge-space object (#284): `CONVERGENCE_MAP_V1.md` (every artifact as a KSO component), `theory/KSO_SUBSTRATE_CONTRACT_V1.md` (maths + mechanics, Part I/II), `theory/KSO_ARCHITECTURE_V1.md` (components, dependency graph), `theory/KSO_PARENT_SUBTRACTION_V1.md`; checkers `reference/kso_math_v1.py`, `reference/kso_m0_freeze_checks_v1.py`, `reference/kso_m1_mex1_population_v1.py`; results under `results/KSO_*`.

The active research question is now: what is the minimal substrate under which a machine can acquire procedures with warrant from instruction, demonstration, interaction, experimentation and feedback; compose them with warrant preserved; and revise its own representation, learning strategy and architecture without losing exact authority over what it already knows. Revocation-complete learning is the authority-preservation constraint on the last of these, not the programme.

This directory is math-first. It authorizes no frontier-model training, protected evaluation, natural-language competence, quantum advantage, paper existence, novelty, or architecture-superiority claim. The pre-directive terminal block is retained in `OCM_SNAPSHOT_V1.json` (`terminals_recorded_elsewhere_quoted_not_asserted`) as history.
