# Z8 named results

Scope is fixed by `FREEZE_V1.md`: the three-mode binary transducer universe
(`L = 4`, uniform i.i.d. inputs unless an ingredient changes the law, initial
state `0`, `b ∈ {0,1,2}`, window `{2,3}`), the `135`-world grid
`η ∈ {1,2,3}` × `(p0,p1,p2)` over eighths, the price grid `{j/16 : j = 0..24}`,
and the two-level delay-1 population under the seven registered input laws.
Exact rational arithmetic throughout; both routes agree on every number below.

The registered law built on is `IC-1` / `λ* = ηp·R0` (thresholds are marginal
error masses, supporting slopes of the lower convex envelope); `λ* = ηp/2` is
retired and appears only as the input-law-blind competitor.

---

## `ZH-1` — the verdict-move matrix: every ingredient moves a registered verdict or is proved unable to

| ingredient | `V_SEL` | `V_NICHE` | `V_THR` | `V_FAIL` |
|---|---|---|---|---|
| `I1` near-ties | MOVES `132/135` worlds (`204` tie cells) | UNABLE (price-independent) | UNABLE (price-independent) | via `V_SEL` |
| `I2a` uniform verifier noise | MOVES `179 / 348 / 637` cells at `ε = 1/16, 1/8, 1/4` | **UNABLE** (`ZH-2`), `135/135` at each `ε` | MOVES `132/135` | MOVES `135/135` worlds |
| `I2b` delay-2-only noise | MOVES | MOVES `3 / 6 / 12` worlds at the three `ε` | MOVES `108/135` | MOVES |
| `I2c` verifier failure (window `{3}`) | MOVES `81/135` worlds | MOVES `12/135` | MOVES `108/135` | MOVES `65/135` |
| `I3` causal aliasing (period-2 law) | MOVES `108/135` | MOVES `12/135` | MOVES `108/135` | MOVES `108/135` |
| `I4a` distribution shift (two-level) | MOVES `2612/33075` cells | n/a at two levels | MOVES on every pair with `R0(q) ≠ R0(q')` | via `V_SEL` |
| `I4b` in-window nonstationarity | moves the stateless floor on `42/49` pairs | n/a | MOVES | via `V_SEL` |
| `I5a` affine accounting `ρ = 2b+1` | **UNABLE** with the matching price (`0` cells) | **UNABLE** (`ZH-2`) | UNABLE (raw pair is accounting-free) | UNABLE |
| `I5b` state-count accounting | MOVES `216` cells, `100` worlds | MOVES `36/135` | UNABLE | MOVES `96` worlds |
| `I5c` concave accounting | MOVES `516` cells, `131` worlds | MOVES `24/135` | UNABLE | MOVES `126` worlds |
| `I6a` history-weighted mixture | MOVES `11264/151875` cells; a shared level is **never** dropped (`134907/134907`) | n/a | n/a | via `V_SEL` |
| `I6b` hysteresis `κ ∈ {1/32, 1/8}` | MOVES `2003 / 5069` of `50625` cells | n/a | n/a | via `V_SEL` |
| `I7a` Moore grammar | **UNABLE** (constant shift, `0` cells) | **UNABLE** (`0/135`) | **UNABLE** (`0/135`) | MOVES `108/135` |
| `I7b` input-only grammar | MOVES `625` cells, `108` worlds | MOVES `12/135` | MOVES `108/135` | MOVES `108/135` |
| `I7c` relabelling (state / input, with the task) | **UNABLE** (bijection) | UNABLE | UNABLE | UNABLE |
| `I8` single-start descent | MOVES `86/135` worlds | MOVES `12/135` | MOVES `108/135` | MOVES `108/135` |
| `I8` seeded hill-climb | UNABLE (attains `9/9` floors) | UNABLE | UNABLE | UNABLE |
| `I9` freeze before scoring | protocol: custody by git order; hostile world set `1399` entries, one `sha256` | | | |

