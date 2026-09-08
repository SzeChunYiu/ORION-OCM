# Action-sufficient epistemic state — formal spine for Minimum Sufficient Cognition

**Research status:** conventional decision-theoretic synthesis / no novelty claim / no ML authorization.

This note sharpens `CONVERGENCE_V1.md` into one object that can be falsified by
R0A/R0B/R0C/R0D.  It is intentionally expressed as standard decision theory,
metareasoning and state abstraction rather than as an OCM-specific theorem.

## 1. Safety sufficiency is not economic sufficiency

For surviving admissible models `V` in context `d`, let

```text
G_m(d) = protected actions acceptable if model m is true
Gamma(V,d) = intersection_{m in V} G_m(d)
```

`Gamma(V,d) != empty` proves that full hidden-model identification is not
required to take *some* protected action.  It does **not** by itself prove that
further cognition is wasteful.

If every model licenses action `a_safe`, but `a_safe` is expensive, a paid probe
may still be worthwhile when it can reveal that a cheaper protected action is
available.  Therefore there are two separate questions:

```text
safety sufficiency:
  is a protected action already certified?

economic sufficiency:
  is buying more cognition cheaper than acting with what is already certified?
```

DEV5/common-action results answer the first question.  DEV6/X1/R0B show why the
second must be charged separately.

## 2. Paid-cognition stopping rule

For a fixed, prospectively declared nonnegative resource price vector `w`, let
`r(m,a)` be the raw resource vector for protected action `a` when `m` is true.
For a worst-case objective define the current stop cost

```text
Stop_w(V,d)
  = min_{a in Gamma(V,d)} max_{m in V} w . r(m,a).
```

For a cognitive intervention/probe `u` with resource vector `c(u)`, legal
outcome `y`, and successor version space `V_u^y`, the standard finite recurrence
is

```text
D_w(V,d)
  = min(
      Stop_w(V,d),
      min_u [ w . c(u) + max_y D_w(V_u^y, d_u^y) ]
    ).
```

Use an explicitly frozen expected-cost analogue when a prior/demand model is
registered.  Never switch between worst-case and expected objectives after
seeing results.

The machine has performed **minimum sufficient cognition** at `(V,d)` when the
stop arm is no worse than every admissible cognitive intervention under the
registered objective.

This corrects the over-strong shortcut

```text
Gamma(V,d) != empty  =>  stop immediately.
```

The correct implication is only

```text
Gamma(V,d) != empty  =>  full identification is unnecessary for safety.
```

## 3. Cognition can change information, reusable state, or both

R0B requires a state richer than a version space.  Let

```text
sigma = (V, s, d)
```

where `s` is non-authoritative reusable machine state: an exact index, proof
route structure, cache, support structure, checkpoint, or other retained
computation.

A cognitive intervention may then have two values:

```text
information value: V -> V'
state-investment value: s -> s'
```

and some interventions do both.

For a finite horizon, a conventional Bellman form is

```text
J_w(sigma,h) = min(
  min_{a in Gamma(V,d)} [
    w . c_action(sigma,a)
    + E J_w(T_action(sigma,a), h-1)
  ],

  min_u [
    w . c_cognition(sigma,u)
    + E_y J_w(T_cognition(sigma,u,y), h)
  ]
).
```

The exact time index depends on whether an intervention consumes a demand step;
that convention must be frozen per experiment.  The important point is that
probe acquisition and persistent-state construction are both paid state
transitions, not free preprocessing.

This gives one disciplined interpretation of several lanes:

```text
R0A  optional extra verification after a sufficient exact answer
      -> buy more cognition only if lifecycle value exceeds check cost

DEV5  common protected answer before singleton identification
      -> information stopping opportunity

DEV6/X1
      -> the stopping predicate itself has acquisition/maintenance cost

R0B  inverse now versus build/extend reusable semantic state
      -> state-investment decision

R0C  layered versus indexed proof search
      -> exact strategy/state-investment decision if a real population exists
```

## 4. Action-sufficient state and decision quotient

Let `C` be the frozen protected output + lifecycle contract and let `w`/horizon
be part of the registered objective.  Two legal machine states are
**decision-equivalent** at this scope when every admissible protected action and
cognitive intervention has the same contract-relevant value and successor
class.  Operationally, this is the usual decision-state/bisimulation idea:
retain only distinctions that can change an admissible decision or its future
contract value.

The resulting quotient is the target representation for decision making.  It
is generally coarser than hidden-world identity.

Consequences:

```text
same hidden cause not required
same best-operator label not required
same current answer not always sufficient
same confidence/entropy not authoritative
same legal observation can be insufficient
```

A lifecycle distinction belongs in the quotient whenever it can change future
revocation, replay, support, fallback, authority, or resource behavior.

