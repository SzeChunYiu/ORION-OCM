# AE9 named results

Every result below is stated at the registered finite scope of `FREEZE_V1.md`:
the input space `X = {0,1}^4`, the registered 8-point training pool `P`, the
registered 8-point held-out set `H = X \ P`, sample counts `m = 0..8`, the
readout budget (junta arity `2`, tree depth `2`), the exact-match exponent
`k = 8`, and the three registered **non-neural** learners. Every accuracy is
the exact rational expectation over all `C(8,m)` subsets of `P`. All
quantities are exact rationals or integers; no float appears in any claim.
Route A is `ae9_transition_markers_v1.py`, route B is
`independent_marker_oracle_v1.py`, and the two agree on every value.

## Definition D-AE9 — the registered marker family

A **representation** is the learner's committed code map `phi : X -> Z`. Every
marker below is a function of the induced partition `ker(phi)`, of the
registered task `t`, and of the registered readout class `H_R` — and of
nothing else. In particular no marker reads an architecture class, a layer, a
parameter count or a code alphabet.

- `CELLS(phi)` is the number of cells of `ker(phi)`.
- `REFINEMENT(phi, psi)` is the integer pair `(merged, split)` obtained by
  refining `ker(phi)` to the common refinement and then coarsening to
  `ker(psi)`, together with the exact rational pair-counting distance
  `d(P, Q) = |{{x,y} : together in exactly one of P, Q}| / C(16,2)`.
- `SEPARABILITY(phi, t)` is the exact rational fraction of label-discordant
  pairs split by some `h` in `H_R` that is constant on the cells of `ker(phi)`.
- `INVARIANCE(phi)` is the order of the stabiliser of `ker(phi)` in the
  coordinate-permutation group of `X`, a group of order `4! = 24`.
- `READOUT_ARITY(phi, t)` is the least `k` for which some function of at most
  `k` coordinates of `X` is constant on the cells of `ker(phi)` and equals `t`
  exactly, and the symbol `NONE` if no such function exists.
- `USABLE(phi, t, R)` is the exact rational best accuracy over all `h` in
  `H_R` that are constant on the cells of `ker(phi)`.

`CELLS`, `INVARIANCE` and `READOUT_ARITY` are the registered structural
invariants; `SEPARABILITY` and `USABLE` are graded.

**Assumptions.** The input space, pool, held-out set, sample range, readout
budget and task are the registered ones; the coordinate decomposition of `X`
is part of the registered input space and not an architecture.

**Dependencies.** Elementary combinatorics of set partitions; the pair-counting
partition metric; the notion of an essential variable of a Boolean function.

**Falsifiers.** A marker whose value changes when only the code alphabet
changes; a marker that reads any quantity outside `(ker(phi), t, H_R)`; a pair
of distinct partitions on which `REFINEMENT` returns distance `0`.

**Strongest parents.** Meila (2007), doi:10.1016/j.jmva.2006.11.013, owns the
partition-comparison metric; Xu, Zhao, Song, Stewart and Ermon (2020),
arXiv:2002.10689, own the idea that usable content is relative to a decoder
class; Mossel, O'Donnell and Servedio (2004),
doi:10.1016/j.jcss.2004.04.002, own junta arity. Nothing in the definition is
claimed novel against them.

*Deviation recorded.* `FREEZE_V1.md` names `SEPARABILITY` as splitting by a
"GF(2)-affine functional of `phi`" and `READOUT_ARITY` as a junta of the code
coordinates. An arbitrary injective re-encoding of the code set destroys both
the `GF(2)` structure and the coordinate structure of `Z`, so neither literal
reading can satisfy the freeze's own governing sentence that every marker is a
function of `ker(phi)` and the registered readout class. The definitions above
take the governing sentence as primary and read both markers through the
registered readout class over the coordinates of `X`, which is
re-encoding-invariant. This is a reading of the freeze, not an edit of it.

## AE9-1 — the markers are functions of the induced partition alone

**Scope.** The registered roster of representations and the registered tasks
`x1 XOR x2` and the parity of all four coordinates. **Quantifiers.** Universal
over injective re-encodings of the code set; exhibited on one pair of
materially different learners.

Every marker of D-AE9 takes `ker(phi)` as its only representation argument, so
two learners whose committed code maps induce the same partition return
identical values on all six markers by construction. The construction is
witnessed: the `GF2_ELIMINATION` learner, having pinned the affine form, and
the `GREEDY_DECISION_LIST` learner, having split greedily to depth `2`, induce
the *same* partition of `X` on the registered task and return exactly
`CELLS = 2`, `INVARIANCE = 4`, `READOUT_ARITY = 2`, `SEPARABILITY = 1`,
`USABLE = 1`.

