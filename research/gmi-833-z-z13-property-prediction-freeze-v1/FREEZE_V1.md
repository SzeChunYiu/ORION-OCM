# GMI #833 Section Z / Z13 — a property-first prediction, frozen for a later lane

## THIS IS NOT A CLOSURE

This artifact **closes no row**, names no row as reconciled, and appears in no
`replacements[]` entry of any reconciliation JSON. It is a prospectively frozen
prediction, committed so that a **later, separate lane** can adjudicate it
without the adjudication being written by the lane that made the prediction.

Row 1 of `### Z13` asks to "Freeze a property-first prediction for an unobserved
morphology from theory alone." Freezing the prediction and scoring it inside the
same package is the `POST_HOC_SUSPECT` pattern that audit #976 filed, and rows
`9`, `10` and `11` of `Z13` additionally require prospective niche
demonstration, a matched negative ecology and **independent** replication —
none of which the producing lane can supply for itself. All twelve `Z13` rows
and all six `Z16` rows are therefore listed as `not_closed` in this lane's
reconciliation, with that reason.

- `source_main`: `5e57d4292266bccf435136e1f7d72caa32e920a0`
- branch: `research/833-sec-z3`
- committed before any executor, search or outcome for this prediction exists

## 1. Where the prediction comes from

`research/gmi-833-z-z6-discrimination-v1` established, over `404` registered
worlds, that the selection boundary is

```
lambda* = eta * p * R0
```

where `R0` is the minimum delayed-channel error rate attainable **without**
state under the environment's own input law, and that the registered
`lambda* = eta*p/2` is the uniform-input case of it. `R0` is a property of the
*task-and-input pair*, not of any architecture.

That law is stated for a one-bit budget and a two-channel task. It has a
consequence for a budget it was never fitted on, and that consequence is the
prediction below. Nothing about the extended universe has been enumerated.

## 2. The frozen prediction `Z13-P1`

**Extended universe (declared now, not yet enumerated).** State budget
`b in {0, 1, 2}`; three task modes — immediate copy, delay-1 recall, delay-2
recall — over input sequences of length `L = 4`, uniform independent bits,
canonical initial state `0`. Declared cost

```
C = eta * ( p0 * r_now + p1 * r_delay1 + p2 * r_delay2 ) + lambda * b
```

with `p0 + p1 + p2 = 1`.

**Prediction, property-first — no family name, no template.** The theory
predicts that state is bought **one bit at a time**, at two distinct prices

```
lambda_1* = eta * p2 * R0(delay2 | b = 1)  +  eta * p1 * R0(delay1 | b = 0)
lambda_2* = eta * p2 * R0(delay2 | b = 1)
```

and therefore that there exists a morphology occupying the **intermediate
cell**: exactly one state bit, the delay-1 channel solved at zero error, and the
delay-2 channel left at its one-bit floor. Its declared properties, stated
without naming any family:

- `P-a` its output depends on both the state and the current input, and on
  neither alone in a way that makes the other redundant;
- `P-b` its next-state function is the current input (a one-step shift register
  in behaviour, not in name);
- `P-c` at `b = 1` it attains `r_now = 0` and `r_delay1 = 0` simultaneously,
  while `r_delay2` sits strictly above `0` and at the exact one-bit floor;
- `P-d` no member of the six registered named families of the `L = 3` universe
  (`F_STATELESS`, `F_DEAD_TABLE`, `F_FROZEN_STATE`, `F_MOORE`, `F_MEALY_PURE`,
  `F_IDENTITY_STATE`), lifted to the extended universe, simultaneously satisfies
  `P-a`, `P-b` and `P-c` **and** is the unique cost minimiser somewhere in the
  predicted niche.

**Predicted niche, frozen before any test.** The intermediate morphology is the
unique property-class minimiser exactly on

```
lambda_2*  <  lambda  <  lambda_1*
```

and nowhere else; below `lambda_2*` the two-bit class wins and above
`lambda_1*` the stateless class wins.

**Matched negative ecology, frozen now.** At `p2 = 0` — the delay-2 channel
unpriced — the interval `(lambda_2*, lambda_1*)` collapses and the intermediate
morphology must lose its advantage everywhere. A lane that finds it still
dominating at `p2 = 0` has falsified `Z13-P1`.

## 3. How a later lane must adjudicate it

1. Build the extended universe exhaustively with exact integer error counts and
   `fractions.Fraction` costs. Record its size.
2. Compute `R0(delay1 | b = 0)`, `R0(delay2 | b = 1)` and both thresholds
   exactly, then locate the true property-class minimiser on a swept `lambda`
   grid straddling both.
3. Score `P-a` through `P-d` and the niche statement. `Z13-P1` is **HIT** only
   if all four properties hold of the minimiser on the whole predicted interval
   **and** the matched negative ecology behaves as frozen.
4. Publish the verdict either way. A miss is a result and must be filed in a
   failed-prediction register, not repaired into a hit.
5. `Z13` rows `4`, `5`, `11` (remints, independent search algorithms,
   independent replication) still require work this artifact does not supply,
   and `Z16` cannot close before `Z13` produces an adjudicated result.

## 4. Custody

This file is the whole artifact. There is no executor, no receipt and no
outcome in this package, by design: its value is exactly that it was written
before anyone looked.

Forbidden promotions:

```
Z13_ROW_CLOSED_BY_THIS_ARTIFACT
Z16_ROW_CLOSED_BY_THIS_ARTIFACT
UNSEEN_MORPHOLOGY_DISCOVERED
W4_STATUS_CLAIMED
PREDICTION_ADJUDICATED_BY_ITS_OWN_LANE
```
