# GMI capability transfer v1

This capsule addresses two #602 F4 rows at exact finite scope: transfer across task families and calibrated abstention when capability is not identifiable.

Two raw task families have different absolute requirement/capacity scales. An exhaustive `{-2,0,2}^5` margin grid gives 243 members per family. The already-fitted development-only predictor is evaluated against the exact capability oracle.

Result: 1,944 capability cells; 416 determinate predictions, 416 correct, 0 determinate errors, 1,528 abstentions. Coverage is `52/243`; selective accuracy is `1`.

Claim ceiling: **G3** for this invariant-sufficient-statistic transfer setting. This is not probabilistic confidence calibration or real-regime transfer.
