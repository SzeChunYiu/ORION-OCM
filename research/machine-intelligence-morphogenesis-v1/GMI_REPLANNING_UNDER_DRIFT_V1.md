# Replanning under model drift — and the boundary the stopping rule left open

Date: 2026-09-14. Status: **CONJECTURE REFINED BY ITS OWN COUNTEREXAMPLE**. Closes I4's *"replanning
under model error/drift"*, and **resolves the open boundary** registered in
`GMI_PLANNING_STOPPING_RULE_V1.md`.

## 1. The conjecture, and where it broke

The stopping rule says: stop searching when no deeper search can change the committed action. The natural
dual is that **resuming** search obeys the same criterion against a different threat — replan when
accumulated model error makes the committed action no longer the one a corrected model would choose.

Tested against the two policies it must beat, over 40 steps × 200 trials per drift regime:

| drift | never replan | **on action change** | always replan | best |
|---:|---:|---:|---:|---|
| 0.05 | 120.06 | 120.06 | 200.06 | tie |
| 0.20 | **120.23** | 120.58 | 198.95 | never |
| 0.50 | 121.92 | **114.02** | 189.09 | on change |
| 1.00 | 136.62 | **110.24** | 183.52 | on change |

**Action-change triggering wins only 2 of 4.** At drift 0.2 it pays for 0.8 replans on average and ends
up *worse* than never replanning — the action genuinely changes, but the improvement is worth less than
the replan that finds it.

## 2. That is precisely the divergence the stopping rule could not construct

`GMI_PLANNING_STOPPING_RULE_V1.md` registered this falsifier: *"a problem family and search price where
the cost-optimal depth is strictly less than the invariance depth."* Sweeping search price 16-fold failed
to produce one. **It appears here**, in the drift setting rather than the depth setting, for exactly the
predicted reason: an action change worth less than the search that reveals it.

**Action-invariance is necessary but not sufficient.** The stopping rule's coincidence with the optimum
was a property of that problem family, not a general identity — and the falsifier it registered has now
fired.

## 3. The refinement, and it weakly dominates

Add the value test the counterexample demands: replan when the action would change **and** the
improvement over the remaining horizon exceeds the replan cost.

| drift | never | on action change | **value-aware** | always | best |
|---:|---:|---:|---:|---:|---|
| 0.05 | 119.85 | 119.85 | **119.85** | 199.85 | tie |
| 0.20 | 119.39 | 120.00 | **119.02** | 198.28 | **value-aware** |
| 0.50 | 119.84 | 112.87 | **111.45** | 188.32 | **value-aware** |
| 1.00 | 133.94 | 110.37 | **109.18** | 183.37 | **value-aware** |

**Cheapest on 3 of 4 and tied on the fourth — weakly dominant across every regime tested.** And it
achieves that with **fewer** replans than action-change triggering everywhere (0.3 against 0.9; 1.5
against 2.3; 2.8 against 3.5), because it declines exactly the changes that do not pay.

## 4. The corrected rule, for both directions

> **Search, or resume searching, exactly when the action would change *and* the change is worth more than
> the search that finds it.**

Action-invariance bounds where search *could* help; the value test says where it *does*. One rule now
covers when to stop searching and when to start again, with the same two conditions in both directions.

## 5. Scope

**Derived:** a replanning policy that weakly dominates never-replan, always-replan and pure
action-change triggering across four drift regimes.

**Assumptions:** two actions, scalar drifting costs, free observation of the true costs, and a known
remaining horizon. Costly observation would add a third term, and with more actions the value test needs
the best alternative rather than a single comparison.

**Evidence class:** simulation over 400 trials per cell, not exact enumeration — weaker than the finite
witnesses used elsewhere in this lane, and labelled as such.

**Falsifier:** a drift regime where pure action-change triggering or always-replan beats the value-aware
policy.
