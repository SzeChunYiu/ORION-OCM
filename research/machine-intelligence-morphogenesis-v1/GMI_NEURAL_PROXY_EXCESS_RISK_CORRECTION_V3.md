# GMI neural proxy excess-risk correction v3

Status: **FORMAL REFINEMENT OF V2 CORRIGENDUM / OFFSET-INVARIANT ACCOUNTING**

Date: 2026-09-12.

Purpose: replace a safe but proxy-offset-dependent bound with the exact invariant quantity that measures whether optimizing the declared proxy also reduces protected excess risk.

The historical NMI-1 remains preserved. `GMI_NEURAL_THEOREM_CORRIGENDUM_V2.md` remains a valid conservative correction. This v3 gives the preferred invariant formulation.

## 1. Protected and proxy excess risks

Let

\[
R^*=\inf_\theta R(\theta),
\qquad
P^*=\inf_\theta P(\theta).
\]

For developed state `\hat\theta`, define

\[
E_R(\hat\theta)=R(\hat\theta)-R^*,
\qquad
E_P(\hat\theta)=P(\hat\theta)-P^*.
\]

Both are invariant to adding arbitrary constants to their respective objectives.

Proxy optimization error is exactly

\[
\epsilon_{opt}=E_P(\hat\theta)\ge0.
\]

Define the **excess-risk transfer residual**

\[
\tau_{P\to R}(\hat\theta)
=
E_R(\hat\theta)-E_P(\hat\theta).
\]

## 2. Theorem PE-1 — exact proxy-to-protected identity

By definition,

\[
\boxed{
R(\hat\theta)
=
R^*
+
\epsilon_{opt}
+
\tau_{P\to R}(\hat\theta)
}.
\]

Hence

\[
R(\hat\theta)
\le
R^*
+
\epsilon_{opt}
+
\tau^+_{P\to R}(\hat\theta),
\]

where `tau^+=max(tau,0)`, or conservatively with `|tau|`.

This is an identity, not a probabilistic bound.

## 3. Why this is preferable to raw objective gaps

Adding any constants `c_R,c_P` to the two objectives leaves `E_R,E_P,tau` unchanged. Therefore the decomposition cannot be manipulated by an arbitrary loss baseline.

The raw quantity `R(\hat\theta)-P(\hat\theta)` is not invariant to such shifts and should not be treated as a standalone scientific generalization mechanism unless objective normalization has semantic meaning.

## 4. Uniform calibration modulus

A useful prospective development theorem has the form

\[
E_R(\theta)
\le
\omega(E_P(\theta)) + \epsilon_{cal}
\]

for all reachable relevant states with high registered confidence, where `omega(0)=0` ideally.

Then

\[
R(\hat\theta)
\le
R^*+
\omega(\epsilon_{opt})+\epsilon_{cal}.
\]

This separates:

```text
representation floor R*
actual proxy optimization epsilon_opt
proxy-to-protected calibration law omega, epsilon_cal
```

rather than mixing loss offsets with generalization.

## 5. Negative twin

A proxy may have states with arbitrarily small `E_P` but large `E_R`; then no useful small calibration modulus exists. Excellent proxy optimization does not imply protected intelligence.

This includes reward/model misspecification, benchmark shortcuts and objectives that ignore protected authority/lineage/intervention distinctions.

## 6. Interface/development composition

If protected risk is already end-to-end, the identity applies directly. If an intermediate core risk is used, interface/update terms may be added only through a separately proved semantic composition inequality or failure-event union bound, as stated in the v2 corrigendum.

## Claim ceiling

This fixes the algebraic accounting target. Estimating a useful prospective calibration modulus for modern neural development remains OPEN-BLOCKING.