**Quantifiers.** For all `135` worlds and all `25` prices of the declared grids, and for the declared parameter ladders of each ingredient.

**Assumptions.** The declared additive cost with a linear price on the declared resource map; exact rational floors re-enumerated in both routes; hostile ground truth recomputed under the modified universe.

**Dependencies.** The nine registered base floors; `ZH-2`, `ZH-3`; both route receipts.

**Falsifiers.** An ingredient row whose every cell reads UNABLE without a theorem; a UNABLE cell contradicted by one moved world; disagreement between the routes on any count.

**Strongest parents.** The mechanisms are owned upstream: `gmi-833-history-switching-hysteresis-v1` (`HIST-1`, `HIST-2`), `gmi-833-search-law-morphology-change-v1` (`SLM-1`..`SLM-6`), `gmi-833-g0-grammar-bias-v1` (`RELABEL-2`), `gmi-833-capability-predictor-v1` (`FM_ALIASING`), `gmi-833-capability-predictor-evaluation-v1` (`KE-7`), `gmi-833-z-z5-critical-phenomena-v1` (`CP-3`), `gmi-833-z-z6-discrimination-v1` (`DS-4`, `DS-5`); see `PARENT_DISCLOSURE_V1.md`. None of them measures a verdict move on the three-mode ladder; that is this package's residual.

**Forbidden extrapolations.** `INGREDIENT_COUNTED_AS_EARNED_WITHOUT_A_MOVED_VERDICT_OR_A_THEOREM`; `HOSTILE_WORLD_RESULTS_EXTENDED_BEYOND_L4_B2_THREE_MODE_SCOPE`.

---

## `ZH-2` — affine maps of the profile cannot move the niche verdict

Let `E' = a·E + c` on every level with `a > 0` (uniform verifier noise:
`a = 1 − 2ε`, `c = ηε`; affine re-accounting `ρ' = a·ρ + c` is the same
statement on the resource axis). The lower convex envelope of `{(ρ(k), E'(k))}`
has the same vertex set as that of `{(ρ(k), E(k))}`, so `V_NICHE` is invariant;
every supporting slope scales by `a` (or `1/a`), so `V_SEL` is invariant under
the matching price map and `V_THR` scales. Verified exhaustively: uniform noise
leaves `V_NICHE` unchanged in `135/135` worlds at each of three `ε`, with the
affine identity `E' = (1−2ε)E + ηε` checked exactly; affine re-accounting with
`λ' = λ/2` moves `0` of `3375` price cells.

The theorem is sharp: channel-selective noise is **not** affine on the profile
(it reweights `p2 → (1−2ε)p2`), and it moves `V_NICHE` in `3, 6, 12` worlds —
exactly the worlds with `4p1 ≤ p2 < 4p1/(1−2ε)`, as frozen; a non-affine
monotone map `r ↦ r²` moves it in `36` (hostile `HX4`).

**Quantifiers.** For all `a > 0`, `c`, all profiles; verified on all `135` worlds at `ε ∈ {1/16, 1/8, 1/4}` and under `ρ = 2b+1`.

**Assumptions.** Noise acts identically on every channel's error indicator (uniform case); the resource map is re-priced by the matching factor (affine case).

**Dependencies.** Convexity of the envelope under positive affine maps; the base floors.

**Falsifiers.** One world where uniform noise or affine re-accounting changes the vertex set.

**Strongest parents.** Positive affine invariance of argmins (Z6 `DS-6`; Z3 `IV-3` for `(η, λ) → (cη, cλ)`); Everett 1963 on Lagrangian scalarisation.

**Forbidden extrapolations.** `VERIFIER_NOISE_CLAIMED_TO_MOVE_THE_NICHE_VERDICT_WITHOUT_CHANNEL_SELECTIVITY`; nothing is claimed for non-affine noise models.

---

## `ZH-3` — five ingredients move the niche verdict in the same twelve worlds, and why

