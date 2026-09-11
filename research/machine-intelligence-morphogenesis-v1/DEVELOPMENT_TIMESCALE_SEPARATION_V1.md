# Execution vs development timescale separation v1

Status: **theory correction motivated by neural and programmatic parents**.

## Problem

A tempting definition of a fundamental cognitive unit is:

```text
state + input -> output + self-update
```

But this silently assumes that learning/adaptation is local and online at the same timescale as execution.

Many legitimate machine-intelligence forms violate that assumption.

Examples:

- a neuron/activation unit may have a fixed forward transformation while backpropagation changes shared weights through a separate training process;
- a frozen trained neural model may perform sophisticated cognition with no online parameter update;
- a symbolic production can be fixed while an external chunking/rule-learning process creates new productions;
- a program may be immutable during execution while an external synthesizer/evolutionary process creates a successor program;
- a Bayesian inference engine may have fixed inference rules while posterior state changes;
- hardware may be fixed while mutable memory carries adaptation.

Therefore unit-level self-adaptation cannot be assumed necessary for all machine intelligence.

## Two-timescale factorization

Track B should separate:

### Execution basis

\[
B_{exec}=(\mathcal T,\mathcal P,\mathcal C,\rho_{exec})
\]

containing typed transformations/composition used to execute the current machine.

### Developmental basis

\[
B_{dev}=(\mathcal U,\mathcal G,\rho_{dev})
\]

containing legal update/mutation/synthesis/rewrite operations over:

```text
parameters
state
memory
programs
rules
topology
representation
control policies
```

A complete generative substrate is then provisionally:

\[
B=(B_{exec},B_{dev}).
\]

This is a modeling separation, not a claim that the two sets are physically distinct. A primitive may participate in both.

## Three timescales to record

For a morphology `M` distinguish:

```text
T0 execution:
   current M processes one task/step

T1 learning/development:
   experience changes state/parameters/rules/topology of M

T2 morphogenesis/meta-development:
   the machinery that defines M's representation/update/search itself changes
```

Examples:

```text
neural:
  T0 forward pass
  T1 gradient/meta-learned parameter update
  T2 architecture / optimizer / representation evolution

programmatic:
  T0 execute program
  T1 library/synthesis update
  T2 mutation/search-language change

OCM-like:
  T0 operator execution
  T1 admit/revise cognitive assets
  T2 change acquisition/executive/representation machinery under governance
```

## Consequence for fundamental-unit claims

A unit should not be rejected merely because it lacks an internal learning rule.

The stronger minimality question is:

> What is the smallest pair/equivalence class of execution + developmental generating operations sufficient to recover the registered morphology families under bounded cost?

This may yield:

```text
EXECUTION_PRIMITIVES_SMALL__DEVELOPMENTAL_OPERATORS_RICH
```

or the opposite. Do not force them into one tuple.

## Consequence for neural derivation

To derive a neural morphology we need separately:

1. an execution construction for weighted aggregation/nonlinearity at registered precision;
2. a developmental construction for changing parameters/topology;
3. a compiler/resource account for both.

Backpropagation is therefore a candidate **developmental morphology**, not a property every neural execution unit must contain.

## Consequence for fixed pretrained models

A fixed model may have no `T1` adaptation during evaluation and still have substantial competence because its developmental history occurred earlier.

Hence:

```text
current adaptability != intelligence
```

and

```text
developmental history must be accounted even when the deployed morphology is frozen.
```

This is important for matched comparisons to foundation models.

## New hostile

Any future basis proposal that places a strong architecture-specific learning rule inside the fundamental execution primitive must compare against a separation in which the same rule lives at `B_dev` instead.

If moving it outward preserves capability/development at equal or lower cost:

```text
UNIT_INTERNAL_ADAPTATION_NOT_IRREDUCIBLE
```

## Current implication

The live Track-B object is better written as:

\[
\mathfrak B=[(B_{exec},B_{dev})]_{E,R,V,\mathcal K}
\]

rather than assuming one self-modifying cognitive atom.