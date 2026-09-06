# QG to OCM: finite query-relative views (developer calibration)

Owners: #70 compression, #72 navigation, #69 vessel. This is an executable follow-on to the existing verifier-guided science synthesis in #92, not a new architecture or a replacement for #38/#73 acceptance.

## What is being adopted

ORION #908 / MAX-R4E-A already implements query-scoped authority-indexed representation routing. Its frozen compiler result chose among 45-class bulk, 54-class spectrum and 715-class indexed-response views; the first two partitions are incomparable. The source records 10/10 correct B2 minimum-authorized routes and 7/7 compact opportunities, with no held-out transfer, general quantum advantage or OCM novelty claim. See https://github.com/SzeChunYiu/ORION/issues/908 and its receipt `research/extensions/orion-q/MAX_R4EA_AUTHORITY_INDEXED_ROUTER_RESULTS.json` at ORION commit `962e9d264fe24780291ca8223b8da130ebd6cea9`.

The transferable rule is **choose the cheapest representation sufficient for this query and its required revision/scope observations; otherwise refine or abstain**. This is classical computation inspired by our quantum-research artifacts, not a quantum computer. ORION-V2 #205 currently records `NO_ELIGIBLE_OPERATOR`; this prototype does not reopen that gate.

The storage parent here is ordinary dictionary encoding with packed integer membership, available in mature systems such as Apache Arrow: https://arrow.apache.org/docs/format/Columnar.html#dictionary-encoded-layout . The module is a small standard-library reference calibration, not a new production database. Adopt a mature backend if this contract survives real workload tests.

## Finite mathematical contract

For finite source states X and registered observations Q, define `x ~Q y iff every q in Q has q(x) == q(y)`. Equal response signatures are exactly the quotient classes for those observations. Adding required observations refines the partition; changing the question can require an incomparable view, not merely a deeper node of a universal tree.

`compile_view` groups selected observation signatures and stores packed IDs. `verify_view` independently compares every decoded response to the supplied source snapshot and checks its identity. `select_view` chooses minimum encoded-payload size among current host-validated views that cover all requested observations. A missing observation produces `REFINE_REQUIRED`; source drift requires revalidation. This is a single explicit storage objective, not a universal Pareto optimum.

A current-answer-only summary is not a lifecycle-safe summary. The test with three currently LIVE states has one current-answer class, but three different responses after one withdrawal: DEAD, LIVE and UNKNOWN. Those distinctions must be retained for that withdrawal question, or the machine must decline to answer from the coarse view.

## Core correctness repair included in this branch

At OCM base `29085f80c727f1cb47d3a76df39837b0b6a585d1`, `quotient_admissible` traversed a partition twice. An outer or inner generator could be exhausted before warrant measurability, making the second condition vacuous. The fix snapshots the partition once and freezes every registered revocation scenario. It also replaces repeated linear ID searches with an ID-position dictionary and avoids a full `atom_map()` copy in a small warrant check. Cold structural-index construction and the dense lumpability matrix are still charged whole-space work; no end-to-end sparse bound is claimed.

The new 20-case regression suite covers iterable forms, complete/partial warrants, one-shot inputs, invalid partitions, unknown atoms, and simultaneous failures. The first RED CI run (`34024731726`) also contained a test-fixture error: `WarrantProfile.of("left")` names character evidence, not the singleton ID. That was corrected to `of({"left"})`. Against the unchanged real source, the corrected 19-test suite produced **10 failed / 9 passed** locally. After the repair plus one no-copy sentinel, **20 passed** locally. Keep the initial CI artifact as history; do not describe its 11 failures as eleven independent valid defects. Full CI results belong in the PR/checks, not inferred from these local checks.

## Reproduce

```sh
PYTHONPATH=src python -m pytest -q tests/m1/test_quotient_iterable_safety.py
python -m unittest discover -s research/qg-transfer -p 'test_*.py' -v
python research/qg-transfer/diagnostic.py
```

The 16 standalone tests include 768 exhaustive finite table/view combinations, incomparable views, finer-query refusal, three-valued withdrawal observations, source drift, fabricated signatures/membership, caller mutation, row-order/length changes and unsigned-ID width boundaries.

## Storage diagnostic, not an OCM advantage

A local Python 3.13.5 run over one million repetitions of 16 three-column signatures produced:

- source JSON-lines encoding: **41,375,045 bytes**;
- actual packed-view encoding: **1,000,787 bytes**, including **1,000,000 membership bytes** and the dictionary/header;
- retaining both source and view: **42,375,832 bytes**, an increase over source alone;
- compile about **2.88 s**, independent full-source verification about **3.40 s**, 10,000 cached-snapshot lookups about **0.00449 s** on that host.

This is deliberately easy repetitive synthetic data, not learned competence or a protected benchmark. The same standard dictionary parent explains the result. Do not compare packed bytes to LLM weights, infer a universal compression ratio, call this a million-knowledge-item OCM, or omit archives/metadata/temporary buffers. The temporary 64-bit membership array alone uses 8N bytes; packing, serialization, Python objects and retained source add further peak memory. The full source is scanned on build and validation. These timings are one developer measurement, not stable performance promises. Terminal: `PARENT_SUFFICIENT_DICTIONARY_ENCODING_DEVELOPMENT_ONLY`.

## Deliberate limits

No learned routing, quantum hardware, LLM, empirical validator, proof of arbitrary program equivalence, or runtime registration is included. A plain view object and a hash do not confer authority: the host must run the source checker before registering a view and must supply a trustworthy current source identity. This is not a security boundary. Global snapshot invalidation is conservative and not local revision. Future revocations not enumerated among the observations are not covered. The finite observation verifier does not establish navigation lumpability; the KSO gate remains a separate obligation. Incompressible data may give no saving. Choosing observations correctly is still a correspondence problem.

## Executable integration checklist (existing owners only)

- [x] Isolate the real KSO generator bug with tuple/generator and valid/invalid controls.
- [x] Repair shared-partition validation without relaxing warrant/lumpability conditions.
- [x] Build a stdlib packed-view parent with independently checked responses.
- [x] Test incomparable views and required lifecycle distinctions.
- [x] Expose source/archive costs and abstain outside the checked finite scope.
- [ ] Finish source-bound engineering qualification and independent PR review; do not edit frozen receipts to force green.
- [ ] Bind a registered view to actual KSO source identity, operator/checker versions, query family, authority, scope, expiry and revocation dependencies.
- [ ] Keep READ/PROPOSE separate from ADMIT/COMMIT; no plugin or quantum donor may self-certify.
- [ ] Compare ordinary dictionary/Arrow, strongest native query-indexed router, and OCM with identical information and lifecycle requirements.
- [ ] Use real OCM language/procedure traces, held-out families and negative-transfer cases; do not promote synthetic repetition as language learning.
- [ ] Measure build/verify cost, cold/warm navigation, total/index/active/archived bytes, lookup work, stale survivors and local update work together.
- [ ] Replace global binding only after chunk-level dependencies and suffix/epoch updates have independent correctness tests.
- [ ] Test when an extra summary is worthwhile over its expected uses; reclaim unused views while retaining required provenance and reconstruction.
- [ ] Add partition-refinement/joint-view construction only if ordinary query planning is insufficient; test worst-case partition explosion.
- [ ] Preserve `PARENT_SUFFICIENT`, `NO_COMPRESSION`, `REFINE_REQUIRED`, `STALE_SOURCE` and `CANNOT_CHECK` outcomes.
- [ ] Only #73 may translate fresh matched evidence into bounded LLM-comparability claims.
