# Exact capability predictor, prospective failure modes, and total uncertainty — v1

**Issue:** #833, Section K. **Freeze:** `FREEZE_V1.md` at commit
`f09288d920ea085e984a2f7ba191c777ee1871a2`.
**Claim ceiling:**
`GMI_833_EXACT_CAPABILITY_PREDICTOR_FAILURE_TAXONOMY_AND_TOTAL_UNCERTAINTY_AT_REGISTERED_FINITE_SCOPE`.

All statements are `forall_fin[Sigma_1]` over the registered finite universe and
input grid of `SCOPE_V1.md` unless a proof is marked analytic, in which case the
quantifier is stated in the theorem. All arithmetic is exact (`Fraction`/`int`).

## 0. Objects

Registered finite realization universe `X`; registered capability contract
`E = (T, mu, u, V, tau)`; registered resource object `R = (b, m)` with `b` the
14-coordinate lifecycle budget and `m` the BUDGET-1 mandatory shared charge;
registered morphology constraint `M = K_M`; registered interaction history `H`;
registered developmental law `D`; registered typed uncertainty object `U` (a U-1a
`FeasibleSet` or a U-1b `ConfidenceSet`).

```text
cap_E(x)   = sum_j mu_j u(x, t_j)                       (CAP-1, exact Fraction)
q_{E,R}(x) = cap_E(x)    if rho(x) <= b - m coordinatewise
           = UNSATISFIED otherwise                       (CAP-1: not fabricated)
C          = X ^ Expr(M) ^ Reach(D) ^ Seen(B) ^ Epis(H,U)     (candidacy)
A_0 = X,  A_1 = A_0 ^ Expr(M),  A_2 = A_1 ^ Res(R),
A_3 = A_2 ^ Reach(D),  A_4 = A_3 ^ Seen(B),  A_5 = A_4 ^ Epis(H,U) = C ^ Res(R)
c_i = max { cap_E(x) : x in A_i },  c_i = BOTTOM if A_i = {}
q_tau(x) = 1 if q_{E,R}(x) >= tau else 0     (UNSATISFIED >= tau is false)
```

`F` emits exactly one of `IDENTIFIED(y)`, `CANNOT_IDENTIFY(S)`,
`INCONSISTENT_REGISTERED_ASSUMPTIONS`, `CANNOT_CHECK(reason)`, each carrying a
typed uncertainty object.

---

## KP-1A — totality, determinism, exception-freedom

**Statement.** `F` is a total deterministic function on the registered input grid:
every grid input produces exactly one emission, the emission depends only on the
input, and no input raises.

**Scope / quantifiers.** `forall_fin[Sigma_1]` over the main grid and the
semantics-defect sub-census.

**Assumptions.** The registered universe and grid of `SCOPE_V1.md`; no mutable
global state between calls.

**Proof.** The guard sequence is exhaustive: either the query/threshold semantics
are unregistered or the query is not total on `X` (terminal `CANNOT_CHECK`), or `C`
is empty (terminal `INCONSISTENT_REGISTERED_ASSUMPTIONS`), or `C` is nonempty and
the exact image `q_{E,R}[C]` of a nonempty finite set is nonempty, so its
cardinality is either `1` (terminal `IDENTIFIED`) or greater than `1` (terminal
`CANNOT_IDENTIFY`). These four cases are mutually exclusive and cover every input.
Every constituent operation is a finite set intersection, a finite image, or an
exact rational comparison; none is partial on its registered domain. Determinism
follows because every operation is a pure function of the input record. `[]`

**Machine certificate.** Exhaustive replay over the frozen grid recording, per
input, the emission and the reached emit-site id; the exception count is obtained
by wrapping each call in `try/except BaseException` and must be zero.

**Falsifiers.** Any grid input with zero or more than one emission; any raise; any
two evaluations of the same input differing.

**Strongest parents.** U-4A (image cardinality), #913 terminals.

**Forbidden extrapolation.** Totality is over the *registered* grid. Nothing is
claimed for inputs outside `Sigma_1`.

---

## KP-1B — soundness (unconditional)

**Statement.** If `F(M,E,R,H,D,U) = IDENTIFIED(y)` then for **every** realization
`x in X` consistent with the registered inputs, `q_{E,R}(x) = y`. In particular the
emitted point equals the externally evaluated capability of every consistent
realization, so `F` can never be wrong when it speaks.

