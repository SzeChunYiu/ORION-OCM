# Neutral rediscovery of three learning laws from one low-level grammar — formalization V1

Issue #768; parent ledger #602 Section C. Pre-implementation authority: `FREEZE_V1.md`, commit `0d7810039a8705dab44928d09f1bdebd4cd3b91e`. The opaque target-table artifact was materialized afterwards at commit `2f2324109373d97e055736d1291077fe12efd296`; the scorer/search implementation did not exist at either authority point.

## 1. Claim boundary and parent subtraction

Claim ceiling:

```text
NEUTRAL_THREE_LAW_REDISCOVERY_AT_REGISTERED_FINITE_GRAMMAR_SCOPE
```

The mathematical parents are finite enumerative program synthesis, dynamic programming, exact extensional equivalence on finite domains, and elementary dependency arguments. No novelty is claimed for those techniques. The repository residual is the freeze-first shared grammar/cost protocol, family-blind opaque scoring, exact semantic quotient, global minimum-cost certificate and hostile evidence discipline.

Evidence classes:

- C1-1 and C1-2: P1 finite formal results;
- C1-3: P1 minimality consequence + P2 exhaustive quotient certificate;
- C1-4 and C1-5: P1 dependency theorems + P2 exact witnesses/exhaustion.

Not implied: universal law discovery, causal identification outside the registered table semantics, cross-grammar recovery, real-agent evidence or complete GMI.

## 2. Registered domain and shared grammar

Let

```text
U = {-1,0,1}^4
```

with coordinates `(w,x,y,r)` and the 81 rows in lexicographic product order. All values are exact rationals.

The single grammar, unchanged across all three targets, is

```text
Expr ::= -1 | 0 | 1 | w | x | y | r
       | half(Expr)
       | (Expr + Expr)
       | (Expr - Expr)
       | (Expr * Expr).
```

Every terminal and operator node costs one. Thus

```text
cost(terminal)=1,
cost(half(a))=1+cost(a),
cost(a op b)=1+cost(a)+cost(b).
```

The registered cap is `C=6`.

For any expression `e`, let

```text
T(e) = (e(u))_{u in U} in Q^81
```

be its complete exact truth table. The semantic quotient stores one canonical minimum-cost representative per table.

The scorer receives only opaque target IDs and frozen 81-entry target vectors. It does not branch on target ID and contains no named learning-law template.

## 3. C1-1 — bounded search completeness [P1]

### Theorem

For every legal expression `e` with `cost(e)<=6`, the dynamic programme contains semantic table `T(e)` at some recorded cost no greater than `cost(e)`.

### Proof

Proceed by structural induction on `e`.

**Base.** Every legal terminal is inserted at cost one, so its table is present exactly at its syntactic cost.

**Unary step.** Let `e=half(a)` with true cost `1+cost(a)`. By induction there is a stored expression `a*` with

```text
T(a*)=T(a)
and cost(a*)<=cost(a).
```

When the DP processes cost `1+cost(a*)`, it applies `half` to every table first appearing at the previous cost and therefore generates

```text
T(half(a*)) = T(half(a)) = T(e)
```

at cost no greater than `cost(e)`. If that table was already seen, then it was seen at an even lower cost, so the claim remains true.

**Binary step.** Let `e=a op b`, `op in {+,-,*}`. By induction, semantic representatives `a*` and `b*` occur at costs `ca<=cost(a)` and `cb<=cost(b)`. At total DP cost `1+ca+cb`, the ordered cost split `(ca,cb)` is enumerated and the operator is applied to every pair of semantic tables first appearing at those costs. Hence it generates

```text
T(a* op b*) = T(a op b) = T(e)
```

no later than cost `1+cost(a)+cost(b)=cost(e)`. Again, quotienting can only replace this generation by an already-existing identical table at lower cost.

Thus every legal semantic table reachable by a cost-`<=6` expression is represented by the quotient. QED.

A separate hostile test independently enumerates the raw syntactic search through cost 3, without semantic quotienting, and verifies every resulting table is present in the DP at no greater cost.

## 4. C1-2 — quotient soundness [P1]

### Theorem

Two expressions are merged by the registered quotient iff they define the same function on the registered finite domain `U`.

### Proof

The quotient key is the exact 81-tuple `T(e)`. Equality of keys means equality of every rational output on every registered input row, which is exactly equality of functions `U -> Q`. Conversely, if two functions agree on every `u in U`, their 81-tuples are componentwise equal and therefore identical keys. No approximation, float tolerance or sampled comparison is used. QED.

The theorem is deliberately finite-domain scoped. Two expressions that agree on `U` may differ outside `U`; this lane makes no claim there.

## 5. C1-3 — neutral globally minimal recovery [P1/P2]

The exhaustive quotient contains exactly

```text
cost 1:    7 new semantic tables
cost 2:    6
cost 3:   60
cost 4:  128
cost 5:  650
cost 6: 1834
----------------
total:   2685
```

The three opaque tables are first encountered as:

```text
opaque_1: cost 4,  half((w+y))
opaque_2: cost 6,  ((half(x)*y)+w)
opaque_3: cost 6,  ((half(r)*x)+w)
```

