# Stage D-v0 — common microbasis derivation calibration

This is the first direct test of the user-level Track-B requirement:

> if there is a general machine-intelligence substrate, known forms should be recoverable from the same lower-level basis rather than inserted as architecture-labelled primitives.

## Frozen microbasis

The bounded basis contains only:

```text
finite local state / inputs / feedback label
constants {0,1,2}
is-zero / is-two
bounded increment / decrement
bounded addition
minimum
if-then-else composition
```

Forbidden basis vocabulary includes:

```text
NEURON
PRODUCTION_RULE
BAYES_UPDATE
PROGRAM_INTERPRETER
ATTENTION
BACKPROP
```

Exact semantic enumeration to expression size 6 yielded:

```text
prediction semantic classes = 702
update semantic classes     = 1,979
```

## Four registered tiny targets

### 1. Neural-like discrete parametric threshold learner

This target has a mutable scalar parameter/state, a thresholded distributed input sum, and a label-directed parameter update.

Exact minimum expressions found within the frozen basis:

```text
predict size 6: is2(add(s,add(x0,x1)))
update  size 6: add(l,is2(add(s,l)))
```

This is only a **micro analogue** of parametric neural learning. It is not a multilayer network and does not implement backpropagation.

### 2. Symbolic rule micro-system

State acts as an enabled-rule flag and the input activates the rule.

```text
predict size 3: min(s,x0)
update  size 6: ite(min(x0,l),x0,s)
```

### 3. Evidence-accumulator micro-system

State stores a bounded evidence count and output depends on whether evidence is non-zero.

```text
predict size 3: is0(is0(s))
update  size 3: add(s,l)
```

This is **not** a full Bayesian posterior or probabilistic program. It is a deterministic evidence-update analogue intended to pressure the same-basis hypothesis before a stochastic arm is introduced.

### 4. Programmatic register micro-system

State behaves as an explicit register with conditional read/write.

```text
predict size 4: ite(x0,s,x1)
update  size 4: ite(x0,l,s)
```

## What this establishes

At this finite scope, a single architecture-neutral primitive set can compile the registered current-behavior + update laws of four deliberately different tiny targets.

Terminal:

```text
COMMON_MICROBASIS_D1_COMPILES_FOUR_TOY_MORPHOLOGIES__UNIVERSALITY_NULL_OPEN
```

This is stronger than D0 representability because update/development semantics are included, but it remains only a bounded **D1 developmental compilation** result.

## What this does NOT establish

It does not establish:

- a fundamental cognitive unit;
- a unique minimal basis;
- that a neural network, production architecture, Bayesian system or program learner in full scale derives efficiently;
- developmental acquisition of those forms without target labels;
- a morphology phase law;
- an intelligence-specific result beyond a small generic program algebra.

The strongest mundane explanation remains:

```text
small generic program algebra can encode several tiny state/update systems
```

Therefore the live nulls remain:

```text
UNIVERSAL_COMPUTATION_ONLY
PARENT_FORMALISM_SUFFICIENT
```

## Why the result is still useful

It establishes a concrete distinction between three increasingly strong requirements:

```text
D0 simulate a known form
D1 compile its behavior + update law from a common frozen basis
D2 acquire that form without architecture labels
```

Stage D-v0 reaches only D1.

The next decisive attack is not to add more named forms by hand. It is:

1. replace the convenient microbasis with the Stage C-v1 structured basis frozen before targets;
2. search for the four target developmental phenotypes from that basis;
3. compare description/update/execution cost against exact parent implementations;
4. introduce an explicit stochastic arm for a genuine probabilistic target;
5. only after that test D2 blind developmental acquisition.
