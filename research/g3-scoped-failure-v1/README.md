# G3 scoped failure knowledge v1

**Status:** prospectively frozen successor to merged #192/#193.  
**Owners:** #165 G3.2, #62, #143.  
**Claim ceiling:** bounded useful method-specific failure memory in one exact polynomial ecology.

## Question

> Can exact failed-use experience become a scoped persistent object that prevents
> repeated wasted method search on fresh task identities without blocking cases
> where the method would have helped?

A failure record here means:

```text
method + task features + scope + resource envelope + search version
-> method was more expensive than the primitive parent
```

It does **not** mean the task is impossible, the theorem is false, or the method
is globally invalid.

## Starting method

Use the already-earned method from prospectively frozen #192:

```text
square -> dec -> square
```

#192 established fresh causal use after restart and exact support-withdrawal
ablation. This study does not relearn or retune that method.

The exact macro-serving implementation is pinned to:

```text
research/g2-macro-operator-v1/experiment.py
blob 4c8cb45c182f12a5e09db873fb7625dc37dbf599
```

The polynomial semantics source remains pinned through that module.

## Strong parents

Failure memory is not an OCM novelty claim. Compare:

1. `ALWAYS_MACRO`
   - use the learned macro on every task.

2. `STATIC_APPLICABILITY`
   - ordinary analytic applicability check from known operator semantics;
   - the macro's exact expansion has minimum output degree 4, so targets of degree
     < 4 use primitive search;
   - otherwise use macro search.

3. `TASK_ID_CACHE`
   - remember exact development task IDs where macro search was harmful;
   - fresh test identities should receive no benefit.

4. `SCOPED_FAILURE_PARENT`
   - same learned scope records as OCM, ordinary JSON persistence.

5. `OCM_SCOPED_FAILURE`
   - same records represented as persistent method-specific constraint objects
     with exact evidence/support and restart.

Any residual must survive the static applicability parent.

## Fresh populations

Use minimum-primitive-length-8 tasks only.

Reconstruct and exclude all previously exposed length-8 identities:

- #192 64-task test;
- #193 256-task generic composition test.

### Development family

- salt `orion-ocm-g3-failure-development-v1`;
- first **128** non-exposed identities.

### Test family

- salt `orion-ocm-g3-failure-test-v1`;
- first **256** identities excluding prior exposure and the development family.

No outcome participates in task selection.

## Exact outcome per task

For each task, using the unchanged #192 search grammar, record:

```text
primitive enumeration_attempts
macro enumeration_attempts
macro_used
verified program
```

Classify only resource effect:

```text
HARMFUL  iff macro_attempts > primitive_attempts
HELPFUL  iff macro_attempts < primitive_attempts
NEUTRAL  iff equal
```

A timeout is not impossibility. This registered finite population is required to
be exactly solved by both search arms.

## Static applicability subtraction

Let:

```text
macro_min_degree = degree(normal_form(square, dec, square)) = 4
```

`STATIC_APPLICABILITY` uses primitive search for target degree < 4 and macro
search otherwise.

Before any learned failure-memory claim, development/test controls must confirm
there is no strict macro win below that bound. If the control fails:

```text
CANNOT_CHECK_STATIC_APPLICABILITY
```

## Frozen pre-search feature families

All features are computed from the target polynomial before search.

Primitive features:

```text
degree
constant_sign          in {-1,0,1}
abs_constant_mod2      in {0,1}
nonzero_coeff_count
```

Candidate scope families, ordered simplest-first for ties:

```text
F1 = (degree)
F2 = (degree, constant_sign)
F3 = (degree, abs_constant_mod2)
F4 = (degree, constant_sign, abs_constant_mod2)
F5 = (degree, nonzero_coeff_count)
F6 = (degree, constant_sign, nonzero_coeff_count)
```

No feature is added after development outcomes.

## Frozen failure-scope induction

Learn only from **statically applicable** development tasks (degree >= 4).

For each feature family and bucket:

- support = number of development tasks in the bucket;
- bucket becomes a failure scope only if support >= **4**;
- every observed task in that bucket must be `HARMFUL`;
- any `HELPFUL` or `NEUTRAL` development task prevents blocking that bucket.

Policy:

```text
if degree < 4:
    primitive            # static parent
elif bucket is learned failure scope:
    primitive
else:
    macro
```

For every feature family compute development aggregate search attempts.

Select the family with the lowest development aggregate attempts; ties use the
frozen F1..F6 order.

Deploy only if it strictly improves on `STATIC_APPLICABILITY` on development and
learns at least one failure scope. Otherwise:

```text
NO_SCOPED_FAILURE_BUCKET
```

## Test conditions

A positive failure-memory result requires all:

```text
at least one fresh test task hits a learned failure scope
SCOPED_FAILURE test attempts < STATIC_APPLICABILITY test attempts
SCOPED_FAILURE test attempts < ALWAYS_MACRO test attempts
zero false blocks
at least one nonblocked fresh task still gets a strict macro win
TASK_ID_CACHE == STATIC_APPLICABILITY on all fresh test identities
```

A **false block** is a fresh test task where the learned scope chooses primitive
but macro search would have been strictly cheaper.

Any false block yields:

```text
HARMFUL_TRANSFER_LIMIT
```

rather than averaging the damage away.

## Persistent failure object

Each learned failure scope is stored separately as a `constraint` atom.

Its metadata includes exactly:

```text
method_fingerprint
macro primitive expansion
feature_family
bucket
resource_metric = enumeration_attempts
search_version = g2.macro-operator.v1
max_primitive_length = 8
support task ids
support count
```

The constraint is backed by exact development-comparison evidence and linked to
the method with a typed `CONSTRAINT` edge.

On restart, only live constraints matching the **same method fingerprint, search
version, resource metric and envelope** may suppress macro use.

A changed search version or resource envelope therefore reopens applicability by
construction; failure memory cannot become timeless global falsity.

## Causal persistence controls

- ordinary scoped parent stores/reloads identical scopes in JSON;
- OCM stores the same scopes as separate constraint identities;
- ordinary == OCM task-by-task on test;
- revoke all failure-scope evidence before restart -> OCM reduces exactly to
  `STATIC_APPLICABILITY`;
- change `search_version` at read time -> no failure scope applies.

## Positive terminal

```text
FAILURE_MEMORY_USEFUL_AT_SCOPE
```

requires the test conditions and persistence controls above.

This supports scoped reusable **failure knowledge**, not OCM-specific novelty.
The ordinary scoped-nogood parent receives the same learned records and policy.

## Negative terminals

```text
CANNOT_CHECK_STATIC_APPLICABILITY
NO_SCOPED_FAILURE_BUCKET
FAILURE_SCOPE_DOES_NOT_GENERALIZE
HARMFUL_TRANSFER_LIMIT
STATIC_APPLICABILITY_PARENT_SUFFICIENT
FAILURE_MEMORY_NOT_USEFUL
CANNOT_CHECK_FAILURE_MEMORY_PERSISTENCE
```

## Cost accounting

Report separately:

- development primitive and macro search attempts;
- feature extraction work;
- bucket induction work;
- number of stored scopes;
- serialized bytes;
- per-query scope lookup work;
- test search attempts for every parent;
- avoided harmful macro attempts;
- false-block cost if any.

A positive mechanism result is not a lifetime-net-benefit result unless learning,
storage, maintenance and lookup costs also repay over the registered horizon.

## Freeze rule

After the first result, do not alter populations, support threshold, feature
families, family order, safety rule or positive criteria to rescue v1.
