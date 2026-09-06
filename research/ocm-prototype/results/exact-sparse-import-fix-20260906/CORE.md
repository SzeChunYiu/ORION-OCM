# Donor test discovery correction

PR106's actual CI run 34029741744 / job 101476966906 failed during collection:
the research helper directory was absent from Python's module search path.
The numerical donor at `6678900ef3e3dc563a6d65fdcde24e1b4160ac82` is unchanged.

A minimal test-local conftest adds the prototype directory to pytest's search path.
An explicit fixture supplies that path only to the three existing child-process
controls. No workflow, dependency, default runtime or numerical code changed.
No tests are skipped and no assertion is weakened.

## Executed checks

- [Original CI red](raw/original-ci-red.log), copied byte-for-byte.
- [Local collection red](raw/collection-red.log): 34 collected, two actual import errors.
- [Affected green](raw/affected-green.log): **58 passed**, zero skipped.
- [Full CI-scope collection](raw/ci-scope-collection-green.log): **286 collected**, no errors.

All local commands ran from the repository root on laptop billy with
`PYTHONPATH=src` only: the launcher supplied no prototype path.
This points to the exact local core without mutating the shared editable installation.
CI's installed package provides the core instead. Child-control research imports
are now explicitly configured by their test fixture in either setting.

The complete CI test scope was collected, not executed again. Only the affected
donor suite ran; there was no comparative timing or model study.

[Bindings](BINDINGS.json) records numerical/test source hashes and exact recipes.
[Artifact inventory](ARTIFACTS.json) binds this compact successor, preserving all
earlier controls and failure records.
