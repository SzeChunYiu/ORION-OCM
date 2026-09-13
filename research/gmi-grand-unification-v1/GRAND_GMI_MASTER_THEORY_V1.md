# Grand GMI Master Theory V1

Status: **DECLARED CAUSAL-PROCESS SCHEMA; THEOREM-SPECIFIC ASSUMPTIONS AND RECURSIVE AUDIT REQUIRED**
Date: 2026-09-12; corrected synthesis: 2026-09-13

Read first: [scientific CORE](CORE.md). Current correction authority: `RECURSIVE_GAP_AUDIT_20260913.md` and its [successor scientific queue](SCIENTIFIC_GAP_QUEUE_V2.md). A complete list
of named objects, or green finite receipts, does not establish that every
theorem or empirical instance has been verified. Earlier ontology-closure
labels refer to the chosen schema, not an exhaustive absence-of-gaps theorem.

This document is the synthesis of the finite operational theorem and Grand-GMI layers 1–5. It is normative for the current theory package.

---

## 0. Domain axiom

Grand GMI applies to any machine intelligence that is physically realized as a causal process with a declared system boundary, interventions/observations and resource accounting.

It does **not** assume neural networks, programs, Bayesian agents, symbols, classical bits or a particular physical substrate.

The primitive declaration is

\[
\boxed{
\mathfrak G=(\mathbf P,\mathcal B,\mathcal E,\Omega,\Theta,\rho,\mathcal D,\varepsilon)
}
\]

where:

- `P` — physical/process theory: systems, legal transformations and composition;
- `B` — machine/environment boundary and free side information;
- `E` — admitted ecology/environment set, not a probability prior;
- `Omega` — obligation family / admissible outcome relation;
- `Theta` — intervention, continuation and probe family defining operational resolution;
- `rho` — vector of physical/developmental resources;
- `D` — admitted development/update/search processes;
- `epsilon` — declared approximation/error tolerance, with zero allowed.

No architecture syntax occurs in the primitive tuple.

---

## 1. Canonical derived objects

### 1.1 Exact semantic state

Let `Q_h` be the complete protected future response profile of history `h` over all declared environments, interventions, continuations and obligation probes.

Define **exact** semantic equivalence by

\[
h\equiv_0 h' \iff Q_h=Q_{h'}.
\]

Equality is transitive, so the canonical semantic state is the genuine quotient

\[
\boxed{S^*=\mathcal H/\!\equiv_0}.
\]

This quotient classifies preservation of the **complete declared response map**.
Enlarging obligation, ecology, horizon or interventions can only refine it when
the old response coordinates remain unchanged. Finer exact states canonically
map onto coarser exact states. A deterministic encoding reproduces that entire map through a common decoder iff
it determines its quotient class.

Merely satisfying a relational task may require less information. If two histories
allow actions `{a,b}` and `{a,c}`, always choosing `a` solves both although their
full action-success response rows differ. Task-success memory lower bounds must
use incompatible action requirements (SC-1), not assume that every adequate
machine reconstructs all counterfactual response distinctions. Implementing the
quotient as a recurrent state also requires a well-defined update: full
continuation closure supplies congruence; finite-horizon refinement alone does not.
Responses on null/unreachable histories require an explicit rooted-kernel or
almost-sure convention; they cannot be inferred from a trajectory law alone.

### 1.2 Approximate semantic resolution

A tolerance relation of the form `distance <= epsilon` is generally **not transitive** and therefore must not be called a quotient equivalence. For approximate intelligence, choose a declared response pseudometric

\[
d_Q(h,h')=\sup_{\lambda\in\Lambda} d_\lambda(Q_h(\lambda),Q_{h'}(\lambda)),
\]

or another declared operational response metric. Approximate semantic complexity is then represented by metric objects such as covering/packing numbers

\[
N_\varepsilon(S^*,d_Q),\qquad P_\varepsilon(S^*,d_Q),
\]

or by an explicitly declared transitive coarse-graining. There is no automatic quotient by `d_Q<=epsilon`.

This distinction is normative throughout Grand GMI: **exact state is a quotient; approximate state is a metric/coarse-graining problem unless transitivity is separately proved.**

### 1.3 Semantic cut spectrum

For every causal cut `C`, first define the attainable resource set

\[
\boxed{
\mathcal C(C,\varepsilon)=
\{\rho_C(K,d):(K,d)\text{ is jointly legal and achieves }\Omega
\text{ within }\varepsilon\}.
}
\]

Its resource spectrum is `kappa(C,epsilon)=Pareto(C(C,epsilon))`, with the
underlying attainable set retained even if no Pareto point exists. Across
ecologies one common admissible decoder must satisfy the risk constraints;
separately optimized ecology risks are only an oracle lower envelope (SC-2–5).
Channel, decoding, randomization and simulation costs must remain charged in
their registered regions.