With the delay-1 floors `(1/2, 0, 0)` and now-channel floors constant across
levels, level `1` is an envelope vertex iff

```
p1/2  >  p2 · σ2,     σ2 := 2·R0(1,2) − R0(0,2) − R0(2,2).
```

On the base ladder `σ2 = 5/8 − 1/2 − 0 = 1/8`, giving the registered `4p1 > p2`.
Each of the following drives `σ2` to `0`, so the niche becomes `p1 > 0` and
`V_NICHE` moves in exactly the `12` worlds with `4p1 ≤ p2` and `p1 > 0`
(`(p1, p2) ∈ {(1/8, 4/8), (1/8, 5/8), (1/8, 6/8), (1/8, 7/8)}` at each `η`):

| ingredient | delay-2 floors `(b=0, 1, 2)` | `σ2` | `V_NICHE` moved |
|---|---|---|---|
| `I2c` window `{3}` | `(1/2, 1/4, 0)` | `0` | `12` |
| `I3` period-2 law | `(0, 0, 0)` | `0` | `12` |
| `I7b` input-only grammar | `(1/2, 1/2, 1/2)` | `0` | `12` |
| `I8` single-start descent | `(1/2, 5/16, 1/8)` | `0` | `12` |
| `I2b` delay-2 noise `ε = 1/4` | `(1/2, 5/16, 0)` reweighted by `1/2` | `1/16` | `12` |

`I7a` (Moore) keeps `(1/2, 5/16, 0)` and therefore keeps `σ2 = 1/8`: it moves
nothing on the niche, which is exactly what `ZH-1` records. The state-count and
concave accountings move the niche by changing the *resource* axis instead
(`36` and `24` worlds, vertex rules `2Δ1 > Δ2` and `8p1 > 7p2`).

**Quantifiers.** For all `135` worlds and each listed floor set.

**Assumptions.** Delay-1 floors `(1/2, 0, 0)` and a level-constant now-channel, which every listed ingredient preserves.

**Dependencies.** `ZH-1`; the enumerated hostile floors of both routes.

**Falsifiers.** A listed ingredient whose moved-niche set is not the twelve-world set; a world with `σ2 = 0`, `p1 > 0` and an empty niche.

**Strongest parents.** The second-difference vertex criterion of `gmi-833-z-z13-adjudication-v1` `ZA-5` (`4p1 ≤ p2` as the repaired collapse condition) and `IC-1`.

**Forbidden extrapolations.** The twelve-world set is a fact about the eighths grid; nothing is claimed off the grid or at `L ≠ 4`.

---

## `ZH-4` — the frozen nonstationary floor is exact only on one side of `1/2` (EARNED BY COUNTEREXAMPLE)

Under `x_t ~ Bernoulli(q)` for `t < 2` and `Bernoulli(q')` for `t ≥ 2`, the
frozen stateless delay-1 floor `(R0(q) + R0(q'))/2` holds on `31/49` ordered
pairs — exactly the `31` pairs with `q` and `q'` on the same side of `1/2` —
and fails on all `18` opposite-side pairs (first witness `q = 1/5, q' = 4/5`:
frozen `1/5`, enumerated `1/2`). The mechanism: one output table serves both
scored moments and cannot switch its guess when the law crosses `1/2`; the
pooled Bayes error is `R0((q+q')/2)`, which is linear on each side of `1/2`.
That form reproduces `49/49` enumerated floors but was derived after the
enumeration and is **recorded, not scored** (`FAILED_PREDICTION_REGISTER_V1.json`
`P4b`).

**Quantifiers.** For all `49` ordered pairs of the seven registered laws.

**Assumptions.** Window `{2,3}`, `L = 4`, one stateless table shared across the window.

**Dependencies.** Full enumeration of the four stateless tables under each switched law (both routes).

**Falsifiers.** A same-side pair where the frozen average fails; an opposite-side pair where it holds.

