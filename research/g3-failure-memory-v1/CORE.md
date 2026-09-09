# G3.2 scoped failure memory v1 — claim ceiling

**Claim authority:** bounded remaining-state failure memory in one exact
polynomial residual-search ecology.

This capsule may support:

```text
FAILURE_MEMORY_USEFUL_AT_SCOPE
```

only as a **G3.2 scoped-failure** result: retained failed continuations,
keyed by remaining residual polynomial + method + remaining-length budget +
environment, reduced later compatible dead ends on a frozen held-out stratum,
without banning the same method on other remaining states, and with
applicability reopened after a budget raise.

It does **not** support:

- an OCM architecture residual versus the identical ordinary JSON memory
- task-id blacklists as a substitute for remaining-state scope
- promoting one method's budget miss to logical ATMS task impossibility
- cross-domain transfer
- whole-lifetime net-benefit

## Mechanism (frozen)

Backward residual search over the registered `inc/dec/double/square`
grammar. Remaining-state signature = canonical coefficient polynomial still
to be realized. A method is tried as the last operator; invert it through
the residual, then recurse under `max_length-1`.

Skip key:

```text
(method_token, remaining_coefficient_signature, max_length=L, environment_version)
```

`task_id` may appear on `FailureAttemptV1` only as lineage. It is not a skip
key.

`METHOD_FAILURE` = that method did not solve this residual under this bound
(invert-impossible or continuation failed). `TASK_IMPOSSIBILITY` requires a
completeness certificate: every method was fully enumerated under the bound.
A single method miss stays `METHOD_FAILURE` or `UNKNOWN`.

## Parents (same frozen data)

| Parent | Role |
|---|---|
| none | primitive residual replay, no memory |
| TMS/nogood | same `(method, remaining, budget)` skip tuples |
| CBR | nearest prior **failed task** by coefficient L1 |
| CEGAR | degree-generalized method skip |
| logical ATMS overclaim | any method failure becomes a remaining-state nogood, ignoring method/budget |
| task-id blacklist | must fail the budget-raise reopen arm |
| ordinary JSON vs OCM admit/restart/revoke | identical algorithm; ordinary is expected to tie |

Logical ATMS nogoods in `src/ocm/kso/nogoods.py` are inconsistent assumption
sets. They are **not** used to declare a polynomial residual impossible
because a budgeted method missed.

## Valid terminals

```text
FAILURE_MEMORY_USEFUL_AT_SCOPE
FAILURE_MEMORY_NOT_USEFUL
PARENT_SUFFICIENT
HARMFUL_TRANSFER_LIMIT
CANNOT_CHECK_<reason>
```

A negative is a valid G3.2 result. Do not retune salts. If v1 is negative,
a v2 successor must change the **mechanism** (for example budget-scoped
records versus logical nogoods), not the frozen partition.
