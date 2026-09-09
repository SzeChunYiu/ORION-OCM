# G2 macro-operator serving study v1

**Status:** prospectively frozen successor to #189/#191 for #165 G2.4 / #62.  
**Claim ceiling:** bounded causal method reuse in one exact polynomial ecology.

## Why this successor is scientifically distinct

The existing fixed-fragment learner is no longer the only diagnosed problem.

- #189: one frequency-selected fragment was broadly harmful under the current alternate-baseline serving schedule.
- #191: exact utility selection among the top 16 training-derived fixed fragments still selected **no method**; every candidate lost aggregate validation search work.

However, individual fragments still produced strict guided wins on some tasks. The common failure mode is that the current serving policy launches a separate guided enumeration and alternates it with primitive search, imposing search overhead on unrelated tasks.

This v1 changes **serving representation**, not the exposed #189/#191 populations:

> a selected learned fragment becomes one macro/operator token in the same exact search grammar, so one macro decision may expand to multiple primitive instructions.

This is standard library/macro search, not an OCM novelty claim. Stitch/DreamCoder/program-library learning remain strong conceptual parents.

## Immutable task grammar and verifier

Underlying semantics remain exactly the repository's registered polynomial domain:

```text
inc
dec
double
square
```

Exact task identity is polynomial normal form. Exact correctness is checked with the existing `normal_form` / polynomial identity machinery from:

```text
src/ocm/learning/methods.py
blob 50323a33418b8ef8bb6500ddeba4b9d1f795e9e3
```

No production source changes.

## Fresh prospective populations

Enumerate all exact polynomial identities reachable by primitive programs through length 8 and assign minimum primitive program length.

### Training

- minimum primitive length exactly 6;
- salt `orion-ocm-g2-macro-training-v1`;
- first **48** identities;
- exact primitive solver, `max_length=6`.

### Validation

- minimum primitive length exactly 7;
- salt `orion-ocm-g2-macro-validation-v1`;
- first **32** identities.

### Test

- minimum primitive length exactly 8;
- salt `orion-ocm-g2-macro-test-v1`;
- first **64** identities.

All three strata are disjoint by minimum primitive length. Salts/counts are immutable after the first result.

## Frozen candidate construction

From each exactly verified training program, enumerate every proper contiguous fragment of primitive length 2 through 4.

Support = number of distinct mathematical training tasks containing the fragment.

Keep support >= 2, order by:

```text
-support
-fragment length
lexicographic fragment
```

Take the first **16** candidates.

Validation/test outcomes cannot create or reorder candidates.

## Exact macro grammar

For candidate fragment `f`, define tokens:

```text
MACRO_f
inc
dec
double
square
```

`MACRO_f` expands exactly to primitive sequence `f` before verification.

Search is breadth-first by **token count**. Within a token depth, token order is exactly the list above. Prefixes whose expanded primitive length already exceeds the registered maximum are pruned before descendants are generated.

Every complete token word generated within the primitive-length bound counts one `enumeration_attempt`, including words whose expanded primitive program duplicates an earlier word. Exact polynomial checking is performed only for the first occurrence of each expanded primitive program; `unique_candidates_checked` is reported separately.

This prevents duplicate tokenizations or macro expansion work from becoming free.

The primitive parent is the same algorithm with tokens:

```text
inc
dec
double
square
```

so it reduces to ordinary breadth-first primitive enumeration.

## Frozen utility selection

Run primitive macro-search once on all 32 validation tasks.

Run each of the 16 single-macro candidates on all 32 validation tasks.

Choose the candidate with minimum aggregate `enumeration_attempts`, ties broken by the frozen candidate order.

Deploy only if:

```text
candidate aggregate enumeration_attempts
<
primitive aggregate enumeration_attempts
```

Otherwise select no method and terminate:

```text
MACRO_TOURNAMENT_SELECTS_NO_METHOD
```

No per-task router, allow-list, post-hoc token cost, or test-informed threshold.

## Test arms

1. `PRIMITIVE`
   - primitive-token grammar only.

2. `ORDINARY_PERSISTENT`
   - selected macro stored/reloaded from ordinary atomic JSON;
   - same macro grammar.

3. `OCM_LIVE`
   - selected macro represented as a procedure object supported by frozen training-selection and validation-utility evidence;
   - persist/restart before test;
   - same macro grammar.

4. `OCM_REVOKED`
   - revoke training-selection evidence before persistence/restart;
   - method must become non-live;
   - test reduces exactly to primitive grammar.

The ordinary parent receives the identical selected macro and exact search algorithm.

## Actual-use witness

For each solved task record:

- token word;
- expanded primitive program;
- `macro_used` boolean;
- enumeration attempts;
- unique candidates checked;
- exact verification.

A learned-method win requires:

```text
macro_used == true
AND
candidate enumeration_attempts < primitive enumeration_attempts
```

Persistence without macro use is not reuse evidence.

## Positive terminal

```text
CAUSAL_MACRO_OPERATOR_REUSE_SUPPORTED_AT_LENGTH8
```

requires all:

- macro selected by the frozen validation rule;
- exact success on every test task;
- at least one strict test win with `macro_used=true`;
- aggregate OCM test enumeration attempts < primitive;
- ordinary persistent == OCM live task-by-task;
- revoked OCM == primitive task-by-task;
- fresh runtime reconstruction before test.

This would establish bounded causal method reuse under a conventional macro-serving mechanism. It would not establish an OCM-specific architecture residual.

## Cost accounting

Keep separately:

- training primitive search attempts;
- primitive validation attempts;
- all candidate validation attempts;
- validation unique checks;
- test attempts;
- test unique checks;
- candidate mining work;
- wall/CPU/RSS.

A separate search-work lifetime terminal includes **all candidate-selection work**:

```text
LIFETIME_MACRO_SEARCH_PAYBACK_AT_64_LENGTH8_TESTS
NO_LIFETIME_MACRO_SEARCH_PAYBACK_AT_64_LENGTH8_TESTS
```

Whole-resource architecture net benefit remains outside this study.

## Frozen negative terminals

```text
NO_REPEATED_MACRO_CANDIDATES
MACRO_TOURNAMENT_SELECTS_NO_METHOD
NO_CAUSAL_MACRO_CONSUMPTION
NO_AMORTIZED_MACRO_SEARCH_ON_LENGTH8_TEST
CANNOT_CHECK_COMPONENT_TRANSPLANT_PARITY
CANNOT_CHECK_REVOCATION_ABLATION
```

## Freeze / successor rule

After the first result, do not change task salts/counts, candidate cap/support threshold, macro lengths, token order, pruning rule, attempt accounting, selection objective, or test population to rescue v1.

If negative, fixed contiguous fragments + exact macro serving are closed at this ecology. The next G2 mechanism must use **richer abstraction construction** (faithful Stitch/library learning, anti-unification/parameterized schemas, or another prospectively justified representation) on a new population.
