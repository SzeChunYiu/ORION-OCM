# GMI Section D V5 — Boundary Uncertainty + Out-of-Scale Extrapolation Freeze

Date frozen: 2026-09-14.  
Parent ledger: #602.  
Child tracker: #681.  
Base: merged V4 `2aa5fbcef337731111b9d8da2f17adc1091d6818`.

This file is the **stage-1 pre-data authority**. It must exist in Git history before:

- the uncertainty sample is acquired;
- any tiny-size training measurements are committed;
- any affine coefficients are fitted;
- any held-out size `n=17` or `n=31` is executed.

The two claims under test are deliberately distinct:

1. **uncertainty:** if an ecology coordinate is estimated from finite data, propagate a preregistered nonasymptotic interval into a phase-boundary interval rather than reporting a point crossover as exact;
2. **extrapolation:** fit a registered operation law only on tiny worlds, freeze the resulting larger-world predictions in a second Git commit, and only then inspect the held-out larger worlds.

Even a perfect pass is limited to:

```text
FINITE_PROSPECTIVE_PHASE_BOUNDARY_CONFIDENCE_INTERVAL
FINITE_PROSPECTIVE_OUT_OF_SCALE_PHASE_LAW_EXTRAPOLATION
PARENT_OWNED_CONCENTRATION_INDEXING_AMORTIZATION
NO_REAL_WORLD_COVERAGE_UNIVERSAL_SCALING_OR_REAL_SCALE_CLAIM
```

---

## 1. Strongest-parent first refusal

The result document must parent-subtract at least:

- W. Hoeffding, *Probability Inequalities for Sums of Bounded Random Variables*, JASA 58(301), 1963, DOI `10.2307/2282952` / `10.1080/01621459.1963.10500830`;
- P. G. Selinger et al., *Access Path Selection in a Relational Database Management System*, SIGMOD 1979, DOI `10.1145/582095.582099`;
- R. M. Karp, R. Motwani, P. Raghavan, *Deferred Data Structuring*, SIAM J. Comput. 17(5), 1988, DOI `10.1137/0217055`;
- classical concentration inequalities, confidence-set propagation, indexing, preprocessing/query tradeoffs and amortization.

No confidence theorem, access-path result, indexing mechanism, or affine scaling law is claimed as GMI novelty. The only candidate residual is the governance protocol that places explicit uncertainty and prospective out-of-scale validation inside the same architecture-neutral morphology phase ledger.

---

# PART U — phase-boundary uncertainty

## 2. Registered mechanism and ecology model

There are four opaque key/value pairs under an exact bijection. An inherited key-oriented index is installed. The future choice is:

```text
A = keep key_index
B = pay 8 future operations to migrate to value_index.
```

Serving costs are frozen:

```text
                 forward     reverse
key_index           1           4
value_index         4           1
```

Let `X_i=1` mean reverse and `X_i=0` mean forward. The registered synthetic ecology model is:

```text
X_i iid Bernoulli(p)
p = 7/8.
```

This is a controlled synthetic sampling model. It is **not** evidence that a real workload is iid Bernoulli and cannot support a real-world coverage claim.

Expected per-query costs are:

```text
E[C_key]   = (1-p)*1 + p*4 = 1 + 3p
E[C_value] = (1-p)*4 + p*1 = 4 - 3p.
```

So value's expected serving advantage is:

```text
Delta(p) = E[C_key-C_value] = 6p - 3 = 3(2p-1).
```

For `p>1/2`, the continuous expected-cost migration boundary is:

```text
q*(p) = 8 / Delta(p).
```

At the preregistered true ecology:

```text
p = 7/8
Delta = 9/4
q* = 32/9 ~= 3.555555...
```

The first integer horizon at which migration is **strictly** cheaper is therefore `Q=4`.

## 3. Raw-sample acquisition frozen before acquisition

After this freeze exists, acquire exactly `N=16384` bytes using Python's OS-backed `secrets.token_bytes(16384)`.

Map each byte independently to a registered Bernoulli observation by:

```text
X_i = 1 iff raw_byte_i < 224
X_i = 0 otherwise.
```

Because `224/256 = 7/8`, this maps a uniform byte to Bernoulli(7/8) exactly under the registered random-byte model.

Pack the resulting bits in observation order, eight observations per output byte, most-significant observation bit first. Commit a raw-data JSON containing at least:

```text
n = 16384
packing = "MSB_FIRST_8"
threshold = 224
packed_bits_hex
ones_count
packed_sha256
```

