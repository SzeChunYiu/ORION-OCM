# Independent custody review

The package/runtime reviewer checked Git commit/tree/blob membership, fixed config and
archive hashes, complete parent runtime/provenance inclusion, prior binding coverage,
immutable old documents/results, exact current source inventory, and dependency omission.
The first forty V2 correctness and boundary tests passed.

The review then found a narrower acceptance-scope problem in the unsealed draft: any
successful command record and any hash-bound file could satisfy replay structure. A
`true` command and a plain text file therefore qualified despite establishing no
regression coverage. The demonstration was confined to temporary test evidence; no
historical or repository result was modified.

Before V2 receipts were generated, the draft was corrected to require two fixed named
validation gates, exact normalized pytest arguments and corresponding JUnit artifacts.
The parser checks positive testcase coverage, count consistency, zero failures/errors,
and rejects an entirely skipped suite. The full gate requires at least the parent's
613 tests; the focused gate names the final surface, runtime, distribution, sparse
solver and receipt test files. Negative cases preserve the original counterexample,
omitted/duplicate gate, subset command, absent artifact, plain text, empty/undersized
suite, failure/error, all-skipped suite and inconsistent count.

The corrected receipt proves repository custody and that the recorded commands/results
meet the declared structural gates. It remains a local execution attestation and does
not provide cryptographic execution proof, external evaluation, independent replication
or scientific promotion.

The same independent reviewer rechecked the correction and confirmed rejection of the
original counterexample. All 52 V2 tests passed independently in 20.73 seconds. The
specific acceptance-scope finding is resolved within the declared recorded-run gate.
