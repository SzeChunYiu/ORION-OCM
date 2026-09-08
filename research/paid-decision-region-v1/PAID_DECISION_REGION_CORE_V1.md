# Paid Decision Region Determination — formal core for R0D

**Research status:** conventional Decision Region Determination + rational
metareasoning synthesis / source-derived OCM reduction / no novelty claim / no ML
authorization.

This note separates three questions that DEV-5, DEV-6 and X1 previously exposed
empirically but did not place in one formal decision problem:

```text
1. Has the current version space already determined a protected action?
2. What does it cost the machine to establish that fact?
3. Even if a common protected action exists, is more information economically
   worthwhile because it may reveal a cheaper protected action?
```

The mature parents are Decision Region Determination / Equivalence Class
Determination and value-of-computation metareasoning.  The contribution here is
the source-controlled reduction and exact-parent ordering for the OCM donor.

---

## 1. Version spaces and protected decision regions

Let `Theta` be a finite admitted hypothesis class and `V subseteq Theta` the
surviving version space.  For hypothesis `theta`, let

```text
G_theta(d)
```

be the protected actions acceptable in current contract/lifecycle context `d`.
Define

```text
Gamma(V,d) = intersection_{theta in V} G_theta(d).
```

### Theorem 1.1 — common-action safety sufficiency

Assume the true protected world `theta*` is in `V`.  If

```text
a in Gamma(V,d),
```

then `a` is protected-safe under `theta*`.

**Proof.**  `a` belongs to the safe-action set of every surviving hypothesis,
and `theta*` is one of those hypotheses. QED.

This is exactly why DEV-5's per-query unanimity rule can be sound before the
version space collapses to a singleton: singleton identification is sufficient
for a verdict but need not be necessary.

### Corollary 1.2 — singleton stopping is weakly more informative than necessary

If `|V|=1`, every action safe under its sole member is common.  The converse does
not hold: `Gamma(V,d)` can be nonempty for `|V|>1`.

Thus an identification objective and a protected-decision objective are distinct.
This is the standard Decision Region Determination viewpoint.

---

## 2. A unanimous external verification has zero in-class information value

For one query/index, let every hypothesis predict a deterministic verdict

```text
y_theta in Y.
```

Suppose all surviving hypotheses agree:

```text
y_theta = y*  for every theta in V.
```

If an external verification returns the in-class predicted outcome `y*`, the
posterior/version space is

```text
V' = {theta in V : y_theta = y*} = V.
```

### Theorem 2.1 — zero in-class version-space reduction

Under realizability and error-free deterministic verification, an external query
whose outcome is already unanimous over `V` does not shrink `V`.

**Proof.**  Every member of `V` predicts the observed outcome, so every member
survives conditioning. QED.

This proves a narrow but important statement:

```text
external verification has zero information value for distinguishing admitted
hypotheses at this query.
```

It does **not** say that computing unanimity is free, or that verification has no
out-of-class safety value under misspecification.  DEV-4's deficient-language
counterexample remains binding.

---

## 3. Computing a decision region is cognition and must be charged

Let the version space contain ordered survivors

```text
(theta_1,...,theta_n)
```

and let one unit of work evaluate one hypothesis's verdict at the queried index.
A sequential exact unanimity evaluator inspects the first verdict and continues
until either:

```text
(a) the first disagreement appears; or
(b) all n verdicts have been inspected.
```

### Theorem 3.1 — fixed-prefix short-circuit evaluation is pointwise minimal

For a fixed survivor order, the sequential evaluator above uses the minimum
number of verdict evaluations among correct evaluators that inspect a prefix of
that order.

### Proof

If the first disagreement occurs at position `k`, then after inspecting only the
first `k-1` positions the observed prefix is still unanimous.  There exist two
possible completions of the unseen suffix consistent with that prefix: one in
which all remaining verdicts agree and the final result is unanimous, and one in
which position `k` disagrees and the final result is mixed.  A correct evaluator
cannot distinguish those cases before inspecting position `k`.

