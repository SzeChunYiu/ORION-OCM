# GMI Section D Phase Winners V2 — Pre-outcome Freeze

Issue: #675  
Parent ledger: #602  
Parent Section D witness: #674 / `research/gmi-section-d-free-lunch-v1/`

## Status and authority

This file is the **pre-outcome authority** for the V2 Section D experiment. It must exist in Git history before any scored V2 result JSON, witness output, or result/proof document is committed.

The experiment is finite, exact and prospective. It asks whether three still-missing morphology regions can be made to enter a registered Pareto frontier under architecture-name-free obligation/resource conditions:

1. posterior/belief state;
2. weighted local composition;
3. online frontier search/planning.

A fourth target is search-method robustness: the same held-out winner must be recovered by exact enumeration and by an independently coded non-exhaustive seeded stochastic morphology search.

The claim ceiling, even if every prediction passes, is:

```text
FINITE_EXACT_PROSPECTIVE_SECTION_D_PHASE_LAW_V2
PARENT_OWNED_BAYES_THRESHOLD_SEARCH
NO_UNIVERSAL_NEURAL_PROBABILISTIC_PLANNING_OR_REAL_SCALE_CLAIM
```

No result here may be used to claim that classical no-free-lunch theorems are false. #674 remains the NFL symmetry control.

---

# 1. Common protocol

## 1.1 Candidate evaluation

Each candidate is evaluated on:

```text
valid_exactly       whether every registered obligation in the world is met
persistent_cells    retained cells that survive between queries
working_cells       peak scratch cells required anywhere in lifecycle
lifecycle_ops       install/update + serving operations over the registered horizon
```

A candidate is eligible only if `valid_exactly` is true and all hard resource caps are met.

Pareto dominance is ordinary coordinatewise dominance over the three resource coordinates:

```text
A dominates B iff
A.persistent_cells <= B.persistent_cells
and A.working_cells <= B.working_cells
and A.lifecycle_ops <= B.lifecycle_ops
and at least one inequality is strict.
```

There is no scalarization, learned weight, or post-hoc preference coefficient.

## 1.2 Remints

The scored witness must run each world in its base encoding and in a disjoint remint:

- P: exchange the observable token names `0 <-> 1` and exchange latent-state names consistently;
- N: bit-coordinate permutation `pi_N = (5, 0, 7, 2, 6, 1, 3, 4)`;
- S: node-token permutation `pi_S = (6, 2, 7, 0, 5, 1, 4, 3)`.

A passing remint must preserve validity, exact resource counts and the exact Pareto winner after mapping names back. Architecture/family names may not be inputs to the selector.

## 1.3 Exact and stochastic morphology search

Two search procedures are frozen.

### Search A — exact authority

Enumerate every frozen candidate in the world, evaluate exact validity/resource coordinates, remove invalid/over-cap candidates, then compute the complete nondominated set.

### Search B — non-exhaustive seeded stochastic replication

For each seed `s in {0,...,99}`:

```text
state = s + 1
repeat 64 proposals:
    state = (1664525 * state + 1013904223) mod 2^32
    i = state mod K
    evaluate candidate i
    retain the nondominated set among candidates sampled so far
```

where `K` is the number of frozen candidates in that world.

The stochastic procedure samples with replacement and is not allowed to enumerate missing candidates after the 64th proposal. It observes candidate semantics only through the same validity/resource evaluator. Family names are revealed only after the retained mechanism(s) are selected.

Frozen success criterion:

```text
for each of P, N and S independently,
>= 95 of the 100 seeds must contain the exact held-out winner
in the stochastic retained nondominated set.
```

This criterion is intentionally allowed to fail on some seeds. Passing it is evidence only for robustness in this finite candidate grammar.

---

# 2. P world — posterior state enters the frontier

## 2.1 Obligation

Latent state:

```text
theta in {0,1}, P(theta=0)=P(theta=1)=1/2.
```

Evidence consists of `T=12` conditionally independent binary observations. For each observation `y`:

```text
P(y = theta | theta) = 2/3
P(y != theta | theta) = 1/3.
```

After the evidence phase, the system receives `Q` decision queries. The query carries a loss context, so one cached action is not sufficient. The scored held-out horizon is:

```text
T = 12
Q = 8
```

The exact evaluator checks every reachable evidence count `n1 in {0,...,12}` and all eight frozen loss contexts, not one favored history.

