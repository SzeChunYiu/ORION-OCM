# Z12 freeze v1 — amendment 1: the third disposition

Committed **before any score in this package has been computed**. `git log`
shows this commit preceding the first commit that contains a scorer.

## What the v1 freeze missed

`FREEZE_V1.md` enumerated three registered prediction types — `POINT`,
`SET`, `ABSTAIN_FULL` — and declared that an empty prediction set is refused and
fails the run. Loading the pinned population shows the parent's disposition
alphabet has **three** values, not two:

| universe | `CANNOT_IDENTIFY` | `IDENTIFIED` | `INCONSISTENT_REGISTERED_ASSUMPTIONS` |
|---|---:|---:|---:|
| `SIGMA_SYN` | 92 | 4 | 0 |
| `SIGMA_ARCH` | 88 | 8 | 0 |
| `SIGMA_REAL` | 80 | 4 | 12 |

The 12 `INCONSISTENT_REGISTERED_ASSUMPTIONS` records carry an **empty**
`identified_set`, and their externally computed truth set `external_values` is
**also empty**. The prediction is not malformed: it asserts that the registered
world is contradictory, so no capability value is consistent with it — and the
external evaluator agrees. Refusing them would discard a correct prediction on a
typing technicality.

This is a structural fact about the pinned population, established by counting
dispositions. No score has been computed, and this amendment fixes no outcome.

## Registered change

1. A fourth prediction type is registered: **`REFUTE_WORLD`**, defined by
   `|S_i| = 0`, meaning "the registered assumptions admit no value".
2. `REFUTE_WORLD` records are **admitted** to the population and reported as
   their own stratum, never pooled with the others.
3. They are scored for `BND-1` typing and for `COV-1` coverage, where
   `T_i subset-or-equal S_i` reduces to `T_i = empty`.
4. They are **excluded** from `CAL-1`, `BRI-1`, `SHP-1` and `VAC-1`, whose
   definitions divide by `|S_i|` or compare `S_i` to the full alphabet `A` and
   are undefined at `|S_i| = 0`. The excluded count is reported explicitly in
   `RESULT_V1.json` as `REFUTE_WORLD_excluded_from_mass_scores`.
5. A record with `|S_i| = 0` whose truth set is **non-empty** remains a refusal
   and still fails the run: that would be a prediction that excluded the truth.
   Both routes assert this branch is reachable by constructing such a record.

Everything else in `FREEZE_V1.md` — claim ceiling, the nine rows, the two
routes, the six hostiles, the 200-seed null, the forbidden promotions — is
unchanged.
