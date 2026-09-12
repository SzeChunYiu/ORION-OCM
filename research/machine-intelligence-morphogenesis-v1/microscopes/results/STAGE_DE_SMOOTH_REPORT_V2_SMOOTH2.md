# Stage D'/E' — smooth-generalization ecology: report V2_SMOOTH2

Target coefficients [0.5, -0.5, 0.25, 0.75]. Receipt `STAGE_DE_SMOOTH_V2_SMOOTH2.json` (sha256 `1f69d3294e90c832…`). 16 inputs, 8 seen; θ = 0.85; rows S4 (gradient net), S2 (exact linear search, grammar of 2401), S5 (exemplar memory), S3 (particles over the grammar).

## Capability after the protocol (largest ladder size, by column)

| row | B0 | B1 | B2 | B3 | U | P3 |
|---|---|---|---|---|---|---|
| S4@4 | 0.7578 | 0.7578 | 0.7578 | 0.7578 | 0.7578 | 0.7578 |
| S2@4 | 0.4167 | 0.4167 | 0.4167 | 0.4167 | 0.4167 | 0.4167 |
| S5@4 | 0.7917 | 0.7917 | 0.7917 | 0.7917 | 0.7917 | 0.7917 |
| S3@8 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 |

C2 (Dev tables identical across columns): True

## PH-REV on E_smooth (frozen prediction E' in CLAIM_LADDER_V2)

- **B0**: NOT_OBSERVABLE__NO_DENSE_ROW_ON_FRONTIER (dense rows below theta or dominated at r=0) — winners by r at H=16: {'0': [], '1': [], '2': [], '4': [], '8': [], '16': [], '32': []}
- **B1**: NOT_OBSERVABLE__NO_DENSE_ROW_ON_FRONTIER (dense rows below theta or dominated at r=0) — winners by r at H=16: {'0': [], '1': [], '2': [], '4': [], '8': [], '16': [], '32': []}
- **B2**: NOT_OBSERVABLE__NO_DENSE_ROW_ON_FRONTIER (dense rows below theta or dominated at r=0) — winners by r at H=16: {'0': [], '1': [], '2': [], '4': [], '8': [], '16': [], '32': []}
- **B3**: NOT_OBSERVABLE__NO_DENSE_ROW_ON_FRONTIER (dense rows below theta or dominated at r=0) — winners by r at H=16: {'0': [], '1': [], '2': [], '4': [], '8': [], '16': [], '32': []}
- **U**: NOT_OBSERVABLE__NO_DENSE_ROW_ON_FRONTIER (dense rows below theta or dominated at r=0) — winners by r at H=16: {'0': [], '1': [], '2': [], '4': [], '8': [], '16': [], '32': []}
- **P3**: NOT_OBSERVABLE__NO_DENSE_ROW_ON_FRONTIER (dense rows below theta or dominated at r=0) — winners by r at H=16: {'0': [], '1': [], '2': [], '4': [], '8': [], '16': [], '32': []}

P2 exact at a 16-input, 8-bit scope; one target; frozen cost model; the S2 grammar contains the target by construction (declared), which is the exact-search advantage the Abbe/Shalev-Shwartz reading predicts.

## RV-377-009 clause (iv): analytic r* from E_smooth vs observed crossing here

- **B0**: predicted r* 1.195, observed crossing None, both admissible {'S2': False, 'S4': False}, within one grid step: None
- **B1**: predicted r* 0.819, observed crossing None, both admissible {'S2': False, 'S4': False}, within one grid step: None
- **B2**: predicted r* None, observed crossing None, both admissible {'S2': False, 'S4': False}, within one grid step: None
- **B3**: predicted r* 1.195, observed crossing None, both admissible {'S2': False, 'S4': False}, within one grid step: None
- **U**: predicted r* 0.479, observed crossing None, both admissible {'S2': False, 'S4': False}, within one grid step: None
- **P3**: predicted r* 0.479, observed crossing None, both admissible {'S2': False, 'S4': False}, within one grid step: None
