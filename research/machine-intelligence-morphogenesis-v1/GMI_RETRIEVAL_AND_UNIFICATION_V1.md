# Retrieval policy, and when one memory store suffices — I1 (#602)

Date: 2026-09-14. Status: **DERIVATION + EXACT WITNESS**. Closes the two remaining boxes of I1. The other
eight were closed by `GMI_MEMORY_REGIME_PARTITION_V1.md` and
`GMI_CONSOLIDATION_FORGETTING_THEOREM_V1.md`.

## 1. Retrieval policy — the third use of one stopping rule

Retrieval is PVR-3's `U` term, and *which* item to try is a stopping problem: try candidates in some
order, each costing a retrieval, stopping when another try is not worth its cost.

Two claims, both checked against exhaustive enumeration over every ordering and every stopping point:

| claim | result |
|---|---|
| the optimal order is decreasing **match probability per retrieval cost** | **exact** — `p/c` ordering costs 3.5650, the exhaustive optimum is 3.5650 |
| the stopping point is the **value-aware rule** already derived for planning and replanning | **exact** — both pick `k = 3` |

> **Retrieve in decreasing `p/c`, and stop when the expected saving from another retrieval falls below its
> cost.**

The stopping half is not a new rule. It is the same one that governs **planning depth**
(`GMI_PLANNING_STOPPING_RULE_V1.md`) and **replanning under drift**
(`GMI_REPLANNING_UNDER_DRIFT_V1.md`): *act when the change is worth more than the search that finds it.*
Three settings, one rule.

## 2. When is a unified store sufficient?

The partition gave four regimes with different growth laws. A **unified** store must serve every regime at
a single per-item cost — necessarily the most expensive any regime demands. **Differentiated** stores pay
each regime's own.

| per-item costs by regime | unified | differentiated | winner | saving |
|---|---:|---:|---|---:|
| 1, 1, 1, 1 | 18 | 18 | **unified** (tie) | 0 |
| 1, 2, 3, 1 | 54 | 25 | differentiated | 29 |
| 1, 4, 8, 1 | 144 | 41 | differentiated | 103 |
| 1, 8, 16, 1 | 288 | 69 | differentiated | **219** |

> **Differentiation pays exactly when per-item costs differ across regimes, and the saving grows with the
> spread. At equal costs a unified store is sufficient.**

This is the answer I1 asks for, and it is a *conditional* one: the four regimes derived earlier are
distinct in their **growth laws** regardless, but they only need to be distinct **stores** when their
per-item costs diverge. A machine whose episodic, semantic and procedural items cost the same to hold has
no reason to separate them, however different their growth.

## 3. Scope

**Derived:** the retrieval order and its stopping point, both exact against enumeration; and the
unified-versus-differentiated condition with its monotone saving.

**Assumptions:** independent candidate matches for retrieval — correlated candidates change the expected
reach and therefore the order. For unification, additive per-item costs and no shared overhead between
stores; a fixed cost per store would shift the boundary toward unification.

**Not derived:** the *content* of what is retrieved, only which store and in what order. And the four
regimes' per-item costs are taken as given here rather than derived from the substrate.

**Falsifier:** a candidate set where `p/c` ordering is not optimal, or a cost profile with unequal
per-item costs where unification still wins.

## 4. I1 status — all ten boxes

| box | where |
|---|---|
| working / episodic / semantic / procedural regimes | partition document (four distinct growth laws) |
| consolidation, replay and forgetting triggers | consolidation theorem (three-way condition) |
| interference / stability–plasticity | already covered by the continual-retention theorem |
| **retrieval policy** | **here** |
| **unified vs differentiated** | **here** |
