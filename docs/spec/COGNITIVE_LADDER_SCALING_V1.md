# COGNITIVE_LADDER_SCALING_V1 — scale, cognitive productivity and the lifetime frontier

Status: **PROTOCOL. NO RESULT, NO SCALING CLAIM, NO PRODUCTIVITY CLAIM.**
Programme: issue #143. Companion to `COGNITIVE_LADDER_PROTOCOL_V1.md`, which owns identification,
admissibility, custody and pre-registration. This document owns **scale**.
Inherited measurement discipline: `research/machine-epistemics-lifetime-v1/lifetime_metrics.py`
(coordinate names, the `k`-is-instrumented rule, and `CANNOT_CHECK` as a first-class outcome).

The hypothesis under test, stated so it can fail:

> As a persistent machine accumulates verified reusable competence, the marginal information, active
> state, search, verification and revision required for future cognition grow substantially more
> slowly than total accumulated competence, while task quality remains comparable to the strongest
> matched parent.

This is a **falsifiable programme-level hypothesis, not an assumption**. Several of the terminals in
§8 assert its negation, and those terminals are publication results.

---

## 1. Scale variables

Scale is never an object count and never a parameter count. Every scaling statement is made over the
declared vector:

```text
N              total persistent logical competence objects
B_N            total persistent bytes
k              task-active / touched logical objects
B_k            active bytes per query
D              registered task complexity
Q              verified task-quality vector
C_acquire      cost of acquiring new competence
C_query        query / reasoning cost
C_verify       checker / verifier cost
C_revision     revision / relearning cost
C_maintenance  indexing / consolidation / maintenance cost
C_lifetime     the complete cumulative resource vector
```

**CL-S-T1 (`k` is instrumented, never inferred).** `k` counts persistent objects a path *actually
touched*. It is never read off the size of a returned result set, a non-zero activation count, or a
sparse edge count. If a path can perform an uninstrumented global scan, that path reports
`CANNOT_CHECK` and not a favourable number. This rule is inherited verbatim from the lifetime metrics
module and is the load-bearing discipline of the whole document.

---

## 2. The registered persistent-state growth study

One long-lived machine, **no reset**, through prospectively frozen competence scales:

```text
1x   3x   10x   30x   100x where feasible
```

At every scale, the same frozen probe families are re-run. The scale axis is grown by adding
competence, never by changing the probes.

At each scale record:

- [ ] `N` and `B_N`;
- [ ] `k`, `B_k` and `k/N` on the frozen probes;
- [ ] all hidden index / router work, separated into **build** and **maintenance**;
- [ ] `C_query`, search expansions and checker calls;
- [ ] marginal `C_acquire` for a newly taught **structurally related** task;
- [ ] marginal `C_acquire` for a newly taught **unrelated** task;
- [ ] repair cone and cost after revoking one **local** support;
- [ ] repair cone and cost after revoking one **globally shared** support (hostile);
- [ ] retention / forgetting on earlier probe families;
- [ ] negative-transfer rate;
- [ ] restart custody preserved between stages (protocol §3).

**The unrelated-task arm is not optional.** A machine that shows falling acquisition cost on
*everything* is showing an order effect, not transfer. The unrelated arm is the control that makes
the related arm mean something, and a programme that reports only the related curve has not measured
transfer at all.

---

## 3. Scaling relations and how they may be fitted

Prospectively registered relations:

```text
k(N)                                query_work(N)
revision_work(N)                    persistent_bytes(N)
acquisition_cost(experience)        failure_recurrence(experience)
transfer_benefit(experience)        max_solvable_complexity(resource)
```

**CL-S-T2 (no assumed power law).** Fit at least four candidate models to every registered
relation — constant, logarithmic, linear, and power law — select among them by a declared
information criterion, and report the selected model **with its uncertainty and its residual**. A
power-law exponent may be reported only when the power law is the selected model and its residual is
stated. Where no model fits acceptably, the relation is reported as unmodelled with the raw points
shown.