**Scope / quantifiers.** Analytic: `forall` registered finite `X`, `C`, `q`.
Machine-certified `forall_fin[Sigma_1]`.

**Assumptions.** "Consistent with the registered inputs" means `x in C`, where `C`
is the candidacy intersection above. No probabilistic premise. No independence.

**Proof.** `F` emits `IDENTIFIED(y)` only when `C != {}` and `|q_{E,R}[C]| = 1`.
By U-4A, a singleton image means `q_{E,R}(x) = y` for every `x in C`. `[]`

**Why the resource cut must stay out of `C`.** Suppose `Res(R)` were applied to `C`.
Take `x_1` with `rho_0(x_1) = 1`, `cap_E(x_1) = 1/2` and `x_2` with
`rho_0(x_2) = 9`, `cap_E(x_2) = 1`, both satisfying `M`, `H`, `D`, `Seen`, with
effective budget `5`. The pruned survivor set is `{x_1}`, the image is `{1/2}`, and
`F` would emit `1/2` — yet `x_2` is a realization consistent with the registered
inputs whose contract verdict is `UNSATISFIED != 1/2`. The statement above would be
false. Keeping `x_2` in `C` with verdict `UNSATISFIED` makes the image
`{1/2, UNSATISFIED}`, multi-valued, and forces the abstention that is in fact
warranted. This is the load-bearing design decision of the tranche and is frozen in
`FREEZE_V1.md` section 4.3.

**Falsifiers.** A grid input where a point is emitted and some `x in C` has a
different verdict; a code path that prunes `C` by resource admissibility; a
coercion of `UNSATISFIED` to `0`.

