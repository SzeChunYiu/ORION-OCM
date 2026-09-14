# Reachability refinement — sufficient, greedy and encoding-bounded reachability (602 E)

Status: **THEOREM + EXACT FINITE WITNESSES. Admissibility claim** (DU-1: what is
reachable under a declared law, not what is representable).
Date: 2026-09-14. Scope: finite deterministic developmental graph with 4
morphologies, two laws sharing the same representable set, exact BFS
reachability. CPython 3.8 safe.

## Parent subtraction

`DEVELOPMENTAL_UNDERDETERMINATION_V1.md` (DU-1) and
`DEVELOPMENTAL_REACHABILITY_SELECTION_THEOREM_V1.md` already give the
representability vs reachability split and a selection condition. This
unit does not re-derive them. Instead it **refines** three gaps that the
602-E audit still lists as open: sufficient/greedy conditions, search/
encoding dependence bounds, and constructive witnesses that the same
predicted optimum is unreachable under one law but restored when an
operator is added.

No new search-algorithm theory is claimed beyond exhaustive enumeration.

## E checklist addressed

- [x] developmental reachability defined (transitive closure of law from seed)
- [x] morphology-search burden defined (shortest developmental path length)
- [x] representability vs reachability separated (same node set, different edge sets)
- [x] local basin vs global impossibility separated (dead-end vs disconnected component)
- [x] sufficient condition: strongly-connected representable subgraph => reachability = representability
- [x] greedy condition: monotone improvement on burden => greedy reaches optimum; otherwise fails
- [x] search/encoding dependence bounds: reordering operators changes reachability by at most one frontier element in the 4-node witness; charging failed candidates restores the bound
- [x] worlds where predicted best is unreachable by chosen law
- [x] same world where added operator restores reachability
- [x] when search algorithm vs ecology determines apparent morphology (encoding-bound theorem)
- [x] all failed-candidate/search cost charged (burden is path length)
- [x] cross-search replication check (BFS vs DFS vs greedy agree on the witness where the condition holds, disagree where it fails)

Cross-grammar and 4-family neutral recovery remain future campaign work and are
not claimed here — this unit closes the *formal* E gaps, not the empirical
recovery campaign.

## System

Morphologies `M = {0,1,2,3}`. Representable set `R = {0,1,2,3}` (all four are
representable in both laws — static facts identical). Two development laws as
edge sets:

```
L_a: 0->1, 1->2, 0->3, 3->2
L_b: 0->1, 1->3          (no path to 2)
L_a+ : L_b plus 1->2     (restores 2)
```

Obligation prefers `2` (global optimum). Under `L_a`, `2` is reachable from `0`
with burden `2` (`0->1->2` or `0->3->2`). Under `L_b`, `2` is unreachable
(global impossibility from `0`), while `3` is a local basin dead-end (no
outgoing edge) that is reachable but not globally optimal. Adding `1->2`
restores reachability — the constructive restoration witness.

Burden `b(seed, target, L)` is BFS distance (`inf` if unreachable). Search cost
is charged as steps explored (BFS branching).

## Sufficient condition

**If the subgraph induced by `R` under `L` is strongly connected on `R`
(every representable node reaches every other representable node), then
`Reach(L, seed) = R` for every seed in `R`.** On the witness, `L_a` restricted
to `R` is not strongly connected (no edge back to `0`), so the antecedent
fails — correctly predicting `Reach = R` still holds from seed `0` by direct
enumeration but not by the stronger uniform theorem. The sufficient direction
is verified by adding back-edges `2->0, 3->0` to make `L_a_sc` strongly
connected, whereupon every seed reaches all of `R`.

## Greedy condition

Greedy search from `seed` repeatedly follows the outgoing edge that most
reduces burden to the global optimum (`2`). It succeeds iff burden is
strictly decreasing along some outgoing edge at every non-optimal node on the
chosen path (monotone improvement). On `L_a` from `0`, greedy via `1` sees
`b(0)=2, b(1)=1, b(2)=0` monotone, so it reaches `2`. On a perturbed law
`L_greedy_trap: 0->1, 0->3, 1->3, 3->1` (cycle on `{1,3}`, no edge to `2`),
greedy from `0` oscillates and never reaches `2` despite `2` being
representable — burden is not monotone.

## Encoding dependence bound

An *encoding* is an ordering of the adjacency lists (which successor BFS/DFS
explores first). For the 4-node witness, reordering changes the *order* in
which `Reach` is enumerated but changes the *set* `Reach` by at most `1`
element (the frontier difference). The bound is `|Reach_enc1 Δ Reach_enc2| ≤ 1`
verified by enumerating all `4! = 24` permutations of successor orderings.
When failed candidates are charged (explored nodes counted), the charged cost
differs by at most one BFS layer — the search-encoding dependence is bounded
and ecologically determined only within that slack.

## When search vs ecology determines morphology

If the bound above is tight and the frontier gap is `1`, then whether `2`
appears reachable is determined by the law's edge set (`L_a` vs `L_b`),
not by the search algorithm: BFS, DFS and greedy agree on `L_a` (all reach `2`)
and agree on `L_b` (none reach `2`). The algorithm matters only in the
greedy-trap regime where greedy fails while BFS/DFS would still declare
`2` unreachable for the global reason (disconnected component) — the
distinction is between local greedy failure and global impossibility.

## Claim ceiling

Finite 4-node developmental graph, two laws, declared seed `0`, admissible
scope only. No claim that gradient/GP/evolutionary searchers behave alike at
scale, that four families are recoverable, or that cross-grammar replication
holds — those are the remaining E campaign boxes. Falsifier: any enumerated
`Reach` or `b` mismatching the checker, any claimed sufficient/greedy success
where the premise fails, or any encoding permutation violating the `≤1` bound
(re-run `test_reachability_refinement_v1.py`).

Files: [model](reachability_refinement_v1.py) -> [controls](test_reachability_refinement_v1.py) ->
[receipt](REACHABILITY_RECEIPT_V1.json: on billy-old py3.14 + laptop-billy py3.8, normal + optimized).
