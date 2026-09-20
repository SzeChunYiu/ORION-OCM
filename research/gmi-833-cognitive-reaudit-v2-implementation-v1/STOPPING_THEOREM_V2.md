# PS-1 — stopping is a Bellman comparison on a finite acyclic computation graph

Status: **THEOREM + EXACT FINITE WITNESSES.** Issue #833 Section M row
`Re-audit planning and stopping.`; freeze `cb6d6a59`; package
`gmi-833-cognitive-reaudit-v2-implementation-v1`. All arithmetic exact
rational (CPython `Fraction`); no float appears anywhere.

## 1. Setting

A **computation graph** is a finite acyclic directed graph of states. At each
state `s`:

- there is a nonempty set of **registered terminal actions**, each with an
  exact rational value `val(s,a)`; write
  `best(s) = max_a val(s,a)`. A state with no registered terminal action is a
  **missing goal/model** and is refused, never silently completed;
- `s` may own **tests**; test `t` has an exact nonnegative cost `c(t)` and
  branches to children `(c, P(c))` with `P(c)` exact, nonnegative, and
  summing to one, every child being a strict descendant in the acyclic order.

Every cost is charged exactly once in the recursion: a test at `s` charges its
`c(t)` and the child state's optimal value already charges everything
downstream (the supplied first-use/storage/lookup/transport/execution price
terms are the complete prices). A **cyclic** graph is refused rather than
silently completed, so unbounded computation cannot arise.

## 2. Optimal value and the Bellman equation

Let `V*(s)` be the optimal value achievable from `s` by **any** policy: at
each reached state the policy either stops (taking `best(s)`) or runs one
registered test and continues optimally.

**Bellman equation.** For a finite acyclic computation graph,

```
V*(s) = max( best(s),  max_{t in tests(s)} [ -c(t) + sum_c P(c) V*(c) ] )
```

with the empty test set giving `V*(s) = best(s)`.

**Proof** (induction over the acyclic order, children before parents).
*Base:* sinks (no tests) have `V*(s) = best(s)`, which is the expression.
*Step:* assume the formula for every child (strictly earlier in the order).
Any policy at `s` either stops (value `best(s)`) or runs test `t` at cost
`c(t)` and then follows some continuation in each child; by induction that
continuation has value at most `V*(c)`, so the total is at most
`-c(t) + sum_c P(c) V*(c)`, which is at most the displayed maximum.
Conversely the maximum is attained: stop, or run the argmax test and follow
an inductively attaining optimal policy in each child. Hence equality. The
order is finite, so the induction terminates; only exact rational arithmetic
is used, never approximation and never floating point. ∎

## 3. PS-1 — stopping optimality criterion

**Theorem PS-1.** On a finite acyclic computation graph with every cost
charged (first-use, storage, lookup, transport, execution), *stopping is
optimal at `s` exactly when the best registered terminal action value is at
least every cost-charged continuation value computed with future optimal
computation included*:

```
stop optimal at s  <=>  best(s) >= -c(t) + sum_c P(c) V*(c)   for every test t at s.
```

**Proof.** Stopping is optimal at `s` iff `V*(s) = best(s)`. By the Bellman
equation, `max(best(s), max_t cont(s,t)) = best(s)` iff
`max_t cont(s,t) <= best(s)` iff `cont(s,t) <= best(s)` for every `t`. Both
directions are constructive: `(<=)` stop and you are optimal; `(=>)` if a
test's continuation exceeded `best(s)` the Bellman equation would force
`V*(s) > best(s)`, contradicting optimality of stopping. ∎

The executable `stop_is_optimal` evaluates exactly this comparison; the
executor additionally verifies `V*(root)` by an independent
`optimal_value_by_policy_search` that enumerates **every** policy (48 in the
registered instance — root has 3 choices {stop,t1,t2}, each of the four
one-test states has 2, each sink has 1) and propagates its exact value — a
genuinely different code path, zero mismatches across the hostile, clean and
tie instances (144 policies in total).

**Assumptions.** `s` is a state of a finite acyclic computation graph with a
nonempty registered terminal-action set and exact rational test costs and
transition probabilities summing to one; every cost is charged exactly once
(first-use, storage, lookup, transport, execution); the graph is acyclic, so
no computation is silently unbounded.

**Dependencies.** The Bellman equation for finite acyclic computation graphs
(Section 2); the claim-governance contract of the upgraded #833 foundation
(`c0c574c4...`) and axiom core (`3366a3bc...`), pinned in MANIFEST_V1.json and
re-checked at run time by `parents_v1.py`.

**Falsifiers.** Any finite acyclic computation graph with all costs charged in
which stopping is optimal at `s` yet `best(s) < cont(s,t)` for some test `t`;
a cyclic graph silently completed; a missing goal/model silently completed;
any floating-point arithmetic in the comparison.

