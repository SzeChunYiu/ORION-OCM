# GMI #833 foundation v1 — scientific constitution and mathematical core

Status: **FORMAL FOUNDATION / GOVERNANCE CONTRACT — NOT CORPUS OR EMPIRICAL CLOSURE**  
Parent issue: #833. Child: #837.

## 1. Flagship question and bounded claims

**Flagship scientific question.**

> Under explicitly disclosed representation, search, ecology, evaluation, and resource assumptions, can implementation-independent behavioral specifications predict which computational mechanisms are necessary, reachable, and selected, and can those predictions prospectively recover known and previously unregistered machine-intelligence forms with falsifiable capability/resource laws?

**Weakest defensible current GMI core claim.** GMI is presently defensible as a formal/evaluation framework that separates behavioral specification, exact response equivalence, admissibility, developmental reachability, resource/Pareto selection, and evidence maturity. Existing bounded results can instantiate those distinctions; they do not establish a universal architecture law.

**Strongest eventual claim.** A mature GMI theory would prospectively derive property-level mechanism requirements from architecture-uncommitted specifications/ecologies, recover the predicted mechanism classes under P3/P4 search, predict held-out transitions and failure regions, survive independent implementation/replication, and retain calibrated validity at real scale.

`checklist complete`, `formalized`, `expressible`, `recoverable`, `predicted`, `replicated`, and `real-scale validated` are distinct predicates. Ontological completeness is never inferred from checklist closure.

## 2. Evidence and maturity

Evidence level is orthogonal to scientific maturity.

| level | meaning | cannot by itself license |
|---|---|---|
| EV0 | definition/protocol/registration | theorem truth, empirical effect |
| EV1 | deductive theorem with explicit premises and falsifiers | reachability, selection, empirical validity |
| EV2 | exact/computer-assisted certificate at a bounded declared universe | universal extrapolation, held-out prediction |
| EV3 | prospectively frozen held-out experiment | independent replication, external validity |
| EV4 | disjoint and/or independent implementation replication | universal real-scale law |
| EV5 | real-scale prospective validation with calibrated uncertainty | ontological completeness or unrestricted universality |

Maturity ladder:

`M0 concept -> M1 theorem -> M2 exact witness -> M3 architecture-prior-free relative recovery -> M4 frozen held-out prediction -> M5 independent replication -> M6 real-scale prospective validation`.

Forbidden extrapolation is monotone: a result may claim only what its premises, proof mode, evidence level and maturity jointly support. No maturity level, including M6, implies ontological completeness.

## 3. Behavioral specification

Let `I` be a registered instance/context set and `Tr(i)` the legal externally observable trace set for `i`. A **behavioral specification** is

\[
\mathcal B=(I,\operatorname{Acc}),\qquad
\operatorname{Acc}(i)\subseteq Tr(i),\ \operatorname{Acc}(i)\ne\varnothing.
\]

`Acc(i)` contains exactly the traces accepted at the declared scientific scope. It says *what behavior is acceptable*, not how an implementation realizes it. Probabilistic confidence, utility and resource criteria are separate registered predicates rather than silently folded into implementation structure.

For a machine/environment realization `M`, let `Supp(M,i)` be the support of its protected trace distribution on instance `i`. Exact strong satisfaction is

\[
M\models\mathcal B
\iff
\forall i\in I:\ Supp(M,i)\subseteq\operatorname{Acc}(i).
\]

Other statistical notions of satisfaction must be named separately.

### BS-1 — conservative legacy-obligation map

Existing GMI work uses a registered obligation object `Omega` (historically written with fields such as `(E,D,J,V,C,H,R)`) plus a legal trace universe and an acceptance/verification semantics. Define

\[
\Phi(\Omega)=\mathcal B_\Omega,
\qquad
\operatorname{Acc}_\Omega(i)
=\{\tau\in Tr_\Omega(i):\operatorname{Accept}_\Omega(i,\tau)\}.
\]

**Theorem BS-1.** If the legacy and paper-facing objects use the same registered instances, legal trace universe and acceptance predicate, then for every implementation `M`,

