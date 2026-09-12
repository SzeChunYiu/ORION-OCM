# Stage D'/E' — smooth-generalization ecology: report V22_SYM5_S4

Target coefficients [0.3125, 0.3125, 0.3125, 0.3125]. Receipt `STAGE_DE_SMOOTH_V22_SYM5_S4.json` (sha256 `094dd282b6c8cc57…`). 16 inputs, 8 seen; θ = 0.85; rows S4 (gradient net), S2 (exact linear search, grammar of 2401), S5 (exemplar memory), S3 (particles over the grammar).

## Capability after the protocol (largest ladder size, by column)

| row | B0 | B1 | B2 | B3 | U | P3 |
|---|---|---|---|---|---|---|
| S4@4 | 0.7812 | 0.7812 | 0.7812 | 0.7812 | 0.7812 | 0.7812 |
| S2a@4 | 0.9375 | 0.9375 | 0.9375 | 0.9375 | 0.9375 | 0.9375 |
| S5h@4 | 0.8958 | 0.8958 | 0.8958 | 0.8958 | 0.8958 | 0.8958 |
| S5@4 | 0.5833 | 0.5833 | 0.5833 | 0.5833 | 0.5833 | 0.5833 |
| S3@8 | 0.9375 | 0.9375 | 0.9375 | 0.9375 | 0.9375 | 0.9375 |

C2 (Dev tables identical across columns): True

## PH-REV on E_smooth (frozen prediction E' in CLAIM_LADDER_V2)

- **B0**: SUPPORTED__DENSE_WINS_LOW_r_LOCAL_WINS_HIGH_r — winners by r at H=16: {'0': ['S3'], '1': ['S5h'], '2': ['S5h'], '4': ['S5h'], '8': ['S5h'], '16': ['S5h'], '32': ['S5h']}
- **B1**: SUPPORTED__DENSE_WINS_LOW_r_LOCAL_WINS_HIGH_r — winners by r at H=16: {'0': ['S3'], '1': ['S5h'], '2': ['S5h'], '4': ['S5h'], '8': ['S5h'], '16': ['S5h'], '32': ['S5h']}
- **B2**: NOT_OBSERVABLE__DENSE_WINS_AT_EVERY_r (no local row reaches theta) — winners by r at H=16: {'0': ['S3'], '1': ['S3'], '2': ['S3'], '4': ['S3'], '8': ['S3'], '16': ['S3'], '32': ['S3']}
- **B3**: NOT_OBSERVABLE__DENSE_WINS_AT_EVERY_r (no local row reaches theta) — winners by r at H=16: {'0': ['S3'], '1': ['S3'], '2': ['S3'], '4': ['S3'], '8': ['S3'], '16': ['S3'], '32': ['S3']}
- **U**: NOT_OBSERVABLE__DENSE_WINS_AT_EVERY_r (no local row reaches theta) — winners by r at H=16: {'0': ['S3'], '1': ['S3'], '2': ['S3'], '4': ['S3'], '8': ['S3'], '16': ['S3'], '32': ['S3']}
- **P3**: NOT_OBSERVABLE__DENSE_WINS_AT_EVERY_r (no local row reaches theta) — winners by r at H=16: {'0': ['S3'], '1': ['S3'], '2': ['S3'], '4': ['S3'], '8': ['S3'], '16': ['S3'], '32': ['S3']}

P2 exact at a 16-input, 8-bit scope; one target; frozen cost model; the S2 grammar contains the target by construction (declared), which is the exact-search advantage the Abbe/Shalev-Shwartz reading predicts.

