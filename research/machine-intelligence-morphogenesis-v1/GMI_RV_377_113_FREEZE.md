# RV-377-113 — FREEZE: does the neutrally-recovered coefficient carrier survive rule 36?

Frozen BEFORE the run. Outcomes appended only.

## What the CP1 baselines turned up

The `RV-377-110` baseline stage (full alphabet, 20 000 evaluations, the four rule-40
discriminating ecologies) produced a result that is, on its face, a **positive for GMI** —
and therefore the one to attack hardest.

| ecology | DENSE | KVSTORE | NONE | PROGRAM | TABLE |
|---|---|---|---|---|---|
| `E_smooth1` | 0.8333 | **0.8958** | 0.8333 | **0.8958** | **0.8958** |
| `E_smooth3` | 0.8125 | **0.8958** | 0.8125 | **0.8958** | **0.8958** |
| **`E_sym5`** | **0.9115 ✓** | **0.8750** | 0.7917 | **0.9115** | **0.9115** |
| `E_wit1` | 0.7708 | **0.8802** | 0.4167 | **0.9531** | **0.9531** |

On `E_sym5` the neutral search **found a DENSE-carrier genotype at 0.9115** — the
coefficient carrier `D1`, recovered from primitives by a search with no architecture macro
in its alphabet.

`E_sym5|unseen` is `DISCRIMINATING` under rule 40 (best constant 0.7917), and 0.9115 beats
that constant by **2.875 fx units**. So this is not a non-discriminating artefact.

If it holds, it is **the first neutral recovery of the coefficient carrier on a rule-40
discriminating ecology in the entire corpus**, and G15 step (ii) — recovery by neutral
search — becomes reachable for the first time.

## Why it is probably wrong

`b1.main` scores under the **`standard` intervention only**. It has no intervention loop.
So 0.9115 is a single-intervention number and **rule 36 forbids calling it admissible
unqualified** — the exact defect that voided `RV-377-082`, `RV-377-088` and, this session,
`RV-377-111`.

The immediately relevant prior is hostile. `RV-377-111`, adjudicated an hour ago, found
`half_events` binding on **11 of 11** coefficient-carrier cells, and `GMI-DA9` names
`half_events` and `shuffled_events` as the two interventions that break coefficient rows.
This genotype is a coefficient carrier.

## The test

Extract the recovered `E_sym5` DENSE genotype from its receipt and score it under all six
registered interventions via `ecology.run_genotype`, which is the intervention-aware path.
Report the minimum. Apply rule 40's margin against the best constant (0.7917) **in fx
units**, and rule 42's requirement of a fixed-function null.

## Frozen predictions

| id | prediction | falsifier |
|----|-----------|-----------|
| V1 | **The recovered DENSE genotype FAILS under the six-intervention family** — min over six < 0.85. | min ≥ 0.85 |
| V2 | **`half_events` is the binding intervention**, per `GMI-DA9` and `RV-377-111`. | some other intervention binds |
| V3 | The `PROGRAM` and `TABLE` carriers on `E_sym5` (also 0.9115) **also fail** under the family — the failure is not specific to the coefficient carrier. | they survive while DENSE fails |
| V4 | **At least one carrier on at least one of the four ecologies survives all six.** Something in this table is real. | every carrier on every ecology fails |

V1 and V2 predict **against** the apparent positive. V4 is the prediction that gives GMI a
route to a genuine result, and it is the one I expect to be hardest.

If V1 is falsified — if the recovered coefficient carrier survives all six interventions —
that is a real and reportable positive for GMI, arrived at on a discriminating ecology by a
neutral search, and it will be recorded as such without hedging.

## Scope amendment to `RV-377-110`, recorded before the ablation stage runs

The freeze planned 33 ablations × 4 ecologies = 132 runs, sized from a measured 27.5 s per
2 000 evaluations (linear ⇒ ≈ 275 s per 20 000-evaluation run). **The measurement was
wrong**: the four baselines took **1 869 s each**, 6.8× the linear projection, because the
search slows as the MAP-Elites archive fills.

132 runs at 1 869 s with 4-way parallelism is ≈ 17 hours. The ablation stage is therefore
**reduced to one ecology, `E_wit1`** — 33 runs, ≈ 4.7 hours — chosen because it carries the
largest constant-control margin in the registry (3.401 fx units on `unseen`).

This is a **reduction in scope, declared with its reason and its cost measurement before
the run**, not a silent truncation. Its consequence is stated plainly: the resulting
irreducibility classification will hold for `E_wit1` only, and `RV-377-110`'s predictions
T3 and T4 are to be read at that scope. Extending to the other three ecologies is
registered as owed, not claimed.

`T1` and `T2` from `RV-377-110` are adjudicated by these baselines and appear in the
adjudication of that record.

---

# RV-377-113 — ADJUDICATION (appended; nothing frozen above was edited)

## Predictions, scored

| id | prediction | outcome |
|----|-----------|---------|
| V1 | the recovered DENSE genotype **fails** under the six-intervention family | **FALSIFIED** — min over six = 0.8542 ≥ θ. It survives. |
| V2 | `half_events` is the binding intervention | **CONFIRMED** — `half_events` binds on `E_sym5` DENSE |
| V3 | `PROGRAM` and `TABLE` on `E_sym5` also fail | **FALSIFIED** — both survive |
| V4 | at least one carrier on at least one ecology survives all six | **CONFIRMED** — 10 do |

I predicted the apparent positive would collapse under rule 36, on the strength of
`RV-377-111` an hour earlier. It did not. Recorded without hedging, as committed.

