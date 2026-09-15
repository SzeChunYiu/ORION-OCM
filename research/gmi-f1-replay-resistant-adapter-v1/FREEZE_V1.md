# #657 freeze — replay-resistant ARC-6 adapter for the F1 capability assay

Date: 2026-09-15. Parent ledger: #602 section M. Child issue: #657.

This commit is the pre-implementation authority for this tranche. No scored adapter implementation, result receipt, or hostile test for this tranche exists on this branch before this file.

## Claim boundary

Target: a **conditional finite-record adapter** connecting the F1 paired-difference assay to the already-merged ARC-6 countable adaptive-row confidence theorem.

This tranche may establish only:

```text
REPLAY_RESISTANT_F1_ARC6_ADAPTER_AT_REGISTERED_SCOPE
SIMULTANEOUS_INTERVAL_COMPOSITION_WITHOUT_INDEPENDENCE_SHORTCUT
DEVELOPMENTAL_EVIDENCE_NONINHERITANCE_BY_DEFAULT
```

It may not establish physical sample freshness, iid sampling, a G6 capability predictor, real-world calibration, or universal validity under drift. Declared source IDs and tokens are bookkeeping objects; they cannot prove that external draws are genuinely fresh. The load-bearing statistical premise remains ARC-6's frozen conditional-mean contract.

## Strongest parents

Mechanism ownership remains with:

- ARC-6 in `research/gmi-countable-row-corrigendum-v1/FORMALIZATION_V1.md`;
- Hoeffding-style bounded conditional supermartingales and optional-stopping arguments;
- confidence-sequence / safe anytime-valid inference literature (Howard et al. 2021; Ramdas et al. 2023);
- ordinary simultaneous-confidence logic and deterministic interval arithmetic;
- adaptive-data-analysis work for the warning that reused data need a separate validity mechanism (Dwork et al. 2015).

The residual here is operational glue: preregistered F1 paired differences, reserve-before-observe provenance, single-use declared evidence, fail-closed developmental versioning, and exact interval/gate composition.

## Frozen statistical reduction

For every registered F1 comparison row, let the paired difference be

```text
d_t = u(M,w_t) - u(P,w_t) in [-1,1].
```

Define

```text
Y_t = (d_t + 1)/2 in [0,1].
```

If, on every attained predictable visit to row `j`,

```text
E[d_t | F_(t-1)] = mu_j,
```

then

```text
E[Y_t | F_(t-1)] = theta_j = (mu_j+1)/2.
```

Therefore the existing ARC-6 global event for `theta_j` transfers by the affine inverse map to a simultaneous interval for every finite attained paired-difference mean `mu_j`.

Use exactly the existing campaign allocation

```text
w_j = 1/[j(j+1)]
delta_(j,n) = alpha/[j(j+1)n(n+1)].
```

No new tail inequality or confidence-rate claim is introduced.

## Frozen campaign semantics

One campaign owns one fixed `alpha` and monotonically increasing, never-reused ARC-6 row indices.

A comparison contract is immutable and contains at least:

```text
comparison_id
capability_id
developmental_version
system_digest
parent_digest
twin_digest
tau_parent
tau_twin
```

Registering one comparison allocates exactly two rows, in order:

```text
positive
twin
```

A later comparison may be registered adaptively, but its contract is frozen before any evidence for either of its rows is reserved. Every row remains under the same campaign-wide `alpha`; unused allocations are not recycled.

A new developmental version is a new comparison contract and receives new row indices with zero inherited visits. Old statistical evidence is not transported unless a separate theorem explicitly licenses such transport.

## Frozen provenance state machine

For a row, evidence can enter only through:

```text
REGISTERED -> RESERVE(origin_id, token) -> OBSERVE(origin_id, token, d)
```

Rules:

1. reservation occurs before observation enters the adapter;
2. `origin_id` is globally single-use within the campaign;
3. `token` is globally single-use within the campaign;
4. a repeated read of a consumed token adds no evidence;
5. an observation with no matching reservation is rejected;
6. a missing or malformed reserved outcome retires the row;
7. acquisition charge is incurred at reservation and survives retirement;
8. retirement prevents later evidence from reviving the row;
9. token/origin uniqueness is only a declared-provenance invariant, not proof of external freshness.