Invariance is claimed against a named group and no other. On the code side it
is the full group of injective re-encodings `Z -> Z'`: recoding the registered
code map through four different injections moves the code map as a function
and leaves every marker exactly unchanged, at partition distance exactly `0`.
On the input side nothing is claimed beyond the coordinate-permutation group,
which `INVARIANCE` itself measures rather than quotients away. The register's
`H_PARTITION_RELABEL` is an inverted hostile and the required silence is
asserted: the checker does not fire.

**Assumptions.** The registered readout budget and coordinate decomposition;
exact rational arithmetic throughout.

**Dependencies.** D-AE9; the greedy tie-break registered as lexicographic
ascending; the exhaustive computation in `RESULT_V1.json` under
`results.architecture_independence`.

**Falsifiers.** Two learners inducing the same partition but differing on any
marker; an injective re-encoding that moves any marker; any marker reading a
layer count, a parameter count or an architecture class name.

**Strongest parents.** Meila (2007) for partition-level invariance;
Kriegeskorte, Mur and Bandettini (2008),
doi:10.3389/neuro.06.004.2008, Raghu, Gilmer, Yosinski and Sohl-Dickstein
(2017), arXiv:1706.05806, and Kornblith, Norouzi, Lee and Hinton (2019),
arXiv:1905.00414, own representational-similarity measurement on real neural
systems, which this tranche deliberately does not perform.

**Forbidden extrapolation.** Nothing here licenses a claim about a neural
system. `NEURAL_RESULT_FROM_NON_NEURAL_ROSTER` is registered and asserted
absent.

## AE9-2 — distinct partitions are separated by REFINEMENT

**Scope.** All pairs of the registered partitions. **Quantifiers.** Universal
over the `15` pairs tested, and universal in the general statement below.

The pair-counting distance in `REFINEMENT` is zero exactly on equal
partitions, so a genuine change of partition moves at least one marker
unconditionally: if `P` differs from `Q` then some unordered pair lies together
in one and apart in the other, so `d(P, Q) > 0`. Over the registered family of
six distinct partitions all `15` pairs are separated with distance strictly
above `0`. The receipt additionally records, pair by pair, whether any of the
four unary markers also moves, so the coarseness of the unary markers is
visible rather than hidden.

Together with AE9-1 this closes the definitional row in both directions: the
markers are blind to everything except the partition and the registered readout
class, and they are not blind to the partition.

**Assumptions.** Partitions of the registered 16-point space; the
pair-counting distance of D-AE9.

**Dependencies.** D-AE9; AE9-1.

**Falsifiers.** A pair of distinct partitions of `X` at distance `0`; a
registered pair on which no marker moves.

**Strongest parents.** Meila (2007), doi:10.1016/j.jmva.2006.11.013. The
metric property is hers; nothing is claimed novel.

## AE9-3 — smooth quantitative improvement without structural change

**Scope.** `TRAJ_SMOOTH`, the registered exact lookup learner on the task
`x1 XOR x2`. **Quantifiers.** Universal over all `C(8,m)` subsets at every
`m = 0..8`.

The exact accuracy is `(16 + m)/32`, running `1/2, 17/32, 9/16, 19/32, 5/8,
21/32, 11/16, 23/32, 3/4`. The eight per-step increments are all exactly
`1/32`, so the increment spread is exactly `0` and the rise is strictly
positive at every step. The committed code map of a lookup learner is its key
map, which does not depend on the sample at all; hence the structural triple is
constant at `(CELLS, INVARIANCE, READOUT_ARITY) = (16, 24, 2)` not merely along
one training order but across **every** subset at every `m`. The exact held-out
accuracy is `1/2` at every `m`.

This is quantitative improvement with no representational restructuring
whatever.

**Assumptions.** The registered pool, held-out set and accuracy convention;
the lookup learner predicts the memorised label on seen points and the
registered default elsewhere.

**Dependencies.** D-AE9; the exact expectation computed in closed form by route
A and by exhaustive subset averaging in route B.

**Falsifiers.** Any per-step increment differing from `1/32`; any structural
invariant taking two values at one `m`; a held-out accuracy above `1/2`.

**Strongest parents.** Elementary linearity of expectation. No novelty is
claimed for the arithmetic.

## AE9-4 — a qualitative computational transition at m* = 5

**Scope.** `TRAJ_JUMP`, the registered exact `GF(2)` elimination learner on the
task `x1 XOR x2`. **Quantifiers.** Universal over all subsets for `m <= 4`;
the onset index is exact.

