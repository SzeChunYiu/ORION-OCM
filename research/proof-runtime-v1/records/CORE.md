# Proof/runtime records

Read this file first. This archive records one exposed F0 lifecycle commissioning.

- **Native result:** 24 phases passed; two OCM solve/admit routes; two worker runs, eight Lean phases and three cold readers.
- **Target:** `F0Target.statement`, freshly checked by Lean 4.33.1 in both routes; constructed proof axiom lists are empty.
- **Lifecycle:** discovery A is separate from correctness B/C; both routes share environment S. Revocation/reinstatement and unbound cold reads are recorded.
- **Qualification:** final 96 focused controls and 1,303 core engineering tests passed, zero failures/errors/skips; these are engineering tests.
- **Costs:** driver outer wall 42.449141277 s; GNU time elapsed 42.54 s, user 31.22 s, system 6.98 s, reported maximum RSS 90,676 KiB.
- **Cost scope:** earlier runtime acquisition/preparation and final result serialization are outside driver wall. Nested costs overlap; reported RSS is not simultaneous aggregate system memory.
- **Claim scope:** typed symbolic construction and authenticated lifecycle integration. No learned method, LLM superiority, scaling, FLT or completed research-programme claim.

## Core evidence

- [Archive contract and counts](commissioning-20260907/ARCHIVE.json)
- [Native result](commissioning-20260907/raw/result.json)
- [Frozen sources and inputs](commissioning-20260907/raw/freeze.json)
- [Actual parent launch and imports](commissioning-20260907/raw/parent.json)
- [Final record audit](commissioning-20260907/supporting/audit-v2/AUDIT.md)
- [Independent semantic review](commissioning-20260907/supporting/reviews/proof-runtime-native-claim-review.md)
- [Supporting input identities](commissioning-20260907/SUPPORTING_INPUTS.json)
- [Qualification evidence](commissioning-20260907/supporting/qualification/proof-runtime-engineering-evidence.json)

## Custody and retention

The original native tree contains 313 files / 14,402,274 bytes.
This archive preserves 307 raw files / 13,754,530 bytes unchanged.
Six `.olean` bodies / 647,744 bytes are represented by [exact hashes and sizes](commissioning-20260907/OMITTED.json).
No `__pycache__` files are present in the native tree.
The original complete tree remains at `/home/billy/orion-director-work/20260907/proof-runtime-commissioning-20260907`.
This is an evidence bundle: metadata-only compiled files and relocated paths cannot satisfy the original live custody API.
[Original full inventory](commissioning-20260907/supporting/audit-v2/RAW_INVENTORY.json) preserves all 313 identities.
[Top-level seal](SHA256SUMS) binds every archived file except itself.

The native result SHA256 is `c1d93fa010515a97f8746bd53252253c8b7d46a95c1c8e78222a023d0ae2f5da`.
The source/input freeze SHA256 is `f71f9053b8dd2270c9a41bcb4e4415f26cc5ee03d1c49b04ae035f5e0f2d5b8f`.
The native runtime manifest SHA256 is `93aa17a738a8511bbb8996eff91e81da0ec5868db50d0f81ab26809e38661894`.

Supporting development RED/repair records include corrected audit-helper assumptions; they are not extra native trial failures.
The environment folder retains readiness, requirement hashes and timing scope only; installation bodies remain outside this archive.
