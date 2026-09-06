# Historical evidence restored after migration

Owner: #72 / #38 / #49. INFRASTRUCTURE; restoration of existing evidence only.

Commit `c750a0f0f1b452989b7e18baaf1513c51fe669e6` deleted exactly 19 historical research
files and added no replacement. It was merged without rewriting its history. The current verifier
then actually returned exit 1 with:

    CURRENT ENGINEERING REFUSED: MISSING required evidence: research/orion-machine/design/00_INDEX.md

The 19 paths below were restored byte-for-byte from `68b444b094e26f35628eaa14a3dc2f42eda98ff8`.
Total restored size: 344,725 bytes. Both byte comparisons and Git blob identities matched. No new
files from the migration were overwritten, and no historical result was regenerated.

Before this note was added, the complete restored Git index tree exactly equaled the already
verified `9c547fbdf1bd4d753b050dbf5982ee82685049c8` tree:

`8b3d9e0620d0dfde0b4bdbe27c8afd3ffc0c5634`

Current source digest remained `33e7bb0a24b773b6c5261183dc37efba312418625eafffbbf67b0b6812c51b83`.
All twelve milestone wrappers passed, and V4/V5 predecessor custody passed. The existing 133-test
focused and 979-test full replay remains applicable to the identical source and bound artifacts;
no full suite was rerun for this restoration. Protected evaluation was NOT_RUN and scientific
promotion remains NOT_ESTABLISHED.

[Raw before/after command receipts and file hashes](MIGRATION_CUSTODY_RESTORATION_V1.json).

| Restored original path | Original Git blob SHA1 |
|---|---|
| research/orion-machine/design/00_INDEX.md | `bc85f7fe3fd5aefdadf7488b5979b4503c631fde` |
| research/orion-machine/design/01_STRUCTURES.md | `1528867ade1f637b9236da7caa549f0d2f4b25a2` |
| research/orion-machine/design/02_MATHS.md | `f02b4f83f4463ba0c35091cd1dcf7edbd611e7f0` |
| research/orion-machine/design/03_DYNAMICS.md | `ef5d87de2e5510e56c15420a2b44f07c0bef41a4` |
| research/orion-machine/design/04_ALGORITHMS.md | `08f97a104092859e75556e03e205093b1af39004` |
| research/orion-machine/design/05_MECHANICS.md | `2163c52cd7594d17dd42d5a2d37efe3e5d403f11` |
| research/orion-machine/design/06_ARCHITECTURE.md | `f89b3f2d27df37949728994135025c389c32c296` |
| research/orion-machine/design/07_ABSORPTION.md | `242f5a9cbda7bb057275ba7356993f570d4d309f` |
| research/orion-machine/design/08_PARENTS.md | `39609e8f15b5d8882f66338a95542b1fcc7b4ab2` |
| research/orion-machine/domains/algebra/ALGEBRA_SOURCE_V1.json | `68178acbd025404b95f38ea6363d4e8fab2adb1d` |
| research/orion-machine/domains/algebra/ALGEBRA_SOURCE_V1_SUPERSEDED_RECONSTRUCTED.json | `4a94c5ea02ca2665c11e0a041115f7f02cba0a9c` |
| research/orion-machine/domains/algebra/ALGEBRA_SOURCE_V3.json | `97d9bd3dd25655e086a564b49d3d742c23c4eea6` |
| research/orion-machine/results/KSO_M2B_ALGEBRA_OUTCOME_V1.md | `af95b1c71893e9108d74ff7b36497bcfe5267d96` |
| research/orion-machine/results/KSO_M2B_ALGEBRA_OUTCOME_V3.md | `47eba70f528958c0486b04ee492930c25b21c3f8` |
| research/orion-machine/results/KSO_M2B_ALGEBRA_RECEIPT_V1.json | `4ebe026aca0db33bd9f8cccb4442d541b89aee9c` |
| research/orion-machine/results/KSO_M2B_ALGEBRA_RECEIPT_V3.json | `1d9263e559308ebe6298824aa1068ea6cb462ad3` |
| research/orion-machine/results/KSO_M2B_DESIGN_V2.json | `713372a0eafe88e66fc633441e97bfabbf692ac8` |
| research/orion-machine/results/KSO_M2B_DESIGN_V3.json | `e644d9704f6d68ef1776dcde81f6a30704c34e86` |
| research/orion-machine/results/KSO_PARAMETER_STUDY_V1.json | `208bcc5f3ddf04538d9621e96031e28b114be547` |
