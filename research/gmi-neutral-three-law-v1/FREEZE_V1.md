# #768 freeze — neutral rediscovery of three learning laws from one low-level grammar V1

Date: 2026-09-15. Parent ledger: #602 Section C. Child issue: #768.

This is the pre-implementation scientific authority. No target-table artifact, search executor, scored result, test, or dedicated workflow for this lane exists on this branch before this commit.

## Claim boundary

Target only:

```text
NEUTRAL_THREE_LAW_REDISCOVERY_AT_REGISTERED_FINITE_GRAMMAR_SCOPE
```

This lane may establish bounded exact neutral rediscovery of three qualitatively distinct update-law semantics from one shared low-level grammar on one finite exact domain. It may not claim universal law discovery, causal identification outside the registered truth tables, cross-grammar replication, real-agent evidence, external task-distribution validity, or complete GMI.

## Strongest parents

The mathematics is parent-owned by finite program synthesis / enumerative search, dynamic programming, extensional equivalence of functions on finite domains, and elementary dependency/counterfactual arguments. The repository residual is only the freeze-first one-grammar protocol, explicit family-blind scoring, exhaustive semantic quotient, minimal-cost certificate and hostile evidence discipline.

## Frozen universe

Inputs are exact integers

```text
(w,x,y,r) in {-1,0,1}^4
```

ordered lexicographically with axis order `(w,x,y,r)` and value order `(-1,0,1)`, exactly as Python `itertools.product((-1,0,1), repeat=4)`.

There are exactly 81 rows. Canonical universe JSON is a compact `json.dumps(..., sort_keys=True, separators=(',',':'))` of rows `{w,x,y,r}` in that order. Frozen SHA-256:

```text
e8aec22f36a3558cb3f9356e57b4e13575d7905862cfac9fe1240618850ce523
```

All semantic evaluation uses exact `fractions.Fraction`; floats are forbidden.

## Frozen shared grammar and cost

One grammar is used unchanged for all targets:

```text
Expr ::= -1 | 0 | 1 | w | x | y | r
       | half(Expr)
       | (Expr + Expr)
       | (Expr - Expr)
       | (Expr * Expr)
```

No named learning rule, gradient, Bayesian update, reward update, prediction-error macro, target identifier, target-specific constant, conditional, lookup table, or task-specific operator is legal.

Frozen additive tree cost:

```text
cost(-1)=cost(0)=cost(1)=cost(w)=cost(x)=cost(y)=cost(r)=1
cost(half(a)) = 1 + cost(a)
cost(a op b)  = 1 + cost(a) + cost(b), op in {+,-,*}
```

Frozen exhaustive cap:

```text
C = 6
```

No grammar/cost/cap mutation is permitted after target tables are materialized.

## Frozen semantic quotient/search protocol

For an expression `e`, define its semantic table

```text
T(e) = ( e(u_1), ..., e(u_81) ) in Q^81
```

on the frozen universe.

Two expressions are equivalent iff their complete exact tables are equal. The dynamic programme processes exact total cost `c=1,...,6` and stores at most one canonical representative per semantic table. A table already present at lower cost is never replaced by a higher-cost expression. Within the same cost, ties choose the lexicographically smallest fully parenthesized representation.

At cost 1, enumerate the seven terminals. At cost `c>1`:

- apply `half` to every table first appearing at `c-1`;
- for every ordered split `a+b+1=c`, combine every table first appearing at cost `a` with every table first appearing at cost `b` under `+`, `-`, `*`;
- evaluate extensionally using exact rationals;
- quotient by complete table equality and then by already-seen lower-cost tables.

The target scorer receives only opaque target IDs plus 81-output exact tables. It reports an exact match only by table equality; it must not branch on target ID or use the formulas below.

## Frozen opaque targets / independent oracle authority

The three scientific target laws are frozen here only to define an independent oracle. The search/scorer itself must consume only their materialized opaque tables.

```text
opaque_1: w' = (w+y)/2
opaque_2: w' = w + (x*y)/2
opaque_3: w' = w + (r*x)/2
```

Canonical target artifact object is `{opaque_id, outputs}` with each rational output serialized as an integer string or `p/q`, compact sorted-key JSON. Frozen object SHA-256 values:

```text
opaque_1  7d575d7033a2eef62b6fe818be4dd15092f86617a9eb902366e871beaa6577d9
opaque_2  93d925ea0d70134e43ad0add4b1b5a49730eb3f74dacba2345f4caf3ac956db3
opaque_3  65b57eef0aa754f875d9f7bd656504a2a1f2cf543562948faf1af9de3143b315
```

