# Focused authored qualification

The historical helper bodies were extracted from the two pinned source files;
only their function names were prefixed G2/G3 to load both in an isolated module.
[Source origins](SOURCE-ORIGINS.json) retain the exact function ranges/hashes.
Full study modules and their OCM imports were never executed.

The same seven newly authored methods ran first against those old bodies and
then against the corrected successor. Old bodies produced ten expected assertion
failures for strict-prefix and empty-population subcases, with zero errors.
The four clean/mismatch/schema-preservation methods passed before the repair.
All seven methods pass after adding the two-line precondition to each function.
There was no historical G2/G3 suite, index or scientific result rerun.

| Stage | Child PID | Exit | Child wall s | User/system CPU s | Peak RSS KiB |
|---|---:|---:|---:|---:|---:|
| Old-body reproduction | 2538477 | 1 | 0.037724140 | 0.029819/0.004969 | 38616 |
| Corrected helper | 2539234 | 0 | 0.032921619 | 0.024441/0.008147 | 38708 |

Both were reaped by wait4 on pinned CPython3.11.14/Linux, actual cwd `/tmp`.
The helper, test, observer and interpreter hashes match before/after. Child
receipts record actual imported helper path, test path, PID/PPID and file-backed
module paths. This is not a byte freeze of every stdlib module. No forbidden
study/OCM module import was recorded.

Child wall includes startup/imports/test/export and is nested in the external
observer session. The inner control windows overlap it and must not be added.
Authoring, source reading and packaging time are not measured as zero; these
figures are qualification costs, not serving or lifetime performance evidence.

[RED controls](records/red-01/CONTROLS.json), [RED process](records/red-01/PROCESS.json),
[GREEN controls](records/green-01/CONTROLS.json) and [GREEN process](records/green-01/PROCESS.json)
retain failures, exact source identities, stdout/stderr and timing boundaries.
