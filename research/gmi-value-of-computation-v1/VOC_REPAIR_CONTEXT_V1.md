# PR571 correction context

Source: merge743b9deda78be7ee48b77846ee2aa85e4a0e415f.
The three original files are preserved byte-for-byte in
[raw source bindings](raw/pr571-743b9ded/SOURCE_BINDINGS_V1.json).

The original deterministic-successor scope already excluded stochastic
Bayesian optimality. A geometric process is therefore a boundary example,
not a counterexample to that stated scope.

Actual repairs:

- VOC2 separates finite-value terminating policies from rank-exhausted dead ends.
- VOC3 computes the viable set, assigns +infinity to traps, and proves uniqueness
  on the finite-valued domain. A complete incumbent cost bounds optimal path length.
- The strict continuation rule is explicitly a stop-on-ties convention.
  A local minimizing selector additionally needs progress: a zero-cost loop
  can tie a serving path while never serving. The chooser requires VOC3
  positive charges; a ranked policy must use its decreasing-rank state.
- The executable ranked helper retains complete state and rank; the original
  helper returned10 where two zero-charge alternatives have exact optimum0.
- W4 now consistently names one unordered collision (two ordered pairs).
- Nonnegative value functions are explicit for VOC1's fixed-point interval.

[The current model](value_of_computation_model_v1.py) and active tests use the
corrected helper. The defective original exists only in the raw archive and is
executed as an explicitly failing historical countercontrol. A tracked source
search at743b9ded over research/.github found its definition, internal recursion,
two local tests and the unit CORE link; no grand consumer was found in that scope.

The [full repair receipt](REPAIR_RECEIPT_V1.json) retains source hashes and actual
normal/optimized command outputs for both historical and corrected tests.
The existing clean ranked fixture remains10. The positive graph census compares
729 registers against full deterministic stationary-policy trace enumeration;
the ranked census compares4374 state/rank values with all bounded paths.
No candidate, ecology, campaign, hardware or grand-capsule execution occurred.

The parent review's general implementation obligations remain open wherever
these finite model and explicit price premises have not been discharged.