The eight contexts are `(wrong_guess_cost W, safe_cost S)`:

```text
(3,1), (4,1), (5,1), (5,2),
(6,1), (7,2), (8,3), (9,4).
```

Actions are `guess_0`, `safe`, `guess_1` with losses:

```text
L(guess_0, theta=0) = 0
L(guess_0, theta=1) = W
L(guess_1, theta=1) = 0
L(guess_1, theta=0) = W
L(safe, theta) = S for either theta.
```

Bayes-optimal action is the exact minimum expected-loss action, with deterministic tie order:

```text
guess_0 < safe < guess_1.
```

For count state `(n0,n1)`, common likelihood factors cancel and exact unnormalised evidence weights are:

```text
w0 = 2^n0
w1 = 2^n1.
```

Thus the posterior is `w1/(w0+w1)`.

## 2.2 Frozen candidates

### P0 point-only

Retains only a one-bit MAP latent label after evidence, with ties mapped to latent label 1. It may use the supplied loss context but no confidence, count, history or posterior weight.

Frozen prediction: **invalid**. Two evidence states can share MAP label 1 while requiring different Bayes actions under `(W,S)=(3,1)`:

```text
n1=n0=6: posterior 1/2 -> safe
n1=7,n0=5: posterior 4/5 -> guess_1.
```

### P1 raw-history replay

Retains all 12 observation tokens.

Resource law:

```text
persistent_cells = T
working_cells = 2
update/install ops = T
serve ops/query = 2T + 4
lifecycle_ops = T + Q(2T+4).
```

The `2T` term means two explicit likelihood multiplications per stored observation. No exponentiation macro is allowed.

### P2 count/replay

Retains `(n0,n1)` and reconstructs evidence weights from counts on every decision query.

```text
persistent_cells = 2
working_cells = 2
update ops = T
serve ops/query = T + 4
lifecycle_ops = T + Q(T+4).
```

The `T` query term is exactly `n0+n1` explicit doublings. No hidden power/exponentiation primitive is allowed.

### P3 online belief weights

Retains exact proportional evidence weights `(w0,w1)` and updates both after every observation.

```text
persistent_cells = 2
working_cells = 2
update ops = 2T
serve ops/query = 4
lifecycle_ops = 2T + 4Q.
```

The four query operations are the frozen exact comparisons needed to select the minimum expected-loss action from `(w0,w1,W,S)`; normalization is not required because a common positive denominator cancels.

## 2.3 Frozen phase law

For P2 and P3, persistent and working cells are equal, so lifecycle operations decide dominance:

```text
P3 < P2
iff 2T + 4Q < T + Q(T+4)
iff T < QT
iff Q > 1.
```

Therefore:

```text
Q = 1     P2 and P3 tie in all frozen resource coordinates
Q >= 2    P3 strictly dominates P2
```

At held-out `(T,Q)=(12,8)`:

```text
P1 raw history:  persistent 12, working 2, lifecycle 236
P2 count/replay: persistent  2, working 2, lifecycle 140
P3 belief:       persistent  2, working 2, lifecycle  56
```

Frozen held-out prediction: **P3 is the unique exact Pareto winner.**

## 2.4 Negative twin

Under ordinary symmetric binary 0-1 decision loss with only the final class action required, MAP is a sufficient decision statistic. The witness must exhibit this as a negative twin and must not claim that full belief state is universally necessary.

## 2.5 Parent boundary

The belief-state/posterior result belongs to Bayesian decision theory and finite partially observed control. Relevant parents include Blackwell's comparison-of-experiments/value-of-information framework and Smallwood-Sondik belief-state control. GMI's only residual here is the registered composition/protocol and cross-family Pareto accounting.

---

# 3. N world — weighted local composition enters the frontier

## 3.1 Obligation

Input `x in {0,1}^8`.

Held-out exact obligation:

```text
y(x) = 1 iff HammingWeight(x) = 4.
```

The evaluator exhausts all 256 inputs.

Hard persistent-memory cap:

```text
persistent_cells <= 32.
```

There is no named `EXACT_4`, shell, neural-network, DNF or architecture-family primitive. The added generic mechanism is only composition of weighted sums, scalar thresholds and a final threshold over intermediate Boolean outputs. If a future grammar adds a dedicated exact-count macro, this frozen result need not survive and no universality claim is permitted.

## 3.2 Frozen candidates

