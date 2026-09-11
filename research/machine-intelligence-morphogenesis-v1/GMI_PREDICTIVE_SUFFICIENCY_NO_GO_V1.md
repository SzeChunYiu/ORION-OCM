# GMI Predictive Sufficiency / Identity-Encoding No-Go v1

Status: **FORMAL/METHODOLOGICAL THEORY HARDENING — CLOSES LOW-DIMENSIONAL LOOKUP-TABLE VACUITY**

Status date: 2026-09-12.

Refs:

- `GMI_REALIZATION_DEMAND_SIGNATURE_V1.md`
- `GMI_CAUSAL_MECHANISM_PHASE_THEORY_V1.md`
- `GMI_MORPHOLOGY_SELECTION_NO_GO_V1.md`
- `COMPILER_INFORMATION_NO_GO_V1.md`
- `GMI_E1_E3_THEORY_VALIDATION_GATE_V2.md`

Purpose:

> Make “compact architecture-neutral predictor” non-vacuous. Dimension alone is not an information bound; a signature or response descriptor can hide world/candidate identity or protected outcomes. GMI therefore needs semantic invariance, pre-outcome measurability and bounded information/description precision, plus an explicit sufficiency/collision criterion.

---

# 1. Atomic gap: low dimension is not low information

The current realization-sufficiency conjectures ask whether a bounded-dimensional signature `Xi` can predict frontier movement.

This is necessary but not sufficient to rule out memorization.

A single real number can, in a purely mathematical model with unbounded precision, encode arbitrarily much information.

For a finite registered set of obligations

\[
\Omega_1,\ldots,\Omega_N,
\]

define

\[
\Xi_{id}(\Omega_i)=i.
\]

This is one-dimensional.

A downstream predictor can memorize the entire protected frontier table indexed by `i`.

Perfect prediction would then establish only:

```text
WORLD_IDENTITY_LOOKUP
```

not a cross-paradigm realization law.

Therefore:

\[
\boxed{
\text{bounded dimension}
\not\Rightarrow
\text{bounded scientific information}.
}
\]

---

# 2. Response-descriptor lookup-table vacuity

The same failure can occur on the realization side.

Suppose `R_M` is unconstrained.

For every morphology `M` and protected world `Omega_i`, let the descriptor contain a table

```text
R_M[i] = exact protected burden/frontier outcome of M on Omega_i.
```

Then

\[
(\Xi,R_M)\to Y
\]

is trivially perfect even if `Xi` contains no meaningful demand law.

Likewise a scalar response coordinate with unbounded precision can encode the same table.

Therefore `R_M` must also be:

```text
pre-outcome;
measurement-defined;
bounded in information/description precision;
semantically interpretable across the claimed scope;
forbidden from containing protected world/candidate outcome lookup.
```

This is the response-side analogue of `COMPILER_INFORMATION_NO_GO_V1.md`.

---

# 3. Admissible demand measurement map

Write the demand signature as an explicit measurement map

\[
\Psi:\Omega\to\mathcal X,
\qquad
\Xi=\Psi(\Omega).
\]

For confirmatory GMI prediction, `Psi` must be frozen before protected outcomes and satisfy the measurement-sheet contract in `GMI_REALIZATION_DEMAND_SIGNATURE_V1.md`.

In addition, declare an information/description contract.

Possible finite contracts include:

```text
coordinate count;
finite numeric precision / quantization;
allowed structured-object size;
description length of Psi;
number/complexity of obligation queries used by Psi;
computation budget for measurement;
```

The exact budget is experiment-relative.

The non-negotiable point is:

> a “compact” signature must have a registered finite information channel from obligation to predictor; unbounded-precision world identifiers do not count.

---

# 4. Semantic remint invariance

Let `G_surface` be a prospectively defined class/group of transformations that alter only surface representation while preserving the registered semantic obligation up to isomorphism.

Examples may include:

