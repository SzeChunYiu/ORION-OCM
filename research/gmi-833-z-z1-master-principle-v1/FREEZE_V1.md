# GMI #833 Section Z / Z1 — master selection principle and incompressibility freeze

Committed **before any executor, oracle, witness search or receipt exists in this
package**. Git order proves it.

- `source_main`: `0dcdec54fbece041ee2b7cd1f630469ad85d19d3`
- branch: `research/833-sec-z4`

Claim ceiling:

```
GMI_833_Z1_MARGINAL_VALUE_PRINCIPLE_AND_EXACT_INCOMPRESSIBILITY_SEPARATIONS_AT_REGISTERED_FINITE_SELECTION_SCOPE
```

## 0. Disclosure — what was known before this freeze was written

The principle in §1 was written down by reading the already-merged and
already-frozen Z5/Z6 packages and the Z13 prediction freeze, and by hand algebra
on their closed forms. It was **not** discovered by the executor this package
will build. No witness pair for §3 has been searched for, and no number in §4 or
§5 has been computed. The statement of the principle is therefore *prior* to this
package's evidence, and the evidence is what tests it; the reverse ordering is
forbidden and is registered as a forbidden promotion below.

## 1. The principle, stated before it is tested

**`IC-1` — the Marginal Value Principle (MVP).** Let `X` be a finite candidate
set carrying a declared resource map `rho: X -> {0, 1, ..., K}` and declared
channel error rates `r_m: X -> Q` with declared channel weights `p_m` and a
declared error price `eta`, under the additive declared cost

```
C_lambda(x) = eta * sum_m p_m * r_m(x) + lambda * rho(x).
```

Define the **resource-error profile**

```
E(k) = min { eta * sum_m p_m * r_m(x) : x in X, rho(x) = k }.
```

Then:

1. `x` minimises `C_lambda` for some `lambda >= 0` only if `(rho(x), E(rho(x)))`
   is a vertex of the **lower convex envelope** of `{(k, E(k)) : k = 0..K}`;
2. a resource level `k` is the strict minimiser exactly on the open interval
   `(Delta_{k+1}, Delta_k)` where the **marginal error mass**
   `Delta_k = E(k-1) - E(k)` is taken along the envelope; the interval is
   non-empty exactly when `k` is an envelope vertex;
3. therefore **every selection threshold is a marginal error mass** — a
   supporting-line slope of the lower convex envelope — and **never an error
   level**.

Clause 3 is the sharp, falsifiable part. It is falsified by exhibiting one
registered selection threshold that is an error level and provably not a
marginal.

## 2. Corollary obligations (row 1)

The principle must be shown, by exact recomputation and not by re-derivation on
paper, to entail each of the following already-registered results. Each is a
named corollary with its own pass/fail line; a corollary that does not fall out
is reported as a failure of `IC-1`, not excused.

- `IC-1a` `lambda* = eta*p/2` (Z5 `CP-2`) — the two-level case with
  `E(0) = eta*p/2`, `E(1) = 0`;
- `IC-1b` `lambda*(A) = eta*p*(1 - 1/A)` (Z5 `CP-5`) — the same, with the
  alphabet-`A` stateless floor;
- `IC-1c` `lambda* = eta*p*R0` (Z6 `DS-5`) — the same, with the input-law
  stateless floor `R0`, and `eta*p/2` recovered at `R0 = 1/2`;
- `IC-1d` the `Z13` three-level ladder `Delta_1, Delta_2` — including the exact
  point at which `Z13-P1`'s frozen closed form departs from `IC-1`, if it does.

`IC-1a`-`IC-1c` share the structure `E(k) = 0` for `k >= 1`, which makes level
and marginal numerically equal. That coincidence is **why** clause 3 is not
idle, and it must be stated in the theorem note, not hidden.

## 3. Incompressibility (row 5) — what a proof must exhibit

Define the **MVP content** of an instance as the pair
`(declared accounting (eta, p, lambda-axis), resource-error profile E(.))`.
A law `L` is **MVP-compressible** iff `L`'s prediction on every instance is a
function of that instance's MVP content alone.

To prove a named law `L` **not** MVP-compressible this package must exhibit a
`SEPARATION WITNESS`: two instances `I` and `I'` with

- byte-identical declared accounting, and
- **exactly equal** resource-error profiles `E(.) = E'(.)` as rationals
  (hence identical MVP predictions at every `lambda`), while
