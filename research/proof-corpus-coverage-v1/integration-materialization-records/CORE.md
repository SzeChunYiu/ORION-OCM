# Current materialization integration records

The current laptop run passed 411 tests; seven explicit host controls were skipped
and two exact-interpreter registrar tests were deliberately deselected.
All three retained-evidence guards passed. This is engineering evidence only.

Read [INDEX](INDEX.json), [current result](RESULT.json) and
[commands/environment](PRELAUNCH.json). [PROCESSES](PROCESSES.json) retains the
four separate measured processes; [SOURCE-BEFORE](SOURCE-BEFORE.json) binds 137
selected project files, unchanged through the final run.

[records.tar.gz](records.tar.gz) retains all three integration generations,
both repair records, source snapshots, raw logs/JUnit and two independent reviews.
The first failed because loader tests polluted the module registry; the second
correctly failed the historical guard after an older test was changed.
The final repair restores the old file and isolates only the new loader tests.
Neither predecessor is reported as an accepted integration.

[MEMBERS](MEMBERS.json.gz) and [VERIFY](VERIFY.json) bind the retained originals.
[OMISSIONS](OMISSIONS.json) identifies temporary fixture bodies and host inputs
that remain external. No missing bytes were reconstructed or tested by packaging.