The acquired observations are immutable experimental data. The later witness must verify their length, bit count and SHA-256 digest but must **not** regenerate them.

No seed is frozen. The point of the post-freeze acquisition is that the realized count is genuinely unavailable to this authority.

## 4. Full-sample confidence rule

The analysis is frozen as a two-sided Hoeffding interval with fixed half-width:

```text
N = 16384
epsilon = 1/64
p_hat = ones_count / N
p_lo = max(0, p_hat - epsilon)
p_hi = min(1, p_hat + epsilon).
```

Hoeffding gives:

```text
P(|p_hat-p| >= epsilon)
<= 2 exp(-2 N epsilon^2)
= 2 exp(-8)
< 0.001.
```

So, under the registered iid Bernoulli model, the interval has coverage at least:

```text
1 - 2 exp(-8) > 0.999.
```

The receipt must report the bound itself. It may additionally report decimals, but it may not replace the bound with a normal/Wald approximation.

## 5. Propagating the confidence interval into phase space

If `p_lo <= 1/2`, the data are insufficient to certify a finite positive migration boundary and the full-sample localization prediction fails.

Otherwise define:

```text
Delta_lo = 6 p_lo - 3
Delta_hi = 6 p_hi - 3
q_lo = 8 / Delta_hi
q_hi = 8 / Delta_lo.
```

Monotonicity of `q*(p)` for `p>1/2` means `[q_lo,q_hi]` is the registered boundary confidence interval induced by the Hoeffding set.

### Frozen U predictions

The post-freeze random sample passes only if:

```text
U1  p=7/8 lies in [p_lo,p_hi].
U2  q*=32/9 lies in [q_lo,q_hi].
U3  [q_lo,q_hi] is strictly contained in (3,4).
U4  therefore every p in the reported confidence set implies the same first strict integer migration horizon Q=4.
U5  nominal failure bound is reported as 2 exp(-8) < 0.001.
```

If U1/U2 fail, retain the prospective statistical miss; do not widen epsilon after seeing the sample.

## 6. Small-sample uncertainty negative control

Use **only the first 64 committed observations**. No resampling.

Frozen interval:

```text
N_small = 64
epsilon_small = 1/4.
```

This has the same Hoeffding exponent:

```text
2*N_small*epsilon_small^2 = 8,
```

so its registered failure bound is also `2 exp(-8)`.

Apply the same clipping and boundary propagation if its lower p bound exceeds 1/2. If its lower bound is at or below 1/2, record the phase-boundary upper side as unbounded rather than fabricating a finite number.

### Frozen negative-control prediction U6

The small-sample phase-boundary set must **not** be strictly contained in `(3,4)` and therefore must not uniquely localize the strict integer transition to Q=4.

This is required evidence that the uncertainty machinery responds to information quantity rather than simply returning the preregistered answer.

---

# PART X — extrapolation beyond fitted tiny worlds

## 7. Generic exact indexing mechanism

For an integer size `n>=2`, define opaque tokens:

```text
K_n = {k0,...,k_{n-1}}
V_n = {v0,...,v_{n-1}}.
```

The registered relation is the cyclic bijection:

```text
rho_n(k_i) = v_{(i+1) mod n}.
```

The two single-orientation mechanisms are generic implementations, not size-specific formulas:

### `key_index`

- retain `rho_n` by key;
- forward lookup reads one indexed payload and charges 1 op;
- reverse lookup scans **all n entries**, even after finding the answer, and charges n ops.

### `value_index`

- retain the inverse relation by value;
- reverse lookup reads one indexed payload and charges 1 op;
- forward lookup scans **all n entries** and charges n ops.

### migration

Actual key->value reindexing iterates every retained key entry and performs:

```text
one read + one opposite-orientation write per pair.
```

The training/holdout measurement records the executed operation counter. No hand-written `2*n` value may be substituted into the measurement receipt.

Each held-out implementation must also answer all `2n` distinct forward/reverse token queries exactly.

## 8. Registered training workload

At every size, the operation-count block has direction multiplicities:

```text
3 forward
4 reverse.
```

Concrete token requests are generated mechanically from the size but are excluded from the extrapolation predictor; only direction counts and measured numeric receipts matter.

## 9. Tiny training set

Only these sizes are legal before the second freeze:

```text
TRAIN = {2,3,4,5}.
```

The training measurement must record exactly five numeric columns:

```text
n
persistent_cells_single_orientation
migration_ops
key_block_ops
value_block_ops.
```