**Strongest parents.** Bayes error under a mixture of conditionals; `gmi-833-ae-ae2-predictive-boundary-v1` (`DRIFT_INVERT`) for the nonstationary-source construct.

**Forbidden extrapolations.** `NONSTATIONARY_FLOOR_AVERAGE_STATED_ACROSS_THE_HALF_POINT`; `FROZEN_PREDICTION_REPAIRED_INTO_A_HIT_AFTER_A_MISS`.

---

## `ZH-5` — three frozen predictions miss on exact-tie cells, and the misses are published

`P1`: the `1/64` near-tie probe lands on the neighbouring marginal in the one
world where `Δ1 − Δ2 = 1/64` (`η = 1, p = (1/2, 1/8, 3/8)`), returning the tie
set `{1,2}` where `{1}` was frozen. `P4a`: `908` of the `2612` moved shift cells
lie *outside* the frozen "strictly between" band — every cell where the price
equals exactly one threshold and one side's verdict is the tie set. `P6b`:
`865` hysteresis cells move with excess exactly `0`, because an incumbent
inside a current tie set replaces a set verdict by a singleton. All three are
verdicts about **sets** at exact ties — the object `I1` exists to expose — and
the frozen sentences quantified as if verdicts were singletons. None is
repaired into a hit; the verdict-move matrix (`ZH-1`) is unaffected by any of
them.

**Quantifiers.** For the declared grids of `I1`, `I4a`, `I6b`.

**Assumptions.** `V_SEL` is a set, as `FREEZE_V1.md` §1 defines it.

**Dependencies.** `ZH-1`; the register.

**Falsifiers.** A miss missing from the register, or a register entry whose numbers are not reproducible from the receipt.

**Strongest parents.** The Z13 and Z5 discipline of publishing failed preregistered predictions (`gmi-833-z-z13-adjudication-v1`, `gmi-833-z-z5-critical-phenomena-v1` `CP-6`).

**Forbidden extrapolations.** `FROZEN_PREDICTION_REPAIRED_INTO_A_HIT_AFTER_A_MISS`.

---

## `ZH-6` — the instruments

Six hostiles, each with an `applicable` flag that would fail the run if it did
not move its quantity, all applicable and all detected: a corrupted floor
(`5/16 → 1/4`) breaks the registered closed forms in `108` worlds; an identity
ingredient is refused the earned flag; a null pool containing `IC-1`'s pair
reports a meaningless `135/135`; a non-affine noise model moves the niche in
`36` worlds where the affine theorem says `0`; a bound `moved ≤ 135` over
`[0,135]` is classified `VACUOUS`; a power-of-two LCG read at its low bit yields
a period-2, zero-variance null. Null: `200` seeded two-parameter marginal laws
(`148` distinct, `IC-1`'s pair excluded) score at best `48/249` on the hostile
targets where `IC-1` reads `249/249`; the base closed form applied blindly to
the hostile profiles scores `33/249`. No-alarm case: relabelling of state or
input with the task moves `0` verdicts and raises no alarm.

**Quantifiers.** For all six hostiles and all `200` null draws.

**Assumptions.** The null pool excludes the true pair; the hostile targets are the worlds of `I3`, `I5b`, `I7b` where the base and hostile envelope slopes differ.

**Dependencies.** `ZH-1`..`ZH-3`; both receipts.

**Falsifiers.** An inapplicable or undetected hostile; a null draw matching `IC-1`; an alarm on the relabelling control.

**Strongest parents.** The `applicable`-flag and vacuity-classification discipline of `gmi-833-z-z7-impossibility-v1` (`IM-4`, `IM-7`) and the enumeration-grounded null of `gmi-833-z-z5-critical-phenomena-v1`.

**Forbidden extrapolations.** `SEARCH_LAW_RESULTS_CLAIMED_FOR_SEARCHERS_NOT_RUN`; nothing is claimed about hostiles not listed.
