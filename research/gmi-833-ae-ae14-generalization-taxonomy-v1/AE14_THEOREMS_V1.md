# AE14 named results

Every result below is stated at the registered finite scope of `FREEZE_V1.md`:
input space `X = {0,1}^4`, the registered block decomposition
`{x0,x1} | {x2,x3}`, junta arity `2`, decision-tree depth `2`, composition depth
cap `3`, the order-4 coordinate-rotation group, the frozen four-rule Horn system
over six atoms, and `200` null trials. All quantities are exact rationals or
integers; no float appears in any claim. Route A is
`ae14_generalization_taxonomy_v1.py`, route B is
`independent_taxonomy_oracle_v1.py`, and the two agree on every value reported
here.

## Definition D-AE14 (the seven modes as exact predicates)

A **task** is a map `t : X -> {0,1}` together with a registered training support
`Tr subset X`. `span(Tr)` is the smallest subcube of `X` containing `Tr`:
every coordinate constant across `Tr` is fixed, the rest are free. A **learner
class** `L` is a finite set of functions `X -> {0,1}`, given either as an
explicit family or as a family of algorithms instantiated on the training data.

For a mode `M`, a class `L` and a support `Tr`, the predicate `M(t, L, Tr)`
holds iff the registered structure of `M` at `Tr` is non-empty and some member
of `L` is exact on `Tr` together with that structure:

| mode | registered structure at `Tr` |
|---|---|
| `MEMORIZATION` | exact on `Tr`, and scoring **exactly** the base rate on `X \ Tr` |
| `INTERPOLATION` | `span(Tr) \ Tr` |
| `EXTRAPOLATION` | `X \ span(Tr)` |
| `SYSTEMATIC_GENERALIZATION` | the recombinations of block values occurring in `Tr`, minus `Tr` |
| `ANALOGY` | the answers `g.c` for `c` in `Tr` and every group element `g` that never appears in `Tr` |
| `PLANNING_INFERENCE` | the points no single registered primitive maps into `Tr` but some word of length at most `3` does |
| `REASONING` | the entailments of shortest derivation depth at least `2` outside `Tr`, together with their one-atom non-entailed neighbours |

The registered classes are `L0` (every function constant off `Tr`), `L1` (the
2-juntas computable by a depth-2 decision tree, 70 functions), `L_lin` (the 32
GF(2)-affine functionals), `L_mod` (the block-modular compositions
`h(g1(block1), g2(block2))`, 520 functions) and `L_search[3]` (operator subsets
of `{pi1, pi2, rho, tau}` with a registered readout: transport the query by the
lex-least word of length at most `3` and read the training label, or report
whether an atom is derivable within three applications).

---

## AE14-1 — the seven modes are architecture-independent exact predicates

**Scope.** The registered roster of eleven tasks and five classes, 55 cells per
mode. **Quantifiers.** For every mode, every task and every class, the predicate
is decided exactly.

Each predicate reads only the function realized on `X`, the registered support,
and the registered structure derived from that support. No predicate mentions a
layer, a parameter count, a training procedure or a model family, so two systems
realizing the same function on `X` from the same support receive the same verdict
by construction. The receipt carries the full `7 x 11 x 5` truth cube and, for
each ordered pair of distinct modes, a registered `(task, class)` cell on which
the first holds and the second fails: **41 of the 42 ordered pairs are separated,
every one of them by a witness whose second mode has a non-empty structure**. The
remaining pair is AE14-8.

**Assumptions.** The registered input space, block decomposition, group,
primitives and rule system of `FREEZE_V1.md`; classes enumerated exhaustively.

**Dependencies.** `span`, `recomb`, `analogy_pts`, `plan_pts`, `reason_pts` and
the five class builders of route A, each recomputed by a materially different
algorithm in route B.

**Falsifiers.** A registered cell whose reported truth value differs from a
direct recomputation; an ordered pair reported as separated whose witness cell
does not in fact hold the first mode and fail the second; a predicate whose
value changes when the realized function and support are held fixed.

**Strongest parents.** The operational split between memorization and
generalization is Zhang, Bengio, Hardt, Recht and Vinyals (2017) and Feldman
(2020); the interpolation-versus-extrapolation geometry is Balestriero, Pesenti
and LeCun (2021); systematic generalization is Fodor and Pylyshyn (1988), Lake
and Baroni (2018) and Hupkes, Dankers, Mul and Bruni (2020); analogy as structure
mapping is Gentner (1983). Nothing in the definitions is claimed novel against
them.

---

## AE14-2 — three modes are realized by no prediction-only learner and exactly by the composition class

