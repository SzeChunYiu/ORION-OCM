# Replay-resistant F1 / ARC-6 adapter — formalization V1

Issue #657; parent ledger #602 section M. Pre-implementation authority: `FREEZE_V1.md` committed as `ac6fccf148140e4481f822c797f55c66791936d2` before the adapter, tests, or scored receipt.

**Scope.** Conditional finite-record adapter for bounded paired F1 comparisons. Statistical validity inherits ARC-6's fixed-per-row conditional-mean premise and one countable global confidence event. The adapter adds operational provenance invariants, exact paired-difference mapping, fail-closed developmental versioning, deterministic interval composition, and abstaining F1 gate semantics.

**Evidence classes.** RR-1, RR-3, RR-4 and RR-5 are P1 deterministic statements about the registered state machine / interval map. RR-2 is a P3 probability guarantee inherited from ARC-6 plus a P1 affine reduction. The finite hostile suite and receipt are P2 executable checks. No P4 empirical capability claim is made.

**Claim ceiling.** `CONDITIONAL_FINITE_RECORD_ADAPTER_NOT_G6`.

## 1. Objects and quantifiers

Fix one campaign confidence budget `alpha in (0,1)`. Comparison contracts may be created adaptively. A contract is frozen before evidence is reserved for either of its two rows and contains its comparison identity, capability identity, developmental version, system/parent/twin digests and margins `tau_parent`, `tau_twin`.

Registering the k-th comparison creates two never-reused ARC-6 rows with consecutive creation indices. More generally write `j=1,2,...` for the campaign creation order. All rows share one campaign `alpha`; no confidence mass is recycled.

On an attained visit to row `j`, the registered F1 datum is the paired utility difference

```text
d_t = u(M,w_t) - u(P,w_t) in [-1,1].
```

Let `(F_t)` be the filtration containing all past observations, controller choices and already-used randomness. The load-bearing external statistical premise is exactly

```text
E[d_t | F_(t-1)] = mu_j
```

whenever row `j` is selected predictably at step `t`, for a row parameter `mu_j` frozen by the row contract. Global iid sampling and independence between rows are not assumed. Arbitrary dependence without this conditional-mean property is not covered.

The adapter's string-valued `origin_id` and `token` fields do not establish this premise. They only constrain what the software will count as evidence.

## 2. RR-1 — reserve-before-observe provenance invariant [P1]

For every execution trace accepted by `Campaign`, the following invariants hold:

1. each counted observation has a prior live reservation for the same `(row, origin_id, token)`;
2. each declared `origin_id` is reserved at most once campaign-wide;
3. each declared `token` is reserved at most once campaign-wide;
4. a consumed token cannot increment any visit count again;
5. acquisition charge is incremented at successful reservation, before outcome validity is known;
6. retirement never decrements acquisition charge;
7. malformed or explicitly missing reserved outcomes retire the affected row without incrementing its visit count;
8. retired rows cannot accept later reservations or observations.

**Proof.** Initially all global origin/token sets are empty, all row visit/charge counters are zero, and no row is retired. `reserve` is the only operation that adds an origin/token to the global sets or increments acquisition charge. It first rejects a retired row and any previously present origin/token, then inserts each identifier exactly once and increments charge exactly once. `observe` is the only operation that increments visits; it calls `_consume`, which requires a live pending reservation with matching origin and removes that reservation before inspecting the value. Therefore the same reservation cannot be consumed twice. If the value is not an exact `Fraction` in `[-1,1]`, `_retire` is called and visits are not incremented. `mark_missing` likewise consumes one live reservation and retires without incrementing visits. `_retire` clears remaining pending reservations but never changes charge, and every later reserve/consume checks the retired flag. Induction on the operation trace preserves all eight invariants. QED.

**Nearest false generalization.** These invariants do not imply that two different origin strings are two physically fresh random draws. An external sampler can lie. The hostile control deliberately submits the same apparent value under four distinct declared origins and the adapter accepts all four bookkeeping records; this is evidence that the implementation does **not** pretend metadata proves the ARC-6 premise.

## 3. RR-2 — paired-difference simultaneous confidence bridge [P1/P3]

Define

```text
Y_t = (d_t + 1)/2.
```

Then `Y_t in [0,1]` and, on visits to row `j`,

```text
E[Y_t | F_(t-1)] = theta_j := (mu_j+1)/2.
```

ARC-6 allocates

```text
w_j = 1/[j(j+1)]
delta_(j,n) = alpha/[j(j+1)n(n+1)]
```

and provides, with probability at least `1-alpha`, one event `G_Y` on which every finite attained row/look interval `[L^Y_(j,n), U^Y_(j,n)]` contains `theta_j`.

The adapter reports

