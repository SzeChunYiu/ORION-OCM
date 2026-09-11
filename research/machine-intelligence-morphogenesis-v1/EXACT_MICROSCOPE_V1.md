# GMI-D2 Exact Microscope v1

Purpose: calibrate Track-B minimality/equivalence machinery on finite worlds **before** any architecture search or LUNARC campaign.

## Stage A — known-answer Boolean calibration (executed)

Universe:

- all `16` binary Boolean functions on inputs `(x,y)`;
- projections `x,y` are free variables, not counted as primitives;
- primitive catalogue: `NOT, AND, OR, XOR, NAND, NOR`;
- legal construction: functional composition only;
- cost coordinate: minimum expression depth in this first calibration.

Executed result:

```text
54 / 63 subsets are complete at this tiny scope.

Inclusion-minimal complete bases:
  {NAND}       max minimum depth 3
  {NOR}        max minimum depth 3
  {NOT, AND}   max minimum depth 4
  {NOT, OR}    max minimum depth 4
```

This is **not new mathematics**. Post/clone theory and classical functional-completeness results own the underlying Boolean structure. This stage calibrates compensation-aware census machinery only.

Terminal:

`EXACT_BASIS_CENSUS_CALIBRATED_ON_KNOWN_BOOLEAN_SCOPE`

---

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

Terminal:

`CURRENT_BEHAVIOR_EQUIVALENCE_DOES_NOT_IMPLY_DEVELOPMENTAL_EQUIVALENCE_EXACT`

Scientific consequence: morphology equivalence cannot be current I/O behavior alone; registered update/development behavior must be part of the relation.

Artifacts:

```text
developmental_equivalence_witness.py
test_developmental_equivalence_witness.py
EXACT_DEVELOPMENTAL_EQUIVALENCE_V1.json
```

Claim boundary: finite exact counterexample only.

---

## Stage C-v0 — one-bit adaptive Boolean basis census (executed)

This stage extends the calibration from static Boolean functions to tiny adaptive transducers while deliberately remaining exact.

A morphology is:

```text
one-bit state s
one-bit input x
one-bit supervised label l

output  f(s,x)   -> y
update  g(s,x,l) -> s'
initial state s=0
```

Both `f` and `g` are composed from subsets of:

```text
NOT, AND, OR, XOR, NAND, NOR
```

No `LEARN`, `NEURON`, `BACKPROP`, `BAYES_UPDATE`, `PRODUCTION_RULE`, `PROGRAM_INTERPRETER` or other architecture-labelled primitive exists.

Developmental signatures are computed exactly over every supervised history of length `<=2`, followed by both probe inputs.

Executed exact result:

```text
basis subsets enumerated                  63
complete basis subsets                    54
full (f,g) morphology universe          4096
current-behavior classes at s=0            4
developmental classes (history <=2)     2884
```

Inclusion-minimal complete bases remain:

```text
{NAND}
{NOR}
{NOT, AND}
{NOT, OR}
```

Registered compilation-depth results over the complete adaptive universe:

```text
{NAND}       mean depth(f)+depth(g) = 5.47265625   max = 8
{NOR}        mean depth(f)+depth(g) = 5.47265625   max = 8
{NOT,AND}    mean depth(f)+depth(g) = 6.14062500   max = 10
{NOT,OR}     mean depth(f)+depth(g) = 6.14062500   max = 10
```

Within the registered six-gate catalogue the lowest mean complete-basis compilation depth is achieved by a richer basis including `{AND, OR, XOR, NAND, NOR}`:

```text
mean depth sum = 3.43359375
max depth sum  = 5
```

### What Stage C-v0 establishes

1. **Developmental equivalence is much finer than current behavior** in this finite fixture: `2884` developmental classes versus only `4` current behavior classes.
2. **Primitive cardinality is not resource optimality**: a minimal-cardinality complete basis can require deeper compilation than a richer basis.
3. Exact developmental/resource census is tractable enough to calibrate before heuristic architecture search.

### What it does NOT establish

The functional-completeness core is still ordinary Boolean clone/Post mathematics. The adaptive result composes two Boolean maps; therefore this is not evidence that Boolean connectives are a machine-intelligence atom.

