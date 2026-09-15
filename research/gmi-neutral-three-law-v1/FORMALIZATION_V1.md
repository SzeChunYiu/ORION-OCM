# FORMALIZATION V1 — bounded neutral three-law rediscovery

Issue #768; parent #602 Section C. `FREEZE_V1.md` is the pre-implementation authority.

## Objects

Let

```text
D = {-1,0,1}^4
```

with coordinates `(w,x,y,r)`. Let `G` be the frozen expression grammar with leaves
`w,x,y,r,-1,0,1`, unary `half`, and binary `add,sub,mul`. Every syntax-tree node costs one. Let
`G_<=6` be all expressions of total node cost at most six.

For `e ∈ G_<=6`, define its registered semantics

```text
T(e) = (e(p))_{p∈D} ∈ Q^81.
```

The semantic quotient is `G_<=6 / ~`, where `e ~ f` iff `T(e)=T(f)`.

The executable search stores a semantic table only at the **first cost layer at which that table is
reached**. Thus an expression of exact syntactic cost `c` may have the same table as a cheaper expression
and need not itself survive in exact layer `c`. All completeness/minimality statements below therefore
refer to the cumulative quotient through a cost layer, not to preservation of every redundant syntax in
that exact layer.

## C1-1 — bounded semantic-DP completeness [P1]

**Theorem.** For every integer `c∈{1,...,6}` and every expression `e` of exact cost `c`, after the DP has
processed layers `1,...,c`, its cumulative quotient contains `T(e)` represented at some cost `d<=c`.

**Proof.** Strong structural induction on `e` / its node cost.

Base `c=1`: `e` is one of the seven registered leaves. Initialization inserts its complete table. If two
leaves ever had equal registered semantics, retaining one would still preserve that table.

Inductive step: assume the claim for all strict subexpressions.

- If `e=half(a)`, let `cost(a)=c-1`. By induction the cumulative quotient through `c-1` contains a
  representative `a*` with `T(a*)=T(a)` and `cost(a*)=d<=c-1`. The construction of
  `half(a*)` therefore has cost `d+1<=c` and table `T(e)`. When layer `d+1` is processed, either that table
  is inserted, or it is already present at an even smaller cost. In either case it is present cumulatively
  by layer `c`.
- If `e=op(a,b)` for `op∈{add,sub,mul}`, write child costs `c_a,c_b` with
  `c_a+c_b+1=c`. By induction there are quotient representatives `a*`,`b*` with the same registered child
  tables and costs `d_a<=c_a`, `d_b<=c_b`. The DP visits their ordered semantic pair when processing cost
  `d_a+d_b+1<=c`, constructing exactly
  `op(T(a*),T(b*))=op(T(a),T(b))=T(e)`. Again the table is either inserted then or was already present
  earlier.

Therefore semantic deduplication cannot remove a reachable registered behavior; it can only move its
canonical representative to a cheaper layer. ∎

### Independent finite certificate

`check_raw_syntax_completeness_v1.py` does **not** use semantic pruning. It separately enumerates every raw
syntax tree through cost six and checks each complete 81-point table against the semantic quotient. The
frozen grammar has exactly

```text
cost:             1      2      3      4       5       6
raw syntaxes:     7      7    154    448    7,063  32,347
```

for `40,026` raw expressions total. The independent first-hit semantic counts must be

```text
7, 6, 60, 128, 650, 1834
```

and must exactly equal the searcher's semantic layer counts. This P2 census is a direct executable check
of the P1 argument above and of the freeze's literal “every expression” bounded-universe requirement.

**Consequence.** If a target table first appears in semantic DP layer `c`, no expression of cost `<c`
realizes it. Otherwise C1-1 would place its table in an earlier cumulative layer. Thus the first-hit layer
is a global minimum cost in `G_<=6`, not a search-order artifact.

## C1-2 — quotient soundness and completeness [P1]

For all `e,f∈G_<=6`,

```text
T(e)=T(f)
iff
for every p∈D, e(p)=f(p).
```

This is immediate from the definition of the 81-coordinate truth-table vector. Therefore retaining one
canonical representative per vector preserves every registered extensional behavior exactly. Syntax may
change; registered semantics cannot.

## C1-3 — neutral minimum-cost recovery [P1 + P2 certificate]

Let frozen target tables be `A,B,C` from `FREEZE_V1.md`. The semantic-DP certificate reports the first
layer containing each table, while the independent raw-syntax census scans all `40,026` bounded syntax
trees and independently derives the same minima. By C1-1, those layers are global bounded minima. The
preregistered expected minima are

```text
cost(A)=4,
cost(B)=6,
cost(C)=6.
```

A positive P2 result requires exact equality on all 81 points, one unchanged grammar/pricing protocol,
no target-ID branch in the search routine, and agreement between semantic-DP and raw-syntax minima.

## C1-4 — counterfactual dependency necessity [P1]

Let `f:D→Q` and coordinate `z`. Suppose there exist `p,q∈D` differing only in coordinate `z` with
`f(p) != f(q)`. Then no deterministic realization independent of `z` can equal `f` on all of `D`.

**Proof.** A function independent of `z` must assign equal outputs to any two rows identical on all other
coordinates. The exhibited pair violates that equality. ∎

Conversely, at this finite scope, if every pair differing only in `z` has equal target output, the target
is invariant to `z` on `D`. The executable certificate checks all such row pairs.

Applied to the frozen targets, the exact irreducible signatures are

```text
A: {w,y}
B: {w,x,y}
C: {w,x,r}.
```

They are pairwise distinct, so the three targets are not one extensional law under different syntax.

## C1-5 — no-`half` impossibility [P1]

Consider the ablated grammar obtained by deleting `half`. Every leaf evaluates to an integer on every
`p∈D`; `add`, `sub`, and `mul` preserve integrality. By structural induction every ablated expression is
integer-valued on all 81 inputs.

Each frozen target has at least one half-integer output. Therefore none of `A,B,C` is realizable by the
no-`half` grammar at any syntax cost, not merely below cap six.

## C1-6 — protocol immutability / confirmatory boundary [contract theorem]

The grammar, node-cost rule, cap, universe order, and tie rule are frozen before implementation. The
`Protocol` object exposes variables/operators/cap/tie rule; leaf/operator node prices and the universe are
fixed by the implementation and are not target-adjustable inputs. A scored confirmatory run is valid only
under the exact frozen protocol fingerprint. Any exposed protocol mutation after activation must terminate
as

```text
FROZEN_PROTOCOL_MUTATION.
```

This is governance, not a theorem about learning.

## Strongest-parent subtraction

C1-1/C1-2 are standard exhaustive program-enumeration / semantic-hashing facts; C1-4 is elementary
functional dependence; C1-5 is an elementary closure invariant. The scientific residual is only the
frozen common-grammar experiment and its exact finite certificate.

## Claim ceiling

`NEUTRAL_THREE_LAW_REDISCOVERY_AT_REGISTERED_FINITE_GRAMMAR_SCOPE`.

No claim is made about cross-grammar robustness, real agents, unbounded program synthesis, causal
identification outside the frozen table, or universal learning-law discovery.
