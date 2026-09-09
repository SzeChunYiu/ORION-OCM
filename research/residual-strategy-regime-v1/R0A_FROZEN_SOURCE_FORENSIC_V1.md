# R0A frozen-source forensic V1

**Status:** historical test-donor migration upper bound / source-level only / no production authority.

`R0A_CHECKER_PROVENANCE_AUDIT_V1.md` establishes a negative about the recorded
runtime channel: the frozen receipt and current persistent manifest do not bind
checker implementation/effect identity.  That does not imply every historical
checker body is impossible to reconstruct from other immutable repository
sources.  This companion audit asks the narrower forensic question.

## Frozen source custody

The three source files that account for the corrected 20 multi-PASS CHECK-tail
opportunities are byte-identical between the frozen R0 commit and this research
branch:

```text
tests/m2/test_navigation_serving_runtime.py
  Git blob 55224956133d7b3c2a5c1078d06998e4ed0bd3a2

tests/m2/test_runtime_extraction_index.py
  Git blob 90397bb6fc68ab20fda182b0b9ab9fb3b38b6867

tests/m2/test_solve_operator_index.py
  Git blob dd354658b67f2307f1c9c3743eb8705d0c51de53
```

Frozen commit:

```text
47d706ab42d8528060356c7d4a267e1454ce9e7a
```

The relevant operator factories use trivial checker expressions of the form

```python
checker=lambda out: SV.Status.PASS
```

and the executable audit parses the source AST after verifying Git blob identity.
It does not trust string search alone.

## Exact opportunity census

The frozen receipt's loops/parameterizations and the byte-identical source give:

```text
navigation serving runtime                                      7
  complete solve dense/index parity                             4
  runtime revocation/restart                                    3

runtime extraction index                                       11
  default/indexed semantic-trace parity                         4
  selected indexed path                                         1
  reused index                                                   2
  revocation/reinstatement                                       2
  restart/rebind                                                 2

solve operator index                                             2
  real solve reference/index parity                              2
                                                               ----
TOTAL                                                           20
```

This equals the corrected R0A upper bound of 20 actual tail CHECK callbacks.
Therefore the historical **test** donor has a 20/20 source-level trivial-PASS
coverage upper bound.

## What 20/20 means — and what it does not

It is useful positive evidence for feasibility of a restricted checker migration:
the old opportunity was not created by twenty visibly complex host-effectful
checkers.  A pure-checker experiment on fixtures of this shape would cover the
entire historical tail count.

It is not an authority upgrade:

```text
receipt/manifest bound these checker bodies?       NO
runtime effect certificate existed?                NO
literal CHECK trace preserved by omission?         NO
production checker ecology represented?            NO
migration/build/replay cost measured?               NO
```

Source-forensic purity and runtime-certified purity are different evidence
classes.  A future runtime cannot safely decide to elide a callback because a
researcher can later find a matching-looking lambda in a frozen test file.  The
checker certificate must be bound prospectively to the registered operator and
replay identity before execution.

## Converged R0A position

The two R0A results are complementary:

```text
CHECKER_PROVENANCE_INSUFFICIENT_R0A
  historical runtime evidence cannot authorize checker-effect elision

FROZEN_R0_TEST_TAILS_FORENSICALLY_PURE_NOT_RUNTIME_CERTIFIED
  nevertheless, all 20 historical test opportunities reconstruct to trivial
  PASS checker factories, so a prospective restricted-checker migration is a
  plausible experiment rather than an obviously empty lane
```

The next empirical tranche should therefore be prospective, not retrospective:
bind checker certificate schema/language/AST digest/effects into operator and
replay identity, define the protected trace projection, freeze a non-test checker
population, and then measure certified-pure coverage and complete migration cost.

No learned router or neural checker is authorized by this result.