\[
M\text{ satisfies }\Omega
\iff
M\models\Phi(\Omega).
\]

**Proof.** Both sides quantify over the same instances/traces and apply the same predicate; `Phi` merely extensionalizes the accepted traces. Therefore no accepted/rejected trace changes. QED.

This proves a terminology migration, not that every historical use of the word `obligation` already obeyed the same semantics. Corpus-wide migration remains open.

### BS-2 — specification equivalence and protected behavioral equivalence

Two behavioral specifications `B1=(I,Acc1)` and `B2=(I,Acc2)` on the same registered instance and legal-trace universe are **specification-equivalent** exactly when

\[
\forall i\in I:\quad Acc_1(i)=Acc_2(i).
\]

Two realizations `M1,M2` are **protected-behaviorally equivalent** for a registered observation map when, for every registered instance/context, they induce the same protected trace distribution (or the same exact protected trace in deterministic scope). This is stronger than merely both satisfying a relational specification: two machines may choose different accepted traces and still both satisfy `B`.

This distinction prevents the known false inference that equality of full counterfactual response profiles is always necessary for weaker task success. The exact quotient below is therefore a quotient for **full protected-response preservation**, unless a separate task-success equivalence has been formally defined.

## 4. Architecture-neutral machine/process objects

A minimal realization contract is

\[
\mathfrak M=(X,x_0,Q,U,\Chi,\rho),
\]

where:

- `X` is an internal state carrier;
- `x0` is initial state (or an initialization kernel);
- `Q` is an execution/proposal kernel from registered state/context to externally visible action/output proposals;
- `U` is a state/update kernel;
- `Chi` is the declared communication/tool-channel contract;
- `rho` maps lifecycle events to a complete resource vector.

Observation alphabets, action/output alphabets, environment transitions and verification are registered by the behavioral specification/ecology and external verifier contracts rather than hidden as architecture names.

A developmental history is the finite sequence of registered interactions, verifier outcomes and resource increments. A developmental law `Delta` maps current realization plus history to allowed successor realizations. Under budget vector `B`,

\[
Reach_\Delta(M_0,B)
=\{M:\exists\text{ an allowed finite path }M_0\leadsto M
\text{ whose cumulative resource vector is }\preceq B\}.
\]

Thus *expressible/admissible* and *reachable under a developmental law* are different predicates by definition.

## 5. Exact protected-response equivalence and quotient

For finite registered histories `H`, legal continuations `C` and protected response map `R:H x C -> Y`, define

