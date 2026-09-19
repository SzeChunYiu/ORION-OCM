# Scalable sampling theorems V1

## Definitions

Fix an exact positive budget `B=(N,R)`. For each `1<=n<=N` and `1<=r<=R`,
let `Q_(n,r)` be the ordered instruction alphabet used by #966 and let

```text
q(n,r) = |Q_(n,r)| = 1 + 3rn + rn^2,
H_(n,r) = q(n,r)^n.
```

Order strata with `r` outermost and `n` innermost. Let `o_h` be the exact sum
of sizes of all preceding strata and `M=sum_h H_h`.

## T1 — disjoint finite stratification

The #966 population is the disjoint union of the `NR` strata
`Q_(n,r)^n`. Distinct strata differ in declared label count or register count,
and each within-stratum Cartesian power has exactly `q(n,r)^n` members.
Therefore the union has exactly `M` members.

## T2 — exact rank/unrank bijection

Map each instruction to its index in `Q_(n,r)`. A table's instruction indexes
are an `n`-digit base-`q(n,r)` numeral `ell` in `[0,H_(n,r))`; define global
rank `o_h+ell`. Disjoint half-open prefix intervals make the global map
injective. Euclidean division uniquely recovers the `n` digits of every local
rank, and the unique prefix interval recovers the stratum, proving
surjectivity. The arithmetic digit map is proved equal to #966's explicit
instruction order by exhaustive tests at four small budgets.

## T3 — population-size scalability

Constructing the stratum table uses `O(NR)` big-integer operations and stored
integers. Rank/unrank adds `O(n)` digit work (plus prefix lookup). Neither work
nor storage performs an `O(M)` population scan, although big-integer bit cost
necessarily depends on `log M`. Floyd uses exactly `k` ideal draw-oracle calls,
`O(k)` working memory, and expected `O(k log k)` time here because the returned
ranks are sorted. Materializing `k` candidates costs only the sum of their
label counts. This is scalability in population cardinality, not a constant-
time claim in budget dimensions, integer bit length, or adversarial hash cost.

## T4 — Floyd SRSWOR is uniform

At step `j`, Floyd draws `t` uniformly from `{0,...,j}`. If `t` is absent it
is inserted; otherwise `j` is inserted. Inductively, after processing through
`j`, every subset of the current size in `{0,...,j}` has the same number of
draw histories: subsets containing `j` arise either from the collision branch
or the unique predecessor obtained by removing `j`; subsets omitting `j`
arise from their unique selected `t`. Thus the final `k`-subset is uniform
among the `C(M,k)` subsets. The independent registered `M=5,k=2` oracle
exhausts all 20 draw traces and obtains each of the 10 subsets twice.

## T5 — inclusion probabilities and miss coverage

Uniform subset counting gives

```text
pi_i  = C(M-1,k-1)/C(M,k) = k/M,
pi_ij = C(M-2,k-2)/C(M,k) = k(k-1)/(M(M-1)).
```

For a fixed qualifying subset of size `A`, exactly `C(M-A,k)` samples miss it,
so `P(miss)=C(M-A,k)/C(M,k)` when `k<=M-A`, and zero otherwise. This exposes a
hostile boundary: a very small scientific niche can have high miss
probability even though the global design is candidate-uniform.

For positive stratification, if the predicate has `A_h` members in stratum
`h`, independent within-stratum draws give the exact miss probability
`product_h C(H_h-A_h,m_h)/C(H_h,m_h)`, with a zero factor whenever
`m_h>H_h-A_h`.

## T6 — Horvitz–Thompson unbiasedness

For fixed values `y_i`, the estimator of the population total is
`sum_(i in S) y_i/pi_i`. Taking expectations and using the indicator identity
`E[1{i in S}]=pi_i` yields `sum_i y_i`. No outcome distribution or
independence of the `y_i` is required; the fixed registered population is the
scope.

## T7 — positive stratified design

Reserve one draw per nonempty stratum, then apportion the remaining
`k-NR` draws over residual capacities `H_h-1` by exact Hamilton largest
remainders. When `NR<=k<=M`, quotas do not exceed capacity; floors plus at most
one residual unit remain within capacity and sum to `k`. Independent
within-stratum SRSWOR gives

```text
pi_(i in h) = m_h/H_h,
pi_(ij in h) = m_h(m_h-1)/(H_h(H_h-1)),
w_i = H_h/m_h.
```

Every stratum is represented because `m_h>=1`. Across different strata,
independent ideal draws give product pair inclusion. This guaranteed
stratum-level coverage is bought by unequal individual inclusion
probabilities, which the weights expose.

## T8 — deterministic replay boundary

Rejection of uniform bit strings above the largest accepted multiple/range is
an exact uniform-integer construction under ideal independent fair input bits.
The committed counter-hash stream fixes an operational transcript and permits
byte-stable replay, but a fixed transcript is not random and SHA-256 is not
proved here to instantiate physical IID entropy. All inclusion and coverage
probabilities therefore describe the declared randomized design, not the one
realized fixed seed in isolation.

## Claim boundary

These theorems concern a finite syntax population under the registered
`G0-fin-v1` grammar. They do not prove semantic-uniformity, naturalness of the
grammar, unbounded sampling, adequacy for every unknown niche, 10^6 or 10^8
candidate execution, QD/open-ended search, or external validity.
