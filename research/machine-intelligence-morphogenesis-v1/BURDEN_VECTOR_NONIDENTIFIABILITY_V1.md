# Burden-vector non-identifiability v1

Status: **formal no-go against treating measured developmental cost alone as morphology identity.**

## Claim attacked

A tempting Track-B shortcut is:

> characterize a morphology by its vector of costs on a finite registered target set; if two systems have different burden vectors, they are different forms of intelligence, and the vector itself reveals the underlying developmental structure.

The first clause can be operationally useful at a fixed benchmark. The second is false in general.

## Finite construction

Let the registered target set be finite:

\[
T=\{t_1,\ldots,t_n\}.
\]

Let any desired positive integer burden vector be

\[
c=(c_1,\ldots,c_n),\qquad c_i\ge 1.
\]

Construct an ordinary finite program / finite-state transducer `P_c` with one branch per target identity. On target `t_i`, it executes exactly `c_i-1` counted no-op transitions and then emits the registered verified answer/action for `t_i`.

Therefore `P_c` realizes exactly the prescribed first-hit burden vector `c` on the finite registered scope.

The same construction can be implemented with many syntactically and structurally different programs, state machines, circuits or networks.

Hence:

```text
finite burden vector
!= unique morphology
!= unique developmental geometry
!= evidence for a fundamental cognitive unit
```

## Stronger version

For any finite set of measured statistics that depend only on externally visible finite traces, a sufficiently general program/state-machine parent can encode the same traces while using an arbitrarily different internal factorization.

Consequently, finite phenotype measurements identify at most an equivalence class relative to a frozen compiler/observation/resource contract.

This is another reason Track B uses bounded developmental equivalence rather than syntax labels.

## What survives

A burden vector becomes scientifically explanatory only when it is **predicted from independently specified structure/update/history** under a frozen resource semantics.

The live causal chain is therefore:

\[
\boxed{
S_M,H_M,U_M
\longrightarrow
\widehat{G}_M
\longrightarrow
\widehat{B}(M,E)
\longrightarrow
B_{observed}
}
\]

where:

- `S_M` is morphology structure/factorization;
- `H_M` is legal developmental history/state;
- `U_M` is the update/proposal law;
- `G_M` is a pre-outcome developmental-geometry signature;
- `B` is externally measured verified burden.

If `G_M` is fitted after observing the same burden it explains, no mechanistic credit is earned.

## Relation to parent theory

This no-go is not presented as a deep new computability theorem. It is a direct finite construction using ordinary program/state-machine expressivity and reinforces existing identification/equivalence cautions.

It combines with:

- finite flattening;
- universal-program representation;
- compiler-information accounting;
- algorithm-selection parent theory;
- drift / hitting-time parent theory.

## Track-B consequence

The next result cannot be:

```text
we measured different cost profiles for neural / symbolic / probabilistic systems
```

alone.

It must be closer to:

```text
pre-outcome structural invariant(s)
-> prospectively predict the cost profile / frontier
-> prediction transfers across held-out ecologies
-> intervention on the invariant changes the burden in the predicted direction
```

## Terminal

```text
FINITE_BURDEN_VECTOR_DOES_NOT_IDENTIFY_MORPHOLOGY
STRUCTURE_TO_BURDEN_CAUSAL_PREDICTION_REQUIRED
```
