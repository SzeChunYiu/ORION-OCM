# GMI Routing Core + Residual Theorems v1

Status: **FORMAL ZERO-PRIOR ROUTING HARDENING / EXACT SET-THEORETIC PHASE LAW**

Status date: 2026-09-12.

Purpose:

> Replace a binary fixed-versus-dynamic routing comparison with the exact decomposition of stable dependency core and input-specific residual dependencies.

---

# 1. Required dependency family

For every legal input `x in X`, let exact required dependency edges be

\[
E_x.
\]

Define the **stable core**

\[
I=\bigcap_xE_x
\]

and residual demand

\[
F_x=E_x\setminus I.
\]

Let residual union be

\[
U_F=\bigcup_xF_x.
\]

Then

\[
E_x=I\cup F_x
\]

with disjoint union for every `x`.

---

# 2. Exact routing-opportunity decomposition

## Theorem RR-1

The original union-minus-average routing opportunity satisfies

\[
\left|\bigcup_xE_x\right|-\mathbb E|E_x|
=
|U_F|-\mathbb E|F_x|.
\]

### Proof

Because `I` belongs to every `E_x` and is disjoint from every residual,

\[
|\cup E_x|=|I|+|U_F|
\]

and

\[
\mathbb E|E_x|=|I|+\mathbb E|F_x|.
\]

Subtract. QED.

### Interpretation

Edges required for every input create **zero dynamic-routing opportunity**. All opportunity resides in the variable residual dependency set.

---

# 3. Fixed-core + dynamic-residual crossover

Let active-edge burden be `c_e` per edge/query. Let residual-router burden be `c_r`, including search/control overhead, and expected registered failure penalty be `Lambda_r`.

A fully static exact union realization costs

\[
C_{static}=c_e(|I|+|U_F|).
\]

A fixed-core + dynamic-residual realization costs

\[
C_{hybrid}=c_e|I|+c_r+c_e\mathbb E|F_x|+\Lambda_r.
\]

## Theorem RR-2 — hybrid routing criterion

The hybrid is cheaper iff

\[
c_r+\Lambda_r
<
c_e\left(|U_F|-\mathbb E|F_x|\right).
\]

This is exactly the original dynamic-routing law applied to the residual dependency family.

---

# 4. Fully dynamic routing is not structurally necessary for stable edges

If a fully dynamic router also selects the stable core each query, and its route-decision burden is independent of the number of routed edges, then edge-activation burden is the same as fixed-core + dynamic-residual:

\[
c_e\mathbb E|E_x|
=c_e|I|+c_e\mathbb E|F_x|.
\]

Thus making the stable core static cannot hurt edge count and may reduce router search/error burden.

If routing cost grows with candidate-edge vocabulary, fixing core edges can strictly reduce routing burden.

### GMI prediction

Do not spend adaptive routing capacity on dependencies that are invariant across the ecology unless there is another reason (fault tolerance, load balancing, substrate placement).

---

# 5. Negative twins / phase endpoints

## Entirely fixed dependency

If

\[
F_x=\varnothing
\]

for all inputs, routing opportunity is zero. Any positive residual router burden makes dynamic routing unnecessary.

## Entirely variable, no stable core

If

\[
I=\varnothing,
\]

the theorem reduces to the original fixed-union versus dynamic-routing comparison.

## Small residual vocabulary

If `|U_F|` is small or almost every residual edge is used on every input, the union-minus-average gap is small and dynamic residual routing may not repay its overhead.

---

# 6. Hierarchical extension

Dependencies may have multiple persistence scales:

```text
edges required in every ecology
edges required within one mode/context
edges varying per example
edges varying per decoding/search step
```

Repeatedly apply intersection/residual decomposition within groups. This yields a routing hierarchy with increasingly adaptive layers only where demand actually varies.

The theoretical target becomes a **multi-timescale dependency decomposition**, not one globally fixed or globally dynamic graph.

---

# 7. Development/update interpretation

If the residual dependency family changes faster than the stable core, update burden also favors separation:

```text
stable core:
    compiled/shared and updated rarely

residual router:
    updated/adapted at the volatile timescale
```

This links routing directly to local morphogenesis/versioned residual theory.

---

# 8. Gap update

`GKF-05 dependency geometry` now has:

```text
static exact union lower bound                       CLOSED
union-minus-average dynamic crossover               CLOSED
stable-core/residual decomposition                   CLOSED
fixed-core + dynamic-residual phase law              CLOSED
unseen dependency identifiability no-go              CLOSED
real pre-outcome dependency estimator                OPEN-BLOCKING
router learnability/error                            OPEN-BLOCKING
```

---

# 9. Claim ceiling

These are exact set/cost laws conditional on known required dependency sets and registered routing costs. Real systems must infer the dependency family and can use approximate edges; that estimation/learning problem remains open.
