# Evidence and regression replay

This packet preserves failed development evidence and current repair controls.
It does not replace the original study seal or turn exposed cases into a protected test.

Verify this packet from its directory:

```sh
sha256sum -c SHA256SUMS
```

The complete v2 archive is a separate release-only ZIP; its exact size/hash and
the original seal are in raw-asset-bindings.json. The local preserved ZIP contains
all capture bytes, copied model states, executed source, raw process outputs and
the independently produced external grade. Model binaries are excluded from git.
Publication must retain that exact asset identity; the asset record currently
states that its public download location has not yet been assigned.

After verifying and extracting that asset, verify every files[path] hash in
clia-reuse-capture-v2/capture-manifest.json against the extracted relative file.
All 320 sealed files were checked before archive creation; ZIP integrity was checked.
Never update the original seal to accommodate changed or missing bytes.
The ZIP includes the already graded files; reproducing a grade is optional and
must be labelled replay, leaving the original external grade untouched.

The previous failed v1 ZIP and its original initialization-repair packet remain
unchanged. Their original actor wall/CPU receipts remain included here by reference.

Run the current repair checks from repository root in a configured Linux G1 env:

```sh
PYTHONPATH=src:research/ocm-prototype PYTHONDONTWRITEBYTECODE=1 \
  python -m pytest tests/m2/test_event_reducer_consistency.py \
  research/ocm-prototype/test_clia_reuse_cold_withdrawal.py -q
```

Dependencies are the existing requirements-g1.txt pins plus pytest 8.3.5.
The cold lifecycle control uses exposed unit programs and the existing exact
checker; it performs no synthesis acquisition or trained-model inference.
The full qualified command is recorded in controls/final-start.json, including
its explicit hosted-test/result exclusions and development-data path.
Historical absolute paths in raw records describe the original execution host;
relocation must not rewrite those records or their source bindings.

The copied-ledger refusal script in controls/ uses the original host paths.
It documents a read-only failure check, not a recovery utility.
Do not run a new prospective capture without the separately registered source freeze.
