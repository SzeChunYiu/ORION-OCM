# #203 goal-only lifecycle: the all-UNKNOWN run is an artifact, not a result

**`VACUOUS_RUN_RESOURCE_BOUND_NOT_RESULT`** — diagnostic re-run, not scored evidence.

## What was reported

The frozen `research/goal-only-lifecycle-v1` study (#203, commit `29c0ec4`) returned
`COMPLETE_THREE_ARM_ENGINEERING_RUN` with **0 causal decision witnesses**, **0 checked
cohort-use tasks**, `all_preparation_parity: false`, and `UNKNOWN` on all 10 tasks in all
3 arms. A follow-up compared a 150 s and a 300 s hard wall and found the two outputs
**byte-identical**, which looked like reassuring robustness.

## What is actually true

The original invocation did not retain per-row receipts. Re-running it unchanged and
reading them settles it: **all 30 rows terminate at the registered 8-second soft solver
wall**, with error `REGISTERED_SOFT_WALL_BOUND`, and `parent_scope_complete: false`
throughout.

Of the five registered budgets, **exactly one is saturated**:

| budget | used | registered | saturation |
|---|---:|---:|---:|
| **solver soft wall** | **8.000 s** | **8 s** | **100%** |
| grounded instances | 13,648 | 100,000 | 13.7% |
| token states | 45,672 | 2,000,000 | 2.3% |
| **abstract proof-tree decisions** | **0** | **3** | **0%** |

**Not one abstract proof decision was ever made, in any arm, on any task.** The mechanism
under test — cohort method eligibility, which acts *at* proof decisions — never got the
chance to act. So "0 causal decision witnesses" says nothing whatever about the inherited
22-method library. It is the vacuous negative this programme has now hit twice: G3.2's
first draft reported `FAILURE_MEMORY_NOT_USEFUL` from a run in which no failure had
occurred, and this reports zero witnesses from a run in which no decision occurred.

## Why the wall-doubling comparison was reassuring about the wrong thing

`--hard-wall` is a **per-arm** process bound. The 8-second soft wall is **per task**.
Doubling 150 s → 300 s therefore changed nothing that binds, and the byte-identical
outputs are what that looks like — not evidence of robustness. The comparison artifact
also carries no timing fields at all, so byte-identity could never have demonstrated
insensitivity to a *time* budget in the first place.

## Where the 8 seconds goes

Per task, ~162,000 syntax requests, of which **96.3% return
`NOT_DERIVABLE_REGISTERED_GRAMMAR`**. The wall is consumed by syntax derivation against a
grammar that rejects almost everything asked of it, before search reaches a proof
decision. That is the term to attack: it is a preparation cost, not a search cost, and
`cache_hits: 161,280` against `cache_misses: 895` shows the cache is already working —
the requests are cheap and simply numerous and futile.

## What this does and does not license

**Does:** `COMPLETE_THREE_ARM_ENGINEERING_RUN` should not be read as a retained negative
about method reuse. #203's own protocol already says so — *"UNKNOWN, timeout, unsupported
parent scope and native-check failure are **not** evidence that removing the method
reduced capability"* — and this shows every row is exactly that case. `all_preparation_parity:
false` is likewise downstream of the timeout, not an independent defect.

**Does not:** claim the library is useful, that a longer wall would produce witnesses, or
anything architectural. The honest disposition is `CANNOT_CHECK` on a resource bound. To
convert it into a real result the run needs either a soft wall large enough that some other
budget binds first, or a cheaper syntax path — and until then the arms are not comparable
on anything.

## Reproduction

```
python3 allocation.py --manifest manifest.json --prefix joined.mm --repo <repo> --out tasks/
python3 lifecycle.py  --repo <repo> --bundle <bundle-dir> --tasks tasks/TASKS.json \
                      --output <run-dir> --hard-wall 300
```
The bundle is recovered from `research/ordinary-goal-cohort-result-v1/RAW.zip` per
`RECONSTRUCTION.json` (base + one newline + suffix = 1,812,202 bytes). Note `--prefix`
takes the **joined** prefix, not the base.