**Scope.** The three registered home specifications `GROUP_ORBIT`,
`COMPOSITION_DEPTH_GE_2` and `DEDUCTIVE_CLOSURE`. **Quantifiers.** For **every**
member of **every** prediction-only class — all functions constant off the
support, all 70 depth-2 juntas, all 32 affine functionals, all 520 block-modular
compositions — the joint accuracy on the registered constraint set is strictly
below `1`; the exact maxima are

| specification | constraint points | best over `L0` | `L1` | `L_lin` | `L_mod` | `L_search[3]` |
|---|---|---|---|---|---|---|
| analogy on `T_ANALOGY` | 15 | `11/15` | `11/15` | `11/15` | `13/15` | `1` |
| planning on `T_PLAN` | 10 | `4/5` | `4/5` | `4/5` | `4/5` | `1` |
| reasoning on `T_REASON` | 10 | `4/5` | `9/10` | `4/5` | `9/10` | `1` |

Because the classes are enumerated whole, "no prediction-only learner realizes
it" is decided, not sampled. The machinery that does realize each one is named:
the analogy specification is realized only by transport members
(`lookup|pi2+rho|d` among 8 realizing members, no derivability readout realizes
it); the reasoning specification only by a derivability readout
(`atom|tau|5`, `atom|pi2+tau|5`; **no** transport member realizes it); the
planning specification by transport members over the two planning primitives.
Restricting the composition class to depth `1` drops all three below `1`
(`14/15`, `4/5`, `9/10`), so the depth cap is load-bearing.

**Assumptions.** The registered budgets: junta arity `2`, tree depth `2`,
one-bit per-block features, composition depth cap `3`. The claim is about these
budgets and no others.

The freeze fixes the input space, the blocks, the group, the primitives, the
rule system and the budgets, and leaves each task's training support to the
instantiation, so the supports were chosen here and their provenance is
disclosed in full. For `T_PLAN` and `T_REASON` the support is the outcome of an
exhaustive search over every support of the registered sizes, keeping those
whose registered structure is non-degenerate — at least four planning targets, a
non-empty depth-2 entailment set, both labels present in the evaluation set and
in the support — **and** on which the separation being claimed actually obtains.
That search is a construction, which is what the row asks for, not a test of a
pre-chosen support: `T_PLAN = {0, 2, 3, 6, 14}` is the one maximising the
resulting margin, `1/5`, and `T_REASON = {0, 4, 8, 10}` is the lexicographically
least qualifying support. `T_SYS = {0, 5, 10, 15}` is the block diagonal, chosen
by a criterion that mentions no outcome at all — it maximises the number of
held-out recombinations, `12` of the 16 points — and `T_ANALOGY = {0, 1, 3, 5, 7}`
was fixed by hand so that no non-identity group element is witnessed in it.

What is **not** chosen after the fact: the class enumeration behind every number
in the table above, the exhaustive family sweep of AE14-6, the null controls,
and the register, all of which are computed once the construction is fixed. The
family sweep is what carries AE14-6 past the seven constructed instances.

**Dependencies.** AE14-1 for the predicates; the exhaustive class builders; the
bound records `AE14-B-PREDICTION-ONLY-*` and `AE14-B-COMPOSITION-*`, each
carrying a `violated_by` witness from an explicitly relaxed class (relaxing the
junta arity to 3, or the block decomposition to any balanced 2+2 coordinate
partition, lifts the prediction-only maxima to `14/15`, `1` and `1`
respectively; relaxing the depth cap downward to 1 breaks the lower bound).

**Falsifiers.** A single prediction-only member exact on one of the three
constraint sets; a composition member reported as exact that is not; the same
three separations surviving when the registered budgets are held but the
supports are replaced by the ones the receipt names.

**Strongest parents.** Junta and decision-tree lower bounds are Mossel,
O'Donnell and Servedio (2004) and O'Donnell (2014); the learnability frame is
Valiant (1984) and Blumer, Ehrenfeucht, Haussler and Warmuth (1989); the claim
that composition is not recoverable from prediction over a non-compositional
class is Fodor and Pylyshyn (1988) and Lake and Baroni (2018). The residual here
is the exact finite construction and its machine-checked verification.

---

## AE14-3 — four modes reduce to prediction at their registered specification

**Scope.** The registered home specifications `LOOKUP_ONLY`, `JUNTA`, `AFFINE`
and `BLOCK_FACTORIZED`. **Quantifiers.** For each, some member of a
prediction-only class is exact on the whole constraint set.

Memorization is realized by the base-rate constant off the support (`L0`,
`13/16` on 16 constraint points, which is the base rate exactly); interpolation
by a depth-2 junta (`1` on 8 points, where `L0` reaches only `3/4`);
extrapolation by an affine functional (`1` on 12 points, where `L1` reaches
`7/12`); systematic generalization by a block-modular composition (`1` on 16
points, where `L0`, `L1` and `L_lin` reach `7/8`, `3/4` and `3/4`). Together with
AE14-2 this answers the row exactly: **four of the seven modes are reducible to
prediction under the registered specification and three are not.**

