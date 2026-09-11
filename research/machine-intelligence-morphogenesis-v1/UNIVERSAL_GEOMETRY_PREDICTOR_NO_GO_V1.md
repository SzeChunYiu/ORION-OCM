# Universal developmental-geometry predictor no-go v1

Status: **computability boundary inherited from halting/Rice-style limits; not novel mathematics.**

Refs #377, #233, #373.

## Claim attacked

An overstrong GMI theory might promise a computable function that, for **every** arbitrary machine morphology `M` and task `tau`, predicts exactly whether/when the machine will reach a verified solution and therefore its exact developmental/search burden.

That cannot hold over an unrestricted Turing-complete morphology class.

## Reduction from halting

Assume a computable predictor

\[
P(M,x)
\]

that returns the exact finite first-hitting burden if machine/program `M` reaches the registered success state on input `x`, and a distinguished value `INFINITY/NEVER` otherwise.

Given an arbitrary program `p` and input `x`, construct a Track-B morphology whose registered success event is exactly:

```text
p(x) halts.
```

Run the hypothetical predictor.

- finite burden => `p(x)` halts;
- `NEVER` => `p(x)` does not halt.

This decides the halting problem, contradiction.

Therefore no such total computable exact predictor exists for unrestricted Turing-complete morphologies/tasks.

## Stronger semantic warning

Many nontrivial semantic questions about arbitrary programs are subject to Rice-style undecidability. A universal exact classifier of morphology behavior, usefulness or future competence cannot be assumed merely because the morphology has a common representation.

## What remains possible

Track B can still produce useful theory in restricted regimes:

### Finite exact classes

Bound state/program size, horizon and transition grammar; enumerate or solve exactly.

### Decidable structured families

Exploit special structure such as convex optimization, finite factor graphs, bounded treewidth, restricted grammars or proof systems.

### Approximate / probabilistic predictors

Learn or derive predictors under explicit task/ecology distributions and report uncertainty/generalization bounds.

### Lower/upper bounds

Prove burden bounds without exact outcome prediction.

### Empirical phase laws

Prospectively test a frozen structural predictor on held-out but bounded/structured ecologies.

## Consequence for “general theory” wording

`general` cannot mean:

> exact prediction of intelligence/development for every computable machine and every future task.

A defensible meaning is closer to:

> one vocabulary/measurement theory plus families of theorems/predictors whose assumptions are explicit and which transfer across several materially different morphology classes.

## Consequence for unknown-form search

There cannot be a complete computable oracle that certifies, for every arbitrary candidate, all future developmental advantages over all possible tasks.

New-morphology claims must therefore be:

```text
registered ecology / resource / verifier scope
+ bounded equivalence checks
+ disjoint empirical/formal replication
+ explicit unresolved external regimes
```

## Terminal

```text
UNIVERSAL_EXACT_DEVELOPMENTAL_GEOMETRY_PREDICTOR_IMPOSSIBLE_FOR_UNRESTRICTED_TURING_COMPLETE_SCOPE
```

This limit strengthens the programme by forcing scoped, falsifiable laws rather than metaphysical universality.