# Correction and evidence boundaries

The reviewed PR158 snapshot is head `1f6a975b5921da4109dd2286ac030613a55e8261`. These patches are based on that preserved source. No live PR branch was changed by this capsule; integration must account for its actual current source.

The numerical correction reuses the pinned PR159 `_rational` and `_items` functions. Finite `int`, `Fraction` and represented binary-float inputs use exact rational arithmetic; this is not arbitrary-real arithmetic. The DRD recurrence still minimizes worst-case cost over proper finite terminating trees. It was not replaced with an expected-cost decision process. Input/STOP assumptions are explicit in the [model contract](source/research/paid-decision-region-v1/EXACT_MODEL_CONTRACT.md).

The maintenance guard accepts only two built-in integer zeros. The source inventory covers exactly:

- `research/developmental-spine/dev6_arms.py`;
- `research/developmental-spine/run_dev6.py`;
- `research/developmental-spine/dev6.py`.

The existing inventory checks their source bytes. The final successor also validates the actual loaded `dev6` module path before the runner uses sweep configuration; the other two path checks were already present. This is not full transitive runtime/commitment closure or a claim of arbitrary in-memory object immutability.

The historical 15-control Linux receipt remains evidence for the unchanged numeric, maintenance and earlier custody implementation. The successor changes only two runner lines; the other 13 source files remain byte-identical. Its single affected test evaluates only extracted import/path-check wiring with synthetic cached modules. It records predecessor shadow acceptance, successor refusal before consumption, and clean acceptance. PID 2086253 exited 0 and was reaped, with zero attempts to import real donor modules and unchanged source hashes.

The original independent review's one blocker is retained openly; the separate closure accepts its narrow repair. Historical RED generations and the original PR158 source review remain in RAW. This is 15 earlier controls plus one later affected control, not a newly rerun 16-case suite.

Fraction serialization, actual donor/adapter qualification, complete runtime/lifetime costs, portable CI integration and runtime adoption remain separate work. No published aggregate result, native evidence, parent comparison or novelty conclusion changes.

The direct source/control/receipt copies are for inspection. Their embedded original paths are historical identities; use the copy map and RAW member map to locate those contexts. Packaging relocates no execution authority. RAW retains the complete original directory-relative layouts, including preimages, patches, controls and all reviews. The unchanged workflow is a source snapshot inside `source/`, not newly installed CI.

The 406-line historical paid-region source note is retained exactly in RAW and the full patch; [its omission record](OMITTED-DIRECT.json) identifies the bytes. All current Python sources remain directly inspectable.