No measurement at any other size is allowed before `FIT_AND_HOLDOUT_FREEZE_V5.md` is committed.

## 10. Frozen fitting algorithm

For each of the four dependent coordinates independently:

1. let the observations at `n=2` and `n=3` be `(2,y2)` and `(3,y3)`;
2. fit the affine law `y(n)=a*n+b` exactly as rational/integer arithmetic:
   - `a = y3-y2`;
   - `b = y2-2a`;
3. predict `n=4` and `n=5`;
4. require zero residual at both validation sizes;
5. if either residual is nonzero, X preregistration fails and **no polynomial/higher-order refit is permitted**.

The predictor sees only the numeric training tuples. It does not receive token names, implementation source labels, or a hand-written asymptotic formula.

## 11. Second-stage freeze requirement

After training measurements exist and the affine fits pass internal validation, commit:

```text
FIT_AND_HOLDOUT_FREEZE_V5.md
```

before any held-out execution.

That file must contain:

- the immutable training receipt hash;
- all four fitted `(a,b)` coefficient pairs;
- explicit numeric predictions at `n=17` and `n=31` for all four coordinates;
- the predicted inherited-key crossover horizon derived only from those fitted coordinates;
- predicted winners immediately below and at/above the strict crossover.

If a held-out size is executed before that commit exists, the extrapolation box is not earned.

## 12. Held-out sizes

Only after the second freeze:

```text
HOLDOUT = {17,31}.
```

These are 3.4x and 6.2x the largest fitted size.

At each holdout the scored witness must:

1. build the registered opaque cyclic bijection;
2. execute and instrument both orientations on the 3F/4R block;
3. execute key->value migration and count operations;
4. verify all `2n` distinct exact lookups for both orientations;
5. compute the inherited-key lifecycle ordering over integer block horizons around the second-freeze predicted crossover;
6. compare every observed coordinate and winner to the second-freeze prediction with **zero tolerance**.

No refit after holdout is allowed.

## 13. Disjoint remint

For each holdout independently apply token renamings that alter spelling and order:

```text
key index i -> "amber_<n-1-i>"
value index i -> "quartz_<(i+5) mod n>".
```

These are bijective for every registered n. Relation edges and queries are renamed consistently.

Exact answers, instrumented operation counts, fitted-law comparisons and crossover winner must remain unchanged.

## 14. Anti-leakage / implementation controls

The final witness must expose separately:

```text
training numeric receipt
fitted coefficients
second-freeze predictions
held-out observations
comparison booleans.
```

The held-out evaluator may use the generic mechanism implementations but may not call the fitted predictor to manufacture observed operation counts.

A hostile test must mutate one second-freeze prediction in memory and show that the comparator detects the mismatch.

---

## 15. Frozen pass ledger

### Uncertainty

```text
U1 full sample contains true p.
U2 induced q interval contains true 32/9.
U3 full q interval lies strictly in (3,4).
U4 integer strict crossover localized to Q=4 across full confidence set.
U5 nonasymptotic failure bound 2e^-8 < 0.001 reported.
U6 first-64 negative control does not localize boundary to (3,4).
U7 raw packed sample length/count/hash reproduce exactly.
```

### Extrapolation

```text
X1 training execution is restricted to n={2,3,4,5}.
X2 affine fits from n=2,3 have zero residual at n=4,5.
X3 second-stage freeze predates any n=17/31 scored receipt.
X4 n=17 observed persistent/migration/key-block/value-block counts exactly match frozen extrapolation.
X5 n=31 observed counts exactly match frozen extrapolation.
X6 predicted inherited-key crossover/winners match n=17.
X7 predicted crossover/winners match n=31.
X8 both orientations exact on all 34 held-out queries at n=17 and all 62 at n=31.
X9 disjoint remints preserve exactness, counts and winner.
X10 hostile altered-prediction comparator fails closed.
```

Any failed frozen prediction remains a failure. Do not adjust epsilon, fit family, training set, holdout sizes, or predicted coefficients after outcomes.

---

## 16. Box and scope disposition

A clean pass can support, at this synthetic finite scope:

```text
[x] Quantify uncertainty in phase-boundary location.
[x] Test phase-law extrapolation beyond fitted tiny worlds.
```

It cannot support:

- real-world statistical coverage;
- empirical hardware-runtime scaling;
- arbitrary-function extrapolation;
- a complete ecology/resource coordinate schema;
- universal scaling laws;
- real-scale morphology transfer.
