# GMI-D2 Exact Microscope v1

Purpose: calibrate Track-B minimality/equivalence machinery on finite worlds **before** any architecture search or LUNARC campaign.

## Stage A — known-answer Boolean calibration (executed)

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

## Stage B — developmental-equivalence counterexample (executed)

Fixture:

```text
registered input universe = {0,1}
initial current behavior for both machines = [0,0]
shared experience = supervised event (x=1, label=1)

M_static:
  update rule = NO_OP
  post-experience behavior = [0,0]

M_adaptive:
  update rule = SUPERVISED_MEMORIZE
  post-experience behavior = [0,1]
```

Before the event the machines are extensionally identical on **every input in the complete registered universe**. After the same event they diverge because their update laws differ.

This is an exact finite witness for:

```text
CURRENT_BEHAVIOR_EQUIVALENCE
  does not imply
DEVELOPMENTAL_EQUIVALENCE
```

Artifacts:

```text
developmental_equivalence_witness.py
test_developmental_equivalence_witness.py
EXACT_DEVELOPMENTAL_EQUIVALENCE_V1.json
```

Terminal:

`CURRENT_BEHAVIOR_EQUIVALENCE_DOES_NOT_IMPLY_DEVELOPMENTAL_EQUIVALENCE_EXACT`

Claim boundary: finite exact counterexample only; not a universal taxonomy of intelligence morphologies.

## Stage C — tiny typed adaptive bases (next decisive exact work)

Register a finite grammar containing only low-level typed primitives such as:

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

### Stage-C design constraints added by the second hardening pass

- treat a plain Moore/coalgebraic state machine as a **parent**, not Track-B novelty;
- keep local transition semantics separate from update-of-transition/topology semantics;
- include a no-learning/static control;
- include one ecology where current behavior is identical but future update utility differs;
- include resource price variants so basis rank and resource rank can disagree;
- keep stochasticity in an explicit arm rather than hiding it in an opaque universal interpreter;
- exhaust tiny spaces before using heuristic search.

## Stage D — known-form micro-derivations

Only after Stage C is stable, construct tiny target instances from different paradigms:

1. a 2–3 unit feedforward threshold/neural computation;
2. a finite production/rewrite controller;
3. a tiny stochastic/Bayesian update fixture;
4. a tiny explicit program/library learner.

The goal is not to prove general derivability yet. The question is whether the same frozen basis can reproduce the **behavior + registered update law** without architecture-labelled macros and at what cost.

## Stage E — developmental frontier calibration

After known-form micro-derivations exist, vary at least two ecology coordinates and test whether the complete finite Pareto frontier changes membership between registered morphology classes.

Possible tiny axes:

```text
reuse horizon
revision frequency
noise / stochasticity
exact-verification requirement
```

This is the first finite setting in which `DEVELOPMENTAL_FRONTIER_V1.md` can be attacked exactly rather than only discussed conceptually.

## Adoption/kill rules

- If every candidate basis is complete only because it contains a universal interpreter, return `UNIVERSAL_COMPUTATION_ONLY`.
- If a “local adaptive transducer” result is already exactly captured by standard coalgebra/dynamical-system formalisms and no developmental/resource residual remains, return `PARENT_FORMALISM_SUFFICIENT`.
- If different bases are equivalent but resource overhead differs, retain the Pareto/equivalence result rather than choosing a metaphysical winner.
- If stochastic/probabilistic fixtures require a primitive not derivable at bounded cost, report the obstruction; do not hide stochasticity in an opaque random-program primitive.
- If one basis is selected only after seeing target results, the study becomes exploratory and must be re-frozen.
- If phase regions are explained only after outcomes, no phase-law credit is earned.

## No-HPC rule

GMI-D2 is intentionally finite/exact and should run on ordinary hardware. #221/#220 search machinery is not authorized until the exact microscope has established a neutral grammar, equivalence test and nontrivial residual.