Terminal:

`ADAPTIVE_BOOLEAN_BASIS_CENSUS_EXACT__PARENT_MATHEMATICS_DOMINATES`

Artifacts:

```text
adaptive_boolean_basis_census.py
test_adaptive_boolean_basis_census.py
EXACT_ADAPTIVE_BOOLEAN_CENSUS_V1.json
```

This is a scientifically useful negative/subtraction result: **the naive adaptive-Boolean route is too close to mature functional-completeness mathematics to carry the general-intelligence novelty. Move upward.**

---

## Stage C-v1 — structured adaptive basis beyond clone-theory calibration (next)

The next exact grammar must introduce structure that is not exhausted by simply choosing two arbitrary Boolean functions.

Candidate low-level components, frozen before outcome:

```text
typed local state
explicit read/write state operation
message/pass value
conditional composition
bounded local update of a parameter/state coordinate
explicit topology add/remove in a separate arm
explicit stochastic choice in a separate arm
resource meter
```

Do **not** include architecture labels:

```text
NEURON
PRODUCTION_RULE
BAYES_UPDATE
PROGRAM_INTERPRETER
ATTENTION
BACKPROP
```

### Required attacks

- compare against a plain Moore/coalgebraic-state-machine parent;
- compare against program/universal-interpreter encodings;
- quotient exact current behavior;
- quotient exact developmental behavior;
- compensation-aware primitive removal;
- vary resource prices so primitive rank and resource rank can disagree;
- separate on-unit adaptation from externally applied update laws;
- deterministic and explicit-stochastic arms;
- no-learning/static control;
- exhaustive enumeration before heuristic search wherever feasible.

Possible terminals:

```text
STRUCTURED_ADAPTIVE_BASIS_RESIDUAL_AT_SCOPE
MULTIPLE_EQUIVALENT_ADAPTIVE_BASES_AT_SCOPE
PARENT_FORMALISM_SUFFICIENT
UNIVERSAL_COMPUTATION_ONLY
NO_SMALL_CROSS_PARADIGM_BASIS
NON_IDENTIFIABLE_AT_CURRENT_RESOLUTION
```

---

## Stage D — known-form micro-derivations

Only after Stage C-v1 is frozen and interpretable, construct tiny targets from different paradigms:

1. 2–3 unit neural/threshold computation plus one update step;
2. finite production/rewrite learner;
3. tiny stochastic/Bayesian update fixture;
4. tiny explicit program/library learner;
5. one simple hybrid statistical + exact-check fixture.

The same frozen basis should reproduce **behavior + registered update law** without architecture-labelled macros. Record D0 representability, D1 compilation resources and eventually D2 acquisition.

---

## Stage E — exact developmental-frontier calibration

After known-form micro-derivations exist, vary at least two ecology coordinates and compute complete finite frontiers.

Candidate axes:

```text
reuse horizon
revision frequency
noise / stochasticity
exact-verification requirement
```

Freeze phase-crossing predictions on development worlds, then test them on disjoint tiny worlds.

This is the first exact test of `DEVELOPMENTAL_FRONTIER_V1.md` rather than a post-hoc explanation.

---

## Adoption/kill rules

- Universal interpreter success alone -> `UNIVERSAL_COMPUTATION_ONLY`.
- Generic local state-machine success already captured by coalgebra/dynamical parents with no residual -> `PARENT_FORMALISM_SUFFICIENT`.
- Boolean functional-completeness/minimal-basis results -> parent mathematics/calibration, not GMI novelty.
- Different bases equivalent but resource-ranked differently -> preserve Pareto/equivalence result; do not force a metaphysical winner.
- Stochastic fixture needs irreducible stochastic primitive at registered bound -> report obstruction, do not hide randomness in opaque code.
- Basis chosen after target results -> exploratory only; re-freeze.
- Phase regions explained after outcome -> no phase-law credit.

## No-HPC rule

GMI-D2 remains finite/exact and runs on ordinary hardware. #221/#220 search machinery is not authorized until the structured grammar, equivalence test and nontrivial residual survive these microscopes.
