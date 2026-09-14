# GMI Section D Developmental-History Phase Law V4 — Pre-outcome Freeze

Date frozen: 2026-09-14.  
Parent ledger: #602.  
Child tracker: #677.  
Base: merged Section D V2/V3 tranche `b2269b9fd2de0101e01acf9da778ac478198a4f4`.

This file is the **pre-outcome authority**. No scored witness output, result JSON, or result/proof document may be committed before this freeze exists in Git history.

The claim under test is finite and exact:

> Holding the present obligation, verifier, scalar resource caps, and future query ecology fixed, two systems with equal present scalar resource occupancy can have different unique Pareto-optimal morphologies solely because their inherited **semantic installed state** differs. The history effect must disappear when future conversion cost is set to zero and must be overcome when the future serving advantage grows beyond the conversion cost.

This is a switching-cost / hysteresis / warm-start statement. It is not a universal GMI theorem of history.

Claim ceiling even if all predictions pass:

```text
FINITE_EXACT_PROSPECTIVE_DEVELOPMENTAL_HISTORY_PHASE_LAW
PARENT_OWNED_SWITCHING_COST_PATH_DEPENDENCE_WARMSTART
NO_UNIVERSAL_HYSTERESIS_OR_REAL_SCALE_CLAIM
```

---

## 1. Parent first refusal

The result document must parent-subtract at least these lines:

1. W. Brian Arthur (1989), *Competing Technologies, Increasing Returns, and Lock-In by Historical Events*, Economic Journal 99(394), 116–131, DOI `10.2307/2234208`: historical events and increasing returns can select/lock in technological trajectories.
2. Stuart Russell & Eric Wefald (1991), *Principles of Metareasoning*, Artificial Intelligence 49, 361–395, DOI `10.1016/0004-3702(91)90015-C`: computational actions should be selected by their resource-bounded decision value.
3. Marius Lindauer & Frank Hutter (2018), *Warmstarting of Model-Based Algorithm Configuration*, AAAI 32, DOI `10.1609/aaai.v32i1.11532`: previously accumulated information can reduce future configuration cost.
4. More generally, classical switching-cost, hysteresis, installed-base, indexing, and amortization theory own the mechanism.

The candidate GMI residual is only a prospective architecture-name-free Section D registration: semantic inherited state is explicitly represented as a morphology-selection coordinate and is tested beside zero-cost and long-horizon controls.

---

## 2. Present obligation and exact relation family

There are four opaque key tokens and four opaque value tokens:

```text
K = {k0,k1,k2,k3}
V = {v0,v1,v2,v3}.
```

A world relation is any bijection `rho: K -> V`. There are `4! = 24` such worlds.

The serving obligation is bidirectional exact lookup:

```text
F(k_i) = rho(k_i)
R(v_j) = rho^{-1}(v_j).
```

A candidate is valid only if it answers **all eight distinct direction/token queries** correctly for **all 24 bijections**. A mechanism that is correct only on the held-out relation is invalid.

The scored held-out relation is fixed before execution:

```text
rho(k0)=v1
rho(k1)=v3
rho(k2)=v0
rho(k3)=v2.
```

No arithmetic or lexical order of token spellings is allowed to carry relation information.

---

## 3. Physical resource contract

To remain compatible with Section D V1, the Pareto coordinate vector is:

```text
(persistent_cells, lifecycle_ops).
```

Hard persistent cap:

```text
persistent_cells <= 4.
```

Every valid candidate is charged the same exhaustive verification cost:

```text
verification_units = 8
```

(one unit per distinct serving obligation in the held-out relation).

A fixed **reconfiguration workspace of four transient cells** is supplied by the environment to every candidate at the morphology boundary. It is part of the held-fixed resource environment, not a candidate-specific Pareto coordinate. No candidate may use more than those four transient cells. This makes conversion explicit without pretending that old and new indexes coexist as persistent state.

Past construction cost before the decision point is **sunk and excluded**. Only future work is charged.

Pareto dominance is ordinary coordinatewise dominance after the hard cap; no scalarization is permitted.

---

## 4. Frozen neutral morphology grammar

Names describe mechanisms, not architecture families.

### M0 — `key_index`

Retains one value payload for each key slot.

```text
persistent_cells = 4
forward serve cost = 1
reverse serve cost = 4
```

Reverse lookup scans all four entries even if the match is found early; this keeps cost invariant under token remint and relation permutation.

### M1 — `value_index`

Retains one key payload for each value slot.

