# Multi-objective coverage state — objective specification before routing

**Status:** conventional multi-objective decision-theory reduction / exact R0B
specialization / no ML authorization.

The price-conflict lower bound reveals that `objective` is part of the decision
context, not a nuisance variable that a router should silently infer.  The mature
parent is multi-objective sequential decision making: when preferences are not
fixed, retain a coverage set/Pareto set; when a linear scalarization is known,
select the member minimizing that scalar objective.

No novelty is claimed for coverage-set theory.

## 1. Decision context must include the objective

The earlier metalevel state

```text
sigma = (V, s, d)
```

is sufficient only when the resource objective is fixed outside the state.  More
explicitly write

```text
sigma = (V, s, d, o)
```

where `o` contains either:

```text
(a) a prospectively registered scalar objective, e.g. w>=0;
(b) a declared constrained objective;
(c) a Pareto/coverage-set request; or
(d) a robust preference family W.
```

If two objectives induce disjoint optimal strategy sets and the policy is not
given which objective applies, the ordinary feature-collision theorem applies:
no increase in model capacity can make one objective-blind action optimal for
both.

## 2. Known-horizon raw vectors

For horizon `H`, let

```text
c_tau(H) in R_+^3
```

be the raw primary-resource vector of the deterministic one-way threshold policy
`tau`, with

```text
tau=0  = semantic from the first demand
tau=H  = inverse for the whole episode.
```

`known_horizon_pareto_verify.py` exhaustively enumerates every `tau=0..H` from the
source-derived lifetime curves and removes componentwise dominated vectors.

The verified deterministic Pareto pattern is:

```text
H <= 3    : { inverse }
H = 4..8  : { inverse, semantic }
H >= 9    : { semantic }
```

No intermediate threshold is Pareto-efficient at any `H=1..142`.

## 3. Linear scalarization needs only a convex coverage set

Fix a nonnegative linear objective

```text
U_w(c) = w.c,  w>=0.
```

### Proposition 3.1 — randomization cannot improve a known linear objective

Let a randomized policy choose deterministic policies `a` with probabilities
`p_a`.  Its expected scalar cost is

```text
E[U_w(c_a)] = sum_a p_a U_w(c_a).
```

This convex combination is at least

```text
min_a U_w(c_a).
```

Therefore, when `w` is known before action, some deterministic member of the
coverage set is optimal. QED.

Randomization can still matter for a **robust minimax objective over unknown w**;
that is a different problem, as Phase 2B2 and `PRICE_OBJECTIVE_CONFLICT_V1.md`
show.

## 4. Exact R0B convex coverage set

For the current deterministic known-horizon family, define `CCS(H)` as the
minimal subset sufficient to attain the minimum for every nonnegative linear
weight vector.

Because a componentwise dominated point can never be uniquely optimal under a
strictly positive weight vector, and because the two static vectors in the
price-sensitive band are each optimal under at least one basis-price objective,
the source-derived set is exactly

```text
CCS(H) =
  {inverse}             H<=3
  {inverse, semantic}   H=4..8
  {semantic}            H>=9.
```

`objective_coverage_verify.py` verifies both facts from `regime.json`:

1. every intermediate threshold is dominated;
2. in H=4..8, at least one registered basis resource prefers inverse and at least
   one prefers semantic, so neither static arm can be deleted from the coverage
   set.

### Corollary 4.1 — exact objective advice is trivial once the objective is declared

At known `H`, a registered linear objective requires only evaluating

```text
w.I(H)  versus  w.S(H)
```

on the two coverage-set members.  No learned strategy selector is needed.

The apparent "routing population" at H=4..8 is therefore a **preference tradeoff
population**, not evidence of hidden per-target strategy structure.

## 5. Unknown preference timing gives three distinct problems

Multi-objective literature distinguishes when preference information becomes
available.  R0B should do the same.

### Objective known at design/runtime decision time

Freeze `w`, then optimize the scalar expected/robust lifetime problem and report
all raw resources.  This is the normal parent for a deployable controller.

### Objective unknown while planning, known before final choice

Maintain the small coverage set and choose its member once `w` is supplied.  For
known horizon R0B, the set has size at most two.

### Objective never supplied

There is no unique scalar optimum.  Return Pareto/coverage information or solve
a prospectively declared robust preference problem such as

```text
min_pi sup_{w in W} regret_w(pi).
```

The joint randomized threshold certificate is one such robust parent for
`W={w>=0,w!=0}` modulo positive scale.

These scenarios must not be conflated.

## 6. Objective uncertainty versus world uncertainty

The correct decomposition is

```text
world uncertainty:
  H, future targets, invalidation events, observations

objective uncertainty/specification:
  w, constraints, risk criterion, Pareto/robust request
```

A lawful prediction channel may reduce world uncertainty.  It should not be
credited for guessing an objective that the experiment failed to state.

This distinction also sharpens the paid-information gate:

```text
VOI(Z | objective=o)
```

must be measured under a prospectively registered `o`.  Otherwise a single
"value of horizon information" is not well-defined in the price-sensitive band.

## 7. Literature parent

The direct parent is the multi-objective sequential decision-making literature,
in particular the taxonomy and coverage-set treatment surveyed by Roijers,
Vamplew, Whiteson and Dazeley (JAIR 2013).  Their key distinction is that,
depending on scalarization and when preference information is available, the
appropriate solution object can be a single policy, a convex coverage set, or a
Pareto front.

R0B does not need a new multi-objective learning mechanism at this stage.  Its
known-horizon coverage set is already exactly enumerable and tiny.

## 8. Gate consequence

Before any learned lifetime/router experiment, register:

```text
objective family and timing
lifetime/advice source and timing
protected fallback
complete cognition + lifecycle costs.
```

Current no-ML terminal on the objective side:

```text
EXACT_COVERAGE_SET_SUFFICIENT_FOR_KNOWN_H_OBJECTIVE_SELECTION_R0B
```

The remaining scientific uncertainty is the unknown-lifetime control problem
under a declared objective, not a need to learn which deterministic Pareto point
exists.
