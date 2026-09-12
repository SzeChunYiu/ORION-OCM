# Stage D'/E' — smooth-generalization ecology: report V34_SYMn2_H

Target coefficients [-0.125, -0.125, -0.125, -0.125]. Receipt `STAGE_DE_SMOOTH_V34_SYMn2_H.json` (sha256 `7ef8a6ff7d292b41…`). 16 inputs, 8 seen; θ = 0.85; rows S4 (gradient net), S2 (exact linear search, grammar of 2401), S5 (exemplar memory), S3 (particles over the grammar).

## Capability after the protocol (largest ladder size, by column)

| row | B0 | B1 | B2 | B3 | U | P3 |
|---|---|---|---|---|---|---|
| S4@4 | 0.849 | 0.849 | 0.849 | 0.849 | 0.849 | 0.849 |
| S2a@4 | 0.9167 | 0.9167 | 0.9167 | 0.9167 | 0.9167 | 0.9167 |
| S5h@4 | 0.9583 | 0.9583 | 0.9583 | 0.9583 | 0.9583 | 0.9583 |
| S5@4 | 0.8333 | 0.8333 | 0.8333 | 0.8333 | 0.8333 | 0.8333 |
| S3@8 | 0.625 | 0.625 | 0.625 | 0.625 | 0.625 | 0.625 |

C2 (Dev tables identical across columns): True

## PH-REV on E_smooth (frozen prediction E' in CLAIM_LADDER_V2)

- **B0**: NOT_OBSERVABLE__NO_DENSE_ROW_ON_FRONTIER (dense rows below theta or dominated at r=0) — winners by r at H=16: {'0': ['S2a'], '1': ['S5h'], '2': ['S5h'], '4': ['S5h'], '8': ['S5h'], '16': ['S5h'], '32': ['S5h']}
- **B1**: NOT_OBSERVABLE__NO_DENSE_ROW_ON_FRONTIER (dense rows below theta or dominated at r=0) — winners by r at H=16: {'0': ['S2a'], '1': ['S5h'], '2': ['S5h'], '4': ['S5h'], '8': ['S5h'], '16': ['S5h'], '32': ['S5h']}
- **B2**: NOT_OBSERVABLE__NO_DENSE_ROW_ON_FRONTIER (dense rows below theta or dominated at r=0) — winners by r at H=16: {'0': ['S2a'], '1': ['S5h'], '2': ['S5h'], '4': ['S5h'], '8': ['S5h'], '16': ['S5h'], '32': ['S5h']}
- **B3**: NOT_OBSERVABLE__NO_DENSE_ROW_ON_FRONTIER (dense rows below theta or dominated at r=0) — winners by r at H=16: {'0': ['S2a'], '1': ['S5h'], '2': ['S5h'], '4': ['S5h'], '8': ['S5h'], '16': ['S5h'], '32': ['S5h']}
- **U**: NOT_OBSERVABLE__NO_DENSE_ROW_ON_FRONTIER (dense rows below theta or dominated at r=0) — winners by r at H=16: {'0': ['S2a'], '1': ['S5h'], '2': ['S5h'], '4': ['S5h'], '8': ['S5h'], '16': ['S5h'], '32': ['S5h']}
- **P3**: NOT_OBSERVABLE__NO_DENSE_ROW_ON_FRONTIER (dense rows below theta or dominated at r=0) — winners by r at H=16: {'0': ['S2a'], '1': ['S5h'], '2': ['S5h'], '4': ['S5h'], '8': ['S5h'], '16': ['S5h'], '32': ['S5h']}

P2 exact at a 16-input, 8-bit scope; one target; frozen cost model; the S2 grammar contains the target by construction (declared), which is the exact-search advantage the Abbe/Shalev-Shwartz reading predicts.

