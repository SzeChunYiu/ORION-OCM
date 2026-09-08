# G2 macro reuse: source and aggregate reconciliation

PR192 supplies a bounded causal-use witness for a conventional learned macro. The equally equipped ordinary persistent parent achieves the same result. Programme wording should acknowledge this positive mechanism result while keeping architecture benefit, full cost recovery and the Metamath lane separate.

## Exact read scope

- Merged source: [PR192](https://github.com/SzeChunYiu/ORION-OCM/pull/192), commit 0cd4f4c541491a386677ffd91a97c83d49562dc0, tree 827648ea91963e506d9e51b661a47f70b7a0fc0a.
- Full study source, README, nine-control source and workflow read; immutable copies and Git blob identities are in [bindings](BINDINGS.json).
- Main push run [34280814977](https://github.com/SzeChunYiu/ORION-OCM/actions/runs/34280814977), attempt 1, completed successfully. Artifact 10077609834 has SHA256 7337eaefdb602d4735600d113119d790d1e56619b3d04c8c577edbed9c97b790.
- The archive's result member is 563,119 bytes, SHA256 896b39429a4fd520cfc7517e73cdd0efb27518a83d7e31f9e6cf99560401db49. Only aggregate fields were interpreted; no per-task outcomes or validation/test identities were inspected. [AGGREGATES.json](AGGREGATES.json) preserves the selected fields.
- No study, control, target import, native verifier or new evaluation was executed. This is source/aggregate reconciliation, not independent per-task replay.
- PR193 was OPEN at metadata read, head c9cd1fbd4030df9843588f46f49510dcd61a14e1. Its independent-composition study is prospective here.

## What causal reuse is supported

The code chooses 48/32/64 distinct polynomial identities by minimum primitive lengths 6/7/8 and fixed salts. It mines repeated proper contiguous fragments of length 2–4 from exactly solved training programs, then selects among the fixed top 16 by validation first-hit rank. See experiment.py lines 59–123 and 211–273.

The chosen fragment is square, dec, square, supported by 12 training tasks. Validation rank work is 392,674 versus 485,273 primitive. The fragment becomes a macro token in the same exact polynomial search grammar; returned words expand before normal-form verification (lines 126–201).

Published test aggregates are:

| Arm | Enumeration-rank sum | Unique-check-rank sum |
|---|---:|---:|
| Primitive | 3,610,299 | 3,610,299 |
| Ordinary persistent macro | 3,334,970 | 3,099,083 |
| OCM live macro | 3,334,970 | 3,099,083 |
| OCM revoked | 3,610,299 | 3,610,299 |

There are 13 strict wins with actual macro use and 51 harmed tasks. The aggregate rank saving is 275,329 (7.6262%). These values are the published aggregates, not a newly inspected task ledger. The compare_rows function counts both directions and requires macro use for the causal win (369–380); the success terminal checks macro selection, ordinary equality, withdrawal equality and aggregate rank improvement (461–480).

The content survives ordinary JSON reload or OCM persistence followed by a new runtime-object reconstruction in the same process. Withdrawing training support makes the OCM macro unavailable and returns the primitive grammar (276–366, 434–459). This is actual acquired-content consumption and an authority-withdrawal intervention; it is not merely successful serialization.

The nearest equally equipped parent is the implemented ordinary persistent macro store with the identical selected fragment and search algorithm. Published equality covers task identity, rank counters, expanded program and token word (383–391, 447–459). The source constructs every arm from the same fixed test tuple. No OCM-specific search advantage over this parent is established. This parent is a concrete conventional baseline; it is not a completed benchmark against Stitch or every library-learning system.

## Costs and one concrete wording correction

The registered selected-path coordinate is:

174,521 training slots + 485,273 primitive validation ranks + 8,525,253 all-candidate validation ranks + 3,334,970 OCM test ranks = 12,520,017.

It exceeds primitive test work of 3,610,299, yielding the published NO_LIFETIME_MACRO_SEARCH_PAYBACK_AT_64_LENGTH8_TESTS terminal (482–495, 547–558). This includes all candidates in the declared rank sum, not every acquisition/storage/control or machine resource cost.

The full study records 94.311728 internal wall seconds. GNU time records 94.77 wall, 94.63 user, 0.11 system seconds and 143,056 KiB peak RSS. Candidate index construction is 27.271418 seconds, nested in the study. The two retained nine-control runs took 10.916 and 11.084 seconds; they are separate qualification work. None is a per-task serving-time comparison.

**Correction task G2-COST-WORDING-01:** README line 98 says overlong prefixes are pruned before descendants are generated. Actual build_search_index enumerates full token words, expands each, then skips overlong words (159–168); there is no prefix-pruning generator. It builds the entire bounded index before task lookup. Returned task counters are first-hit positions captured while building that index (170–208), not observed repeated online searches.

Correct the prose to “full words are expanded, then overlong words are excluded from the admissible first-hit rank counter,” or implement prospective prefix pruning in a separately frozen successor. Keep the current result unchanged. The rank ordering/parity and bounded causal consumption remain interpretable; the 7.6262% rank saving must not be advertised as measured serving-time speedup. Work on rejected words, full index construction, population enumeration and mining is only partly represented by the rank coordinate, though included in overall study wall time.

**Future guard task G2-PARITY-LENGTH-01:** rows_equal uses all(zip(...)) without first checking equal lengths (383–391). Empty or truncated arguments can therefore pass in isolation. In this frozen run every arm is built by evaluate_index from the same 64-task tuple, so this is not evidence that recorded parity is false. Before reusing/refactoring the guard, require equal lengths and meaningful empty/truncated rejection controls; no new control is run in this review.

## Programme wording

Suggested current statement:

> A training-derived polynomial macro is causally consumed after persistence and runtime reconstruction, with 13 strict macro-use wins and lower aggregate search rank on 64 length-8 tasks. An equally equipped ordinary persistent parent matches OCM exactly, and acquisition/selection does not repay its registered search work at this horizon. Independent learned-method composition remains prospective.

Avoid saying that no acquired executable method has ever been causally used anywhere in OCM. The narrower Metamath opportunity screen still has zero native admissions and no demonstrated learning utility; this polynomial result does not promote its cuts. Distinct polynomial identities and length strata establish this bounded within-domain transfer, not source-family independence, language transfer, global learning utility or architecture novelty.
