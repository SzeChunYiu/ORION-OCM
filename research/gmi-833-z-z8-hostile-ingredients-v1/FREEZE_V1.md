# GMI #833 Section Z / Z8 — hostile ingredient freeze

Committed **before any executor, oracle, enumeration under a modified universe,
or receipt exists in this package**. Git order proves it.

- `source_main`: `f1e150ea89d1e3422d5ab18ec9a61d36ff17c3e5`
- branch: `research/833-sec-z811`

Claim ceiling:

```
GMI_833_Z8_NINE_HOSTILE_INGREDIENTS_EACH_SHOWN_TO_MOVE_A_REGISTERED_VERDICT_OR_PROVED_UNABLE_AT_REGISTERED_THREE_MODE_FINITE_STATE_SCOPE
```

## 0. Disclosure — what was known before this freeze was written

Everything below was written by hand algebra on numbers that are already
registered on sibling branches and on `main`:

- the nine three-mode ladder floors of `gmi-833-z-z13-adjudication-v1` `ZA-1`
  (`b=0: (0, 1/2, 1/2)`, `b=1: (0, 0, 5/16)`, `b=2: (0, 0, 0)`), which this
  package re-derives from scratch rather than imports;
- the marginal value principle `IC-1` of `gmi-833-z-z1-master-principle-v1`
  (`λ* = ηp·R0`, thresholds are marginal error masses — supporting slopes of the
  lower convex envelope of the resource–error profile — never levels; `135/135`,
  unique of `289`), which is the **registered law** this package builds on;
  `λ* = ηp/2` is retired and is used below only as a competitor;
- the two-level stateless floor `R0(q) = min(q, 1−q)` for the seven registered
  input laws (`IC-1c`) and `R0(A) = 1 − 1/A` (`IC-1b`);
- `gmi-833-z-z13-adjudication-v1`'s report that a deterministic single-start
  coordinate descent from the all-zero next-state function stalls at `4` of `32`
  errors on the `b=2` delay-2 channel where exhaustive enumeration reaches `0`;
- the on-`main` parents that already own the *mechanisms* behind five of the nine
  ingredients, absorbed rather than re-derived: `gmi-833-history-switching-hysteresis-v1`
  (`HIST-1`, `HIST-2`: the exact two-form hysteresis band under switching costs),
  `gmi-833-search-law-morphology-change-v1` (`SLM-1`..`SLM-6`: when a search law
  changes the observed candidate), `gmi-833-g0-grammar-bias-v1` (`RELABEL-2`: a
  same-semantics grammar change reverses the choice) with
  `gmi-833-remint-equivariance-v1` (relabelling invariance),
  `gmi-833-capability-predictor-v1` (`FM_ALIASING`: observational aliasing forces
  abstention), `gmi-833-capability-predictor-evaluation-v1` (`KE-7`: structural
  out-of-universe shift) and `gmi-833-ae-ae2-predictive-boundary-v1`
  (`DRIFT_INVERT`: a nonstationary source); the exact ties of
  `gmi-833-heldout-20-transitions-v1` and `gmi-833-z-z5-critical-phenomena-v1` `CP-3`.
  **None of those parents states or measures whether its ingredient moves a
  registered verdict on the three-mode ladder; that residual is the whole content
  of this package.**

**No enumeration under any modified universe (a changed input law, a changed
grammar, a dropped scored moment, a changed search law) has been run.** Every
number in §3 that requires one is a prediction and is scored HIT/MISS by the
executor; a MISS goes to `FAILED_PREDICTION_REGISTER_V1.json` and is not
repaired into a HIT by this lane. The only laptop run before this freeze was a
timing check that reproduced the nine registered base floors verbatim.

## 1. The base universe and the registered verdicts

`U0`: the three-mode binary transducer universe of Z13 — sequence length `L = 4`,
uniform i.i.d. binary inputs, canonical initial state `0`, state budget
`b ∈ {0, 1, 2}`, per-mode output table `out: (state, cur) → {0,1}` and next-state
table `next: (state, cur) → state`, scored window `t ∈ {2, 3}`, modes
`m ∈ {0: now, 1: delay-1, 2: delay-2}` with target `x_{t−m}`.

`W0`: the grid `η ∈ {1, 2, 3}` × `(p0, p1, p2)` over eighths summing to `1` —
`45 × 3 = 135` worlds. Resource–error profile
`E_w(k) = η · Σ_m p_m · R0(k, m)`; declared cost `C_λ(k) = E_w(k) + λ·k`.
`Λ`: the price grid `λ ∈ {j/16 : j = 0..24}` (`25` values; every registered
threshold on `W0` lies in `[0, 3/2]`).

Four **registered verdicts** on a world `w` (and a price `λ` where one is needed):