If no disagreement exists, omitting any unseen survivor leaves open a completion
where that survivor disagrees, so all `n` verdicts are necessary to certify
unanimity. QED.

### Consequence for DEV-6

DEV-6's `UNANIMITY_NAIVE` charges `len(survivors)` for every consultation even
though its Python `all(...)` implementation stops at the first disagreement.
That tariff is a defensible conservative full-scan price, but it is not the
cheapest ordinary exact implementation of the same predicate.

Therefore the first R0D implementation parent is:

```text
UNANIMITY_FULLSCAN       donor accounting parent
UNANIMITY_SHORTCIRCUIT   same decisions/state, exact evaluations actually needed
```

before any cache, vote book, compiled table, feature gate or learned policy.

`shortcircuit_parent.py` enforces this as a one-fragment source transform of the
DEV-6 donor and `run_shortcircuit.py` requires every non-consultation Phase
coordinate to remain identical.

---

## 4. Safety sufficiency is not economic sufficiency

Let `r(theta,a)` be the cost of protected action `a` if `theta` is true.  Under a
worst-case objective, define current stop cost

```text
Stop(V)
  = min_{a in Gamma(V,d)} max_{theta in V} r(theta,a).
```

Let a cognitive probe `u` cost `c(u)>=0` and partition `V` into successor version
spaces `V_u^y`.

The exact finite recurrence is

```text
D(V)
 = min(
     Stop(V),
     min_u [ c(u) + max_y D(V_u^y) ]
   ).
```

### Theorem 4.1 — a common safe action does not imply optimal stopping

There exist states with `Gamma(V,d) != empty` for which the minimizing action in
`D(V)` is a probe.

**Constructive proof.**  Let two hypotheses both license a conservative action
`a_safe` costing 10.  Hypothesis 1 also licenses `a_1` costing 0; hypothesis 2
licenses `a_2` costing 0.  A probe costing 1 identifies which hypothesis is true.
Then

```text
Stop(V)=10
probe cost + worst successor stop cost = 1+0=1.
```

The optimal policy probes. QED.

### Corollary 4.2 — cognition can become uneconomic without changing safety

In the same example, raise probe cost to 20.  The safe-action structure is
unchanged but the optimal policy stops at cost 10.

Thus R0D must report both:

```text
decision sufficiency: can we act safely without more identification?
economic sufficiency: is the cheapest remaining cognition worth buying?
```

DEV-5 primarily exposes the first; DEV-6 and X1 expose the second.

---

## 5. Exact finite Bellman parent

`decision_region_core.py` implements the finite worst-case recurrence for:

```text
hypotheses
safe-action sets
action costs
legal deterministic probes
probe outcomes
probe costs.
```

It can also impose `identification_only=True`, producing the exact full-
hypothesis-identification parent on the same problem.

This yields a clean parent ladder:

```text
P0  full identification only
P1  singleton stopping
P2  common-action / decision-region stopping
P3  common-action stopping with exact short-circuit predicate cost
P4  exact paid-probe Bellman/DRD policy
P5  simple observable feature gate approximating P4, with regret-floor audit
P6  ordinary statistical algorithm selection if a payable residual remains
P7  tiny learned model only after P6 fails and complete lifecycle cost is charged
```

A Bellman optimum is a normative lower bound until policy computation/lookup,
table storage, updates, drift handling, checkpoint/replay and failure handling are
also charged.

---

## 6. Source custody: what DEV-5, DEV-6 and X1 actually establish

### DEV-5 — one-line decision-rule ablation

The donor holds the same version-space language, streams, budgets and serve loop.
`SINGLETON_FULL` acts only when one predicate survives; `UNANIMITY_FULL` acts
whenever all survivors agree at the queried index.

With a language containing the true predicate, both are sound.  A deliberately
deficient language control shows that unanimity does not repair misspecification.

DEV-5's original flat consultation-price result established that the stronger
singleton rule was needlessly conservative, but its headline magnitude depended
on the consultation tariff.