**Strongest parents.** #926/#927 freeze conclusion 2 (stopping is a Bellman
comparison; pin `cb6d6a59`); the myopic META-3 EVC stop rule retained only at
its proved scope (`gmi-planning-stopping-v1`, pin `7219b55a...`).

## 4. PS-2 — a merely myopic one-step EVC rule is not generally sufficient

The **myopic one-step EVC** at `s` for test `t` is

```
EVC_m(s,t) = -c(t) + sum_c P(c) best(c) - best(s)
```

It prices each immediate child by its best-terminal value `best(c)` and stops
when `EVC_m <= 0` for every test. Because it substitutes `best(c)` for the
optimal continuation `V*(c)`, it can under-value tests whose *descendants*
are worth paying for — i.e. it can miss exactly the two-step information plans
that the Bellman comparison would continue into.

**Hostile instance (registered, exact).** `X = f1 XOR f2` with `f1, f2` iid
fair bits. Terminal actions `a0` (predict `X = 0`) and `a1` (predict `X = 1`),
each with value equal to its probability of correctness; tests `t1 = observe
f1`, `t2 = observe f2`, each at exact cost `k`.

At the root `P(X = 1) = 1/2`, so `best(root) = 1/2`. For `k = 1/8`:

- `myopic EVC(root, t1) = -1/8 <= 0` and `myopic EVC(root, t2) = -1/8 <= 0`
  → the myopic rule **stops**;
- yet `V*(f1=0)=V*(f1=1)=V*(f2=0)=V*(f2=1)=7/8`,
  `V*(00)=V*(01)=V*(10)=V*(11)=1`, and
  `cont(root,t1) = -1/8 + (1/2)(7/8) + (1/2)(7/8) = 3/4 > 1/2 = best(root)`;
- `V*(root) = 3/4`, so the two-step information plan (observe one bit, then
  the other, then predict with certainty) has net value
  `V*(root) - best(root) = +1/4 > 0`, and the Bellman comparison **continues**.

So on the very same instance the myopic rule stops while optimal computation
continues with strictly positive net value. This hostile genuinely fires: it is
actually computed, the numbers are reproduced by the independent
full-policy enumeration, and it is caught by the Bellman comparison.

**Clean variant (no alarm).** At `k = 1`, `V*(root) = best(root) = 1/2`,
stopping is optimal, and the myopic EVC is `-1 <= 0` — the myopic rule also
stops. The control does not alarm on a genuinely stop-optimal instance.

**Tie-preserving control.** At `k = 1/4`, `cont(root,t1) = cont(root,t2) =
best(root) = 1/2`: the optimal choice set at the root is exactly
`{stop, t1, t2}` (size 3) and the best terminal-action set is `{a0, a1}`
(size 2). Optimal ties remain sets and are never silently broken.

**Assumptions.** The registered hostile instance `X = f1 XOR f2` with `f1, f2`
iid fair and tests `t1`, `t2` at exact cost `1/8`; the `k = 1` clean variant;
the `k = 1/4` tie control; exact rational arithmetic throughout.

**Dependencies.** PS-1's Bellman comparison and the independent full-policy
enumeration oracle (`optimal_value_by_policy_search`); the retained myopic
META-3 EVC scope (13/35) from the frozen `gmi-planning-stopping-v1`.

**Falsifiers.** A registered instance on which the myopic one-step EVC rule and
the Bellman comparison disagree in the opposite direction; the `k = 1` clean
variant alarming (firing a false positive); optimal ties silently broken;
`MYOPIC_EVC_IS_UNIVERSALLY_OPTIMAL` asserted anywhere.

**Strongest parents.** #926/#927 freeze conclusion 2 (a merely myopic one-step
EVC rule is not generally sufficient; pin `cb6d6a59`); the upgraded #833
foundation (`c0c574c4...`) and axiom core (`3366a3bc...`).

## 5. Refusal controls

- **Missing goal/model** — a state with no registered terminal action is
  refused (`ValueError`), not completed with a silent value.
- **Cyclic unbounded computation graph** — refused (`ValueError`), because an
  unbounded computation cannot be silently completed.

## 6. Retained myopic scope (freeze duty)

The META-3 myopic EVC stop rule is imported verbatim from the frozen
`gmi-planning-stopping-v1` package (pin `7219b55a64d1baf5d9fe03a9b40f5c0bceec00b7`)
and retained only at its proved scope: optimal in exactly **13 of 35**
no-common-action subsets, with the disagree witness `S = {3,5}` (EVC-myopic
picks `t0`, TDA-optimal `t1`). The freeze forbids
`MYOPIC_EVC_IS_UNIVERSALLY_OPTIMAL`; PS-2 is precisely the counterexample the
freeze demands.

## 7. Claim boundary

Earned only at green CI, at the frozen exact scope:
`GMI_833_HIERARCHY_PLANNING_CAUSAL_REAUDIT_AT_REGISTERED_EXACT_SCOPE`.
No claim that neutral search reaches any goal, that goals are derived from
value-free dynamics, or that myopic EVC is a general optimal-stopping rule.
