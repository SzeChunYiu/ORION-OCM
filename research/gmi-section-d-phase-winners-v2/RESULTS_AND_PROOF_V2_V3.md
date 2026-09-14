# Section D Phase Winners V2 + Neural Replication V3 — Results and Proof Boundary

Pre-outcome authorities:

- V2 freeze: commit `b8c407428cfb76dda736d9867e50c1c8a365eabb`.
- V3 neural-replication freeze: commit `e08f9ddcc53516fafc685f8da5bd182c0c9df7d0`.

Executable receipt: `section_d_phase_winners_witness.py` -> `RESULT_V2_V3.json`.

## Executive disposition

The experiment produced **one preregistered quantitative failure and three phase-winner results**:

1. **V2 overall is FAILED_PREREGISTRATION.** Its N-world forecast said the best cutoff-plus-exceptions residual would be 56. Exhaustive enumeration finds 70 because the frozen analysis forgot the legal constant-zero cutoff. The freeze was not edited.
2. The separately preregistered **P probabilistic subtest passes**: at `T=12,Q=8`, exact belief weights are the unique Pareto winner among the frozen candidates.
3. The separately preregistered **S online-planning subtest passes**: at `Q=4`, complete online BFS is the unique Pareto winner and the frozen crossover occurs at `Q=9`.
4. The fresh **V3 neural-like replication passes cleanly**: on a new 9-bit held-out exact-weight-4 shell, the analytically frozen cutoff residual is exactly 126 and the 23-cell weighted-local-composition mechanism is the unique valid candidate under the 32-cell cap.
5. The independent seeded stochastic morphology search recovers each exact held-out winner in **100/100 seeds**, exceeding the frozen >=95/100 criterion without seeing family names before selection.

No result here upgrades the claim to universal morphology, real-scale transfer, or novel Bayesian/threshold/search theory.

---

# 1. Why V2 is formally failed

For the V2 neural world, target positives are the 70 points with Hamming weight 4 in `{0,1}^8`.

The freeze predicted a best one-cutoff-plus-exceptions residual of 56. Exhaustive search over every integer cutoff and both polarities instead finds:

```text
best residual = 70
best registered representation = constant zero
```

A constant-zero cutoff makes errors only on the 70 positive shell points. This candidate had been omitted in the hand reasoning that produced 56.

Therefore:

```text
frozen V2 N3 prediction = false
V2 overall status       = FAILED_PREREGISTRATION
```

The qualitative cap-32 winner would still have been weighted local composition because `2+70=72 > 32`, but that survival is **not** used to close the neural-like box from V2. A new held-out world was frozen instead.

This is the intended function of prospective registration: the mistake becomes evidence about the theory/protocol rather than a post-hoc edit.

---

# 2. P world — probabilistic belief wins prospectively

## 2.1 Point state is insufficient

For binary latent state with observation reliability `2/3`, proportional posterior weights after `n1` ones and `n0` zeros are:

```text
w0 = 2^n0
w1 = 2^n1.
```

Under the frozen `(W,S)=(3,1)` decision context:

```text
n1=6,n0=6 -> posterior 1/2 -> safe
n1=7,n0=5 -> posterior 4/5 -> guess_1.
```

Both histories map to the same frozen MAP point label 1, so a point-only state cannot implement both Bayes-optimal decisions. Across all registered evidence counts and eight loss contexts, the witness finds 9 such point-state conflicts.

The symmetric 0-1-loss negative twin passes: MAP alone is a sufficient final decision statistic there. So the witness does not claim belief is universally necessary.

## 2.2 Exact resource law

Frozen count/replay:

```text
C_count(T,Q) = T + Q(T+4).
```

Frozen online belief weights:

```text
C_belief(T,Q) = 2T + 4Q.
```

The two candidates have identical persistent and working state `(2,2)`. Thus:

```text
C_belief < C_count
iff 2T+4Q < T+Q(T+4)
iff T < QT
iff Q > 1.
```

The executable phase sweep matches exactly:

```text
Q=1      {count_replay, belief_weights}
Q=2..12  {belief_weights}
```

At held-out `T=12,Q=8`:

| mechanism | persistent | working | lifecycle ops | exact? |
|---|---:|---:|---:|---|
| point only | 1 | 1 | 20 | no |
| raw history replay | 12 | 2 | 236 | yes |
| count/replay | 2 | 2 | 140 | yes |
| belief weights | 2 | 2 | 56 | yes |

So `belief_weights` is the unique exact Pareto winner.

The observation/latent relabel remint also passes. Tie priority is transformed consistently with the action-name remint, so a pure renaming cannot create a label artifact.

## 2.3 Parent subtraction

This result is not a new theorem of probability. Bayesian decision theory owns posterior expected-loss minimization. Blackwell's comparison-of-experiments line owns value-of-information ordering; Smallwood-Sondik own finite belief-state control in partially observed processes. The residual here is only the prospective GMI protocol that places posterior state in the same registered resource/Pareto accounting used for the other morphologies.

---

# 3. V3 N world — clean neural-like / weighted-composition replication

The new held-out target is:

```text
x in {0,1}^9
y=1 iff HammingWeight(x)=4
persistent-memory cap = 32.
```

## 3.1 Analytic lower alternatives, frozen before enumeration

There are:

```text
C(9,4) = 126
```

positive shell points.

Therefore:

```text
full map               = 512 cells
default + exceptions   = 127 cells.
```

The corrected cutoff analysis explicitly includes constants.

For `1[weight>=t]`:

- `t>=5`: the base is disjoint from the shell, so error is `126 + tail(t) >=126`, equality at `t=10`;
- `t<=4`: the base contains the shell and at least all weights 5..9, already 256 errors.

For complement `1[weight<t]`:

- `t<=4`: error is `126 + lower(t) >=126`, equality at `t=0`;
- `t>=5`: it contains the target shell plus at least weights 0..3, adding 130 false positives.

Thus the prospectively frozen minimum residual is exactly 126, and cutoff+exceptions needs:

```text
2 + 126 = 128 cells.
```

The exhaustive witness matches 126 exactly. It also confirms no GF(2)-affine candidate and no single cutoff is exact.

## 3.2 Constructive upper bound

Two generic weighted threshold units and one output threshold suffice:

```text
h4 = 1[sum x_i >= 4]
h5 = 1[sum x_i >= 5]
y  = h4 AND NOT h5.
```

Frozen parameter accounting:

```text
h4  9 weights + threshold = 10
h5  9 weights + threshold = 10
out 2 weights + threshold =  3
                             --
total                       23 cells.
```

The witness exhausts all 512 inputs and finds 512/512 exact agreement. At cap 32 it is the only valid frozen candidate under the cap, hence the unique Pareto winner.

The coordinate-permutation remint passes.

## 3.3 Negative twin

For the monotone twin:

```text
y=1 iff HammingWeight(x)>=4
```

a single cutoff is exact with two description cells and dominates the deeper composition. This is a hard guard against universal selection of the neural-like phenotype.

## 3.4 Classification and parent subtraction

The mechanism is classified **after** recovery as `weighted_local_composition` / neural-like because the neutral graph is made of weighted sums and scalar thresholds. Classical threshold logic/circuit theory owns this representation. This witness does not establish a neural-exclusive form; an equivalent threshold circuit is the same mechanism under a different disciplinary label.

---

# 4. S world — online search/planning wins prospectively

The frozen graph has `N=8`, `E=10`, opaque node tokens and all 56 ordered distinct start-goal queries.

A label-arithmetic greedy candidate is deliberately illegal as a structural shortcut and fails on 9 ordered pairs. For the frozen explicit example `0 -> 7`, token-greedy chooses first hop 2, while a shortest route starts with 1.

Both exact candidates pass all 56 pairs:

```text
online complete BFS:
  persistent = 1
  working    = 8
  ops        = 28Q

compiled all-pairs next hop:
  persistent = 57
  working    = 8
  ops        = 224 + Q.
```

Since working memory is equal and online search uses less persistent memory, online dominates while:

```text
28Q <= 224+Q
27Q <= 224
Q <= 8.
```

The executable sweep matches the frozen law exactly:

```text
Q=1..8   {online_bfs}
Q=9..16  {online_bfs, compiled_all_pairs}
```

At held-out `Q=4`:

```text
online_bfs         = (persistent 1,  working 8, ops 112)
compiled_all_pairs = (persistent 57, working 8, ops 228)
```

