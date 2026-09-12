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
