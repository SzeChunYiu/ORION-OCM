# Independent-authorship fail-closed policy

Issue #165 §16. Executable copy: `policy.py`.

## Rule

Do not label benchmark truth from generator intent when that intent is the target.

```text
if target ∈ {cause, diagnosis, true_layer, true_class,
             planted_cause, minimum_sufficient_cause, root_cause}:
    truth ← independent exact recovery
    if recovery is not exact and cheap:
        truth ← CANNOT_CHECK
    generator intent is audit-only
```

## Admissible truth sources

| Target | Admissible source | Forbidden source |
|---|---|---|
| Transition / kernel / checker decision | Frozen independent oracle or kernel | Planter family, authored method id, scenario layer |
| Minimum sufficient cause | Recovered min-repair / first-invalid atom from that oracle, without reading the planted label | `Instance.family`, `Scenario.true_layer`, author-intended method I |
| E3+ confirmatory item | Independently authored world/task family | Any internally generated extra world that shares the mechanism taxonomy |

## Required retain

- Generator-intent audit fields stay on the record (`planted_family_audit`, variant, case id).
- Task generation stays out of the diagnosis policy. Sharing a taxonomy is already a leak; rejection-sampling until the oracle matches the planter is a second leak.
- An artifact-explained positive (shared taxonomy, oracle-filtered planter, author-planted method) is a **negative** finding for independent authorship.

## Fail closed

- No fallback from `CANNOT_CHECK` to planted labels.
- No E3/E4/E5 claim on a generator-authored family.
- More internally generated worlds do not substitute for independent authorship.