so online BFS is the unique exact Pareto winner.

The node-token remint preserves exactness, resource counts and the held-out winner.

This is a bounded online-vs-compiled amortization law. Classical BFS/shortest-path planning and computational-resource tradeoffs own the mechanism; GMI's residual is only the prospective ecology/resource-to-morphology registration.

---

# 5. Different search algorithm replication

The exact authority enumerates all frozen candidates and computes the complete Pareto set.

Independently, Search B uses a frozen 32-bit LCG, 64 uniform proposals **with replacement**, and keeps only the nondominated set among sampled candidates. It is non-exhaustive by protocol and receives only validity/resource vectors; candidate family labels are mapped back only after selection.

Frozen criterion: `>=95/100` seeds for each held-out world must retain the exact winner.

Observed:

```text
P belief winner             100/100
V3 weighted-composition     100/100
S online-BFS winner         100/100
```

This is materially stronger than the V1 all-pairs-vs-skyline implementation check because the second procedure is stochastic and is not allowed to fill in unsampled candidates after its proposal budget.

It is still only a finite candidate-grammar robustness result, not generic NAS/AutoML convergence.

---

# 6. What Section D boxes this evidence can support

At this registered finite scope, the evidence supports:

```text
[x] Demonstrate at least one phase law where neural-like wins.
[x] Demonstrate at least one phase law where probabilistic wins.
[x] Demonstrate at least one phase law where search/planning wins.
[x] Replicate with different search algorithms.
```

The neural-like box is supported by the **clean V3** replication, not by the failed V2 quantitative forecast.

Still not closed by this work:

- complete/unbounded ecology and resource coordinate schemas;
- developmental-history as a demonstrated phase axis;
- stochastic/heuristic search robustness beyond this finite candidate grammar;
- empirical/real-scale phase-boundary uncertainty;
- extrapolation beyond registered tiny worlds;
- any universal or real-scale morphology claim.

---

# 7. Falsifiers

This tranche is falsified at its claimed scope if any of the following occurs:

1. the committed result cannot be reproduced exactly from the witness;
2. P point-only state becomes sufficient for every registered asymmetric-safe context;
3. P belief fails to dominate count/replay for any checked `Q>=2` under the frozen operation contract;
4. V3 exhaustive cutoff residual is not 126;
5. the 23-cell V3 weighted composition is not exact on all 512 inputs;
6. a different frozen candidate under the 32-cell cap is exact and nondominated;
7. S online BFS is not exact on all 56 ordered pairs;
8. the `Q<=8` / `Q>=9` S crossover is not reproduced;
9. any remint changes the held-out exact winner;
10. stochastic recovery falls below 95/100 seeds in any world;
11. optimized execution changes the result receipt.

---

# 8. Literature / strongest parents

Parent ownership is intentionally explicit:

- David Blackwell, *Equivalent Comparisons of Experiments*, Annals of Mathematical Statistics 24(2), 1953, DOI `10.1214/aoms/1177729032`.
- Richard D. Smallwood and Edward J. Sondik, *The Optimal Control of Partially Observable Markov Processes over a Finite Horizon*, Operations Research 21(5), 1973, DOI `10.1287/opre.21.5.1071`.
- Saburo Muroga, *Threshold Logic and Its Applications*, Wiley-Interscience, 1971; more generally classical threshold-circuit theory.
- Classical breadth-first / shortest-path graph search and online-vs-compiled amortization.
- Stuart Russell and Eric Wefald, *Principles of metareasoning*, Artificial Intelligence 49, 1991, DOI `10.1016/0004-3702(91)90015-C`.
- Wolpert-Macready NFL and the sharpened closed-under-permutation boundary remain inherited controls from #674; this tranche does not challenge them.

## Final claim ceiling

```text
FINITE_EXACT_PROSPECTIVE_SECTION_D_PHASE_LAW_V2_WITH_RECORDED_V2_N_FAILURE
FINITE_EXACT_PROSPECTIVE_NEURAL_LIKE_PHASE_REPLICATION_V3
PARENT_OWNED_BAYES_THRESHOLD_SEARCH
NO_UNIVERSAL_NEURAL_PROBABILISTIC_PLANNING_OR_REAL_SCALE_CLAIM
```
