# Independent hostile audit addendum — #748

This addendum records the final pre-PR hostile review of the developmental uncertainty transport capsule. It does not change the frozen theorem, frozen expected images, confidence-budget arithmetic, or claim ceiling in `FREEZE_V1.md`.

## Review lenses

- **Formal methods:** checked quantifiers, set-image induction, union-bound direction, and the no-relation counterexample.
- **Sequential/statistical validity:** checked that no independence assumption appears and that transition-relation failure budgets are merely premises, not empirically manufactured by the adapter.
- **Developmental semantics:** checked that INFO/RECODE/SKILL/LAW/MORPH names contribute no mathematical force beyond their registered relations and that raw source observations are not inherited by target versions.
- **Hostile systems review:** checked post-activation registration, relation completeness, version custody, malformed exact arithmetic, deterministic replay, and fail-closed no-relation behavior.

## Defect found and fixed

The first implementation of `propagate_unknown` accepted any syntactically valid `ConfidenceObject`, including one fabricated outside the campaign. Although the full-target-domain fallback remained set-theoretically sound, this weakened provenance/custody: a caller could attach the fallback to an object that was not the campaign's actual registered chain tail.

The implementation was hardened so `propagate_unknown` now requires:

1. source activation has occurred;
2. the supplied object is exactly the deterministic tail produced by that campaign's registered chain;
3. the target version is the adjacent next version;
4. the target domain is a nonempty exact sorted `Fraction` domain.

A hostile test now constructs a fabricated tail and requires rejection. Boolean query tables were also hardened to require exact `bool` values rather than relying on Python truthiness.

## Dependence certificate

`DEPENDENCE_CERTIFICATE_V1.json` supplies an exact 200-atom witness with pairwise-disjoint source/relation failure sets. The actual joint-good probability is exactly `187/200`, equal to the union-bound lower bound, while the product that would be obtained from an unjustified independence assumption is different. This makes the no-independence boundary executable rather than merely textual.

## Verification status before PR

Independent local reconstruction of the hardened branch files produced:

```text
37/37 tests GREEN — normal Python
37/37 tests GREEN — python -O
```

The deterministic `RESULT_V1.json` content remains unchanged after the custody hardening. Repository CI remains authoritative for merge: it must verify the pre-implementation freeze ancestry, run both normal/optimized suites, and reproduce the committed receipt byte-for-byte.

## Claim ceiling unchanged

```text
SOUND_DEVELOPMENTAL_UNCERTAINTY_TRANSPORT_AT_REGISTERED_FINITE_SCOPE
```

This addendum does not establish G7 developmental prediction, real transition-law calibration, physical sample freshness, or small uncertainty after development.
