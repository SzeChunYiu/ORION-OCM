# Evidence custody

Read the exact issued [CORE](CORE.md), [source note](NOTE.md),
[review](REVIEW.json) and [aggregate projection](AGGREGATES.json).
These support bounded causal macro use and equality with the ordinary parent;
they do not establish serving-time speedup or registered lifetime payback.

[RAW.zip](RAW.zip) preserves all original reconciliation files byte-for-byte:
source snapshots, GitHub/run/artifact metadata, retained control/time logs,
the original downloaded aggregate artifact, and the three unissued drafts.
[RAW-MEMBERS](RAW-MEMBERS.json) binds every member to its original path.
The archive member `reconciliation/aggregate-artifact.zip` preserves GitHub
artifact 10077609834 after provider expiry; its original SHA256 is
`7337eaefdb602d4735600d113119d790d1e56619b3d04c8c577edbed9c97b790`.

The artifact's nested result identity is retained in AGGREGATES. Packaging hashes
and copies the artifact as opaque bytes; it does not decode that result, inspect
per-task/validation/test rows, execute source, or rerun any study/control.

[Immutable source references](UPSTREAM.json) use commit
`0cd4f4c541491a386677ffd91a97c83d49562dc0`. The recorded PR193 OPEN/prospective
observation is scoped to the review time; it is not a claim about later activity.
Unissued pre-guard drafts are history only. Their bytes and the issued note remain
unchanged; only the current top-level REVIEW is the issued reconciliation receipt.

[Direct-copy identities](COPY-MANIFEST.json), [original seal](HASHES.json),
[package readback](READBACK.json) and [public inventory](FILES.json) distinguish
original scientific evidence from packaging. Source/control files stay inside
RAW as evidence and are not installed or qualified as a new runnable study.
