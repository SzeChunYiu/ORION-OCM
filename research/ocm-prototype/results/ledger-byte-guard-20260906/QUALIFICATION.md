# Engineering and custody qualification

Final current source: 1e87a74d16aecd8e7bd74a1ff8fa33125a7c6970d40522634d17c43e3498446d (312 files).
Selected immutable receipt SHA256:
dced7c6ee62c2be0238288c8b4b34ff8e85fcfbdc555f58c27c40832c2deb3dc.
[Receipt](../../../../docs/provenance/engineering_revisions/runs/1e87a74d16aecd8e7bd74a1ff8fa33125a7c6970d40522634d17c43e3498446d/b470ae7f0c324477/RECEIPT.json).

The ordinary recorder ran once after normally merging main29085f8 metadata at
83de559d8ffbadd6f62cfc2e27a92004120fb290. The production/tests/tools trees remained
identical to candidate4408d7c. No PR90 changes are included.

- Focused engineering recipe: 133 passed, 0 failures/errors/skips, JUnit 32.614 s.
- Full engineering recipe: 1,031 passed, 0 failures/errors/skips, JUnit 223.223 s.
- Recorder outer wall: 256.712076 s; packaging overlapped part of engineering execution.
- All twelve current milestone wrappers verified the new selector.
- Separate protected V5 wrapper verified archived custody only.
- All 331 prior tracked provenance files were checked byte-identical; only the current
  engineering selector changed, and new source/run artifacts were added.

Environment: existing receipt-env Python 3.13.12, pytest 8.3.5, setuptools 75.8.0,
wheel 0.45.1. No environment installation or modification was needed.
Exact commands, stdout/stderr digests and predecessor bindings are in
[qualification/verification.json](qualification/verification.json);
the immutable selected run contains actual logs, JUnit, source archive and environment.
Current scientific promotion: NOT_ESTABLISHED. Protected reevaluation: NOT_RUN.
Engineering tests are not a claim of protected scientific replication.

## Focused implementation history

raw.zip retains the initial baseline red (three failures/three passes), first green
(15 passes), compatibility gate (32 passes), and the actual allocation-failure red.
It also retains exact executed source versions, final focused34, runtime270 and
aggregate-reader5 results. The optional-cache MemoryError repair was reviewed before timing.
The paired benchmark was run only once after final source/plan registration.

## Portable post-execution grading

The first archive replay stopped before the frozen grader could start because the
venv Python symlink pointed through a version alias absent in the namespace.
The second stopped at Python startup because /dev random devices were absent.
Their stderr, receipts and exact wrapper source remain under replay/attempt-v1 and attempt-v2.
The small corrections select the same resolved Python executable and mount /dev.
They alter only archive-replay setup, never the original experiment.

[Final clean replay](replay/clean-v4/REPLAY_RECEIPT.json) reconstructed 129 raw and 327 source/tool files,
and the unchanged grader reproduced the original grade bytes exactly in 0.415560 s wall.
Its self CPU (0.301578 s) and direct waited-child CPU (0.069866 s) are separately scoped;
total process-tree CPU remains UNKNOWN. This is later verification cost, not another sample.
[Corrupted-archive control](replay/corrupt-control.json) refused a copied archive with one
flipped byte before grading. No original archive, ledger, clock or outcome was changed.

The first clean replay (v3) also matched exactly and is retained. A later mount-layout
correction exposes only results/ writable, removing the extracted input directory's writable
alias. Final v4 and the repeated copied-archive refusal use that narrower mount.
No original storage measurement, input or grade was rerun or modified.
