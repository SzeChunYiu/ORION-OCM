# Hybrid Complementarity Theorem V1

**Issue:** #602 B20 — derive neuro-symbolic/statistical-symbolic hybrid conditions  
**Evidence class:** P1 finite expectation identity + P2 exact witness  
**Claim ceiling:** `PARENT_OWNED_HYBRID_COMPLEMENTARITY_CONDITION_AT_REGISTERED_FINITE_SCOPE`

## Setup

Let contexts `x` have frozen probabilities `p(x)`. Two parent solvers `A` and `B` have complete verified losses `L_A(x)` and `L_B(x)` on the same obligation/resource scale. Let a hybrid pay fixed/routing/verification overhead `h >= 0` and use a router that misroutes with contextwise probability `e(x)`.

With a perfect router,

`C_oracle = h + E[min(L_A,L_B)]`.

The best monolith costs

`C_mono = min(E[L_A], E[L_B])`.

Define the **complementarity gap**

`G = C_mono - E[min(L_A,L_B)] >= 0`.

Then the hybrid strictly dominates the best monolith iff

`h < G`.

This is an identity, not a new hybrid algorithm.

For a binary router that, on a misroute, chooses the other solver, the exact expected misrouting penalty is

`P_e = E[e(x) * |L_A(x)-L_B(x)|]`.

The routed hybrid strictly dominates iff

`h + P_e < G`.

Verification/fallback costs belong inside `h` (or inside the contextwise losses if they vary by context); they are never free.

## Neuro-symbolic / statistical-symbolic specialization

Instantiate `A` as a neural/statistical parent solver and `B` as a symbolic parent solver. A hybrid is warranted only when the parents have enough **context-dependent complementary advantage** to pay routing, verification, communication, maintenance and misrouting burden. Architecture names alone imply no positive gap.

The same equation covers statistical-symbolic hybrids. Mechanism ownership remains with mixture-of-experts, algorithm selection, decision theory/value-of-information, neuro-symbolic/statistical-relational systems, and verifier/fallback parents.

## Exact positive witness

Two equally likely contexts have losses

`A=(0,4)`, `B=(4,0)`.

Each monolith has expected loss `2`; the perfect pointwise minimum is `0`, so `G=2`. With overhead `h=1`, the hybrid costs `1` and strictly wins.

If misrouting probability is the same `epsilon` in both contexts, `P_e=4 epsilon`; therefore the hybrid wins exactly when

`1 + 4 epsilon < 2`, i.e. `epsilon < 1/4`.

At `epsilon=1/4` it ties; above it loses.

## Negative twin

For `A=(0,0)`, `B=(1,1)`, `A` pointwise dominates. The pointwise minimum equals `A`, so `G=0`; any positive hybrid overhead makes the hybrid strictly worse. Heterogeneity by itself therefore earns nothing.

## Scope / falsifiers

This closes only the formal B20 condition row. It does **not** establish a distinct intelligence domain, a universal benefit of neuro-symbolic systems, real-scale routing efficiency, or neutral emergence.

Falsifiers at this registered scope:

- computed `G` disagrees with direct finite expectation;
- a positive-overhead hybrid beats a pointwise-dominating parent when `G=0`;
- the misrouting threshold differs from `h + P_e < G` under the declared router;
- any cost is omitted from the common loss scale.
