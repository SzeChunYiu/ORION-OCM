# Developmental geometry as stochastic-shortest-path / metareasoning parent v1

Status: **parent subtraction.** The purpose is to prevent `developmental geometry` from being renamed as a new formalism when finite cases are already covered by mature control/decision theory.

Refs #377, #233, #373.

## 1. Current candidate geometry

Track B currently uses a provisional object such as

\[
\mathcal G_M=(\mathcal H_M,\pi_M,K_M,c_M,V_M),
\]

where `H` is the morphology's internal configuration/hypothesis space, `pi` its proposal bias, `K` its experience-conditioned transition/proposal kernel, `c` resource cost, and `V` its verification/evidence interface.

This is a useful cross-paradigm measurement object.

It is **not automatically novel mathematics**.

## 2. Finite reduction to stochastic shortest path

Fix a finite registered developmental scope.

Let:

```text
state         = current internal/configuration state h in H
action        = a legal computation/update/proposal choice a
transition    = P(h' | h,a,e)
cost          = registered resource cost c(h,a,h',e)
goal set      = configurations satisfying the frozen verified capability condition
```

Then minimizing expected resource cost to first reach a verified target configuration is a stochastic shortest-path / undiscounted MDP problem, subject to the usual assumptions needed by that theory.

Bertsekas & Tsitsiklis (1991) give a mature stochastic-shortest-path framework for minimum expected cost to a destination. Therefore:

```text
DEVELOPMENTAL_GEOMETRY_AS_FINITE_COSTED_STATE_TRANSITION_SYSTEM
```

is parent-owned.

## 3. Computation selection is also parent-owned

Russell & Wefald's rational metareasoning treats computations as actions whose value derives from their effect on eventual external decisions, explicitly accounting for computational cost and uncertainty.

Hence:

```text
choose which cognitive computation/update to perform based on expected downstream value - cost
```

is not an OCM/Track-B novelty.

This is directly relevant to OCM's executive/metareasoning layer and to morphology phase comparisons.

## 4. What remains useful in `developmental geometry`

The cross-paradigm value of the object is **structural compression and prediction**, not the existence of a costed state graph.

Track B must ask:

1. Can `H`, `K`, proposal bias and costs be represented compactly from morphology structure rather than enumerated?
2. Can measurable invariants of that compact structure predict acquisition/update burden?
3. Can experience change the compact geometry in ways that transfer to fresh tasks/ecologies?
4. Can the same invariants compare neural, symbolic, probabilistic and programmatic systems?
5. Can they prospectively predict a morphology frontier before running architecture search?

If not, a generic SSP/metalevel MDP is already sufficient as the formal parent.

## 5. Strong null

If all Track-B phase results can be restated as:

```text
solve the fully specified metalevel MDP / stochastic shortest-path problem
```

with no new structural prediction, compression or learned generalization across morphologies/ecologies, return:

```text
STOCHASTIC_SHORTEST_PATH_PARENT_SUFFICIENT
```

## 6. Stronger residual

The live residual is therefore:

> infer useful developmental geometry from compact architecture/experience, transfer that inference across tasks, and prospectively predict which morphology factorization will be Pareto-admissible without enumerating the complete metalevel state graph.

This is substantially harder than defining a state graph with costs.

## 7. Connection to HST / OCM

HST's proposal/search state `Q_t` and Track-B's `pi/K` should be treated as compatible views, while avoiding duplicate theory.

#323's history-induced search-prior result can be interpreted as a measured change in proposal geometry. That does not establish a new stochastic-control formalism; it supplies an empirical phenomenon that a general theory must explain and predict.

## 8. Parent anchors

- D. Bertsekas & J. Tsitsiklis, *An Analysis of Stochastic Shortest Path Problems*, Mathematics of Operations Research 16(3), 1991.
- S. Russell & E. Wefald, *Principles of Metareasoning*, Artificial Intelligence 49, 1991.

These parents should receive first refusal for any future formal claim that merely treats internal computation as costed sequential decision making.