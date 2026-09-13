# What a subgoal is, derived — checklist item 11 (partial)

Date: 2026-09-14. Status: **CONJECTURE FALSIFIED, CORRECTED, THEN EXACT**. Addresses half of the gap the
coverage audit recorded for item 11: *"missing: goal formation and subgoal decomposition."* This supplies
subgoal decomposition. Goal formation and the planning stopping rule remain open.

## The conjecture, and why it failed

Item 10 derived a skill as a retained sub-quotient, which suggested: **a subgoal is the entry state of a
retained skill** — the state from which a compiled skill becomes applicable.

Tested by complete enumeration over all 30 prefix-states of five targets, comparing cost-to-go with and
without the retained skill set:

| quantity | count |
|---|---:|
| states where retention strictly lowers cost-to-go | **20** |
| states where some retained skill is applicable | **10** |
| sets identical? | **no** |
| entry state but no cost drop | 0 |
| cost drop but not an entry state | **10** |

**Falsified, and the direction is informative.** Entry states are a strict *subset*. Ten further states —
`('abcabc', 1)`, `('abcabc', 2)` and their analogues — show a cost drop without any skill being applicable
there, because a skill applies *later* in the remaining plan and the benefit propagates backward by
ordinary dynamic programming. "Where the cost-to-go drops" over-counts subgoals two to one, and what it
is really measuring is *reachability of a benefit*, not a decomposition point.

## The correction, and it is exact

The benefit must be **realised locally**, not inherited. Define a state as a *local* discontinuity iff its
drop **exceeds the drop inherited from its successor**:

> **`drop(s) > drop(successor(s))`**

| quantity | count |
|---|---:|
| local discontinuities | **10** |
| entry states | **10** |
| **identical?** | **yes** — symmetric difference empty, both directions |

> **A subgoal is a state at which the cost-to-go drop is realised locally, and that set is exactly the set
> of entry states of retained skills.**

The locality condition removes precisely the backward propagation that broke the naive version. Subgoals
are where a compiled capability *becomes available*, not everywhere its eventual availability is felt.

## Why the failure was worth keeping

The naive conjecture is the one a reader would reach first, and it is wrong by a factor of two in this
witness. Recording the falsification makes the locality condition load-bearing rather than decorative — it
is not a technical refinement, it is what separates a decomposition point from the ordinary fact that
good outcomes have value in advance.

## Scope and what remains

**Derived:** subgoal decomposition, given a retained skill set.

**Not derived:** *goal* formation — where the top-level target comes from — and the **stopping rule for
planning**, which item 11 also names. The acquisition theorem supplies a stopping rule for probing, not
for search over futures; that remains open and is the natural next piece.

**Load-bearing assumption:** the skill set is fixed and given. Subgoals here are relative to what has
already been compiled, so the decomposition is a *consequence* of prior chunking, not independent of it. A
different retained set yields a different subgoal set, which is a substantive prediction rather than a
caveat: **an agent's subgoals are determined by its skills, so two agents with different skills decompose
the same task differently.**

**Falsifier:** a retained skill set and target where the local-discontinuity set and the entry set differ
in either direction.
