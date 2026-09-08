# Repeated migration deletion: exact evidence restoration

The normal merge preserves upstream commit
`92310f13b2587871242b93c1ab59324a42a7cc2b` and its parent
`c14b0026853da0d5fd01cb1cad3b3e9ada099011`.
The upstream commit removed the same 19 historical files recorded in the
[previous restoration](MIGRATION_CUSTODY_RESTORATION_V1.md).
The previous incident and all original scientific receipts remain unchanged.

## Actual failure and cause

On the merged branch, `python -B tools/m1_receipt.py --verify` returned exit 1:

    CURRENT ENGINEERING REFUSED: MISSING required evidence: research/orion-machine/design/00_INDEX.md

The milestone wrapper verifies the current engineering record, whose predecessor
custody verifier requires the original historical inputs. The missing evidence is
therefore an integration failure even though the donor's 385 source inputs match.

The repository-owned one-shot workflow still deleted `research/orion-machine`,
replaced it with the older pinned ORION-V2 tree, and pushed directly to main.
Its self-file push trigger made a completed migration runnable again. The new
commit's message and author match this recipe; that observation alone does not
identify an external invocation or runner.

## Repair

All 19 files are restored from the exact `c14b002` Git blobs: 344,725 bytes total.
Their byte counts, SHA256 values, Git blob identities and 100644 modes match the
[prior restoration map](MIGRATION_CUSTODY_RESTORATION_V1.json).
No old result is regenerated, no receipt/check is weakened, and upstream ancestry
is retained. The completed `.github/workflows/migrate-ocm-stack.yml` is removed.
Its full recipe remains in Git history. It can no longer run through the current
repository's workflow; an external checkout of old code is outside this change.

## Current qualification

After restoration, all 12 `tools/mN_receipt.py --verify` commands return zero.
The existing M12 archive qualification has 13 passes and no failures/errors/skips,
including no-regeneration and receipt/preregistration/archive tamper controls.
All 352 engineering code inputs and all 385 donor qualification inputs remain
byte-identical. The donor's preceding 104-pass qualification is retained as
unchanged-source evidence; it is not relabelled as a rerun on this merge.
Protected reevaluation and historical recipe execution are NOT_RUN.

Raw records are external at
`/home/billy/orion-director-work/20260907/unary-clause-revival-qualification-v1/17-migration-repair/`.
The red M1 stdout, all command/exit/raw records, JUnit, source maps and exact
restoration map are preserved there.

- RESULT.json SHA256: d3f1b7c9159ce2e0f2e04de16c4f2e71dbe7c59d65c4c754a2dae5c5172cb43d.
- RESTORED.json SHA256: fdc2f793c9b8298e8f7f18f6c37cac15a5fc709a3a37dc3320038fdeb74baa44.
- SOURCE-AFTER.json SHA256: bea8575f0b0ad53940749243a52c6bda055cacb1af14ac155b77267577479a0b.
- Prior restoration map SHA256: b0c21d6b7d49f7cc80e77c6845b8fc92cdeb395b2df629eff305403e8a3fc193.
