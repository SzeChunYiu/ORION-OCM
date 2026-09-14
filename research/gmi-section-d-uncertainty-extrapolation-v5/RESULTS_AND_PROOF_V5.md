# Section D V5 — Boundary Uncertainty and Out-of-Scale Extrapolation

Stage-1 pre-data authority: `FREEZE_V5.md` at commit `ab231d78aae98beb679ca0e0ce8c36c4651dc438`.  
Stage-2 pre-holdout authority: `FIT_AND_HOLDOUT_FREEZE_V5.md` at commit `0a153e972dd920f61f394ce117d5dfa189ad964f`.

Executable authority: `section_d_uncertainty_extrapolation_witness.py` -> `RESULT_V5.json`.

## Executive disposition

Every frozen V5 prediction passes at the registered synthetic finite scope.

The two results are intentionally different kinds of evidence:

1. **Boundary uncertainty:** a post-freeze random sample estimates a stochastic ecology coordinate. A fixed nonasymptotic Hoeffding interval is propagated into an interval for the morphology crossover. The full sample localizes the integer transition; a preregistered first-64 negative control does not.
2. **Out-of-scale extrapolation:** operation laws are fitted only from instrumented tiny worlds `n=2..5`. A second Git freeze locks coefficients and explicit `n=17,31` predictions. Only then are those larger worlds executed. Both holdouts match every frozen numeric coordinate and crossover with zero tolerance.

This is not real-world workload evidence and not a universal scaling law.

---

# 1. Statistical phase-boundary uncertainty

## 1.1 Registered stochastic ecology

For a four-pair exact bidirectional lookup world, let `X=1` denote a reverse query. The registered synthetic generator is:

```text
X_i iid Bernoulli(p)
p = 7/8.
```

Serving costs are:

```text
                 forward   reverse
key_index           1         4
value_index         4         1
```

Changing the inherited key orientation to value orientation costs `K=8` future operations.

Expected serving advantage of value is:

```text
Delta(p)
= E[C_key-C_value]
= 3(2p-1).
```

For `p>1/2`, continuous expected-cost equality occurs at:

```text
q*(p) = 8 / Delta(p).
```

At the preregistered true `p=7/8`:

```text
Delta = 9/4
q* = 32/9 = 3.5555...
```

so the first integer query horizon at which migration is strictly cheaper is Q=4.

## 1.2 Post-freeze sample custody

Only after the stage-1 freeze, 16,384 OS-backed random bytes were acquired and mapped by the frozen rule `X_i=1 iff byte_i<224`.

The committed packed sample has:

```text
N                    = 16384
reverse observations = 14369
p_hat                 = 14369/16384
                      = 0.877014160156...
packed SHA-256        = 736e589ddcd23903820bbb12b30ccc5b5deb7f6ff377ca0b604db1f4b5c22540
```

The witness does not regenerate the sample. It unpacks the committed observations, verifies length/count/hash, and analyzes those raw observations.

The generator is synthetic. Frequentist coverage below is conditional on the registered iid Bernoulli model; no real-workload iid claim is made.

## 1.3 Nonasymptotic confidence set

The frozen full-sample half-width is:

```text
epsilon = 1/64.
```

Hoeffding's bounded-iid inequality gives:

```text
P(|p_hat-p| >= 1/64)
<= 2 exp(-2 * 16384 * (1/64)^2)
= 2 exp(-8)
= 0.000670925255805...
```

Hence registered coverage is at least:

```text
1 - 2 exp(-8)
= 0.999329074744195...
> 99.9%.
```

The observed p interval is exactly:

```text
I_p = [14113/16384, 14625/16384]
    = [0.86138916015625, 0.89263916015625].
```

It contains the preregistered true `7/8`.

This is deliberately not a Wald/normal interval and does not depend on an estimated variance.

## 1.4 Boundary interval propagation

Because the observed lower p bound exceeds 1/2, `Delta(p)=6p-3` is positive over the whole set and `q*(p)=8/Delta(p)` is monotone decreasing.

The exact induced interval is:

```text
Delta in [17763/8192, 19299/8192]

q* in [65536/19299, 65536/17763]
   = [3.395823617804..., 3.689466869335...].
```

The true `32/9` boundary is inside that interval. More importantly, the entire reported confidence set lies strictly inside `(3,4)`.

Therefore every ecology parameter admitted by the confidence set yields the same first strict integer migration horizon:

```text
Q = 4.
```

The uncertainty is not hidden: the continuous boundary is reported as an interval. The integer decision is stable only because that entire interval lies between two adjacent integer horizons.

## 1.5 Required low-information negative control

The stage-1 freeze required analysis of only the first 64 observations with:

```text
epsilon_small = 1/4.
```

This has the same Hoeffding exponent because:

```text
2 * 64 * (1/4)^2 = 8.
```

The first 64 observations contain 58 reverse queries, producing:

```text
p_hat_small = 29/32.
```

Its propagated boundary interval is:

```text
q* in [8/3, 128/15]
   = [2.666666..., 8.533333...].
```

Possible first strict integer migration horizons are:

```text
{3,4,5,6,7,8,9}.
```

So the low-information control cannot localize Q=4 even at the same conservative Hoeffding failure bound. This is the required falsifier against a boundary routine that merely emits the preregistered answer regardless of evidence quantity.

---

# 2. Prospective extrapolation beyond fitted tiny worlds

## 2.1 Scientific order

The extrapolation lane has two separate freezes.

Before any training result, stage 1 fixed:

```text
training sizes = {2,3,4,5}
affine fitting rule = fit on n=2,3; validate exactly on n=4,5
held-out sizes = {17,31}
```

Only the tiny training program was then executed. It is explicitly guarded against running held-out sizes, including under optimized Python.

Its numeric receipt hash is:

```text
a559ca1ffcb6fded7bc9731ca273b7d04117bb462b7e57016e2e9d6dc477d016
```

After fitting, stage 2 committed all coefficients and every held-out numeric prediction before any n=17 or n=31 execution.

That ordering is the core evidence for extrapolation rather than retrospective curve fitting.

## 2.2 Tiny measurements and fitted laws

Instrumented training measurements were:

| n | persistent | migration | key 3F/4R | value 3F/4R |
|---:|---:|---:|---:|---:|
| 2 | 2 | 4 | 11 | 10 |
| 3 | 3 | 6 | 15 | 13 |
| 4 | 4 | 8 | 19 | 16 |
| 5 | 5 | 10 | 23 | 19 |

Using only n=2 and n=3, the frozen affine procedure recovered:

```text
persistent(n) = n
migration(n)  = 2n
key_block(n)  = 4n + 3
value_block(n)= 3n + 4.
```

All four laws have zero residual at validation sizes n=4 and n=5. No higher-order fit was attempted or permitted.

These are classical indexing/amortization operation laws. GMI does not own them.

## 2.3 Frozen n=17 prediction and observation

Stage 2 predicted:

```text
persistent = 17
migration  = 34
key block  = 71
value block= 55.
```

For inherited key orientation:

```text
stay key      = 71m
migrate value = 34 + 55m
m* = 17/8 = 2.125.
```

Thus:

```text
m=2: stay key 142 < migrate value 144
m=3: migrate value 199 < stay key 213
first strict migration horizon = 3.
```

Post-freeze execution observed exactly the frozen tuple `(17,34,71,55)` and exact crossover `17/8`, with zero tolerance.

Both generic orientations answered all 34 distinct forward/reverse obligations exactly, and actual reindexing produced the exact inverse relation.

## 2.4 Frozen n=31 prediction and observation

Stage 2 predicted:

```text
persistent = 31
migration  = 62
key block  = 127
value block= 97.
```

For inherited key orientation:

```text
stay key      = 127m
migrate value = 62 + 97m
m* = 31/15 = 2.06666...
```

Thus:

```text
m=2: stay key 254 < migrate value 256
m=3: migrate value 353 < stay key 381
first strict migration horizon = 3.
```

Post-freeze execution observed exactly `(31,62,127,97)` and `31/15`, again with zero tolerance.

Both orientations answered all 62 distinct obligations exactly and the executed reindex was exact.

The holdouts are respectively 3.4x and 6.2x the largest fitted size.

## 2.5 Remint and hostile comparator

Each held-out world is independently renamed into disjoint opaque key/value token namespaces. The remints preserve:

- all exact answers;
- all four measured coordinates;
- the predicted m=3 crossover.

The comparator is also tested against intentionally altered frozen predictions. Changing a held-out migration or block-count prediction causes comparison failure rather than silent refitting.

---

# 3. Parent subtraction

The statistical result is parent-owned by classical concentration theory. Hoeffding (1963) provides the nonasymptotic bound used here; the transformation from a confidence set on p to a confidence set on a monotone function `q*(p)` is ordinary interval propagation.

The morphology/resource result is parent-owned by classical access-path, preprocessing/query, indexing and amortization theory:

- W. Hoeffding, *Probability Inequalities for Sums of Bounded Random Variables*, JASA 58(301), 1963, DOI `10.2307/2282952` / `10.1080/01621459.1963.10500830`.
- P. G. Selinger, M. M. Astrahan, D. D. Chamberlin, R. A. Lorie, T. G. Price, *Access Path Selection in a Relational Database Management System*, SIGMOD 1979, DOI `10.1145/582095.582099`.
- R. M. Karp, R. Motwani, P. Raghavan, *Deferred Data Structuring*, SIAM Journal on Computing 17(5), 1988, DOI `10.1137/0217055`.

The narrow GMI residual is procedural: estimated ecology coordinates must carry explicit uncertainty into phase claims, and a fitted morphology law does not earn extrapolation language until larger disjoint worlds were frozen and survived prospectively.

---

# 4. Box disposition

At the registered synthetic finite scope, this evidence supports exactly:

```text
[x] Quantify uncertainty in phase-boundary location.
[x] Test phase-law extrapolation beyond fitted tiny worlds.
```

The first box is earned by an explicit nonasymptotic confidence interval and a low-information negative control, not by displaying a noisy point estimate.

The second is earned by the two-stage freeze and zero-tolerance n=17/n=31 holdouts, not by deriving a formula after looking at those worlds.

Still not earned:

- real-world statistical coverage or measured hardware-runtime uncertainty;
- a complete/unbounded ecology coordinate schema;
- a complete/unbounded resource coordinate schema;
- arbitrary-n or arbitrary-obligation extrapolation;
- real-scale transfer;
- universal morphology selection.

## Claim ceiling

```text
FINITE_PROSPECTIVE_PHASE_BOUNDARY_CONFIDENCE_INTERVAL
FINITE_PROSPECTIVE_OUT_OF_SCALE_PHASE_LAW_EXTRAPOLATION
PARENT_OWNED_CONCENTRATION_INDEXING_AMORTIZATION
NO_REAL_WORLD_COVERAGE_UNIVERSAL_SCALING_OR_REAL_SCALE_CLAIM
```
