# Parent ownership — what this tranche does not claim

## Repository parents

`gmi-833-aj9a-known-family-benchmark-v1` owns the eleven-family registry, the post-hoc
fingerprints, the outcome terminals and — decisively for this tranche — the
`forbidden_generator_inputs` list. The eight audit classes are that list, quoted, not
re-worded. The registry is pinned by git blob and the audit fails closed on drift.

`gmi-833-aj9b-v1` … `gmi-833-aj9h-v1` own the blind searches, their configurations, their
outcomes and the recovery verdicts. This tranche neither re-runs nor re-judges any of them.

`gmi-833-aj10-prospective-unknown-v1` established the shape of a source audit with its
`blind_source_forbidden_hits` field; this package generalizes that shape across every holdout
and adds the validation the row's wording requires.

## External practice

Static source auditing, lexical scanning and holdout discipline in blind evaluation are
ordinary practice and are not claimed novel. The specific discipline of proving a checker's
recall on planted positives and proving the scan works on known-positive data before reporting
an absence is standard verification hygiene, stated here because this corpus has been bitten by
its absence before.

## What is NOT claimed novel

The registry, the forbidden list, the blind searches, the recovery verdicts, and source
scanning as a technique.

## The residual contribution

1. A search vocabulary derived programmatically from the frozen registry rather than authored,
   so it cannot quietly drift from what the parent forbids.
2. A published exemption rule: a holdout's own statement of what it forbids is not leakage, and
   every exemption applied is listed with file, line and text.
3. Two severity levels, so a generic word in an identifier is reported and read rather than
   either ignored or treated as a violation.
4. Recall on all eight forbidden classes, a control proving the scan works, and a hostile that
   encodes the one recall defect this validation actually caught.
5. One custody gap in a merged package, published.
