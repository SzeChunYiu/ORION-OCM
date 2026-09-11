# GMI VLC prediction update v2 — after the first falsified twin

Status: **PROSPECTIVE CORRECTION, FROZEN BEFORE V2 CONFIRMATORY EXECUTION.**

The V1 exact microscope failed one registered prediction: setting `nu -> 0` did remove the value of versioning, but did **not** make the monolithic `k=N` realization win. The high semantic/materialization burden remained large enough that factorization was still preferred.

This is a theory correction, not a parameter patch.

---

# 1. Atomic gap exposed by V1

V1 implicitly bundled two different decisions:

```text
A. how coarse should the semantic/implementation factorization be?
B. should updates use shadow-version verify-before-swap?
```

They are not controlled by the same coordinates.

Low invalidation `nu` directly weakens the benefit of versioned updates, but does not erase high semantic complexity `sigma` or a realization whose materialization/build cost grows sharply with factor size.

Therefore:

```text
nu -> 0  DOES NOT IMPLY  monolithic morphology.
```

The corrected theory must combine obligation demand `Xi` with realization response `R_M`, exactly as required by `GMI_MORPHOLOGY_SELECTION_NO_GO_V1.md`.

---

# 2. Revised decomposition

## 2.1 Factorization phase

Module/factor granularity is controlled primarily by the competition among:

```text
semantic/materialization curvature     (sigma + realization response)
query/composition coordination cost    (pi + dependency/query structure)
update dependency cone                 delta
update rate                            nu
reuse horizon                          eta
```

High `sigma` with rapidly growing materialization cost can keep a system factorized even when `nu=0`.

## 2.2 Versioning phase

For a fixed factorization, versioned verify-before-swap is controlled primarily by:

```text
update count/rate
retention/availability price lambda
local rebuild size
extra shadow-copy memory price pi_memory
```

For the frozen E0 cost model, versioning changes only memory and retention-exposure terms. Let

```text
m        module count
w        local materialization size
q_u      expected modules touched per update
U        update count
L        retention price
p_mem    memory price
```

Then versioning wins iff

\[
p_{mem}mw
<
(1-e)ULq_uw,
\]

where `e` is the versioned exposure fraction.

Canceling `w` yields the exact V2 threshold:

\[
\boxed{
UL > \frac{p_{mem}m}{(1-e)q_u}
}
\]

for a fixed `k`.

This is a stronger, testable prediction than “stationarity implies monolith.”

---

# 3. V2 confirmatory world

A new exact world is used; no V1 row counts.

```text
N = 18
query_arity = 5
module_sizes = {1,2,3,6,9,18}
coordination_cost = 0.30
verify_multiplier = 0.40
memory_price = 6
versioned_exposure = 0.02
```

High-sigma materialization remains `2^k`.

## R2 target

```text
H=200000, U=900, cone=1, retention=3.0
```

Prediction:

```text
winner is versioned
1 < k < 18
```

## S2 stationary-high-sigma twin

```text
H=200000, U=0, cone=1, retention=3.0
```

Prediction:

```text
winner is unversioned
k < 18
```

This explicitly predicts **persistent factorization without versioning**.

## W2 weak-retention twin

```text
H=200000, U=900, cone=1, retention=0
```

Prediction:

```text
winner is unversioned
```

## H2 short-reuse twin

```text
H=10000, U=900, cone=1, retention=3.0
```

Prediction:

```text
winner.module_size <= R2.winner.module_size
```

## C2 high-coordination twin

Keep R2 except increase coordination cost from `0.30` to `1.50`.

Prediction:

```text
winner.module_size >= R2.winner.module_size
```

This isolates the pressure to coarsen factorization when cross-factor serving/composition is expensive.

---

# 4. Exact threshold test

For every `k` in the candidate set and for update counts

```text
U in {0,1,2,5,10,20,50,100,200,400,900}
```

with `retention=3.0`, the script computes the analytic versioning inequality before comparing the two enumerated lifecycle costs.

Acceptance requires exact agreement for every `(k,U)` pair.

This tests a numeric theory prediction, not only a winner label.

---

# 5. V2 acceptance

Strong terminal:

```text
VLC_PHASE_DECOMPOSITION_V2_EXACT_GREEN
```

iff:

1. all five regime predictions pass; and
2. every analytic versioning-threshold prediction agrees with enumeration.

Any failure remains in the receipt. No V2 parameter retuning after outcome access.

---

# 6. Consequence for the larger GMI theory

If V2 is green, the allowed claim is still narrow:

> The exact microscope supports a **two-phase realization law**: factor granularity and safe-update versioning respond to different combinations of GMI demand and realization-response coordinates.

It does not establish VLC as a new intelligence form.

The scientific value is that the first failure improved the theory's causal decomposition instead of being explained away.
