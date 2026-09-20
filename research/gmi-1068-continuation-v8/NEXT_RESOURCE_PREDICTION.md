# Next resource prediction: exact distinction thresholds

Status: candidate theorem/protocol before its own implementation freeze.
V8 run semantics were inspected. No threshold implementation, exhaustive test,
kernel proof, empirical performance result or novelty claim exists yet.

## Model and proposed exact consequence

Let states/actions be finite. Each action has either no edge or one edge
(output,cost,successor), with natural-number cost. Every current/intermediate
observation and every successful EDGE(output,cost) is visible. An absent or
unaffordable edge returns ILLEGAL while preserving the preceding response.
Both compared runs start with the same budget.

Write s ~_B t for equality of responses to all finite words at initial budget B.
Let D(s,t) be the least distinguishing budget, or infinity if none exists.
The proposed prediction is s ~_B t iff B<D(s,t): larger budgets only refine
equivalence. Full edge-cost visibility is an essential premise.

## Product graph and proof argument

Use vertices (s,t) and a mismatch sink. Unequal current observations give a
sink edge of cost zero. For equal observations consider each action:

| Edges | Product contribution |
|---|---|
| Both absent | None |
| Exactly one present, cost c | Sink edge cost c |
| Different costs c,d | Sink edge cost min(c,d) |
| Same cost c, different output | Sink edge cost c |
| Same cost c and output | Edge cost c to successor pair |

Candidate theorem: D(s,t) equals shortest distance to the sink.
Until a first response mismatch, successful edges must have equal outputs and
costs, hence equal accumulated consumption. At the mismatch, the table gives
exactly the required residual budget. Conversely every product path to the
sink supplies a distinguishing word at its path cost. Higher budgets preserve
that mismatch: if both unequal-cost edges become affordable, their visible
costs still differ. These directions identify the minimum and prove nesting.

Nonnegative cycles can be removed from a shortest witness. Thus zero-cost
cycles do not require infinite words, and an unreachable sink means unbounded
full-response equivalence. Derive an explicit finite witness-cost bound from
the product-vertex count and maximum cost before fixing any test sweep range.

## Zero-cycle loophole

Bellman equations alone do not identify the intended solution:

- Zero self-loop and no mismatch yields d=d. Finite assignments satisfy this,
  although the correct distance is infinity.
- Zero self-loop and mismatch threshold 5 yields d=min(d,5). Every d<=5 solves
  this equation, although the correct threshold is 5.

Use reverse shortest paths initialized at infinity/local mismatch thresholds,
or prove the appropriate greatest-fixed-point characterization in numeric order.
Initialization at zero is invalid. Dijkstra permits zero edges, but arbitrary
equality-successor witness extraction can loop forever. Retain acyclic settled
predecessors or a proved hop-count/rank tie-break.

## Representation boundary

At fixed B, k(B), the number of ~_B classes, is the minimum number of codes
for all continuation responses from same-budget snapshots with B externally
known. Fixed-length binary storage needs ceil(log2 k(B)) bits. Class growth
need not produce a rounded bit-count increase.

This is not minimal total online memory across all residual budgets.
Matching affordable transitions lead to ~_(B-c), not generally ~_B.
Counterexample: all observations/outputs agree; s,t have cost-1 edges to u,v;
u has a cost-1 edge and v none. Then s ~_1 t but u is not ~_1 v.
Online updates need budget-indexed classes or lifted (state,budget) semantics.

Nested equivalences further imply D(s,u)>=min(D(s,t),D(t,u)), by transitivity
at every smaller budget. Each distinct positive threshold forces a strict
partition refinement, so there are at most |S|-k(0) such thresholds.
These are additional proof/checker targets, not empirical laws.

## Primary parents actually inspected

[Bisping, Process Equivalence Problems as Energy Games, CAV 2023](https://arxiv.org/pdf/2303.08904):
Theorem 1 (PDF p13), section 4.3 (PDF p17). Minimal attacker budgets characterize
behavioral distinctions. Its resources price logical observation power;
V8 consumes operational edge costs. Credit this strong general parent.

[Hansen et al., Reasoning About Bounds in Weighted Transition Systems, 2018](https://lmcs.episciences.org/4992/pdf):
Definitions 2.6/2.7 (PDF p5). Exact-weight bisimulation differs from coarser
bounds-preserving equivalence. Full cost visibility cannot silently be replaced
by interval matching.

[Lombardy and Sakarovitch, Morphisms and Minimisation of Weighted Automata](https://arxiv.org/pdf/2112.09387):
Theorems 3.12/3.13 and Remark 3.14 (PDF pp10-11). Coarsest congruences/minimal
quotients are not automatically globally smallest weighted realizations.

Treat the candidate as an adapted deterministic scalar-resource integration of
established methods. No absence of earlier identical work has been established.

## Separate freeze and decisive experiment

Freeze response semantics, shortest-path claim, witness format, zero-cycle
progress and same-budget memory scope before implementation.
Compare Dijkstra thresholds with independently constructed budget lifts and
independently swept complete continuation partitions for exhaustive small
machines with costs {0,1,2}; use a proved sweep bound.

Include zero/positive cycles, no mismatch, absent edges, unequal costs/outputs,
different current/successor observations and ties. Execute every finite witness
at D and at D-1 when D>0. Check relabeling, nesting, transitivity and bounds.
The cost-hidden control must break monotonicity: s->z costs 1, t->z costs 2,
with identical outputs/observations and terminal z. They differ at B=1 but
agree at B=2 when cost observations are removed.
Exact model consequences do not establish learned-model accuracy, calibrated
physical resources, useful cognition or general intelligence.
