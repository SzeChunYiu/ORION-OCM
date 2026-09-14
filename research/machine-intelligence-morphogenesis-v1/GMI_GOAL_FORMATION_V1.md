# Goal formation, and its duality with forgetting — I4 (#602) / item 11 (#592)

Date: 2026-09-14. Status: **DERIVATION + EXACT WITNESS WITH A DISCRIMINATING CONTROL**. Closes the last
open half of item 11. I4 asks for *"goal formation from obligation/utility structure"* — from the
structure, not posited.

## 1. The claim

`GMI_CONSOLIDATION_FORGETTING_THEOREM_V1.md` showed that when **retention** capacity is exceeded the
machine must drop obligations, and CSR-1 names which. Goal formation is the same selection run **forward**:
when the **achievement** budget cannot cover every obligation, the machine must choose which to pursue.

> **The set a budget-constrained planner pursues is the set a capacity-constrained retainer keeps.**
> Goals and forgetting are one selection rule seen from two directions, so **goal formation requires no
> new principle** — it is the obligation/utility structure under a budget, which is what I4 asks for.

## 2. Witness, and the control that gives it content

Six obligations with utilities and costs; every subset enumerated at each budget.

**Matched costs** (achievement cost = retention cost):

| budget | pursued (forward) | retained (backward) | identical |
|---:|---|---|---|
| 6 | o1, o2, o4 | o1, o2, o4 | ✅ |
| 8 | o1, o5 | o1, o5 | ✅ |
| 10 | o1, o2, o5 | o1, o2, o5 | ✅ |
| 14 | o1, o2, o3, o5 | o1, o2, o3, o5 | ✅ |
| 18 | all six | all six | ✅ |

**Identical at every budget, 9 of 9.**

**The control — costs deliberately mismatched:**

| budget | pursued | retained | identical |
|---:|---|---|---|
| 2 | o2 | o3 | ❌ |
| 4 | o1, o4 | o2, o5 | ❌ |
| 8 | o1, o5 | o2, o3, o5 | ❌ |
| 16 | o1, o2, o3, o4, o5 | o1, o2, o3, o5, o6 | ❌ |

**They differ on 7 of 9 budgets.**

Without that control the first table proves nothing — "it is the same knapsack" would be a fair objection.
The control shows the identity is a **consequence of the cost structure being matched**, not of the two
problems being the same problem by construction. The identity is contingent and therefore has content.

## 3. The divergence is itself a prediction

When achievement and retention costs differ, the sets come apart in a specific way: **an agent pursues
things it will not retain, and retains things it did not pursue.** Cheap-to-do but expensive-to-keep
obligations are achieved and then forgotten; expensive-to-do but cheap-to-keep ones are held once acquired
but never chosen fresh.

That is a falsifiable structural prediction about any bounded agent, and it follows from the duality
rather than being added to it.

## 4. Scope

**Derived:** goal formation as constrained selection over the obligation/utility structure, and its
duality with forgetting.

**Not derived:** *where the utilities come from*. The obligation structure supplies them here; deriving
utility itself is outside this and is not claimed.

**Assumptions:** additive utility and additive cost with a single scalar budget. Under interacting
obligations — where satisfying one changes another's cost — the selection is no longer a knapsack and the
duality is not established.

**Falsifier:** matched achievement and retention costs under which the pursued and retained sets differ,
or a mismatched pair under which they provably cannot.

## 5. Item 11 / I4 status after this

| box | status |
|---|---|
| goal formation from obligation/utility structure | **derived here** |
| subgoal discovery | derived (`GMI_SUBGOAL_DERIVATION_V1.md`) |
| planning stopping rule | derived (`GMI_PLANNING_STOPPING_RULE_V1.md`) |
| plan-vs-habit / amortization crossover | already covered by GKF-11 |
| model-based future simulation | open |
| replanning under model error / drift | open |