```text
persistent_cells = 4
forward serve cost = 4
reverse serve cost = 1
```

Forward lookup scans all four entries even if the match is found early.

### M2 — `dual_index`

Retains both directions.

```text
persistent_cells = 8
forward serve cost = 1
reverse serve cost = 1
```

Exact but predicted infeasible under cap 4.

### M3 — `pair_list`

Retains four explicit key/value pairs.

```text
persistent_cells = 8
forward serve cost = 4
reverse serve cost = 4
```

Exact but predicted infeasible under cap 4.

No candidate-specific cache, learned query frequency, hidden direct inverse primitive, or architecture-family macro is legal.

---

## 5. Developmental histories and future migration

At the decision boundary, the two developmental histories have equal scalar occupancy and differ only in semantic installed state:

```text
H_key:
  a valid key_index is already installed
  persistent_cells currently occupied = 4

H_value:
  a valid value_index is already installed
  persistent_cells currently occupied = 4.
```

Past build cost is excluded in both histories.

Choosing the already installed orientation costs zero future migration operations.

Changing orientation uses the common four-cell transient workspace and performs exactly:

```text
4 reads of installed entries
4 writes of reindexed entries
--------------------------------
K = 8 future migration operations.
```

The old persistent four-cell representation is then replaced by the new four-cell representation. Final persistent occupancy remains 4.

The witness must explicitly execute a reindex transformation on every one of the 24 bijections and confirm the resulting opposite orientation answers all eight queries exactly. A mere arithmetic cost stub is insufficient.

### Cold start control

`H_cold` has no installed orientation. Building either single orientation from the registered four-pair developmental input stream costs the same:

```text
4 source reads + 4 writes = 8 operations.
```

The stream is available only at the reconfiguration boundary; it is not a serving-time oracle.

---

## 6. Present future-query ecology

One future ecology block contains exactly eight queries by direction:

```text
3 forward
5 reverse.
```

The concrete held-out block is frozen as:

```text
F(k0), F(k1), F(k3),
R(v0), R(v1), R(v2), R(v3), R(v1).
```

The repeated reverse query is intentional. No candidate-specific memoization is allowed, so only the registered direction mix matters.

For one block:

```text
C_key   = 3*1 + 5*4 = 23
C_value = 3*4 + 5*1 = 17.
```

Thus the **present ecology statically favors value_index by D=6 operations per block** before migration cost.

The scored horizon is a positive integer number `m` of identical direction-mix blocks. The witness must check `m=1..8`.

---

## 7. Frozen analytic hysteresis theorem

Let two exact candidate morphologies A and B have equal persistent coordinates and equal common verification cost. Suppose future serving over horizon `h` costs `C_A(h)` and `C_B(h)`, with

```text
D_h = C_A(h) - C_B(h) > 0
```

so current future serving favors B. Let inherited A -> B conversion cost be `K>0`, while staying in the inherited orientation costs zero.

From inherited A:

```text
future(A | H_A) = C_A(h)
future(B | H_A) = K + C_B(h).
```

Therefore:

```text
A wins  iff D_h < K
A,B tie iff D_h = K
B wins  iff D_h > K.
```

From inherited B:

```text
future(B | H_B) = C_B(h)
future(A | H_B) = K + C_A(h),
```

so B strictly wins whenever `D_h>0` and `K>=0`.

If `K=0` and `D_h>0`, B wins from either inherited history: **history cannot change the winner**.

This is algebraically a switching-cost/hysteresis result. The witness must verify the frozen finite grid:

```text
base B cost c in {1,2,3,4,5}
per-block advantage D in {1,2,...,8}
conversion K in {0,1,...,12}
horizon m in {1,2,...,8}
```

for all `5*8*13*8 = 4160` tuples, including tie cases. This grid is a theorem sanity check, not a claim beyond the algebra above.

---

## 8. Frozen held-out phase predictions

Common verification `+8` appears in every valid candidate and is included in receipts below.

### 8.1 `H_key`, migration K=8

```text
key_index   ops = 8 + 23m
value_index ops = 8 + 8 + 17m
```

(the first `8` is common verification; the second in the value expression is migration).

Comparison:

```text
8+23m < 16+17m
iff 6m < 8.
```

Frozen predictions:

```text
m=1       unique feasible Pareto winner = key_index
m=2..8    unique feasible Pareto winner = value_index.
```

At the held-out point `m=1`:

```text
key_index   = (persistent 4, lifecycle 31)
value_index = (persistent 4, lifecycle 33).
```