### DEV-6 — honest deliberation pricing audit

DEV-6 keeps the same decision rules and re-prices computation:

```text
singleton consultation       1
naive unanimity               len(survivors)
incremental vote book         O(1) query + charged seed/elimination maintenance.
```

The naive unanimity arm still beats singleton throughout the frozen sweep, but
the ratio range is corrected from roughly

```text
0.197...–0.890...
```

to

```text
0.292...–0.970....
```

The proposed incremental vote book loses badly because maintenance is fully
charged.  This is direct evidence that "make the predicate cheaper" is not enough
unless the data structure repays its lifecycle cost.

### X1 — cross-domain sign reversal

A separate existing enumerator already used the same logical contract under a
different name: skip an intervention when the current evidence already determines
its answer.  At matched exact capability the determined-rule arm reduces
interventions from 529 to 198, yet total work rises from 4936 to 8039 because the
reasoning is more expensive than the interventions it removes.

Therefore the transferable object is not "unanimity wins."  It is:

```text
perform internal decision-region reasoning iff its complete cost is below the
external/counterfactual work it avoids.
```

That is exactly a value-of-computation statement.

---

## 7. Misspecification remains an authority boundary

All safety theorems above are relative to the admitted model class.  If the true
world is outside that class, an internally unanimous version space can be
unanimously wrong.

Therefore:

```text
unanimity / common action  => in-class decision sufficiency
not                       => class adequacy or protected authority.
```

A deployable protected action still requires either a coverage/adequacy argument
for the hypothesis language or an independent fail-closed checker/authority
boundary.

The R0D learned-router lane must never use posterior concentration, singleton
collapse or unanimity as independent authorization under misspecification.

---

## 8. What the first empirical tranche can and cannot prove

The short-circuit DEV-6 rerun tests one exact implementation question:

```text
How much of DEV-6's full-scan deliberation tariff is avoidable by the ordinary
fixed-order short-circuit evaluator, with zero extra state?
```

A strict win over full-scan is expected whenever mixed version spaces often expose
an early disagreement.  Because decisions and version-space updates are identical,
this is an implementation-cost parent, not a stronger information source.

It does not yet establish the globally cheapest way to evaluate unanimity.
Candidate ordering can change expected short-circuit depth; caching can trade
build/storage/maintenance for queries; a feature gate can sometimes choose not to
consult.  Each is a later parent and must pay for the information/state it uses.

---

## 9. Next exact research order after the short-circuit tranche

If the short-circuit parent materially changes the economic conclusion, the next
research steps are:

```text
1. measure the distribution of actual short-circuit depths by version-space state;
2. audit zero-cost legal state already present before each consultation;
3. test exact/simple candidate orders using only that state;
4. calculate feature collisions and exact regret floors for any cheap consult/skip gate;
5. instantiate paid DRD/Bellman on a finite source-derived donor slice;
6. charge the metapolicy itself;
7. only then ask whether residual ordinary algorithm selection exists.
```

No learned model is authorized by the existence of mixed consultation costs alone.

---

## 10. Current R0D terminals

The formal core supports several possible honest terminals:

```text
DECISION_REGION_STOPPING_DOMINATES_IDENTIFICATION
  identification is unnecessary for protected action.

COGNITION_NOT_ECONOMIC
  a finer decision is possible but determining it costs more than acting/probing.

EXACT_PREDICATE_PARENT_SUFFICIENT
  short-circuit/simple exact evaluation absorbs the practical residual.

OBSERVATION_CHANNEL_INSUFFICIENT
  legal cheap features alias states requiring disjoint consultation/action choices.

MISSPECIFIED_CLASS_AUTHORITY_LIMIT
  no in-class stopping rule can establish the protected claim.

RESIDUAL_PAID_DRD_ALGORITHM_SELECTION
  only if multiple exact strategies retain a payable, legally observable residual.
```

The first empirical tranche should not skip directly to the last terminal.
