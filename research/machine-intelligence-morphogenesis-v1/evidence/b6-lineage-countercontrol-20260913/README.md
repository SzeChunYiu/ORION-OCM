# B6 primary-lineage countercontrol

This packet preserves the exact original countercontrol and its source.
It tests a single pinned crossover: TABLE primary plus DENSE donor produces a
DENSE child, while the original assignment retains only the TABLE primary root.
No search, ecology evaluation, atrophy, or admissibility test is performed.

`COUNTERCONTROL.json` has no machine paths or runtime-dependent identifiers.
`PINNED_SOURCE.zip` contains the 13 package modules at original commit
`5378c2b7f91f8fbc567764a2ee0c5ff6e256e814`, including the unchanged
crossover primitive. `SOURCE_BINDINGS.json` binds each extracted member.
`MANIFEST.json` binds every packet file except itself.

Run with CPython 3.12; the output filename must be new:

```sh
python3 replay.py --output /tmp/b6-lineage-replay-unique.json
```

The script needs no checkout history, network or dependencies. It imports the
pinned package from a temporary directory and requires exact receipt bytes.
The primary-origin expression is reproduced directly from b1.search; the search
loop is not executed. A mismatching expected receipt returns exit status 1.

The negative control supplies `--expected` with a copied receipt falsely
claiming the child's primary origin is donor seed1. The replay must retain
primary seed0 and reject that altered expected result. This is a semantic
mismatch control, distinct from merely detecting damaged source bytes.
`VALIDATION.json` records both runs and binds the script and original receipt.
See [the correction](../../B6_LINEAGE_ATTRIBUTION_CORRECTION_V1.md) for the
scientific scope, source interpretation and constructive provenance repair.
