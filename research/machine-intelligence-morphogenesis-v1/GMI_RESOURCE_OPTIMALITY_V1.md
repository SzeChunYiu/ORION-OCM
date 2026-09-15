# Section C box 11 — when is a learning law *resource*-optimal?

Box 12 compared the six learning laws on capability alone. It found that every
law loses somewhere, that three are never *uniquely* best, and that two of those
three were explained by strict member containment. The third, `state-only`, was
not explained, and was committed to the record as an open anomaly rather than
folded in.

Box 11 charges cost. It does two things: it answers the box as asked — the
assumptions under which each law is resource-optimal — and it closes box 12's
anomaly, for a reason that turns out to have nothing to do with cost.

## Protocol

Two-phase. `gmi_microscope/predict_resource_optimality.py` was committed first
(`08cfe261`) with the cost model, the tie-break rule and eight falsifiable
predictions, and **no measuring code**. `compare_resource_optimality.py` landed
afterwards. Git commit order is the evidence.

The cost model has free choices that a pure capability comparison does not, and
they are fixed in advance:

| coordinate | definition | kind |
|---|---|---|
| `spec(P)` | `ceil(log2 |P|)` — bits to say which member you mean | task-independent |
| `mem(P,t)` | distinct states reachable from START, minimised over the members achieving P's best score on `t` | task-dependent |

**Tie-break: argmax-score then min-cost.** `score` is a max over members, cost is
not, so "the cost of `P` on `t`" is undefined until a member is named. Taking the
cheapest member *overall* would let a paradigm buy cheapness by surrendering
capability it is not being charged for; thresholding would add a second free
parameter. Rule-table size was deliberately not used as a third coordinate: every
update object is an 8-tuple, so it is the constant 8 everywhere.

Objective `value(P,t,w) = score(P,t) − w·cost(P,t)` with `w` an exact
`Fraction`. Scores and costs are integers, so the argmax changes at finitely many
rational breakpoints — all 13 are enumerated exactly. No floating point appears
in any reported number.

## The anomaly is closed, and not by cost

| law | member-contained in | behaviour-contained in |
|---|---|---|
| `overwrite` | idempotent-on-repeat, keep-or-replace | idempotent-on-repeat, keep-or-replace |
| `keep-or-replace` | idempotent-on-repeat | idempotent-on-repeat |
| **`state-only`** | **— (nothing)** | **overwrite, insertion-monotone, idempotent-on-repeat, keep-or-replace** |

`state-only` ignores evidence, so its behaviours are exactly the four constant
tuples. `overwrite` depends only on the last symbol, so its behaviours are the
sixteen tuples of the form `(a,b,a,b)` — which *include* every constant tuple.
So `state-only`'s behaviour set is contained in `overwrite`'s, while its member
set is not: a `state-only` map with a non-constant state function is not an
`overwrite` map.

Scoring is defined on behaviours, not on members. So the right theorem is:

> **If `beh(A) ⊆ beh(B)` then `A` is never uniquely best.**
> `score(P,t)` is a max over `beh(P)`, so `beh(A) ⊆ beh(B)` gives
> `score(A,t) ≤ score(B,t)` for every `t`; `A` can never strictly exceed `B`.

Member containment implies behaviour containment, so **box 12's theorem is a
corollary of this one**, stated with an unnecessarily strong hypothesis.
`state-only` is the unique witness in this ecology that the converse fails. Box
12 did not have a wrong computation; it had a hypothesis that was too strong to
cover its own data, and reported the residue honestly instead of hiding it.

## What each coordinate says

Unique-argmax cells (the strong notion — sole optimum at some `(task, w)`):

| law | spec | mem |
|---|---|---|
| `overwrite` | 2296 | 28 |
| `additive` | 1216 | 376 |
| `insertion-monotone` | 693 | 360 |
| `idempotent-on-repeat` | 76 | 376 |
| `keep-or-replace` | 63 | **0** |
| `state-only` | **0** | 236 |

**Each coordinate kills a different law.** `state-only` is optimal for no task
under specification cost and on the Pareto frontier for 0 of 256 tasks — yet it
is the sole optimum on 236 `(task, w)` cells under memory cost. `keep-or-replace`
is the mirror image: 63 cells under spec, zero under mem.

The two coordinates disagree on **256 of 256 tasks** — every single one. There is
no task where a single "cost" number would be safe. Resource-optimality here is
not a property of a law; it is a property of a law *and a stated coordinate*.

This is the answer to the box. `state-only` — the law capability alone cannot
justify — is resource-optimal exactly under memory-dominated assumptions and
never under specification-dominated ones.

## Adjudication

| prediction | outcome |
|---|---|
| P1 `state-only` never on the spec frontier | HOLDS (0/256) |
| P2 behaviour containment is the right hypothesis | HOLDS |
| P2 `state-only` behaviour-contained in `overwrite` | HOLDS |
| P2 `state-only` member-contained in `overwrite` | HOLDS (predicted false, is false) |
| P3 `w=0` reproduces box 12's win counts | HOLDS — exactly |
| P4 unique optimum vanishes at high `w` | **FALSIFIED** |
| P5 every law but `state-only` uniquely optimal somewhere | HOLDS |
| P6 the two coordinates disagree on some task | HOLDS (all 256) |

P3 is an exact cross-box check: at `w=0` the objective *is* the score, so box 11
must reproduce box 12's capability comparison. Both give
`additive 14, insertion-monotone 18, idempotent-on-repeat 20`, and zero for the
other three. The two boxes agree to the task.

### P4 was falsified, and the reasoning error is worth recording

I predicted that uniqueness would vanish as `w` grew, because `additive` and
`overwrite` both cost `ceil(log2 16) = 4` bits and would therefore tie once cost
dominated. That is wrong, and wrong in an instructive way: **equal costs cancel
in the objective.** If `cost(A) = cost(B)` then
`value(A) − value(B) = score(A) − score(B)` at *every* `w`, so a cost tie does
not produce an objective tie — it hands the comparison back to capability.

The correct statement is that as `w → ∞` the argmax becomes lexicographic:
minimise cost first, then maximise score *within the cheapest tier*. Uniqueness
at high `w` is therefore governed by capability differences inside that tier, and
is more common, not less: 142 tasks have a unique optimum at `w = 4` against 52
at `w = 0`.

## Non-vacuity

All four controls pass: `spec` varies across the laws; some task has ≥2
Pareto-optimal laws and some has exactly 1; the frontier is neither all six laws
everywhere nor one law everywhere; and `mem` genuinely varies. Without these, a
"resource-optimal" claim can be true and empty.

## Scope

Exhaustive over this ecology: 4 states, 2 evidence symbols, length-2 sequences,
65536 update objects, 256 tasks, 13 exact rational breakpoints. Every number is
enumerated, not sampled. The claims are about this ecology; nothing here asserts
that the same frontier structure holds at larger `S`, `E` or `L`.

Receipt: `microscopes/results/STAGE_RESOURCE_OPTIMALITY_V1.json`.
