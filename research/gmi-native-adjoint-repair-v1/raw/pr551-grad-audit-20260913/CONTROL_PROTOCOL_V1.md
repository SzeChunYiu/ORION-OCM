# Fixed GRAD side-effect countercontrol

Registered before execution, source commit `7328d5b3b0a5111fd43c3e277679faf0edeee1bb`.
Run exactly `grad_side_effect_control_v1.py` once on laptop Python3.12, no optimization/tuning.
This is one deterministic VM input/feedback test, not an ecology/campaign run.

Use the pinned native B0 basis, seed0 and the six-node INPUT(width1), DENSE(width1),
LINEAR, OUTPUT, TARGET, GRAD(lr1) graph written literally in the script.
Wire DENSE and INPUT to LINEAR; LINEAR to OUTPUT; DENSE/LINEAR/TARGET to GRAD.
The GRAD node has no outgoing edge. The pinned initialization sets its only
dense cell to fixed-point8. Query integer input1, give feedback target0, query1 again.
Under the authored arithmetic, the nonzero error8 and lr1 yield one fixed-point
unit of change: dense8→7 and query8→7. Record every outcome, including disagreement.

Retain the complete genotype, ordered VM schedule, before/after cells, stores,
all native ledger coordinates, op counters and write records; bind source,
script, protocol, interpreter version and binary. No timers or performance ratios.
The native ledger is the authored primitive model and excludes audit/import and
physical runtime costs. This control establishes only that a GRAD result edge
is unnecessary for a feedback-driven parameter/response change at this input.
It does not imply nonzero gradients for every graph or capability/learning quality.
