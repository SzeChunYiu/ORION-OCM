# R5-S1 post-merge adjudication

R5 V1 is historical evidence. Its merge does not erase later review findings.

## R5-A1 — presentation-transport check was tautological

The V1 executable route assigned the "renamed" path list by copying the original path costs. Equality of the frontiers therefore could not fail.

**Repair:** R5-S1 transforms node names in the graph, independently re-enumerates transformed paths, and recomputes the cost set/frontier. A cost-changing control changes the result and is rejected.

## R5-A2 — Lean identity and triangle statements assumed their conclusions

The V1 Lean theorems accepted `dAA=0` and `dAC <= dAB+dBC` as hypotheses and returned them.

**Repair:** R5-S1 defines the registered finite distances and kernel-proves:
- `dAA=0` by reduction;
- `dAC <= dAB+dBC` from the explicit `Nat.min` path-cost formula.

It also proves a generic cost-set transport theorem from a path bijection plus cost preservation.

## R5-A3 — arbitrary frontier existence was implicit

`ParetoMin {c(f)}` was written as though every ordered cost set supplies a minimum/frontier.

**Repair:** the general object is the reachable cost set. Pareto/frontier objects are conditional derived views. The descending `{1/n}` schema records an infinite no-minimum boundary.

## R5-A4 — identity-zero and triangle need resource assumptions

A compositional identity need not have zero measured cost under every accounting, and sequential costs need not be additive.

**Repair:** zero distance is conditional on a zero-cost empty/identity path. Triangle is conditional on a subadditive composition account and an appropriate finite minimum/extended-distance semantics.

## Reverse-dependency consequence

R6-S1 must consume this corrected conditional resource geometry rather than the R5 V1 GREEN status alone.

## Claim ceiling

`GRAND_GMI_V2_R5_S1_REACHABLE_COST_SET_AND_CONDITIONAL_DIRECTED_GEOMETRY_AT_REGISTERED_SCOPE`
