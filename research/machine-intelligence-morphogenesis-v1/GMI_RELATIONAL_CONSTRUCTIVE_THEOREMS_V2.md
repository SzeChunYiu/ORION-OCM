# GMI Relational and Constructive Theorems v2

Status: **EXACT FINITE THEORY HARDENING / NOVELTY CLAIMS NARROWED**

Status date: 2026-09-12.

Purpose:

> Generalize the strongest exact results for relational local-to-global state and constructive closure, and prove the strongest currently available parent reductions.

---

# 1. Relational local-to-global state on arbitrary graphs

Let `G=(V,E)` be a finite undirected graph with `n=|V|`, `m=|E|`, and `c` connected components. Each edge `e={u,v}` carries a Boolean label `b_e` and imposes

\[
x_u\oplus x_v=b_e.
\]

Let

\[
\beta_1(G)=m-n+c
\]

be the cycle-space dimension over `F_2`.

## Theorem RLG-T1 — cycle consistency

A global assignment `x:V->{0,1}` exists iff the XOR of the edge labels around every cycle is zero.

### Proof

Necessity: XOR the constraints along any cycle. Every vertex value appears exactly twice and cancels, so the cycle-label XOR must be zero.

Sufficiency: choose one root per connected component and assign its bit arbitrarily. Extend values along a spanning forest by `x_v=x_u XOR b_{uv}`. Every non-tree edge closes a fundamental cycle. Zero parity on every cycle guarantees the independently propagated endpoint values satisfy each non-tree edge. QED.

## Theorem RLG-T2 — solution count

If the system is consistent, it has exactly

\[
2^c
\]

global assignments.

### Proof

Each connected component has one free root bit. Once chosen, every other vertex value in that component is forced by path propagation. Components are independent. QED.

## Theorem RLG-T3 — obstruction-space dimension

The space of edge-label systems modulo vertex-potential relabellings has dimension

\[
\beta_1(G)=m-n+c.
\]

Equivalently, there are exactly

\[
2^{\beta_1(G)}
\]

distinct cycle-obstruction syndromes.

### Proof

Fix an arbitrary orientation. The coboundary map

\[
\delta:F_2^V\to F_2^E
\]

maps vertex assignments to induced edge parities. Its image has dimension `n-c` because the kernel consists exactly of assignments constant on each connected component and therefore has dimension `c`. By rank-nullity,

\[
\dim(F_2^E / im\,\delta)=m-(n-c)=m-n+c=\beta_1(G).
\]

QED.

## Corollary RLG-C1 — exact developmental lower bound for full obstruction queries

If the future query family can ask for every independent obstruction coordinate, any exact developmental descriptor must distinguish all `2^beta_1` syndromes and hence requires at least

\[
\beta_1(G)
\]

bits in the worst case.

A fundamental-cycle syndrome vector attains this lower bound.

## Negative twin

If the only future obligation is the one-bit question “does a solution exist?”, the `beta_1`-bit syndrome is not necessary after preprocessing; one consistency bit suffices. Therefore the lower bound is query-family dependent and must never be presented as an unconditional state requirement.

---

# 2. Symbolic reduction for the graph-XOR family

## Theorem RLG-R1 — linear symbolic realization

There is an ordinary symbolic/program realization that, given `(G,b)`, computes a spanning forest, propagates vertex potentials, extracts all fundamental-cycle obstruction bits, and decides consistency in

\[
O(n+m)
\]

time and `O(n+m)` input/state space, with `O(n)` additional mutable working state under adjacency-list representation.

### Proof

Depth-first or breadth-first search constructs a spanning forest in `O(n+m)`. During traversal, assign each newly reached vertex its forced potential. Every non-tree edge is checked once; its endpoint-potential XOR with `b_e` is exactly the corresponding fundamental-cycle syndrome. QED.

## Consequence

For this family, relational/sheaf language exposes the correct invariant, but the strongest symbolic parent realizes the same asymptotic law. Therefore this family does not support H2/H3 domain separation.

Current verdict:

```text
mechanism theorem:      GREEN
state lower bound:      GREEN for full obstruction-query family
native upper bound:     GREEN
symbolic reduction:     GREEN
new-domain separation:  REDUCED on this family
```

---

# 3. Constructive closure with monotone rules

Let a constructive system contain finite object set `V`, initial available set `F`, and rules

\[
r=(P_r\to v_r)
\]

where finite prerequisite set `P_r` must all be available before `v_r` can be constructed.

Define the monotone operator

