# G2 utility-aware fragment tournament v1

**Status:** prospectively frozen research successor to #189 for #165 G2.4 / #62.  
**Claim ceiling:** bounded causal method reuse in this registered polynomial ecology only.

## Motivation fixed before outcomes

Two prior results are retained, not overwritten:

1. the original native `learn_generator` learned a real fragment but increased aggregate future search work on the short polynomial lifetime;
2. prospectively frozen #189 expanded the ecology to minimum-length 5 validation / length 6 test and returned `UTILITY_GATE_REJECTS_METHOD`: the inherited `inc -> square` fragment helped only 2/32 validation tasks and harmed 30/32.

Therefore the next causal question is not whether OCM can persist a method. That is already engineering-qualified. The open question is whether **candidate generation/selection** can produce a method with prospective downstream utility.

This study changes the acquisition rule, not #189's exposed task identities. It moves to fresh complexity strata and fresh hash salts.

## Strong-parent doctrine

The mechanism is deliberately conventional and transparent:

```text
training solutions
-> repeated proper fragments
-> bounded candidate pool
-> exact with-vs-without validation tournament
-> choose one fragment or choose no method
```

This is a Minton-style utility-selection parent adapted to the repository's exact search-slot metric. It is not claimed as OCM novelty.

The existing Stitch adapter (`research/ocm-prototype/generation_stitch.py`) remains the next library-learning donor comparison. It is not used as the decisive consumer here because its current CLIA/cvc5 route still reports `CANNOT_CHECK_CONSUMPTION`: submitted grammar is not native learned-production use evidence. A positive or negative result here therefore does not subtract Stitch/DreamCoder-class abstraction learning.

## Immutable production mechanism

No production code changes.

Pinned source:

```text
src/ocm/learning/methods.py
blob 50323a33418b8ef8bb6500ddeba4b9d1f795e9e3
```

Reuse exactly:

- `PolynomialTask`
- `SearchBudget`
- `GeneratorMethod`
- `solve`
- `verify_solution`
- primitive and guided search schedule
- exact polynomial normal form
- `OCMRuntime` persistence/restart/revocation semantics

The study adds only a research-side candidate miner, exact selector, and generic research admission adapter for the selected `GeneratorMethod`.

## Frozen task universe

Enumerate all primitive programs over:

```text
inc
dec
double
square
```

through primitive length 7. Deduplicate by exact polynomial identity. Each task receives its **minimum primitive program length** based only on the mathematical identity.

Acquisition/validation/test partitions are separated by minimum length, so they cannot share task identities.

### Training family

- minimum primitive length exactly 5;
- sort by `SHA256("orion-ocm-g2-utility-training-v1" || NUL || fingerprint)`;
- first **48** identities;
- primitive solve only;
- budget `slots=200000, max_length=5`.

### Utility-selection family

- minimum primitive length exactly 6;
- salt `orion-ocm-g2-utility-validation-v1`;
- first **32** identities;
- budget `slots=200000, max_length=6`.

### Test family

- minimum primitive length exactly 7;
- salt `orion-ocm-g2-utility-test-v1`;
- first **64** identities;
- budget `slots=200000, max_length=7`.

These salts, sizes, strata, grammar and budgets are immutable after the first result.

## Frozen candidate generation

For each exactly verified training solution, enumerate every **proper contiguous fragment** of length 2 through 4.

Support is the number of distinct mathematical training tasks whose verified solution contains the fragment at least once.

Keep candidates with support >= 2.

Sort by:

```text
-support
-length
lexicographic fragment
```

Take the first **16** candidates.

This is candidate generation from training only. Validation and test tasks cannot create, reorder or enlarge the candidate pool.

If fewer than one candidate survives, terminal:

```text
NO_REPEATED_FRAGMENT_CANDIDATES
```

## Frozen utility tournament

Compute the primitive baseline once over all 32 utility-selection tasks.

For each candidate fragment `f`, construct:

```text
GeneratorMethod(fragments=(f,), training_tasks=<48 frozen training ids>)
```

Run the unchanged exact solver on all 32 utility tasks.

Record:

- aggregate candidate slots;
- aggregate baseline slots;
- strict improvements;
- harmful tasks;
- guided-stream strict wins;
- every verified program;
- candidate support.

Candidate ordering cannot depend on test results.

### Selection rule

Choose the candidate with minimum aggregate validation slots.

Ties are broken by the already-frozen candidate order.

Deploy the selected candidate only if:

```text
selected aggregate validation slots
<
primitive aggregate validation slots
```

Otherwise choose **no method** and terminal:

```text
UTILITY_TOURNAMENT_SELECTS_NO_METHOD
```

No per-task allow-list, learned router, task-specific gate, post-hoc price, or test-aware threshold is permitted.

## Test arms

1. `PRIMITIVE`
   - unchanged exact primitive solver.

2. `ORDINARY_PERSISTENT`
   - exact same selected `GeneratorMethod`;
   - atomic JSON persist/reload before the test;
   - no OCM epistemic machinery.

3. `OCM_LIVE`
   - research adapter admits a training-selection receipt and validation-utility receipt as explicit evidence;
   - selected method becomes a procedure object supported by both;
   - persist;
   - reconstruct a fresh `OCMRuntime` process object;
   - load method from the live procedure object;
   - run the same exact solver.

4. `OCM_REVOKED`
   - same selected method and evidence construction;
   - revoke the training-selection evidence before persistence/restart;
   - loader must refuse the method;
   - test falls back to primitive search.

The ordinary arm receives the same fragment, same search schedule and same selection rule. OCM has no exclusive algorithmic information.

## Actual-use attribution

As in #189, the research runner wraps the existing primitive/guided generators only to record which stream first emitted the verified winning program.

A task counts as a learned-method win only if:

```text
selected slots < primitive slots
AND
winning program first appeared in the guided stream
```

A persisted method that is never invoked is not reuse evidence.

## Positive G2 terminal

```text
CAUSAL_UTILITY_SELECTED_METHOD_REUSE_SUPPORTED_AT_LENGTH7
```

requires all:

- selected method passed the frozen length-6 aggregate utility rule;
- exact verification on every test task;
- at least one guided-stream strict test win;
- aggregate selected-method test slots < aggregate primitive test slots;
- ordinary persistent and OCM live are task-by-task identical;
- revoked OCM is task-by-task identical to primitive;
- fresh OCM runtime reconstruction occurred before test.

This establishes bounded causal reuse of an acquired, prospectively selected method. It does **not** establish architecture uniqueness or whole-lifetime net benefit.

## Lifetime search-slot accounting

Keep separate:

- training primitive solve slots;
- baseline validation slots;
- **all 16 candidate validation slots** (candidate-selection cost);
- test slots;
- candidate mining CPU/wall separately where available.

A separate terminal:

```text
LIFETIME_SEARCH_SLOTS_PAYBACK_AT_64_LENGTH7_TESTS
```

requires the selected path's training + full tournament + test search slots to be lower than the primitive test-only comparator over the registered horizon.

Otherwise:

```text
NO_LIFETIME_SEARCH_SLOTS_PAYBACK_AT_64_LENGTH7_TESTS
```

This intentionally makes the candidate tournament pay its search cost. Search-slot payback is not a whole-resource claim.

## Frozen negative terminals

```text
NO_REPEATED_FRAGMENT_CANDIDATES
UTILITY_TOURNAMENT_SELECTS_NO_METHOD
NO_CAUSAL_METHOD_CONSUMPTION
NO_AMORTIZED_SEARCH_ON_LENGTH7_TEST
CANNOT_CHECK_COMPONENT_TRANSPLANT_PARITY
CANNOT_CHECK_REVOCATION_ABLATION
```

Any negative closes v1. Do not rescue it by changing salts, counts, candidate cap, support threshold, fragment lengths, budgets or test distribution after the first result.

## Successor rule

If v1 is negative, the next G2 mechanism must be qualitatively stronger candidate construction, such as:

- faithful Stitch/library learning;
- anti-unification / parameterized abstraction;
- program-library search with utility in the objective;
- a representation change that lets learned methods replace rather than merely reorder primitive search.

It must use a new prospective population.

If v1 is positive, G2 can advance to replication / G3 composition while strongest-parent subtraction continues.