```text
L^d_(j,n) = 2 L^Y_(j,n) - 1
U^d_(j,n) = 2 U^Y_(j,n) - 1.
```

### Theorem RR-2

For every process satisfying the stated conditional-mean premise,

```text
P( for all j,n attained: mu_j in [L^d_(j,n), U^d_(j,n)] ) >= 1-alpha.
```

**Proof.** The map `g(y)=2y-1` is strictly increasing and `mu_j=g(theta_j)`. On `G_Y`, `theta_j` lies in every attained ARC-6 interval; monotonicity gives `g(theta_j)` between the transformed endpoints. Thus the paired-difference global event contains `G_Y` and has probability at least `1-alpha`. No additional union bound and no row-independence assumption is introduced. QED.

This theorem inherits ARC-6's all-finite-attained-visits boundary. It does not promise eventual sampling, eventual narrow intervals, safe infinite deployment cost, physical sample authentication, or validity after an unregistered change in the row's conditional mean.

## 4. RR-3 — simultaneous F1 parent/twin gate soundness [P1/P3 consequence]

For one comparison let the positive-row true mean be `mu_+`, the twin-row true mean be `mu_-`, with simultaneous intervals

```text
mu_+ in [L_+,U_+]
mu_- in [L_-,U_-].
```

The adapter emits `SUPPORTED` only if

```text
L_+ > tau_parent,
L_- >= -tau_twin,
U_- <=  tau_twin.
```

### Theorem RR-3

On the RR-2 global event, every emitted `SUPPORTED` terminal satisfies

```text
mu_+ > tau_parent
and
|mu_-| <= tau_twin.
```

Consequently, over the entire campaign and every finite attained look, the probability that the adapter ever emits `SUPPORTED` while either of those two mean-level conclusions is false is at most `alpha`, provided the ARC-6 premise holds.

**Proof.** On the global event, `mu_+ >= L_+ > tau_parent`. Also `L_- <= mu_- <= U_-` and the gate places the whole twin interval inside `[-tau_twin,+tau_twin]`, hence `|mu_-|<=tau_twin`. This deterministic implication holds simultaneously for every registered row/look already covered by RR-2. Therefore a false support terminal can occur only on the complement of the global event, whose probability is at most `alpha`. QED.

The other terminals are deliberately conservative. `PARENT_NOT_SEPARATED` requires `U_+ <= tau_parent`; `TWIN_NOT_COLLAPSED` requires the twin interval to be disjoint from the allowed band. Partial overlap yields `CANNOT_IDENTIFY`. A retired input row yields `CANNOT_IDENTIFY_RETIRED`.

## 5. RR-4 — deterministic interval composition without an independence shortcut [P1]

Let primitive parameters `mu_1,...,mu_k` have simultaneous intervals `I_i=[L_i,U_i]` on one event `G`. Let `f` be any deterministic derived quantity and let `J` be any sound enclosure satisfying

```text
f(x_1,...,x_k) in J
```

for every `x_i in I_i`.

Then on `G`, `f(mu_1,...,mu_k) in J`. This is immediate because the true vector belongs to the Cartesian product of the primitive intervals on `G`. No distributional independence is used.

For the registered affine case

```text
z = b + sum_i a_i mu_i,
```

the exact enclosure is

```text
z_lo = b + sum_i min(a_i L_i, a_i U_i)
z_hi = b + sum_i max(a_i L_i, a_i U_i).
```

### Theorem RR-4A — exactness of the affine enclosure

`[z_lo,z_hi]` is the smallest closed interval containing the affine image of the axis-aligned box `prod_i I_i`.

**Proof.** Each coordinate contributes independently to the affine objective. If `a_i>=0`, its minimum contribution is `a_i L_i` and maximum is `a_i U_i`; if `a_i<0` those endpoints reverse. Summing coordinatewise minima gives the global minimum and summing maxima gives the global maximum. Both are attained at box corners, so the bounds are exact. QED.

The hostile suite exhaustively enumerates all corners of finite rational boxes and matches the independent formula.

### Why marginal confidence labels are insufficient

Take 20 equiprobable atoms. Interval A fails only on atom 0 and interval B fails only on atom 1. Each marginal covers on `19/20 = 95%` of the atoms, but both cover together on only `18/20 = 90%`. Thus two labels saying “95%” do not imply a 95% joint event. RR-4 is safe here specifically because ARC-6 supplies one simultaneous event across rows/looks.

The implementation additionally requires affine weights to be registered before any referenced acquisition. This preregistration constraint is scientific governance against post-outcome coordinate choice; the deterministic enclosure theorem itself would remain algebraically true for a later-chosen weight.

## 6. RR-5 — developmental version noninheritance [P1]

Registering a new `(comparison_id, developmental_version)` creates two new row objects with fresh, larger creation indices, zero visits, zero mapped sum and zero acquisition charges. The API exposes no operation that copies old row observations into a new row.