\[
\Phi(S)=S\cup\{v_r:P_r\subseteq S\}.
\]

The constructive closure is the least fixed point

\[
Cl(F)=\bigcup_{t\ge0}\Phi^t(F).
\]

## Theorem CC-T1 — closure is exact reachability state

For future challenge `v`, success under unlimited time and the registered rule set occurs iff

\[
v\in Cl(F).
\]

Thus `Cl(F)` is sufficient for all binary future module-reachability queries.

## Theorem CC-T2 — present behavior is insufficient

For every `k`, there exists a family of `2^k` systems with identical current input-output behavior but every possible future success signature over `k` construction challenges.

Hence any exact descriptor of all `k` future challenge outcomes requires at least `k` bits.

This is the v1 direct-constructor lower bound and remains unchanged.

---

# 4. Construction depth and deadline capability

Define earliest construction round recursively by

\[
t(v)=0 \quad(v\in F)
\]

and for other objects

\[
t(v)=1+\min_{r:v_r=v}\max_{u\in P_r}t(u),
\]

with `t(v)=infinity` when no rule has all prerequisites eventually reachable.

## Theorem CC-T3 — min-max deadline law

With unlimited parallelism and synchronous construction rounds, `t(v)` is exactly the earliest possible round at which `v` can be constructed.

### Proof

Lower bound: every rule producing `v` must wait until all its prerequisites are available, so use of rule `r` cannot finish before `1+max_{u in P_r}t(u)`. Taking the best rule gives the stated lower bound.

Attainment: construct every reachable object at its recursively assigned earliest round. By induction on `t`, all prerequisites of the minimizing rule for `v` are available by round `t(v)-1`, so `v` is constructed at round `t(v)`. QED.

## Corollary CC-C1 — exact capability under deadline `T`

The full set of modules available by deadline `T` is exactly

\[
C_T=\{v:t(v)\le T\}.
\]

This is a quantitative capability law, not only a qualitative claim that construction matters.

## Negative twin

When all future demands are known in advance and the horizon is short enough that all needed modules can be precompiled at lower total burden, constructive closure has no predicted advantage.

---

# 5. Strong symbolic reduction for explicit monotone construction

Let

\[
I=\sum_r |P_r| + |R| + |V|
\]

be total explicit rule incidence.

## Theorem CC-R1 — linear-time forward-chaining compilation

For an explicit finite monotone constructor system, an ordinary symbolic program can compute `Cl(F)` in

\[
O(I)
\]

time and `O(I)` representation space using prerequisite counters and a queue of newly available objects.

### Proof

For each rule, store the number of prerequisites not yet available and incidence links from each prerequisite object to the rules that require it. Initialize a queue with `F`. Each object enters the queue at most once. When popped, decrement each incident rule counter once. When a counter reaches zero, enqueue that rule's output if new. Every object, rule, and prerequisite incidence is processed a constant number of times. QED.

The same data structure computes closure layers/earliest rounds for acyclic rule systems, and standard fixed-point iteration gives the general monotone closure.

## Consequence CC-R2

Explicit monotone constructive closure does not establish an H3 polynomial-complexity domain distinct from symbolic/program computation. The representation and reachability law compile with linear overhead.

This leaves only tighter H0-H2 lifecycle possibilities such as:

```text
native physical materialization
local update without global recompilation
massive parallel construction
energy/communication locality
constructor reuse across changing hardware/ecologies
```

Those require separate lower bounds and experiments.

---

# 6. What is proved and what remains open

## Relational local-to-global state

Proved:

```text
arbitrary-graph consistency theorem
2^c exact solution count
beta_1-dimensional obstruction quotient
beta_1-bit lower bound for full independent obstruction-query family
linear symbolic realization
```

Not proved:

```text
any H2/H3 separation from symbolic/CSP parents
real learning advantage
protected neutral recovery as a distinct domain
```

## Constructive closure state

Proved:

```text
present-behavior insufficiency
k-bit future-capability lower bound
closure sufficiency
exact min-max deadline capability law
linear symbolic compilation for explicit monotone rules
```

Not proved:

```text
H0-H2 physical/lifecycle separation
super-polynomial separation from universal program/morphogenesis
protected real-world niche advantage
new-domain status
```

---

# 7. Hardening rule

A theorem that proves only compression relative to a deliberately weak baseline must not be cited as domain evidence. Every positive theorem must be paired with the strongest known compiler theorem. If the compiler matches the native asymptotics, the novelty claim is demoted even if the representation remains scientifically useful.