```text
renaming labels/variables/components;
permuting feature encodings;
isomorphic graph relabeling;
reminting task names;
changing serialization/layout with semantics fixed.
```

A strongly architecture-neutral obligation measurement should satisfy, exactly or within frozen estimator tolerance,

\[
\boxed{
\Psi(g\cdot\Omega)
=
\Psi(\Omega)
\qquad
\forall g\in G_{surface}.
}
\]

If a coordinate changes under pure semantic remint, it is measuring surface identity or an implementation convention rather than the intended obligation property.

This is stronger than merely withholding an explicit `family_id` column.

Terminal:

```text
SURFACE_IDENTITY_LEAKAGE_IN_DEMAND_SIGNATURE
```

---

# 5. Realization-side implementation invariance

Likewise let `G_impl` contain implementation transformations that preserve the registered realization mechanism/semantic/resource object while changing irrelevant representation details.

Examples:

```text
component renaming;
memory-address/layout remint;
source-code refactor with same behavior/resource meter;
mechanism-equivalent A4 realization under the witness contract where resource descriptor is separately retained.
```

A mechanism-level response descriptor `Phi(M)` should be invariant to irrelevant implementation remints while preserving legitimate resource-response differences.

This requires care:

```text
mechanism semantics may be invariant;
resource cost need not be invariant.
```

Therefore split where necessary:

\[
\Phi(M)
=(\Phi_{mech}(M),\Phi_{resource}(M,P)).
\]

Do not force physically different costs to be identical merely because mechanism semantics match.

---

# 6. Registered predictive object

For one candidate morphology `M`, let protected outcome object be

\[
Y_M(\Omega,P,h)
\]

containing only prospectively registered capability/resource/mechanism targets.

Let

\[
X=\Psi(\Omega),
\qquad
R=\Phi(M,h_{dev}),
\]

where any history dependence admitted to `Phi` is frozen by protocol.

A GMI predictor has form

\[
\widehat Y=f(X,R,P).
\]

The scientific hypothesis is not that some arbitrary `f,X,R` can fit a finite table.

It is that a **frozen, bounded-information, semantically invariant** `Psi/Phi/f` transfers to protected obligations/families.

---

# 7. Frontier sufficiency criterion

Over a registered distribution/class of obligations, contexts and morphologies, define exact/statistical sufficiency as the conditional relation

\[
\boxed{
Y_M
\perp\!\!\!\perp
\Omega
\mid
\Psi(\Omega),\Phi(M,h),P
}
\]

at the claimed scope, with the obvious history qualification.

In words:

> once the registered demand signature, response descriptor and context are known, the remaining details of the obligation add no predictive information about the registered outcome.

This is the strongest clean statistical form of the realization-signature hypothesis.

In deterministic finite worlds it reduces to a collision condition.

In noisy real worlds it becomes a conditional-distribution/calibration hypothesis.

No finite experiment proves this universally.

It can only support or reject it over the registered scope.

---

# 8. GMI-PS1 — deterministic collision theorem

## Statement

Let `Omega_1,Omega_2` be two protected obligations and `M_1,M_2` matched so that

\[
\Psi(\Omega_1)=\Psi(\Omega_2),
\]

\[
\Phi(M_1,h_1)=\Phi(M_2,h_2),
\]

and exogenous context `P` is the same.

If the exact registered outcomes differ,

\[
Y_{M_1}(\Omega_1,P,h_1)
\ne
Y_{M_2}(\Omega_2,P,h_2),
\]

then no deterministic predictor

\[
f(\Psi,\Phi,P)
\]

can be exact on both cases.

## Proof

The predictor receives identical inputs in the two cases, so it must return the same output.

The required exact outputs differ.

Contradiction.

QED.

Terminal:

```text
PREDICTIVE_SIGNATURE_RESPONSE_COLLISION
```

This theorem is elementary but should be the canonical logic behind collision hostiles.

---

# 9. GMI-PS2 — stochastic irreducible collision error

Suppose identical predictor inputs

\[
(X,R,P)=c
\]

