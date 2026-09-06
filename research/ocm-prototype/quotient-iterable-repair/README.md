# Query-relative compression: quotient-check repair

Owners: #70 and #72; architecture #69; acceptance #38; integration #73.
Related synthesis: PR #92. This patch does not replace that note or create a new architecture lane.

## Scope

`quotient_admissible` accepts `Iterable[Iterable[str]]`. Previously it consumed the partition to create matrix indices and reused the same iterable for warrant measurability. An exhausted outer iterator skipped all blocks; exhausted inner iterators produced empty blocks. Thus a partition whose members have different LIVE/UNKNOWN/DEAD behavior could receive `ADMISSIBLE` (or `NOT_LUMPABLE` instead of `NEITHER`).

Materialize both iterable levels once so both checks inspect the same partition. Reject empty blocks at the partition boundary rather than accepting a partition that `lump` cannot construct. Replace repeated `ids.index` calls with one ID-to-index dictionary; unknown IDs still raise `ValueError` (with a clearer message).

This repairs the existing **navigation + registered-liveness predicate only**. It is not a complete proof of authority, semantic-query, intervention, or arbitrary future-revision preservation. Do not expand the meaning of `ADMISSIBLE` beyond the existing registered checks.

## Actual local validation

Source inspected at `29085f80c727f1cb47d3a76df39837b0b6a585d1`.

A full clone could not run because the container could not resolve GitHub. Five authentic modules were fetched through the GitHub connector, written locally, and each original file was verified against its Git blob hash before testing:

| Module | Original Git blob |
| --- | --- |
| abstraction.py | f8f33c5d23bed3dbf9de19801deb2205db57ed0f |
| space.py | 111238da15cbab330b8312168b7ca2e5f298ad96 |
| warrant.py | 6cf431adb2e7e45fe5e23122a482262e45e11211 |
| types.py | 94ecc413c176cb535b5529fe5c70876a6df1c664 |
| ids.py | f06e46e0a01d4f619398e631eac8475ea1b3c436 |

They were imported as a namespace-package source slice. No substitute implementations of liveness, types, or KnowledgeSpace were used. The repository package initializers, vendored modules, original full test suite, and qualification recorder were **not** run locally.

New focused suite before fix: **22 failed / 33 passed**.
Same suite after fix: **55 passed**.
One test enumerates 20 valid warrant intervals over two evidence atoms, all 400 interval pairs, all four revocations, and four iterable shapes: **6,400 verdict comparisons** against the defining liveness condition.

The ID-translation sentinel tests absence of repeated linear `.index` calls, not end-to-end speed. Translation becomes expected O(N + partition-members) with O(N) temporary indexing; the exact matrix and liveness checks remain separately costly. No sparse-cognition or speedup claim is made.

Reproduce in a full checkout:

```sh
PYTHONPATH=src python -m pytest tests/m1/test_abstraction_iterable_contract.py -q
```

## Qualification checklist

- [x] Preserve an authentic pinned pre-fix implementation for RED testing.
- [x] Exercise tuple, outer iterator, inner iterator, and nested iterator partitions.
- [x] Exercise all four quotient verdicts, late revocation, UNKNOWN, empty revocation families, malformed partitions, and empty state.
- [x] Exercise all 6,400 finite interval/revocation/shape combinations.
- [x] Remove repeated ID scans without claiming the whole checker is local.
- [ ] Run full repository M1 regression and current-source engineering qualification.
- [ ] Obtain independent review, including interactions with #90 and future compressed-field implementations.
- [ ] Rebind current engineering evidence through the repository's actual recorder, not by editing expected hashes or archived receipts.
- [ ] Merge only after the applicable gates pass.

## Why this arose from the ORION-Q audit

ORION #908 / PR #910 already earned a **bounded classical routing calibration** in a quantum compiler domain. The committed source receipt is:

`SzeChunYiu/ORION@962e9d264fe24780291ca8223b8da130ebd6cea9:research/extensions/orion-q/MAX_R4EA_AUTHORITY_INDEXED_ROUTER_RESULTS.json`

It selects representations of sizes 45, 54, and 715 according to the query. The 45- and 54-class summaries are not interchangeable and are not one nested hierarchy. Its 10/10 result explicitly grants no held-out transfer, autonomous skill-selection, broad quantum improvement, or novelty authority.

The reusable lesson is **check sufficiency before compression; preserve the distinctions required by the query and its evidence lifecycle**. The iterator defect violates that lesson before any quantum implementation is involved. Fixing it is a correctness prerequisite, not evidence that OCM beats a faithful classical parent.

ORION-V2 #205 remains closed at `NO_ELIGIBLE_OPERATOR`. This patch does not reopen it, execute a quantum circuit, or claim quantum advantage.