These hashes are frozen before target-table materialization and implementation.

## Frozen theorem C1-1 — bounded search completeness [P1]

For every legal grammar expression `e` with `cost(e)<=6`, the dynamic-programming semantic quotient contains table `T(e)` at some recorded cost no greater than `cost(e)`.

Proof target: structural induction on expression/cost. Terminals occur at cost 1. For `half(a)`, the inductive table for `a` occurs no later than its true cost, so a semantically identical half-table is generated no later than the declared cost. The binary case follows from the exhaustive ordered cost split and operator enumeration. Quotienting can remove only a duplicate table already present at equal or lower cost, so semantic reachability is preserved.

## Frozen theorem C1-2 — quotient soundness [P1]

For this registered finite universe, two expressions are identified by the quotient iff their exact output vectors agree on all 81 rows. Therefore quotienting changes representation only; it never merges two functions that differ on the registered domain.

## Frozen theorem C1-3 — neutral minimum-cost recovery [P1/P2]

For each opaque target table, search all quotient tables through cost 6. If an exact match exists, report the first cost at which its table occurs and the canonical expression at that cost. Because C1-1 enumerates every legal expression through the cap and lower costs are processed first, that cost is globally minimal within the frozen grammar/cap.

Frozen expected target costs, derived before implementation:

```text
opaque_1 -> 4
opaque_2 -> 6
opaque_3 -> 6
```

The implementation must fail if any target is absent or appears at a lower/different cost than frozen.

## Frozen theorem C1-4 — variable-dependency necessity [P1]

If two registered rows differ only in input variable `z` and the target outputs differ, any exact deterministic realization on the registered domain must semantically depend on `z`. Otherwise equal non-z coordinates would force equal outputs, contradiction.

The implementation will exhibit a concrete one-coordinate pair for every required variable and exhaustively verify invariance for every non-required variable.

Frozen irreducible signatures:

```text
opaque_1: {w,y}
opaque_2: {w,x,y}
opaque_3: {w,x,r}
```

## Frozen theorem C1-5 — qualitative distinctness [P1]

The three target semantics are pairwise distinct because their complete exact tables differ. More strongly, their irreducible dependency signatures above are pairwise different. Thus they are not one semantic update law under three syntactic encodings at this registered scope.

This is a finite semantic distinction only; it does not claim a universal taxonomy of learning paradigms.

## Frozen hostile controls

1. **Required-variable removal.** For each target and each variable in its frozen dependency signature, remove that terminal from the otherwise unchanged grammar. The target must be unreachable through cost 6. The C1-4 witness already proves no exact deterministic expression lacking that variable can match at any cost.
2. **Remove `half`.** With terminals restricted to integers and operators `+,-,*`, every output remains integer-valued. Each target has at least one half-integer output, so all three become globally impossible, not merely absent under cap 6.
3. **Perturbed-table hostile.** Change only the first output of `opaque_1` by `+1/4`, leaving all other 80 rows fixed. This altered table is frozen as a negative search target and must have no exact match through cost 6.
4. **Equivalent syntax.** `half(w)+half(y)` must have the same table as `half(w+y)` but a higher tree cost (5 versus 4). The quotient must retain the lower-cost semantic representative.
5. **Post-activation mutation.** Grammar, costs, cap, universe, target tables and scoring rule become immutable once target artifacts are activated; mutation attempts fail closed.
6. **Opaque-ID permutation.** Renaming/permuting opaque IDs without changing target tables may permute report rows only; recovered semantic tables/costs must be unchanged.

## Frozen receipt requirements

The deterministic receipt must report:

- freeze commit;
- universe and target hashes;
- exact grammar/cost/cap;
- number of new semantic tables at each cost 1..6 and total quotient size;
- recovered minimum cost, canonical expression, exact table digest and dependency signature for each opaque target;
- explicit dependency witnesses;
- required-variable ablation results;
- `half` impossibility control;
- perturbed-table result;
- equivalent-syntax quotient control;
- opaque-ID permutation invariance;
- proof/evidence classes and claim ceiling.

Normal Python and `python -O` must emit byte-identical receipts.

## Falsifiers

This lane is falsified at its stated scope if the frozen target hashes do not reproduce; the quotient misses a generated expression table; any two unequal tables are merged; a target is absent within cost 6 or appears below the frozen minimum; a required-variable ablation still exactly matches; a non-required variable is actually necessary; removal of `half` still reaches a half-integer target; the perturbed table is recovered within cost 6; equivalent syntax changes semantics; target-ID permutation changes semantic/cost outcomes; optimized mode changes results; or any claim exceeds the registered finite grammar scope.
