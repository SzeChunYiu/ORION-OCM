# Oracle scope correction V1 — optimality is always relative to an action set

**Status:** proved finite correction / no ML / no production change.

Phase 1 called its exact DP a "full-information oracle" because it receives
`R(q)`, `I(q)` and `K(q)` before choosing between the two registered arms:

```text
A1 = {INVERSE, TARGET_TRIGGERED_SEMANTIC}.
```

Phase 2B0 adds a new admissible policy family:

```text
PARTIAL_PREBUILD(f) + SEMANTIC_HIT_IF_COVERED + EXACT_INVERSE_FALLBACK.
```

Therefore the old DP is still an exact oracle on `A1`, but it is not an upper
bound on the expanded action set.

## Theorem — action-set expansion monotonicity

For any state `s`, cost function `Q(s,a)`, and finite action sets

```text
A subset A',
```

define

```text
V_A(s)  = min_{a in A}  Q(s,a)
V_A'(s) = min_{a in A'} Q(s,a).
```

Then

```text
V_A'(s) <= V_A(s).
```

### Proof

The minimum defining `V_A'` is taken over every action available to `V_A` plus
possibly more actions.  In particular the action achieving `V_A` is feasible in
`A'`.  Hence the minimum over `A'` cannot exceed `V_A`.  QED.

The same argument applies recursively to a finite-horizon Bellman problem when
each expanded state has a superset of admissible actions and the old transition
and cost semantics are retained.

## Strict-improvement corollary

If there exists a state `s` and added action `a_new in A'\A` such that

```text
Q(s,a_new) < V_A(s),
```

then

```text
V_A'(s) < V_A(s).
```

Thus a new exact parent beating the old cost-informed DP does **not** contradict
the old result.  It proves that the old oracle's action class was incomplete for
the newer question.

## Reporting rule

From Phase 2B0 onward use:

```text
PHASE1_TWO_ARM_ORACLE_REFERENCE
```

not an unqualified `full_information_oracle`.

A signed comparison is required.  If the fixed-frontier parent lies below the
reference, report that as **action-set expansion gain**, not as negative regret
and not as a selector result.

The earlier Phase-1 statement remains valid only with its original qualifier:

> upper bound on the value of per-query selection between the two frozen exact
> arms before selector cost.

It never bounded arbitrary future exact strategy families.