So the inherited key morphology is predicted to remain selected **despite the present serving ecology favoring value indexing**.

### 8.2 `H_value`, migration K=8

```text
value_index ops = 8 + 17m
key_index   ops = 8 + 8 + 23m.
```

Frozen prediction for every `m=1..8`:

```text
unique feasible Pareto winner = value_index.
```

At held-out `m=1`:

```text
value_index = (4,25)
key_index   = (4,39).
```

### 8.3 Registered developmental-history collision

At the **same present obligation, same held-out relation, same future query block, same verifier, same persistent cap, same migration law, same horizon m=1, and same present scalar occupancy of four cells**, changing only semantic inherited state must change the unique winner:

```text
H_key   -> key_index
H_value -> value_index.
```

This is the box-earning prediction. If it fails, the developmental-history phase box remains open.

---

## 9. Negative controls

### C1 — zero migration cost

Set `K=0` without changing the current 3F:5R ecology.

Frozen prediction for both `H_key` and `H_value`, every `m=1..8`:

```text
unique winner = value_index.
```

The history effect must disappear.

### C2 — cold start

`H_cold`, equal build cost 8 for either orientation.

Frozen prediction for every `m=1..8`:

```text
unique winner = value_index.
```

History is not a label bonus; without an installed orientation, the statically better serving morphology wins.

### C3 — mirrored present ecology

Mirror the current direction mix to:

```text
5 forward, 3 reverse.
```

Then:

```text
C_key   = 17
C_value = 23.
```

With `K=8`:

```text
H_value, m=1  -> value_index   # inherited state retained despite current ecology favoring key
H_value, m>=2 -> key_index
H_key,   m>=1 -> key_index.
```

This must mirror the main law and prevents hard-coding a privileged orientation label.

### C4 — exhaustive relation family

All four frozen mechanisms must be evaluated on every one of the 24 bijections and all eight direction/token obligations. M0–M3 are predicted exact on all `24*8 = 192` world-query pairs.

M2/M3 remain over the persistent cap and cannot enter the held-out Pareto set merely because they are exact.

---

## 10. Disjoint token remint

Apply independent renamings:

```text
keys:
k0 -> amber
k1 -> cedar
k2 -> delta
k3 -> birch

values:
v0 -> quartz
v1 -> onyx
v2 -> jade
v3 -> opal
```

The remint changes lexical order and namespace spellings but preserves relation structure and query directions.

Frozen predictions:

- all exact answers map through the remint;
- all persistent and lifecycle resource laws are unchanged;
- the held-out `m=1` history collision remains `installed-key-orientation -> key orientation` and `installed-value-orientation -> value orientation` after names are mapped back;
- zero-cost and mirrored controls are unchanged.

---

## 11. Search / implementation robustness

Two independently coded exact selectors are frozen:

1. all-pairs coordinatewise dominance;
2. reverse-order incremental skyline.

They must agree on every history/control/horizon cell checked by the witness.

This is implementation robustness only; #676 already supplies the genuinely stochastic search-algorithm box.

---

## 12. Pass/fail ledger

The V4 witness passes only if every item below holds without editing this freeze:

```text
H1  all four candidate mechanisms are exact on all 24 bijections x 8 obligations;
H2  key/value reindex transformations are executed and exact for all 24 bijections;
H3  M2/M3 are over cap4 and excluded before Pareto comparison;
H4  H_key at m=1 uniquely selects key_index;
H5  H_value at m=1 uniquely selects value_index;
H6  H_key crosses to value_index for every m=2..8;
H7  H_value keeps value_index for every m=1..8;
H8  zero-K control selects value_index from both histories for m=1..8;
H9  cold-start control selects value_index for m=1..8;
H10 mirrored 5F:3R control produces the symmetric history/crossover law;
H11 the general theorem checker passes all 4160 frozen tuples;
H12 the disjoint key/value token remint preserves answers, costs, controls and winners;
H13 all-pairs and incremental skyline Pareto implementations agree everywhere.
```

Any mismatch is a failed preregistration. Preserve the failure; do not retune the target after outcomes.

---

## 13. Scope if successful

A clean pass can support only:

```text
[x] Demonstrate developmental history as a phase axis at the registered finite scope.
```

It cannot support:

- a complete/unbounded history coordinate schema;
- universal hysteresis;
- empirical/real-scale phase-boundary uncertainty;
- extrapolation outside the registered finite relation/query/index grammar;
- universal morphology selection.
