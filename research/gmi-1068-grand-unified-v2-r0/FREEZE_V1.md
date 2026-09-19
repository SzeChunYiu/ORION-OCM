# Grand Unified GMI V2 — R0 programme freeze

Issue: #1068
Parent programme: #833
Source main: 74e7b889eab2e16a5fb1f7c8183bce2e5d179c82

This file is the freeze-only first commit for R0. No atomic-registry outcome, checker result, dependency result, or literature adjudication existed on this branch when this freeze was committed.

## Candidate theory under attack

The working hypothesis is that GMI may reduce, up to structure-preserving equivalence, to two logically independent inputs:

1. a substrate-relative typed compositional process universe C_S;
2. an externally supplied family of observational/evaluative contexts K.

The candidate central derived object is contextual attainability A_k(x).

R0 does NOT establish this fixed point. It only registers the programme that will try to refute, weaken, or certify it.

## R0 deliverables frozen before implementation

R0 must ship:

1. ATOMIC_CHECKLIST_V1.json
   - every row has a stable id, round, title, evidence kind and initial status;
   - UNKNOWN/CANNOT_CHECK remain valid;
   - no row is marked scientifically earned merely because it appears in the registry.

2. THEORY_DAG_V1.json
   - round dependency graph;
   - acyclic;
   - fixed-point publication cannot precede foundation, derivation, hostile-review and formal-verification rounds.

3. PARENT_REGISTRY_V1.json
   - initial parent-literature anchors;
   - every entry classed PARENT_OWNED / COMPARISON_PARENT / HISTORICAL;
   - no novelty is granted by registration.

4. THEOREM_STATUS_V1.json
   - status vocabulary:
     PROVED
     PARENT_OWNED
     FINITE_CALIBRATION
     CONJECTURE
     EMPIRICAL
     CANNOT_CHECK
     NOT_STARTED.

5. MERGE_GATE_V1.json
   - frozen round merge requirements matching issue #1068.

6. check_r0.py and RESULT_V1.json
   - check unique atomic ids;
   - require every issue round R0..R16 to exist;
   - require a DAG with no cycle;
   - require only allowed status/evidence vocabularies;
   - require parent rows to have a source identifier;
   - require final round to depend on formal verification and hostile recursive closure;
   - run planted hostiles proving these checks move.

## Non-goals

R0 proves no final GMI theorem.
R0 performs no neural-family recovery.
R0 does not close any #833 scientific row.
R0 does not claim literature saturation.
R0 does not claim Lean/Coq/Isabelle certification.
R0 does not establish metaphysical completeness.

## Claim ceiling

GRAND_GMI_V2_R0_PROGRAMME_REGISTRY_AND_EXECUTION_CONSTITUTION_ONLY

## Forbidden promotions

- GRAND_GMI_FIXED_POINT_PROVED
- TWO_FACTOR_CORE_IRREDUCIBLE
- COMPLETE_AI_LITERATURE_EXPLAINED
- BLANK_COMPUTER_INTELLIGENCE_DERIVED
- NEURAL_FAMILY_DERIVED
- FULL_GMI
- ABSOLUTE_FOUNDATION_PROVED
