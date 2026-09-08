# Exposed development checks before evaluation freeze

`PYTHONPATH=src python research/lifetime-advantage-v1/test_semantic_session.py`
passed all eight independent test families before the evaluation freeze.
Complete worlds through primitive length 0, 1, 2, 3 had 1, 5, 19, 64 distinct
polynomials. A raw-word exact interpolation oracle agreed with both semantic
BFS and independently implemented inverse synthesis. Tests cover shortest
representatives, zero-budget refusal, full bounded exhaustion, interruption,
checkpoint replay, tampering, reset and accounting monotonicity.

The benchmark plumbing was exercised on two authored length-2 training tasks
(inc-square and double-square) and two length-2 targets (dec-square and
square-inc). All five arms returned two verified answers. The persistent arm
wrote/fsynced/read a checkpoint and charged 16 replay transitions.
These observations are development exposure; they are not evaluation evidence.

No length-4 target outcomes or aggregate counts were inspected before freezing.
The protocol, engines, benchmark and these tests are committed before the
coordinator constructs the registered length-4 evaluation manifest.

Arithmetic accounting is an operation model: baseline wrappers count every
actual call to numeric execution, coefficient normalization and Horner
evaluation; new engines count incremental operations and analytically count
the identical final normal-form verification. Fraction bit complexity is not
modeled. Learning costs include actual search/checker execution, actual timed
mining, and separately recorded fragment enumeration. No single aggregated
cost score is reported.
