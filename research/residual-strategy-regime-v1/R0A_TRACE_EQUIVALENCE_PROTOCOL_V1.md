# R0A trace/lifecycle equivalence protocol V1

**Status:** formal parent adoption / no learned policy / no production early-exit authorization.

R0A asks whether post-first-pass verification work can be removed after an exact
answer is already available.  The correct parent is not answer equality alone.
It is **observational/stuttering equivalence plus lifecycle-state equivalence**.

The mature formal-methods literature already distinguishes strong stepwise
bisimulation from stutter-insensitive/branching equivalences that may collapse
unobservable internal steps while preserving the chosen temporal observations.
Program slicing makes the complementary point that statements may be removed only
relative to an explicitly selected observable property/state slice.

Parent references:

- Browne, Clarke and Grumberg, 1988: stuttering equivalence / CTL* without the
  next operator;
- De Nicola and Vaandrager, 1990: branching bisimulation and stuttering
  equivalence;
- Clarke, Grumberg and Peled, *Model Checking*: LTL without `X` is invariant
  under stuttering;
- Harman and Danicic, 1995: slicing relative to the variables/properties under
  test.

## 1. Protected observation alphabet

Before touching compose/check code, freeze a visible label function

```text
L(s,step) = (
  protected answer/status,
  authority/checker result,
  support/provenance mutations,
  revocation/failure-knowledge mutations,
  persistent search/learning-state mutations,
  externally consumed audit/event record,
  resource counters declared part of the experiment
).
```

A step may be called `tau`/silent only if removing its *occurrence* does not alter
any protected visible label required by the experiment or production contract.
Do not classify a checker invocation as silent merely because its Boolean answer
matches a prior checker invocation.  If the call contributes support, evidence,
failure knowledge, a persistent trace, accounting, learning data, or future
revocation behavior, it is visible at the protected scope.

## 2. Suffix-elision theorem

Let a deterministic execution after first exact answer be

```text
s0 --tau1--> s1 --tau2--> ... --taun--> sn
```

and let `~C` be a protected contract-bisimulation relation over persistent
machine states.  Suppose:

1. every `tau_i` is invisible under the frozen protected observation alphabet;
2. `s0 ~C sn`;
3. every future legal lifecycle action from related states satisfies the same
   contract-bisimulation conditions (same admissible protected actions,
   immediate protected contract, and successor equivalence-class behavior).

Then replacing the whole suffix by immediate termination at `s0` preserves:

```text
current protected visible output;
all future finite-horizon protected values/contracts;
all temporal properties over the frozen visible labels that are insensitive to
internal stuttering.
```

### Proof

Condition 1 makes the removed finite suffix an unobservable stutter block.  The
visible trace before the suffix and at its end is unchanged.  Condition 2 puts
the early-exit persistent state and the original post-suffix persistent state in
the same contract-bisimulation class.  By the finite-horizon bisimulation theorem
in `FORMAL_DECISION_CORE_V2.md`, every future legal lifecycle policy has the same
protected value/contract behavior from either state.  Standard stuttering
invariance gives preservation of temporal formulas over visible labels that do
not count the number of invisible next steps.  Therefore the suffix can be
elided at this declared observation scope.  QED.

## 3. Converse hostile rule

If any removed post-pass step has a protected visible effect, or if early-exit
state and original final state are separated by a future lifecycle experiment,
then output equality alone is **not** a proof of safe elision.

A single counterexample is sufficient to reject the optimization.

Examples that must remain hostile:

```text
same answer but second check adds independent support;
same answer but second check records a failure/negative observation;
same answer but later revocation survives only because of duplicated support;
same answer but replay/event log differs at a contract-consumed event;
same answer but cache/index/learning state changes future cost or action;
same answer but timeout/exception path differs;
same final state projection but resource/accounting contract includes checker calls.
```

## 4. `next`-operator boundary

Ordinary stuttering equivalence deliberately ignores the exact number of internal
steps and therefore does not preserve a temporal specification that explicitly
observes "the next step".  If OCM's protected contract includes exact event
positions/order at every internal verification call, use a stronger
next-preserving/strong trace relation instead of claiming stuttering safety.

Thus the experiment must preregister which events are semantically visible.
Choosing the alphabet after seeing an optimization result is invalid.

## 5. Exact R0A experiment

For each candidate post-first-pass check:

1. execute incumbent and early-exit variants from an identical checkpoint;
2. compare protected visible traces under the frozen alphabet;
3. compare complete serialized/persistent state, then if bytes differ prove a
   narrower contract-bisimulation relation rather than hand-waving equality;
4. replay both states through a frozen adversarial lifecycle suite:
   revocation, support withdrawal, retry, reset, checkpoint/restore, failure
   injection and any learning/update path touched by the checks;
5. publish raw work removed and work added by the early-exit predicate;
6. accept only if every removed check is either proved silent or proven redundant
   by the stronger state relation.

## 6. Terminals

```text
EXACT_EARLY_EXIT_TRACE_EQUIVALENT
  full protected trace/lifecycle gate passes and exact work is removed

EARLY_EXIT_OUTPUT_ONLY_NOT_LIFECYCLE_EQUIVALENT
  answer equality passes but protected state/trace/future behavior differs

EARLY_EXIT_PREDICATE_COST_DOMINATES
  semantically valid elision exists but recognizing it costs at least the work
  removed
```

No learned router belongs in this lane unless exact semantic elision fails but a
real safe strategy-choice residual remains afterward.