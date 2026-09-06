# Integration on current main

The reviewed adapter commit is `a800a2696acb29bc9c9a24b3c22ae088ecf6cd45`.
Normal merge source: `f8c1c1b16076fa9e3de9939091e9494cc05a04ef`.
Merged main: `7ff8d1ec803e78d04f95e3d966e92ed48b29ff81`.
No adapter API or production-core change was made during integration.

**118 tests passed in 20.15s**, zero failures/errors/skips, on laptop billy.
The command matches the current N1 packed-chart workflow's test scope:

```sh
PYTHONPATH=<worktree>/src OCM_G1_DEV_PATH=<custody-dev-file> <g1-env>/bin/python -m pytest \
  research/ocm-n1 research/ocm-prototype -q \
  --ignore=research/ocm-prototype/results \
  --ignore-glob='research/ocm-prototype/test_hosted_*.py'
```

The actual command adds a JUnit output path. Laptop Python was 3.13.12;
the workflow declares 3.11. This is the same test scope, not an identical CI image.
The supplied EWT dev file was checked against its required SHA256 before loading.
See [command and source bindings](raw/integration/n1-g1-command-completed.json)
and [actual JUnit](raw/integration/n1-g1-integrated.xml).

All 1,357 existing main blobs outside the reviewed G1 hook remained byte-identical
before and after the run. This covers historical results, current generic source,
its selector and immutable receipts. New adapter files are separately source-bound.

A read-only generic receipt verification succeeded at unchanged source
`e83d89b9a345062f090d14eb3dd2864f445ceaeb2188622d54c0a3301d887ec9`
and receipt SHA256
`700098f3e99f53653cfced07e3c20a7ca12b8775b9e75aa15ca5e5a1572ed7e1`.
This verifies archived gate custody; those earlier 133/1000 suites were not rerun.
No historical recipe, hosted model, protected study or prospective reuse panel ran.

The next executable study still needs the freezes and matched acquisition contract
listed in [CONTRACT.md](CONTRACT.md). This packet establishes engineering readiness only.
