# RV-377-111 — FREEZE: does `RV-377-088` survive the intervention index it never swept?

Frozen BEFORE the run. Outcomes appended only.

## Why this run exists

The DG-7 V2 audit (merged this session) found that `RV-377-088` — the record that
**opened** DG-7 and supplies **both** of its claimed overturns — never swept the
intervention index. Verified independently here before acting on it:

* `STAGE_DE_SMOOTH_V30_DENSE_PARENT_MAXIMAL.json` contains **zero** occurrences of
  the string `"intervention"`.
* Its `claim_ceiling` enumerates the seed and column indices and omits the
  intervention set entirely.
* Its `C2_column_invariance_of_the_winner` verifies the winner on "all six" —
  and the six are **columns** (`B0`, `B1`, `B2`, `B3`, `P3`, `U_UNIFORM_UNIVERSAL`),
  not interventions. The phrase is what made this look already-swept.

Rule 36 was opened by `RV-377-085` three records earlier **in the same lane**, which
measured 5 of 8 registered rows changing status between `standard` alone and the
six-intervention family; `RV-377-082`'s structurally identical dense witness on
`E_smooth1` fell 0.8906 → 0.8281 / 0.7448 / 0.5260 under it. The risk is quantified,
not speculative.

## What is at stake

`RV-377-088`'s `C1` asserts, unqualified, that the dense row class contains an
admissible member. On that rest the withdrawals of two `NOT_OBSERVABLE` terminals
(`RV-377-009`, `RV-377-014`). If the cells do not survive the family, **DG-7's running
score of "two negatives overturned" is zero**, and both terminals return.

## Method, and the control that makes it readable

`RV-377-088`'s rows are `S4Net` subclasses scored by `smooth.run` at 48 development
events on the `all` criterion. `smooth.run` has no intervention parameter, and
`ecology.run_genotype` — which does — takes a genotype graph and the registry's
16-event specs, so it cannot reproduce these numbers.

`gmi_microscope/rv111_dg7_rescore.py` therefore re-implements the development loop with
the intervention applied, copying `ecology.run_genotype`'s semantics line for line: the
same `J` dict, the same `order` permutation, the same `revoke` / `double_revoke` rule,
the same `extra` unseen-feedback rule.

**`smooth.run` is not modified.** No existing result moves.

> **Faithfulness control.** Under the `standard` intervention this loop must reproduce
> `RV-377-088`'s published admissibility for **every** one of the 11 cells. If the
> control fails, the re-implementation is wrong and **no intervention number from this
> run may be read** — the receipt's status becomes
> `CONTROL_FAILED__NO_INTERVENTION_NUMBER_IS_READABLE` and the run is discarded, not
> patched.

11 cells (`E_smooth` 4, `E_smooth2` 4, `E_smooth3` 3) × 6 interventions = 66 developments.

## Frozen predictions

| id | prediction | falsifier |
|----|-----------|-----------|
| U1 | The faithfulness control **passes** on all 11 cells. | any cell where recomputed `standard` admissibility differs from the published grid |
| U2 | **Fewer than half the 11 cells survive all six interventions** (≤ 5 of 11). | 6 or more survive |
| U3 | **At most 1 of the 4 `E_smooth2` cells survives** — these are the cells the two overturns rest on. | 2 or more survive |
| U4 | The binding intervention is `shuffled_events` or `half_events` on a majority of the cells that fail — `GMI-DA9` names exactly these two for coefficient carriers, and this row is a coefficient carrier. | some other intervention binds on most failures |

U2 and U3 are predictions **against** the corpus's own positive record: they say a
record this lane has been citing for weeks does not survive the rule its own lane
wrote three records earlier. U4 is a prediction **for** GMI — a genuine risk, since
`GMI-DA9` was fitted on different rows and this is fresh ground for it.

If U3 holds, two `NOT_OBSERVABLE` terminals are restored and DG-7's overturn count
goes to zero or one. That is recorded as such, and the restored terminals are
reinstated verbatim rather than re-derived.
