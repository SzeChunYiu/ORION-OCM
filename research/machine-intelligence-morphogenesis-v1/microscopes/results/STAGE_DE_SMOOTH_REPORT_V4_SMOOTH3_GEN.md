# Stage D'/E' — smooth-generalization ecology: report V4_SMOOTH3_GEN

Target coefficients [0.5, 0.25, -0.5, 0.375]. Receipt `STAGE_DE_SMOOTH_V4_SMOOTH3_GEN.json` (sha256 `837b6eb45b5b5239…`). 16 inputs, 8 seen; θ = 0.85; rows S4 (gradient net), S2 (exact linear search, grammar of 2401), S5 (exemplar memory), S3 (particles over the grammar).

## Capability after the protocol (largest ladder size, by column)

| row | B0 | B1 | B2 | B3 | U | P3 |
|---|---|---|---|---|---|---|
| S4@4 | 0.8646 | 0.8646 | 0.8646 | 0.8646 | 0.8646 | 0.8646 |
| S2@4 | 0.5417 | 0.5417 | 0.5417 | 0.5417 | 0.5417 | 0.5417 |
| S2a@4 | 0.9583 | 0.9583 | 0.9583 | 0.9583 | 0.9583 | 0.9583 |
| S5@4 | 0.7083 | 0.7083 | 0.7083 | 0.7083 | 0.7083 | 0.7083 |
| S3@8 | 0.4583 | 0.4583 | 0.4583 | 0.4583 | 0.4583 | 0.4583 |

C2 (Dev tables identical across columns): True

## PH-REV on E_smooth (frozen prediction E' in CLAIM_LADDER_V2)

- **B0**: REFUTED_OR_NONMONOTONE — winners by r at H=16: {'0': ['S2a'], '1': ['S4'], '2': ['S4'], '4': ['S4'], '8': ['S4'], '16': ['S4'], '32': ['S4']}
- **B1**: REFUTED_OR_NONMONOTONE — winners by r at H=16: {'0': ['S2a'], '1': ['S4'], '2': ['S4'], '4': ['S4'], '8': ['S4'], '16': ['S4'], '32': ['S4']}
- **B2**: REFUTED_OR_NONMONOTONE — winners by r at H=16: {'0': ['S2a'], '1': ['S4'], '2': ['S4'], '4': ['S4'], '8': ['S4'], '16': ['S4'], '32': ['S4']}
- **B3**: REFUTED_OR_NONMONOTONE — winners by r at H=16: {'0': ['S2a'], '1': ['S4'], '2': ['S4'], '4': ['S4'], '8': ['S4'], '16': ['S4'], '32': ['S4']}
- **U**: REFUTED_OR_NONMONOTONE — winners by r at H=16: {'0': ['S2a'], '1': ['S4'], '2': ['S4'], '4': ['S4'], '8': ['S4'], '16': ['S4'], '32': ['S4']}
- **P3**: REFUTED_OR_NONMONOTONE — winners by r at H=16: {'0': ['S2a'], '1': ['S4'], '2': ['S4'], '4': ['S4'], '8': ['S4'], '16': ['S4'], '32': ['S4']}

P2 exact at a 16-input, 8-bit scope; one target; frozen cost model; the S2 grammar contains the target by construction (declared), which is the exact-search advantage the Abbe/Shalev-Shwartz reading predicts.

