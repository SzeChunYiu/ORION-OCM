# Portable external grading

Use the archived grader for each attempt. It needs Python 3.13 standard library;
no OCM runtime, SymPy, Z3, model or original laptop paths are needed for grading.
The raw manifests retain historical absolute paths as custody metadata. Do not
rewrite them when relocating this directory.

From this packet directory, first verify its inventory:

```sh
sha256sum --check SHA256SUMS
```

Then choose new, nonexistent output files:

```sh
python3.13 raw/attempt-1/source/trial_grade.py \
  --capture raw/attempt-1/capture \
  --manifest-sha256 03412cc5c308e07f806c94141abd2e6c154599005684e16822acb0a4178a8a48 \
  --output /tmp/exact-sparse-attempt-1-regrade.json
```

Expected exit 2 and unchanged CANNOT_CHECK. The secondary error diagnostic is
historical evidence; this command intentionally uses its original grader.

```sh
python3.13 raw/attempt-2/source/trial_grade.py \
  --capture raw/attempt-2/capture \
  --manifest-sha256 29801ea57cd59a870b5b3b0ed4b3ede8bc5057cebce019798b65f038afff76b4 \
  --output /tmp/exact-sparse-attempt-2-regrade.json
```

Expected exit 0, EXACT_FUNCTIONAL_PARITY and WARM_GAIN_ONLY_COLD_COST_UNRESOLVED.
Exit0 means valid exact observations; it does not mean the adoption gate passed.

The completed relocation check used new source/capture copies, blocked opening
all original source/context paths, reproduced both original grade hashes and
then required exit 2 after altering one copied raw vector without changing its
seal. See qualification/relocation/RECEIPT.json. Those external regrade costs are
separate from the study. Original captures were untouched.

## Source and dependency availability

raw/contexts/{original,successor}/ includes every manifest-bound input/source
file and each original SHA256SUMS. The successor evaluator retains its embedded
MPL 2.0 notice and exact vendor/NOTICE.md attribution. Historical unbound bytecode
caches are excluded. Installed packages are not copied: actor reproduction would
require the exact external runtime files/distribution versions whose actual hashes
are in each manifest, and a new prospectively registered launch. The archived
LAUNCH.json paths describe historical launches and must not be rerun as a new study.

This packet supplies portable grading, not a new relocation/actor framework.
The standard qualification/synthetic-fixtures.tar.gz retains raw synthetic
controls; all earlier log/XML and source generations remain separately bound.
