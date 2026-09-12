# Stage D'/E' — smooth-generalization ecology: report V34_SYMn1_H

Target coefficients [-0.0625, -0.0625, -0.0625, -0.0625]. Receipt `STAGE_DE_SMOOTH_V34_SYMn1_H.json` (sha256 `345c2bcdce6ac3ac…`). 16 inputs, 8 seen; θ = 0.85; rows S4 (gradient net), S2 (exact linear search, grammar of 2401), S5 (exemplar memory), S3 (particles over the grammar).

## Capability after the protocol (largest ladder size, by column)

| row | B0 | B1 | B2 | B3 | U | P3 |
|---|---|---|---|---|---|---|
| S4@4 | 0.7604 | 0.7604 | 0.7604 | 0.7604 | 0.7604 | 0.7604 |
| S2a@4 | 0.9375 | 0.9375 | 0.9375 | 0.9375 | 0.9375 | 0.9375 |
| S5h@4 | 0.9792 | 0.9792 | 0.9792 | 0.9792 | 0.9792 | 0.9792 |
| S5@4 | 0.9167 | 0.9167 | 0.9167 | 0.9167 | 0.9167 | 0.9167 |
| S3@8 | 0.6458 | 0.6458 | 0.6458 | 0.6458 | 0.6458 | 0.6458 |

C2 (Dev tables identical across columns): True

## PH-REV on E_smooth (frozen prediction E' in CLAIM_LADDER_V2)

- **B0**: NOT_OBSERVABLE__NO_DENSE_ROW_ON_FRONTIER (dense rows below theta or dominated at r=0) — winners by r at H=16: {'0': ['S5'], '1': ['S5'], '2': ['S5'], '4': ['S5'], '8': ['S5'], '16': ['S5'], '32': ['S5']}
- **B1**: NOT_OBSERVABLE__NO_DENSE_ROW_ON_FRONTIER (dense rows below theta or dominated at r=0) — winners by r at H=16: {'0': ['S5'], '1': ['S5'], '2': ['S5'], '4': ['S5'], '8': ['S5'], '16': ['S5'], '32': ['S5']}
- **B2**: NOT_OBSERVABLE__NO_DENSE_ROW_ON_FRONTIER (dense rows below theta or dominated at r=0) — winners by r at H=16: {'0': ['S5'], '1': ['S5'], '2': ['S5'], '4': ['S5'], '8': ['S5'], '16': ['S5'], '32': ['S5']}
- **B3**: NOT_OBSERVABLE__NO_DENSE_ROW_ON_FRONTIER (dense rows below theta or dominated at r=0) — winners by r at H=16: {'0': ['S5'], '1': ['S5'], '2': ['S5'], '4': ['S5'], '8': ['S5'], '16': ['S5'], '32': ['S5']}
- **U**: NOT_OBSERVABLE__NO_DENSE_ROW_ON_FRONTIER (dense rows below theta or dominated at r=0) — winners by r at H=16: {'0': ['S5'], '1': ['S5'], '2': ['S5'], '4': ['S5'], '8': ['S5'], '16': ['S5'], '32': ['S5']}
- **P3**: NOT_OBSERVABLE__NO_DENSE_ROW_ON_FRONTIER (dense rows below theta or dominated at r=0) — winners by r at H=16: {'0': ['S5'], '1': ['S5'], '2': ['S5'], '4': ['S5'], '8': ['S5'], '16': ['S5'], '32': ['S5']}

P2 exact at a 16-input, 8-bit scope; one target; frozen cost model; the S2 grammar contains the target by construction (declared), which is the exact-search advantage the Abbe/Shalev-Shwartz reading predicts.