Malformed means a non-exact score or a paired difference outside `[-1,1]`.

## Frozen F1 gate

Let `[L_+,U_+]` be the simultaneous ARC-6 interval for the positive paired-difference mean and `[L_-,U_-]` the interval for the negative twin.

A comparison is `SUPPORTED` only if

```text
L_+ > tau_parent
and
L_- >= -tau_twin
and
U_- <=  tau_twin.
```

If either row is retired, report `CANNOT_IDENTIFY_RETIRED`.

If `U_+ <= tau_parent`, report `PARENT_NOT_SEPARATED`.

If `[L_-,U_-]` is disjoint from `[-tau_twin,+tau_twin]`, report `TWIN_NOT_COLLAPSED`.

All other cases report `CANNOT_IDENTIFY`.

This is a soundness gate, not a forced-decision rule.

## Frozen simultaneous-composition theorem target

On one global event `G`, every primitive row mean lies in its reported interval. For a preregistered affine derived quantity

```text
z = b + sum_i a_i mu_i,
```

the exact interval enclosure is

```text
z_lo = b + sum_i min(a_i L_i, a_i U_i)
z_hi = b + sum_i max(a_i L_i, a_i U_i).
```

On `G`, `z` lies in `[z_lo,z_hi]`. No independence between rows is needed because coverage is inherited from the same simultaneous event. Derived affine contracts must be frozen before acquisition on any referenced row; post-hoc weights are rejected.

The proof document must also state the general deterministic image-set version: any sound enclosure of a function over the Cartesian product of simultaneous primitive intervals preserves the same global coverage event. It must not claim that naive marginal intervals compose at their original nominal level without a simultaneous event.

## Frozen exact positive/control campaign

Use:

```text
alpha = 1/20
tau_parent = 1/2
tau_twin = 1/4
```

For the first registered comparison (`positive` row index 1, `twin` row index 2):

- reserve and observe 1024 distinct declared origins/tokens with `d=1` on the positive row;
- reserve and observe 1024 distinct declared origins/tokens with `d=0` on the twin row.

Frozen expected terminal: `SUPPORTED`.

Also freeze a derived affine contract

```text
contrast = mu_positive - mu_twin.
```

Its reported interval must contain the exact value `1`.

A small-prefix control using the first 64 observations per row must not be promoted to `SUPPORTED` under these thresholds.

## Frozen adversarial controls

At minimum the test suite must demonstrate:

1. observation before reservation is rejected;
2. token replay is rejected and does not increment visits;
3. duplicate declared origin under a fresh token is rejected;
4. malformed paired difference retires the row, leaves visits unchanged, and keeps its acquisition charge;
5. an explicitly missing reserved outcome retires the row and keeps its acquisition charge;
6. a new developmental version starts with zero visits and cannot inherit old row evidence;
7. adaptive registration of a later comparison receives fresh larger row indices under the same `alpha`;
8. affine interval composition is exact against exhaustive corner enumeration on a finite rational test family;
9. a derived contract registered after referenced acquisition has begun is rejected;
10. two individually 95%-covered intervals are not treated as a 95% joint event merely because each marginal says 95%; include a finite disjoint-failure counterexample with only 90% joint coverage;
11. distinct declared origin strings carrying a cached repeated physical draw can pass the metadata checks, demonstrating that provenance strings do not prove ARC-6's conditional-mean premise;
12. normal and `python -O` runs produce the same deterministic receipt.

## Frozen falsifiers

This tranche fails if any of the following occurs:

- replay or unreserved evidence increases a row's visit count;
- retirement erases already incurred acquisition charge;
- a new developmental version inherits visits without a separately registered transport theorem;
- the adapter reports `SUPPORTED` when the simultaneous intervals do not imply both F1 gates;
- affine interval composition misses any exact corner value;
- a post-outcome derived weight is accepted;
- the implementation silently assumes row independence;
- it claims declared token uniqueness proves physical sample freshness;
- the committed deterministic receipt differs under normal versus optimized Python.

No #602 checkbox is to be changed merely because this freeze exists. Closure requires implementation, hostile tests, deterministic receipt reproduction, repository CI, and review of the claim boundary.