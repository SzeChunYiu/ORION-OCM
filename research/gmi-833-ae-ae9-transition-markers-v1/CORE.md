# gmi-833-ae-ae9-transition-markers-v1

Section AE9 of issue #833 asks for representation-change quantities that do
not depend on neural architecture names, for a line between smooth
quantitative improvement and genuine qualitative computational transition,
and for a re-audit of the word `emergence`. This package answers those three
rows on one registered **non-neural** roster, in exact rational arithmetic,
with two independent computational routes. It answers none of AE9's four
measurement rows, which need a real neural training run; those stay open with
a named instrument.

## The registered construction

The input space is `X = {0,1}^4`. The registered training pool is the 8-point
set `P = {0000, 0001, 0010, 0100, 1000, 1001, 1010, 1100}` and the registered
held-out set is `H = X \ P`, also 8 points. A sample is an `m`-subset of `P`
with `m` running over `0..8`, and **every accuracy is the exact rational
expectation over all `C(8,m)` such subsets** — never a sampled estimate.

A representation is the learner's committed code map `phi : X -> Z`. Every
marker is a function of the induced partition `ker(phi)` and of the registered
readout class (junta arity `2`, tree depth `2`) and of nothing else, which is
what makes it architecture-independent.

| marker | what it reads |
|---|---|
| `CELLS` | number of cells of `ker(phi)` — an integer effective rank with no eigenvalue |
| `REFINEMENT` | exact `(merged, split)` integers plus the exact rational pair-counting partition distance |
| `SEPARABILITY` | exact rational fraction of discordant label pairs split by a budgeted `ker(phi)`-measurable readout |
| `INVARIANCE` | integer order of the stabiliser of `ker(phi)` in the coordinate-permutation group of order `24` |
| `READOUT_ARITY` | least junta arity of an exact readout of the task from `ker(phi)`, or `NONE` |
| `USABLE` | exact rational best accuracy of the budgeted readout class on `phi` |

`CELLS`, `INVARIANCE` and `READOUT_ARITY` are the registered **structural
invariants**: they take values in finite discrete sets, so a transition read
off them cannot be manufactured by thresholding a graded quantity.

## What is closed, with the exact numbers

**Row 1 — architecture-independent definitions, proved in both directions.**
`GF2_ELIMINATION` and `GREEDY_DECISION_LIST` are materially different learners
that induce the *same* partition on the registered task and return exactly
equal values on every marker (`CELLS 2`, `INVARIANCE 4`, `READOUT_ARITY 2`,
`SEPARABILITY 1`, `USABLE 1`). An arbitrary injective re-encoding of the code
set moves the code map but leaves **every** marker exactly unchanged, at
partition distance exactly `0`. And a genuine change of partition always moves
a marker: all `15` pairs of distinct registered partitions have partition
distance strictly above `0`. Without that second direction the markers could
have been degenerate constants.

**Row 3 — smooth versus qualitative.** `TRAJ_SMOOTH` (the lookup learner)
rises strictly from `1/2` to `3/4` in eight per-step increments that are **all
exactly `1/32`**, while the structural triple stays constant at
`(CELLS, INVARIANCE, READOUT_ARITY) = (16, 24, 2)`. `TRAJ_JUMP` (the GF(2)
elimination learner) sits at exactly the base rate `1/2` for `m = 0,1,2,3,4`
and then jumps to `11/14` at `m* = 5`, with `READOUT_ARITY` moving `NONE -> 2`
and `INVARIANCE` moving `6 -> 4` **in that same step**. The jump is exactly
`2/7` on the held-out set. `m* = 5` is forced: an affine form over `GF(2)^4` is
pinned only by five affinely independent points, and `32` of the `56`
five-subsets of `P` achieve it.

**Row 4 — the `emergence` re-audit.** Three witnesses and a classifier
validated on the real roster in both directions.

