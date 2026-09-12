# GMI Known-Domain Capability Theorems v1

Status: **FORMAL CALIBRATION / POSITIVE AND NEGATIVE CAPABILITY LAWS**

Status date: 2026-09-12.

Purpose:

> Calibrate GMI against known structural paradigms by proving not only where a carrier works, but where its native law imposes a capability ceiling or resource lower bound.

These are not novelty claims.

---

# 1. Hyperdimensional vector superposition

Let `v_1,...,v_k` be independent random bipolar vectors in `{−1,+1}^d` and form the additive bundle

\[
s=\sum_{i=1}^{k}v_i.
\]

Let `u_1,...,u_M` be independent distractor vectors from the same distribution. Retrieval ranks candidates by inner product with `s`.

## Theorem HD-T1 — simple bundle retrieval bound

For target `v_1`, define target score

\[
T=\langle s,v_1\rangle
\]

and distractor score

\[
D_j=\langle s,u_j\rangle.
\]

For `k>1`,

\[
Pr[T\le d/2]\le \exp\left(-\frac{d}{8(k-1)}\right),
\]

and for each distractor

\[
Pr[D_j\ge d/2]\le \exp\left(-\frac{d}{8k}\right).
\]

Therefore

\[
Pr[\text{retrieval failure}]
\le
\exp\left(-\frac{d}{8(k-1)}\right)
+
M\exp\left(-\frac{d}{8k}\right).
\]

### Proof

Condition on `v_1`. Then

\[
T=d+\sum_{i=2}^k\sum_{\ell=1}^d v_{i\ell}v_{1\ell},
\]

and the noise term is a sum of `(k-1)d` independent Rademacher variables. Hoeffding's inequality gives the first bound for a downward deviation of `d/2`.

Condition on a fixed distractor `u_j`. Then

\[
D_j=\sum_{i=1}^k\sum_{\ell=1}^d v_{i\ell}u_{j\ell}
\]

is a sum of `kd` independent Rademacher variables, so Hoeffding gives the second bound. Apply the union bound across `M` distractors. QED.

## Corollary HD-C1 — sufficient dimension

A sufficient condition for failure probability at most `delta` is

\[
d\ge
\max\left\{
8(k-1)\ln\frac{2}{\delta},
8k\ln\frac{2M}{\delta}
\right\}.
\]

Thus simple superposition capacity scales at most on the order

\[
k=O\left(\frac{d}{\log(M/\delta)}\right)
\]

under this retrieval contract.

## Capability interpretation

This gives GMI an explicit native response law:

```text
more superposed items -> lower retrieval margin
larger dimension -> exponentially lower collision probability
larger candidate dictionary -> logarithmically greater dimension requirement
```

## Weak-domain implication

Scaling dimension is not free. If memory/energy/communication price grows with `d`, the domain can become uneconomic before semantic error becomes small. The theorem predicts a measurable capability-resource frontier rather than unlimited scaling.

## Parent-reduction warning

The theorem establishes a useful algebraic capacity law, not new-domain status. HDC/VSA has extensive prior theory and classical implementations.

---

# 2. Local-field / cellular computation

Let computation occur on graph `G=(V,E)`. At each synchronous step, node `v` may update only from states inside graph-distance `r`.

## Theorem LF-T1 — causal light cone

After `t` update rounds, the state of node `v` can depend only on initial states within graph-distance at most

\[
r t
\]

of `v`.

### Proof

Induct on `t`. At `t=0`, dependence radius is zero. If every node at time `t` depends only on its radius-`rt` initial neighborhood, then the radius-`r` inputs used to update `v` at `t+1` collectively depend only on initial nodes at distance at most `r+rt=r(t+1)`. QED.

## Corollary LF-C1 — global-information latency lower bound

If a protected output at node `v` must distinguish two initial worlds that differ only at node `u` with distance `L=d_G(u,v)`, exact solution requires

\[
t\ge \left\lceil\frac{L}{r}\right\rceil.
\]

## Capability interpretation

Local-field systems can be extremely efficient for local repair, local sensing and spatially matched obligations, but they have a hard communication-speed ceiling for global coordination unless they add long-range edges, hierarchy, broadcast or another domain mechanism.

This theorem is implementation-invariant for the registered locality contract.

---

# 3. Population-hereditary computation

Let the population at generation `t` have support `S_t` over heritable types.

## Theorem PH-T1 — selection cannot create absent variants

Under pure selection/resampling with no mutation, recombination creating new types, immigration or construction,

\[
S_{t+1}\subseteq S_t
\]

for every generation. Hence

\[
S_t\subseteq S_0
\]

