# Additional fixed zero-input adjoint control

Registered before execution at source `7328d5b3b0a5111fd43c3e277679faf0edeee1bb`.
Execute `grad_zero_input_adjoint_control_v1.py` once on laptop CPython3.12.
No ecology, search, campaign, capability or timing run. Preserve every outcome.

Use exactly the previously retained six-node DENSE1/INPUT1/LINEAR/OUTPUT/TARGET/GRAD
graph, B0, seed0, lr1 and pinned initialization dense8.
Query integer input0; give feedback target16; query0 again.
The input multiplier is fixed-point0. The product output is identically0
for every representable weight; its exact sensitivity and quadratic-loss
parameter derivative are therefore0. A valid parameter adjoint leaves dense8.

Source predicts a counterexample: the parameter marker is on product pv,
whose error adjoint is−16, so the existing code writes dense8→9 despite
the zero sensitivity. This prediction is a falsifying condition, not a target
to tune. Existing x1/target0 raw control supplies the nonzero-input no-alarm.

A passive observer serializes the complete reachable Val tape before/after
the one original _backprop invocation and returns the original result.
It makes no Machine operation or RNG draw and does not modify any Val or cell.
Retain the native Machine tape, source/binary identity, before/after cells,
outputs, full authored ledger and write records. This observer's own overhead,
source loading and physical costs are outside the authored primitive ledger.
