# AE7 named results v1

Every result below is stated at the **registered finite scope** of
`FREEZE_V1.md`: `8` latent states with a uniform exact prior `1/8`, all
`Bell(8) = 4140` sensors (set partitions of the state set), `6` registered
prediction targets, `4` registered utilities over `4` actions, and a `33`-point
exactly rational sensing-price ladder. All arithmetic is `Fraction` or `int`;
no float and no logarithm appears anywhere.

---

## PC-1 — predictive content does not determine control value

**Statement.** There exist two sensors whose *predictive profiles* — the
multiset over blocks of (block mass, conditional law of each registered target)
— are equal cell by cell as exact rationals, and whose achievable control values
under a registered utility differ by exactly `1/2`.

**Quantifiers.** Existential over sensors, for a *named* utility; universal over
the registered target suite (the profiles agree for **every** registered
target). Census: **10,980** such pairs among the `4140 × 4139 / 2` ordered-free
pairs, across **712** distinct profiles.

**Why the profile is the right object.** The expected score of any predictor
under any loss is a function of the sensor only through this multiset.
Equality of profiles therefore means the two sensors are indistinguishable by
*every* registered prediction task, not merely by the ones that were tried.

**Assumptions.** Finite state set; uniform prior; deterministic targets;
expected-utility control with a finite action set.

**Falsifiers.** A sensor pair with equal profiles and equal control value for
*every* utility — the receipt reports exactly this case for
`U_visible_coordinate`, where the count is `0`, so the claim is known to be
utility-dependent and is not stated unconditionally.

**Strongest parents.** Belief-state sufficiency for POMDPs (Åström 1965;
Smallwood & Sondik 1973); the observation that prediction and control impose
different sufficiency requirements is parent-owned.

**Forbidden extrapolations.** `PREDICTION_INSUFFICIENT_FOR_INTELLIGENCE_IN_GENERAL`.
What is proved is insufficiency **at the registered scope**, not a claim about
intelligence as such.

---

## PC-2 — control sufficiency, its coarsest witnesses, and the Helly failure

**Statement.** `T` is control-sufficient iff `V(T) = V_full`. The set of
control-sufficient sensors is upward closed under refinement; its minimal
elements are computed exhaustively. For the four registered utilities there are
**225, 225, 208, 221** control-sufficient sensors and **1, 1, 3, 8** minimal
ones. A block is free — mergeable at no control cost — **iff** the intersection
of its states' optimal-action sets is non-empty; this criterion agrees with the
exact value function on every pairwise merge (`0` mismatches).

**Non-locality (the sharp part).** Mergeability is **not** a pairwise property.
Under `U_helly_triple` the states `0, 1, 2` are pairwise compatible
(`{a0,a1} ∩ {a1,a2} ≠ ∅`, etc.) yet have empty triple intersection, so a
pairwise checker declares the block free when it is not. Exactly **1** such
triple exists in the registered problem and it is exhibited.

**Quantifiers.** Universal over the 4140 sensors and the 28 state pairs;
existential for the Helly witness.

**Falsifiers.** A control-sufficient block whose states share no optimal
action; a pairwise-compatible block that *is* free. Neither occurs.

**Strongest parents.** MDP bisimulation and model minimisation (Givan, Dean &
Greig 2003); state aggregation. `PARENT_SUFFICIENT` on the sufficiency notion.

**Forbidden extrapolations.** `CONTROL_SUFFICIENCY_IMPLIES_PREDICTIVE_SUFFICIENCY`
and its converse; both are refuted at this scope and neither may be promoted to
a general law.

---

## PC-3 — strongest-parent audit

**Statement.** Every symbol this package introduces maps onto a named parent
with a DOI; **3** of the **5** crosswalk entries terminate `PARENT_SUFFICIENT`.

**Residual, named.** The exhaustive exact-rational census over all 4140 sensors
that counts the separation **in both directions**, the Helly failure, and the
priced ladder with prospectively frozen predictions. Nothing else is claimed
novel.

