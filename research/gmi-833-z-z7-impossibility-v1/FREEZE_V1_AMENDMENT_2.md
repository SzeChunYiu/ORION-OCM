# Z7 freeze amendment 2 — the tightness test cannot see a vacuous upper bound

Committed **before** the receipt carrying the corrected classification.

## What was wrong

`FREEZE_V1.md` requires every ceiling to be shown **valid** (no candidate beats
it) and **tight** (attained), on the stated ground that *a valid but slack
ceiling tests nothing*. The `H2_VACUOUS_CEILING` hostile demonstrates the test
working: restating `C1` as `e_delay >= 0` leaves the attained minimum at `8`, so
the ceiling is reported slack and the hostile fires.

Tightness-as-attainment only detects vacuity for a **lower** bound. For an
**upper** bound sitting at the top of the quantity's a priori range, attained and
vacuous coincide, and the check goes silent.

`C4` is exactly that case. It claims `min(e_now, e_delay) <= K4` with the measured
`K4 = 16`. Both error counts lie in `[0, 16]` by construction, so the bound
cannot be violated by any candidate in any universe: `violations = 0` was
guaranteed before the enumeration ran. The first receipt reported it
`valid: true, tight: true` and the gate passed.

`C5` is a second instance of a different kind: `|S_1| = K5` with `K5` *defined*
as `len(S_1)`, so the claim is an identity, and its `valid` and `tight` fields
were hardcoded literals — the same defect the Z5 amendment records for that
package's first null, surviving here. `Z7_THEOREMS_V1.md` already described `C5`
honestly as "measured / measured", so the theorem note and the receipt
disagreed.

`C3`, `risk >= 0`, is a third: the bound is at the bottom of the range and
forbids nothing. Its real content is the *attained minimum*, which is exactly
`0`.

## The repair

A **vacuity check** is added. For each ceiling the executor records the
quantity's a priori range and the bound's direction, and classifies it:

- `FORBIDDING_BOUND` — a lower bound strictly above the range minimum, or an
  upper bound strictly below the range maximum. Only these are ceilings in the
  sense row 4 means, and only these are gated valid-and-tight.
- `NON_BINDING` — a bound at the range boundary. It cannot be violated and
  therefore tests nothing.
- `MEASURED_IDENTITY` — a claim whose right-hand side is defined as the measured
  quantity.

The check is validated on real data before its verdicts are used: it must flag
`C4` and the `H2` hostile `e_delay >= 0`, and must stay silent on `C1`, `C2` and
`C6`. Both the recall and the no-alarm case are gated.

## What this changes in the claim

`C1` (`e_delay >= 8`), `C2` (`risk >= p/2` for every `p`) and `C6`
(`min J = min(eta*p/2, lambda)`) remain genuine prospectively frozen forbidding
ceilings, each valid and tight, with `git log` proving the freeze preceded the
enumeration. Those three close row 4.

`C3`, `C4` and `C5` are retained in the receipt but are **no longer counted as
ceilings**: `C3` is reported as an attained minimum of exactly `0`, `C4` as
`NON_BINDING`, `C5` as a `MEASURED_IDENTITY`. The reconciliation line, the
theorem note and `CORE.md` are corrected to say so.

Counting a tautology as a frozen capability ceiling is the inert-instrument class
this freeze names, and it is corrected here rather than left for an auditor.

## Nothing else in the freeze changes

The claim ceiling, the rows, `Q1`–`Q5`, the families, the null, the hostiles and
the forbidden promotions are unchanged.