### Theorem RR-5

Under the adapter state machine, changing developmental version cannot silently inherit old statistical evidence.

**Proof.** `register_comparison` allocates new `_RowState` instances initialized at their dataclass defaults and stores them under a row identity containing the new version. Global token/origin sets remain spent, so old reservation identifiers cannot be reused. No method mutates a new row's sum/visits except `observe` following a new live reservation. Therefore the new version starts with no old evidence and can gain evidence only through new reserved observations. QED.

This is a fail-closed update rule, not a theorem that old uncertainty has been transported through the developmental change. A scientifically justified transport map or drift theorem would be a separate registered mechanism.

## 7. Epistemic versus aleatoric uncertainty at this adapter scope

The distinction is explicit but narrow:

- **Aleatoric variability** is variation of the future paired outcome `d_t` under the registered row-generating process, conditional on the past. ARC-6 assumes only bounded support plus a fixed row conditional mean; this adapter does not estimate a variance decomposition.
- **Epistemic sampling uncertainty** here is uncertainty about the fixed conditional mean `mu_j` after finitely many attained visits, represented by the ARC-6 interval.

A wide interval can arise from few visits / severe multiplicity allocation even when outcomes are deterministic. Conversely, intrinsically variable outcomes need not imply a permanently wide mean interval if the conditional-mean premise is stable and visits accumulate. The two concepts therefore must not be identified.

This local distinction does not by itself close every #602 Section-M uncertainty obligation across all morphology/capability/developmental claims.

## 8. Exact frozen control

The freeze registered

```text
alpha = 1/20
tau_parent = 1/2
tau_twin = 1/4
n_+ = n_- = 1024
d_+ = 1 on every positive observation
d_- = 0 on every twin observation.
```

The deterministic receipt reports

```text
positive interval = [197/256, 1]
twin interval     = [-15/64, 15/64]
decision          = SUPPORTED
contrast interval = [137/256, 79/64]
```

The exact contrast truth `1` lies inside the derived interval. With only 64 observations per row the terminal is `CANNOT_IDENTIFY`, so the positive result is not hard-coded independently of evidence amount.

Malformed and missing controls each incur one acquisition charge, zero accepted visits, and a retired terminal. A new developmental version receives row indices 3 and 4 and starts at `[0,0]` visits. Replay, duplicate-origin and post-outcome derived registration are rejected.

## 9. Verification and falsifiers

`test_replay_resistant_f1_v1.py` contains 28 exact/adversarial controls covering contract immutability, adaptive row numbering, reserve-before-observe, replay, duplicate origin/token, wrong-origin handling, malformed/missing retirement, preserved charges, the metadata/freshness boundary, exact ARC-6 affine mapping, positive/abstention/refutation terminals, exact affine corner enclosure, preregistration of derived weights, retired-input invalidation, marginal-vs-joint coverage, developmental noninheritance and deterministic receipt reproduction.

The workflow runs the suite and receipt comparison under both normal Python and `python -O`. It also verifies that freeze commit `ac6fccf148140e4481f822c797f55c66791936d2` is an ancestor and that the freeze commit changed only `FREEZE_V1.md`.

Falsifiers include any accepted replay that increments visits, erased acquisition charge on retirement, silent evidence inheritance across versions, `SUPPORTED` without interval implication of both gates, an affine corner outside the reported derived interval, acceptance of a post-acquisition derived contract, or optimized-mode receipt drift.

A process satisfying ARC-6's stated conditional-mean premises for which the reported global error exceeds `alpha` would falsify the inherited statistical theorem, not merely this adapter. Conversely, a cached/reused physical draw that violates the conditional-mean premise is a premise failure and must not be presented as evidence against or for the bound.

## 10. Parent subtraction and literature anchors

No statistical novelty is claimed. The result is deliberately subordinate to:

- Howard, Ramdas, McAuliffe & Sekhon (2021), *Time-uniform, nonparametric, nonasymptotic confidence sequences*, Annals of Statistics 49(2), 1055–1080, DOI `10.1214/20-AOS1991`;
- Ramdas, Grünwald, Vovk & Shafer (2023), *Game-Theoretic Statistics and Safe Anytime-Valid Inference*, Statistical Science 38(4), 576–601, DOI `10.1214/23-STS894`;
- Dwork, Feldman, Hardt, Pitassi, Reingold & Roth (2015), *Generalization in Adaptive Data Analysis and Holdout Reuse*, for the separate problem created by adaptively reusing fixed data;
- the repository's merged ARC-6 proof for countable adaptive row birth and all finite attained visits.

The only retained contribution of this capsule is the exact operational adapter and its fail-closed research governance at the stated finite-record scope.
