# Surprise background channel repair

Owner [#72](https://github.com/SzeChunYiu/ORION-OCM/issues/72#issuecomment-5558295754).
Classification: INFRASTRUCTURE. Base 29085f80c727f1cb47d3a76df39837b0b6a585d1.
The repair changes only the channel pairing in the existing solve loop.

## Cause

For each mode m, the fixed point is a_m = alpha*s_m + (1-alpha)*P_m^T*a_m.
PROPAGATED surprise therefore compares b_q,m = a_q,m - alpha*s_q,m with
b_pi,m = pi_m - alpha*s_uniform,m for the same mode.
The old caller combined exploratory activation/prior with warranted pi.
At a withdrawn atom, warranted pi is zero while exploratory uniform restart is alpha/n,
producing the observed negative background -1/42 on the original 14-atom fixture.
The subsequent logarithm failed. This was an incompatible channel pair, not evidence
that the registered propagated-mass formula needs clipping.

navigate_stage now obtains both mode-specific uniform fixed points.
The existing background key remains warranted; background_x is exploratory.
Both UNIFORM and PROPAGATED extraction use the matching channel background.
surprise.py, seed gating, navigation matrices, denominators, formulas and default model
are unchanged. There is no clipping or exception swallowing.

## Actual controls

The independent three-atom witness has q->d plus isolated u and alpha=1/3.
After d becomes DEAD or UNKNOWN, warranted background at d is 0; exploratory background
is 5/27, with propagated background 2/27 and query propagated mass 2/9.
The test asserts all exact rational activation/background values and the expected
surprise in both models, then checks d remains exploratory-only.

The original solve fixture is tested under both models with clean state and withdrawal
of fact, rule or unrelated partial warrant. Withdrawn prerequisites never commit;
the unaffected PROPAGATED answer remains 42. Missing exploratory background preserves
CANNOT_CHECK and prevents commitment.

- New controls before repair: 8 failures/5 passes, including three actual math-domain errors.
- New controls after repair: 13 passed.
- Full existing M2 suite plus new controls: 158 passed.
- Zero errors/skips in green runs. Exact JUnit/log/source bindings are in verification.json.
- Original consumer failure bytes and original solve.py are retained unchanged.

## Costs and limits

The navigation work proxy now charges 4*n*n for four fixed-point computations,
plus existing target-navigation work. It is not measured physical runtime.
Previous three-computation timing receipts do not qualify this new source.
No main merge, full current engineering recorder, model inference or performance study
was run for this repair. Current-source qualification follows integration.
No scientific or capability promotion follows from this correctness fix.