### N0 full map

One output per input:

```text
persistent_cells = 256.
```

Frozen prediction: over cap.

### N1 default + exceptions

Store majority default plus minority keys. The shell contains:

```text
C(8,4) = 70
```

positive points out of 256, so:

```text
persistent_cells = 1 + 70 = 71.
```

Frozen prediction: over cap.

### N2 affine fold

Any GF(2)-affine Boolean function.

Frozen prediction: invalid for the exact-weight-4 shell.

### N3 one Hamming-weight cutoff

Any threshold `1[weight >= t]` or polarity complement.

Frozen prediction: invalid because one monotone cutoff cannot isolate a single interior Hamming shell.

### N4 one cutoff + exceptions

Choose the best N3 cutoff and store correction keys.

Frozen prediction: the best base is `1[weight >= 4]`, which is correct on the weight-4 shell and wrong on all points with weights 5,6,7,8:

```text
C(8,5)+C(8,6)+C(8,7)+C(8,8)
= 56 + 28 + 8 + 1
= 93
```

That is **not** the best polarity/cutoff overall. The registered exhaustive evaluator must search every cutoff and both polarities. The frozen predicted minimum correction count is **56**, achieved by a cutoff/polarity choice that must be reported by the witness, giving:

```text
persistent_cells = 2 + 56 = 58.
```

Frozen prediction: over cap.

The experiment is failed if exhaustive evaluation finds a correction count below 56.

### N5 two-boundary weighted local composition

Construct two generic weighted threshold units:

```text
h4 = 1[sum_i x_i >= 4]
h5 = 1[sum_i x_i >= 5]
```

and a final threshold implementing `h4 AND (NOT h5)`.

Parameter-cell accounting:

```text
h4: 8 weights + 1 threshold = 9
h5: 8 weights + 1 threshold = 9
out: 2 weights + 1 threshold = 3
total persistent_cells = 21.
```

Frozen serve accounting counts 18 weighted-input accumulations/comparisons per query. Installation/description is charged separately exactly as emitted by the witness; all candidates receive the same exhaustive-verification unit count, so the hard-memory result does not depend on that common term.

Frozen prediction: exact on all 256 inputs and under the 32-cell cap.

## 3.3 Frozen held-out prediction

At cap 32, N5 is predicted to be the **only valid frozen candidate under the cap**, hence the unique exact Pareto winner.

This mechanism may be classified after recovery as `weighted_local_composition` / neural-like, but the representation is parent-owned by threshold logic / threshold circuits. No claim of a neural-exclusive representation is allowed.

## 3.4 Negative twin

For:

```text
y_twin(x) = 1[HammingWeight(x) >= 4]
```

N3 one-cutoff is exact with two persistent description cells and must beat the deeper composition. The witness must fail if the weighted-composition morphology is selected universally.

## 3.5 Search-method replication target

The stochastic morphology sampler in Section 1.3 runs over N0..N5 with names hidden until selection. At least 95/100 frozen seeds must sample and retain N5 as the exact held-out winner.

---

# 4. S world — online search/planning enters the frontier

## 4.1 Graph and obligation

Base graph has eight opaque node tokens `0..7` and ten undirected unit-cost edges:

```text
(0,1), (0,2), (1,3), (3,7), (2,4),
(4,5), (5,6), (6,7), (1,4), (2,5).
```

Every query supplies an arbitrary ordered pair `(start, goal)`, `start != goal`. The obligation is to return a first hop that lies on a shortest path. The evaluator checks all 56 ordered pairs.

Node token values are semantically opaque. A remint permutes them. No arithmetic on token values is a legal source of path information.

Held-out query horizon:

```text
Q = 4.
```

## 4.2 Frozen candidates

### S0 token-greedy without frontier

At each step choose the adjacent token whose integer spelling is closest to the goal token; no frontier or backtracking.

This candidate is deliberately label-dependent and exists only as a negative control.

Frozen prediction: invalid on at least one ordered pair in the base graph. In particular, for base labels and query `0 -> 7`, it chooses `2` first although a shorter route starts with `1`.

### S1 online complete BFS

For every query, run a complete breadth-first traversal from `start`, retaining enough predecessor information to return an exact shortest first hop. To keep resource counts encoding-independent, the registered implementation scans the full connected graph even if `goal` is discovered early.

With `N=8`, `E=10`:

