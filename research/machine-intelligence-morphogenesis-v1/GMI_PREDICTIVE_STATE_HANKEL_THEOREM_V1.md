# GMI Predictive-State Hankel Theorem v1

Status: **PARENT-THEOREM INTEGRATION / ZERO-PRIOR SEQUENCE-STATE CALIBRATION**

Status date: 2026-09-12.

Purpose:

> Integrate the exact linear-dimension theorem behind weighted automata/predictive-state representations into GMI's zero-prior derivation of recurrent and state-space machine families.

This is established parent mathematics, not a new GMI theorem.

---

# 1. Sequence law and Hankel matrix

Let `Sigma` be a finite alphabet and let

\[
f:\Sigma^*\to\mathbb F
\]

be a scalar sequence function over field `F` (for example string probability/weight, or one component of a predictive response law).

Define the bi-infinite Hankel matrix

\[
H_f(u,v)=f(uv),
\qquad u,v\in\Sigma^*.
\]

Rows are indexed by histories/prefixes and columns by future suffixes/tests.

---

# 2. Linear sequential realization

A `d`-dimensional weighted linear realization has vectors `alpha,beta in F^d` and one transition matrix `A_a in F^{dxd}` per symbol such that

\[
f(a_1\cdots a_T)
=\alpha^T A_{a_1}\cdots A_{a_T}\beta.
\]

## Theorem PS-1 — realization implies Hankel-rank upper bound

Every `d`-dimensional linear realization satisfies

\[
\operatorname{rank}(H_f)\le d.
\]

### Proof

For prefix `u` define row-state

\[
p(u)^T=\alpha^T A_u
\]

and for suffix `v` define column-state

\[
q(v)=A_v\beta.
\]

Then

\[
H_f(u,v)=p(u)^Tq(v),
\]

so the Hankel matrix factors through dimension `d`. QED.

---

# 3. Finite Hankel rank gives a minimal linear state

Classical weighted-automata/Hankel realization theory (Carlyle–Paz/Fliess; closely related to linear predictive-state representations) establishes the converse.

## Parent theorem PS-2 — minimal linear realization dimension

If

\[
r=\operatorname{rank}(H_f)<\infty,
\]

then `f` has an exact linear sequential realization of dimension `r`, and no exact linear realization has dimension smaller than `r`.

Therefore

\[
\boxed{d^*_{linear}=\operatorname{rank}(H_f)}.
\]

### Construction intuition

Choose `r` linearly independent Hankel rows as a basis. Represent each history by the coefficients expressing its predictive row in that basis. Appending a symbol maps one predictive row to another, inducing a linear transition operator on the basis coordinates. A suffix/evaluation vector recovers future weights.

---

# 4. GMI interpretation

The theorem supplies an exact zero-prior state-dimension variable:

\[
\chi_{pred}^{linear}=\operatorname{rank}(H_f).
\]

It is not an architecture name. It is the minimum dimension of any exact **linear predictive state** for the registered sequence law.

Thus GMI should predict pressure toward compact recurrent/state-space realization when:

```text
raw history grows with horizon
Hankel/predictive rank stays bounded or slowly growing
recursive state updates are cheap
serving prefers scan/streaming state over replaying history
```

This provides a formal derivation route for linear state-space/weighted-automaton/PSR-like forms.

---

# 5. Relation to the exact future-response quotient

The future-response quotient in `GMI_KNOWN_FORM_DERIVATION_THEOREMS_V1.md` is a general exact state notion based on equality of all future behavior.

Hankel rank is different:

```text
quotient cardinality:
    minimal number of arbitrary exact discrete response classes

Hankel rank:
    minimal dimension of a linear predictive realization over a field
```

A system may have many/infinite distinct predictive rows but low linear rank. Therefore both coordinates are useful and should not be conflated.

---

# 6. Finite-data limitation

A finite observed Hankel block `H_{P,S}` satisfies

\[
\operatorname{rank}(H_{P,S})\le\operatorname{rank}(H_f).
\]

It provides only a lower bound on the full linear dimension unless the selected prefixes/suffixes are known sufficient.

This matches the zero-prior identifiability theorem: unseen histories/tests can increase the required dimension.

Therefore real zero-prior prediction requires:

```text
prefix/test coverage assumptions
rank/noise thresholding
uncertainty on effective rank
held-out predictive checks
```

rather than declaring the observed finite rank to be the true state dimension.

---

# 7. Controlled systems

Predictive-state representation theory extends the same principle to action-conditional tests/histories: state can be a set/vector of predictions about future observable events conditioned on actions.

For GMI, this means hidden-state representation need not be interpreted as a latent physical variable; a predictive quotient/linear predictive basis can itself be the semantic sufficient state.

---

# 8. Gap update

`GKF-07 recurrent/state dimension` now contains:

```text
exact arbitrary future-response quotient minimality     CLOSED
approximate TV-packing lower bound                      CLOSED
minimal exact linear predictive dimension = Hankel rank PARENT-THEOREM CLOSED
finite-horizon/unseen-history identifiability limit     CLOSED
finite-data effective predictive-rank estimator         OPEN-BLOCKING
nonlinear realization advantage                         OPEN-BLOCKING
```

---

# 9. Claim ceiling

This integrates established linear realization theory. It does not imply that real sequence tasks are finite-rank, that finite sample Hankel rank is reliable without assumptions, or that a linear state-space realization is always lifecycle-optimal versus attention/memory/nonlinear state.