| verdict | definition |
|---|---|
| `V_SEL(w, λ)` | the argmin **set** `{k : C_λ(k) minimal}` |
| `V_NICHE(w)` | whether level `1` is a vertex of the lower convex envelope of `{(k, E_w(k))}` — equivalently `E_w(0) − 2·E_w(1) + E_w(2) > 0`, which on `U0` is `4·p1 > p2` |
| `V_THR(w)` | the marginal pair `(Δ_1, Δ_2) = (E_w(0) − E_w(1), E_w(1) − E_w(2))` — on `U0`, `(η(p1/2 + 3p2/16), η·5p2/16)` |
| `V_FAIL(w, λ)` | the failure-mode set of the selected level: `{m : p_m > 0 and R0(k, m) > 0}` for the smallest `k ∈ V_SEL(w, λ)` |

An ingredient `I` is a map from base worlds to hostile worlds whose ground truth
is recomputed **from scratch** under the modified universe. `I` **moves** a verdict
`V` iff there is a world (or world × price cell) on which `V(I(w)) ≠ V(w)`.
`I` is **unable to move** `V` iff this is proved for every world of the grid, by
a theorem in `Z8_THEOREMS_V1.md` **and** an exhaustive check. The binding
condition set by the previous lane is that every one of the nine ingredients ends
in one of those two states for every registered verdict; an ingredient that is
defined and changes nothing anywhere, with no theorem saying why, is a defect of
this package and does not close its row.

## 2. The nine ingredients, fixed now

| id | issue row | hostile-world map |
|---|---|---|
| `I1` near-ties | `Include near-tie morphologies.` | prices placed exactly at, and `1/64` either side of, each marginal `Δ_k`; the triple-tie locus `Δ_1 = Δ_2` |
| `I2` verifier noise/failure | `Include verifier noise/failure.` | (a) every scored error indicator flipped with probability `ε ∈ {1/16, 1/8, 1/4}`, uniformly across channels; (b) the same flip applied to the delay-2 channel only; (c) verifier failure: the scored moment `t = 2` is dropped, window `{3}` only |
| `I3` causal aliasing | `Include causal aliasing.` | the input law is period-2 (`x_t = x_{t−2}`, uniform over the four seeds `(x_0, x_1)`), so the delay-2 target is causally aliased with the current input |
| `I4` shift / nonstationarity | `Include severe distribution shift/nonstationarity.` | (a) model selection under input law `q_train`, scoring under `q_test`, both from the seven registered laws `{1/5, 1/4, 1/3, 1/2, 2/3, 3/4, 4/5}`, on the two-level delay-1 population; (b) nonstationarity inside the window: `x_t ~ Bernoulli(q)` for `t < 2` and `Bernoulli(q')` for `t ≥ 2` |
| `I5` resource accounting | `Include resource-accounting changes.` | (a) affine `ρ = 2b + 1`; (b) state count `ρ = 2^b − 1 ∈ {0, 1, 3}`; (c) concave `ρ ∈ {0, 2, 3}` |
| `I6` history / current optimum | `Include history/current-optimum conflicts.` | (a) history-weighted profile `w·E_h + (1−w)·E_c`, `w ∈ {1/4, 1/2, 3/4}`, over ordered pairs of ecologies `(p_h, p_c)` at `η = 1`; (b) hysteresis: the history optimum is retained under current ecology iff its excess cost is `≤ κ`, `κ ∈ {1/32, 1/8}` |
| `I7` grammar / encoding | `Include grammar/encoding changes.` | (a) Moore grammar: `out` reads the state only; (b) input-only grammar: `next` reads `cur` only; (c) encoding change: state relabelling and input-symbol relabelling applied to machine and task together |
| `I8` search law | `Include search-law changes.` | the profile attained by deterministic single-start coordinate descent from the all-zero next-state function (`E_S`), and by a seeded randomised hill-climb (`E_H`), each compared with exhaustive enumeration |
| `I9` freeze before scoring | `Freeze predictions before revealing hostile worlds to the scoring implementation.` | this document: the world maps and every prediction in §3 are committed before the scoring implementation exists; the executor emits `sha256` of the generated hostile world set and the workflow asserts git order |

## 3. Frozen predictions, one per ingredient, scored HIT/MISS

Counts are over the `135` worlds of `W0` unless a cell count is named.
"moves" means the executor must find the stated number of worlds (or cells)
where the verdict differs from its base value; "unable" means `0` such worlds
and a theorem.

- `P1` (near-ties). At `λ = Δ_1` exactly, `V_SEL ⊇ {0, 1}` in every world with
  `Δ_1 > Δ_2`; at `λ = Δ_1 − 1/64` it is `{1}` and at `Δ_1 + 1/64` it is `{0}`
  (with the symmetric statement at `Δ_2`). Exactly `6` worlds have `Δ_1 = Δ_2`
  (the locus `4·p1 = p2`: `(p1, p2) ∈ {(0, 0), (1/8, 4/8)}` at each `η`), of
  which `3` are degenerate (`Δ = 0`). `I1` moves `V_SEL` in every non-degenerate
  world; it cannot move `V_NICHE` or `V_THR` (they do not depend on `λ`).