**The claim is the comparison, not the exponent.** The registered claim takes the form *"`query_work`
grows materially more slowly than `N`, and materially more slowly than the global-scan ablation"* —
never *"the exponent is 0.31"*. Exponents are descriptive; the ordering against a named alternative
is what a reviewer can check.

---

## 4. The crossover number

The single most decisive scalar this programme can report, and the direct answer to the
index-construction hostile:

```text
Q*_crossover  =  the number of queries after which the indexed arm's TOTAL work
                 (build + maintenance + query) falls below the global-scan
                 ablation's total work on the same probe stream
```

An arm that looks sparse per query but never reaches crossover within the registered lifetime has not
demonstrated sparse cognition; it has moved the cost. `Q*_crossover` is reported at every scale and
is a primary endpoint of ME-SCALE-1. If it is unreached, the terminal is
`INDEX_MAINTENANCE_DOMINATES` and that is the result.

---

## 5. Task-complexity scaling

Difficulty `D` is varied **independently** of `N`, along the registered ladder:

```text
finite subtraction games → multi-state games → hidden-information / discrimination
→ planning / subgoals → cross-game transfer → formal reasoning / proofs
→ controlled compositional language → richer bounded language
```

For a frozen quality threshold `Q*`:

```text
D*(R, Q*)  =  the maximum registered complexity solved within resource budget R
              while satisfying Q*
```

The reported object is the **complete complexity-resource frontier**, not a selected task. A single
favourable `(D, R)` point is not a frontier and is not admissible as a scaling result.

---

## 6. Neural and Transformer comparators

Comparator configurations, as the domain matures: neural / RL parent; meta-learning and
continual-learning parent; Transformer; Transformer + retrieval; Transformer + persistent memory;
Transformer + tools / checkers; Transformer + adaptation / skill memory; strongest
domain-specialized parent.

**CL-S-T3 (comparator right of refusal on allocation).** Under a matched total compute budget the
comparator chooses its own compute-optimal allocation across model size, data and test-time compute.
The programme does not fix the comparator's architecture or training schedule and then call the
result fair. A comparator that was denied persistent memory or post-deployment adaptation that the
machine itself received is flagged `PARENT_UNDERTUNED` and its comparison is inadmissible.

Matching is on information, examples, feedback, tools, checker access, memory permissions,
interaction budget and protected-task access. Results are reported as **resource vectors**, never as
parameter counts.

---

## 7. Cognitive Productivity — secondary, vector-valued, worst-coordinate-first

At a pre-registered quality threshold `Q*`, for resource coordinate `r`:

```text
CP_r(Q*)  =  Resource_parent_r(Q*) / Resource_OCM_r(Q*)
```

`CP_r > 1` means the machine used less of coordinate `r` at matched quality. Reported separately for:
new information / examples; acquisition compute; query compute; storage; active memory; verification;
revision / retraining; maintenance / indexing; energy where measurable; whole-lifetime cost.

**CL-S-T4 (no scalar productivity score).** There is no weighted scalar CP. Weights would be chosen
after the outcomes and would be the mechanism by which a loss is hidden.

**CL-S-T5 (worst-coordinate disclosure).** Any statement citing a favourable `CP_r` must cite the
**least favourable coordinate in the same breath**, in the abstract as well as the body. This is the
structural answer to the hostile *"one favourable resource coordinate hides losses elsewhere"*: a
paper that satisfies this rule cannot make the claim the hostile describes.

**The capability gate comes first.** No productivity statement is read at all until task quality meets
the pre-registered non-inferiority margin against the strongest parent.

---

## 8. Registered scaling signatures

Each requires, without exception: a positive family, a negative/control family, the strongest parent,
an ablation, a scale sweep, an interval or statistical model, full resource accounting, a falsifier,
and an honest terminal.

