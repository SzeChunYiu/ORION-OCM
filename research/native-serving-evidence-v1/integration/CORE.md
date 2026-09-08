# Native serving source integration

The research adapter and explicit Linux CI job are ready for the repository. The local
portable qualification passed 42 controls; 3 external-bundle controls were deselected.
Native verification was prohibited and the guard recorded zero calls. This is separate
from the preceding native serving experiment, whose measured source remains archived.

- [Source manifest](SOURCE-MANIFEST.json) pins all 34 source/workflow files to base 3430919.
- [Independent source review](SOURCE-REVIEW.json) accepts the bounded integration.
- [Portable receipt](PORTABLE-RECEIPT.json) names every selected and excluded test.
- [Process record](PORTABLE-PROCESS.json) binds argv, PID, source hashes and costs.
- [JUnit](PORTABLE-TESTS.xml) records 42 passing cases.
- [Independent outcome review](QUALIFICATION-REVIEW.json) confirms 262 retained-data checks.

The process took 3.893533292 seconds wall, 2.249758 user and 0.273673 system, with 59,424 KiB
peak child RSS. These are engineering-check costs, not native solving measurements.

Serving statements are unchanged. Successor differences are prefix wording, explicit
actual-input declarations/fixture and receipt metadata, focused CI collection, and four
spaces removed from one vendored checker blank line with its provenance hash updated.
The Python AST of that checker is unchanged. The full original MIT notice remains.

The module remains outside installed package discovery. No old receipt qualifies this
successor for native outcomes; no acquisition, language ability or novelty is claimed.
Exact new-head GitHub CI is recorded on the associated PR, separately from this local run.
