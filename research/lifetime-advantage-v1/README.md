# Measured engineering advantage from reusable exact search

**Result: bounded synthesis work decreased at unchanged exact coverage.** The
intervention is **HUMAN_SUPPLIED_REPAIR**: this engineering session supplied a
conventional semantic-search mechanism. OCM did not invent it. The result is
E2/L0 engineering on one finite polynomial ecology, not self-evolution,
cross-domain cognition, novel operator discovery or whole-runtime speedup.

The protocol, both new engines, benchmark and independent calibration tests
were committed before evaluation at
`3b9bc06cfcc98ef98ed4803508f91621c20a9f06`. The unmodified frozen sources produced
80 raw subprocess runs in [results/run-v1](results/run-v1). No worker failed.

## What changed and why it works

The incumbent `ocm.learning.methods.solve` reconstructs candidate programs and
their semantics for every task. The additive `SemanticSearchSession` retains
an exact polynomial index, a BFS frontier and shortest primitive witnesses.
Each new query can reuse previous search computation. Equal polynomials remain
equal under all four primitives, so merging equivalent prefixes preserves
bounded reach. This is ordinary semantic memoization/enumerative synthesis.

The index is extended lazily from the identity polynomial; it receives only
the current target specification, never the oracle's task universe. It returns
an answer only after the existing OCM exact verifier checks it. Checkpoint
restore reconstructs every retained transition and compares the complete
canonical state; all replay work is charged. This expensive restore is a
transparent first implementation, not an optimized persistence design.

## Registered evaluation

Every arm solved the same 12 training polynomials of shortest length 3, followed
by all **142 distinct polynomials whose shortest primitive program has length
4**. Eight shuffled orderings used seeds 4101..4108. Training and evaluation
mathematical identities were disjoint. All five arms achieved **142/142 exact
evaluation answers in every ordering** (1,136/1,136 per arm); each run also paid
for its 12 training answers. Eight cold single-query controls per arm all passed.

Medians over eight lifetime orderings follow. Arithmetic columns count exact
coefficient/numeric operations, including training and mandatory checking.
They are separate resource coordinates, not a weighted total.

| Arm | Additions | Multiplications | Instrumented lifetime wall, ms (range) | Whole subprocess wall, ms |
|---|---:|---:|---:|---:|
| Current primitive OCM search | 243,034 | 230,632 | 424.50 (408.23–460.55) | 506.84 |
| Current learned-fragment OCM search | 211,424 | 207,325 | 384.84 (374.79–406.84) | 463.38 |
| Semantic search, reset each query | 60,088 | 64,146 | 135.01 (124.25–150.43) | 218.01 |
| Persistent semantic search + restart | 3,329 | 3,627 | 12.58 (11.81–13.13) | 87.52 |
| Independent inverse-search parent | 17,652 | 14,455 | 20.24 (19.68–21.64) | 95.04 |

The inverse parent additionally used 6,757 exact divisions and 1,632 integer
square-root calls per lifetime. The persistent semantic engine used **15,935
serialized bytes**, while inverse search retained no cross-query search index.
This is a compute/storage trade-off, not uniform resource domination.
Process CPU, high-water RSS, probes, per-query work and all ranges are retained
in [summary.json](results/run-v1/summary.json) and the raw records. Fraction
operations are not constant-cost bit operations; RSS is process high-water
memory rather than live cognitive-field size.

Baseline wrappers count actual executed arithmetic calls; the new engines
maintain explicit inline counters. Timings therefore describe these
**instrumented implementations**, including their different accounting overhead.
They must not be presented as an uninstrumented production-speedup estimate.
Whole-subprocess timings include interpreter/import overhead and reduce the
apparent timing ratio substantially.

## Causal mechanism and negative result

Resetting the same semantic engine before each target increased lifetime
transitions from median **512** (including median **256 replay transitions**)
to **24,031**, while retaining within-query semantic deduplication. Additions
rose from 3,329 to 60,088 and multiplications from 3,627 to 64,146. Persistent
reuse answered **132–139 of 142 distinct evaluation targets** without any new
semantic transition; these were independently rechecked, not unchecked cache
answers. A previous query had already computed their semantics as search work.

In all eight cold single-query controls, persistent and reset semantic engines
had **identical core query operation counts**. There was no accumulated
persistence advantage to exploit. Inverse search was faster on these cold
controls: median instrumented 0.619 ms versus persistent semantic 1.580 ms.
This is a workload-dependent frontier. It does not establish that every task
should build a semantic table.

The current learned arm genuinely acquired eight recurring fragments from its
own checked training solutions; their mining and training-verification costs
were included. Its measured improvement over primitive search is preserved,
but it still repeatedly pays for many previously computed semantics.

## Scientific checkpoint

- THEORY QUESTION: Can retained exact search computation lower lifetime work
  across distinct targets while preserving bounded synthesis correctness?
- CURRENT HYPOTHESIS: Semantic memoization provides amortized computation reuse
  on this repeated fixed-grammar ecology.
- STRONGEST PARENT: Conventional semantic BFS is the mechanism itself;
  independently implemented target-directed inverse synthesis is measured too.
- FORMAL OBJECT: A BFS over rational-polynomial congruence classes, bounded by
  primitive word length, with shortest witnesses and exact answer verification.
- PREDICTION: Retaining the frontier lowers repeated search work; resetting it
  removes that benefit. Cold controls have no persistence effect.
- FALSIFIER: Missing reachable targets, invalid witnesses, unsound exhaustion,
  or no improvement after acquisition/checking/checkpoint/replay costs.
- VERIFICATION ROUTE: V2 exact calibration plus exposed E2 engineering runs;
  no universal empirical proof or external replication.
- EMPIRICAL RUNG: #143 CL0 measurement, bounded CL1 reuse/CL6 lifetime pressure;
  no rung exit is claimed.
- RESULT: All exact checks passed; compute use decreased, with a storage cost.
- NEGATIVE / COUNTEREXAMPLE: Cold inverse search was faster; the identical
  conventional semantic kernel explains the alleged OCM-specific mechanism.
- WHAT WAS REMOVED OR MERGED: Search reuse reduces to semantic memoization;
  no new cognitive primitive or learned representation is required here.
- WHAT SURVIVES: An additive engineering repair to repeated incumbent search.
- CLAIM CEILING: HUMAN_SUPPLIED_REPAIR; ADOPT/PARENT_SUFFICIENT; E2/L0.
- EXACT ARTIFACTS: Frozen sources, calibration tests, manifest, 80 raw runs and
  machine-readable summary in this directory.
- NEXT DECISIVE TEST: Measure adaptive selection between inverse search and
  table construction on newly frozen lifetime lengths, charging the selector;
  separately test a machine-generated repair lane before claiming self-evolution.

## Reproduction and boundary

From the repository root:

```sh
PYTHONPATH=src python research/lifetime-advantage-v1/test_semantic_session.py
PYTHONPATH=src:research/lifetime-advantage-v1 python research/lifetime-advantage-v1/benchmark.py --out /tmp/ocm-lifetime-new-run
```

Choose a new output path; the coordinator refuses to overwrite prior results.
The independent calibration uses raw-word interpolation through lengths 0..3
and checks both engines, shortest witnesses, exhaustion, zero budgets, reset,
tampering and fresh use after replay. No protected #143 study was executed.

This benchmark exercises the authoritative OCM answer checker. A full governed
runtime admission/revocation integration is **NOT_RUN_IN_THIS_BENCHMARK** and
cannot be inferred from these timings. Snapshot identities bind grammar,
checker, engine sources and bounds; they are mathematical state identities,
not permission to reuse revoked external authority.
