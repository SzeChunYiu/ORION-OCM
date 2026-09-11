# GMI Axioms and Theorems v1

Status: **formal working core**. Every row is classified as `ADOPTED_PARENT`, `DERIVED_FROM_DEFINITIONS`, `FINITE_EXACT`, `PROBABILISTIC_PARENT`, `EMPIRICAL_CONJECTURE`, or `IMPOSSIBILITY_LIMIT`.

The aim is to make GMI-v1 a theory with explicit assumptions, not a vocabulary list.

---

# Axioms / constitutive assumptions

## A0 — obligation and protocol relativity

Every intelligence claim is made relative to a declared cognitive obligation/development contract

\[
\mathcal O=(\mathfrak E,\mathcal A,\mathcal Y,V,C,\rho,H,D,J),
\]

where `D` fixes initialization/development/intervention permissions and `J` fixes the future probe/intervention class relevant to state distinguishability.

There is no claim of architecture-independent success without specifying what outcomes count, what information/actions/updates are legal, who verifies them, what resources are charged, and which starting capital is supplied.

## A1 — external verification separation

`V` and `C` are external to the machine's internal proposal/training objective. A system may optimize an internal loss/utility/score, but admissible success is determined by the registered external verifier/constitution.

This blocks the common identification:

```text
low training loss == truth == capability.
```

## A2 — future-consequence developmental-state equivalence

A **developmental situation** `d=(chi,h,xi)` contains the current machine configuration `chi`, registered interaction/development history `h`, and any current public/experimental context `xi` that can affect protected futures.

Two developmental situations are equivalent iff no admissible future intervention/programme in `J`, under the same development protocol `D`, can distinguish them through registered future verified outputs, developmental changes or resource receipts:

\[
d\sim_{\mathcal O,D,J}d'
\iff
\forall j\in J:\ P(Future_{\mathcal O}|d,j,D)=P(Future_{\mathcal O}|d',j,D).
\]

The equivalence class is the abstract developmental sufficient state.

History alone is not assumed sufficient: identical external histories can leave different optimizer state, memory, random state, posterior, replay buffer or morphology configuration.

## A3 — realization multiplicity

The same abstract developmental state/process may have multiple computational realizations. A morphology is therefore a realization/factorization plus resource semantics, not the abstract state itself.

## A4 — resource explicitness

Resources are represented as a vector. Scalar cost/utility exists only after a price/utility mapping is fixed prospectively.

## A5 — temporal separation

Execution/cognition, within-form development, and morphogenesis are distinct processes even when a concrete implementation fuses them into one dynamical system.

## A6 — inherited development

A change counts as developmental only when information/state produced by earlier registered experience persists causally into future cognition or future update/morphogenesis.

## A7 — no universal superiority without ecology restriction

Morphology/deployed-system superiority is always relative to an ecology/resource/verifier/development class. A global total order is not assumed.

---

# Theorem / proposition programme

## GMI-T01 — finite developmental minimization

**Class:** `ADOPTED_PARENT + FINITE_EXACT`

For a finite deterministic developmental transducer and finite registered event alphabet, quotienting complete machine situations/states by equality of all future output/update traces produces a unique minimal deterministic machine up to isomorphism.

**Parent:** Myhill-Nerode / deterministic transducer minimization.

**Track-B witness:** current-query quotient merges states that the developmental quotient separates after teaching.

**Consequence:** minimality is mathematically meaningful only relative to the future-obligation trace semantics.

---

## GMI-T02 — no representation-independent implementation atom

**Class:** `IMPOSSIBILITY_LIMIT at the stated level`

If unit boundaries are defined only by computational behavior, a unit can generally be refactored into a composition of smaller units, while finite collections can be flattened into a single global transition machine. Therefore computation alone does not identify one unique irreducible implementation atom.

**Consequence:** an irreducible implementation unit requires extra structure such as locality, causal intervention boundaries, physical cost, communication constraints, or a declared primitive grammar.

---

## GMI-T03 — factorization can exponentially compress developmental state

**Class:** `FINITE_EXACT + ADOPTED_PARENT`

There exist families with minimal global developmental state count exponential in `n` while a factored realization uses `O(n)` local state plus a fixed shared local rule and `O(1)`-local updates.

Track-B exact construction:

\[
|Z_{min}|=3^n,
\qquad
|T_{flat}|=2n3^n,
\]

while realization uses `n` local cells + one six-entry rule.

**Parent:** factored MDP / DBN / structured-program representation theory.

**Consequence:** morphology/factorization can matter dramatically even when it does not create a new computational class.

---

## GMI-T04 — lifecycle phase boundary

**Class:** `DERIVED_FROM_DEFINITIONS`

For two fixed deployed systems with scalarized build costs `A_i,A_j`, expected per-use burdens `c_i(E),c_j(E)`, and reuse horizon `H`,

\[
C_i=A_i+Hc_i(E),\quad C_j=A_j+Hc_j(E),
\]

so

\[
i\prec j
\iff
A_i-A_j+H[c_i(E)-c_j(E)]<0.
\]

A crossover exists when the denominator is nonzero:

\[
H^*=\frac{A_j-A_i}{c_i(E)-c_j(E)}.
\]

**Parent ownership:** amortization/materialization/algorithm-selection/resource economics.

**GMI use:** simplest exact phase law for why a high-build low-use-cost system (e.g. a trained neural model) may dominate only at sufficiently long reuse horizon.

---

## GMI-T05 — information-bias phase identity in idealized proposal search

**Class:** `ADOPTED_PARENT / DERIVED`

For target ecology `P`, morphology proposal distribution `Q_M`, expected code/search burden is

\[
H(P)+D_{KL}(P\Vert Q_M)
\]

under the registered ideal prefix/proposal model. Adding build cost `B_M` and horizon `N` gives

\[
C_M=B_M+N[H(P)+D_{KL}(P\Vert Q_M)].
\]

Therefore morphology competition is governed by ecology-bias mismatch plus amortization in this idealized case.

**Parents:** source coding, MDL/Bayes, information-theoretic bounded rationality.

**Boundary:** not a universal machine-intelligence law; many developmental processes do not reduce to this exact proposal model.

---

## GMI-T06 — progress-potential to hitting-time reduction

**Class:** `ADOPTED_PARENT`

Given a valid progress potential `Phi` and drift conditions, expected time/cost to hit a target can be bounded/derived by drift theorems.

**Parent:** additive/multiplicative/variable drift analysis, stochastic shortest path.

**GMI consequence:** the nontrivial problem is not `potential + drift -> time`; it is deriving a compact pre-outcome potential/drift signature from morphology/ecology structure that transfers across families.

---

## GMI-T07 — history-induced cognition capital criterion

**Class:** `DEFINITION + EMPIRICAL_CAUSAL_CRITERION`

Let fresh target `tau` have verified solution `m*` absent from the relevant developmental history. Let `Q_0` be matched-reset proposal dynamics and `Q_H` inherited-state-conditioned dynamics.

Inherited developmental state creates K1 cognition capital if, before access to target success, it causes a change in future proposal/control/representation that reduces complete verified burden:

\[
E[B_H(\tau)]<E[B_0(\tau)]
\]

and a pre-solution mediator is observed, e.g.

\[
rank_H(m^*)<rank_0(m^*)
\]

or higher useful proposal mass.

**Current OCM evidence:** #323 supports this at authored program-search scope; it is not a theorem of arbitrary learners.

---

## GMI-T08 — developmental-capital criterion

**Class:** `DEFINITION + EMPIRICAL_CAUSAL_CRITERION`

K2 requires not merely cheaper future solving but cheaper acquisition of new K1:

\[
E[B^{acq}_{H}(K1_{new})]
<
E[B^{acq}_{RESET}(K1_{new})].
\]

The mechanism must be inherited-state-derived and matched against a procedure that has the same external information/tools but lacks the relevant developmental state.

**Current OCM status:** NOT_ESTABLISHED at the #323 grammar for retained-capital recombination (registered bar met on 2/9 fresh seeds).

---

## GMI-T09 — conditional meta-generalization

**Class:** `PROBABILISTIC_PARENT`

Under explicit related-task/meta-environment assumptions, prior tasks can improve expected future-task performance/sample complexity/regret through learned representations, priors, or learning algorithms.

**Parents:** Baxter; Pentina-Lampert PAC-Bayes lifelong learning; Maurer-Pontil-Romera-Paredes; Alquier-Mai-Pontil; PACOH; later PAC-Bayesian learning-algorithm meta-learning.

**GMI consequence:** developmental intelligence is not guaranteed over arbitrary tasks. Any broad claim requires a registered ecology distribution/relatedness assumption or empirical cross-domain test.

---

## GMI-T10 — ecology/resource-conditioned morphology

**Class:** `ADOPTED_PARENT + EMPIRICAL/FINITE_SPECIALIZATIONS`

Task dependency structure and resource pressures can change which factorization/architecture is selected and can alter future evolvability.

**Parents:** factored models; Kashtan-Alon modularly varying goals; facilitated variation; connection-cost modularity/hierarchy; information-theoretic bounded rational systems.

**Track-B finite special case:** exhaustive four-variable partition census shows exact build/communication/horizon phase transitions.

**Boundary:** broad ecology→architecture is parent-owned. A new GMI law requires prospective cross-paradigm quantitative prediction beyond family-native theories.

---

## GMI-T11 — no universal exact developmental-burden predictor

**Class:** `IMPOSSIBILITY_LIMIT`

For unrestricted Turing-complete morphology classes, an exact computable predictor that decides whether a target will be reached within finite burden would solve general halting/reachability instances.

**Consequence:** predictive GMI theorems must restrict the morphology/ecology family, use computable surrogates/bounds, or be statistical/empirical.

---

## GMI-T12 — compact exact signature lower bound

**Class:** `FINITE INFORMATION LOWER BOUND`

For a finite target set of size `n`, if the admitted morphology class can realize every burden vector in `{1,...,L}^n`, then an exact signature that predicts every burden vector needs at least

\[
n\log_2 L
\]

bits in the worst case.

**Consequence:** a genuinely compact cross-paradigm structural signature is possible only by exploiting restricted family regularity; arbitrary machines cannot be compressed into a tiny exact universal morphology metric.

---

## GMI-T13 — generality preorder

**Class:** `DEFINITION / ORDER THEORY`

For an ecology family `Eset`, define a deployed system `S=(M,d,D)` and its intelligence profile. `S1` developmentally dominates `S2` when its capability-resource frontier weakly dominates on every registered ecology.

This relation is reflexive and transitive but not antisymmetric on machine identities: different systems can have identical profiles.

Therefore generality dominance is a **preorder on deployed systems**.

Define profile equivalence by mutual dominance. The induced relation is a partial order on profile-equivalence classes under the declared frontier semantics.

**Consequence:** statements such as "more generally intelligent" can be made without a universal scalar, but the ecology family, starting situations, development protocols and frontier coordinates must be explicit.

---

## GMI-T14 — scalar generality requires declared measure

**Class:** `DERIVED_FROM_DEFINITION`

A scalar generality score is meaningful only after declaring ecology distribution `mu`, starting developmental situation `d`, development protocol `D`, and utility/scalarization `u`:

\[
G_{\mu,u}(M,d,D)=E_{E\sim\mu}[\sup_{(Q,B)\in F_M(E\mid d,D)}u(Q,B)].
\]

Different `mu,u,d,D` can reverse rankings.

**Parent relation:** Universal Intelligence supplies an especially broad complexity-weighted environment measure for reward-oriented agents; GMI retains raw developmental/resource profiles before scalarization.

---

# Theory closure conditions

## Established synthesis theory at scope

GMI-v1 may be called

```text
GMI_SYNTHESIS_THEORY_ESTABLISHED_AT_SCOPE_V1
```

when all are true:

- [ ] definitions/axioms are internally consistent and non-circular after hostile review;
- [ ] finite exact reference implementation matches core profile/dominance/amortization/minimization semantics;
- [ ] mappings from at least four materially different morphology families use the same schema/definitions;
- [ ] imported parent theorems have explicit assumption maps/reduction maps;
- [ ] major impossibility/negative cases are represented rather than excluded by definition.

This is a **formal synthesis claim**, not an empirical cross-domain intelligence claim.

## Empirically supported general developmental theory

Additionally requires real-domain evidence that the same definitions survive materially different validation regimes (e.g. Lean mathematics + execution-verified coding) without semantic rewriting, with disjoint replication.

## New general law

Additionally requires at least one of:

- [ ] pre-outcome cross-paradigm predictor/signature beats family-specific parent products on held-out regimes;
- [ ] theory-predicted morphology phase transition recovered prospectively from a neutral endogenous candidate space;
- [ ] theory-predicted parent-frontier hole filled by a non-parent-equivalent morphology.

## New form of intelligence

Requires the third route plus parent reduction and replication.

## RSI / meta-morphogenesis

Requires declining burden to obtain fresh verified frontier improvements across genuine generations under a fixed external constitution and strong meta-optimization parents.

These accomplishments are different rungs and must not be conflated.