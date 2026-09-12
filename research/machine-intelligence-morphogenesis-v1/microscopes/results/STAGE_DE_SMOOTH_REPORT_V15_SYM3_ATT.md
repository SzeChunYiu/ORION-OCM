# Stage D'/E' — smooth-generalization ecology: report V15_SYM3_ATT

Target coefficients [0.1875, 0.1875, 0.1875, 0.1875]. Receipt `STAGE_DE_SMOOTH_V15_SYM3_ATT.json` (sha256 `1580492187604cea…`). 16 inputs, 8 seen; θ = 0.85; rows S4 (gradient net), S2 (exact linear search, grammar of 2401), S5 (exemplar memory), S3 (particles over the grammar).

## Capability after the protocol (largest ladder size, by column)

| row | B0 | B1 | B2 | B3 | U | P3 |
|---|---|---|---|---|---|---|
| S4@4 | 0.8854 | 0.8854 | 0.8854 | 0.8854 | 0.8854 | 0.8854 |
| S2a@4 | 0.9375 | 0.9375 | 0.9375 | 0.9375 | 0.9375 | 0.9375 |
| S5h@4 | 0.9375 | 0.9375 | 0.9375 | 0.9375 | 0.9375 | 0.9375 |
| S5a@4 | 0.8958 | 0.8958 | 0.8958 | 0.8958 | 0.8958 | 0.8958 |
| S5@4 | 0.75 | 0.75 | 0.75 | 0.75 | 0.75 | 0.75 |

C2 (Dev tables identical across columns): True

## PH-REV on E_smooth (frozen prediction E' in CLAIM_LADDER_V2)

- **B0**: NOT_OBSERVABLE__NO_DENSE_ROW_ON_FRONTIER (dense rows below theta or dominated at r=0) — winners by r at H=16: {'0': ['S2a'], '1': ['S5h'], '2': ['S5h'], '4': ['S5h'], '8': ['S5h'], '16': ['S5h'], '32': ['S5h']}
- **B1**: NOT_OBSERVABLE__NO_DENSE_ROW_ON_FRONTIER (dense rows below theta or dominated at r=0) — winners by r at H=16: {'0': ['S2a'], '1': ['S5h'], '2': ['S5h'], '4': ['S5h'], '8': ['S5h'], '16': ['S5h'], '32': ['S5h']}
- **B2**: NOT_OBSERVABLE__NO_DENSE_ROW_ON_FRONTIER (dense rows below theta or dominated at r=0) — winners by r at H=16: {'0': ['S2a'], '1': ['S5h'], '2': ['S5h'], '4': ['S5h'], '8': ['S5h'], '16': ['S5h'], '32': ['S5h']}
- **B3**: NOT_OBSERVABLE__NO_DENSE_ROW_ON_FRONTIER (dense rows below theta or dominated at r=0) — winners by r at H=16: {'0': ['S2a'], '1': ['S5h'], '2': ['S5h'], '4': ['S5h'], '8': ['S5h'], '16': ['S5h'], '32': ['S5h']}
- **U**: REFUTED_OR_NONMONOTONE — winners by r at H=16: {'0': ['S2a'], '1': ['S4'], '2': ['S4'], '4': ['S4'], '8': ['S4'], '16': ['S4'], '32': ['S4']}
- **P3**: REFUTED_OR_NONMONOTONE — winners by r at H=16: {'0': ['S2a'], '1': ['S4'], '2': ['S4'], '4': ['S4'], '8': ['S4'], '16': ['S4'], '32': ['S4']}

P2 exact at a 16-input, 8-bit scope; one target; frozen cost model; the S2 grammar contains the target by construction (declared), which is the exact-search advantage the Abbe/Shalev-Shwartz reading predicts.