- `P2` (verifier noise/failure). (a) Uniform flip noise `ε` maps the profile to
  `E'(k) = (1 − 2ε)·E(k) + η·ε`, so every marginal scales by `(1 − 2ε)` and
  **`V_NICHE` is unchanged in `135/135` worlds at every `ε`** (theorem: an
  affine map with positive slope preserves envelope vertices); `V_SEL` moves in
  every `(w, λ)` cell with `λ` strictly between a scaled and an unscaled
  marginal; `V_THR` moves in every world with a non-zero marginal. (b) Delay-2-only
  noise is a reweighting `p2 → (1 − 2ε)·p2` plus a constant, so `V_NICHE` moves
  exactly in the worlds with `4·p1 ≤ p2 < 4·p1 / (1 − 2ε)` — at `ε = 1/4` that
  is the worlds with `4·p1 ≤ p2 < 8·p1`: `(p1, p2) ∈ {(1/8, 4/8), (1/8, 5/8),
  (1/8, 6/8), (1/8, 7/8), (2/8, 8/8)}` minus those violating `p1 + p2 ≤ 1`,
  i.e. `4` triples, `12` worlds. (c) Dropping the scored moment `t = 2` leaves
  `R0(0, 1) = R0(0, 2) = 1/2`, `R0(1, 1) = 0`, all `b = 2` floors `0`, and makes
  `R0(1, 2) > 0` (a single next-state function cannot both store `x_1` at `t = 2`
  and ignore `x_2` at `t = 3`); whether `R0(1, 2)` differs from `5/16` is left to
  the enumeration, and `V_THR` moves iff it does.
- `P3` (causal aliasing). Under the period-2 law the floors become
  `b=0: (0, 1/2, 0)`, `b=1: (0, 0, 0)`, `b=2: (0, 0, 0)`, so `V_NICHE` becomes
  `p1 > 0`: `I3` moves `V_NICHE` in exactly `12` worlds (`4·p1 ≤ p2` with
  `p1 > 0`) and `V_THR` in exactly `108` worlds (`p2 > 0`). An input-law-blind
  application of the base closed form misses `V_THR` in those `108`; `IC-1`
  applied to the aliased profile reproduces `V_THR` in `135/135`.
- `P4` (shift/nonstationarity). (a) Over the `7 × 7` law pairs, `η`, `p` and
  `λ ∈ Λ`, the train-selected level differs from the test-optimal level exactly
  on the cells where `λ` lies strictly between `η·p·R0(q_train)` and
  `η·p·R0(q_test)`, and nowhere else; the pairs `(q, 1 − q)` move nothing
  (`R0(q) = R0(1 − q)`). (b) Under the in-window switch `q → q'` the stateless
  delay-1 floor over the window `{2, 3}` is `(R0(q) + R0(q'))/2` and the
  threshold is `η·p·(R0(q) + R0(q'))/2`, exact in every `(q, q', η, p)` cell.
- `P5` (resource accounting). (a) Affine `ρ = 2b + 1`: **unable** to move
  `V_NICHE`, and `V_SEL` is unchanged under the matching price `λ' = λ/2`, in
  `135/135` worlds. (b) State-count `ρ ∈ {0, 1, 3}`: level `1` is a vertex iff
  `2·Δ_1 > Δ_2`, i.e. iff `(p1, p2) ≠ (0, 0)`; moves `V_NICHE` in exactly `36`
  worlds (the `12` triples with `4·p1 ≤ p2` and `(p1, p2) ≠ (0, 0)`).
  (c) Concave `ρ ∈ {0, 2, 3}`: level `1` is a vertex iff `8·p1 > 7·p2`; moves
  `V_NICHE` in exactly `24` worlds (the `8` triples with `4·p1 > p2 ≥ 8·p1/7`).
- `P6` (history/current optimum). (a) If the history verdict and the current
  verdict share a level, that level is in the history-weighted verdict at every
  `w` (**unable**, by convexity of the mixture); the weighted verdict differs
  from the current-optimum verdict on a non-empty set of cells. (b) Hysteresis
  moves `V_SEL` exactly on the cells with `0 < excess cost ≤ κ`; the moved-cell
  count is monotone in `κ` and non-zero at `κ = 1/32`.
