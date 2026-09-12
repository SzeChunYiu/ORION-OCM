# Stage D'/E' — smooth-generalization ecology: report V5_PARITY_PH5

Target coefficients (none: parity target, PH-5 control). Receipt `STAGE_DE_SMOOTH_V5_PARITY_PH5.json` (sha256 `3d06b523f1b65a40…`). 16 inputs, 8 seen; θ = 0.85; rows S4 (gradient net), S2 (exact linear search, grammar of 2401), S5 (exemplar memory), S3 (particles over the grammar).

## Capability after the protocol (largest ladder size, by column)

| row | B0 | B1 | B2 | B3 | U | P3 |
|---|---|---|---|---|---|---|
| S4@4 | 0.2448 | 0.2448 | 0.2448 | 0.2448 | 0.2448 | 0.2448 |
| S2@4 | 0.3333 | 0.3333 | 0.3333 | 0.3333 | 0.3333 | 0.3333 |
| S2a@4 | 0.3333 | 0.3333 | 0.3333 | 0.3333 | 0.3333 | 0.3333 |
| S5@4 | 0.3333 | 0.3333 | 0.3333 | 0.3333 | 0.3333 | 0.3333 |
| S3@8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

C2 (Dev tables identical across columns): True

## PH-REV on E_smooth (frozen prediction E' in CLAIM_LADDER_V2)

- **B0**: NOT_OBSERVABLE__NO_DENSE_ROW_ON_FRONTIER (dense rows below theta or dominated at r=0) — winners by r at H=16: {'0': [], '1': [], '2': [], '4': [], '8': [], '16': [], '32': []}
- **B1**: NOT_OBSERVABLE__NO_DENSE_ROW_ON_FRONTIER (dense rows below theta or dominated at r=0) — winners by r at H=16: {'0': [], '1': [], '2': [], '4': [], '8': [], '16': [], '32': []}
- **B2**: NOT_OBSERVABLE__NO_DENSE_ROW_ON_FRONTIER (dense rows below theta or dominated at r=0) — winners by r at H=16: {'0': [], '1': [], '2': [], '4': [], '8': [], '16': [], '32': []}
- **B3**: NOT_OBSERVABLE__NO_DENSE_ROW_ON_FRONTIER (dense rows below theta or dominated at r=0) — winners by r at H=16: {'0': [], '1': [], '2': [], '4': [], '8': [], '16': [], '32': []}
- **U**: NOT_OBSERVABLE__NO_DENSE_ROW_ON_FRONTIER (dense rows below theta or dominated at r=0) — winners by r at H=16: {'0': [], '1': [], '2': [], '4': [], '8': [], '16': [], '32': []}
- **P3**: NOT_OBSERVABLE__NO_DENSE_ROW_ON_FRONTIER (dense rows below theta or dominated at r=0) — winners by r at H=16: {'0': [], '1': [], '2': [], '4': [], '8': [], '16': [], '32': []}

P2 exact at a 16-input, 8-bit scope; one target; frozen cost model; the S2 grammar contains the target by construction (declared), which is the exact-search advantage the Abbe/Shalev-Shwartz reading predicts.

