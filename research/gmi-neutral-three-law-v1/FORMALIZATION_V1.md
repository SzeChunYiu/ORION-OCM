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

## C1-1 — bounded dynamic-programming completeness [P1]

**Theorem.** For every integer `c∈{1,...,6}` and every expression `e` of exact cost `c`, the DP layer
constructed through cost `c` contains semantic table `T(e)`.

**Proof.** Structural induction on `e`.

Base `c=1`: `e` is one of the seven registered leaves. The initialization inserts all leaf tables.

Inductive step: suppose the claim holds for all expressions of cost `<c`.

- If `e=half(a)`, then `cost(a)=c-1`. By induction, `T(a)` is present in layer `c-1`; the unary
  construction inserts the pointwise table `T(e)=T(a)/2` into candidate layer `c`.
- If `e=op(a,b)` for `op∈{add,sub,mul}`, then
  `cost(a)+cost(b)+1=c`, so both child costs are `<c`. By induction both child semantic tables are
  present in their exact-cost layers; the binary construction visits that ordered pair and inserts the
  pointwise `op(T(a),T(b))=T(e)` table.

Deduplication can remove only a duplicate table, never the table value itself. Hence every bounded
expression semantics is present. ∎

**Consequence.** If a target table first appears in DP layer `c`, no expression of cost `<c` realizes it.
Thus the first-hit layer is a global minimum cost in `G_<=6`, not a search-order artifact.

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

Let frozen target tables be `A,B,C` from `FREEZE_V1.md`. The executable certificate enumerates the full
bounded quotient and reports the first layer containing each table. By C1-1, those layers are global
bounded minima. The preregistered expected minima are

```text
cost(A)=4,
cost(B)=6,
cost(C)=6.
```

A positive P2 result requires exact equality on all 81 points, one unchanged grammar/pricing protocol,
and no target-ID branch in the search routine.

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

The grammar, operator costs, cap, universe order, and tie rule are frozen before implementation. A scored
run is confirmatory only under that exact protocol fingerprint. Any attempted mutation after activation
must terminate as

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
