# Grand GMI Developmental Underdetermination Theorem V1

Status: **SCOPED UNDERDETERMINATION + CONSTRUCTIVE FINITE CLOSURE; V2 REPAIR**
Date: 2026-09-13. The historical V1 receipt is preserved; current evidence is
`GRAND_GMI_DEVELOPMENTAL_UNDERDETERMINATION_RECEIPT_V2.json`.

## 1. Register and scope of the repair

Fix admitted realizations X, scalar profiles c:X->R_(>=0), family labels,
initial state s0, and a development transition relation D. At most B legal
updates define Reach_B. In a controlled system D may include all admitted
actions; a particular policy can induce a smaller reachable set. Profiles,
legal transitions, admission and resource semantics must be registered.
Reachability is existential over legal paths, not a guarantee under every
policy or stochastic rollout. B counts updates here; path-dependent resource
costs require charged edges or augmented state, not an identification of update
count with total development work.

Static realization summaries alone need not identify development. That is a
missing premise for unconditional prediction, not a reason to close the
constructive registered-D learning programme. The package already carries D
and contains conditional reachability/controlled-acquisition machinery.
Neither this witness nor an undecidability theorem forbids useful conditional
training, control, convergence or finite attainability theorems.

The V1 wording overreached in three places: it promoted static-summary
underdetermination to an impossibility of derivation; promoted lower-bound
monotonicity to persistence of competitive exclusion; and treated finite
prefixes as incapable of ever certifying a limit. These claims are corrected
below, with positive retained-comparator and complete-closure certificates.

## 2. DU-1 — static data alone does not identify an unconstrained D

Two laws can share X, c, family assignment and all D-independent necessities
while giving different Reach_B and family support. Let X={s0,a,b}, costs
10,5,3 and labels A,A,B. One law permits only s0->a, the other only s0->b.
At B=1 their cheapest reachable families are A and B respectively. Hence no
single exact map from those shared static summaries predicts the reachable
frontier for every otherwise unconstrained D. This is an elementary witness.

It does not show that D cannot be constructed, identified from additional
observations, or determined by stronger hypotheses. It does not forbid all
conclusions independent of D: static lower bounds remain valid. Statements
about every other component of the full package are unwarranted when some
components already encode development. Concrete registered-D research and
theory-guided design remain open work, including the constructive Q2 target.

## 3. DU-2 — chosen schedules and all-schedules reachability differ

Start at 1 with operations double and add_three; accept a transition only if
its proposed value is at most 6. The prescribed order double/add_three reaches
1,2,5. The order add_three/double reaches 1,4, then rejects proposal 8. The
last admitted state is 4, not the rejected state 8.

Thus selecting a schedule matters to its trajectory. It does not follow that
one must prescribe a schedule to define reachability: if every admitted
operation may be chosen at every step, the fully specified transition relation
already determines the union over all schedules. At B=2 this union is
{1,2,4,5}. Composition, admission and policy quantifiers are required; a fixed
schedule is not. Policy synthesis over this graph is legitimate constructive
work, as in finite dynamic programming and the registered controlled layer.

## 4. DU-3 — restriction preserves lower bounds, conditionally exclusions

