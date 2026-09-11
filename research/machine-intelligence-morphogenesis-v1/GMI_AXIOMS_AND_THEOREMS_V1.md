# GMI Axioms and Theorems v1

Status: **formal working core**. Every row is classified as `ADOPTED_PARENT`, `DERIVED_FROM_DEFINITIONS`, `FINITE_EXACT`, `PROBABILISTIC_PARENT`, `EMPIRICAL_CONJECTURE`, or `IMPOSSIBILITY_LIMIT`.

---

# Axioms / constitutive assumptions

## A0 — obligation and protocol relativity

Every intelligence claim is made relative to

\[
\mathcal O=(\mathfrak E,\mathcal A,\mathcal Y,V,C,\rho,H,D,J).
\]

`D` fixes initialization/development/tool/human/reset/morphology-change permissions and `J` fixes the future intervention/probe class relevant to distinguishability.

No architecture-independent success claim is made without specifying outcomes, legal information/actions/updates, verification, starting capital and metered resources.

## A1 — external verification separation

`V,C` are external to the machine's internal proposal/training objective. Internal loss/reward/posterior/heuristic is not automatically admissible evidence.

## A2 — semantic future-consequence equivalence

A developmental situation is

\[
d=(\chi,h,\xi)
\]

with current machine configuration, registered history and relevant public/experimental context.

Let `Omega_sem` be the registered future **semantic** trace space. It includes future externally protected cognitive/evidence/developmental observables, but not raw private implementation changes or raw resource receipts by default.

Define