**Assumptions.** The classification is indexed by the registered home
specification of each mode. It is not a claim about the mode at every support.

**Dependencies.** AE14-1; the same exhaustive class enumeration as AE14-2.

**Falsifiers.** A prediction-only class reported as realizing one of the four
whose witness member is not in fact exact; or a demonstration that the least
realizing class is lower in the registered priority order than reported.

**Forbidden extrapolation.** The receipt reports the counter-direction
explicitly: away from its home task, extrapolation on `T_ANALOGY` is realized by
the composition class and by no prediction-only class, and planning and reasoning
acquire further hard instances. Reducibility is therefore a property of the
`(mode, specification)` pair, never of the mode alone.

**Strongest parents.** As AE14-2; additionally Rissanen (1978) and Grunwald
(2007) for description-length-indexed model classes.

---

## AE14-4 — equal predictive accuracy with different compositional capability

**Scope.** The registered matched pair `T_MATCH_COMPOSITIONAL` and
`T_MATCH_LOOKUP` with the shared support `{0, 15}` and shared test points
`{5, 6, 9, 10}`. **Quantifiers.** The two tasks agree on every point of the
shared training view and differ exactly on the two held-out block
recombinations `{3, 12}`.

Their Bayes predictive accuracy on the registered test distribution — uniform on
the shared test points with the registered symmetric label noise `1/4` — is
therefore **exactly equal: `3/4` and `3/4`**. The shortest-code model consistent
with that view is index `0` of the frozen model order at `3` bits, and its exact
accuracy on the held-out recombinations is **`0` for the compositional task and
`1` for the lookup task**. All four numbers are reported in the receipt. Nothing
in the training or test data distinguishes the pair; only the recombination
behaviour does.

**Assumptions.** The registered test distribution and noise rate; the frozen
model order and its integer code.

**Dependencies.** The block decomposition; the model space of AE14-5.

**Falsifiers.** A point of the shared training view on which the two tasks
disagree; a shorter consistent model than index `0`; a recombination accuracy
that differs from a direct recount.

**Strongest parents.** Compositional generalization benchmarks with matched
in-distribution accuracy are Lake and Baroni (2018) and Hupkes, Dankers, Mul and
Bruni (2020); the Bayes-accuracy identity under label noise is textbook
statistical decision theory.

---

## AE14-5 — equal integer description length with different transfer

**Scope.** The frozen model space: the 32 affine functionals in registered
`(mask, bias)` order, then the depth-2 juntas, then the block-modular
compositions, deduplicated, 520 models. The code assigns
`1 + 2*ceil(log2(index+2))` bits, computed with integer arithmetic only.
**Quantifiers.** Over the 16 points of the registered input space.

The code is Kraft-compliant over the whole model space: the exact sum of
`2^-length` is `523273/2097152 <= 1`. `T_CODE_A` sits at index `16` and
`T_CODE_B` at index `20`, both in the same plateau, so their description lengths
are **exactly equal at `11` bits**. Their exact transfer accuracy to the
registered target task is **`3/8` and `3/4`**, a gap of `3/8`. Equal
compression therefore does not fix transfer at the registered scope.

**Assumptions.** The frozen model order and prefix-free code; the registered
transfer target and the transfer set (all 16 points).

**Dependencies.** The class builders of AE14-2; the bound record
`AE14-B-TRANSFER-GAP`, whose `violated_by` witness is the pair `(T_CODE_A,
T_CODE_A)` in the explicitly relaxed class of equal-length pairs not required to
be distinct, with gap `0`.

**Falsifiers.** A code length recomputed differently; a transfer accuracy that
differs from a direct recount; a violation of the Kraft inequality.

**Forbidden extrapolation.** This is a statement about one frozen code over one
frozen model space. It does not say that description length is uninformative
about transfer in general, and it is not evidence for or against any identity
between compression and capability.

**Strongest parents.** Kraft (1949); Rissanen (1978); Grunwald (2007).

---

## AE14-6 — the frozen mechanism predictor is right on all seven registered structure types

**Scope.** The seven registered structure types and their home specifications.
**Quantifiers.** The predictor table was frozen in
`PROSPECTIVE_REGISTER_V1.json` before any evaluation existed; the executor
recomputes the register's own digest and refuses to emit on mismatch.

The least class of the registered priority order that realizes each home mode is
`L0`, `L1`, `L_lin`, `L_mod`, `L_search`, `L_search`, `L_search` — exactly the
frozen table, **`7` hits of `7`**. The registered null draws a uniformly random
class for each structure type, `200` trials: its **largest hit count is `4`**,
and the rate of trials at or above the predictor is `0/200`. The primary
comparison is threshold-free.

