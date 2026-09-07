# Custody and costs

PREDECESSORS.json preserves the exact source pins and observed predecessor
outputs. It distinguishes hosted log evidence from the retained ZIP artifact.
The 29,511 versus 690 discrepancy was traced to lexical restrictions; the
predecessor failures remain unchanged. No new coverage number is inferred.

A run binds the package's files before reading source and checks the same
inventory after writing data artifacts. Output is never overwritten.
Generated receipts under provenance/runs are excluded to avoid self-reference.
CODE_SOURCE.json includes this policy, the predecessor metadata, source and tests.

The public driver reads one Git blob at a time and retains lexical records,
rather than materializing the complete proof-body corpus in memory.
It still reads the full selected corpus globally and retains all wrapper context.
This is not query-local work and does not establish OCM active-subspace scaling.

REPORT.json records wall time, own/child CPU, bytes read from Git, largest blob,
metadata bytes, artifact bytes before the report and row accounting.
Own peak RSS and finished-child maximum RSS are process-lifetime measures;
their sum is not the concurrent process-tree peak. Physical I/O, cache state
and process-tree peak are not measured. The final report serialization/write,
initial Python import and external acquisition/build work are excluded explicitly.

Output files are evaluator-only. Solution hashes/imports are retained; solution
body text is not written. Wrapper context can contain helper proofs, so this
inventory is not a security boundary for future blinded studies.

Tests may write small authored Git-object fixtures into temporary directories on
the laptop. They never fetch source, select a public proof target or call Lean.
A passing fixture receipt does not authorize or substitute for a full corpus run.