For a declared scalar resource, an infimum is a lower-bound value and must not
be promoted to an attained resource without a witness or attainment theorem.
At finite zero-error deterministic classical one-way alphabet scope the attained scalar minimum is
the semantic-conflict-hypergraph chromatic requirement. Noisy, bounded-memory,
retrieval, verifier and side-information laws are scoped specializations.
An interactive transcript changes the encoder's information; recompute the cut
after feedback. A quantum state need not encode a globally readable classical
color. For one-way exact functions its unassisted dimension is governed by the
appropriate orthogonal representation; general relations require quantum
state/measurement feasibility. Neither extension inherits a classical alphabet
bound without a proof of the interface assumptions.

### 1.4 Transformation-complexity spectrum

For every local transformation site or process region `v`, define

\[
\boxed{
\mathcal T(v,\varepsilon)=
\{\rho_{comp}(T):T\text{ legally realizes the local obligation within }\varepsilon\},
\qquad \tau(v,\varepsilon)=\operatorname{Pareto}(\mathcal T(v,\varepsilon)).
}
\]

Again the attainable set is primary. A componentwise infimum of a vector set
can combine mutually incompatible coordinates: attainable costs `(1,3)` and
`(3,1)` have lower envelope `(1,1)`, but neither fits budget `(2,2)`.
Do not replace the frontier or feasibility test by that envelope. A registered
scalar utility gives a separate scalar optimization; scalarized optima need not
exhaust a nonconvex Pareto frontier.

`kappa` and `tau` remain irreducible as a pair: equal final semantic width can
coexist with arbitrarily different local computation/query complexity.

### 1.5 Symmetry object

Let

\[
G_{\mathfrak G}=\operatorname{Aut}(\mathbf P,\mathcal E,\Omega,\Theta,\rho)
\]

be the transformations that preserve the declared problem. `G` acts on the
exact quotient `S*`. Under GG20's G-stable finite averaging hypotheses, or its
compact barycentric-closure and coordinate-regularity hypotheses, every
attainable randomized point has an equivariant feasible representative with no
worse resources. A frontier representative requires an existing frontier point
or separate attainment. A unique deterministic optimum is equivariant when the
feasible class and selection rule are G-invariant.

### 1.6 Developmental reachability

Development is itself a GMI process on morphology state. Let

\[
\operatorname{Reach}_{\mathcal D}(B)
\]

be the registered realization states reachable under the declared development process and budget. A quotient representation may be used when the registered projection preserves the protected profiles and future development semantics; membership of a realization then means membership of its projected class. Learning, meta-learning, architecture search, program synthesis, test-time adaptation, self-modification and evolutionary population updates are repeated applications of this lift.

`D` is an irreducible component of the primitive tuple, not a derived object.
Two development laws sharing every other registered input can have different
reachable frontiers, so no derivation from semantic, cut, transformation,
symmetry, resource or realization facts determines a trained outcome. A
registered `D` must also fix its schedule semantics, because admitted updates
need not commute. Reachability never lowers a derived lower bound but can
invalidate a construction, and no finite budget certifies an
unbounded-development verdict.

### 1.7 Causal semantic information

A physical distinction has semantic information only insofar as interventions on it can change an obligation-relevant attainable profile. At deterministic classical one-way zero-error finite cut scope, a scalar specialization is conflict reduction

\[
I^0_\Omega(C)=\log\chi(H_0)-\log\chi(H_C).
\]

Garbling cannot increase it. A declared viability/constitution predicate induces an endogenous obligation, but bare physical dynamics do not select arbitrary values.

---

## 2. Grand morphology law

For physical regime/substrate parameters `theta`, let `Phys_P(theta)` be the physically legal realizations. Define the global attainable set

\[
\mathcal A_{\mathfrak G,\theta}
=
\{(Q(M),\rho(M)):M\in Phys_{\mathbf P}(\theta),\ M\models\mathcal B\}.
\]

Use the declared obligation order on response/risk coordinates and the declared
resource order; raw probabilities are not automatically all maximized. The
physical intelligence morphology frontier is

\[
\boxed{
\mathcal F_{\mathfrak G,\theta}
=
\operatorname{Pareto}(\mathcal A_{\mathfrak G,\theta}).
}
\]

The developmental/reachable frontier is separately

