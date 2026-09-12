# Cost per form and reachability of forms — generated from the executed receipts (B0 column; headline cell H = 16, r = 1)

Lifecycle cost = desc + 16·exec/query + update/event + verify/event + revision/4. 'Capability per kilo-cost' is the note's d(development)/d(cost) read at the headline cell: it is a ratio at one point of the (H, r) diagram, not a derivative law.

| receipt | row | form | capability | admissible | desc | exec/query | update/event | verify/event | revision | lifecycle cost | capability per kilo-cost |
|---|---|---|---|---|---|---|---|---|---|---|---|
| STAGE_DE_CREDIT_V11_CREDIT_E32 | R1 | RL as inference (consistency search) | 1.0 | yes | 362 | 3.4 | 51.5 | 61.0 | 754 | 717.9 | 1.3929 |
| STAGE_DE_CREDIT_V11_CREDIT_E32 | R2 | tabular Monte-Carlo Q | 0.5 |  | 1682 | 29.7 | 93.9 | 407.5 | 110 | 2685.6 | 0.1862 |
| STAGE_DE_CREDIT_V11_CREDIT_E32 | R3 | REINFORCE policy net | 0.25 |  | 565 | 96.3 | 289.2 | 1056.0 | 5249 | 4762.8 | 0.0525 |
| STAGE_DE_CREDIT_V11_CREDIT_E32 | R4 | kNN credited action | 0.75 |  | 1648 | 162.0 | 7.0 | 2180.0 | 295 | 6500.4 | 0.1154 |
| STAGE_DE_CREDIT_V11_CREDIT_E8 | R1 | RL as inference (consistency search) | 1.0 | yes | 122 | 2.6 | 140.1 | 52.0 | 490 | 477.8 | 2.0927 |
| STAGE_DE_CREDIT_V11_CREDIT_E8 | R2 | tabular Monte-Carlo Q | 0.5 |  | 482 | 25.2 | 80.5 | 372.9 | 84 | 1360.0 | 0.3676 |
| STAGE_DE_CREDIT_V11_CREDIT_E8 | R3 | REINFORCE policy net | 0.75 |  | 325 | 93.7 | 416.5 | 1056.0 | 1854 | 3759.7 | 0.1995 |
| STAGE_DE_CREDIT_V11_CREDIT_E8 | R4 | kNN credited action | 0.75 |  | 448 | 42.6 | 7.0 | 656.0 | 91 | 1815.0 | 0.4132 |
| V1 | S2 | exact program search | 1.0 | yes | 154 | 4.0 | 1842.7 | 80.0 | 4045 | 3152.1 | 0.3172 |
| V1 | S3 | particles (stochastic search) | 0.5625 |  | 252 | 4.0 | 1987.4 | 80.0 | 1740 | 2818.4 | 0.1996 |
| V1 | S4 | gradient net (dense numeric) | 0.8802 | yes | 404 | 64.0 | 290.8 | 1040.0 | 2362 | 3349.2 | 0.2628 |
| V1 | S5 | exemplar memory | 0.8125 |  | 195 | 7.7 | 9.7 | 144.8 | 11 | 475.8 | 1.7075 |
| V10_SMOOTH3_BAYES_E6 | S2a | approximate program search | 0.5208 |  | 154 | 4.0 | 36421.7 | 80.0 | 33625 | 45126.3 | 0.0115 |
| V10_SMOOTH3_BAYES_E6 | S4 | gradient net (dense numeric) | 0.7969 |  | 304 | 64.0 | 291.7 | 1040.0 | 908 | 2886.7 | 0.2761 |
| V10_SMOOTH3_BAYES_E6 | S5h | generalizing kNN memory | 0.8542 | yes | 106 | 35.8 | 6.2 | 697.8 | 7 | 1384.3 | 0.6171 |
| V10_SMOOTH3_BAYES_E6 | S5 | exemplar memory | 0.7083 |  | 95 | 5.4 | 6.2 | 110.3 | 7 | 299.5 | 2.3647 |
| V10_SMOOTH3_BAYES_E6 | S7 | Bayesian model averaging (posterior mean) | 0.8646 | yes | 236 | 112.0 | 53738.3 | 1808.0 | 50905 | 70300.6 | 0.0123 |
| V12_SMOOTH3_BAYES_E6_FIX | S2a | approximate program search | 0.5208 |  | 154 | 4.0 | 36421.7 | 80.0 | 33625 | 45126.3 | 0.0115 |
| V12_SMOOTH3_BAYES_E6_FIX | S4 | gradient net (dense numeric) | 0.7969 |  | 304 | 64.0 | 291.7 | 1040.0 | 908 | 2886.7 | 0.2761 |
| V12_SMOOTH3_BAYES_E6_FIX | S5h | generalizing kNN memory | 0.8542 | yes | 106 | 35.8 | 6.2 | 697.8 | 7 | 1384.3 | 0.6171 |
| V12_SMOOTH3_BAYES_E6_FIX | S5 | exemplar memory | 0.7083 |  | 95 | 5.4 | 6.2 | 110.3 | 7 | 299.5 | 2.3647 |
| V12_SMOOTH3_BAYES_E6_FIX | S7 | Bayesian model averaging (posterior mean) | 0.7917 |  | 236 | 112.0 | 53738.3 | 1808.0 | 50905 | 70300.6 | 0.0113 |
| V12_SMOOTH3_BAYES_NOISE_FIX | S2a | approximate program search | 0.9167 | yes | 334 | 4.0 | 105050.4 | 80.0 | 134479 | 139148.3 | 0.0066 |
| V12_SMOOTH3_BAYES_NOISE_FIX | S4 | gradient net (dense numeric) | 0.849 |  | 404 | 64.0 | 290.5 | 1040.0 | 2362 | 3349.0 | 0.2535 |
| V12_SMOOTH3_BAYES_NOISE_FIX | S5h | generalizing kNN memory | 0.8802 | yes | 206 | 74.0 | 9.7 | 1280.4 | 11 | 2683.5 | 0.328 |
| V12_SMOOTH3_BAYES_NOISE_FIX | S5 | exemplar memory | 0.7083 |  | 195 | 7.7 | 9.7 | 144.8 | 11 | 475.8 | 1.4885 |
| V12_SMOOTH3_BAYES_NOISE_FIX | S7 | Bayesian model averaging (posterior mean) | 0.8281 |  | 336 | 112.0 | 106048.0 | 1808.0 | 118768 | 139676.0 | 0.0059 |
| V12_SMOOTH3_BAYES_REF_FIX | S2a | approximate program search | 0.9583 | yes | 274 | 4.0 | 65133.2 | 80.0 | 100861 | 90766.6 | 0.0106 |
| V12_SMOOTH3_BAYES_REF_FIX | S4 | gradient net (dense numeric) | 0.8646 | yes | 404 | 64.0 | 290.4 | 1040.0 | 2362 | 3348.9 | 0.2582 |
| V12_SMOOTH3_BAYES_REF_FIX | S5h | generalizing kNN memory | 0.901 | yes | 206 | 74.0 | 9.7 | 1280.4 | 11 | 2683.5 | 0.3358 |
| V12_SMOOTH3_BAYES_REF_FIX | S5 | exemplar memory | 0.7083 |  | 195 | 7.7 | 9.7 | 144.8 | 11 | 475.8 | 1.4885 |
| V12_SMOOTH3_BAYES_REF_FIX | S7 | Bayesian model averaging (posterior mean) | 0.875 | yes | 336 | 112.0 | 106034.2 | 1808.0 | 118759 | 139660.0 | 0.0063 |
| V2_SMOOTH2 | S2 | exact program search | 0.4167 |  | 184 | 4.0 | 6257.8 | 80.0 | 10465 | 9202.2 | 0.0453 |
| V2_SMOOTH2 | S3 | particles (stochastic search) | 0.5 |  | 252 | 4.0 | 1987.2 | 80.0 | 1739 | 2817.9 | 0.1774 |
| V2_SMOOTH2 | S4 | gradient net (dense numeric) | 0.7578 |  | 404 | 64.0 | 289.9 | 1040.0 | 2348 | 3344.9 | 0.2266 |
| V2_SMOOTH2 | S5 | exemplar memory | 0.7917 |  | 195 | 7.7 | 9.7 | 144.8 | 11 | 475.8 | 1.6638 |
| V3_SMOOTH2_D48 | S2a | approximate program search | 0.9167 | yes | 654 | 4.0 | 153019.6 | 80.0 | 235335 | 212651.4 | 0.0043 |
| V3_SMOOTH2_D48 | S2 | exact program search | 0.4167 |  | 344 | 4.0 | 5683.6 | 80.0 | 10473 | 8789.9 | 0.0474 |
| V3_SMOOTH2_D48 | S3 | particles (stochastic search) | 0.3542 |  | 572 | 4.0 | 3373.4 | 80.0 | 4086 | 5110.9 | 0.0693 |
| V3_SMOOTH2_D48 | S4 | gradient net (dense numeric) | 0.8411 |  | 724 | 64.0 | 289.1 | 1040.0 | 6386 | 4673.6 | 0.18 |
| V3_SMOOTH2_D48 | S5 | exemplar memory | 0.7917 |  | 515 | 8.7 | 11.2 | 157.6 | 11 | 826.1 | 0.9583 |
| V4B_SMOOTH3_ROWS_V4_CALIB | S2a | approximate program search | 0.9583 | yes | 274 | 4.0 | 65133.2 | 80.0 | 100861 | 90766.6 | 0.0106 |
| V4B_SMOOTH3_ROWS_V4_CALIB | S3 | particles (stochastic search) | 0.4583 |  | 252 | 4.0 | 1987.8 | 80.0 | 1740 | 2818.8 | 0.1626 |
| V4B_SMOOTH3_ROWS_V4_CALIB | S4 | gradient net (dense numeric) | 0.8646 | yes | 404 | 64.0 | 290.4 | 1040.0 | 2362 | 3348.9 | 0.2582 |
| V4B_SMOOTH3_ROWS_V4_CALIB | S5k | kNN memory (defective, RV-021) | 0.7083 |  | 206 | 102.5 | 9.7 | 1768.8 | 11 | 3626.8 | 0.1953 |
| V4B_SMOOTH3_ROWS_V4_CALIB | S5 | exemplar memory | 0.7083 |  | 195 | 7.7 | 9.7 | 144.8 | 11 | 475.8 | 1.4885 |
| V4C_SMOOTH1_ROWS_V6_CALIB | S2a | approximate program search | 1.0 | yes | 154 | 4.0 | 14711.1 | 80.0 | 50434 | 27617.7 | 0.0362 |
| V4C_SMOOTH1_ROWS_V6_CALIB | S3 | particles (stochastic search) | 0.5417 |  | 252 | 4.0 | 1987.4 | 80.0 | 1740 | 2818.4 | 0.1922 |
| V4C_SMOOTH1_ROWS_V6_CALIB | S4 | gradient net (dense numeric) | 0.8698 | yes | 404 | 64.0 | 290.8 | 1040.0 | 2362 | 3349.2 | 0.2597 |
| V4C_SMOOTH1_ROWS_V6_CALIB | S5h | generalizing kNN memory | 0.9167 | yes | 206 | 74.0 | 9.7 | 1280.4 | 11 | 2683.5 | 0.3416 |
| V4C_SMOOTH1_ROWS_V6_CALIB | S5 | exemplar memory | 0.625 |  | 195 | 7.7 | 9.7 | 144.8 | 11 | 475.8 | 1.3135 |
| V4_SMOOTH3_GEN | S2a | approximate program search | 0.9583 | yes | 274 | 4.0 | 65133.2 | 80.0 | 100861 | 90766.6 | 0.0106 |
| V4_SMOOTH3_GEN | S2 | exact program search | 0.5417 |  | 184 | 4.0 | 6423.8 | 80.0 | 11101 | 9527.2 | 0.0569 |
| V4_SMOOTH3_GEN | S3 | particles (stochastic search) | 0.4583 |  | 252 | 4.0 | 1987.8 | 80.0 | 1740 | 2818.8 | 0.1626 |
| V4_SMOOTH3_GEN | S4 | gradient net (dense numeric) | 0.8646 | yes | 404 | 64.0 | 290.4 | 1040.0 | 2362 | 3348.9 | 0.2582 |
| V4_SMOOTH3_GEN | S5 | exemplar memory | 0.7083 |  | 195 | 7.7 | 9.7 | 144.8 | 11 | 475.8 | 1.4885 |
| V5B_PARITY_PH5_MIXED | S2a | approximate program search | 0.5 |  | 314 | 4.0 | 89293.6 | 80.0 | 100861 | 114967.1 | 0.0043 |
| V5B_PARITY_PH5_MIXED | S2 | exact program search | 0.25 |  | 184 | 4.0 | 6122.1 | 80.0 | 11217 | 9254.5 | 0.027 |
| V5B_PARITY_PH5_MIXED | S3 | particles (stochastic search) | 0.125 |  | 252 | 4.0 | 1986.9 | 80.0 | 1737 | 2817.1 | 0.0444 |
| V5B_PARITY_PH5_MIXED | S4 | gradient net (dense numeric) | 0.7031 |  | 404 | 64.0 | 290.0 | 1040.0 | 2354 | 3346.5 | 0.2101 |
| V5B_PARITY_PH5_MIXED | S5 | exemplar memory | 0.6667 |  | 195 | 7.7 | 9.7 | 144.8 | 11 | 475.8 | 1.4011 |
| V5_PARITY_PH5 | S2a | approximate program search | 0.3333 |  | 154 | 4.0 | 14711.1 | 80.0 | 50434 | 27617.7 | 0.0121 |
| V5_PARITY_PH5 | S2 | exact program search | 0.3333 |  | 154 | 4.0 | 1221.9 | 80.0 | 265 | 1586.4 | 0.2101 |
| V5_PARITY_PH5 | S3 | particles (stochastic search) | 0.0 |  | 252 | 4.0 | 1987.2 | 80.0 | 1738 | 2817.8 | 0.0 |
| V5_PARITY_PH5 | S4 | gradient net (dense numeric) | 0.2448 |  | 404 | 64.0 | 290.9 | 1040.0 | 2362 | 3349.4 | 0.0731 |
| V5_PARITY_PH5 | S5 | exemplar memory | 0.3333 |  | 195 | 7.7 | 9.7 | 144.8 | 11 | 475.8 | 0.7005 |
| V6_SYM3 | S2a | approximate program search | 0.9375 | yes | 294 | 4.0 | 75637.8 | 80.0 | 84052 | 97088.9 | 0.0097 |
| V6_SYM3 | S3 | particles (stochastic search) | 0.2812 |  | 252 | 4.0 | 1988.2 | 80.0 | 1739 | 2819.0 | 0.0998 |
| V6_SYM3 | S4 | gradient net (dense numeric) | 0.8854 | yes | 404 | 64.0 | 291.1 | 1040.0 | 2360 | 3349.1 | 0.2644 |
| V6_SYM3 | S5k | kNN memory (defective, RV-021) | 0.75 |  | 206 | 102.5 | 9.7 | 1768.8 | 11 | 3626.8 | 0.2068 |
| V6_SYM3 | S5 | exemplar memory | 0.75 |  | 195 | 7.7 | 9.7 | 144.8 | 11 | 475.8 | 1.5762 |
| V6_SYM5 | S2a | approximate program search | 0.9375 | yes | 314 | 4.0 | 89293.6 | 80.0 | 100861 | 114967.1 | 0.0082 |
| V6_SYM5 | S3 | particles (stochastic search) | 0.1354 |  | 252 | 4.0 | 1988.5 | 80.0 | 1739 | 2819.2 | 0.048 |
| V6_SYM5 | S4 | gradient net (dense numeric) | 0.7812 |  | 404 | 64.0 | 290.6 | 1040.0 | 2360 | 3348.6 | 0.2333 |
| V6_SYM5 | S5k | kNN memory (defective, RV-021) | 0.5833 |  | 206 | 102.5 | 9.7 | 1768.8 | 11 | 3626.8 | 0.1608 |
| V6_SYM5 | S5 | exemplar memory | 0.5833 |  | 195 | 7.7 | 9.7 | 144.8 | 11 | 475.8 | 1.2258 |
| V6_SYM7 | S2a | approximate program search | 0.9375 | yes | 294 | 4.0 | 75637.8 | 80.0 | 84052 | 97088.9 | 0.0097 |
| V6_SYM7 | S3 | particles (stochastic search) | 0.0 |  | 252 | 4.0 | 1988.9 | 80.0 | 1740 | 2819.9 | 0.0 |
| V6_SYM7 | S4 | gradient net (dense numeric) | 0.724 |  | 404 | 64.0 | 290.8 | 1040.0 | 2358 | 3348.2 | 0.2162 |
| V6_SYM7 | S5k | kNN memory (defective, RV-021) | 0.4167 |  | 206 | 102.5 | 9.7 | 1768.8 | 11 | 3626.8 | 0.1149 |
| V6_SYM7 | S5 | exemplar memory | 0.4167 |  | 195 | 7.7 | 9.7 | 144.8 | 11 | 475.8 | 0.8757 |
| V6_SYM8 | S2a | approximate program search | 1.0 | yes | 154 | 4.0 | 14711.1 | 80.0 | 50434 | 27617.7 | 0.0362 |
| V6_SYM8 | S3 | particles (stochastic search) | 0.25 |  | 252 | 4.0 | 1987.7 | 80.0 | 1739 | 2818.4 | 0.0887 |
| V6_SYM8 | S4 | gradient net (dense numeric) | 0.651 |  | 404 | 64.0 | 290.6 | 1040.0 | 2356 | 3347.6 | 0.1945 |
| V6_SYM8 | S5k | kNN memory (defective, RV-021) | 0.375 |  | 206 | 102.5 | 9.7 | 1768.8 | 11 | 3626.8 | 0.1034 |
| V6_SYM8 | S5 | exemplar memory | 0.3333 |  | 195 | 7.7 | 9.7 | 144.8 | 11 | 475.8 | 0.7005 |
| V7_PARITY_COSET_XOR | S2a | approximate program search | 0.3333 |  | 154 | 4.0 | 14711.1 | 80.0 | 50434 | 27617.7 | 0.0121 |
| V7_PARITY_COSET_XOR | S2 | exact program search | 0.3333 |  | 154 | 4.0 | 1221.9 | 80.0 | 265 | 1586.4 | 0.2101 |
| V7_PARITY_COSET_XOR | S3 | particles (stochastic search) | 0.0 |  | 252 | 4.0 | 1987.2 | 80.0 | 1738 | 2817.8 | 0.0 |
| V7_PARITY_COSET_XOR | S4 | gradient net (dense numeric) | 0.2448 |  | 404 | 64.0 | 290.9 | 1040.0 | 2362 | 3349.4 | 0.0731 |
| V7_PARITY_COSET_XOR | S5 | exemplar memory | 0.3333 |  | 195 | 7.7 | 9.7 | 144.8 | 11 | 475.8 | 0.7005 |
| V7_PARITY_COSET_XOR | S6 | algebraic (XOR-linear) identification | 0.3333 |  | 54 | 8.0 | 8.0 | 144.0 | 5 | 335.4 | 0.9937 |
| V7_PARITY_MIXED_XOR | S2a | approximate program search | 0.5 |  | 314 | 4.0 | 89293.6 | 80.0 | 100861 | 114967.1 | 0.0043 |
| V7_PARITY_MIXED_XOR | S2 | exact program search | 0.25 |  | 184 | 4.0 | 6122.1 | 80.0 | 11217 | 9254.5 | 0.027 |
| V7_PARITY_MIXED_XOR | S3 | particles (stochastic search) | 0.125 |  | 252 | 4.0 | 1986.9 | 80.0 | 1737 | 2817.1 | 0.0444 |
| V7_PARITY_MIXED_XOR | S4 | gradient net (dense numeric) | 0.7031 |  | 404 | 64.0 | 290.0 | 1040.0 | 2354 | 3346.5 | 0.2101 |
| V7_PARITY_MIXED_XOR | S5 | exemplar memory | 0.6667 |  | 195 | 7.7 | 9.7 | 144.8 | 11 | 475.8 | 1.4011 |
| V7_PARITY_MIXED_XOR | S6 | algebraic (XOR-linear) identification | 1.0 | yes | 134 | 8.0 | 32.2 | 144.0 | 49 | 450.7 | 2.2189 |
| V7_SMOOTH3_XOR | S2a | approximate program search | 0.9583 | yes | 274 | 4.0 | 65133.2 | 80.0 | 100861 | 90766.6 | 0.0106 |
| V7_SMOOTH3_XOR | S2 | exact program search | 0.5417 |  | 184 | 4.0 | 6423.8 | 80.0 | 11101 | 9527.2 | 0.0569 |
| V7_SMOOTH3_XOR | S3 | particles (stochastic search) | 0.4583 |  | 252 | 4.0 | 1987.8 | 80.0 | 1740 | 2818.8 | 0.1626 |
| V7_SMOOTH3_XOR | S4 | gradient net (dense numeric) | 0.8646 | yes | 404 | 64.0 | 290.4 | 1040.0 | 2362 | 3348.9 | 0.2582 |
| V7_SMOOTH3_XOR | S5 | exemplar memory | 0.7083 |  | 195 | 7.7 | 9.7 | 144.8 | 11 | 475.8 | 1.4885 |
| V7_SMOOTH3_XOR | S6 | algebraic (XOR-linear) identification | 0.7083 |  | 164 | 8.0 | 200.8 | 144.0 | 265 | 703.2 | 1.0073 |
| V8_SMOOTH3_H | S2a | approximate program search | 0.9583 | yes | 274 | 4.0 | 65133.2 | 80.0 | 100861 | 90766.6 | 0.0106 |
| V8_SMOOTH3_H | S3 | particles (stochastic search) | 0.4583 |  | 252 | 4.0 | 1987.8 | 80.0 | 1740 | 2818.8 | 0.1626 |
| V8_SMOOTH3_H | S4 | gradient net (dense numeric) | 0.8646 | yes | 404 | 64.0 | 290.4 | 1040.0 | 2362 | 3348.9 | 0.2582 |
| V8_SMOOTH3_H | S5h | generalizing kNN memory | 0.901 | yes | 206 | 74.0 | 9.7 | 1280.4 | 11 | 2683.5 | 0.3358 |
| V8_SMOOTH3_H | S5 | exemplar memory | 0.7083 |  | 195 | 7.7 | 9.7 | 144.8 | 11 | 475.8 | 1.4885 |
| V8_SYM3_H | S2a | approximate program search | 0.9375 | yes | 294 | 4.0 | 75637.8 | 80.0 | 84052 | 97088.9 | 0.0097 |
| V8_SYM3_H | S3 | particles (stochastic search) | 0.2812 |  | 252 | 4.0 | 1988.2 | 80.0 | 1739 | 2819.0 | 0.0998 |
| V8_SYM3_H | S4 | gradient net (dense numeric) | 0.8854 | yes | 404 | 64.0 | 291.1 | 1040.0 | 2360 | 3349.1 | 0.2644 |
| V8_SYM3_H | S5h | generalizing kNN memory | 0.9375 | yes | 206 | 74.0 | 9.7 | 1280.4 | 11 | 2683.5 | 0.3494 |
| V8_SYM3_H | S5 | exemplar memory | 0.75 |  | 195 | 7.7 | 9.7 | 144.8 | 11 | 475.8 | 1.5762 |
| V8_SYM5_H | S2a | approximate program search | 0.9375 | yes | 314 | 4.0 | 89293.6 | 80.0 | 100861 | 114967.1 | 0.0082 |
| V8_SYM5_H | S3 | particles (stochastic search) | 0.1354 |  | 252 | 4.0 | 1988.5 | 80.0 | 1739 | 2819.2 | 0.048 |
| V8_SYM5_H | S4 | gradient net (dense numeric) | 0.7812 |  | 404 | 64.0 | 290.6 | 1040.0 | 2360 | 3348.6 | 0.2333 |
| V8_SYM5_H | S5h | generalizing kNN memory | 0.8958 | yes | 206 | 74.0 | 9.7 | 1280.4 | 11 | 2683.5 | 0.3338 |
| V8_SYM5_H | S5 | exemplar memory | 0.5833 |  | 195 | 7.7 | 9.7 | 144.8 | 11 | 475.8 | 1.2258 |
| V8_SYM7_H | S2a | approximate program search | 0.9375 | yes | 294 | 4.0 | 75637.8 | 80.0 | 84052 | 97088.9 | 0.0097 |
| V8_SYM7_H | S3 | particles (stochastic search) | 0.0 |  | 252 | 4.0 | 1988.9 | 80.0 | 1740 | 2819.9 | 0.0 |
| V8_SYM7_H | S4 | gradient net (dense numeric) | 0.724 |  | 404 | 64.0 | 290.8 | 1040.0 | 2358 | 3348.2 | 0.2162 |
| V8_SYM7_H | S5h | generalizing kNN memory | 0.8542 | yes | 206 | 74.0 | 9.7 | 1280.4 | 11 | 2683.5 | 0.3183 |
| V8_SYM7_H | S5 | exemplar memory | 0.4167 |  | 195 | 7.7 | 9.7 | 144.8 | 11 | 475.8 | 0.8757 |
| V8_SYM8_H | S2a | approximate program search | 1.0 | yes | 154 | 4.0 | 14711.1 | 80.0 | 50434 | 27617.7 | 0.0362 |
| V8_SYM8_H | S3 | particles (stochastic search) | 0.25 |  | 252 | 4.0 | 1987.7 | 80.0 | 1739 | 2818.4 | 0.0887 |
| V8_SYM8_H | S4 | gradient net (dense numeric) | 0.651 |  | 404 | 64.0 | 290.6 | 1040.0 | 2356 | 3347.6 | 0.1945 |
| V8_SYM8_H | S5h | generalizing kNN memory | 0.8333 |  | 206 | 74.0 | 9.7 | 1280.4 | 11 | 2683.5 | 0.3105 |
| V8_SYM8_H | S5 | exemplar memory | 0.3333 |  | 195 | 7.7 | 9.7 | 144.8 | 11 | 475.8 | 0.7005 |
| V9_SMOOTH3_H_SHRFIX | S2a | approximate program search | 0.9583 | yes | 274 | 4.0 | 65133.2 | 80.0 | 100861 | 90766.6 | 0.0106 |
| V9_SMOOTH3_H_SHRFIX | S3 | particles (stochastic search) | 0.4583 |  | 252 | 4.0 | 1987.8 | 80.0 | 1740 | 2818.8 | 0.1626 |
| V9_SMOOTH3_H_SHRFIX | S4 | gradient net (dense numeric) | 0.8646 | yes | 404 | 64.0 | 290.4 | 1040.0 | 2362 | 3348.9 | 0.2582 |
| V9_SMOOTH3_H_SHRFIX | S5h | generalizing kNN memory | 0.901 | yes | 206 | 74.0 | 9.7 | 1280.4 | 11 | 2683.5 | 0.3358 |
| V9_SMOOTH3_H_SHRFIX | S5 | exemplar memory | 0.7083 |  | 195 | 7.7 | 9.7 | 144.8 | 11 | 475.8 | 1.4885 |

