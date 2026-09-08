# G3 independent learned-method composition v1

**Status:** prospectively frozen successor to bounded G2 positive #192.  
**Owners:** #165 G3.1, #62, #143.  
**Claim ceiling:** bounded causal composition of independently acquired exact methods in one polynomial domain.

## Starting evidence

G2 is now positive at one bounded exact scope:

```text
CAUSAL_MACRO_OPERATOR_REUSE_SUPPORTED_AT_LENGTH8
```

The selected macro in #192 survived OCM restart, was actually used on fresh tasks,
reduced aggregate test search work, and exact support withdrawal removed the
advantage. The identical ordinary persistent macro parent tied OCM task-by-task,
so macro/library search remains parent-owned.

G3 asks the next causal question:

> Can two methods learned independently from disjoint evidence be retained
> simultaneously and naturally compose on untouched tasks that were **not built
> to contain those methods**?

## No manufactured A+B tasks

This study deliberately does **not** generate a test task by concatenating the
learned macros after seeing them.

Instead:

- method A is selected on one frozen train/validation ecology;
- method B is selected independently on a disjoint frozen train/validation ecology;
- a generic hash-ranked population of minimum-primitive-length-8 tasks is frozen
  before outcomes;
- composition counts only if exact search on that generic population naturally
  uses both `MACRO_A` and `MACRO_B` and each single-method ablation is worse on
  the same task.

This can legitimately return `NO_FRESH_COMPOSITION_DEMAND`.

## Reused mechanism and source custody

The exact single-macro acquisition/serving mechanism is inherited unchanged from
merged #192:

```text
research/g2-macro-operator-v1/experiment.py
Git blob 4c8cb45c182f12a5e09db873fb7625dc37dbf599
```

Production polynomial semantics remain pinned to:

```text
src/ocm/learning/methods.py
Git blob 50323a33418b8ef8bb6500ddeba4b9d1f795e9e3
```

This study reuses:

- exact primitive training solve;
- proper contiguous fragment candidate construction;
- support >= 2;
- top-16 candidate order;
- exact one-macro validation tournament;
- exact macro expansion / verification;
- KSO evidence-backed procedure admission;
- persistence/restart/revocation semantics.

No production code changes.

## Prior exposed polynomial identities are excluded

To avoid silently reusing task outcomes from #189/#191/#192, the registered
partition reconstructs and excludes their hash-selected identities at each
relevant minimum-length stratum.

### Previously exposed minimum-length-6 identities excluded from G3 training

- #189 length-6 test: 64 identities;
- #191 length-6 validation: 32 identities;
- #192 length-6 training: 48 identities.

### Previously exposed minimum-length-7 identities excluded from G3 validation

- #191 length-7 test: 64 identities;
- #192 length-7 validation: 32 identities.

### Previously exposed minimum-length-8 identities excluded from G3 composition test

- #192 length-8 test: 64 identities.

Exclusion uses only the prior published salts/counts and exact task identity.

## Frozen independent acquisition lanes

### Method A training

- minimum primitive length exactly 6;
- salt `orion-ocm-g3-a-training-v1`;
- first **48** non-exposed identities.

### Method B training

- minimum primitive length exactly 6;
- salt `orion-ocm-g3-b-training-v1`;
- first **48** identities excluding prior exposure **and A training**.

### Method A validation

- minimum primitive length exactly 7;
- salt `orion-ocm-g3-a-validation-v1`;
- first **32** non-exposed identities.

### Method B validation

- minimum primitive length exactly 7;
- salt `orion-ocm-g3-b-validation-v1`;
- first **32** identities excluding prior exposure **and A validation**.

Each lane independently runs the #192 candidate miner and exact one-macro
validation tournament.

No diversity constraint is imposed.

If either lane selects no macro:

```text
NO_INDEPENDENT_METHOD_PAIR
```

If both lanes independently select the same primitive fragment:

```text
NO_DISTINCT_METHOD_PAIR
```

Do not choose a second-best fragment to rescue composition.

## Frozen generic composition test

- minimum primitive length exactly 8;
- exclude #192 test identities;
- salt `orion-ocm-g3-composition-test-v1`;
- first **256** identities.

The test identities are fixed by exact mathematics + salt only. They do not
depend on A/B outcomes.

## Exact two-macro search grammar

When both methods exist, the full library tokens are:

```text
MACRO_A
MACRO_B
inc
dec
double
square
```

Token order is frozen as written.

Each macro expands exactly to its independently selected primitive fragment.
Search is breadth-first by token count with the same expanded-primitive-length
pruning and duplicate-tokenization charging rule as #192.

Ablation grammars preserve global label order:

```text
A-only:  MACRO_A, primitives
B-only:  MACRO_B, primitives
none:    primitives
```

## Required composition witness

A fresh test task counts as a **strong A+B composition witness** only if all are
true:

```text
winning full-library token word uses MACRO_A
winning full-library token word uses MACRO_B
full attempts < A-only attempts
full attempts < B-only attempts
full attempts < primitive attempts
exact expanded program verifies
```

Merely invoking both macros is insufficient if either method is unnecessary.

## Persistent causal arms

### Ordinary parent

Persist the selected pair in ordinary atomic JSON, reload before test, then run
the exact two-macro grammar.

### OCM full

Admit A and B as **separate procedure objects**, each with its own independent
training-selection and validation-utility evidence. Persist and reconstruct a
fresh runtime before test.

### OCM revoke A

Revoke A's indispensable training evidence before persistence/restart. Loader
must expose B only. Its search must equal the ordinary B-only grammar task-by-task.

### OCM revoke B

Symmetric; must equal ordinary A-only.

### OCM revoke both

Must equal primitive task-by-task.

This makes local method identity and causal removal explicit.

## Positive terminal

```text
METHOD_COMPOSITION_SUPPORTED_AT_SCOPE
```

requires:

- A and B both independently selected by their frozen validation rules;
- A != B;
- at least one strong A+B composition witness in the 256 generic held-out tasks;
- ordinary full library == OCM full task-by-task;
- OCM revoke A == B-only task-by-task;
- OCM revoke B == A-only task-by-task;
- OCM revoke both == primitive task-by-task;
- fresh runtime reconstruction before test;
- exact verification everywhere.

No aggregate whole-population win is required for the **mechanism** terminal, but
all aggregate search/check costs are reported.

A separate endpoint records whether the full two-macro library improves aggregate
test search work versus primitive.

## Frozen negative terminals

```text
NO_INDEPENDENT_METHOD_PAIR
NO_DISTINCT_METHOD_PAIR
NO_FRESH_COMPOSITION_DEMAND
NO_CAUSAL_COMPOSITION_ADVANTAGE
CANNOT_CHECK_COMPOSITION_PARENT_PARITY
CANNOT_CHECK_LOCAL_REVOCATION
```

A negative is a valid G3 result. Do not manufacture A+B tasks or choose second-best
methods after seeing it.

## Cost accounting

Keep separately for A and B:

- training primitive slots;
- primitive validation attempts;
- all candidate validation attempts;
- candidate mining/index wall;
- selected macro identity/support.

For composition test report:

- primitive attempts/checks;
- A-only attempts/checks;
- B-only attempts/checks;
- full-library attempts/checks;
- number of both-used tasks;
- number of strong composition witnesses;
- per-method ablation deltas.

The identical ordinary macro-library parent receives all the same algorithmic
information. A positive G3 mechanism result therefore does not establish an OCM
architecture residual.

## Freeze rule

After the first result, do not alter salts, counts, exposure exclusions,
candidate rules, token order, search accounting, or composition-witness criterion
to rescue v1.