\[
h\sim_R h'
\iff
\forall c\in C,\ R(h,c)=R(h',c).
\]

This is an equivalence relation. The quotient `H/~R` is the exact protected-response quotient.

### Q-1 — factorization/minimality at the exact response scope

Let `e:H->Z` be any encoding from which all protected responses can be decoded exactly. Then

\[
e(h)=e(h')\Rightarrow h\sim_R h'.
\]

Hence the partition induced by `e` refines `~R`; equivalently the quotient map factors through every exact response-preserving encoding. Therefore `|Z| >= |H/~R|` for reachable encoded states, and equality makes the encoding isomorphic to the quotient up to relabeling.

This is parent mathematics (Myhill–Nerode/minimal sufficient state/bisimulation/predictive-state territory). It is also deliberately scoped to **full protected-response preservation**. PR #516 already corrected the false converse that this quotient is always the minimum memory for weaker relational task success when acceptable action sets overlap. The parent-theory subsumption audit required by #833 remains a separate child.

## 6. Architecture-prior-free derivation is relative, not absolute

A derivation experiment discloses at least:

\[
D=(G,Enc,C,S,E,Eval),
\]

for grammar/hypothesis space `G`, encoding `Enc`, cost/resource model `C`, search strategy/tie rules `S`, ecology/task generator `E`, and evaluation rule `Eval`.

It additionally discloses six prior categories:

1. **architectural prior** — named family or family identity supplied before recovery;
2. **representation prior** — privileged state/parameter/factorization representation;
3. **operator prior** — privileged primitive or macro;
4. **search prior** — proposal order, optimizer, tie rule, initialization, search budget/allocation;
5. **ecological prior** — problem/task/environment distribution or hand-picked operating regime;
6. **evaluation prior** — metric, verifier, scoring/aggregation and stopping rule.

The #833 levels are operationalized as:

- **P0:** named architecture supplied;
- **P1:** architecture-specific property vector supplied;
- **P2:** representation/operator family supplied;
- **P3:** only declared generic computational/interaction primitives are supplied; family identity is mapped only after search;
- **P4:** P3 plus recursive creation/compression/reuse of new primitives under the same disclosed governance.

A result is **architecture-prior-free relative to its disclosed prior set** only at P3/P4 and only when target-family naming/property/operator information is absent from predictor/search-visible inputs and family mapping is post hoc. This wording explicitly does **not** mean representation-, search-, ecology-, evaluation- or inductive-bias-free.

**Derivation-language policy.** P0–P2 may use `derive` only with the supplied prior made explicit (for example, “derive a threshold conditional on the supplied operator family”). They may not use unqualified `architecture-prior-free derivation`, `neutral recovery`, or `discovery` language. P3 may support `architecture-prior-free relative derivation/recovery` when the theorem plus search actually obtains the claimed property from generic primitives; P4 may additionally support claims about recursively invented primitives. `Discover` and `predict` remain separately gated by target non-encoding and pre-outcome temporal separation.

For flagship **known-form** claims, P3 is the default minimum for unqualified architecture-prior-free wording unless an explicit exception explains why a stronger supplied prior is scientifically necessary. Claims about **unseen/new forms** require P3 or P4 and retain the post-hoc family-mapping rule. These are wording/admission rules, not evidence that any existing family has already met them.

### PF-1 — no equal-mass uniform prior on a countably infinite hypothesis set

Let countably infinite `H={h1,h2,...}` assign equal probability `c` to each hypothesis. If `c=0`, total mass is 0. If `c>0`, choose `n>1/c`; the first `n` hypotheses already have mass `nc>1`. Therefore no countably additive equal-mass uniform distribution exists. QED.

### PF-2 — no deterministic unique choice under complete renaming symmetry

Let finite `H` have at least two hypotheses and suppose evidence/scoring is invariant under every permutation of `H`. Assume a deterministic selector `A` is also renaming-equivariant and uniquely returns `h*`. Choose a permutation `sigma` swapping `h*` with another hypothesis while leaving the symmetric evidence unchanged. Equivariance gives

\[
A(e)=A(\sigma e)=\sigma A(e)=\sigma h^*\ne h^*,
\]

contradicting `A(e)=h*`. Thus a unique deterministic choice must break the symmetry through a representation, order, tie rule, extra evidence, or abstention. QED.

For a finite symmetric set, randomized invariance can use the uniform distribution, but the chosen hypothesis set/equivalence/encoding remains a prior. For a countably infinite set PF-1 removes even the equal-mass escape. Wolpert–Macready further shows that algorithmic advantage requires restrictions/structure in the problem distribution. Consequently **literal assumption-/prior-free derivation is ill-posed**; scientifically meaningful claims must be relative to disclosed priors.

## 7. Resource vectors and scalarization

This tranche inherits the 14-coordinate lifecycle accounting contract from merged PR #805 (`research/gmi-resource-lifecycle-ledger-v1/`) and independently rechecks its order theorem on a finite hostile grid.

For minimization vectors `a,b in R^d_{>=0}`, write `a <_P b` when `a_i<=b_i` for all `i` and strict inequality holds for at least one coordinate.

### R-1 — positive scalarization preserves strict Pareto dominance

For any strictly positive weight vector `w>0`,

\[
a<_P b\Rightarrow w\cdot a<w\cdot b.
\]

**Proof.** Every term `w_i(a_i-b_i)<=0`, and at least one is strictly negative. Their sum is strictly negative. QED.

### R-2 — incomparable vectors admit opposite positive scalarizations

If `a,b` are Pareto-incomparable, there exist coordinates `i,j` with `a_i<b_i` and `a_j>b_j`. Give coordinate `i` a sufficiently large positive weight while keeping all other weights positive; then `w dot a < w dot b`. Giving `j` sufficiently large positive weight reverses the order. QED.

Therefore a post-outcome scalar score selects a scientific conclusion. Complete raw vectors are primary; absent a prospectively frozen price vector, report Pareto sets/frontiers. The executable certificate exhausts all 27 vectors in `{0,1,2}^3`, all 351 unordered pairs, all 189 dominance pairs and all 162 incomparable pairs; it constructs both positive-weight orderings for every incomparable pair.

## 8. OPEN_GAP and closure semantics

Every registered gap record contains claim id, premise, inference, unresolved assumption, possible counterexample, severity, owner role, parent result, evidence required, materiality, status and descendant gaps.

Materiality is not discretionary:

- **CRITICAL:** can reverse the claim, invalidate a quantifier, falsify a core premise, or reveal circularity/data leakage;
- **HIGH:** can change the claim/evidence/maturity level or strongest-parent disposition;
- **MEDIUM:** changes a registered estimate/bound materially without reversing the scoped claim;
- **LOW:** editorial/ergonomic and cannot alter scoped scientific truth.

Scientific closure states are ordered evidence labels, not deletion states:

`OPEN -> LOCALLY_CLOSED -> HOSTILE_CLOSED -> REPLICATED_CLOSED -> REAL_SCALE_CLOSED`.

A parent result cannot be promoted beyond any unresolved **critical** descendant. Closing one gap must create records for any new assumptions introduced by the repair. This tranche defines the object and rules; corpus-wide retrofitting remains open.

## 9. Universal versus finite notation

A theorem must carry an explicit domain tag. This tranche uses:

- `forall[D]` for a universal statement over a declared mathematical domain `D` with deductive proof;
- `forall_fin[U]` for complete enumeration of a finite registered universe `U`;
- `heldout[F]` for a prospectively frozen held-out family;
- `sample[P,n]` for a sampled statement with declared population/distribution and sample size.

No `forall_fin`, held-out, or sampled statement may be rewritten as unrestricted `forall` without a separate theorem.

## 10. Strongest parents and novelty boundary

Parent-owned mathematics/terminology receives first refusal:

- formal specification and verification: specification describes intended behavior; verification establishes conformance;
- Rice (1976), *The Algorithm Selection Problem*, DOI `10.1016/S0065-2458(08)60520-3`;
- Wolpert & Macready (1997), *No Free Lunch Theorems for Optimization*, DOI `10.1109/4235.585893`;
- Gulwani, Polozov & Singh (2017), *Program Synthesis*, DOI `10.1561/2500000010`, plus syntax-/grammar-guided synthesis literature in which the search language constrains the program space;
- standard multiobjective/Pareto optimization and weighted-sum scalarization;
- Myhill–Nerode, state minimization, sufficient-state, predictive-state and bisimulation families;
- merged ORION-OCM PRs #396/#516 for the exact protected-response quotient boundary and #805 for lifecycle resource accounting.

Leike & Hutter (2015), *Bad Universal Priors and Notions of Optimality* (PMLR 40), is a useful warning that even “universal” agent constructions can materially depend on representation/universal-machine choice.

The #833 residual is not any of those parent theorems. It is the disciplined integration and prospective test of whether implementation-independent specifications plus disclosed priors/resources can predict and recover mechanism classes across ecologies.

## 11. Claim ceiling and open descendants

Earned only if the code/tests/CI and issue reconciliation are green:

`GMI_833_FOUNDATION_V1_FORMALIZED_AT_DECLARED_SCOPE`.

Not earned here:

`ALL_EXISTING_RESULTS_AUDITED`, `CORPUS_TERMINOLOGY_MIGRATED`, `MYHILL_NERODE_BISIMULATION_PSR_SUBSUMPTION_COMPLETE`, `G0_UNIVERSAL_GRAMMAR_VALIDATED`, `P3_KNOWN_FAMILY_RECOVERY_COMPLETE`, `UNSEEN_FORM_DISCOVERY`, `INDEPENDENT_REPLICATION`, `REAL_SCALE_VALIDATION`, `COMPLETE_GMI`, `ONTOLOGICAL_COMPLETENESS`.
