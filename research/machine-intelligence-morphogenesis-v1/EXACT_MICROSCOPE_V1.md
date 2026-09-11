# GMI-D2 Exact Microscope v1

Purpose: calibrate Track-B minimality/equivalence machinery on finite worlds **before** any architecture search or LUNARC campaign.

## Stage A — known-answer Boolean calibration (executed in this PR)

Universe:

- all `16` binary Boolean functions on inputs `(x,y)`;
- projections `x,y` are free variables, not counted as primitives;
- primitive catalogue: `NOT, AND, OR, XOR, NAND, NOR`;
- legal construction: functional composition only;
- cost coordinate: minimum expression depth in this first calibration.

Procedure:

1. enumerate all `2^6-1 = 63` non-empty primitive subsets;
2. compute exact closure under composition;
3. mark a subset complete iff closure contains all 16 binary Boolean functions;
4. identify inclusion-minimal complete subsets;
5. remove each primitive from every minimal basis and recompute closure (compensation-aware removal);
6. record minimum construction depth.

Executed result:

```text
54 / 63 subsets are complete at this tiny scope.

Inclusion-minimal complete bases:
  {NAND}       max minimum depth 3
  {NOR}        max minimum depth 3
  {NOT, AND}   max minimum depth 4
  {NOT, OR}    max minimum depth 4
```

Removing the sole primitive from `{NAND}` or `{NOR}` leaves only the two projections. Removing either primitive from `{NOT,AND}` or `{NOT,OR}` destroys completeness.

This is **not new mathematics**. It is a machinery check showing that the census correctly recovers multiple non-unique minimal bases and separates basis cardinality from compilation depth.

Terminal:

`EXACT_BASIS_CENSUS_CALIBRATED_ON_KNOWN_BOOLEAN_SCOPE`

## Stage B — developmental-equivalence counterexample

Next exact fixture:

Construct two machines with the same initial Boolean I/O behavior but different update laws:

```text
M_static:
  current function = XOR
  training example leaves parameters unchanged

M_adapt:
  current function = XOR
  one registered feedback event changes one state/parameter
```

Before feedback they are behaviorally identical. After feedback they diverge. This is the smallest planned witness for:

`BEHAVIORAL_EQUIVALENCE_NOT_DEVELOPMENTAL_EQUIVALENCE`.

## Stage C — tiny typed adaptive bases

After Stage B, register a finite grammar containing only low-level typed primitives such as:

```text
bit state / small finite state
read/write local state
boolean/arithmetic transform
message/pass value
conditional composition
bounded stochastic choice (separate arm)
parameter/state update
local topology add/remove (separate arm)
```

Do **not** include architecture labels such as:

```text
NEURON
PRODUCTION_RULE
BAYES_UPDATE
PROGRAM_INTERPRETER
ATTENTION
BACKPROP
```

For every basis:

- enumerate all legal morphologies up to frozen size/depth;
- quotient exact behavioral classes;
- quotient exact developmental classes;
- perform compensation-aware primitive removal;
- compute compilation-depth / state-size / update-work Pareto fronts;
- identify multiple equivalent minimal bases if present;
- retain `NO_SMALL_BASIS` and `NON_IDENTIFIABLE` terminals.

## Stage D — known-form micro-derivations

Only after Stage C is stable, construct tiny target instances from different paradigms:

1. a 2–3 unit feedforward threshold/neural computation;
2. a finite production/rewrite controller;
3. a tiny stochastic/Bayesian update fixture;
4. a tiny explicit program/library learner.

The goal is not to prove general derivability yet. The question is whether the same frozen basis can reproduce the **behavior + registered update law** without architecture-labelled macros and at what cost.

## Adoption/kill rules

- If every candidate basis is complete only because it contains a universal interpreter, return `UNIVERSAL_COMPUTATION_ONLY`.
- If different bases are equivalent but resource overhead differs, retain the Pareto/equivalence result rather than choosing a metaphysical winner.
- If stochastic/probabilistic fixtures require a primitive not derivable at bounded cost, report the obstruction; do not hide stochasticity in an opaque random-program primitive.
- If one basis is selected only after seeing target results, the study becomes exploratory and must be re-frozen.

## No-HPC rule

GMI-D2 is intentionally finite/exact and should run on ordinary hardware. #221/#220 search machinery is not authorized until the exact microscope has established a neutral grammar, equivalence test and nontrivial residual.