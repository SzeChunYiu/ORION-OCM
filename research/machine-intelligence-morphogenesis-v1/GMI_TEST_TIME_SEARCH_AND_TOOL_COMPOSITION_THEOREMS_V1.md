# GMI Test-Time Search and Tool Composition Theorems v1

Status: **FORMAL ZERO-PRIOR STRUCTURAL DERIVATION / EXACT BASE CASES**

Status date: 2026-09-12.

Purpose:

> Derive when inference-time branching and multi-tool composition are rational from obligation/risk/resource geometry, without assuming historical agent architectures.

---

# 1. Verified independent proposal search

Suppose each independent proposal attempt costs `c>0` and has probability `p in [0,1]` of producing an admissible solution. Assume a sound verifier identifies admissible solutions exactly. Failure after all attempts incurs registered loss/risk `L>0`.

With `k` attempts, failure probability is

\[
(1-p)^k,
\]

so expected scalarized burden is

\[
C(k)=kc+L(1-p)^k.
\]

## Theorem TS-1 — exact marginal branch value

Adding attempt `k+1` reduces expected failure loss by

\[
L p(1-p)^k.
\]

Therefore attempt `k+1` is beneficial iff

\[
Lp(1-p)^k>c.
\]

The optimal finite branch count is the largest `k` before marginal expected failure reduction falls below branch cost (with ties handled by the registered convention).

### Consequences

```text
higher verifier-backed proposal success p -> fewer/more valuable early branches
higher failure loss L -> deeper/wider search justified
higher branch cost c -> shallower search
as k grows -> diminishing marginal value under independence
```

### Negative twins

```text
p=0:
    search never helps.

L=0:
    no risk value from extra search.

unsound verifier:
    the simple law fails because accepted bad proposals add false-adoption loss.
```

---

# 2. Correlated proposal correction

Independence is not guaranteed. Let `F_k` be the probability all first `k` attempts fail.

## Theorem TS-2 — general marginal search criterion

Without assuming independence,

\[
C(k)=kc+LF_k.
\]

Attempt `k+1` is beneficial iff

\[
L(F_k-F_{k+1})>c.
\]

Thus the relevant observable is **conditional failure-mass reduction**, not raw branch count.

Highly correlated proposals can make additional branches nearly worthless even when single-branch success looks good.

---

# 3. Train/compile versus test-time search

Let one reusable compiled realization cost `C_compile`, serve each query at `c_comp`, while online search costs expected `c_search` per query at matched protected quality.

## Theorem TS-3 — exact reuse crossover

Over reuse horizon `R`, compilation is cheaper iff

\[
C_{compile}+Rc_{comp}<Rc_{search}.
\]

If `c_search>c_comp`, the crossover is

\[
R>\frac{C_{compile}}{c_{search}-c_{comp}}.
\]

This is the generic phase law behind moving computation from inference time into parameters/cache/program state as reuse grows.

---

# 4. Typed tool composition graph

Let each semantic type be a node in directed graph `G=(V,E)`. A tool invocation is a typed edge

\[
e:u\to v
\]

with burden `c(e)>=0`. The obligation requires transforming available type `s` into target type `t` while respecting the registered semantic contracts.

## Theorem TC-1 — minimum valid tool-composition burden is a shortest path

If tool effects compose exactly according to graph edges and edge costs add, then the minimum burden of any legal tool chain from `s` to `t` is the shortest-path distance

\[
d_G(s,t).
\]

If no path exists, the obligation is unreachable using the current tool ecology.

### Proof

Every legal chain is a path and has additive path cost. The least-cost legal chain is therefore the shortest path by definition. QED.

## Corollary TC-1.1 — when single-step routing is insufficient

If there is no direct edge `s->t` but a path of length greater than one exists, no one-tool router can satisfy the obligation; composition is structurally necessary.

### Negative twin

If a direct tool edge `s->t` exists with cost no greater than every multi-step path and equivalent evidence/risk semantics, composition adds no benefit.

---

# 5. Authority/evidence constraints

Extend each tool edge with an evidence/authority label `a(e)`. Let the target constitution accept only paths whose composed evidence contract belongs to legal set `A_legal`.

## Theorem TC-2 — cheapest semantic path can be inadmissible

The resource-shortest path in the unconstrained graph need not be the cheapest admissible path under evidence/authority constraints.

Therefore tool selection must optimize over

\[
\mathcal P_{legal}(s,t)
\]

rather than over raw resource cost alone.

This recovers the GMI distinction between capability and authority: a tool can compute the right answer yet be illegal as an authoritative state transition.

---

# 6. Search versus tool call

Suppose an obligation can be solved either by internal verified search with expected cost `C_search` or by an admissible tool path `P` with total burden `C_tool(P)` and matched semantic/risk outcome.

## Theorem TC-3 — exact tool/search crossover

Choose the tool realization iff

\[
\min_{P\in\mathcal P_{legal}}C_{tool}(P)<C_{search}.
\]

If external calls introduce failure probability or latency tail, these enter the burden vector/registered scalarization rather than being ignored.

---

# 7. Zero-prior derivation consequences

The theory now predicts agent-like mechanisms from plain obligation geometry:

```text
high failure loss + useful verifier + proposal diversity
    -> inference-time branching/search

high reuse
    -> compile/cache repeated search result

typed obligation not solvable by one primitive
    -> multi-step tool composition

authority constraints
    -> evidence-aware path selection rather than cheapest raw tool
```

No historical agent architecture name is needed.

---

# 8. Gap update

`GKF-13 test-time reasoning/search`:

```text
independent and general marginal branch-value laws CLOSED
compile-vs-search reuse law CLOSED
remaining: pre-outcome estimate of proposal correlation/success/verifier error in real tasks
```

`GKF-14 heterogeneous tool composition`:

```text
typed exact composition and necessity law CLOSED
remaining: automatic semantic type/contract discovery, uncertain tool effects, multi-step error propagation
```

---

# 9. Claim ceiling

These are exact base-case laws. Real agentic systems violate independence, known-cost, exact-contract and stationary-tool assumptions. Those violations are now explicit empirical atoms rather than reasons to treat tool/search architectures as primitive unexplained species.