For X'_F subset X_F in the same task/profile scope,

    inf_(x in X'_F) c(x) >= inf_(x in X_F) c(x),

with inf(empty)=+infinity. This follows from set inclusion. A sound lower
bound on X_F remains a lower bound on X'_F. A fixed relaxation intersected
with additional sound constraints also has a nondecreasing infimum. Arbitrary
new numerical lower-bound estimates are not monotone unless previous valid
bounds are retained or combined with them.

**Competitive exclusion also needs its comparator.** Suppose L_F bounds every
remaining F realization from below and a specific realization a outside F is
retained, with certified c(a)<=U_a<L_F. Then every remaining F realization
costs more than the retained a, so F cannot attain the scalar optimum. The
same proof remains valid under further restriction only if that comparator
(or another adequately bounded one) remains available, at the same task,
valuation, development budget and jointly feasible comparison scope.

The V1 counterexample refutes unconditional exclusion persistence: globally
A has costs 2,9 and B has cost 5. The witness A2 excludes B because 2<5.
Restrict to {A9,B5}: the target lower bound 5 remains valid, but A2 is gone
and B now wins. Restoring the reachable comparator A2 restores the exclusion.
Thus both selections and comparative exclusions can change under restriction;
only the lower-bound inequality survives without a construction premise.
Absolute impossibility below a fixed threshold is distinct from exclusion
by comparison and does retain its valid lower-bound certificate.

## 5. DU-4 — finite prefixes need continuation control, which can be certified

A bounded observed prefix alone need not determine a later verdict. For any
B>=0, take prefix s0->...->sB with costs 1/(i+1) and family A. One continuation
stops there; another adds s_(B+1) of cost 1/(B+2) in family B. The laws agree
through budget B but their eventual cheapest families differ. No single exact eventual cheapest-family prediction
from that prefix alone is valid uniformly over both possible continuations.

This does not imply that no finite budget can certify unbounded reachability.
For a complete registered transition relation, a finite set R with

    s0 in R, every member has a certified path from s0, and D(R) subset R

is **exactly** Reach_infinity. Paths prove R subset Reach_infinity; induction
on path length using successor closure proves the reverse inclusion. If all
these paths have length at most B, then Reach_B=Reach_infinity. The finite
frontier computed on R is therefore the exact unbounded frontier of this
registered graph. This is a positive certificate, not empirical extrapolation.

Equivalently, for a finite graph, Reach_(B+1)=Reach_B is a fixed point and
certifies all later reachable sets. Exhaustive breadth-first exploration
finds it after at most |X|-1 steps from one initial state. The transition
relation must be complete, and any schedule/memory/admission state affecting
future transitions must be represented. Observing no new state in sampled
updates is not a successor-closure proof.

The finite positive witness stops after s0->s1->s2 with costs 3,2,1 in A.
Its path-and-closure certificate proves A optimal for unbounded development.
Adding s2->s3 at cost 1/2 in B preserves the budget-2 prefix but invalidates
that certificate and changes the eventual optimum to B. Extending the
certificate to include s3 then proves the new exact result.

Nor does every improving, family-changing edge force the budget optimum to
alternate in a branching graph. A10->B1 and A10->B9->A8 satisfy those edge
conditions, but B1 is best at both budgets 1 and 2. Alternating optimal support
was valid only for V1's particular single chain. Its known length-8 chain is
itself exhausted at budget 8, contrary to the former universal no-finite-budget
claim. Infinite or partially known systems need their own induction or other
continuation certificates; they are not settled by this finite construction.

## 6. Parent assimilation, evidence and remaining constructive work

[Bradley, *SAT-Based Model Checking Without Unrolling* (2011), Sections 2–3](https://theory.stanford.edu/~arbrad/papers/IC3.pdf)
provides the transition-system and inductive-invariant parent: inclusion of
initial states plus closure under transitions bounds every reachable state.
We use that principle faithfully and add explicit path witnesses for equality;
we do not implement or claim a new IC3 algorithm. Set-inclusion monotonicity,
finite graph reachability and schedule composition are elementary parents.
The package's phase/accounting and controlled-acquisition results supply the
registered profile and action semantics; their hypotheses remain necessary.

The V2 checker executes all four repaired witnesses. Tests additionally compare
finite reachability against independent transitive closure on all 512 directed
three-state graphs and reject malformed, incomplete and non-path certificates.
V1's synthetic numbers remain historical evidence, not authority for its
superseded broader claims. No learning dynamics or resource costs were measured.

Closed here: the static-summary counterexample and the two specific invalid
inferences, with constructive conditions under which exclusion and unbounded
finite-graph selection are certified. Still open: choose or learn a useful D,
prove or measure its costs and attainable outcomes, optimize admitted policies,
and transfer/replicate beyond the registered instance. These are substantive
research obligations, not reclassified away as underdetermination.
