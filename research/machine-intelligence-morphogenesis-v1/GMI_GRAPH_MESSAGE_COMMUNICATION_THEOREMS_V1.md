# GMI Graph Message Communication Theorems v1

Status: **FORMAL ZERO-PRIOR GRAPH/ROUTING HARDENING**

Status date: 2026-09-12.

Purpose:

> Derive exact information limits for local graph message passing and use them to predict pressure toward greater depth, wider messages, long-range edges, hierarchical compression or global/content-dependent routing.

---

# 1. Cut communication model

Let graph `G=(V,E)` be partitioned into regions `A` and `B`. Let the edge cut between them contain

\[
c=|\partial(A,B)|
\]

edges.

Initially, region `A` contains a semantic variable

\[
Z\in\{0,1\}^k
\]

with `2^k` possible values, while region `B` has no side information about `Z`.

A synchronous local message-passing realization runs for `R` rounds. Across each cut edge, at most `b` bits may be transmitted from `A` toward `B` per round.

At the end, a node/system in `B` must recover `Z` exactly.

---

# 2. Exact cut-capacity lower bound

## Theorem GM-1 — information crossing bound

Any deterministic exact realization requires

\[
Rcb\ge k.
\]

### Proof

Over `R` rounds and `c` cut edges, at most `Rcb` transmitted bits can cross from `A` to `B`. Therefore the number of possible distinct cross-cut transcripts is at most

\[
2^{Rcb}.
\]

If `Rcb<k`, there are fewer transcripts than the `2^k` possible values of `Z`, so by pigeonhole at least two distinct values induce the same transcript. Since `B` had no side information distinguishing them, exact recovery is impossible. QED.

## Corollary GM-1.1 — depth lower bound

If message width `b` and cut size `c` are fixed,

\[
R\ge\left\lceil\frac{k}{cb}\right\rceil.
\]

## Corollary GM-1.2 — width lower bound

If depth `R` and cut size are fixed,

\[
b\ge\left\lceil\frac{k}{Rc}\right\rceil
\]

in integer-bit communication models.

---

# 3. Locality/light-cone lower bound

If messages travel at most one graph edge per layer/round, information initially at graph distance greater than `R` from an output node cannot affect that output after `R` rounds.

## Theorem GM-2 — finite-hop indistinguishability

Two graph-labeled worlds that are identical on the radius-`R` neighborhood of an output node but differ only outside that neighborhood produce identical state at that node under any deterministic `R`-round strictly local message-passing algorithm with shared local rules.

### Proof

Induct on rounds. At round 0 the node sees only itself. After one round state depends only on radius 1; after `R` rounds only radius `R`. QED.

---

# 4. Why adding long-range edges can change the phase

Suppose a new routing mechanism adds edges that increase cut size from `c` to `c'` or reduce graph distance from `D` to `D'`.

The lower bounds become

\[
R c' b\ge k
\]

and

\[
R\ge D'
\]

for the corresponding information path.

Thus long-range/dynamic routing can be favored for two distinct reasons:

```text
path-length relief      reduce the number of sequential local steps
cut-capacity relief     increase semantic bandwidth across bottlenecks
```

These should be measured separately.

---

# 5. Compression can beat raw communication only when semantics permit it

The `k`-bit lower bound assumes `B` must recover all `k` independent bits. If the protected target depends only on a quotient

\[
q(Z)
\]

with `M` possible values, the necessary information can drop to

\[
\lceil\log_2M\rceil
\]

bits.

### GMI consequence

A strong graph system has two ways to avoid a communication bottleneck:

1. increase routing/communication capacity;
2. compute a sufficient semantic compression before the cut.

This links graph-message theory directly to the GMI semantic quotient framework.

---

# 6. Negative twin

If the target at `B` depends only on one local bit already present in `B`, then `k=0` cross-cut information is required. Increasing global connectivity adds burden without semantic benefit.

Therefore global attention/long-range routing should not be predicted merely because a graph is large.

---

# 7. Zero-prior architecture-property derivation

From obligation geometry alone, GMI should predict:

```text
small local semantic dependency + adequate cut capacity
    -> local shared message passing

large graph distance but low-dimensional sufficient summary
    -> hierarchical/compressed propagation may suffice

large independent information demand across narrow cuts
    -> local message passing requires large depth/width or new long-range routing

input-dependent bottleneck locations
    -> dynamic/content-dependent routing becomes more attractive
```

This derives GNN/local routing/global routing phases without architecture names.

---

# 8. Gap update

Known-form graph/message derivation now has:

```text
T-hop receptive-field theorem                  CLOSED
cut information-capacity lower bound           CLOSED
semantic compression escape via quotient       CLOSED
long-range routing relief variables             CLOSED
real task k/c/b estimation                      OPEN-BLOCKING
nonlinear aggregation/optimization effects      OPEN-BLOCKING
protected GNN-vs-attention crossover            OPEN-BLOCKING
```

---

# 9. Claim ceiling

These are deterministic exact communication lower bounds. Stochastic coding, shared side information, lossy tolerance and interactive compression can change constants/quantities and must be registered separately. They do not by themselves establish any one neural graph architecture as optimal.