## Full result under all six interventions

| ecology | carrier | `standard` | min over six | binding | rule 36 | fx vs best constant |
|---|---|---|---|---|---|---|
| `E_smooth1` | KVSTORE | 0.8958 | 0.8542 | `half_events` | ✓ | 0.502 → **WITHIN_QUANTIZATION** |
| `E_smooth1` | PROGRAM | 0.8958 | 0.8542 | `shuffled_events` | ✓ | 0.502 → **WITHIN_QUANTIZATION** |
| `E_smooth1` | TABLE | 0.8958 | 0.8542 | `half_events` | ✓ | 0.502 → **WITHIN_QUANTIZATION** |
| `E_smooth3` | KVSTORE | 0.8958 | 0.8594 | `shuffled_events` | ✓ | 1.126 |
| `E_smooth3` | PROGRAM | 0.8958 | 0.8594 | `shuffled_events` | ✓ | 1.126 |
| `E_smooth3` | TABLE | 0.8958 | 0.8594 | `shuffled_events` | ✓ | 1.126 |
| **`E_sym5`** | **DENSE** | **0.9115** | **0.8542** | `half_events` | **✓** | **1.500** |
| `E_sym5` | KVSTORE | 0.8750 | 0.8542 | `half_events` | ✓ | 1.500 |
| `E_sym5` | PROGRAM | 0.9115 | 0.8542 | `half_events` | ✓ | 1.500 |
| `E_sym5` | TABLE | 0.9115 | 0.8542 | `half_events` | ✓ | 1.500 |
| `E_wit1` | KVSTORE | 0.8802 | 0.8333 | `extra_unseen_feedback` | ✗ | — |
| `E_wit1` | PROGRAM | 0.9531 | 0.8333 | `shuffled_events` | ✗ | — |
| `E_wit1` | TABLE | 0.9531 | 0.8333 | `shuffled_events` | ✗ | — |

## Rule 42 — the fixed-function null, extractor validated first

Per rule 42 the extractor was validated on a known inert row and a known learner
**before any witness was read**:

```
known inert  constant_emitter : 1 distinct final-answer vectors over 5 targets
known learner                 : 5 distinct
extractor VALID: True
```

Every one of the 13 admissible carriers then reads `distinct = 5/5 → LEARNS`. None is a
fixed function. `E_sym5 | DENSE` learns.

## G15 STEP (ii) IS REACHED

`E_sym5 | DENSE` clears **every** control the corpus has:

| control | requirement | result |
|---|---|---|
| rule 36 | admissible under all six registered interventions | **0.8542 ≥ 0.85** ✓ |
| rule 40 | separates from the best constant by ≥ 1 fx unit | best constant 0.7917, **1.500 fx units** ✓ |
| rule 42 | passes the constant-answer AND fixed-function nulls | 5/5 distinct, **LEARNS** ✓ |
| rule 45 / DG-12 | the obligation is not degenerate | `E_sym5|unseen` **NON_DEGENERATE** (`RV-377-112`) ✓ |

> **The coefficient carrier `D1` is recovered from primitives by a neutral search with no
> architecture macro in its alphabet, on a rule-40 discriminating ecology, robust to every
> registered intervention, and it demonstrably learns.**
>
> **`G15_STEP_TWO_REACHED` = TRUE at registered scope.** This is the first time in the
> corpus. `RV-377-108` recorded step (ii) as FALSE and "never tested at non-zero
> exposure"; it is now tested, and it holds.

Seven carrier recoveries clear every control: `E_sym5` × 4 (including DENSE) and
`E_smooth3` × 3.

## What this does NOT establish — the counterweights, stated plainly

**One seed, one column, one budget.** Seed 0, column `B0_LOCAL_ADAPTIVE_TRANSDUCERS`,
20 000 evaluations. Not swept. Under rule 38/39 this is a point claim, and by `GMI-DA11`
monotonicity protects point positives — but a *rate* still needs the sweep.

**The margin is 1.5 fx units.** It clears the one-fx-unit floor and is not large. A
different seed could plausibly land below it.

**The carrier descriptor is not identity.** `b1`'s own claim ceiling applies: recovery means
an admissible genotype whose served answer *reads* that carrier, not that the recovered
machine equals any registered row.

**The recovery is ecology-specific, and fails where it was most expected.** On `E_wit1` —
the ecology `RV-377-102` constructed *specifically* to host a coefficient witness — DENSE
is **not** recovered at all (0.7708, inadmissible), and all three carriers that are
admissible there fail rule 36. The ecology built to make this easy is the one where it
does not happen.

**`E_smooth1`'s three carriers are not separations.** They pass rule 36 but sit
**0.502 fx units** above the best constant — below the quantization floor. Rule 40 forbids
calling them separations, and they are excluded from the count of seven.

**`p(D1)` is still not estimable.** `RV-377-108`'s selection-effect argument is untouched:
one success on one ecology, reached without a denominator drawn independently of whether a
witness exists there, does not give an unbiased rate. G15's *stopping rule* remains
inapplicable even though step (ii) is now reached.

## Terminal changes

| terminal | was | now |
|---|---|---|
| `G15_STEP_TWO_REACHED` | FALSE | **TRUE at registered scope** |
| `P_MIN_LOWER_BOUND_EXISTS` | FALSE | **FALSE** — unchanged |
| `DOMAIN_LIST_COMPLETE` | BLOCKED | **BLOCKED** — unchanged |
