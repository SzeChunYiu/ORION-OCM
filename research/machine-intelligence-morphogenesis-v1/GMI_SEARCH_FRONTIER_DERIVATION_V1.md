# Explicit search derived, and priced against a compiled policy (B16)

Date: 2026-09-14. Lane: machine-intelligence-morphogenesis-v1.
Witness: `gmi_microscope/search_frontier_witness.py`.
Receipt: `microscopes/results/STAGE_SEARCH_FRONTIER_V1.json`.
Executed on `laptop-billy`; receipt md5-verified. Reproduced in CI.

PVR-3 says retained structure earns its keep past a break-even fixed by what it
replaces. A compiled policy **is** retained structure; a search is the
recomputation it replaces.

> The search family is not a separate idea. It is the **other side** of the
> break-even this corpus has been using throughout.

## When an explicit frontier is forced

| `b` | `D` | states | budget | policy possible |
|---:|---:|---:|---:|---|
| 2 | 3 | 15 | 40 | ✅ |
| 3 | 3 | 40 | 40 | ✅ |
| 3 | 4 | **121** | 40 | **✗** |

> Search is not *chosen* here. It is what remains when compilation is
> impossible — a statement about the world's size against the machine's
> storage, neither of them a preference.

## Breadth, depth and best-first are memory regimes

Same world, same goal, four orderings:

| order | nodes expanded | peak memory |
|---|---:|---:|
| breadth-first | 121 | **81** |
| depth-first | 121 | **9** |
| best-first (informed) | **5** | 9 |
| best-first (constant h) | 121 | 9 |

Depth-first holds 9 nodes at once against breadth-first's 81 on the *same* 121
expansions — ordering trades memory and nothing else. The constant heuristic
expands all 121: it guides nothing, which is the control that stops "best-first"
from looking inherently good.

> The three orders are not three algorithms to choose between on taste. They are
> what a search looks like **under a memory budget, without one, and with an
> informative heuristic.**

## Heuristic value is the search it removes

A heuristic is charged per node scored.

| price per node | charged blind | charged informed | worth it |
|---:|---:|---:|---|
| 0 | 121 | **5** | ✅ |
| 4 | 121 | 25 | ✅ |
| 16 | 121 | 85 | ✅ |
| **24** | 121 | **125** | **✗** |
| 64 | 121 | 325 | ✗ |

The break-even is high — this heuristic cuts 121 expansions to 5 — but it is
**finite**, which is the point.

> An accurate heuristic on a cheap-to-search problem is still the wrong machine
> if scoring costs more than the search it replaces.

## Compile versus search is a reuse count

World of 121 states; the best available search expands 5 nodes per query.

| queries `r` | compile (once) | search (`r×`) | cheaper |
|---:|---:|---:|---|
| 1 | 121 | **5** | search |
| 16 | 121 | **80** | search |
| 24 | 121 | **120** | search |
| **32** | **121** | 160 | **compile** |
| 64 | **121** | 320 | compile |

> **Test-time search is correct exactly when queries are rare relative to the
> world's size** — when there is not enough reuse to amortize a compiled policy.
> A machine that searches at query time is not a machine that failed to learn;
> it is one whose ecology never repeated itself enough to make learning pay.

*The searcher is priced at the best search it has, not a blind one — a machine
choosing between compiling and searching would not handicap itself. A first
version used blind breadth-first on a world so small it expanded every state,
which made search cost exactly what compiling cost and left no crossover to
find.*

## Neutral recovery, with no `SEARCH` primitive

Candidates are described only by what they store and what they do per query.
No family name appears.

| world | queries | cheapest shape | reads as |
|---|---:|---|---|
| b=2 D=3 | 2 | store nothing, expand per query | **a searcher** |
| b=2 D=3 | 32 | store everything | a compiled policy |
| b=3 D=4 | 2 | store nothing, expand per query | **a searcher** |
| b=3 D=4 | 64 | store everything | a compiled policy |

Both shapes are recovered from the same description by cost alone.

## Scope

- `b`-ary trees of depth ≤ 4 with a single goal leaf, no cycles, unit edge cost.
  A graph with cycles or non-uniform costs would change the expansion counts.
- The heuristic is charged per node *expanded*, not per node scored. Charging
  every push would raise its price and lower the break-even.
- Peak memory counts frontier or stack entries, not bytes.
- The neutral-recovery candidate space has two shapes. A partial-compilation
  shape (store some states, search from the nearest) is legal in this ledger and
  is not evaluated.

**Falsifier.** Exhibit a world where an informative heuristic expands more nodes
than blind breadth-first; or one where compiling is cheaper at every query
count, which would remove the break-even entirely.