**Strongest parents.** ABSTAIN-1 (#913), U-4A (#851), CAP-1 (#848).

**Forbidden extrapolation.** This does **not** say that the emitted point is the
capability of a real system. That bridge is KP-1D.

---

## KP-1C — completeness: the exact condition for a point, and forced abstention

**Statement.** For a registered input with registered query semantics and `C != {}`:

```text
F emits a point   iff   q_{E,R} is constant on C.
```

When `q_{E,R}` is not constant on `C`, abstention is **forced**: there exist
`x, x' in C` with `q_{E,R}(x) != q_{E,R}(x')`, so no single value is uniformly
sound, and every candidate point is refuted by an explicit surviving
counterexample.

**Scope / quantifiers.** Analytic `forall`; machine-certified `forall_fin[Sigma_1]`
with the witness pair exhibited for every abstaining input.

**Assumptions.** `C` nonempty finite; `q_{E,R}` total on `X`.

**Proof.** ("only if") `F` emits a point only when `|q_{E,R}[C]| = 1`, which by
U-4A is exactly constancy on `C`. ("if") constancy on a nonempty `C` gives a
singleton image, so `F` emits. Forcedness is the forced-point counterexample
theorem of #913: for any chosen member `y` of a non-singleton image there is
`x in C` with `q_{E,R}(x) != y`. `[]`

**Consequence (query-relative, not identity-relative).** Constancy of `q_{E,R}` is
strictly weaker than identification of the realization. The coarser threshold query
`q_tau` can be constant on `C` while `q_{E,R}` is not; the certification terminal of
`FM_NONE` is exactly ABSTAIN-1 applied to `q_tau`, not a separate rule.

**Falsifiers.** A non-constant image emitting a point; a constant image forced to
abstain; an abstention whose reported identified set omits a surviving value; an
abstention with no exhibited witness pair.

**Strongest parents.** #913 forced-point theorem; U-4A/U-4B.

---

## KP-1D — boundary, EARNED BY COUNTEREXAMPLE

**Statement.** KP-1B is unconditional about realizations consistent with the
registered inputs. The further bridge "the emitted point is the capability of the
actual system" requires the registration to be truthful, i.e. the actual system must
satisfy every registered constraint. That extra premise cannot be removed: there is
a registered input and a mis-registered constraint under which `F` emits a
perfectly sound point that is not the actual system's capability.

**Counterexample (exhibited by the executor).** Take the true realization `x_t` with
`cap_E(x_t) = 1`. Register `K_M` excluding `k(x_t)` while every surviving candidate
shares a single capability value `y != 1`. Then `C` is nonempty, `q_{E,R}[C] = {y}`,
`F` emits `IDENTIFIED(y)` — sound by KP-1B, since every *consistent* realization has
value `y` — but `x_t` is not in `C` and has value `1`. The obstruction is structural:
`F` observes only the registered constraints, so no function of them can detect a
constraint that is false of the world.

**Adjacent scoped positive.** The unconditional statement that survives is exactly
KP-1B, plus: `F` never emits a point when the registered inputs leave the value
open, so a truthfully registered input can never produce a wrong point. Truthfulness
of registration is therefore the *only* remaining premise, it is named, and it is
outside the mathematics rather than hidden inside it.

**Registered gap.** `GAP-KPRED-REGISTRATION-TRUTHFULNESS`.

---

## KP-2A — ladder monotonicity

**Statement.** `c_0 >= c_1 >= c_2 >= c_3 >= c_4 >= c_5`, with `BOTTOM` below every
rational and absorbing (once `A_i = {}`, all later `A_j = {}`).

**Proof.** `A_{i} subseteq A_{i-1}` by construction, and a maximum over a subset
cannot exceed the maximum over the superset (CAP-2A). If `A_{i-1} = {}` then
`A_i = {}`. `[]`

**Strongest parents.** CAP-2A/CAP-2B (#848), standard supremum monotonicity.

---

## KP-2B — the taxonomy is a partition

**Statement.** The ten modes of `TAXONOMY_V1.md` are pairwise disjoint and jointly
exhaustive on the registered input grid: every input satisfies exactly one mode
predicate.

**Proof.** The two terminal guards are mutually exclusive by definition and
dominate: `FM_CANNOT_CHECK` requires unregistered/non-total query semantics,
`FM_INCONSISTENT` requires registered semantics and `C = {}`. Given registered
semantics and `C != {}`, the remaining eight modes are determined by the position of
`tau` in the chain `c_0 >= ... >= c_5`. Because the chain is nonincreasing (KP-2A),
the set `{ i : c_i < tau }` is an up-set of `{0,...,5}`, so it is either empty or has
a unique minimum `i*`. If it is nonempty, `i*` determines exactly one of the six
ladder modes (`i* = 0,...,5`). If it is empty, `c_5 >= tau` and the dichotomy
`q_tau[C] = {1}` versus `q_tau[C] != {1}` assigns exactly one of `FM_NONE`,
`FM_ALIASING`. These cases are exhaustive and mutually exclusive. `[]`

**Machine certificate.** The census evaluates all ten predicates **independently**
(not as an if/elif chain) and requires the number of true predicates to equal 1 for
every input; overlaps and gaps are counted separately and must both be zero.

**Validation of the checker.** The same checker must flag the planted hostiles
`TAXONOMY_OVERLAP` (a `<=` at one rung) and `TAXONOMY_GAP` (`FM_ALIASING` deleted),
and must raise no alarm on the true taxonomy.

**Falsifiers.** Any input with two or zero true predicates; a hostile that is not
flagged; an alarm on the true taxonomy.

---

## KP-2C — unique binding cut

**Statement.** If an input is assigned ladder mode `i in {1,...,5}` then
`c_{i-1} >= tau` and `c_i < tau`. Hence the cut `P_i` is the unique registered cut
that, conditional on all preceding registered cuts, destroys attainability of the
target: removing it restores a `>= tau` witness at that stage, no earlier cut is
binding (the prefix still attains `tau`), and no later cut has yet been applied.
For `FM_INFORMATION_CEILING`, `c_0 < tau`: no registered cut is responsible and the
obstruction belongs to the registered admissible class itself (the CAP-2
impossibility region).

**Proof.** Immediate from `i = min { j : c_j < tau }` and KP-2A. `[]`

**Falsifiers.** A ladder-mode input with `c_{i-1} < tau` or `c_i >= tau`.

---

## KP-2D — boundary, EARNED BY COUNTEREXAMPLE: order dependence

**Statement.** First-crossing attribution depends on the registered cut order. The
tranche censuses all `120` permutations of the five cuts and reports the exact
number of grid inputs whose attributed mode is not invariant across all orders,
together with an explicit counterexample.

**Counterexample shape (analytic).** Let the full conjunction have ceiling `< tau`,
let dropping `P` alone restore a `>= tau` witness, and let dropping `Q` alone not.
If the prefix `{P}` alone still attains `tau`, order `(P,Q)` first crosses at `Q`
while order `(Q,P)` first crosses at `P`. Both attributions are correct statements
about their own prefix chain; there is no order-free "the" binding cut.

**Proven-structural, not a defect.** Order dependence is a property of conjunctive
constraint systems, not of this implementation. Only a total order on the cuts makes
"first binding" well defined, and the registered order is justified by the
dependency column of `TAXONOMY_V1.md` section 1: expressibility precedes charging,
charging precedes development, development precedes search, and evidence acts on the
observer so it is applied last.

**Adjacent scoped positive.** KP-2C is unconditional and order-free once the order is
registered; and two facts are order-invariant outright and are reported: (i) whether
the input is a shortfall at all (`c_full < tau`, where `c_full` is the ceiling of the
full conjunction, which is order-independent because intersection is commutative),
and (ii) the emission of `F` itself.

---

## KP-3A — total uncertainty attachment

**Statement.** No code path of `F` emits a bare value. Every `return` statement in
the reachable predictor call graph is a call to the single `emit` constructor; `emit`
rejects any emission whose uncertainty field is absent or malformed; and the grid
census raises zero exceptions, so no emission escapes through a raise.

**Scope / quantifiers.** Structural (`ast` over the reachable call graph of the
module) plus `forall_fin[Sigma_1]` runtime census.

**Proof mode.** Mechanical. The structural half is decided by parsing the module,
computing the set of functions reachable from `predict`, and requiring every
`ast.Return` node with a value in that set to be a call to `emit`. The runtime half
checks, for every grid emission, that the uncertainty field is a registered U-1
constructor with constructor-appropriate fields, and counts exceptions.

**Why `assert` is not used.** The package must replay identically under
`python3 -I -O -B`, which strips `assert`. All validation raises `ValueError`.

**Falsifiers.** A reachable `return` that is not an `emit` call; an emission with a
missing/ill-typed uncertainty object; a `FEASIBLE_SET` emission carrying a coverage
number; any exception on the grid.

**Strongest parents.** U-1 constructor disjointness (#851).

---

## KP-3B — dependence-safe budget composition

**Statement.** For every registered `ConfidenceSet` input, the coverage budget
attached to the emission equals the U-2B dependence-safe value

```text
coverage_lower = max(0, 1 - alpha - (beta_M + beta_D + beta_B + beta_H))
```

computed over the registered candidacy relation chain, with no independence
premise. The independence product `(1-alpha) * prod_i (1-beta_i)` is strictly
larger on the registered budgets and is refused. For a `FeasibleSet` input no
coverage field is emitted at all.

**Proof.** The candidacy chain is `C_0 = U.C`, `C_1 = R_M[C_0]`, `C_2 = R_D[C_1]`,
`C_3 = R_B[C_2]`, `C_4 = R_H[C_3] = C`, where each `R_i` is the registered
restriction relation. U-2A gives exactness of the composed image; U-2B gives
`P(theta in C) >= max(0, 1 - alpha - sum beta_i)` from Boole's inequality alone.
U-4B transports that budget through the query image, to the identified set and, when
the image is a singleton, to the point. A `FeasibleSet` has no probability premise
(U-1a), so attaching any coverage number to it would be fabrication. `[]`

**Falsifiers.** An emitted budget differing from the formula; use of the product; a
`FeasibleSet` emission with a coverage number; a budget converted to certainty.

**Strongest parents.** U-2A/U-2B/U-4B (#851), Boole.

**Forbidden extrapolation.** This is the composition of *registered* budgets. It is
not a claim that the registered `beta_i` are the true error rates of any real
pipeline, and it is not an empirical calibration measurement.

---

## KP-3C — exact finite coverage

**Statement.** Over all registered pairs `(input, consistent world)` — that is,
every grid input paired with every `x in C(input)` taken in turn as the ground truth
— the emitted object contains the true capability value `q_{E,R}(x)` in exactly
`100%` of pairs. Formally: for `IDENTIFIED(y)`, `q_{E,R}(x) = y`; for
`CANNOT_IDENTIFY(S)`, `q_{E,R}(x) in S`.

**Proof.** Both follow from the image construction: `S = q_{E,R}[C]` contains the
value of every `x in C` by definition of image, and a singleton image is the special
case. Because the registered candidacy filters are exact set restrictions, no
consistent world is ever excluded from `C`. `[]`

**Relation to KP-3B.** Exact coverage `1` is consistent with, and no weaker than,
the composed lower bound; the registered `beta_i` are declared budgets for possible
mis-registration of the relations, not realized error rates, so the bound is not
tight at this scope. The tightness of U-2B itself is parent-owned (#851) and is
re-exhibited here only as a control.

**Falsifiers.** Any (input, world) pair whose true value is outside the emitted
object; any identified set that omits a surviving value.

**Forbidden extrapolation.** This is exact coverage at the registered finite scope.
It is **not** a calibration-error measurement, not a held-out result, and not a
statement about any real system. `EMPIRICAL_CALIBRATION_ERROR_MEASURED` and
`OOD_FAILURE_MEASURED` remain forbidden.

---

## KP-4 — the null is strictly beaten

**Statement.** The null predictor `NULL_MARGINAL`, which emits the most common
`cap_E` value over the registered universe regardless of input, emits a point on
every grid input and incurs a strictly positive number of exact soundness
violations, where `F` incurs zero. The counts are reported in `RESULT_V1.json`.

**Why the comparison is fair.** Both are evaluated on the identical frozen grid with
the identical soundness test (KP-1B): a point `y` is a violation at an input iff some
`x in C` has `q_{E,R}(x) != y`. The null trades all of soundness for full coverage;
`F` trades coverage for exact soundness and reports exactly which inputs it declines
and why.

---

## Claim boundary

Allowed after green replay:

```text
GMI_833_EXACT_CAPABILITY_PREDICTOR_FAILURE_TAXONOMY_AND_TOTAL_UNCERTAINTY_AT_REGISTERED_FINITE_SCOPE
```

Not established here: held-out synthetic species, held-out known architectures, real
trained systems, pre-evaluation qualitative failure prediction, quantitative
resource/capability curve prediction, empirical calibration error, out-of-distribution
failure measurement, universal capability prediction, or complete GMI.

---

## Appendix — machine certificates (from `RESULT_V1.json`, after the census)

Numbers below are produced by the frozen scope and are reproducible with the
commands in `CORE.md`. They are recorded after the census; every predicate and
threshold they test was fixed in `FREEZE_V1.md` / `TAXONOMY_V1.md` / `SCOPE_V1.md`
before the executor existed.

| item | value |
|---|---|
| registered realizations | 32 |
| main grid inputs | 51,840 |
| emissions: point / abstain / inconsistent / cannot-check | 10,640 / 10,960 / 30,240 / 0 |
| semantics-defect sub-census (all `CANNOT_CHECK`) | 144 / 144 |
| exceptions on the grid | 0 |
| KP-1B soundness violations | 0 |
| KP-1C forced-abstention witness pairs | 10,960 / 10,960 |
| KP-2A ladder monotonicity violations | 0 |
| KP-2B overlaps / gaps | 0 / 0 |
| KP-2C unique-binding-cut violations | 0 |
| mode counts | information ceiling 5,400; expressivity 216; resource 5,976; reachability 2,442; search budget 2,004; observed shortfall 1,410; aliasing 3,529; none 623; inconsistent 30,240; cannot-check 144 (sub-census) |
| KP-2D order census | 8,640 inputs x 120 orders; 6,347 order-sensitive, 2,293 order-invariant |
| KP-2D individually-binding levers | 0 levers 6,104; 1 lever 1,867; 2 levers 669; >=3 levers 0 |
| KP-2D unique-lever cases | 1,379 order-invariant, 488 order-sensitive (the sharp counterexample class) |
| KP-3A bare returns / carrier construction sites | 0 / 1 |
| KP-3B confidence-budget mismatches | 0 |
| KP-3B feasible sets carrying coverage | 0 |
| KP-3B union bound vs independence product | 913/1000 vs 9152473869/10000000000 (product strictly larger, refused) |
| KP-3C coverage | 100,800 / 100,800 = exactly 1 |
| KP-4 null `NULL_MARGINAL` | 51,840 points, 51,840 soundness violations |
| route agreement | both routes agree on all 51,840 inputs and on every aggregate |
| tests | 35, green under `-B` and `-O -B` |

**Why the order-sensitivity number is what it is.** 6,104 of the 8,640 order-census
inputs have *no* single lever that restores attainability, which is exactly the
conjunctive regime in which no order-free "the" binding cut can exist. The
scientifically sharp part of the boundary is the 488 inputs that have a unique
individually-binding lever and are *still* order-sensitive; the shipped
counterexample is one of them (`K_M = {0}`, budget `(2,1,1)`, `B_dev = 2`,
`B = 12`, `tau = 1/6`: the only individually-binding lever is `Res`, yet the 120
orders produce the labels expressivity, reachability and resource). The
individually-binding-cut decomposition is a post-first-census diagnostic; it adds
reporting only and changes no frozen predicate.