for all `t`.

### Proof

Every offspring is copied from a type already present in the parent population. Induct. QED.

## Corollary PH-C1 — hard capability ceiling

If every solution to a future obligation requires a heritable type outside `S_0`, pure selection has success probability zero regardless of population size or number of generations.

This is a strong negative scaling result:

> scaling selection alone does not create novelty.

## Theorem PH-T2 — mutation-limited discovery

Assume `N` independent births per generation and that each birth produces the required previously absent type with probability `mu`. Then the probability it has appeared by generation `T` is

\[
1-(1-\mu)^{NT}.
\]

To achieve success probability at least `1-delta`, it is necessary and sufficient under this simple independent model that

\[
T\ge
\frac{\ln\delta}{N\ln(1-\mu)}.
\]

For small `mu`, this is approximately

\[
T\gtrsim \frac{\ln(1/\delta)}{N\mu}.
\]

## Capability interpretation

Population size, mutation supply and selection quality are distinct causal coordinates. More selection pressure cannot substitute for zero novelty supply.

---

# 4. Energy-landscape local relaxation

Let state space be `{0,1}^n`, `n>=2`, with native move set consisting of Hamming-distance-one moves and a rule that accepts only strictly energy-decreasing moves.

## Theorem EL-T1 — strict local-minimum trap

There exists an energy function with a strict non-global local minimum from which the native dynamics can never reach the global optimum.

### Construction

Define

\[
E(1^n)=0,
\qquad
E(0^n)=1,
\]

and

\[
E(x)=2
\]

for every other state `x`.

Since `n>=2`, every Hamming-distance-one neighbor of `0^n` has energy `2`, so `0^n` is a strict local minimum. But `1^n` has lower energy `0`. Strictly downhill local dynamics initialized at `0^n` has no legal move and therefore never reaches the global optimum. QED.

## Capability interpretation

No amount of additional runtime helps this native dynamics from the trapped state. General search capability requires at least one additional mechanism:

```text
uphill/noisy moves
tunneling/nonlocal moves
restarts
memory/tabu state
morphology/topology change
external proposal mechanism
```

The cost and reliability of the added mechanism must be charged. A claim that “relaxation scales to intelligence” is therefore false for strict local descent without an escape operator.

---

# 5. Memory-indexed exact lookup calibration

Consider `N` independent keys, each storing one value from alphabet of size `q`. The registered obligation is exact answer for every key and arbitrary independent single-key revisions.

## Theorem MEM-T1 — exact state information lower bound

There are

\[
q^N
\]

possible current maps. Any exact semantic state sufficient for all key queries therefore requires at least

\[
N\log_2 q
\]

bits in the worst case.

An explicit table attains this information lower bound up to address/representation overhead.

## Capability interpretation

For arbitrary volatile facts with no exploitable compression, no learning architecture can beat the information requirement by semantic cleverness alone. Parametric models can only compress if the mapping has structure or if error is tolerated.

This gives a clean niche prediction for memory-indexed systems.

---

# 6. Search/frontier calibration

Consider a complete `b`-ary tree of depth `d` with one goal leaf and no observation/heuristic information distinguishing unexplored subtrees.

## Theorem SEARCH-T1 — adversarial exhaustive-search lower bound

Any deterministic algorithm that must guarantee finding the goal can be forced to inspect all

\[
b^d
\]

leaves in the worst case.

### Proof

An adversary places the goal at the last leaf inspected by the deterministic algorithm. Before inspecting a leaf, all uninspected leaves remain observationally equivalent under the registered information contract. QED.

## Capability interpretation

Search is powerful when branching/depth are controlled or informative heuristics/verifiers collapse the frontier. Scaling compute alone cannot remove exponential worst-case growth under an uninformative frontier.

---

# 7. Cross-domain calibration requirements

For each theorem above, experiments must include a matched negative twin where the limiting coordinate is removed:

```text
HD: reduce superposition count or candidate dictionary
LF: add long-range communication / make target local
PH: supply target variation directly
EL: add an escape operator or remove local traps
MEM: introduce compressible structure across key values
SEARCH: provide a discriminative heuristic/verifier
```

GMI succeeds only if it predicts both the original limitation and the disappearance of that limitation in the twin.

---

# 8. Current theory consequence

A structural paradigm may be scientifically real even if it is weak.

Use the capability-envelope taxonomy:

```text
hard semantic ceiling
poor scaling elasticity
combinatorial resource explosion
communication-limited
novelty-supply-limited
local-minimum-limited
narrow ecological niche
```

The theory should attempt to predict which failure mode applies before large-scale search or training.