| id | signature | falsifier |
|---|---|---|
| ME-SCALE-1 | active-subspace scaling: `k << N`, query work tracks `k` not `N` | `k` grows near-linearly in `N`, or `Q*_crossover` is unreached |
| ME-SCALE-2 | amortized acquisition: related-task cost falls with useful experience | the unrelated arm falls equally, i.e. an order effect |
| ME-SCALE-3 | amortized reasoning: marginal query work falls with experience | later families are easier under difficulty matching |
| ME-SCALE-4 | local revision scaling: repair cone grows slower than `N` | the globally shared revocation shows locality was benchmark-imposed |
| ME-SCALE-5 | failure-learning scaling: failure recurrence falls with experience | exclusions are keyed on task identity, not on assumptions |
| ME-SCALE-6 | transfer productivity: transfer benefit rises with experience | benefit is answer retrieval, not witnessed method invocation |
| ME-SCALE-7 | representation / consolidation productivity | consolidation cost exceeds the search it saves |
| ME-SCALE-8 | task-complexity frontier `D*(R, Q*)` dominates the parent's | the parent's frontier meets or exceeds it |
| ME-SCALE-9 | whole-lifetime resource frontier | any coordinate reverses the ordering |

---

## 9. Critical hostile controls

Every one of these must have a named control and a reported result.

- [ ] the machine appears sparse only because index construction scanned all `N` → §4 crossover;
- [ ] preprocessing / indexing cost omitted → build and maintenance charged separately;
- [ ] hand-authored operators encode future tasks → bits-of-prior accounting, protocol §5;
- [ ] storage grows enormously while query compute looks small → `B_N` reported at every scale;
- [ ] acquisition compute grows enormously while inference looks cheap → `C_acquire` on the same axis;
- [ ] the external checker performs the actual cognition for free → checker calls are a charged coordinate;
- [ ] later families are easier, creating fake amortization → difficulty-matched later tasks, frozen probes;
- [ ] transfer benefit is answer retrieval → `ReuseEventV1` execution-trace witness required;
- [ ] `k` grows nearly linearly in `N` → reported as the ME-SCALE-1 falsifier, not omitted;
- [ ] local revision worked only because the benchmark forced locality → the globally shared revocation hostile;
- [ ] the Transformer comparator is not compute-optimal → §6 right of refusal;
- [ ] the neural comparator is denied memory or adaptation the machine received → `PARENT_UNDERTUNED`;
- [ ] capability drops as the machine is scaled → capability gate re-read at every scale, not once;
- [ ] one favourable coordinate hides losses elsewhere → CL-S-T5 worst-coordinate disclosure.

---

## 10. Terminals

```text
ACTIVE_SUBSPACE_SCALING_SUPPORTED          AMORTIZED_ACQUISITION_SUPPORTED
AMORTIZED_REASONING_SUPPORTED              LOCAL_REVISION_SCALING_SUPPORTED
COGNITIVE_PRODUCTIVITY_ADVANTAGE_AT_MATCHED_QUALITY
LIFETIME_RESOURCE_FRONTIER_ADVANTAGE       SCALABILITY_PARTIAL_ONLY
LINEAR_GLOBAL_WORK_DOMINATES               STATE_SIZE_DOMINATES
MAINTENANCE_COST_DOMINATES                 NO_AMORTIZATION
NEGATIVE_TRANSFER_DOMINATES                NEURAL_PARENT_SCALING_DOMINATES
PARENT_SUFFICIENT                          CANNOT_CHECK_<reason>
```

---

## 11. The strongest admissible claim

Not *"the machine has a higher productivity score"*. Only, and only if the curves, ablations, parent
comparisons and independent replication support it:

> Across prospectively registered increases in persistent competence and task complexity, the machine
> maintains matched task quality while exhibiting a distinct scaling regime in which active cognition,
> marginal acquisition and local revision grow substantially more slowly than total accumulated
> competence, and yields a superior whole-lifetime resource frontier relative to the strongest matched
> neural and Transformer parents.

Until every clause of that sentence is separately earned, the correct report is the applicable
terminal from §10 — most plausibly, at the present stage of the programme, `PARENT_SUFFICIENT` on
`k(N)`, because an ordinary index also answers queries without scanning its whole contents. Saying so
early is not pessimism; it is what makes the eventual residual, if there is one, worth reading.
