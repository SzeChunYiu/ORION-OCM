# Confidence, and why calibration is a local requirement — I6 (#602)

Date: 2026-09-14. Status: **DERIVATION + EXACT WITNESS**. Addresses I6, which my own earlier probe found
**mentioned in zero files** of this lane. The other lane holds the self-prediction impossibility bound
(`REFLECTIVE_SELF_REFERENCE_THEOREM_V1.md`); this supplies the decision-side objects.

## 1. Confidence is defined by what it changes

Confidence is not intrinsically valuable. It is charged like everything else here, so it earns its cost
only by **changing an action**. With an abstain option and costs (wrong `W`, abstain `A`, right 0), the
optimal policy is

> **answer iff `(1 − p)W < A`, i.e. `p > 1 − A/W`**

so **confidence is a decision-relevant object exactly where it can cross that threshold**, and the
threshold is set by the cost ratio rather than chosen. Error-likelihood is the same object read the other
way, `1 − p`, and needs no separate derivation.

This is why the substrate's `ABSTAIN` primitive is the metacognitive one: it is the only primitive whose
value depends on an estimate of the machine's own correctness.

## 2. The consequence, which is not obvious

If only the *crossing* matters, then miscalibration far from the threshold should be free. Tested with
`W = 10`, `A = 3`, so the threshold is 0.70, over twenty confidence bins:

| miscalibration region | cost | excess over perfect calibration |
|---|---:|---:|
| far **below** threshold, [0.00, 0.40] | 2.5500 | **+0.0000** |
| **near** threshold, [0.60, 0.80] | 2.6000 | **+0.0500** |
| far **above** threshold, [0.90, 1.00] | 2.5500 | **+0.0000** |

Distortions of ±0.15 were applied in each region; the far regions cost **exactly zero** in both directions.

> **Calibration is a local requirement.** A confidence signal that is badly wrong far from the decision
> threshold costs nothing at all. Only calibration in the neighbourhood of the threshold matters.

The dichotomy is **qualitative, not quantitative** — exactly zero against nonzero, not a gradient. That is
the robust part of the result.

## 3. What that says about metacognition

A machine does not need to know how good it is. It needs to know **whether it is above or below the line
where its action changes**, and only there. "Well-calibrated confidence" as a global property is a
stronger requirement than any decision in this framework can cash.

It also predicts where metacognitive effort should be spent: **on cases near the threshold**, since effort
spent sharpening confidence on cases that are clearly answerable or clearly not is spent for no return.

## 4. Scope

**Derived:** confidence as a threshold-crossing object with the threshold fixed by the cost ratio;
error-likelihood as its complement; and the locality of calibration.

**Effect size caveat:** the near-threshold excess here is 0.05 against a base of 2.55, because confidence
is uniformly distributed over the bins. A distribution concentrated near the threshold would make the
excess much larger. **The structural claim — zero far away, nonzero near — is what is robust; the
magnitude is distribution-dependent** and should not be quoted on its own.

**Assumptions:** a single abstain option, a scalar confidence, and costs that do not vary across items.
Item-varying costs would make the threshold item-specific, which changes where calibration is needed but
not that it is local.

**Falsifier:** a cost structure where miscalibration strictly away from the threshold changes the expected
cost.

## 5. I6 status

| box | where |
|---|---|
| **confidence as an internal decision-relevant object** | **here** — threshold crossing |
| **error-likelihood estimate** | **here** — the complement, same object |
| expected value of further cognition | the value-aware rule (`GMI_REPLANNING_UNDER_DRIFT_V1.md`) |
| continue / stop / reconsider | stopping rule + replanning — all three are one criterion |
| **calibration criterion** | **here** — local, not global |
| strategy selection among reasoning methods | partial — the same cost comparison, not separately witnessed |
| self-model / self-prediction impossibility | other lane's reflective self-reference theorem |