- `P7` (grammar/encoding). (a) Moore floors are `b=0: (1/2, 1/2, 1/2)`,
  `b=1: (1/2, 0, 5/16)`, `b=2: (1/2, 0, 0)` — the now-channel becomes a constant
  `η·p0/2` at every level (witness for `5/16` at `b=1`: `next(0, c) = c`,
  `next(1, c) = 1`, `out(s) = s`, errors `4 + 6` of `32`); therefore Moore is
  **unable** to move `V_NICHE`, `V_SEL` or `V_THR` (`135/135`) and moves
  `V_FAIL` in exactly the `108` worlds with `p0 > 0`. (b) The input-only grammar
  has floors `b=0: (0, 1/2, 1/2)`, `b=1: (0, 0, 1/2)`, `b=2: (0, 0, 1/2)`; it
  moves `V_NICHE` in exactly `12` worlds and `V_THR` in exactly `108`.
  (c) Relabelling of state or of input symbols applied to machine and task
  together is **unable** to move any verdict (a cost-preserving bijection of the
  candidate set); a non-relabelling address scramble is the control and must
  change at least one floor.
- `P8` (search law). `IC-1` applied to the search-attained profile `E_S`
  reproduces the search-observed thresholds in `135/135` worlds (it is a
  statement about whatever profile it is given). The single-start descent
  attains `4/32` on `(b=2, delay-2)` as Z13 reported; **if** it attains `5/16` on
  `(b=1, delay-2)` then `Δ_2^S = η·3p2/16` and `V_NICHE` moves in exactly the
  `12` worlds `4·p1 ≤ p2 < ∞, p1 > 0`; the seeded hill-climb attains the
  exhaustive floors in `9/9` cells and moves nothing.
- `P9` (freeze before scoring). The first commit touching this package carries
  this file and no executor; the executor's world-set `sha256` is reproduced
  byte-stably by both routes.

## 4. Two routes, hostiles, null

Route B may not import Route A and may not enumerate next-state functions the
way Route A does; it recomputes every floor by enumerating full
`(output, next-state)` pairs where feasible and by the declared closed forms
elsewhere, and recomputes every verdict-move count from the emitted hostile
world set by interval arithmetic rather than by scanning the price grid.

Every hostile must carry an `applicable` flag that FAILS the run when the
hostile does not move the quantity it perturbs. The null draws `200` seeded
two-parameter marginal laws `η·(a·p1 + b·p2)`, `a, b ∈ k/16`, from a pool that
**excludes** `IC-1`'s own pair `(1/2, 3/16)`, and scores each on the hostile
worlds of `I3`, `I5(b)`, `I7(b)` where the base and hostile thresholds differ;
the true result must beat the best null. The no-alarm case is `I7(c)`: the
checker must report `0` moved verdicts there without alarm, and must alarm on
the address-scramble control.

## 5. Bounds

Every bound in the receipt is classified for vacuity against its declared range:
a moved-verdict count `c` over `N` worlds is vacuous iff `c ∈ {0, N}` and no
theorem accounts for it; a floor bound `R ≥ 0` is vacuous; `R > 0` is not.

## 6. The exact issue rows this package may reconcile

Section Z lives in issue comment `5684819296`. Verbatim rows of
`### Z8 — Hostile out-of-distribution science`:

```
- [ ] Include near-tie morphologies.
- [ ] Include verifier noise/failure.
- [ ] Include causal aliasing.
- [ ] Include severe distribution shift/nonstationarity.
- [ ] Include resource-accounting changes.
- [ ] Include history/current-optimum conflicts.
- [ ] Include grammar/encoding changes.
- [ ] Include search-law changes.
- [ ] Freeze predictions before revealing hostile worlds to the scoring implementation.
```

Row 1 of `### Z8` is **out of scope for this package and may not be touched by it**:

```
- [ ] Commission independent hostile benchmark construction designed specifically to break GMI assumptions.
```

Reason, fixed now: it names an independent party as the instrument. This lane
is the party that built the ingredients, so it cannot also be the independent
commission; no `HUMAN_GATE_BYPASSED__MODEL_PROXY` is built here.

**No neighboring row is earned here.**

## 7. Forbidden promotions

```
Z8_ROW1_CLOSED_BY_THIS_PACKAGE
INGREDIENT_COUNTED_AS_EARNED_WITHOUT_A_MOVED_VERDICT_OR_A_THEOREM
HOSTILE_WORLD_RESULTS_EXTENDED_BEYOND_L4_B2_THREE_MODE_SCOPE
FROZEN_PREDICTION_REPAIRED_INTO_A_HIT_AFTER_A_MISS
RETIRED_LAW_ETA_P_OVER_2_USED_AS_THE_REGISTERED_PREDICTION
VERIFIER_NOISE_CLAIMED_TO_MOVE_THE_NICHE_VERDICT_WITHOUT_CHANNEL_SELECTIVITY
SEARCH_LAW_RESULTS_CLAIMED_FOR_SEARCHERS_NOT_RUN
Z11_ROWS_CLOSED_BY_THIS_PACKAGE
```
