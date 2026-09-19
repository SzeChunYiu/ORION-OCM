# Z3 freeze amendment 1 — the null caught the frozen detector, and the instrument
# hypothesis was confirmed against it

Committed **before** the receipt carrying the revived numbers. `git log` must show
this file added no later than `RESULT_V1.json`.

Two things the freeze asked to be checked turned out the way the freeze warned
they might, and both are recorded here rather than absorbed into a green run.

## 1. The frozen null detector is not complete: `197/200`

The freeze registered the null as `200` seeded `H1_PSEUDO_RENAME` instances, each
to be **detected** by observing a changed winner class set on at least one of the
`60` registered worlds, with the explicit instruction that survivors be
characterized exactly and the detector revived rather than the result reported
green.

The frozen verdict-level detector catches `197/200`. Three survive.

**Exact characterization, verified and not asserted.** All three survivors hold
the true stateless optimum error pair `(0, 8)` among the `16` identifiers the
pseudo-rename moves into the declared-stateless slots. The executor verifies, for
each survivor and each of the `60` worlds, that the minimum risk over its `16`
slot pairs equals the minimum risk over the true stateless family — `60/60` in
every case. Because the stateful side still contains `(0, 0)`, neither
class-restricted minimum moves, so no verdict can move. The blindness is a
property of the **verdict statistic**, not of the transformation: a winner class
set is a coarse observable, and a transformation that changes the population
without changing either class minimum is invisible to it.

## 2. The revival, using evidence the frozen design already contained

The registry entry for `T1_RENAME` frozen in `FREEZE_V1.md` states that under a
genuine rename *`sigma` travels with the candidate*, and the invariance check
already verifies that the multiset of `(bits, e_now, e_delay)` is preserved — on
the clean case, where it holds `200/200` with zero breaks.

A pseudo-rename, by construction, moves error vectors across the declared-bits
boundary and therefore changes that multiset. Applying the **already frozen**
multiset invariant to the hostile is not a new assumption and not a new
instrument: it is the registered definition of the transformation being used as
the test.

Revived detector: `200/200` detected, `0/200` surviving.

Both numbers are published. The receipt carries `frozen_detector_detected = 197`
and `revived_detector_detected = 200` side by side, and the gate requires the
revived detector to be complete **and** the frozen detector's survivors to be
characterized.

## 3. The syntactic dead-padding count undercounts, as the freeze hypothesised

`FREEZE_V1.md` registered `4096` as the *table-ignores-state* subfamily and
flagged it as *a hypothesis about the instrument*: if the true behavioural census
exceeds it, the syntactic definition undercounts the adversarial family and the
undercount must be recorded as an instrument failure with its repair.

Measured: `12544` behaviourally stateless declared-stateful candidates, of which
`8448` are **not** in the table-ignores-state family. The syntactic count
undercounts by a factor of `3.0625` exactly (`12544/4096 = 49/16`).

**Repair.** The adversarial family is defined behaviourally — identical
`48`-symbol output trace — and never syntactically. Both routes compute it
independently: route A by trace comparison, route B by a reachability closure
that asks whether the output is constant over every occupiable state. They agree
on `12544`.

## Nothing else in the freeze changes

The claim ceiling, the rows, the registry, the hostiles, the forbidden
promotions and the two-route requirement are unchanged.