occur with two or more different protected outcome distributions.

Then any predictor restricted to `c` faces irreducible conditional uncertainty equal to the Bayes risk under the prospectively declared loss/scoring rule.

Thus observed residual error at a signature collision is not merely “model capacity failure.”

It can certify missing predictive information in `Psi/Phi/P` if:

```text
estimation noise is controlled;
outcome stochasticity is correctly modeled;
the collision itself is genuine rather than measurement error.
```

This supplies the statistical generalization of V0 F1.

---

# 10. Whole-frontier sufficiency is stronger than single-candidate sufficiency

Morphology frontier membership depends jointly on multiple candidate outcome vectors.

Let registered candidate class be

\[
\mathcal M=\{M_1,\ldots,M_k\}
\]

and let

\[
\mathbf Y_{\mathcal M}
=(Y_{M_1},\ldots,Y_{M_k}).
\]

A signature/response system is **frontier-sufficient at scope** only if the joint candidate outcome law is sufficiently captured:

\[
\mathbf Y_{\mathcal M}
\perp\!\!\!\perp
\Omega
\mid
\Psi(\Omega),\{\Phi(M_i,h_i)\}_{i=1}^k,P.
\]

Predicting one morphology's cost accurately does not automatically imply correct Pareto ordering or mechanism-core prediction.

Therefore E2 should score:

```text
burden-vector calibration;
rank/frontier calibration;
mechanism-core calibration;
```

separately.

---

# 11. Mechanism-core sufficiency

For registered frontier mechanism core

\[
K^*(\Omega,P),
\]

a separate architecture-neutral target is

\[
K^*
\perp\!\!\!\perp
\Omega
\mid
\Psi(\Omega),P
\]

when the candidate/response class is fixed as required by the morphology-selection no-go.

More generally include registered candidate-class/response descriptors explicitly.

This formulation clarifies what Track B wants beyond algorithm selection:

> compact semantic demand measurements predict mechanism invariants of the frontier, not merely the winner identity in a memorized portfolio.

---

# 12. Residual structural test

Let `W(Omega)` be an architecture-neutral withheld structural feature not used in `Psi`.

After freezing the base GMI predictor, test on protected data whether

\[
W
\]

adds material predictive value for `Y` conditional on

\[
(\Psi,\Phi,P).
\]

If yes, then one of the following is true:

```text
Psi is insufficient at scope;
Phi/P is insufficient;
measurement error created apparent residual information;
the response law is misspecified.
```

The result should trigger theory revision/collision analysis, not silent feature addition on the same protected set.

A revised signature requires fresh confirmation.

---

# 13. Compactness must charge the measurement law itself

A fixed vector of simple quantities and a giant target-specific measurement program are not the same scientific theory.

Therefore complete compactness accounting should include at least:

\[
L(\Psi)
+
L(\Phi)
+
L(f)
+
L_{precision/data}(X,R)
\]

or another prospectively frozen complexity/information budget.

No universal MDL/Kolmogorov claim is needed.

The point is to block this loophole:

```text
small output vector
+
enormous target-specific extractor
=
“compact theory”.
```

This is directly analogous to the target-specific compiler no-go.

---

# 14. Family-native comparison must equalize information access

A shared GMI predictor should not beat family-native parents merely because it receives richer side information.

For every comparison declare:

```text
which obligation/context measurements GMI receives;
which measurements the family-native predictor receives;
which morphology-internal response measurements each receives;
measurement cost;
training/development data budget;
model/description complexity where relevant.
```

Useful comparisons include two modes.

## Equal-information mode

GMI and native parent receive the same legally available raw measurement pool, then build their own predictors.

## Native-first-refusal mode

Native parent receives its strongest prospectively legal family-specific descriptors, while GMI must still add out-of-family/shared predictive value.

Do not mix these two modes without labeling them.

---

# 15. Isomorphism-remint hostile

For each protected semantic obligation world, generate isomorphic/reminted versions under `G_surface`.

