# Warrant Lift: Information Missing from a Behaviorally Correct Model

**Theory candidate V1 — exact characterization and finite algebra checks; priority unresolved**

Date: 2026-09-03  
Scientific umbrella: ORION-V2 #194  
Execution master: ORION-V2 #197  
Focused lane: ORION-V2 #221

## 1. Definition

Let `Omega` be a finite set of latent learned worlds. Let `B: Omega -> Bset` be current behavior and `L: Omega -> Lset` be the complete registered lifecycle response profile: current outputs, held-out compositional responses and required responses after permitted evidence, scope, authority, policy or verifier updates. Assume `L` refines `B` because current behavior is part of the lifecycle profile.

For current behavior value `b`, let

```text
m_b = number of distinct lifecycle profiles among worlds with B(world)=b.
```

Define real worst-case Warrant Lift

```text
lambda_infinity(L|B) = log2 max_b m_b
```

and exact fixed-width bits

```text
Lambda_infinity(L|B) = ceil(lambda_infinity(L|B)).
```

It measures the information missing from a behaviorally correct model that is required for exact future-safe action.

## 2. Characterization theorems

### WL-1 — zero criterion

`lambda_infinity(L|B)=0` exactly when current behavior is already sufficient for every registered lifecycle response; equivalently, `B` and `L` induce the same partition of latent worlds.

### WL-2 — exact side-state characterization

Suppose a decoder knows `B(world)` and receives an additional fixed-width side state `S(world)`. The minimum bits needed so that `L(world)` is a function of `(B(world),S(world))` are exactly

```text
Lambda_infinity(L|B).
```

Lower bound: the largest behavior fiber contains `m_b` lifecycle classes requiring distinct messages. Upper bound: index lifecycle classes within each behavior fiber, reusing codewords across different fibers.

### WL-2A — acquisition/query/abstention frontier

If at most `C` certified acquisition bits can reach at most `B_s` persistent bits, and the system may later ask `Q` binary revalidation questions and abstain on at most `a` independent lifecycle coordinates, then

```text
min(C,B_s) + Q + a >= Lambda_infinity(L|B).
```

## 3. Distributional form

For a fixed distribution `mu` over latent worlds, define distributional Warrant Lift as conditional entropy

```text
lambda_mu(L|B) = H_mu(L|B).
```

This measures expected missing information. It cannot replace the worst-case measure when false authority is a non-compensatory failure.

## 4. Algebraic laws

### WL-3 — obligation monotonicity

If lifecycle obligation set `L2` refines `L1`, then

```text
lambda_infinity(L2|B) >= lambda_infinity(L1|B).
```

Adding held-out tasks or evidence/scope/verifier updates cannot reduce exact lifecycle state requirements.

### WL-4 — independent product additivity

For Cartesian product systems,

```text
lambda_infinity(L1 x L2 | B1 x B2)
= lambda_infinity(L1|B1) + lambda_infinity(L2|B2).
```

Under product distributions, conditional-entropy Warrant Lift is also additive.

### WL-5 — shared-warrant subadditivity

For a joint system whose lifecycle response is `(L1,L2)`, joint Warrant Lift is at most the sum of the individual lifts, with strict inequality when the two systems share the same latent warrant. Common support can reduce total state only when dependence is represented rather than double-counted as independent corroboration.

### WL-6 — current-accuracy blind spot

For every integer `k>=0`, there is a family with one current behavior class but `Lambda_infinity=k`: take `2^k` worlds with one present output and distinct lifecycle profiles. Perfect current accuracy therefore places no finite universal upper bound on future-safe state.

For the independent-support WLL family with `p` skills and `h` contexts, `Lambda_infinity=p*h`. Adding `p-r` procedural degrees of freedom left by rank-`r` endpoint observations gives `(p-r)+p*h`.

## 5. Exact validation

The checker enumerates all set partitions on universes of size one through five and every nested behavior/lifecycle partition pair. It validates the zero criterion, exact side-code construction, a planted code collision for every positive-lift pair, conditional entropy bounds, obligation monotonicity, independent-product additivity, strict shared-warrant subadditivity, and arbitrary current-accuracy blind spots from zero through eight bits. A no-alarm case where behavior already equals lifecycle is included.

## 6. Parent subtraction

The mathematics uses partition refinement, sufficient statistics, conditional entropy, state minimization, communication/information complexity, exact learning and future-equivalence ideas. Those ingredients are not claimed as new.

The potentially novel contribution is Warrant Lift as a non-compensatory lifecycle complexity coordinate for learned procedures with explicit evidence, support, scope, authority, verifier and revocation semantics, together with the strict observation-interface hierarchy and a natural-class acquisition-compilation-repair frontier.

Priority remains blocked pending theorem-level subtraction against Myhill-Nerode/bisimulation quotients, sufficient statistics and Blackwell comparisons, conditional entropy and communication complexity, certified/ticketed unlearning, provenance/TMS, knowledge compilation and dynamic algorithms.

## 7. Decisive next theorem

For a natural compositional program class with implicit support relations, prove or refute a tight bound coupling certified acquisition, compiled warrant state, future revalidation, procedural recourse, abstention, false retention and useful retention. Add a non-cardinality lower bound and an output-sensitive repair upper bound. The strongest parent and an equally provisioned recurrent Transformer receive identical interfaces and resources.

## 8. Authority

Supported: exact finite characterization, algebraic laws, exhaustive checks and arbitrary lifecycle uncertainty hidden by current behavior.

Not supported: literature priority, post-Transformer architecture, parameter efficiency, natural-language competence, quantum advantage or publication readiness.
