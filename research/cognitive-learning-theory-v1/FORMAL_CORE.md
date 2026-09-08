# A scoped formal core for epistemic structure discovery

**Disposition: ADOPT / PARENT_SUFFICIENT for the mathematical core below.**
These are elementary specifications, reductions and proofs, not claims of new
theorems, a complete theory of cognition, or submission readiness. The primary
route is V1 for the propositions; separately implemented finite checks are V2
calibration. Novel empirical residuals remain hypotheses requiring #144 gates.

Governing sources read for this tranche: current local snapshots of #143,
#144 and #145 in `research-context/issue-{143,144,145}.md`, and
`../self-evolution-v1/EPISTEMIC_STRUCTURE_DISCOVERY.md`. Their protected protocols,
outcomes and claim ceilings are unchanged. All definitions are relative to
representation, registered ecology, resource bounds and external constitution.

## 1. Parent reduction and the remaining question

Maintaining hypotheses consistent with observations is version-space learning.
This supplies the parent for FC1, not an ORION-specific learning operation.
[Mitchell, Version Spaces: A Candidate Elimination Approach to Rule Learning](https://www.ijcai.org/Proceedings/77-1/Papers/048.pdf).

Deciding without uniquely identifying the hidden model is directly parent-owned.
Javdani et al. formulate active learning with overlapping decision regions and
give conditions for locating the remaining hypotheses inside one such region.
FC3 is a finite noiseless specialization of that problem, not a novel
"decision-relevant epistemics" theorem.
[Near Optimal Bayesian Active Learning for Decision Making](https://arxiv.org/abs/1402.5886).

EC2 supplies a related strong parent for active learning under noisy observations
and unequal test costs. Our noiseless finite recurrence does not inherit that
paper's noise or approximation guarantees.
[Near-Optimal Bayesian Active Learning with Noisy Observations](https://arxiv.org/abs/1010.3091).

Conservative semantic approximation and alternative assumption supports are
established parents for FC2 and FC5. A union of possible effects is not a new
field operator; support antichains are not new epistemic atoms.
[Cousot and Cousot, Abstract interpretation](https://www.di.ens.fr/~cousot/COUSOTpapers/POPL77.shtml),
[de Kleer, An assumption-based TMS](https://www.sciencedirect.com/science/article/pii/0004370286900809).

The remaining empirical question is whether a machine can **acquire** useful
lifecycle effect/decision models, retain their warranted scope, and use them to
reduce complete future acquisition and repair costs beyond equally informed,
equally adaptive parents. Supplying the true model family, effect table, action
regions, dependency grouping or sound equations is prior information. Their
construction cannot be silently credited to the learner.

## 2. Declared objects and scope

Let the following objects be finite for the exact theory laboratory.

| Symbol | Meaning |
|---|---|
| `F` | Field representation and executable interpretation of machine states |
| `X` | Admissible states, including evidence, environment and authority versions |
| `Q` | Fixed externally meaningful behavioral and epistemic obligations |
| `C` | External preservation/adoption constitution and authorized checker semantics |
| `H` | Candidate lifecycle effect models; model identity need not equal graph syntax |
| `P` | Registered diagnostic probes with explicit outcome and cost semantics |
| `A` | Executable repair/configuration actions, including their certificates |
| `E` | Registered intervention ecology and finite lifecycle horizon |
| `B` | Resource envelope, with separate information/computation/storage coordinates |

A model `m` predicts probe outcomes `o_m(p)` and the registered lifecycle
consequences of interventions/actions. Contexts may be included in `p` and `a`.
The lifecycle observation of an obligation includes all contractually required
truth, warrant scope, dependencies, uncertainty, authority, revocation and
reopening behavior. Equal final task answers need not mean equal lifecycle
observations. If causal effects are claimed, intervention and counterfactual
semantics must be specified; passive associations alone do not supply them.

For FC3/FC4, probes are deterministic, noiseless and resettable or state
preserving: a probe does not change another probe's outcome or the later action
problem. A finite sequence of state-changing interventions requires an expanded
state/model and history-dependent planning problem; the simple recurrence does
not cover it. In stochastic extensions, choose distributional semantics and
error guarantees explicitly instead of treating repeated samples as proof.

The model's prediction that an action is safe does not issue authority. External
admission checks remain necessary. In an exact world the acceptable-action table
can be computed by an independent checker. In an empirical world uncertain or
unavailable authority receipts exclude the action from the certified set.

## 3. FC1 — Version-space contraction, revocation and misspecification

For a finite set of live, scope-compatible observations
`D = {(p_i, y_i)}`, define

\[
V(D)=\{m\in H:\ \forall(p,y)\in D,\ o_m(p)=y\}.
\]

**Proposition FC1.** If `m*` belongs to `H` and every observation is sound for
`m*` in the declared scope, then `m*` belongs to `V(D)`. Adding sound observations
can only shrink the version space. Removing an observation constraint, including
because its warrant was revoked, can only expand the version space.

**Proof.** The true model satisfies every defining equality. Adding equalities
takes an intersection with more sets; deleting equalities removes restrictions.
Thus for `D1 subset D2`, `V(D2) subset V(D1)`. No probability or majority vote is
needed. QED.

Revocation broadens the admissible model set; it does not establish that the
revoked observation was false. A changed checker/environment starts a new scope
unless an authorized transport theorem carries the old constraint across.

**Failure assumptions.** Realizability and observation soundness are essential.
A nonempty version space is not evidence that either holds. For example, let
`H={m0,m1}`, with both predicting observed probe `p=0` and unobserved repair
consequence `r=0`; let the true world predict `p=0,r=1`. Every available `p`
observation agrees forever, but the shared repair prediction is wrong. Empty
`V(D)` means model/observation/scope inconsistency, not global impossibility.
Downstream universal quantification must not turn an empty version space into
vacuous authorization: return a refutation/`CANNOT_CHECK` terminal.

## 4. FC2 — Least conservative impact set, not least repair algorithm

Fix an initial state, intervention and lifecycle horizon. Each surviving model
predicts an affected-obligation set `A_m subset Q`. Define

\[
U(V)=\bigcup_{m\in V}A_m,\qquad
L(V)=\bigcap_{m\in V}A_m,\qquad V\ne\varnothing.
\]

**Proposition FC2.** Under FC1's assumptions,
`L(V) subset A_m* subset U(V)`. Among arbitrary subsets of the shared obligation
universe `Q`, `U(V)` is the unique least set containing the effects of every
surviving model. Refinement `V' subset V`, with both nonempty, implies
`U(V') subset U(V)` and `L(V) subset L(V')`.

**Proof.** The true model is one member of `V`. Every member's effect set contains
the intersection and is contained in the union. A set `S` contains every `A_m`
iff it contains their union. Set inclusion gives both refinement statements.
QED.

This is a least element in the full powerset lattice, not necessarily in a
restricted family of executable repair plans. It gives neither the cheapest
plan nor a bound on the work needed to find `U`. Rechecking only `U` is not
automatically sufficient: repair may need read boundaries, shared checker
inputs, alternative supports, externally governed authority checks and state
migration. Those obligations must be in the declared observation contract or
in separately verified preconditions of the repair algorithm.

The addendum's affected coupling and actual rechecking footprint remain
distinct. With fixed external weights `w_q>0`, uncertainty yields lower and
upper affected fractions from `L(V)` and `U(V)`; actual touched/rechecked
multisets can be larger and can exceed one normalized full pass. Adding inert
stored atoms is not permitted to enlarge the denominator.

**Countermodels retained.** Anchored pairwise probes miss `xyz`; stable sparse
paths can have global effects; a shared authority can invalidate all warrants
without changing answers. Conversely, shared computation can reduce work when
nearly every output is affected. Low edge density is neither FC2's premise nor
a necessary condition for computational advantage.

## 5. FC3 — Decision sufficiency without structural identification

For each model and registered decision context `d`, let

\[
G_m(d)=\{a\in A:\ a\text{ meets }C,\text{ quality and budget requirements in }m\}.
\]

Include verified applicability, exact action semantics, external authority and
required lifecycle consequences in this predicate. Define a separate set
`G_m^benefit(d)` if the question demands a beneficial repair: an always-safe
abstention must not make an advantage claim vacuous. If any model has an empty
acceptable set, even knowing that model exactly cannot produce a certified
action in the present action language.

A structural target `sigma(m)` might be a particular dependency graph or module
decomposition, modulo an explicitly declared isomorphism/gauge. Structural
identification requires that `sigma` be constant on `V`. Decision-profile
equivalence is the genuine equivalence relation

\[
m\sim_D n\ \Longleftrightarrow\
\forall d,\ G_m(d)=G_n(d).
\]

It can be much coarser than the structural target. For a single context, however,
we need even less than a unique decision profile:

\[
\Gamma(V,d)=\bigcap_{m\in V}G_m(d).
\]

**Proposition FC3a.** A deterministic action can be certified acceptable for
every model in a nonempty `V` iff `Gamma(V,d)` is nonempty. Structural
identification is sufficient only when a structurally identified class itself
has a common acceptable action; it is not generally necessary.

**Proof.** A common action belongs to each acceptable set by definition. If an
action is acceptable for every member, it belongs to their intersection. QED.

For example, two models can disagree about a hidden internal edge yet both
certify the same repair. Further probes to identify that edge need not change
the decision. Conversely, overlapping pairs do not suffice: the three sets
`{a,b}`, `{b,c}`, `{a,c}` have pairwise intersections but no common action.
Compatibility through some shared action is not an equivalence relation and
must not be used as one.

Define full-probe equivalence `m ~P n` iff `o_m(p)=o_n(p)` for every registered
probe. It partitions `H` into observation classes. Define each action's decision
region `R_a={m:a in G_m(d)}`; these regions may overlap.

**Proposition FC3b.** With finite models/probes, noiseless resettable semantics,
finite probe costs and no binding probe budget, a finite decision procedure that
always returns a certified acceptable action exists iff every full-probe
equivalence class `K` satisfies `intersection_{m in K} G_m(d) != empty`.

**Proof.** Necessity: models in `K` produce the same transcript under every
adaptive probe policy, hence reach the same action leaf; that action must work
for all of them. Sufficiency: execute every probe, identify the resulting
observation class, and choose a common certified action for it. This constructs
a finite procedure, without claiming that it is efficient. QED.

This is exactly the decision-region stopping condition `V subset R_a` in the
HEC parent. A lack of sufficient probes is an information obstruction relative
to the model, action and probe languages. A timeout from a particular heuristic
is not that obstruction. Randomization cannot give zero-error non-abstaining
success when a transcript class has no common acceptable action.

## 6. FC4 — Exact paid probe trees and their computational limit

Let `c(p)>0` be the cost of executing a probe. For nonempty `V`, define
`V_p^y={m in V:o_m(p)=y}`. Only probes with at least two nonempty outcome cells
are considered. Define

\[
D(V)=\begin{cases}
0,&\Gamma(V,d)\ne\varnothing,\\
\min_p\left[c(p)+\max_{y:V_p^y\ne\varnothing}D(V_p^y)\right],&\text{otherwise},
\end{cases}
\]

with minimum over an empty probe set equal to infinity.

**Proposition FC4.** `D(V)` is the minimum worst-case environmental probe spend
of a deterministic acceptable-action decision tree under FC3b's assumptions.

**Proof.** A common acceptable action needs no further probes. Otherwise every
successful tree begins with an informative probe: deleting a noninformative
positive-cost probe preserves all possible transcripts and lowers cost. Each
nonempty child has fewer surviving models. Induct on `|V|`: the cost at a root
is its probe cost plus the worst child cost, and choosing a minimizing root and
optimal children attains the displayed recurrence. Singleton infeasible cases
have no informative probe and cost infinity. QED.

This recurrence optimizes **probe spend only**. It does not count the work to
enumerate models, construct acceptable regions, discover effects, compute the
policy, compile it or validate it. Exact policy construction may be exponential.
Those costs must enter lifetime accounting and resource-bounded reach.

If different final repairs/checks have material costs `r(m,a)`, replace the
zero-cost stopping option by
`min_{a in Gamma(V,d)} max_{m in V} r(m,a)` and minimize between stopping and
probing. In that richer problem a robust action need not justify immediate
stopping: a paid probe might enable a much cheaper repair. This extension is a
specification here; finite checks of the probe-only recurrence do not verify
the full action-cost optimization problem.

For a registered physical-probe budget `b`, exact `D(V)>b` certifies that no
tree in this declared class meets that worst-case probe budget. It does not
certify insufficiency of all richer intervention languages, stochastic policies
with error allowances, unavailable evidence channels or representations.

## 7. FC5 — Fixed-rule retention, alternative supports and revocation

Let `E0` be finite original evidence and let `H0` be a fixed finite rule language
with data-independent strict total preference `<`. Define consistency by
conjunction of per-observation constraints, and

\[
\ell(S)=\min_<\{h\in H_0:\operatorname{Consistent}(h,S)\},\quad S\subseteq E_0.
\]

Fix one rule `r` consistent with all `E0`; define exact retention
`P_r(S)=[ell(S)=r]`.

**Proposition FC5a.** `P_r` is monotone: if `S subset T subset E0` and
`P_r(S)=1`, then `P_r(T)=1`.

**Proof.** Rule `r` remains consistent because it is consistent with all `E0`.
Every preferred rule `h<r` was inconsistent with `S`; adding conjunctive
constraints cannot make it consistent with `T`. Thus `r` remains the minimum.
QED.

**Actual-source mapping, narrowly scoped.** In
`../self-evolution-v1/donor_runtime/methods.py`, `GrundyRuleLanguage.induce`
uses fixed shape bounds, scans period then preperiod, minimizes computed
`code_bits`, and zero-fills unforced table entries. This is equivalent to the
fixed rank `(computed code_bits, period, preperiod, lexicographic table)` over
all finite allowed tables: zero filling chooses the first consistent table of
each shape. In `depend.py`, `induce_from_blocks` uses sorted, deduplicated
observation union. Therefore the lemma applies to the full rule induced from
all original evidence, after checking its consistency. The identity is the
exact dataclass `(preperiod, period, values)`, not arbitrary extensional function
equivalence. Both formal and hostile reviewers independently checked this
source mapping.

The lemma does not cover data-dependent language construction, changed ranking,
nonconjunctive scores, an inconsistent target rule, arbitrary new output
identity after revocation, or a different environment. Empirical agreement on
all masks of one sample does not establish these source assumptions generally.

For any monotone Boolean support predicate `P` on finite evidence IDs, let
`Min(P)` be its inclusion-minimal true sets.

**Proposition FC5b.** `P(S)=1` iff some `K in Min(P)` satisfies `K subset S`.

**Proof.** Any true finite set contains a minimal true subset by repeated
deletion. Conversely a superset of a true set remains true by monotonicity.
QED.

This explains complete alternative-support retention under deletion. It does
not make singleton deletion a complete discovery method. For `P(a,b)=a OR b`,
both singleton deletions from `{a,b}` preserve the result, while deleting both
does not. The full support representation is `{{a},{b}}`, not an empty graph.
For threshold support `P(S)=[|S|>=r]`, all size-`r` sets are minimal: explicit
support enumeration requires `binomial(n,r)` records. More compact equivalent
representations may exist; this is not a representation-independent storage
lower bound.

Two live-support states `{a}` and `{b}` both currently warrant a claim. Revoking
`a` distinguishes them. An immediate-answer quotient merging these states loses
required lifecycle behavior even though current truth agrees. Restoration and
authority changes must be registered explicitly; deletion-only checks do not
prove them.

**Proposition FC5c (deletion lifecycle signatures).** Let a state be `(P,S)`,
where `P` is a fixed support predicate and `S` the live subset of a shared finite
evidence universe. Let every registered transition delete one named evidence
item, idempotently, and let the observable be `P(S)`. Two states have identical
observations after every finite deletion word iff their signatures
`(P(S minus D): D subset evidence-universe)` agree componentwise.

**Proof.** A deletion word has precisely the effect of deleting its set of named
items, because deletions commute and are idempotent. Conversely every subset is
realized by some finite deletion word. Thus the signatures enumerate exactly
all observable continuations. QED. Monotonicity is not needed for this signature
fact, although the independent finite instances use monotone support functions.

## 8. FC6 — Representation-relative operator reduction

Let primitive operators be partial transformations `o:X -> X`. Let `~` be a
state equivalence. Assume that whenever `x~y`, (i) every registered `C` observable
agrees, (ii) each operator is enabled in both states or neither, and (iii) when
enabled, `o(x)~o(y)`. Observable external events and authority actions are part
of this signature, rather than silently erased.

**Proposition FC6.** Each operator induces a well-defined transformation on
`X/~`, and every finite operator word preserves the corresponding observable
behavior and applicability under quotienting.

**Proof.** Assumptions (ii)/(iii) make the image of an equivalence class independent
of the chosen representative. Induction on word length preserves equivalence
at every step; assumption (i) preserves observations. QED.

This is a standard congruence/transition-system quotient. An executive policy
must also factor through the quotient, or its hidden distinctions must be
preserved; the proposition does not recover a controller that used discarded
information. Current-answer equality alone fails FC6 in the support example.

A proposed operator reduces to a macro only when a declared compilation
preserves its required applicability, intermediate constitution, lifecycle
observables and external effects. An end-state match after an unauthorized
intermediate action is not a valid reduction. Internal stuttering is allowed
only where `C` permits it. Search for compensating programs after removal is
part of testing irreducibility.

If a simulation costs at most `alpha*c+beta` per simulated step, then a word of
length `L` and source cost `c_total` has translated cost at most
`C_encode + alpha*c_total + beta*L`, before additional custody/maintenance costs.
Mutual simulations require bounds in both directions. Fixed overhead thresholds
need not define a transitive equivalence relation: composed translations compose
their bounds. A richer field can move work into encoding or indexing; those
costs cannot disappear from a minimal-operator claim.

Learning fragments, compiling equations, inducing constraints and selecting
actions therefore need not add primitive operators. Their status depends on
registered executable semantics and compilation cost, not their names. Supplied
sound equations are a prior; discovering their validity is a distinct learning
and verification obligation.

## 9. FC7 — Conditional lifetime payback

For one declared resource coordinate, let the structured policy cost

\[
C_S(H)=D+I+V_0+K+\sum_{t=1}^{H}(R_t+L_t+G_t+M_t+U_t),
\]

where `D` is discovery, `I` indexing, `V0` initial validation, `K` policy/model
construction and compilation, `R` routing, `L` repair, `G` preservation and
boundary checking, `M` maintenance, and `U` drift recovery, false alarms and
failed proposals. Compare the matched parent's full cost `C_P(H)`.

**Proposition FC7.** Under a stationary mean-cost model with parent episode cost
`P`, drift rate `delta`, conditional recovery cost `U`, define

\[
b=P-(R+L+G+M+\delta U),\quad
A=D+I+V_0+K-C_{P,0}.
\]

The structured policy has lower expected cost iff `A < H*b`. If `A>0` and
`b>0`, this is equivalent to `H>A/b`; if `A>0` and `b<=0`, repetition does not
repay the extra setup under that model.

**Proof.** Subtract the two affine mean-cost expressions and rearrange. Other
sign cases use the original inequality. QED.

This elementary accounting identity is not a discovered scaling law. Its
forecast validity depends on stationarity, valid structure and correctly
estimated costs. Realized payback and uncertainty must be measured. Apply the
comparison coordinatewise or within preregistered budgets; do not trade a
preservation violation for speed or invent a favorable weighted score.

## 10. Independently executable finite specifications

These checks test elementary scope claims and implementations, not model
realizability in actual incidents or general learning performance. The independent
checker owns implementation and results. They do not run new optimization
fixtures or protected #143 studies.

| ID | Finite universe | Independent comparison / negative |
|---|---|---|
| FC1 | Three models, two binary probes, all outcome tables and partial evidence assignments | Direct equality filtering versus evidence-set contraction/revocation inclusion; retain nonempty misspecification countermodel |
| FC2 | Three models, three obligations, all impact maps and nonempty version spaces | Enumerate every proposed footprint; universal soundness iff it contains the union |
| FC3/FC4 | Three models, three non-abstaining actions, two binary probes, positive costs 1 or 2 | Version-space DP versus all nonrepeating action-labelled trees; identical optimal cost/feasibility; triangle action-set negative |
| FC5a | Fixed finite ordered rule languages and conjunctive consistency tables | All nested evidence subsets versus the fixed-rule retention monotonicity condition |
| FC5b | All monotone Boolean predicates on 0..3 evidence bits | Truth tables versus independently generated minimal-support antichains; singleton-deletion miss |
| FC5c (an FC6 instance) | Finite deletion lifecycle machines built from support predicates | Partition refinement versus complete deletion-subset observation signatures; current-answer equality is insufficient |
| FC7 (proposed check only) | Declared rational setup/per-episode costs | Direct finite sums versus the affine inequality, including zero/negative denominator cases; not an empirical cost prediction |

The source-specific retention learner is a separate scoped study. It must bind
the FC5a assumptions to actual donor source and record every probed mask. These
generic checks do not certify any omitted state migration, learned routing,
third-generation adaptation, authority transfer or cold runtime restoration.

## 11. Publication disposition and next falsifiers

The formal core reduces to version spaces, sound abstraction, decision-region
determination, decision-tree dynamic programming, support antichains and
transition-system congruences. Rewording them as Machine Epistemics does not
create novelty. Their value here is to eliminate unnecessary graph-identification
requirements, prevent unsafe locality claims, and make research protocols exact.

The prospective residual must separately demonstrate paid acquisition of useful
lifecycle models, fresh prediction of intervention consequences, conservative
revision after support changes, and lower full lifetime costs beyond parents
that can learn the same structures. A true graph gift, an acceptable-action
table gift, a copied library or a theorem-proved optimum used without charging
its construction defeats that interpretation. `PARENT_SUFFICIENT`,
`STRUCTURE_GIFT_REQUIRED`, `NON_IDENTIFIABLE`, `VERIFICATION_COST_DOMINATES` and
`CANNOT_CHECK` remain successful outcomes.