```text
B = N + 2E = 28 charged scan operations per query.
```

Resources:

```text
persistent_cells = 1       # generic search mechanism state, no pair-specific route table
working_cells = 8          # one scratch record per node
lifecycle_ops = 28Q.
```

### S2 compiled all-pairs next-hop policy

During installation, run the same complete BFS once from each of the 8 sources, then retain one next-hop entry for every ordered distinct pair.

Resources:

```text
persistent_cells = 1 + 8*7 = 57
working_cells = 8
build_ops = 8*28 = 224
serve_ops/query = 1
lifecycle_ops = 224 + Q.
```

## 4.3 Frozen phase law

S1 has strictly lower persistent memory; working memory is equal. S1 dominates S2 exactly while:

```text
28Q <= 224 + Q
27Q <= 224
Q <= 8.
```

Thus:

```text
Q <= 8    online BFS dominates compiled all-pairs
Q >= 9    neither dominates: online uses less persistent memory,
          compiled uses fewer lifecycle operations.
```

At held-out `Q=4`:

```text
S1: persistent 1,  working 8, lifecycle 112
S2: persistent 57, working 8, lifecycle 228
```

Frozen held-out prediction: **S1 is the unique exact Pareto winner.**

This is an online-vs-compiled amortization law, not a claim that BFS is the best planner in general.

## 4.4 Remint

Apply `pi_S` to every node token in the graph and all ordered queries. Shortest-path distances and S1/S2 resource laws must be unchanged. The exact winner at `Q=4` must remain S1 after mapping token names back.

## 4.5 Parent boundary

Breadth-first shortest-path search, planning-as-search and amortized compilation own the mechanism. Classical graph search and rational metareasoning are parents. GMI's residual is only the architecture-independent registration tying recurrence/resource coordinates to morphology selection.

---

# 5. Frozen predictions summary

The V2 witness passes only if all of the following hold without changing this file:

```text
P1  P point-only candidate is invalid on the registered asymmetric-safe context.
P2  P count/replay and belief tie at Q=1.
P3  P belief strictly dominates count/replay for every checked Q>=2.
P4  P held-out T=12,Q=8 unique exact Pareto winner = belief weights.
P5  P 0-1-loss negative twin admits a point/MAP decision statistic.
P6  P remint preserves exact results.

N1  N full map = 256 cells.
N2  N default+exceptions = 71 cells.
N3  N exhaustive best one-cutoff+exceptions correction count = 56, total 58 cells.
N4  N affine and one-cutoff candidates are inexact.
N5  N weighted local composition = 21 cells and exact on 256/256 inputs.
N6  N held-out cap32 unique exact Pareto winner = weighted local composition.
N7  N >=4 negative twin is won by one cutoff rather than deeper composition.
N8  N bit-coordinate remint preserves exact results.

S1  S token-greedy is invalid on at least one ordered pair.
S2  S online BFS exact on all 56 ordered pairs.
S3  S compiled next-hop exact on all 56 ordered pairs.
S4  S online dominates compiled for Q<=8.
S5  S Q>=9 gives a memory/operations tradeoff rather than domination.
S6  S held-out Q=4 unique exact Pareto winner = online BFS.
S7  S node-token remint preserves exact results.

R1  seeded stochastic morphology search uses exactly 100 seeds x 64 proposals/world.
R2  for each P/N/S, >=95/100 seeds retain the exact held-out winner.
R3  stochastic selection receives no family labels before mechanism selection.
```

Any mismatch is a failed frozen prediction and must be reported, not repaired by editing the target after outcomes are known.

---

# 6. Strongest-parent subtraction

The result document must explicitly credit at least these parent lines before stating any GMI residual:

- D. Blackwell, *Equivalent Comparisons of Experiments* (1953), decision/value-of-information ordering;
- R. Smallwood & E. Sondik, *The Optimal Control of Partially Observable Markov Processes over a Finite Horizon* (1973), belief-state control;
- classical threshold logic / threshold-circuit representation, including Muroga-style threshold logic;
- classical BFS/shortest-path search and compiled-vs-online amortization;
- Russell & Wefald-style rational metareasoning as a parent for computational-resource-aware action selection;
- Wolpert-Macready and sharpened NFL/CUP results remain the symmetry boundary inherited from V1.

The V2 residual may be described only as a finite prospective cross-morphology phase-law composition under the frozen common resource protocol.