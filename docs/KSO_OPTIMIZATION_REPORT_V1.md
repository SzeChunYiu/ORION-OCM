# KnowledgeSpace implementation and numerical corrections

2026-09-05. Engineering measurements on synthetic graphs. No new cognition or organisation claim.
The historical M2 scaling and M8 organisation receipts are preserved unchanged.

## Measured bottleneck and changes

Profiling admission on the original 4,096-atom graph found 8,204 evaluations of `KnowledgeSpace.ids`
and 33,611,797 generated IDs. Tuple generation consumed 6.606 of 8.040 profiled seconds.
Admission constructed its uniform seed with repeated `x in ks.ids`, rebuilding and searching
the full tuple for each atom. This was quadratic work unrelated to the navigation law.

`ids`, atom/edge lookup and incident/outgoing adjacency now belong to each immutable space.
Public `atom_map()` and `edge_map()` still return independent mutable dictionaries. Persistent
edits create fresh caches; constructor sequence inputs are frozen into tuples. Dependency
classification, relevance, warrant liveness and activation remain fresh inputs to every query.
The registry-mutation test specifically changes which relation types propagate dependencies
after adjacency has been materialized.

Admission builds its seed with one atom lookup and one rational mass. For graphs above the
existing 200-atom threshold it now decides positivity using exact matrix support, avoiding a
numerical solve for a Boolean question. Small-graph admission retains the exact rational solver.

Median seconds, three repetitions on the same Python 3.12 host and frozen graph seed:

| Atoms | Before admission | After admission | Ratio | Before sparse activation | After sparse activation |
|---:|---:|---:|---:|---:|---:|
| 256 | 0.029724 | 0.006833 | 4.35× | 0.023390 | 0.032158 |
| 1,024 | 0.178888 | 0.024464 | 7.31× | 0.112820 | 0.151999 |
| 4,096 | 1.954783 | 0.122803 | 15.92× | 0.470290 | 0.622605 |

Sparse activation is slower because it now verifies a numerical error bound using exact
rational residual arithmetic. This is a measured cost of stronger checking, not a speedup.
Warm batches of 128 atom lookups cost about 0.00002 seconds; warm incident lookups about
0.00002–0.00003 seconds. These are cache-hit measurements, not whole-task speedups.
The raw samples include the first access, while the median of three measures predominantly
warm accesses. Construction and admission allocate fresh spaces in every repetition.

The 4,096-atom benchmark materializes 56,800 index entries/references in 990,712 bytes of shallow
Python containers. `index_resources()` reports this storage separately from logical content.
It excludes shared atom/edge/string payloads, allocator overhead and solver temporaries; it is
not a process-RSS measure. Existing admission resource vectors are unchanged: their historical
`navigation_work = n²` coordinate is retained as a declared charge, not relabelled as a measured
operation count. Index storage is an explicit additional observation, not silently free memory.

## Mathematical boundary and reproduced corrections

The support procedure uses the existing KS-T05 restart equation:

\[
a=\alpha\sum_{k\ge0}(1-\alpha)^k(P^\mathsf{T})^k s.
\]

For a nonnegative finite matrix, nonnegative seed and `0 < alpha < 1`, a coordinate is positive
exactly when a positive matrix path reaches it from positive seed support. In the existing
hypergraph matrix an edge contributes from any reached tail only when the edge and every tail
are LIVE. Only LIVE heads with positive shares are included; zero-weight edges contribute no
support. At `alpha = 1`, only gated seed support remains. This is distinct from the all-tails-
reached firing closure. No relevance function, truncation threshold or new evidence rule is
introduced by this admission helper.

An original 201-atom admission with a positive edge weight `1 / 10**400` was incorrectly rejected
as `UNREACHABLE_BY_NAVIGATION` because float conversion erased its positive mass. Exact support
admits that atom, rejects a zero-weight control and rejects propagation at `alpha = 1`.

The original sparse iteration stopped when successive iterates differed by at most `tol`.
For a self-loop, `alpha = 0.01` and `tol = 1e-6`, it returned after 917 iterations with actual
error `9.842572909757319e-5`, about 98 times the requested tolerance. The new
`sparse_fixed_point_certified()` computes the exact residual of the returned float vector
against the system represented by the float inputs, and reports

\[
c=(1-\alpha)\max_i\sum_jP_{ij}<1,\qquad
\|a-a^*\|_1\le\frac{\|\alpha s+(1-\alpha)P^\mathsf{T}a-a\|_1}{1-c}.
\]

The reported residual, contraction and error bound are exact `Fraction` values. This
certificate applies to the represented float matrix, seed and alpha. It does **not** certify
conversion error from the original rational KSO; the exact rational solver remains the
authority for that model. Invalid dimensions, negative/nonfinite inputs, unproved contraction,
floating-point stagnation above the requested tolerance, and iteration exhaustion cannot
produce a convergence certificate. The original tuple API remains available as a wrapper.

Admission also normalizes revocation iterables once. A generator was previously exhausted by
semantic connectivity before activation, allowing a conjunctive edge with a revoked tail to
be admitted. The regression checks identical rejection for a set and a one-shot iterator.

These arguments instantiate inherited obligations, not new mathematics: KS-T04 (frozen
denominators), KS-T05 (restart contraction), KS-T09 (dependency closure), KS-T21 (three-valued
liveness) in [the KSO obligation registry](theorems/KSO_OBLIGATION_REGISTRY_V1.json), and the
finite-calibration limitation of KS-T32 in
[the runtime obligation registry](theorems/OCM_RUNTIME_OBLIGATION_REGISTRY_V1.json).
The existing [M8 report](M8_ORGANISATION_REPORT.md) remains `PARENT_SUFFICIENT` at its measured
scale; these implementation improvements provide no evidence for a new organisation claim.

## Validation and reproducibility

The 38 focused tests check independent closure fixed points, exact support versus rational
activation, multi-tail/multi-head behavior, zero weights/shares, alternative and partial
warrants, dead edges, unrelated capabilities, reinstatement, registry/relevance mutations,
persistent edits, constructor aliasing, deepcopy/pickle, generator revocation, underflow,
numerical error certificates and exhausted precision/budget. Focused tests plus existing
M2 and M8 tests pass: 152 tests, excluding the concurrent runtime agent's new lifecycle file.
The earlier M1/M2/M8 run passed all 183 tests outside that separately owned in-progress file.
The final repository-wide gate is a separate integration obligation.

`tools/kso_optimization_benchmark.py --out PATH --profile` reproduces the engineering study.
Source hashes, raw repetitions, platform details, profiles and semantic controls are stored in:

- `research/ocm-optimization/KSO_BEFORE_V1.json`
- `research/ocm-optimization/KSO_INDEX_ONLY_AFTER_V1.json`
- `research/ocm-optimization/KSO_AFTER_V1.json`

All index-only semantic controls match the original, including float activation digests and
iterations. In the final version all graph, admission, closure, reopening, incidence and
resource controls still match; numerical activation digest and iteration count intentionally
change because the convergence criterion is stronger. The focused tests verify numerical
agreement with rational activation rather than demanding the old stopping error.

M1 source bindings change in `space.py`, `navigation.py`, `admission.py` and `revocation.py`.
M2 source bindings change in `navigation_sparse.py`. Revalidation must record a new revision
while retaining the original receipt history; regenerating historical receipts would erase
the original implementation evidence. The old scaling module's text still describes its
historical float admission path; this new report names the new exact support path explicitly.
