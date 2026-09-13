# Why K2 failed: a decidable condition, and what it predicts

Status: **EXACT CONDITION IN A DECLARED MODEL; NOT EVIDENCE ABOUT #323**
Date: 2026-09-13

`DC-3` records K2 as `NOT_ESTABLISHED` (bar held on 2 of 9 fresh seeds) and
attributes the failure to retained-capital recombination at that grammar. This
unit asks the next question: *under what condition could K2 ever hold?*

## 1. KRC-1 — the model, stated before the result

Retained capital is a library `L` of acquired items. New capital `K1_new` has a
decomposition `P` under the grammar. Acquisition charges one unit per part not
already held:

    B^acq_H     = |P \ L|
    B^acq_RESET = |P \ {}| = |P|

This is a unit-charge abstraction. It is **not** the #323 assay, it measures no
runtime, and no number in it came from an experiment.

## 2. KRC-2 — K2 is decidable in this model, and the condition is exact

    K2 holds  <=>  |P \ L| < |P|  <=>  L ∩ P ≠ {}

So K2 holds **exactly when the library intersects the target's decomposition** —
when new capital is *compositionally reachable* from retained capital. There is
no third case; the condition is necessary and sufficient, not a heuristic.

## 3. KRC-3 — two distinct failure modes, which the bare negative conflates

| mode | condition | reading |
|---|---|---|
| (a) irrelevant library | `L ∩ P = {}`, `|P| > 1` | retention is real but aimed at the wrong parts |
| (b) atomic target, disjoint from the library | `|P| = 1` and `L ∩ P = {}` | acquiring the target itself, which is the only reusable part there is |

These demand different repairs. Mode (a) is fixed by acquiring different
capital; mode (b) is fixed by acquiring the target itself.

**Correction.** An earlier version of this section claimed mode (b) "cannot be
fixed by any library at all". That is false, and the test that appeared to
confirm it was rigged: it drew libraries from a universe that excluded the
target, imposing disjointness by construction. With `P = L = {a}` the history
arm charges 0 against RESET's 1, so **K2 holds on an atomic target whose part
is retained**. Decomposition size alone decides nothing; the governing
condition is `L ∩ P ≠ {}` in both rows. Raised by the ledger repair unit and
verified independently before being written here.

## 4. KRC-4 — the prediction this makes about the registered negative

`DC-3` attributes the 2/9 outcome to retained-capital recombination at the #323
grammar. Under KRC-3 that attribution names mode (b): a grammar whose targets
do not decompose into reusable parts cannot support K2 **for any operator**,
and a retry that changes only the operator would fail again.

This is a **prediction, not a finding.** It is falsified if the registered K2
retry changes only the recombination operator, holds the grammar fixed, and
clears the bar — which would show the failure was mode (a) after all.

## 5. What is not claimed

Not claimed: that #323's grammar is atomic; that the unit-charge model matches
its costs; that clearing the bar in this model would establish K2 empirically;
that K2 is impossible. `DC-3`'s verdict is unchanged — K2 remains
`NOT_ESTABLISHED` — and this unit adds a decidable criterion and a falsifiable
prediction, nothing else.

## 6. Consequence for the registered retry

`K2_RETRY_REGISTRATION_V1` holds the grammar fixed and varies the operator.
KRC-4 predicts that design fails if the target is atomic. The retry should
therefore **also record the decomposition size `|P|`** of each target, so a
second failure can distinguish mode (a) from mode (b) instead of repeating an
uninformative negative. That measurement is cheap and is added to the retry's
required record.