The canonical expressions are a reporting choice within equal-cost semantic ties; notably the scorer was not given the frozen oracle formulas. For example, `opaque_2` is recovered as `half(x)*y + w`, extensionally equal on the whole exact domain to `w + (x*y)/2`.

### Minimality

By C1-1, every legal expression of lower cost is represented in the quotient. The target table is absent from all quotient layers below its reported first layer. Therefore no lower-cost legal expression exists. The reported costs 4, 6 and 6 are global minima within the frozen grammar/cap, not merely costs of three hand-picked constructions. QED.

This is bounded neutral rediscovery, not evidence that these are globally shortest descriptions in other languages.

## 6. C1-4 — irreducible dependency theorem [P1/P2]

### Theorem

Let `f:U->Q`. Suppose there exist two registered inputs `u,v` that differ only in coordinate `z` and satisfy `f(u) != f(v)`. Then every exact deterministic realization of `f` on `U` must semantically depend on `z`.

### Proof

Assume an exact realization does not depend on `z`. Then holding all other coordinates fixed forces identical output for all values of `z`, so it must return the same output on `u` and `v`. This contradicts `f(u) != f(v)`. QED.

Exact witness pairs found before any architectural classification are:

### `opaque_1`

```text
w witness:
(-1,-1,-1,-1) -> -1
( 0,-1,-1,-1) -> -1/2

y witness:
(-1,-1,-1,-1) -> -1
(-1,-1, 0,-1) -> -1/2
```

The table is exhaustively invariant to `x` and `r`, so its exact irreducible signature is

```text
{w,y}.
```

### `opaque_2`

```text
w: (-1,-1,-1,-1)->-1/2 ; (0,-1,-1,-1)->1/2
x: (-1,-1,-1,-1)->-1/2 ; (-1,0,-1,-1)->-1
y: (-1,-1,-1,-1)->-1/2 ; (-1,-1,0,-1)->-1
```

It is exhaustively invariant to `r`; signature:

```text
{w,x,y}.
```

### `opaque_3`

```text
w: (-1,-1,-1,-1)->-1/2 ; (0,-1,-1,-1)->1/2
x: (-1,-1,-1,-1)->-1/2 ; (-1,0,-1,-1)->-1
r: (-1,-1,-1,-1)->-1/2 ; (-1,-1,-1,0)->-1
```

It is exhaustively invariant to `y`; signature:

```text
{w,x,r}.
```

The implementation removes each required variable terminal from the otherwise unchanged grammar and reruns the exact search. Every affected target becomes unreachable through the cap. The counterfactual theorem is stronger than the cap-specific observation: an expression language with no access to `z` cannot realize a table proven to depend on `z` at any cost.

## 7. C1-5 — qualitative distinctness [P1/P2]

The three exact target tables are pairwise unequal. In addition their irreducible dependency signatures are pairwise different:

```text
{w,y}
{w,x,y}
{w,x,r}.
```

Therefore, within the registered semantics, the recovered objects are not one update function under three syntactic spellings. They require different information dependencies. This is the registered sense in which the three recovered laws are qualitatively distinct.

No claim is made that dependency signature alone is a universal classification of learning laws.

## 8. Load-bearing hostiles

### H1 — remove `half`

With terminals in `Z` and only `+,-,*`, structural induction shows every expression is integer-valued on the integer input domain. Every frozen target has at least one half-integer output. Therefore no target is expressible in that ablated grammar at any cost. The exact cap-6 search independently confirms zero matches.

### H2 — perturbed target

The first output of `opaque_1` is changed by `+1/4`, while the remaining 80 outputs are untouched. The resulting table digest is

```text
dbeca315479bb6d3b18b381b9fa1ec2f6221e22b9494c76eced4419ff5886766
```

and it is absent from all 2,685 registered quotient tables. This prevents the evaluator from simply accepting any nearly matching table.

### H3 — equivalent syntax

`half(w)+half(y)` has exactly the same 81-vector as `half(w+y)`, but costs 5 rather than 4. The quotient reports cost 4 and keeps the lower-cost semantic representative. Thus syntactic multiplicity does not inflate recovery counts or defeat minimum-cost reporting.

### H4 — opaque-ID permutation

Reversing the opaque target order leaves the mapping from target table to `(matched,min_cost,table_digest)` unchanged. The scorer therefore does not exploit target-ID order.

### H5 — post-activation mutation

After target activation, attempts to change grammar cap, variable access or `half` availability are rejected. This makes task-specific post-outcome repricing a protocol violation rather than a new experiment.

## 9. Falsifiers and scope

This lane fails if any frozen target hash does not reproduce; a legal cost-`<=6` syntactic table is missing from the quotient; unequal exact tables are merged; any target appears below or above its frozen minimum; a required-variable ablation matches; a supposedly irrelevant variable changes a target; removing `half` reaches a half-integer target; the perturbed table matches; target-ID permutation changes semantic outcomes; post-activation grammar mutation succeeds; or normal and optimized Python disagree.

Strongest permitted terminal from this lane alone:

```text
NEUTRAL_THREE_LAW_REDISCOVERY_AT_REGISTERED_FINITE_GRAMMAR_SCOPE
```
