# A stopping rule for planning — item 11 (#592) / I4 (#602)

Date: 2026-09-14. Status: **DERIVED ANALOGUE + EXACT WITNESS, after two vacuous attempts**. Closes the
second half of item 11, recorded by the audit as: *"the stopping rule for planning is not derived (only
for acquisition)."*

## 1. The analogue

`TDA-1` stops **acquisition** when a common action is compatible with every surviving candidate —
uncertainty about *which world*. Planning's uncertainty is about *which plan*, so the structural analogue
is **action-invariance**:

> **Stop searching when no deeper search can change the action committed now.**

Acquisition stops when one action suits every surviving *candidate*; planning stops when one action
survives every deeper *search*.

## 2. Two vacuous attempts, recorded because they were not obviously vacuous

**Attempt 1** charged the executed plan at the true optimum regardless of search depth. Deeper search
therefore bought nothing, total cost rose monotonically, and "stop at depth 1" won by construction. It
reported a perfect match on all targets — a meaningless one.

**Attempt 2** ran a proper receding horizon but charged the tail past the horizon at one per remaining
step. That estimate was tight enough that depth-1 already chose optimally, so executed cost was flat
across depth and the match was again automatic. **Zero of six cases were non-vacuous.**

Both looked like confirmations. The tell in each was that executed cost did not vary with depth, which is
now checked and reported explicitly.

## 3. The model that actually tests it

The depth-limited planner is **optimistic past its horizon** (tail charged 0), which is what makes shallow
search genuinely misleading: a cheap-looking immediate move can foreclose a far cheaper long skill.

| target | true optimum | executed cost by depth | total by depth | invariance depth | cost-optimal depth |
|---|---:|---|---|---:|---:|
| `abcd` | 1 | 4, 1, 1, 1 | 8, **3**, 4, 5 | 2 | **2** |
| `abcdabcd` | 2 | 8, 5, 2, 2, … | 16, 15, **8**, 10, … | 3 | **3** |
| `abcdef` | 1 | 6, 1, 1, … | 12, **3**, 4, … | 2 | **2** |
| `abcabc` | 1 | 6, 1, 1, … | 12, **3**, 4, … | 2 | **2** |

**Executed cost varies with depth on 4 of 4 cases**, so the test is non-vacuous, and the invariance depth
equals the cost-optimal depth in every one.

## 4. The boundary I expected to find, and did not

Invariance and optimality *should* come apart when an action change is worth **less** than the search that
finds it — then the optimum would be shallower than the invariance depth. Swept over search price
`C_search ∈ {1, 2, 4, 8, 16}`: **all 20 cells still match.**

There is a mechanism rather than a coincidence: in this family, deeper search yields plans that need
**fewer decisions**, so part of the extra per-decision search cost is repaid by having fewer decisions to
pay it on. At `C_search = 16` the depth-2 plan still wins, but only by 3 — the margin narrows as predicted
without crossing.

**Stated honestly: I could not construct a divergence, not that none exists.** Whether a problem family
exists where the cost-optimal depth is strictly shallower than the invariance depth is open, and it is the
sharpest test of this rule.

## 5. Scope

**Derived:** a stopping rule for planning, structurally analogous to the acquisition rule, matching the
cost-optimum across four problems and a 16-fold price sweep.

**Not derived:** goal *formation*, the other half of item 11. Subgoal decomposition is in
`GMI_SUBGOAL_DERIVATION_V1.md`; where the top-level target comes from remains open.

**Assumptions:** deterministic transitions, a fixed retained skill set, and an optimistic horizon
heuristic. Under an admissible-but-tight heuristic the rule degenerates to depth 1 — which is what
attempt 2 measured and is a correct result about that planner, not a failure of the rule.

**Falsifier:** a problem family and search price where the cost-optimal depth is strictly less than the
invariance depth.
