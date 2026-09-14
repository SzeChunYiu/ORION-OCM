# F4 task-family transfer and abstention calibration v1

Two raw task families are registered with different absolute requirement scales. For each family and each margin vector in `{-2,0,2}^5`, raw capacities are constructed as `capacity_i = requirement_i + margin_i`. Thus the raw tasks differ in size while preserving the same architecture-name-free sufficient statistic.

## Transfer theorem at registered scope

If the capability predicate factors only through the registered signed margins, then two raw task instances with equal margin vectors have equal capability truth values. Therefore any predictor whose input is only those margins transfers across the two families wherever it emits a determinate value.

The exhaustive audit evaluates `2 × 3^5 × 4 = 1944` capability cells. It obtains 416 determinate predictions, all 416 correct, and 1528 `CANNOT_IDENTIFY` abstentions. Coverage is `416/1944 = 52/243`; abstention is `191/243`; selective accuracy is `1`.

## Calibration interpretation

This is deterministic selective-prediction calibration, not probabilistic confidence calibration. `CANNOT_IDENTIFY` means the development corpus supplies neither a monotone positive lower witness nor a negative upper witness. Abstentions are counted separately and never promoted to successes.

Both task families have identical audit profiles (972 cells each; 208 determinate correct and 764 abstentions), which is the registered invariance prediction under the sufficient-statistic assumption.

## Boundary

If a new task family changes capability semantics or adds a family-specific interaction not represented by the signed margins, the theorem does not apply. Claim ceiling: **G3** at this exact finite transfer scope, not general G6 or real-regime transfer.
