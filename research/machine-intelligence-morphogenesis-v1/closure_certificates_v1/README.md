# GMI closure certificates v1

Integration base: `858bb7f6c67e4a17cc75027933b5d95346347c8b` (PR #447).
These are same-author, bounded formal corrections and development controls.
They do not declare full GMI closure or amend a protected execution freeze.

## Reproduce

From this directory, Python 3.11 or later, standard library only:

```sh
python run_checks.py
python legacy_class_bound.py > legacy-integration.json
```

The first command runs all unit tests, 78,732 exact frontier equivalence checks,
216 finite class-bound comparisons, and an executed complete-language frontier
control. It writes machine-readable evidence and fails on failures OR skips.
The second command requires the complete repository, checks six upstream Git
blob identities, imports the actual modules, reproduces the witness/class
counterexample and constant-resource recall surrogate, and exhaustively computes
a target-class minimum. It does not use fixtures or a rewritten scoring model.
The GitHub workflow separately runs the default runtime suite and four existing
K4 research suites. Local checks do not impersonate those CI results.

## Components and exact claim scopes

`gmi_closure_microscope.py` implements tie-aware frontier identification, exact
finite minimax regret, full-rectangle interval regret, full-rank coefficient
recovery inside a declared model, and a bounded-observation alpha-spending bound.

`target_witness_gap.py` preserves the earlier source-derived algebraic projection
and checks bound directions. Its numbers alone are not repository execution.

`legacy_class_bound.py` supplies the missing whole-target-class optimization in
the pinned finite surrogate. It enumerates all matching state/work expressions,
all 1..3-element capability subsets, both widths, and ALL matching V5 inert-null
realizations with their distinct null cost rule. Target equality fixes the other
eight coordinates. No numeric lower bound or completeness boolean is trusted
from a caller. Rivals are checked against the same domain and rescored. A null
discount requires the exact registered null ID AND realization, not a flag.

The bound is the exact minimum of the pinned Python floating-point scorer over
that finite product-plus-null domain. It is NOT exact real-number arithmetic,
not an unrestricted architecture bound, and not a realizability proof. The
class may strictly contain the hash sampler's attainable support; this makes
a lower bound conservative for any smaller sampled target class. A failure to
beat this enlarged class does not prove optimality in every smaller class.

`execution_controls.py` enumerates and EXECUTES 548 arithmetic programs at its
default bound. Output correctness and serving-token cost come from the same
execution. Structural token/stack certificates are checked on nine inputs per
program. `certify_finite_frontier` computes a complete target-class optimum after
ranking. Changing the target cannot change the domain/evaluation digest or the
winner. Its objective is description tokens plus registered serving-token steps;
search work is separately reported. Bit complexity, host overhead, physical
energy and generalization outside the registered finite examples are excluded.

`realizability_checks.py` supplies a fixed-decoder exact-recall capacity theorem
and a byte-packed constructive witness. All 2,047 binary datasets through ten
records and 18,434 queries are checked. Public size metadata and Python object
overhead are not included in the payload bit count.

`claim_audit.py` wraps legacy receipts in a separate interpretation containing
the unchanged original JSON data, a canonical digest and the original verdict.
It distinguishes recorded witness dominance from class dominance and capability
scores from actual machine realization. An absent winner is never a successful
noninterference witness. One unchanged paired projection is only one observation,
not a universal proof. This audit does not consume or validate an external
class certificate; use the separately recomputed class comparison instead.

```sh
python claim_audit.py path/to/development-receipt.json
```

An opt-in `run_development_cell` wrapper caps legacy sampling at 20,000. It does
not acquire a seed, launch a protected run, or overwrite any historical receipt.

## Proofs

### Tie-aware frontier identification

For finitely many worlds sharing observable descriptor X and a common finite
admissible candidate set, define `A_e(w)={a:C(a,w)<=min_b C(b,w)+e}`. A single
X-only choice has regret at most e in every world iff `intersection_w A_e(w)`
is nonempty. Necessity follows because the same choice is made in every world;
sufficiency follows by choosing an intersection member. For finitely many worlds,
an almost-sure randomized guarantee requires mass one on that intersection.
Different named minimizers are insufficient: rows (0,0) and (0,1) share winner A.
Pairwise overlap is insufficient for three sets: {A,B}, {B,C}, {A,C}.
See the corrected parent EF-1 document.

### Witness versus class

An admissible target witness gives `inf_T C <= C(witness)`, an upper bound.
A rival beating it does not beat all of T: target costs 10 and 1, rival cost 5.
A VALID lower bound `L <= inf_T C`, together with `C(rival)<L`, proves strict
pointwise dominance over T. For a finite fully enumerated nonempty class, its
minimum supplies such a bound. An empty target class is reported separately.
For infinite classes, strict pointwise dominance need not mean strict inequality
to an unattained infimum; the sufficient lower-bound statement avoids that error.

Completeness of the legacy enumerator follows directly from the pinned sampler:
state and serve are picked from the listed finite expression tuples; capability
atoms are sorted distinct subsets of cardinality one, two or three; width is one
or two; vector equality fixes five categorical and three boolean coordinates.
Enumerating every expression with the target's measured labels and every allowed
atom/width choice contains every matching sampled candidate. The six typed V5
nulls are then checked for target membership too. Admissibility and both cost
rules are evaluated by the pinned source. Taking the smallest evaluated cost
therefore computes the finite surrogate minimum. Code hashes are integrity and
scope bindings, not signatures proving independent authorship.

### Measurement and resource identification

Finite probes cannot identify an unrestricted asymptotic law: n and a law equal
to n up to the largest probe but n^2 afterward are indistinguishable on that panel.
For a declared linear model `y=A theta`, unrestricted coefficients are uniquely
identifiable exactly when A has full column rank. A nonzero nullspace vector
proves necessity; injectivity and solving the consistent system prove sufficiency.
The implementation rejects rank deficiency and exact model mismatch.

For full Cartesian uncertainty `C_i in [L_i,U_i]`, choosing i has exact worst
regret `max(0,max_{j!=i}(U_i-L_j))`; exclude i from the competitor minimum.
This is an upper bound rather than an exact result for correlated uncertainty.
The statistical radius assumes bounded iid samples per fixed candidate; adaptive
stopping does not authorize adaptive candidate changes or outcome-selective reruns.

### Constructive sufficiency and morphogenesis bridges

If the candidate domain contains an admissible witness within gamma of an
externally declared optimum, estimated objectives have uniform error eta, and
search has estimated suboptimality rho, its true regret is at most
`gamma+2 eta+rho`. Compare selected estimated cost to the covered witness and
apply the error bound at each endpoint. A prospectively predicted morphology Q
is then selected if every rival morphology has gap greater than that total.
Coverage, uniform evaluation accuracy, search accuracy and rival separation are
PREMISES; the equation does not discharge them for the full GMI domain.

A forward compiler alone does not transfer a frontier theorem: the destination
may contain unmatched cheaper competitors. With morphology-preserving forward
and competitor-covering reverse maps, objective distortion at most epsilon in
each direction preserves a source separation g whenever `g>2 epsilon`.
Actual architecture maps and their coverage/resource proofs remain obligations.

If from every not-yet-successful history the conditional probability of reaching
a target within L further steps is at least q, then
`P(T>kL)<=(1-q)^k` and `E[T]<=L/q` for q>0. Condition successively on failed blocks;
independence is unnecessary. This does not supply q or L for an actual learner,
or prove persistence after the first hit, adaptation, stability or self-modification.

### Exact recall and independence

A fixed decoder for all N independent b-bit records and all indices needs N*b
bits of dataset-dependent capacity: distinct datasets must encode to distinct
states because some query separates them. Storing the records supplies the upper
bound. No uncharged external store, code or infinite-precision word is permitted.
Query time depends on the access model; the capacity proof alone does not impose
logarithmic query time or demonstrate developmental acquisition.

Exhaustion removes discretion CONDITIONAL ON the chosen class, not information
in selecting the class itself. Bijective token renaming with conjugated semantics
preserves a hypothesis class; disjoint spellings do not prove independent design.
A future timestamp does not prove seed entropy, and publication order alone does
not prove private execution order. Same-author review cannot certify an
independent-author gate. These are explicit limits, not waived requirements.

## Review and remaining gaps

Formal-methods, interpreter/resource-accounting, and experimental-governance
perspectives were used for self-review; there were no independent coauthors or
proof-assistant checks. The review specifically caught omission of same-target
nulls from a product-only bound and added them before integration.

The evidence still needed includes execution-coupled realizations across the
registered architecture families, constructive developmental acquisition at
charged budgets, domain-wide compiler coverage, independent primitive/meter
construction, protected predictive/transfer evidence and physical measurements
where claimed. A finite surrogate optimizer and small exact controls do not
satisfy these larger obligations. Both broad closure terminals remain FALSE.