- `L(I) != L(I')`.

Three obligations are fixed now:

- `W-EXIST` the witness pair must be produced by **enumeration over a declared
  finite population**, exhibited concretely, and re-derivable from the receipt.
  A schema, an existence argument or an appeal to genericity does not close row 5.
- `W-NONVACUITY` it must be shown by count that instances sharing an identical
  profile actually exist in the population, and how many. An envelope-invariance
  argument over a population in which no two instances share an envelope is the
  tautology-over-its-own-range failure class and is disqualifying.
- `W-NOALARM` at least one law must be shown **compressible** — the separation
  search must return "no witness" on a law that genuinely is a corollary of
  `IC-1`. A separator that separates everything is a broken instrument, not a
  result.

## 4. Compression metrics (rows 3 and 4), defined before they are computed

- `independent_predictions` := the number of distinct scored cells
  (world x lambda-cell) on which the theory emits a verdict **without consulting
  the enumeration**, counted over the declared union population.
- `free_theoretical_dof` := the number of numeric constants a theory must be
  supplied that are neither part of the environment's declared accounting
  (`eta`, the `p_m`, `lambda`, the input law, the alphabet size) nor a computed
  value of `E(.)`.
- `compression` := reported as the **raw pair** `(independent_predictions,
  free_theoretical_dof)` first, and only then as a ratio. A ratio alone is
  gameable by inflating the cell count, so the cell-count rule is fixed here:
  one cell per (world, adjacent-threshold-pair) and no finer.
- row 4 is discharged by classifying **every** numeric constant occurring in each
  registered closed form as (a) environment-declared, (b) a computed value of
  `E(.)`, or (c) genuinely arbitrary, and reporting class (c) honestly if it is
  non-empty.

## 5. Baseline comparison (row 6)

Head-to-head over the declared union population: `IC-1` against a
**bag-of-independent-laws** baseline consisting of the registered closed forms
applied literally, each evaluated both inside and outside its registered scope.
Correct / incorrect / abstain counts are reported per theory. The bag's
out-of-scope failures are already published on `main` and must be reproduced, not
re-derived favourably.

## 6. Two routes, hostiles, null

Route B may not import Route A. Every hostile must be shown to move the quantity
it perturbs; an inert hostile is a defect of this package. The null must be one
the true result beats, and must be grounded in the enumeration rather than in the
author's own closed form — the exact instrument failure Z5 recorded and repaired.

## 7. The exact issue rows this package may reconcile

Section Z lives in issue comment `5684819296`. Verbatim rows of `### Z1 — Explanatory compression / master principle`:

```
- [ ] Search for a compact master variational/selection principle from which multiple existing GMI laws follow as corollaries.
- [ ] Quantify theory compression: independent predictions / free theoretical degrees of freedom.
- [ ] Minimize arbitrary constants and post-hoc knobs.
- [ ] Prove which laws cannot be compressed into the proposed master principle and why.
- [ ] Compare one-principle GMI against a bag-of-independent-laws baseline.
```

Row 2 of `### Z1` is **out of scope for this package and may not be touched by it**:

```
- [ ] Show which current memory, abstraction, attention, planning, communication, teaching/culture, morphology and capability laws can be derived from that common principle.
```

Reason, fixed now: that row quantifies over eight named law families and no
canonical register of those families exists on `main`. The
`gmi-833-theory-baseline-v1` `A1`-`A14` table is a corpus-audit assertion table,
not a law register. Assembling an inventory here and classifying only the
morphology and capability entries would be closure by narrowing.

**No neighboring row is earned here.**

## 8. Forbidden promotions

```
MVP_CLAIMED_AS_NOVEL_MATHEMATICS
Z1_ROW2_CLOSED_BY_THIS_PACKAGE
INCOMPRESSIBILITY_CLAIMED_WITHOUT_AN_EXHIBITED_WITNESS_PAIR
SEPARATION_CLAIMED_ON_A_POPULATION_WITH_NO_SHARED_PROFILES
COMPRESSION_RATIO_REPORTED_WITHOUT_ITS_RAW_PAIR
PRINCIPLE_PRESENTED_AS_DISCOVERED_BY_THIS_PACKAGES_EXECUTOR
RESULT_EXTENDED_BEYOND_THE_DECLARED_UNION_POPULATION
```
