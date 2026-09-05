# Sparse knowledge-space continuation

This continuation fixes three numerical/input defects and reduces the cost of the
represented-system certificate introduced in `KSO_OPTIMIZATION_REPORT_V1.md`.
It is engineering validation on synthetic structural workloads. Historical M1/M2/M8
results and the original optimization measurements remain unchanged.

## Correctness changes

1. **Normalize before conversion.** Sparse matrix construction previously converted
   an edge's raw rational mass and denominator to floats separately. A common weight
   scale of `10^-400` erased a normalized unit transition; `10^400` raised
   `OverflowError` for the same rational transition. The new constructor computes
   each normalized rational head contribution first and then converts it. Both
   counterexamples failed before the fix and now agree with the exact rational matrix.
   Conversion of a truly tiny normalized contribution can still underflow. The
   certificate continues to describe the represented float system, not conversion
   error relative to the rational knowledge space.
2. **One revocation snapshot.** The exact solver consumed a one-shot revocation
   iterable during matrix construction and reused its exhausted iterator when gating
   seed mass. A revoked atom retained activation `1/3` instead of zero. The solver
   now shares one immutable snapshot across both operations; the exact-versus-sparse
   comparison helper shares one snapshot across both arms as well.
3. **One matrix snapshot.** Nested one-shot sparse rows could be consumed during
   input validation, leaving an empty operator for iteration and certification.
   A declared self-loop consequently returned activation `0.5` with a zero error
   bound, instead of activation near `1`. `SparseMatrix` now freezes nested sequences
   during construction, also preventing later edits through caller-owned lists.

The latter two boundaries were added after independent review and reproduced as two
additional failing tests before repair. The 20 new tests include independent rational
residual/solution oracles, duplicates, subnormals, non-dyadic direct inputs, common
scaling, generator inputs, aliasing, and collection of obsolete graph generations.

## Exact certificate with fewer allocations

Finite binary floats are dyadic rationals. Represent the weight matrix, seed,
activation and restart parameter by integer numerators with their own common
power-of-two denominators. Lift the three residual terms to a common exponent,
sum their signed integer numerators, and sum their absolute values. One final
`Fraction` reconstructs the exact residual. Integer outgoing row sums likewise give
the exact contraction coefficient. This is an algebraic change of representation;
the acceptance law remains

\[
 c=(1-\alpha)\max_i\sum_jP_{ij}<1,
 \qquad \mathrm{error}_{1}\leq\mathrm{residual}_{1}/(1-c).
\]

No float estimate discharges the bound. Non-dyadic direct rational inputs retain the
general `Fraction` implementation. Extreme exponent spreads can enlarge integer
storage; the optimization makes no constant-cost arithmetic claim.

All five returned fields—activation, iteration count, residual, contraction, and
error bound—exactly match commit `479e781` on 256 independently generated deterministic
represented-system cases. A separate mathematical reviewer checked the common-scale
algebra and outgoing-row orientation, then independently reconstructed 640 dense
`Fraction` systems (one to eight coordinates) and matched the exact residual and
contraction in every case. The exact rational KSO solver remains the authority for
the original rational model.

## Measurements and storage

The before and after runs use the same Python 3.12 host, frozen graph seed, three
repetitions and graph sizes of 4,096 and 16,384 atoms. The sparse workload is the
existing synthetic generator; the conjunctive workload has three tails and two
weighted heads per relation. Every graph/matrix/activation/certificate semantic
control is compared, not inferred from timing. Final measurements are stored in
`research/ocm-optimization/KSO_SPARSE_AFTER_V2.json`.

| Workload | Atoms | Before solver (s) | After solver (s) | Observed ratio |
|---|---:|---:|---:|---:|
| Sparse | 4,096 | 0.367024 | 0.274701 | 1.34× |
| Conjunctive | 4,096 | 0.481329 | 0.296058 | 1.63× |
| Sparse | 16,384 | 1.871899 | 1.235727 | 1.51× |
| Conjunctive | 16,384 | 2.163445 | 1.217643 | 1.78× |

These are observed same-host medians, not isolated-machine or general scaling
guarantees. Exact rational normalization adds work to matrix construction; its
separate timings and the complete raw repetitions are included in each row.
The represented matrix and all solver output controls remain exactly equal to the
baseline on all four ordinary-scale workloads; the extreme-scale regression inputs
intentionally change the previously incorrect matrix behavior.

For 4,096 sparse atoms, the final peak traced Python allocations within the solver
fall from 3,754,156 to 2,328,248 bytes (38.0%). The graph and matrix exist before tracing;
these observations exclude their memory and are not process RSS. Structural index
containers are reported separately in each raw benchmark row. No further structural
cache was justified: per-generation index isolation and garbage collection of an
obsolete, fully indexed graph both pass. There is no global graph cache.

## Reproduction and evidence

With `PYTHONPATH=src` and the repository Python environment:

```
python -m pytest tests/test_kso_sparse_continuation.py tests/test_kso_optimization.py tests/m2 tests/m8 -q
python tools/kso_sparse_continuation_benchmark.py --out /tmp/kso-sparse-replay.json
python tools/kso_sparse_verify_revision.py --baseline-ref 479e781 --out /tmp/kso-sparse-equality.json
```

The focused and existing integration tests pass: **195 tests**. This is separate
from the root repository's final full-suite gate. Git diff whitespace checks pass.

Raw measurements are retained in `research/ocm-optimization/`:

- `KSO_SPARSE_BEFORE_V2.json`: original source and same-host timings.
- `KSO_SPARSE_AFTER_V2.json`: final source and timings, including input snapshots.
- `KSO_SPARSE_DYADIC_ONLY_V2.json`: intermediate timing before the reviewed iterator fixes.
- `KSO_SPARSE_CONTENDED_V2.json`: an earlier after run overlapped traced-memory work;
  retained for transparency and excluded from the final timing comparison.
- `KSO_SPARSE_EQUIVALENCE_V2.json`: reproducible equality and traced-allocation results.
- `KSO_SPARSE_EQUIVALENCE_INITIAL_V2.json`: initial exploratory equality measurement.
- `KSO_SPARSE_EQUIVALENCE_DYADIC_ONLY_V2.json`: equality measurement before the
  independent iterator corrections, preserved with its own source hash.

The new source bindings affect M1 (`navigation.py`) and M2 (`navigation_sparse.py`).
Current validation must issue successor bindings and preserve historical receipts.
Neither faster admission nor faster numerical checking demonstrates stronger
cognition, autonomous learning, a new organization law, or superiority over parents.
