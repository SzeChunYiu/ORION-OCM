# AE10 named results

Registered scope is `FREEZE_V1.md`. Exact rational arithmetic throughout.
Route A is `ae10_usable_information_v1.py`; route B is
`independent_usable_oracle_v1.py`; they agree on every value.

## Definition D-AE10 (usable information)

For a registered world `W`, a task specification `T` and a budget `R` of the
frozen lattice,

    U(W, T, R) = max over rules admissible at R of the expected score
                 -  the best score achievable with no observation.

The frozen lattice is the componentwise product of

- `k`, junta arity: how many coordinates a rule may read;
- `d`, decision-tree depth: the rule's branching budget;
- `m`, labelled-sample budget: how many examples the learner gets to identify
  the target;
- `p`, observation precision: how many leading coordinates are visible;
- `c`, communication: how many bits the rule may pass to its decision stage.

`U` is defined by the rule class and the task, never by an architecture.
**Time and energy are declared dimensions of the lattice and are NOT
instantiated in v1.** No claim in this package depends on them; the receipt
records this explicitly rather than letting the omission pass silently.

The decoder-side lattice has **128** cells. `c` is verified **non-binding** for
a binary target — `communication_is_binding` returns false for every registered
world — and that verification is a test, not an assumption, because the
detector's notion of `below the top` depends on it.

---

## USE-1 — monotonicity

**Statement.** `R <= R'` implies `U(W, T, R) <= U(W, T, R')`.

**Proof.** The admissible rule class is nested: a rule reading at most `k`
coordinates within the top `p`, computable at depth at most `d`, is also
admissible at any componentwise larger budget. A maximum over a larger set is
at least the maximum over a subset.

**Verification.** All **3,000** ordered budget pairs per world across all
**3** registered worlds — **9,000** ordered pairs — with **0** violations. The
rule-class inclusion itself is checked separately, so the premise of the proof
is verified and not merely the conclusion.

**Falsifier.** Any ordered pair with a strictly larger value at the smaller
budget.

---

## USE-2 — the full-information ceiling

**Statement.** `U(W, T, R) <= gain(W, T)` for every `R`, where `gain` is the
unrestricted Bayes optimum minus the blind optimum, with equality at the top of
the binding dimensions.

**Verification.** **0** violations across the whole lattice and all registered
worlds; equality at `k3_d3_p3_c2` holds for every registered world.

**Falsifier.** Any budget whose restricted optimum exceeds the unrestricted one.

**Strongest parents.** The data-processing inequality and the rate-distortion
ceiling; nothing new is claimed.

---

## USE-3 — equal Shannon information, different achievable performance

**Decoding cost.** `W_PARITY3` (`Y = x_0 xor x_1 xor x_2`) and `W_DICTATOR`
(`Y = x_2`) both have `Y` determined by `X` with a uniform `Y`-marginal, so
`I(X;Y) = 1` bit **exactly** for both, by a counting argument with no logarithm
evaluated. At the identical budget `k1_d1_p3_c2`,

    U(W_PARITY3) = 0        U(W_DICTATOR) = 1/2        difference = 1/2.

The difference is attributable to decoder branching cost alone: the information
content is identical, the observation is unrestricted, and only the decoder's
depth budget separates them.

**Search cost.** Here the mutual information is identical **by identity**, not
by coincidence: one fixed world — `Y = <s, x>` with `s` uniform over the seven
nonzero secrets of `GF(2)^3` — is held constant while only the sample budget
`m` varies. The Bayes-optimal expected accuracy is

| `m` | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| accuracy | `5/8` | `43/64` | `383/512` | `3463/4096` |

strictly increasing, for a total move of `903/4096` with the world's
information content unchanged throughout.

Route A derives this curve from a closed-form `GF(2)` coset argument: the
consistent secrets form `s + K` with `K = V^perp` for `V` the span of the
training inputs, so a test point inside `V` is labelled identically by every
consistent secret while outside `V` the coset splits evenly, the only asymmetry
being the exclusion of the zero secret. Route B enumerates every
`(secret, training tuple, test point)` and scores the posterior majority
directly. They agree exactly at every `m`.

An auxiliary comparison against a two-candidate family is reported and
**explicitly labelled as not an equal-Shannon comparison**, since a different
candidate set is a different world.

**Falsifier.** A rule at `k1_d1_p3_c2` beating the base rate on `W_PARITY3`, or
a learner beating the tabulated accuracy at some `m`.

---

## USE-4 — an unconditional pseudorandom-style fixture

**Statement.** For every one of the `7` proper subsets `S` of the coordinates,
the pair `(x_S, y)` is exactly uniform on `{0,1}^(|S|+1)` — **0** violations.
Consequently any rule that effectively reads only a proper subset has exactly
zero correlation with the target, and

    U(W_PARITY3, k=2, d=3, p=3, c=2) = 0,
    U(W_PARITY3, k=3, d=3, p=3, c=2) = 1/2.

**Defensible scope.** The separation is **unconditional**. No cryptographic
hardness assumption is invoked, and the receipt records
`cryptographic_assumption_used: false` and
`is_a_complexity_class_separation: false`. It is therefore strictly weaker than
an HILL-pseudoentropy statement, and stronger in the sense of needing no
conjecture.

**Forbidden extrapolation.** This is not a complexity-class separation, not a
hardness assumption, and not evidence about any cryptographic primitive.

---

## USE-5 — terminology crosswalk

Four entries, each with a citation, mapping `U` onto what already owns it:
predictive V-information (Xu et al., ICLR 2020) — of which `U` is an instance
with `V = H_R` and 0-1 loss; bounded rationality and resource-rational analysis
(Simon 1955; Lieder and Griffiths 2020) for the resource axis; HILL
pseudoentropy (Hastad et al. 1999) for the information-exists-but-is-not-
extractable phenomenon; and the data-processing / rate-distortion ceiling
(Cover and Thomas 2006) for USE-2. No duplicate terminology is introduced
without an entry.

---

## Null and detector validation

Detector: `Y` determined by `X` with a uniform `Y`-marginal — one exact bit of
Shannon information — together with zero usable information at every budget
outside the top face of the binding dimensions `(k, d, p)`, with `c` first
verified non-binding.

- recall: fires on the planted positive `W_PARITY3`;
- no-alarm: does **not** fire on `W_DICTATOR` or `W_XOR2`;
- null: `0` of `200` random deterministic worlds from a deterministic integer
  LCG are flagged.

An earlier version of this detector excluded only the single lattice cell
`(3,3,3,2)` rather than the top face, and consequently failed on its own
planted positive. That was a mis-specified detector, diagnosed and corrected
before any result was reported, not a tuned threshold.

## Row NOT closed here

> Determine whether GMI morphology selection is better predicted by raw
> information, usable information, or a vector of resource-conditioned
> sufficient statistics.

This requires pinned GMI morphology-selection receipts and is deferred to the
morphology sweep package described in
`research/gmi-833-ae-section-map-v1/AE_SECTION_MAP_V1.md`. It is recorded in
the `not_closed` block of the reconciliation.

## Forbidden extrapolations

`MUTUAL_INFORMATION_SUFFICIENT_FOR_INTELLIGENCE`,
`CRYPTOGRAPHIC_HARDNESS_ASSUMED`, `COMPLEXITY_CLASS_SEPARATION`,
`ENERGY_BUDGET_MEASURED`, `TIME_BUDGET_MEASURED`,
`GMI_MORPHOLOGY_PREDICTION`, `ARCHITECTURE_SELECTION_LAW`,
`NOVEL_INFORMATION_MEASURE`, `COMPLETE_GMI`.