## Reachability (label-free search)

| receipt | record | ecology | search family | evaluations | existence certificate | winners | winner classes | best score | best elite class |
|---|---|---|---|---|---|---|---|---|---|
| RECLASS_RUN3 | None | None | random N + hill-climb from top-k by single-node mutation; label-free; scored by (score, -c | None | None | 0 |  | None | None |
| RUN2 | None | None | random N + hill-climb from top-k by single-node mutation; label-free; scored by (score, -c | None | None | 0 |  | None | None |
| RUN3B_BIND16_SEED4 | None | None | random N + hill-climb from top-k by single-node mutation; label-free; scored by (score, -c | None | None | 0 |  | None | None |
| RUN3_BIND16 | None | None | random N + hill-climb from top-k by single-node mutation; label-free; scored by (score, -c | None | None | 0 |  | None | None |
| RUN4_SMOOTH8 | None | None | random N + hill-climb from top-k by single-node mutation; label-free; scored by (score, -c | None | None | 0 |  | None | None |
| RUN6_SMOOTH8_GDEPTH3 | None | None | random N + hill-climb from top-k by single-node mutation; label-free; scored by (score, -c | None | None | 0 |  | None | None |
| RUN7_SMOOTH8_REGEVO_S5 | RV-377-018 | smooth | regularized (aging) evolution, Real et al. 2019 Alg. 1: P=100, S=25, Koza subtree mutation | 100000 | planted 4-coefficient learner 0.9258 (RV | 0 |  | 0.7884 | INERT (fixed program; M0 |
| RUN7_SMOOTH8_REGEVO_S6 | RV-377-018 | smooth | regularized (aging) evolution, Real et al. 2019 Alg. 1: P=100, S=25, Koza subtree mutation | 100000 | planted 4-coefficient learner 0.9258 (RV | 0 |  | 0.7949 | LOCAL_MEMORY (store or c |
| RUN7_SMOOTH8_REGEVO_S7 | RV-377-018 | smooth | regularized (aging) evolution, Real et al. 2019 Alg. 1: P=100, S=25, Koza subtree mutation | 100000 | planted 4-coefficient learner 0.9258 (RV | 0 |  | 0.7884 | INERT (fixed program; M0 |
| RUN8_SMOOTH8_DIV_REGEVO_S5 | RV-377-023 | smooth_div | regularized (aging) evolution, Real et al. 2019 Alg. 1: P=100, S=25, Koza subtree mutation | 100000 | planted 4-coefficient learning-rate-1/4  | 0 |  | 0.7346 | LOCAL_MEMORY (store or c |
| RUN8_SMOOTH8_DIV_REGEVO_S6 | RV-377-023 | smooth_div | regularized (aging) evolution, Real et al. 2019 Alg. 1: P=100, S=25, Koza subtree mutation | 100000 | planted 4-coefficient learning-rate-1/4  | 0 |  | 0.7297 | LOCAL_MEMORY (store or c |
| RUN8_SMOOTH8_DIV_REGEVO_S7 | RV-377-023 | smooth_div | regularized (aging) evolution, Real et al. 2019 Alg. 1: P=100, S=25, Koza subtree mutation | 100000 | planted 4-coefficient learning-rate-1/4  | 0 |  | 0.7312 | LOCAL_MEMORY (store or c |
| V1 | None | None | random N + hill-climb from top-k by single-node mutation; label-free; scored by (score, -c | None | None | 0 |  | None | None |