For `m <= 4` **every** subset of the pool leaves the version space larger than
a singleton, so the learner holds the registered default feature, and the exact
accuracy is `1/2` — exactly the base rate — on `X`, on the training sample and
on the held-out set alike. At `m* = 5` the accuracy jumps to `11/14`, a
held-out jump of exactly `2/7`. In the same step `READOUT_ARITY` moves from
`NONE` to `2` and `INVARIANCE` from `6` to `4`; `CELLS` does **not** move, and
that is reported rather than papered over. The onset is forced, not tuned: an
affine form over `GF(2)^4` is pinned only by five affinely independent points,
and exactly `32` of the `56` five-subsets of the registered pool are such, so
the accuracy onset, the held-out onset and the structural onset are all
exactly `5`.

Because the distinction is carried by discrete structural invariants and not
by thresholding a graded quantity, no choice of cut-off can manufacture it and
no choice of cut-off can remove it.

**Assumptions.** The learner commits only to a singleton version space and
otherwise holds the registered default feature; the registered pool has affine
rank `5`.

**Dependencies.** D-AE9; AE9-3 for the contrast; the affine-subspace
inclusion-exclusion counts of route A, cross-checked by route B.

**Falsifiers.** An accuracy above the base rate at any `m <= 4`; a structural
onset different from the accuracy onset; a `READOUT_ARITY` other than `NONE`
before the onset.

**Strongest parents.** Mossel, O'Donnell and Servedio (2004),
doi:10.1016/j.jcss.2004.04.002, own exact junta arity; linear-algebraic
identifiability of an affine form over `GF(2)` is textbook. No novelty is
claimed for either.

**Forbidden extrapolation.** `m* = 5` is a property of this registered
construction. `ASYMPTOTIC_EXTRAPOLATION_FROM_FINITE_ROSTER` is registered and
asserted absent.

## AE9-5 — the exact-match transform manufactures a knee from an exactly linear curve

**Scope.** `TRAJ_SMOOTH` under the registered exact-match exponent `k = 8`.
**Quantifiers.** Universal over the eight registered steps.

The underlying accuracy increments are all exactly `1/32`; the increments of
the `k`-item exact-match transform `acc^8` are

`2680790145/1099511627776`, `4044203135/...`, `5963602465/...`,
`8616436959/...`, `12222859361/...`, `17053014175/...`,
`23435111745/...`, `31764328895/1099511627776`,

strictly increasing, with last-over-first ratio exactly
`6352865779/536158029` — a sharp knee on a perfectly linear underlying curve,
with every structural invariant constant throughout. The magnitude of the knee
is capped by the registered constants `n = 4` and `m <= 8`, which fix the
underlying curve to the range `[1/2, 3/4]`; it is reported as it falls out
rather than enlarged by changing them.

The classifier of AE9-7 is fed the transformed, knee-bearing curve and still
returns no genuine-transition alarm, because the structural invariants did not
move. That is the whole content of the row: a sharp knee in a transformed
metric is not evidence of internal reorganization.

**Assumptions.** The registered exponent `k = 8`; the registered accuracy
convention.

**Dependencies.** AE9-3; D-AE9's structural invariants; the registered
exact-match transform.

**Falsifiers.** A non-constant underlying increment; a transformed increment
sequence that is not strictly increasing; any structural invariant moving on
`TRAJ_SMOOTH`; the classifier raising an alarm on the transformed curve.

**Strongest parents.** Schaeffer, Miranda and Koyejo (2023),
arXiv:2304.15004, own this mechanism entirely: a discontinuous or nonlinear
scoring rule applied to a smoothly improving underlying quantity produces an
apparent sharp emergence. Wei, Tay, Bommasani, Raffel, Zoph, Borgeaud and
co-authors (2022), arXiv:2206.07682, own the phenomenon being audited. The
residual here is only that the underlying curve is exactly linear, the
transform exact, and the structural invariants exhibited as constant on the
same object, so the artifact and the genuine transition of AE9-4 are separated
by a discrete quantity rather than by an argument.

## AE9-6 — delayed generalization with training accuracy 1 from m = 1

**Scope.** `TRAJ_GROK`, the registered `GF(2)` elimination learner with an
exact lookup table, on the parity of all four coordinates.
**Quantifiers.** Universal over all subsets for `m <= 4`.

Exact training accuracy is `1` for every `m >= 1`, because the lookup table
holds every seen point. Exact held-out accuracy is nevertheless `1/2` — the
base rate on `H` — for all `m <= 4`, and jumps to `11/14` at `m** = 5`, reaching
`1` at `m = 7`. Memorisation is therefore complete long before generalization
begins, with `m** = 5` strictly later than the training-accuracy onset `m = 1`.
At `m**` the structural triple moves from `(2, 6, NONE)` to `(2, 24, 4)`.