\[
d\sim^{sem}_{\mathcal O,D,J}d'
\iff
\forall j\in J:\
P(\Omega^{sem}_{\mathcal O}\mid d,j,D)
=
P(\Omega^{sem}_{\mathcal O}\mid d',j,D).
\]

The equivalence class is the semantic developmental sufficient state.

History alone is not assumed sufficient: identical external histories can leave different optimizer, memory, posterior, replay or morphology states.

## A3 — realization multiplicity

The same semantic developmental state/process may have multiple computational realizations. A morphology is a realization/factorization with its own resource labels, not the abstract state itself.

## A4 — semantic/resource separation

Resource spent by an implementation is attached to realization transitions/frontiers, not automatically used to define semantic-state identity.

If current resource availability changes future legal actions, that availability belongs in the current situation/context.

A stronger resource-sensitive equivalence may be defined for morphology/compiler comparison.

## A5 — resource explicitness

Resources are represented as a raw vector. Scalar cost/utility exists only after a prospectively declared price/utility mapping.

## A6 — temporal separation

Execution/cognition, within-form development and morphogenesis are distinct processes even when a concrete implementation fuses them dynamically.

## A7 — inherited development

A change counts as developmental only when information/state produced by earlier registered experience persists causally into future cognition or future update/morphogenesis.

## A8 — no universal superiority without ecology restriction

Deployed-system superiority is always relative to ecology/resource/verifier/development semantics. A global total order is not assumed.

---

# Theorem / proposition programme

## GMI-T01 — finite semantic developmental minimization

**Class:** `ADOPTED_PARENT + FINITE_EXACT`

For a finite deterministic developmental transducer and finite event/intervention alphabet, quotienting complete machine situations by equality of all future registered semantic traces produces a unique minimal deterministic machine up to isomorphism.

**Parent:** Myhill-Nerode / deterministic transducer minimization.

**Track-B witness:** current-query quotient merges states that the developmental quotient separates after teaching.

---

## GMI-T02 — no representation-independent implementation atom

**Class:** `IMPOSSIBILITY_LIMIT at the stated level`

If unit boundaries are defined only by computational behavior, a unit can generally be refactored into smaller composed units, while finite collections can be flattened into one global transition machine.

Therefore computation alone does not identify one unique irreducible implementation atom.

An irreducible implementation unit requires extra assumptions such as locality, causal intervention boundaries, physical cost, communication constraints or a declared primitive grammar.

---

## GMI-T03 — factorization can exponentially compress developmental state

**Class:** `FINITE_EXACT + ADOPTED_PARENT`

There exist families with minimal global developmental state count exponential in `n` while a factored realization uses `O(n)` local state plus a fixed shared rule and local updates.

Track-B construction:

\[
|Z_{min}|=3^n,
\qquad
|T_{flat}|=2n3^n.
\]

The factorized realization uses `n` local cells + one six-entry local rule.

**Parent:** factored MDP / DBN / structured-program representation theory.

---

## GMI-T04 — lifecycle phase boundary

**Class:** `DERIVED_FROM_DEFINITIONS`

For two fixed deployed systems with scalarized build costs `A_i,A_j`, expected stationary per-use burdens `c_i(E),c_j(E)`, and reuse horizon `H`:

\[
C_i=A_i+Hc_i(E),\quad C_j=A_j+Hc_j(E).
\]

Then

\[
i\prec j
\iff
A_i-A_j+H[c_i(E)-c_j(E)]<0.
\]

If `c_i != c_j`, equality occurs at

\[
H^*=\frac{A_j-A_i}{c_i-c_j}.
\]

**Parent ownership:** amortization/materialization/algorithm-selection/resource economics.

---

## GMI-T05 — information-bias phase identity in idealized proposal search

**Class:** `ADOPTED_PARENT / DERIVED`

Under a registered ideal prefix/proposal model with target ecology `P` and proposal distribution `Q_M`, expected code/search burden is

\[
H(P)+D_{KL}(P\Vert Q_M).
\]

Adding build cost and horizon gives

\[
C_M=B_M+N[H(P)+D_{KL}(P\Vert Q_M)].
\]

This is a source-coding/MDL/Bayes/bounded-rationality parent specialization, not a universal GMI law.

---

## GMI-T06 — progress-potential to hitting-time reduction

**Class:** `ADOPTED_PARENT`

Given a valid progress potential and drift conditions, expected time/cost to a target can be bounded/derived by drift or stochastic-shortest-path theory.

The hard cross-paradigm question is deriving a useful pre-outcome potential/geometry from machine/ecology structure, not the hitting-time theorem itself.

---

## GMI-T07 — K1 cognition-capital criterion

**Class:** `DEFINITION + EMPIRICAL_CAUSAL_CRITERION`

For fresh target `tau` with verified solution `m*` absent from relevant developmental history, inherited state creates K1 when it causally changes future cognition generation before target success and reduces complete verified burden against matched controls.

A pre-solution mediator may be

\[
rank_H(m^*)<rank_{RESET}(m^*).
\]

**Current OCM evidence:** #323 supports this at authored program-search scope.

---

## GMI-T08 — K2 developmental-capital criterion

**Class:** `DEFINITION + EMPIRICAL_CAUSAL_CRITERION`

K2 requires cheaper acquisition of **new K1**, not merely cheaper future task solving:

\[
E[B^{acq}_H(K1_{new})]
<
E[B^{acq}_{RESET}(K1_{new})].
\]

**Current OCM status:** NOT_ESTABLISHED at the #323 grammar for retained-capital recombination; registered bar met on 2/9 fresh seeds.

---

## GMI-T09 — conditional meta-generalization

**Class:** `PROBABILISTIC_PARENT`

Under explicit related-task/meta-environment assumptions, prior tasks can improve expected future-task performance/sample complexity/regret through learned representations, priors or learning algorithms.

**Parents:** Baxter; Pentina-Lampert; Maurer-Pontil-Romera-Paredes; Alquier-Mai-Pontil; PACOH; later PAC-Bayesian learner-of-learning-algorithm results.

**Boundary:** no unconditional arbitrary-domain learning-to-learn theorem follows.

---

## GMI-T10 — ecology/resource-conditioned morphology

**Class:** `ADOPTED_PARENT + EMPIRICAL/FINITE_SPECIALIZATIONS`

Task dependency structure and resource pressures can change which factorization/architecture is selected and alter future evolvability.

**Parents:** factored models; modularly varying goals; facilitated variation; connection-cost modularity/hierarchy; bounded-rational organization.

Broad `ecology -> architecture` is parent-owned; a new GMI law requires cross-paradigm prospective quantitative prediction beyond family-native theories.

---

## GMI-T11 — no universal exact developmental-burden predictor

**Class:** `IMPOSSIBILITY_LIMIT`

For unrestricted Turing-complete morphology classes, an exact computable predictor deciding arbitrary finite target reachability/burden would solve general halting/reachability instances.

Predictive GMI theorems must restrict the class, use bounds/surrogates, or be statistical/empirical.

---

## GMI-T12 — compact exact signature lower bound

**Class:** `FINITE INFORMATION LOWER BOUND`

For target set size `n`, if the admitted machine class can realize every burden vector in `{1,...,L}^n`, an exact signature predicting every burden vector needs at least

\[
n\log_2L
\]

bits in the worst case.

Compact cross-paradigm signatures therefore require restricted family regularity.

---

## GMI-T13 — generality preorder

**Class:** `DEFINITION / ORDER THEORY`

A deployed system is `S=(M,d,D)`. Over ecology family `Eset`, `S1` dominates `S2` when its capability-resource frontier weakly dominates on every registered ecology.

This relation is reflexive and transitive but not antisymmetric on machine identities because different systems can have identical profiles.

Therefore generality dominance is a **preorder** on deployed systems.

Mutual dominance defines profile equivalence; the induced relation is a partial order on profile-equivalence classes under the declared frontier semantics.

---

## GMI-T14 — scalar generality requires a declared measure

**Class:** `DERIVED_FROM_DEFINITION`

A scalar score requires ecology distribution `mu`, starting situation `d`, development protocol `D`, and utility/scalarization `u`:

\[
G_{\mu,u}(M,d,D)
=E_{E\sim\mu}
[\sup_{(Q,B)\in F_M(E\mid d,D)}u(Q,B)].
\]

Different `mu,u,d,D` can reverse rankings.

Universal Intelligence provides a powerful parent measure under its own environment/reward/complexity semantics.

---

## GMI-T15 — semantic equivalence does not imply resource equivalence

**Class:** `DERIVED_FROM_DEFINITIONS`

Let two morphologies induce the same registered semantic future law from corresponding semantic states, but different raw resource receipts.

Then they are semantically equivalent under `~sem` but need not be equivalent under a resource-sensitive developmental compiler relation or occupy the same capability-resource frontier.

This establishes the formal role of morphology: different computational organizations can realize the same semantic cognition with different developmental/resource geometry.

---

# Theory closure conditions

## Established synthesis theory at scope

GMI-v1 may be called

```text
GMI_SYNTHESIS_THEORY_ESTABLISHED_AT_SCOPE_V1
```

when:

- [ ] definitions/axioms are internally consistent after hostile review;
- [ ] finite exact reference implementation matches core profile/dominance/amortization/minimization semantics;
- [ ] at least four materially different morphology families use the same schema/definitions;
- [ ] imported parent theorems have explicit assumption/reduction maps;
- [ ] major negative/impossibility cases are represented rather than excluded by definition.

This is a formal synthesis claim, not yet empirical cross-domain general intelligence.

## Empirically supported general developmental theory

Additionally requires materially different real validation regimes using unchanged definitions (e.g. Lean math and execution-verified code), plus disjoint replication.

## New general law

Additionally requires at least one of:

- [ ] held-out cross-paradigm pre-outcome predictor beating family-specific parent products;
- [ ] prospectively predicted morphology phase transition recovered from a neutral endogenous candidate space;
- [ ] theory-predicted parent-frontier hole filled by a non-parent-equivalent morphology.

## New intelligence morphology

Requires the third route plus bounded parent reduction and replication.

## RSI / meta-morphogenesis

Requires declining burden to obtain fresh verified frontier improvements across genuine generations under a fixed external constitution and strong meta-optimization parents.

These are different scientific rungs and must not be conflated.