Acceptance requires, within estimator uncertainty:

```text
same Xi measurement;
same predicted mechanism pressure;
same predicted outcome law after matching response/context;
```

while family/surface identifiers differ.

If performance collapses only under remint, the predictor relied on identity/proxy information.

This should be a first-class E2 hostile, not a cosmetic robustness check.

---

# 16. Precision hostile

If a real-valued coordinate is used, evaluate whether increasing its numeric precision dramatically improves protected prediction by allowing it to encode incidental world identity.

Freeze operational precision before confirmation.

A suspicious signature pattern is:

```text
semantically coarse stated meaning
+
extremely high numeric precision
+
near-unique value per world
+
large performance collapse after quantization/remint.
```

This does not automatically prove cheating, but it demands an explicit structural explanation.

---

# 17. Candidate/world-ID adversary

Include a red-team baseline allowed to use:

```text
world ID
surface hash
family ID
candidate ID
seed ID
```

but not semantic measurements.

Its role is not to be a valid theory competitor.

Its role is to estimate how much protected predictability is available from identity leakage in the benchmark.

If the supposedly architecture-neutral GMI predictor tracks this baseline and fails remint/family holdout, suspect leakage.

---

# 18. Revised non-vacuous RSC target

Replace any informal reading of “bounded-dimensional signature” with:

> There exists a prospectively frozen, bounded-information/description, surface-isomorphism-invariant obligation measurement map `Psi`, a prospectively legal bounded-information realization response descriptor `Phi`, and a bounded predictive law `f` such that protected burden/frontier/mechanism outcomes are predicted to useful accuracy across registered family-held-out ecologies, with no material architecture-neutral residual structure left unexplained at the claimed scope and with native parents receiving first refusal.

Symbolically the idealized sufficiency target is

\[
Y
\perp\!\!\!\perp
\Omega
\mid
\Psi(\Omega),\Phi(M,h),P,
\]

plus cross-environment invariance and explicit finite information budgets.

This remains a conditional empirical conjecture.

---

# 19. New kill/narrowing terminals

```text
LOW_DIMENSION_HIGH_INFORMATION_IDENTITY_CODE
SURFACE_IDENTITY_LEAKAGE_IN_DEMAND_SIGNATURE
RESPONSE_DESCRIPTOR_CONTAINS_PROTECTED_LOOKUP
TARGET_SPECIFIC_MEASUREMENT_PROGRAM_DOMINATES
PREDICTIVE_SIGNATURE_RESPONSE_COLLISION
ARCHITECTURE_NEUTRAL_RESIDUAL_REMAINS
FAMILY_NATIVE_COMPARISON_INFORMATION_UNFAIR
PRECISION_DEPENDENT_IDENTITY_LEAKAGE
```

These terminals protect GMI from becoming a memorization scheme with scientific-looking coordinate names.

---

# 20. Literature ownership

The logic here is consistent with several mature parent lessons.

- Unsupervised representation/disentanglement is not generically identifiable without assumptions/inductive bias; coordinate discovery must therefore declare anchors rather than assume latent semantics are uniquely recovered.
- Auxiliary/interventional information can restore identifiability under explicit assumptions; GMI should use the same discipline for latent demand measurements.
- Invariant prediction motivates stable relations across intervention/environment changes rather than pooled correlation alone.
- Information bottleneck/rate-distortion traditions already treat compression as an information problem, not merely coordinate count.
- Adaptive-data-analysis work explains why protected outcomes cannot be repeatedly reused to redesign `Psi/Phi/f` without fresh validation.

GMI novelty is not any of those principles individually. The contribution sought is their integration into a common machine-realization/morphogenesis theory.

---

# 21. Current terminal

```text
GMI_PREDICTIVE_SUFFICIENCY_NONVACUITY_CONTRACT_SPECIFIED_V1
COMPACT_CROSS_PARADIGM_SUFFICIENCY_NOT_ESTABLISHED
```
