# G3.2 scoped failure-memory v1

**Status:** prospectively frozen for ORION-OCM issue #165 G3.2.  
**Claim ceiling:** bounded remaining-state failure memory in one exact polynomial ecology. See [CORE.md](CORE.md).

## Why this study exists

G3.2 asks whether failed attempts can be retained and reused as **scoped**
dead-end memory:

- retain failed attempts;
- distinguish method failure from task impossibility;
- reduce repeated compatible dead ends;
- preserve success outside the failure's remaining-state scope;
- reopen applicability after regime change;
- avoid task-id blacklist shortcuts;
- compare TMS/nogood, CEGAR, and CBR parents;
- count storage, index, and maintenance cost.

This is not a task-id cache and not a logical ATMS nogood.

## Immutable domain

```text
src/ocm/learning/methods.py
Git blob 50323a33418b8ef8bb6500ddeba4b9d1f795e9e3
```

Population helpers are reused from `research/g2-macro-operator-v1/experiment.py`.
No production source changes.

## Frozen partition

Enumerate exact polynomial identities through primitive length 6. Assign
minimum primitive length. Salts and counts are immutable after the first
result.

### Training

- minimum primitive length exactly 5;
- salt `orion-ocm-g3-failure-train-v1`;
- first **24** identities.

Length 5 was not used by G2 macro or G3 composition salts (those used 6/7/8).

### Test

- minimum primitive length exactly 6;
- salt `orion-ocm-g3-failure-test-v1`;
- first **16** identities after excluding previously exposed length-6 identities
  from G2 macro training/validation/test salts and G3 independent-composition
  A/B training salts.

Do not manufacture test tasks from observed failures.

## Mechanism

Search works **backward** from the target polynomial. Remaining-state
signature = canonical residual coefficients after a prefix of inverted
last operators. Methods are the four primitive tokens.

A retained `METHOD_FAILURE` at `(method, remaining, budget, env)` is skipped
on later visits to that same tuple. The same method is still tried on other
remaining states. Exhausting every method with a completeness certificate
under the remaining-length bound may be `TASK_IMPOSSIBILITY` at that bound.
A budget miss of one method is never promoted to impossibility.

Regime-change arm: raise remaining-length from 4 to 5 on the training
identities. Scoped memory retries because budget is part of the key.
A task-id blacklist parent must fail this arm.

## Parents and causal controls

Ordinary JSON persistence loads the same skip records as OCMRuntime
admit → persist → restart. Revoking training evidence must restore
no-memory search. TMS/nogood uses the same tuples. CBR uses nearest failed
**task** by coefficient L1. CEGAR generalizes a method failure by residual
degree. The logical ATMS overclaim mutant treats any method failure as a
remaining-state nogood independent of method and budget, and must over-prune
at least one solvable residual.

## Cost

RESULT.json reports stored record count, serialized bytes, lookup counts,
skipped enumerations, and extra retries after reopen.

## Freeze rule

After the first result, do not alter salts, counts, remaining-state keys,
method order, or failure-kind rules to rescue v1.
