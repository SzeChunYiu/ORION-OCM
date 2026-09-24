# R5-S1 successor freeze — cost-set geometry and transport repair

Issue: #1068
Ancestor R5 merge: 83f497e6ea6681d6914a5be96f1a4de256e698a5
Frozen parent candidate: R4-S1 head 7736dca517f9d72ec17580168db99ef987bc5abc

This freeze is committed before R5-S1 outcome-bearing implementation. No R5-S1 result is earned unless the frozen R4-S1 parent merges unchanged or an explicit successor refresh rebinds the dependency.

## Defects to adjudicate

1. R5 V1 presentation-relabel check copied the original path costs and was therefore tautological.
2. R5 V1 Lean identity and triangle statements accepted their conclusions as hypotheses instead of deriving them from a cost/path definition.
3. Bare ParetoMin need not exist for an arbitrary infinite ordered cost set; the foundational general object must not assume a frontier exists.
4. Scalar identity-zero requires nonnegative costs/scalarization plus a zero-cost identity, not merely the existence of an identity process.
5. Scalar triangle requires composability plus a subadditive cost law and a minimum/infimum semantics appropriate to the declared cost space.
6. Relabel/frontier transport requires preservation of reachability, contextual values, and cost vectors. A response/cost-changing rename earns no invariance theorem.

## Frozen successor targets

- define the reachable transformation cost set C(M,N) as the general derived object;
- represent unreachable pairs by an empty cost set / extended +infinity scalar distance rather than a fabricated finite cost;
- derive finite Pareto fronts only where minima exist;
- give the infinite descending-cost counterexample schema {1/n : n>=1}, which has no minimum;
- compute finite scalar distances from actual path enumeration;
- kernel-check the registered identity and triangle inequalities from explicit finite distance definitions, not from conclusion hypotheses;
- retain directed asymmetry;
- transform the whole registered graph under a nontrivial node bijection and recompute the frontier independently;
- include a cost-changing transported control that changes the frontier;
- reconcile all R5 rows and state strongest-parent ownership for resource theories / ordered monoids / Lawvere-style directed distance.

## Claim ceiling

GRAND_GMI_V2_R5_S1_REACHABLE_COST_SET_AND_CONDITIONAL_DIRECTED_GEOMETRY_AT_REGISTERED_SCOPE

## Forbidden promotions

- PARETO_FRONTIER_ALWAYS_EXISTS
- UNIVERSAL_SYMMETRIC_METRIC
- IDENTITY_PROCESS_IMPLIES_ZERO_DISTANCE_WITHOUT_COST_ASSUMPTIONS
- TRIANGLE_WITHOUT_SUBADDITIVE_COMPOSITION
- RELABELING_PRESERVES_FRONTIER_WITHOUT_COST_AND_RESPONSE_PRESERVATION
- ALL_RESOURCE_THEORY_IS_GMI_NOVEL
- FULL_GMI