**Forbidden extrapolations.** `POMDP_BELIEF_SUFFICIENCY_REPROVED`.

---

## PC-4 — the value-of-information threshold is exact and two-sided

**Statement.** For comparable sensors `T ⊒ T'`, acquiring `T` is optimal iff
`V(T) − V(T') > price · (cost(T) − cost(T'))`. Over **163,754** comparable
pairs, **26,790** have value of information exactly `0` and **136,964** strictly
positive; the break-even prices form **71** distinct exact rationals in
`[0, 9/64]`.

**Both sides and the tie.** For the full-versus-blind probe the break-even is
`9/448`; below it the fine sensor strictly wins, at it the two are exactly
equal, above it the blind sensor strictly wins. The tie is reported rather
than skipped, because a threshold claim that never exhibits its equality case
has not been tested at the boundary.

**Falsifiers.** A comparable pair whose chosen sensor flips at a price outside
the computed break-even; a pair with positive value of information at zero cost
increment that is nonetheless not acquired.

**Strongest parents.** Howard 1966. `PARENT_SUFFICIENT` on the quantity.

---

## PC-5 / PC-6 — the two directions, both attested with counts

**PC-5.** Distinctions to which the optimal action is insensitive may be merged
at zero cost: **12, 12, 13, 14** free state pairs for the four utilities.

**PC-6.** The converse. **4** state pairs are invisible to **all 6** registered
targets — no registered prediction task can see them — and **4 of 4** are
strictly control-relevant under `U_hidden_coordinate`: merging `{0,4}` drops `V`
from `1` to `7/8`. Under `U_visible_coordinate` the count is exactly **0**.

**Boundary, measured not assumed.** Enlarging the target suite does not
automatically destroy the witness. `Y_b2` and `Y_parity` destroy it completely
(`0` surviving pairs); `Y_majority` leaves **2**, because on the four states
with `b0 = b1` the majority is pinned by `b0` and the hidden coordinate remains
invisible. The asymmetry is the content of the boundary.

**Falsifiers.** A predictively redundant pair that is control-free under every
registered utility (this occurs and is reported: `U_visible_coordinate`); a
target suite extension under which the count does not change (this occurs and
is reported: `Y_majority`).

**Forbidden extrapolations.** `PREDICTIVE_SUFFICIENCY_IMPLIES_CONTROL_SUFFICIENCY`.

---

## PC-7 — five prospectively frozen predictions, all HELD

The predictions `R1`–`R5` were written into `FREEZE_V1.md` at commit
`65b45210b0cca60dba37d36fd556c8846fa3232f`, before any executor, oracle, test or
receipt blob of this package existed in the tree; the workflow proves that
ordering by asserting that none of those paths resolves at the freeze commit.

| id | prediction | outcome |
|---|---|---|
| `R1` | the chosen sensor coarsens monotonically in price, no re-refinement | **HELD**, `0` violations over 33 prices × 4 problems |
| `R2` | some problem shows ≥ 3 distinct selected sensors | **HELD**, `2` problems |
| `R3` | every transition price is bracketed by a difference quotient of the registered family | **HELD**, `0` outside a **121**-element exact set |
| `R4` | above the maximal gain the blind sensor is selected everywhere | **HELD**, `0` failures |
| `R5` | the priced control order is not the predictive order | **HELD**, `4 of 4` problems |

**Non-vacuity.** `R1` would hold trivially if the chosen sensor never moved.
Every registered problem changes its sensor at least once and two change twice,
and the test asserts this, so the monotonicity claim has something to be
monotone about. A hostile with an inverted sensing cost breaks `R1`, proving
the check has teeth.

**Falsifiers.** Any re-refinement as the price rises; a transition price
outside the difference-quotient set; a problem that keeps a non-blind sensor
above the maximal gain.

**Forbidden extrapolations.** `ENERGY_OR_TIME_PRICE_MEASURED` — the price is a
declared abstract resource unit, not a measured energy or wall-clock cost;
`ARCHITECTURE_SELECTION_LAW`; `GMI_MORPHOLOGY_PREDICTION`.
