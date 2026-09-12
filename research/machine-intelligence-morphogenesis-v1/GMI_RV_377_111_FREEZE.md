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

---

# RV-377-111 — ADJUDICATION (appended; nothing frozen above was edited)

## Result

```
faithfulness control passed: True          status: EXECUTED_EXACT_AT_SCOPE
surviving all six interventions: 0 of 11
binding intervention: half_events on 11 of 11
```

| ecology | cell | `standard` | min over six | θ − min | fx short | |
|---|---|---|---|---|---|---|
| `E_smooth` | `h12_lr0.25` | 0.8568 | 0.6094 | 0.2406 | 5.774 | FAILS |
| `E_smooth` | `h4_lr0.25` | 0.9062 | 0.7708 | 0.0792 | 1.901 | FAILS |
| `E_smooth` | `h6_lr0.125` | 0.8568 | 0.7396 | 0.1104 | 2.650 | FAILS |
| `E_smooth` | `h8_lr0.25` | 0.8646 | 0.7188 | 0.1312 | 3.149 | FAILS |
| `E_smooth2` | `h16_lr0.0625` | 0.8646 | 0.5729 | 0.2771 | 6.650 | FAILS |
| `E_smooth2` | `h3_lr0.25` | 0.8672 | 0.7266 | 0.1234 | 2.962 | FAILS |
| `E_smooth2` | `h4_lr0.125` | 0.8672 | 0.7917 | 0.0583 | 1.399 | FAILS |
| `E_smooth2` | `h6_lr0.125` | 0.8802 | **0.8490** | 0.0010 | **0.024** | **WITHIN_QUANTIZATION** |
| `E_smooth3` | `h4_lr0.125` | 0.8932 | 0.7734 | 0.0766 | 1.838 | FAILS |
| `E_smooth3` | `h6_lr0.125` | 0.8750 | 0.7526 | 0.0974 | 2.338 | FAILS |
| `E_smooth3` | `h8_lr0.125` | 0.8698 | 0.7656 | 0.0844 | 2.026 | FAILS |

## Predictions, scored

| id | outcome |
|----|---------|
| U1 | **CONFIRMED** — control passed on all 11 cells; the intervention numbers are readable |
| U2 | **CONFIRMED** — 0 of 11 survive, against a predicted ≤ 5 |
| U3 | **CONFIRMED** — 0 of 4 `E_smooth2` cells survive, against a predicted ≤ 1 |
| U4 | **CONFIRMED, and more sharply than predicted** — `half_events` binds on **11 of 11**, not merely a majority |

## Consequence: DG-7's overturn count is zero

`RV-377-088`'s `C1` — "the dense row class contains an admissible member", asserted
unqualified — does not hold under the registered intervention family on any of the
three ecologies it measured. Under rule 36 the claim was never admissible to make.

> **The two `NOT_OBSERVABLE` terminals withdrawn on the strength of `RV-377-088` are
> RESTORED:** `E_SMOOTH2_NOT_OBSERVABLE__NO_ADMISSIBLE_ROW_AT_16_EVENTS`
> (`RV-377-009`) and its 48-event counterpart (`RV-377-014`). They are reinstated
> **verbatim**, not re-derived. DG-7's running score of "two class-level negatives
> overturned" is **zero**.

This is the fifth positive claim in this corpus invalidated by a rule the same lane
wrote, and the first where the invalidating rule predated the claim by three records.

## The honest caveat, which cuts against my own conclusion

`E_smooth2 | h6_lr0.125` fails by **0.0010 capability = 0.024 fx units** — a
twenty-fifth of one quantization step. Rule 40's discipline is symmetric: a margin
below one fx unit is not a separation, and that applies to a *failure* exactly as it
applies to a success. That cell is recorded **`WITHIN_QUANTIZATION`, not failed**. It
is the single strongest cell in `RV-377-088`'s grid and it is, on this evidence,
undecided rather than refuted.

So the precise statement is: **0 of 11 cells survive, 10 of 11 fail outright, and 1 is
within quantization.** The restoration of the two terminals rests on the other three
`E_smooth2` cells, which fail by 1.399 to 6.650 fx units and are not close.

## A genuine positive for GMI, on ground it was never fitted to

`GMI-DA9` states that exactness buys intervention-robustness and that **coefficient
rows fail under `shuffled_events` and `half_events`**. It was derived from different
rows, on different ecologies, at a different development length.

`half_events` is the binding intervention on **11 of 11** cells here — every cell,
without exception, on three ecologies, across `h` from 3 to 16 and `lr` from 0.0625 to
0.25. `GMI-DA9` named the failure mode correctly on rows it had never seen.

That is recorded as a corroboration and not inflated: it is one intervention of the
two DA9 names, on one row family, and it does not rescue `C1`.

## Preserved

`RV-377-088`'s text, receipt and published numbers are untouched. The `standard`
column of this re-score reproduces its published admissibility exactly, which is what
makes the intervention column readable. `smooth.run` was not modified.