## 5. Feature-collision impossibility lemma

Let `phi(sigma)` be the frozen legal pre-outcome feature map available to a
selector.  Let `A*(sigma)` be the set of optimal protected strategies under the
registered objective.

If there exist legal states `sigma_1`, `sigma_2` such that

```text
phi(sigma_1) = phi(sigma_2)

but

A*(sigma_1) intersection A*(sigma_2) = empty,
```

then no deterministic selector of the form

```text
pi(phi(sigma))
```

can be optimal on both states.

**Proof:** the selector must emit the same action on equal inputs, while the two
states have disjoint optimal-action sets.  Therefore the emitted action is
non-optimal in at least one state.  QED.

This is an observation-channel result, not a model-capacity result.  Replacing a
threshold with an MLP does not remove the collision.

For a feature bucket `B`, the exact best deterministic feature-conditional cost
is

```text
C_phi(B) = min_a sum_{sigma in B} Q(sigma,a)
```

under the frozen bucket weighting, while the full-information oracle cost is

```text
C_oracle(B) = sum_{sigma in B} min_a Q(sigma,a).
```

Therefore

```text
Regret_floor(B) = C_phi(B) - C_oracle(B) >= 0
```

is a stronger quantity than classification error.  It is the irreducible cost
of the frozen observation partition before paying any policy inference,
training, or maintenance cost.

`prospective_selector.py` implements this audit first for the R0B cold frontier.

## 6. Misspecification remains an authority boundary

The decision quotient is only sound relative to the protected model/contract
language.  If the true world relevant to authority is outside the declared
hypothesis class, a singleton or unanimous version space can still be wrong.

Therefore a policy may use confidence, entropy, margin, or a statistical model
to order exact search, but those quantities do not independently authorize a
protected answer.

A protected action requires either:

```text
an adequacy/coverage argument for the relevant class
or
a fail-closed checker/authority boundary independent of the predictive policy.
```

This keeps DEV4 logically separate from ordinary selector accuracy.

## 7. Vector resources before scalar claims

The Bellman equations above use `w` only to define one prospectively declared
price regime.  The experiment must still publish raw resource vectors.

For candidate policies `A` and `B` with raw difference vector

```text
d = C_A - C_B,
```

report:

```text
Pareto dominance, if present;
otherwise the price region { w >= 0 : w . d < 0 }.
```

A selector does not become generally better because one retrospective scalar
exchange rate makes it look better.  X3 and the native-proof runtime results
make this requirement load-bearing.

## 8. Research terminals implied by the quotient

The convergence can now terminate cleanly at several distinct places:

```text
REPRESENTATION_OR_DISCOVERY_LIMIT
  no useful admissible alternative exists (L0)

ECOLOGY_OR_DEMAND_LIMIT
  alternatives exist but essential use opportunity is zero (L1)

EXACT_POLICY_SUFFICIENT
  the decision quotient is captured by a cheap exact/simple parent

OBSERVATION_CHANNEL_INSUFFICIENT
  legal features alias states with disjoint required decision classes (L4)

COGNITION_NOT_ECONOMIC
  a better-informed/stateful decision exists but the cognition costs more than
  the work it avoids

RESIDUAL_ALGORITHM_SELECTION_OPPORTUNITY
  multiple safe strategies have genuinely different value across legally
  distinguishable states and a payable residual survives exact parents
```

Only the final terminal opens an ordinary algorithm-selection study.  It still
does not imply that a neural model is the right parent.

## 9. Cross-lane falsifiable predictions

The synthesis is useful only if it predicts results before seeing them.

### Prediction A — R0A

If the approximately post-first-pass compose checks have no protected lifecycle
value, an exact early exit should dominate a learned reordering policy because
it removes work without feature/inference cost.  If skipped checks affect trace,
learning, failure knowledge or future state, lifecycle equivalence will fail and
the optimization must be rejected.

### Prediction B — R0B

A state-only known-horizon threshold should capture much of the lifetime sign
change.  Any remaining target-specific residual must first survive the legal
feature-collision/regret-floor audit.  If F0/F1/F2 leave only a tiny payable
regret, selector learning is economically dead even when F3 proves that exact
task identity contains enough information in principle.

### Prediction C — R0C

Layered/indexed proof scheduling becomes a legitimate selector population only
if legal pre-proof structural features distinguish cost regimes across a much
larger frozen family.  Eventual theorem truth/falsity is not a legal selector
feature.

### Prediction D — R0D

Common-action stopping should weakly dominate singleton identification on probe
count whenever the former stops earlier, but can lose on total cognition when
computing the common-action predicate is expensive.  The paid recurrence should
predict the sign once all predicate/probe/action costs are charged.

These predictions are deliberately capable of killing the learned-router lane.
That is a feature, not a failure.