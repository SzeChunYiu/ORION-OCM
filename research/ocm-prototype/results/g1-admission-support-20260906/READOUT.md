# Scope and custody

The change adopts existing `positive_activation_support` for admission's Boolean reachability decision at every size. Rational activation magnitudes and their fixed-point implementation remain available elsewhere and as the comparison oracle. The historical public threshold constant remains for compatibility but no longer dispatches admission. Recorded resource proxies remain unchanged for replay.

For the existing nonnegative, gated navigation contract, positive support follows reachable positive paths from gated positive seeds. This is reuse of an existing mechanism, not a new learning or sparse-revision result. The alpha=1 seed-only case remains part of the implementation contract.

## Evidence order

1. [Original profile](profile/profile-cumulative.txt): one repeated query on a copy of the actual final ledger, including replay. It reports 202 fixed-point calls taking 42.465 cumulative seconds under profiling, and 46.076 seconds in replay. [Caller records](profile/fixed-point-callers.txt) attribute 199 calls / 40.416 seconds to admission and 3 calls / 2.049 seconds to query navigation. Profiling perturbs runtime; these are not matched-run timing estimates.
2. [Before regression](tests/support-before.log): 2 failed / 2 passed; the failures assert admission should avoid magnitude solving at sizes 2 and 199. They diagnose an unnecessary computation path, not an observed wrong semantic answer.
3. [After regression suite](tests/support-after.xml): parent-executed 304 passed, 47.32 seconds. The [final focused suite](tests/support-final-optimization.xml), after the compatibility/scaling-report adjustment, records 42 passed, 0.10 seconds. Packaging did not rerun these suites.
4. [Final-source actual-ledger replay](replay-final/receipt-final.json): exact snapshots and event chains agree. It binds the original and final-support JSON records and reports all source state files unchanged. Original and revised timings are retained separately.
5. [Revised frozen stream](revised/receipt.json), [external grade](revised/grade.json): fresh native and OCM runs under the same frozen 100-syntax / 5-synthesis item order, model and tool contract, with restart every 21 items. The original receipt and grade remain unmodified in `original/`.

The earlier replay's [receipt](replay-prior/receipt.json) and support result precede the compatibility adjustment; their original-arm record and shared script are in `replay-final/`. The final-source replay is the primary comparison.

The first replay attempt failed before evaluation because its diagnostic script imported nonexistent `ocm.runtime.events`. Its empty `original.json`, traceback and script are preserved in `diagnostic-import-error/`. This is an explicit checker-development error, not a semantic failure or a successful check. The corrected script and successful records are separate.

## Function and costs

All 105 assigned items completed in both arms of both runs. Independent grading validates accepted outputs; admission alone is not accuracy. The syntax observation warrant means the frozen model emitted that tree, not that its tree is gold truth. The procedural checker separately enforces the accepted grammar and public universal specification.

Both syntax scores are UAS 1294/1584, base LAS 1234/1584, full LAS 1231/1584, UPOS 1487/1584, exact tree 32/100 and exact tree plus UPOS 30/100. The panel is balanced across genre and length, uses supplied token boundaries and includes punctuation. It measures supervised structural parsing, not semantic language understanding; sentences are not independent lifetime units.

Native final state is 11,826,796 bytes originally and 11,826,797 bytes in the repeat. OCM final state is 22,195,258 and 22,195,126 bytes respectively. These are stocks, not cumulative bytes written, and tiny serialization-size differences are not a compression claim.

`reaped_process_tree_cpu_s` includes worker imports, model archive/copy/reload, ledger replay, proposals, checking and persistence. It excludes training, installation, external grading, earlier failed attempts, hosted actors and energy. Thus it is not a whole-lifetime cost total. The model is 11,631,918 bytes; its parameter count remains `CANNOT_CHECK` and is not inferred from file size.

These are sequential development runs on a shared laptop, not randomized timing replications. The original OCM chunk 3 overlapped a separate donor evaluation for about two seconds; other qualification work could also contend for the host. Wall and CPU differences are descriptive. No confidence intervals, noninferiority conclusion or population efficiency inference is supported.

The CPU figure has one measured point per completed 21-item chunk; lines only connect those points. Its native curve is the revised run, 6.894266 seconds. Original native, 6.852394 seconds, remains in the source data and table; it is neither pooled nor omitted from the evidence.

Global navigation, whole-state hashing and replay remain in execution. The revised OCM total still greatly exceeds the adopted direct parent and its final chunk costs 40.902374 CPU seconds. This package does not measure the revised percentage attributable to each remaining stage, nor demonstrate sparse cognition.

## Content bindings and reproducibility

- Original production source identity: `518d7f135bdb6dac7a75ea73d539f9bcebaf24e152cf78466ae7c716303a940e`.
- Final support source identity: `59d70c4fdc4f45af4adf3c44e34fe78a05ad2f6d57c12601f743a54e61c997ee`.
- Frozen public items: `7ece4dd05bdc5c07caa88213fb5952b75f8a22e26bdc4a379bb83644cfaa48d0`.
- Model: `7bc9a92586cbac6ebd599b035f2f4d686edb7b000ffbed776a93d8e4a23eeea9`.
- External gold DEV: `dd514122385fd3374dd10051ddaf477c957d3da0bba48931d6f969820ece233f`.

Each raw receipt records source-file hashes, runner/worker hashes and custody paths. `origins.json` preserves the raw-copy source paths; those are provenance, not portable execution dependencies. Large model archives, corpus and state directories are deliberately not copied here; full actor replay requires their separately held, content-bound copies.

The actor receipts remain `EXECUTED_NOT_GRADED`; separate immutable grade files supply interpretation. The plot checks receipt/grade binding, complete CPU custody, row-file hashes and completed counts, then matches chunk totals to the grades. `package-check.json` also verifies raw-copy hashes and exact replay equality. These are packaging validations; they do not claim an independent rerun of the parent's production tests.

Use existing matplotlib 3.7.5 on the laptop to regenerate PNG/SVG/PDF: `python3 plot_cpu.py`. It reads only this directory and executes no model, solver, runtime or benchmark. Rebuilding changes rendered-file hashes; regenerate the inventory if publishing regenerated artifacts.

## Paper use

Potential figure: cumulative observed work before/after exact-support adoption, accompanying bounded preservation of donor function and actual-ledger replay semantics. Classification is `INFRASTRUCTURE` / `SUPPORTING` under #72, linked to #73/#69 and #50/#62/#42. It does not independently satisfy #38/#49 acceptance or establish a residual architecture advantage over a faithful persistent parent. Those claims require separate experiments.
