# Grand GMI Substrate-Lifting Theorem V1

Status: **ABSTRACT THEOREM + FINITE EXACT WITNESS**  
Date: 2026-09-12

## 1. Why a grand theory needs a substrate theorem

A theory of machine intelligence cannot make classical bits, neural weights, digital gates, biological cells, or quantum amplitudes part of the *definition* of intelligence. Those are candidate physical realizations. The semantic core must survive a change of realization whenever the protected operational behavior survives.

Grand GMI therefore separates:

\[
\text{semantic obligation/capability}
\quad\text{from}\quad
\text{physical realization/resource cost}.
\]

## 2. Process presentations

A substrate/process presentation `P` supplies:

- physical states or systems;
- legal transformations/processes;
- sequential composition and, where relevant, parallel composition;
- interventions/inputs and observable effects;
- a registered physical resource vector `rho_P`.

A GMI machine in `P` is any legal process network with the declared boundary and probes.

The semantic response functor is the induced map from a physical machine to its complete protected intervention/observation response profile:

\[
\mathcal R_P:M\mapsto Q_M.
\]

GMI semantic equivalence is equality of this response profile at the declared resolution, not equality of microstate description.

## 3. Operational implementation map

Let `F:P -> P'` map machines/processes from one substrate presentation to another. Call `F` a **GMI operational implementation** for a problem class when:

1. legal compositions are preserved;
2. declared interventions have mapped interventions;
3. every protected observable response is preserved:

\[
\mathcal R_{P'}(F(M))=\mathcal R_P(M);
\]

4. the resource transformation is declared, e.g.

\[
\rho_{P'}(F(M))=\phi(\rho_P(M),M)
\]

or at least bounded by a proved map.

## 4. Substrate-lifting theorem

**GG22 — semantic substrate invariance.** For every operational implementation `F`, all response-defined GMI statements commute with `F`:

- obligation satisfaction is preserved;
- semantic equivalence is preserved;
- predictive/control response classes are preserved;
- semantic-cut requirements are preserved;
- trace-defined capability values are preserved.

Proof: every item is a function only of the protected response profile, and the response profile commutes with `F` by definition.

This is a representation-invariance theorem, not a claim that every substrate can efficiently implement every process.

## 5. Resource-frontier transport

Capabilities can be identical while physical cost changes. If the resource map `phi` is known, an attainable point

\[
(Q(M),\rho_P(M))
\]

maps to

\[
(Q(M),\rho_{P'}(F(M))).
\]

Therefore substrate changes preserve semantic coordinates but generally deform the physical Pareto frontier.

**GG23 — resource transport.** A semantics-preserving implementation does not imply resource equivalence. Physical morphology selection therefore lives in the pair

\[
(\mathcal R_P,\rho_P),
\]

not in semantics alone.

## 6. Refinement / microstate theorem

A physical substrate may contain more microstates than the semantic process needs. Let `p:T -> S` be a surjective projection from target microstates to source semantic states such that transitions and observations commute:

\[
p(T'(t,a))=T(p(t),a),
\qquad
O'(t)=O(p(t)).
\]

Then target microstates in the same response class collapse under GMI semantic equivalence. Extra hidden physical degrees of freedom do not create extra intelligence state unless the obligation can probe them.

**GG24 — microstate quotient theorem.** Physical refinement below protected response resolution is quotiented out automatically, while its resource consequences remain measurable.

The exact witness implements one semantic bit using two target microstates per semantic state. A hidden phase bit toggles on every transition. Across 1,020 protected traces through length seven, source and target observations are identical; the target semantic quotient has exactly two classes of two microstates each.

## 7. Classical / stochastic / quantum scope

The theorem is deliberately abstract. Any deterministic, stochastic, continuous, quantum, biological, analog or other process theory can instantiate it **if** it supplies the declared interventions/effects and a semantics-preserving implementation or comparison map.

This document does not assert that quantum processes reduce to classical ones, nor that every quantum capability has a classical implementation. A genuinely quantum channel can change the feasible process set and physical frontier while the GMI obligation/semantic machinery remains well-typed.

## 8. Grand-GMI consequence

Substrate independence is therefore not the statement

`hardware does not matter`.

It is the stronger and more precise pair:

\[
\boxed{\text{semantic intelligence is invariant under protected-response-preserving realization}}
\]

and

\[
\boxed{\text{morphology/capability tradeoffs depend on the substrate resource and process constraints}}.
\]

That separation is required for a theory that aims to cover neural, symbolic, biological, analog and quantum machines without defining any one of them as fundamental.