`TRAJ_GROK` consequently satisfies the phase-like structural signature as well
as the grokking signature. The receipt reports both rather than suppressing
one: on this registered roster delayed generalization coincides with internal
reorganization, which is the parent observation, not a defect of the
classifier.

**Assumptions.** The registered pool and held-out set are disjoint and cover
`X`; the learner memorises the sample and otherwise behaves as in AE9-4.

**Dependencies.** AE9-4 for the elimination mechanism; D-AE9; the registered
split, whose disjointness is asserted in `checks`.

**Falsifiers.** A training accuracy below `1` at any `m >= 1`; a held-out
accuracy above `1/2` at any `m <= 4`; a training point found inside `H`.

**Strongest parents.** Power, Burda, Edwards, Babuschkin and Misra (2022),
arXiv:2201.02177, own grokking; Nanda, Chan, Lieberum, Smith and Steinhardt
(2023), arXiv:2301.05217, own the observation that it coincides with the
formation of an internal structure. Both are absorbed; neither is claimed
here.

## AE9-7 — the emergence classifier, validated in both directions

**Scope.** The registered roster of three trajectories and a `200`-trial
randomized null drawn through the identical pipeline. **Quantifiers.**
Exhaustive over the roster and over the registered trials.

The classifier reads only exact quantities: the held-out onset and whether the
held-out accuracy is exactly at the base rate before it, the structural onset
and the number of distinct structural tuples, the training-accuracy
saturation index, the underlying increment spread, and whether the transformed
increments are strictly increasing. It returns
`GROKKING_DELAYED_GENERALIZATION`, `PHASE_LIKE_REORGANIZATION`,
`THRESHOLDED_METRIC_ARTIFACT` or `NO_EMERGENCE`, and reports every signature
that fired, not only the winner.

Recall is `3/3`: `TRAJ_SMOOTH -> THRESHOLDED_METRIC_ARTIFACT`,
`TRAJ_JUMP -> PHASE_LIKE_REORGANIZATION`,
`TRAJ_GROK -> GROKKING_DELAYED_GENERALIZATION`, with the exact `3 x 4`
confusion counts in the receipt. The no-alarm case is asserted twice: no
genuine-transition alarm on the clean smooth trajectory, and none on its
knee-bearing transformed curve.

The null draws a uniformly random balanced task by combinatorial unranking
from an integer sequence with a seed fixed once, and runs the unchanged
`TRAJ_JUMP` pipeline. Over `200` trials the alarm fires `5` times. One is a
drawn affine task — the same object as the planted witness, a genuine positive
at magnitude `2/7` — and `4` are false alarms, each at magnitude exactly `1/7`,
arising when a task happens to agree with an affine form across the whole pool
while differing on the held-out set. Each firing trial is listed individually
with its magnitude and its diagnosis. The primary comparison is threshold-free:
the planted witness magnitude `2/7` strictly exceeds the largest false-alarm
magnitude `1/7`. No threshold was chosen after the magnitudes were seen.

**Assumptions.** The registered `200` trials, the registered balanced-task
sampler, and the classifier conditions stated above, all fixed before the
trials were run.

**Dependencies.** AE9-3, AE9-4, AE9-5, AE9-6; the registered exact-match
exponent; the disjointness of the registered split.

**Falsifiers.** Recall below `3/3`; any alarm on the clean smooth trajectory or
on its transformed curve; a false-alarm magnitude at or above `2/7`; a firing
trial reported without a diagnosis.

**Strongest parents.** Schaeffer, Miranda and Koyejo (2023),
arXiv:2304.15004, and Wei and co-authors (2022), arXiv:2206.07682, for the
artifact-versus-phenomenon distinction; Power and co-authors (2022),
arXiv:2201.02177, and Nanda and co-authors (2023), arXiv:2301.05217, for the
grokking class. The classifier is an exact finite decision procedure over
their distinctions, not a new theory of emergence.

**Forbidden extrapolation.** The classifier classifies observed trajectories
after the fact. It anticipates nothing, and no marker in this package is
claimed to anticipate a capability onset;
`TRANSITION_MARKER_PREDICTS_CAPABILITY_ONSET` is registered and asserted
absent. `EMERGENCE_IS_ALWAYS_A_METRIC_ARTIFACT` and
`EMERGENCE_IS_ALWAYS_A_PHASE_TRANSITION` are likewise registered and asserted
absent: the roster exhibits all three readings, so neither universal is
supported.

## Scope, and what is deliberately not attempted

Every statement above is scoped to the registered non-neural systems. The four
AE9 measurement rows are untouched and stay open with named instruments: a
training run on a real neural system with checkpointed representations; a
preregistered marker freeze recorded before an observed capability onset; a
predictive comparison against parameter count and training loss on real runs;
and a matched neural-versus-non-neural comparison. No result here is evidence
for or against any of them.