One cell is guaranteed by the definitions and is declared as such: the base-rate
constant off the support attains the base rate on every task, so `LOOKUP_ONLY`
must map to `L0`. Restricted to the six evidential cells the predictor scores
`6` against a null maximum of `4`. Beyond the seven registered instances, an
exhaustive sweep over every function whose least structure type is the swept one
gives hit rates `1` (affine, 10 of 10), `1` (junta, 48 of 48), `1`
(block-factorized, 432 of 432), `1` (composition-depth, 2 of 2) and `26/27`
(group-orbit, 52 of 54) — so the result is not an artifact of the seven chosen
instances.

**Assumptions.** The registered class priority order (lexicographic by name
ascending) defines "least"; the registered supports of the home tasks are held
fixed across the family sweep.

**Dependencies.** AE14-2 and AE14-3 for the per-cell least classes; the register
digest check; the bound records `AE14-B-PREDICTOR-HITS` (violated by a cyclic
shift of the frozen table, which scores `2`) and `AE14-B-NULL-CEILING` (violated
by assignments constrained to agree on the five lexicographically first types,
which score `5`).

**Falsifiers.** A structure type whose least realizing class differs from the
reported one; a null trial exceeding `4` under the registered stream; a family
member reported as a hit whose least class is not the predicted one. The two
group-orbit family misses are reported individually rather than suppressed.

**Forbidden extrapolation.** This predicts which of five registered mechanism
classes a registered structure type needs, at `n = 4`, under the registered
budgets. It is not an architecture law and says nothing about which model class
a real system should use.

**Strongest parents.** The idea that a task's structure dictates the hypothesis
class that can exploit it is the inductive-bias tradition of Valiant (1984) and
Blumer, Ehrenfeucht, Haussler and Warmuth (1989); the group-orbit case is
classical invariance theory.

---

## AE14-7 — the blanket claim is blocked and the block is machine-checked

**Scope.** The registered promotion named in `FREEZE_V1.md` as the blanket
identification of memory, generalization, analogy and reasoning as one mechanism
at different scales. **Quantifiers.** Over every artifact of this package.

A reduction theorem earning that promotion would need, at minimum, a
prediction-only learner realizing every mode under the registered specification.
AE14-2 exhibits three specifications where every member of every prediction-only
class falls strictly short while the composition class is exact, so no such
theorem exists at this scope and the promotion is refused. The executor scans
every artifact of the package and reports `0` unguarded assertions of the
blanket string; the checker is validated in both directions, firing on a planted
assertion and on a bare unattributed occurrence, and staying silent on a
declared forbidden-promotion list.

**Assumptions.** The refusal is at the registered scope. A reduction theorem at
another scope is not addressed, and its absence here is not evidence that one
cannot exist elsewhere.

**Dependencies.** AE14-2; the guard checker and its two-direction validation.

**Falsifiers.** A prediction-only learner realizing all seven modes at the
registered specification; an artifact of this package asserting the blanket
string that the checker does not flag.

**Strongest parents.** The compositionality critique of Fodor and Pylyshyn
(1988). The residual is the machine-checked refusal, not the critique.

---

## AE14-8 — interpolation implies systematic generalization wherever the recombination structure is non-empty

**Scope.** Every non-empty training support of the registered input space.
**Quantifiers.** All `65310` supports on which the recombination structure is
non-empty were checked; there is no counterexample.

The recombination set of a support is contained in its spanned subcube, because
every coordinate constant across the support is constant across every
recombination of block values occurring in it. Exactness on the interpolation
constraint set therefore forces exactness on the systematic-generalization
constraint set, for **every** class: wherever the recombination structure is
non-empty, no learner can interpolate and fail to recombine. Where that
structure is empty the second predicate is false by the registered
non-degeneracy convention and nothing is implied — `Tr = {0, 3, 12, 15}` is such
a support, recombination-closed with a non-empty interpolation structure. The
ordered pair is reported as `NOT_SEPARATED` with this
certificate, and prospective prediction `AE14-P1` — which asserted a complete
pairwise distinctness table — is reported as `REFUTED` rather than edited.

**Assumptions.** The registered definitions of `span` and of the recombination
set; the block decomposition of `FREEZE_V1.md`.

**Dependencies.** AE14-1; the exhaustive support check in the executor, verified
independently in route B by intersecting every subcube containing the support.

**Falsifiers.** A support whose recombination set escapes its spanned subcube; a
class member exact on the spanned subcube and inexact on a recombination point;
a separating cell for this ordered pair whose second structure is non-empty.

**Forbidden extrapolation.** The implication is one-directional and specific to
these two modes at the registered block decomposition. The converse fails, and
the receipt carries the witness: the reverse pair is separated.

**Strongest parents.** Elementary lattice reasoning over subcubes; no novelty is
claimed.
