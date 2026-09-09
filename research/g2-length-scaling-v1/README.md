# G2 length-scaling causal-reuse study v1

**Status:** prospectively frozen development study for #165 G2.4 / #62.  
**Claim ceiling:** bounded causal method reuse in this registered polynomial ecology only.

## Why this study exists

Two existing development controls are retained unchanged:

1. the ordinary-cut Metamath lane now has natively verified non-alias lemmas but no
   demonstrated fresh held-out utility under one-step, REFACTOR/GetSteps, or bounded
   two-decision consumers;
2. the exposed native polynomial pilot found that the existing fragment learner
   increased aggregate search work on a short length-≤4 future tape even though its
   two declared validation tasks were positive.

Those negatives are not discarded. This study asks a different, prospectively
registered phase question:

> Does the same already-existing fragment learner become causally useful when the
> future task family requires strictly longer primitive programs, and can a broader
> pre-deployment utility gate distinguish whether the learned library should be used?

The longer family is motivated before outcomes by the method's mechanism: a
multi-instruction fragment can only repay its search-order overhead when future
tasks contain enough compositional depth for the fragment to replace repeated
primitive enumeration.

## Immutable mechanism

No production learner, solver, checker, KSO warrant rule, or OCM runtime logic is
changed.

Source under test:

- `src/ocm/learning/methods.py`
- required Git blob: `50323a33418b8ef8bb6500ddeba4b9d1f795e9e3`

The exact learner remains `learn_generator`.
The exact solver remains `solve`.
The exact checker remains `verify_solution`.
The OCM arm uses the existing `admit_generator`, `persist`, process reconstruction,
`load_generator`, and `revoke` lifecycle.

The conventional parent receives the **same learned method and same utility gate**.
This study cannot support an architecture-uniqueness claim.

## Frozen acquisition data

Training remains exactly:

- coefficients `(2, 2, 1)`
- coefficients `(2, 4, 2)`

The existing two-task admission check remains exactly:

- coefficients `(0, 2, 1)`
- coefficients `(1, 4, 6, 4, 1)`

These are inherited exposed development data. They are not new evidence.

## Frozen population construction

Task identity is the exact polynomial coefficient tuple.

Enumerate all programs over:

```text
inc
dec
double
square
```

through primitive length 6. Deduplicate by polynomial identity and assign each
identity its **minimum primitive program length**.

No solve outcome participates in population construction.

### Utility-validation family

- minimum primitive length exactly 5;
- exclude acquisition/admission identities;
- rank only by `SHA256("orion-ocm-g2-length5-validation-v1" || NUL || fingerprint)`;
- take the first **32** identities.

### Test family

- minimum primitive length exactly 6;
- exclude acquisition/admission identities;
- rank only by `SHA256("orion-ocm-g2-length6-test-v1" || NUL || fingerprint)`;
- take the first **64** identities.

The validation and test families are disjoint by construction. Once the first
result exists, these salts, counts, grammar, length strata, budgets, and identities
must not be changed in v1.

## Frozen utility gate

On all 32 length-5 validation tasks, run:

```text
primitive solver
vs
same solver + learned fragments
```

with:

```text
slots      = 200000
max_length = 5
```

The deployment rule is fixed before test outcomes:

```text
ACCEPT iff
sum(candidate search slots over all 32 tasks)
<
sum(primitive search slots over all 32 tasks)
```

All tasks must still pass the exact checker.

No per-task cherry-picking, query router, task-specific allow-list, or post-hoc
threshold is permitted.

The gate records harmful tasks, strict improvements, and successful programs even
when the aggregate result is negative.

## Frozen test arms

All 64 length-6 test tasks use:

```text
slots      = 200000
max_length = 6
```

Arms:

1. `PRIMITIVE`
   - no learned fragments.

2. `ORDINARY_PERSISTENT`
   - identical `learn_generator`;
   - identical 32-task utility gate;
   - atomic JSON persistence and reload before test.

3. `OCM_LIVE`
   - existing OCM method admission;
   - utility-gate evidence recorded;
   - persist and reconstruct runtime before test;
   - learned generator used only if the frozen utility gate accepts it.

4. `OCM_REVOKED`
   - same acquisition/admission work;
   - one indispensable training support is revoked before restart;
   - `load_generator` must fail closed;
   - test falls back to the primitive solver.

`OCM_REVOKED` is the preplanned causal ablation. It is not selected after seeing
which tasks benefit.

## Actual-use attribution

The research runner wraps, but does not replace, the two existing candidate
generators used by `solve`:

- `_primitive_programs`
- `_guided_programs`

It records which stream first emitted the eventually verified solution program.

A task counts as an actual learned-method win only if:

```text
candidate slots < primitive slots
AND
winning program first came from the guided stream
```

Merely having a non-empty method library does not count as use.

## Required equalities

Before a positive causal terminal:

- every result must pass `verify_solution`;
- `ORDINARY_PERSISTENT` and `OCM_LIVE` must have identical test programs/slot counts
  when both deploy the same method;
- `OCM_REVOKED` must equal `PRIMITIVE` task-by-task after support withdrawal;
- at least one strict OCM improvement must be attributed to the guided stream;
- OCM total test search slots must be lower than primitive total test search slots.

## Search-slot accounting

The result keeps separate:

- acquisition slots;
- inherited two-task admission-validation slots;
- broad 32-task utility-validation slots for both arms;
- 64-task test slots.

Two conclusions are distinct:

### Causal search reuse

```text
CAUSAL_METHOD_REUSE_SUPPORTED_AT_LENGTH6
```

requires actual guided-stream wins + lower aggregate test search work + successful
revocation ablation.

### Registered-horizon search-slot payback

```text
LIFETIME_SEARCH_SLOTS_PAYBACK_AT_64_TEST_TASKS
```

requires test savings to repay acquisition and all validation search slots.

This is **search-slot accounting only**. CPU, wall time, storage, provenance,
checkpoint/replay, and custody remain separate coordinates and no
whole-architecture net-benefit claim is licensed here.

## Frozen terminals

```text
CAUSAL_METHOD_REUSE_SUPPORTED_AT_LENGTH6
UTILITY_GATE_REJECTS_METHOD
NO_CAUSAL_METHOD_CONSUMPTION
NO_AMORTIZED_SEARCH_ON_LENGTH6_TEST
CANNOT_CHECK_REVOCATION_ABLATION
CANNOT_CHECK_COMPONENT_TRANSPLANT_PARITY

LIFETIME_SEARCH_SLOTS_PAYBACK_AT_64_TEST_TASKS
NO_LIFETIME_SEARCH_SLOTS_PAYBACK_AT_64_TEST_TASKS
```

A negative terminal closes this ecology cleanly. Do not retune v1 after the first
test result. A materially changed learner, grammar, utility estimator, task
distribution, or search policy requires a new version with a new prospective
registration.

## Relation to programme closure

A positive result would discharge the missing **G2.4 causal-use mechanism at one
bounded domain/scope**, not G3, cross-domain transfer, developmental evolvability,
or architecture net benefit.

A negative result is also decisive: it says the current native fragment learner +
utility gate does not earn causal reuse in this registered length-scaling ecology,
and the programme should move to a different acquisition mechanism rather than
continue tuning this one against the same test family.