- *Thresholded metric artifact.* `TRAJ_SMOOTH`'s underlying increments are all
  exactly `1/32`, spread exactly `0` — perfectly linear. Its registered
  `k = 8` exact-match transform has strictly increasing increments with
  last-over-first ratio exactly `6352865779/536158029`, a sharp knee, while
  every structural invariant is constant throughout. Its exact held-out
  accuracy is `1/2` at **every** `m`: the whole apparent rise is memorisation.
- *Phase-like internal reorganization.* `TRAJ_JUMP`, above.
- *Grokking-like delayed generalization.* `TRAJ_GROK` has exact training
  accuracy `1` from `m = 1` while exact held-out accuracy stays at `1/2` until
  `m** = 5`, then jumps to `11/14`.

The classifier attains recall `3/3` on the planted positives and raises **no**
genuine-transition alarm on the clean smooth trajectory — and, the point of
the row, no alarm on the knee-bearing transformed curve either, because the
structural invariants did not move. Over `200` randomized balanced-target
trials it fires `5` times: `1` on a drawn affine target, a diagnosed genuine
positive at magnitude `2/7`, and `4` false alarms all at magnitude `1/7`. The
primary comparison is threshold-free: the planted witness magnitude `2/7`
strictly exceeds the largest false-alarm magnitude `1/7`.

`TRAJ_GROK` also satisfies the phase-like structural signature. That is
reported rather than suppressed: it is the registered roster reproducing the
parent observation that delayed generalization coincides with internal
reorganization.

## What is not closed

The four AE9 measurement rows are **open**, each with its instrument named in
`MANIFEST_V1.json` and in the reconciliation file: a training run on a real
neural system with checkpointed representations; a preregistered marker freeze
recorded before an observed capability onset; a predictive comparison against
parameter count and training loss on real runs; and a matched
neural-versus-non-neural comparison. Nothing here is evidence about a neural
system, and no marker in this package is claimed to anticipate a capability
onset — both are registered forbidden promotions and both are asserted absent.

## Bounds

Five bounds ship, each with a range derived from the **definition** of the
bounded quantity, an attainment witness, and a `violated_by` witness in an
explicitly relaxed class. The sharpest is: the spread of `TRAJ_SMOOTH`'s
underlying increments is `<= 0` over a definitional range of `[0, 1]`,
attained exactly at `0`, and violated by the registered `k = 8` transform of
the very same accuracy sequence, whose spread is
`14541769375/549755813888`. No bound is vacuous and none is an
`UNFALSIFIED_BOUND`.

## Two routes

Route A computes every trajectory quantity in closed form from Moebius
inclusion-exclusion over the lattice of affine subspaces of `GF(2)^4`, and
every marker from canonical labelling, a refinement algebra over cell-size
sums, essential-variable analysis and bitmask/popcount readout algebra. Route B
averages exhaustively over every subset of `P`, builds partitions by explicit
equivalence-class closure, enumerates the `24` coordinate permutations one by
one with set-wise cell-image checks, searches readouts by brute force over
explicit truth tables, and counts pair quantities by enumerating all `120`
unordered pairs. Route B has no executable import of route A; the test parses
route B's AST and asserts it. The two agree on every value.

Claim ceiling:
`GMI_833_AE9_ARCHITECTURE_INDEPENDENT_TRANSITION_MARKERS_DEFINED_AND_EMERGENCE_CLASSES_SEPARATED_ON_NON_NEURAL_REGISTERED_SYSTEMS`.

## Reproduce

```bash
python3 -I -B research/gmi-833-ae-ae9-transition-markers-v1/test_ae9_transition_markers_v1.py -v
python3 -I -O -B research/gmi-833-ae-ae9-transition-markers-v1/test_ae9_transition_markers_v1.py -v
python3 -I -B research/gmi-833-ae-ae9-transition-markers-v1/ae9_transition_markers_v1.py
python3 -I -B research/gmi-833-ae-ae9-transition-markers-v1/independent_marker_oracle_v1.py
```

The executor writes `RESULT_V1.json` to stdout, byte-identical in both modes.
The commands above were run on CPython 3.8; the package workflow re-runs the
same comparison on CPython 3.12, which is where cross-version byte-identity is
verified.
