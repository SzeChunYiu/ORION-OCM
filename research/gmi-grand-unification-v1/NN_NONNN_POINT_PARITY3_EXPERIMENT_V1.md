# Grand GMI NN / Non-NN Point Experiment — Parity-3 on CPython 3.12 V1

Status: **PROSPECTIVE PREREGISTRATION; PROTECTED RESOURCE OUTCOME NOT YET READ**  
Date: 2026-09-12

## 1. Purpose

The formal Grand-GMI derivation grammar can compile one protected intelligence obligation into neural and non-neural realizations and can select a family once real comparative resource evidence is supplied. The evidence-readiness audit shows that the repository still lacks a complete task-bound comparative packet.

This experiment is the smallest prospective packet designed to exercise that bridge end-to-end on a real execution substrate.

It is deliberately a **point experiment**, not a claim about general intelligence architecture.

## 2. Protected obligation

For every binary triple

\[
x=(x_0,x_1,x_2)\in\{0,1\}^3,
\]

emit

\[
y=x_0\oplus x_1\oplus x_2
\]

exactly.

The protected deployment domain is the entire finite domain of eight triples. Therefore deployment adequacy is exhaustively decidable and there is no train/test extrapolation step in this packet.

A constant-zero null is correct on exactly four of eight cases. Every admitted candidate must be correct on all eight.

## 3. Frozen candidates

### N_THRESHOLD_DNF4_V1 — neural

A feed-forward affine-threshold network with four hidden units, one for each positive parity minterm:

- `001`: `-x0 - x1 + x2 >= 1`;
- `010`: `-x0 + x1 - x2 >= 1`;
- `100`: ` x0 - x1 - x2 >= 1`;
- `111`: ` x0 + x1 + x2 >= 3`.

The output threshold fires when at least one hidden detector fires.

This is an exact threshold-network realization of parity-3. It is neural by the preregistered operational family predicate, not because of a library or class name.

### X_XOR2_V1 — non-neural

A direct deterministic Boolean program evaluates

`(x0 XOR x1) XOR x2`.

No affine-threshold hidden-unit network is used inside the candidate.

## 4. Developmental scope

Both candidates are frozen, directly constructed source artifacts. No training, architecture search, synthesis search or hyperparameter selection is performed in this experiment.

Therefore this packet asks only:

> Among these two already-reachable exact realizations, which one is selected by the registered deployment-resource criterion on the declared CPython substrate?

Development cost is explicitly excluded from selection in V1. No conclusion about SGD, program synthesis, learning efficiency or architecture discoverability is permitted from this packet.

## 5. Physical/execution substrate

The protected execution substrate is:

- GitHub Actions hosted `ubuntu-latest` runner;
- CPython `3.12.x` installed by `actions/setup-python@v5`;
- one process;
- no network or external tool calls inside the measurement;
- garbage collection disabled during timed blocks;
- identical input order and number of calls for both candidates.

This is a software-process substrate. Its resource coordinates are interpreter/execution resources, not direct joule measurements.

## 6. Registered resource coordinates

Three coordinates are minimized.

### R1 — exact Python opcode events

Using CPython opcode tracing, count only opcode events whose frame code object is the frozen candidate function. Evaluate the complete eight-input protected domain once.

This coordinate is exact for the executed CPython/code artifact. It is an interpreter-work measure, not a universal machine-instruction or energy count.

### R2 — wall-clock block time

For one timed block, execute exactly `20,000` complete domain sweeps = `160,000` candidate calls and record `perf_counter_ns` elapsed time.

There are `31` timed blocks per candidate. The resource uncertainty set for this registered run is the finite observed envelope

\[
[\min_b t_b,\max_b t_b].
\]

No probabilistic population-coverage claim is attached to this envelope.

### R3 — process CPU-time block time

The same block records `process_time_ns`. The finite observed envelope is used with the same no-extrapolation interpretation.

## 7. Order and warm-up controls

Before protected timing, each candidate receives `5,000` warm-up domain sweeps.

For timed block `b`:

- even `b`: measure neural then non-neural;
- odd `b`: measure non-neural then neural.

This balances first/second order within the frozen finite schedule. No blocks are discarded after measurement.

## 8. Selection rule

Each candidate receives a three-coordinate box:

- exact opcode interval `[o,o]`;
- observed wall interval `[wall_min,wall_max]`;
- observed process interval `[proc_min,proc_max]`.

Candidate `A` robustly dominates `B` only if

\[
U_{A,j}\le L_{B,j}\quad\text{for every coordinate }j
\]

and at least one inequality is strict.

Canonical adjudication:

- X robustly dominates N -> `DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE`;
- N robustly dominates X -> `DERIVED_NEURAL_AT_REGISTERED_SCOPE`;
- otherwise -> `UNDECIDED_FROM_CURRENT_EVIDENCE`.

No post-result scalarization or tie-breaker is allowed.

## 9. Prospective prediction

Before protected resource execution, V1 predicts:

> `X_XOR2_V1` will robustly dominate `N_THRESHOLD_DNF4_V1` across all three registered coordinates on the declared CPython 3.12 hosted-runner scope.

This prediction is falsified for V1 if robust non-neural domination is absent.

If intervals overlap, the correct result is `UNDECIDED`; the benchmark settings may not be edited and rerun under the same version merely to force separation.

If neural robust domination occurs, the opposite family terminal is recorded; the preregistered prediction is marked false.

## 10. Provenance

The measurement artifact must record:

- GitHub SHA and run identifiers when available;
- Python implementation/version;
- platform string and CPU count;
- benchmark harness SHA-256;
- candidate IDs;
- exhaustive capability outputs;
- every timed block, not only summary statistics;
- exact opcode counts;
- resource boxes;
- canonical verdict and prospective-prediction status.

## 11. Hostile expansion requirement

A successful V1 point verdict is not broad enough to finish the empirical programme. A later candidate-expansion round must attack it with at least:

1. an independently optimized exact neural threshold implementation;
2. an exact non-neural lookup-table implementation.

The original V1 result remains valid only for its original two-candidate universe if the expanded winner changes.

## 12. Claim ceiling

Even a clean non-neural win would establish only:

> Under the frozen parity-3 obligation, candidate universe, CPython 3.12 hosted-runner substrate and registered deployment-resource coordinates, the non-neural XOR realization robustly dominates the registered threshold-network realization in that executed run.

It would **not** establish that non-neural intelligence is generally superior, that parity is representative of intelligence, or that neural networks are unnecessary for other Grand-GMI obligations.

The scientific value of V1 is that it turns the Grand-GMI family-selection pipeline into a prospective, executable, falsifiable evidence packet with an honest abstention path.