\[
\boxed{
\mathcal F^{reach}_{\mathfrak G,\theta,B}
=
\operatorname{Pareto}
\{(Q(M),\rho(M)):M\in Phys_{\mathbf P}(\theta)\cap Reach_{\mathcal D}(B),\ M\models\mathcal B\}.
\]

This distinction is mandatory: global optimum and reachable optimum are different objects.

Intersect the **attainable set** with reachability before taking Pareto. The
intersection of the global frontier with the reachable set only answers whether
a globally optimal point is accessible. It can be empty while a constrained
reachable optimum exists. If life-cycle costs are protected, profiles belong to
endpoint/path pairs and retain those costs (DRS-1–3).

---

## 3. Grand GMI factorization theorem

> **GG33 — Operational analysis and conditional factorization.** Every admitted
> machine has its own declared response map, which factors through equality of
> that map's complete response profiles. Its physical realization can be
> analysed by causal cuts, local transformations, resources and development.
> When it is required to preserve the problem's entire protected response map,
> its adequate deterministic encoding must determine `S*`. For a relational-success
> obligation, use SC-1 compatibility and the actual common-policy risk set
> instead; task adequacy alone does not imply recovery of the richer `S*`.

Proof of the response-map factorization is the quotient construction: equal
classes have equal profiles, making the induced map well-defined. Necessity
for full-map preservation follows because equal internal representations
must produce the same protected profile. The overlapping-action example in
section 1.1 disproves the stronger task-success necessity. Dynamic quotient
realization requires the stated congruence/closure hypotheses, and no sufficiency
of separately satisfied cut/resource bounds is inferred without a joint construction.

For distributed systems, agent boundaries become internal cuts. For learned systems, training/deployment is a temporal cut and development is a lifted process. For substrate changes, response-preserving implementation maps preserve semantic coordinates while transforming resource coordinates. Symmetries act on the exact quotient and can constrain frontier representatives.

Thus neural, symbolic, retrieval, recurrent, modular, multi-agent, evolutionary, analog and quantum-capable process descriptions are not separate definitions of intelligence. They are candidate realizations/factorizations of the same obligation-relative process requirements.

---

## 4. Necessity–realization closure theorem

Let `X_nec(theta)` be the set of morphology/resource profiles not ruled out by all proved semantic-cut, transformation, symmetry, physical and developmental necessities. Let `X_con(theta)` be profiles realized by explicit constructions. Physical truth satisfies

\[
X_{con}(\theta)\subseteq X_{phys}(\theta)\subseteq X_{nec}(\theta).
\]

> **GG34 — Sufficient necessity–construction closure certificate.** Use one
> declared product order (write retained risks/resources as quantities to
> minimize). Suppose `X_con subseteq X_phys subseteq X_nec`, and every
> `n in X_nec` is weakly dominated by some `c in X_con`. Then their Pareto
> subsets are equal. If a frontier profile's physical fiber lies in one
> declared operational morphology class, that profile identifies the class
> at that resolution.

Proof: for a Pareto point of either outer set, a weakly dominating constructive
point must have exactly the same profile, or the former point was not Pareto.
Conversely, if a constructive Pareto point were strictly dominated in either
outer set, the assumed constructive dominator of that better point would also
strictly dominate it, a contradiction. The same argument applies to the physical
set between them. QED.

A finite nonempty constructive register with proved coverage additionally supplies
attainment; see [MSC-2](CONSTRUCTIVE_SELECTION_ATTAINMENT_BRIDGE_V1.md).
Architecture-property selection requires a nonempty selected set and the full
physical profile fibers, not a single constructive representative (MSC-1).

This is a **sufficient** certificate, not a necessity claim about every infinite
set. Equality of Pareto sets alone need not mean every feasible point is dominated
by a Pareto point. Nonempty attainable sets can have empty Pareto subsets, so this
certificate does not establish an optimizer's existence. Feasibility, attainment,
joint realization and the fiber statement must each be discharged; merely naming
outer/inner sets or matching coordinatewise lower bounds does not discharge them.

---

## 5. Composition laws

Under exact factorization of ecology, obligation, feasible process class and separately retained resource coordinates,

\[
\mathcal A_{12}=\mathcal A_1\times\mathcal A_2,
\qquad
\operatorname{Pareto}(\mathcal A_{12})
=
\operatorname{Pareto}(\mathcal A_1)\times\operatorname{Pareto}(\mathcal A_2).
\]

Independent exact semantic widths multiply in alphabet size and add in log-width. Coupled obligations need not factor. Therefore modularity is derived from problem factorization, not assumed from implementation style.

---

## 6. Substrate law

If `F:P->P'` preserves the protected response profile,

\[
\mathcal R_{P'}(F(M))=\mathcal R_P(M),
\]

then all response-defined semantic/capability statements commute with `F`. Resource coordinates need not:

\[
\rho_{P'}(F(M))\ne \rho_P(M).
\]

Hence semantics are substrate-invariant under operational implementation, while physical morphology selection is substrate-dependent.

Classical deterministic/stochastic, analog, biological and quantum process theories can instantiate the same Grand-GMI semantics when their process/intervention structure is declared. The theorem does not assert cross-substrate computational equivalence. Preserving task outputs does not preserve the minimum classical message alphabet: a quantum encoding with decoder side information can solve the same task in smaller dimension. The GG37/GG44 capacity bound applies to a genuinely globally decodable identity message under its stated resource contract.

---

## 7. Global definability versus computability

For an explicitly finite effectively enumerable registered realization domain,
attainable set, frontier, operational fibers and bounded developmental reachability
are computable exactly under the stated decidability assumptions. Finite response
alphabets alone do not bound invisible-work costs or the number of implementations.
Exact predicates
and resource comparisons must be decidable; merely computable real coordinates
do not supply a total equality/order test. Zero-cost cycles require finite-state
or state/cost-label reachability, not an assumption that a bounded-cost tree
contains finitely many histories.

For continuous/infinite process spaces, the same exact response quotient and morphology objects remain set-theoretically defined when the response kernels are well-typed. Approximate analysis uses the declared response metric and covering/packing/optimization objects. Existence, attainment and computability require regularity such as measurable kernels, compactness, lower semicontinuity or effective descriptions as appropriate.

For unrestricted Turing-complete machine spaces, no total exact solver can exist; the separate uncomputability theorem reduces the halting problem to exact GMI capability/reachability.

Therefore:

\[
\boxed{\text{global theory definition} \not\Rightarrow \text{total algorithmic solution of every instance}.}
\]

This is a boundary of mathematics, not a missing architecture theorem.

---

## 8. Physics-level completeness criterion

Grand GMI V1 used **globally closed** for a schema-coverage convention with the
following intended categories:

1. every admitted machine intelligence is typed as a causal physical process under the primitive declaration;
2. exact semantic identity is fixed by the canonical response quotient, while approximate resolution is separately metrized/coarse-grained;
3. information/memory/communication requirements are typed by semantic cuts;
4. computation is represented independently by transformation complexity;
5. physical resources and substrate constraints determine feasible morphology frontiers;
6. learning/evolution/search are recursive lifted GMI processes rather than extra primitives;
7. multi-agent/modular systems are process compositions with internal cuts;
8. semantic meaning is causal obligation relevance, with viability providing a conditional endogenous obligation class;
9. symmetry and invariance derive admissible equivariant morphology classes under explicit conditions;
10. exact closure is defined by necessity–construction contact, while undecidability/nonattainment boundaries are stated rather than hidden.

The schema provides a common language for those registered sectors. It does not
prove that all reductions are valid without their hypotheses, that no omitted
sector or counterexample exists, or that every sharp law is known. The recursive
audit explicitly reopened false implications inside previously green sectors.
Each repaired theorem now carries its own assumptions, proof, counterexample,
finite witness and evidence boundary. Sharper laws and prospective validation
remain scientific obligations; a label cannot discharge them.

---

## 9. Master law

The declared theory framework can be written as the chain

\[
\boxed{
(\mathbf P,\mathcal B,\mathcal E,\Omega,\Theta,\rho,\mathcal D)
\Longrightarrow
(S^*,d_Q)
\Longrightarrow
(\kappa,\tau,G, I_\Omega)
\Longrightarrow
(X_{nec},X_{con},Reach_{\mathcal D})
\Longrightarrow
(\mathcal F,\mathcal F^{reach},\text{morphology fibers}).
}
\]

Here `S*` is exact; `d_Q` carries approximate response geometry.

In words:

> Physical law determines possible processes. Ecology and obligation determine which distinctions and transformations matter. Causal placement determines which semantic information must cross each cut and which transformations must occur locally. Resource laws determine which physical realizations can implement those requirements. Development determines which realizations can actually be reached. Intelligence morphology is the resulting resource-conditioned frontier, not a privileged architecture name.

The final arrow has a one-sided derivation rather than only a schema. Given
the proved necessities of the preceding arrows, a structural family predicate,
a resource accounting map that undercharges and a monotone scalar functional,
the relaxed accounting program of `MORPHOLOGY_PHASE_LAW_DERIVATION_V1.md`
computes a family-conditioned lower bound that binds every admitted machine in
that structure class, including machines nobody has constructed. Upper bounds
are not derivable this way, so the chain explains robust family **exclusion**;
selection requires independently justified existence of a selected realization;
an executable selection also needs an admitted construction. Any verdict remains
relative to the registered structure classes and their uncovered residue.

This is the current Grand GMI V1 master statement.
