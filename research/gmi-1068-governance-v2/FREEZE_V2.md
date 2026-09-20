# Grand GMI V2 governance successor freeze

Issue: #1068
Historical constitution: R0 V1 / #1069

R0 V1 artifacts remain immutable historical evidence. This successor exists because later rounds demonstrated that a green/merged round can be invalidated by a later review finding, while the V1 DAG/status files have no executable reverse-dependency semantics.

This freeze precedes the V2 status registry, R17 addendum, validator, and workflow.

## Frozen governance targets

1. Keep the scientific dependency graph acyclic.
2. Give each round R0-R17 one current status from:
   - EARNED
   - IN_PROGRESS
   - STALE
   - NOT_STARTED
   - UNKNOWN
   - CANNOT_CHECK
3. A round may be EARNED only if every declared dependency is EARNED.
4. Therefore making any dependency STALE automatically forbids every descendant from remaining EARNED.
5. A PR that changes an Rn package must start from a base where every dependency of Rn is EARNED.
6. A post-merge correction uses successor evidence; historical receipts are never silently rewritten.
7. Every successor that re-earns a stale round must update the current status registry and name its exact evidence/merge lineage.
8. R17 is a final audit/certificate round, not a back-edge in the scientific DAG.
9. UNKNOWN and CANNOT_CHECK remain valid scoped terminals; they do not become EARNED by issue closure.
10. A scope-bound closure certificate cannot assert absence of unknown unknowns, unique metaphysical foundations, or decidability of unbounded semantics.

## R17 purpose

R17 validates the fixed-point **closure procedure**:
- reverse-dependency invalidation;
- theorem/parent/status successor consistency;
- no active superseded theorem;
- declared open/undecidable regions;
- independent hostile review;
- exact artifact manifest/certificate at a declared scope.

## Claim ceiling

GRAND_GMI_V2_EXECUTABLE_RECURSIVE_GOVERNANCE_AND_SCOPE_BOUND_CLOSURE_PROTOCOL_ONLY
