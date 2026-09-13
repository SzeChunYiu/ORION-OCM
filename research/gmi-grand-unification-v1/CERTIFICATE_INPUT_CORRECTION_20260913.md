# Finite certificate input correction

Date: 2026-09-13  
Baseline: `5622ac45d0261e8fe0a92f4209b1bb782ce43732`  
Scope: the finite NN/non-NN derivation certificate and synthetic scalar protocol
adjudicator. This is a bounded implementation correction, not verification of
every Grand GMI theorem or an empirical family verdict.

## Counterexamples found before repair

The following were executed against the baseline source. `N` denotes a neural
candidate and `P` a non-neural candidate; unspecified fixture gates are true.

| Packet or mutation | Baseline output | Required handling |
| --- | --- | --- |
| `N.profile=(1,)`, `P.profile=(2,0)` | `DERIVED_NEURAL` | A truncated resource vector is not a comparable registered profile. |
| Duplicate name `same`, profiles `(1,1)` and `(2,2)` | `FAMILY_COEXISTENCE` with duplicate selected names | Duplicate identities invalidate the certificate. |
| Cheaper `N.adequate="false"` | `DERIVED_NEURAL` | A string is not a Boolean adequacy certificate. |
| Cheaper `N.adequate=None`, adequate `P` | `DERIVED_NON_NEURAL` | Unknown adequacy must not eliminate a potentially superior rival. |
| `N=[8,9]`; cheaper `P=[1,2]` with no deployment evidence | `DERIVED_NEURAL_AT_REGISTERED_SCOPE` | Missing deployment evidence forces abstention. |
| Both candidates have no deployment evidence | `INFEASIBLE_AT_REGISTERED_SCOPE` | Absence of evidence is unresolved, not proved infeasibility. |
| Unknown family label | `FAMILY_COEXISTENCE_AT_REGISTERED_SCOPE` | An unregistered family cannot receive a canonical certificate. |

The initial hostile suite contained 17 test methods. It reported 60 failing
subcases and 12 erroring subcases before implementation changes; these include
the existing empirical receipt mismatch. Subcase totals are unittest subtest
results, not counts of independent theorem failures. The baseline's existing
88 Grand GMI unittest methods passed, showing that those tests did not expose
these inputs.

## Correction

1. `derive` now requires explicit registered `profile_dimension`; absent or invalid
   dimension yields `UNDECIDED_FROM_CURRENT_EVIDENCE`. All profiles must match that
   dimension, preventing both uneven truncation and a common omitted suffix.
2. Both adjudicators require unique nonempty identities, known finite-checker
   family labels, and literal Boolean evidence fields. Missing and ill-typed
   fields abstain before candidate elimination.
3. Resource coordinates and scalar bounds must be finite real numbers, excluding
   Booleans. Empty/truncated profiles and inverted intervals are rejected. Exact
   fractions, decimals and arbitrarily large integers remain supported.
4. Missing deployment evidence on an otherwise eligible candidate produces
   abstention. An explicit independent hard/development failure can still exclude
   a candidate. This preserves the distinction between unknown evidence and a
   proved failed condition.
5. All repository callers of the finite derivation function found by source search
   were its self-tests; these now declare their two-dimensional registration.

The direct `dominates` helper raises `ValueError` for malformed/incommensurate
profiles, while the certificate API returns the canonical undecided tuple.

## Receipt reconciliation

The derivation receipt remains unchanged and matches regenerated synthetic output.
The empirical receipt previously contained manually added fields absent from
`main()` output, including the incorrect missing-deployment infeasibility claim.
It has been regenerated from corrected source. Its missing-deployment result is
now explicitly `UNDECIDED_FROM_CURRENT_EVIDENCE`; prior manual assertions are not
carried forward as independently executed evidence.

## Verification and remaining boundary

The final hostile suite contains 19 test methods, including the explicit
registration and raw-comparator tests added during review. All 19 pass. It checks
the counterexamples, malformed registries, nonfinite/Boolean/string values,
missing gates, invalid dimensions, duplicate IDs, exact arithmetic, candidate
permutations, ties, certified failure behavior and exact receipt replay.
The complete discovered unittest suite in `research/gmi-grand-unification-v1`
also passed: 107 methods in 26.511 seconds. `git diff --check` passed.

Run it with:

```sh
python -B -m unittest discover -s research/gmi-grand-unification-v1 -p 'test_grand_gmi_certificate_input_validation_v1.py' -q
```

Input validity does not prove empirical facts. Coordinate order/units, candidate
membership, receipt provenance, interval calibration/coverage and common scalar
registration remain external premises. No independent attainability of interval
endpoints is assumed: strict upper-versus-lower separation is sufficient for every
joint evidence world contained in the certified intervals. Overlap remains
undecided under this candidate-level scalar rule.
The scalar routine is a sufficient unique-candidate certificate, not a complete
family-level optimizer: two overlapping candidates of one family can both beat
all rival families while this routine conservatively returns undecided.

Adjacent finite family/resource helpers and the wider receipt stack are separate
review scopes. This correction does not assert that all mathematical or empirical
gaps in Grand GMI are closed.
