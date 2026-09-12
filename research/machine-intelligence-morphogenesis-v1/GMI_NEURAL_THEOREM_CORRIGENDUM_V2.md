# GMI neural theorem corrigendum v2

Status: **FORMAL CORRECTION / PRESERVED PREDECESSOR CLAIMS**

Date: 2026-09-12.

Purpose: correct two overstrong/underspecified statements in the landed neural theorem stack without rewriting their historical text.

Affected predecessors:

```text
GMI_NEURAL_MACHINE_INTELLIGENCE_DERIVATION_V1.md       NMI-1
GMI_NEURAL_PREDICTION_TO_INTELLIGENCE_THEOREMS_V1.md  NPI-4
```

The predecessor files remain unchanged as evidence of theory evolution.

---

# 1. Correction NCOR-1 — proxy optimization needs a proxy-optimum alignment term

Let protected core risk be

\[
R(\theta),
\]

and the frozen development proxy objective be

\[
P(\theta).
\]

Define

\[
R^*=\inf_\theta R(\theta),
\qquad
P^*=\inf_\theta P(\theta),
\]

and developed state `theta_hat`.

Define proxy optimization error

\[
\epsilon_{opt}=P(\hat\theta)-P^*\ge0.
\]

Then there is an **exact signed identity**

\[
R(\hat\theta)
=
R^*
+
(P^*-R^*)
+
[P(\hat\theta)-P^*]
+
[R(\hat\theta)-P(\hat\theta)].
\]

Therefore the nonnegative upper bound is

\[
R(\hat\theta)
\le
R^*
+
|P^*-R^*|
+
\epsilon_{opt}
+
|R(\hat\theta)-P(\hat\theta)|.
\]

The missing term in the predecessor display is

\[
\epsilon_{align}=|P^*-R^*|,
\]

the mismatch between the best achievable proxy value and best protected value.

A proxy can have tiny optimization error and tiny pointwise train/proxy gap at `theta_hat` while still select from a family whose optimum is misaligned with the protected objective. That failure is not representation error or optimizer error.

## Interface/development typing correction

If `R` above is already the end-to-end protected trace risk, then interface and developmental mismatch are already inside `R`; adding independent `epsilon_int` or `epsilon_dyn` terms again can double-count.

Those terms may be appended only when the registered loss has been explicitly decomposed into a pre-interface/core quantity plus separately bounded interface/development contributions, for example by a triangle inequality or disjoint failure-event union bound.

Thus the corrected rule is:

```text
protected risk bound = certified decomposition actually proved for the registered loss
not
sum of named error categories merely because they are scientifically useful diagnostics
```

---

# 2. Correction NCOR-2 — prediction forces predictive latent information, not actual latent identity

The predecessor NPI-4 informally suggested that latent states with different latent-conditioned future laws are forced into an exact predictor. This is too strong when latent state is not observed.

Let observed history be `h` and hidden latent state be `Z`. Exact prediction is conditioned on the observed history:

\[
P(w\mid h)=\sum_zP(w\mid h,z)P(z\mid h).
\]

Two different actual latent realizations compatible with the **same observed history** do not correspond to two inputs of `q_pred`; an observed-history predictor receives the same `h` and in general only needs the posterior predictive mixture.

## Theorem NCOR-2A — latent statistic factorization criterion

Let `s_Z(h)` be any target latent statistic computable from history, such as a posterior over latent equivalence classes. Exact predictive state forces retention of `s_Z` iff

\[
h\sim_{pred}h'\Rightarrow s_Z(h)=s_Z(h').
\]

Equivalently, there exists a map `g_Z` such that

\[
s_Z=g_Z\circ q_{pred}.
\]

This is the same quotient-factorization criterion as NPI-1, applied to the latent statistic rather than to unobserved actual identity.

## Theorem NCOR-2B — posterior identifiability through predictive law

Suppose the mapping

\[
\mu\mapsto \sum_z \mu(z)P(\cdot\mid z)
\]

from reachable latent posteriors `mu=P(Z|h)` to registered future-observation laws is injective. Then exact predictive state determines the reachable latent posterior.

If that mapping is non-injective, distinct posteriors can induce the same future law and prediction alone is not forced to distinguish them.

Even under injectivity, predictive state determines the posterior, not necessarily the realized hidden `z`.

## Counterexample class

At an observed history compatible with multiple hidden states, latent-conditioned future distributions may differ while the predictor's correct output is the mixture weighted by the current posterior. No representation can recover the actual hidden state from the observed history when the observation process has not identified it.

---

# 3. Updated allowed claims

Allowed:

```text
predictive training must preserve distinctions between observed histories that change the registered future law
predictive state may determine a latent posterior/statistic when that statistic factors through predictive state
injective posterior-to-predictive-law maps make the posterior identifiable from exact predictive state
```

Disallowed:

```text
prediction generically recovers the true hidden world state
latent-conditioned law differences alone imply actual latent identity is encoded
proxy optimization error + pointwise generalization gap alone upper-bound protected risk without proxy-optimum alignment
```

# 4. Gap impact

This correction strengthens rather than weakens the zero-prior programme:

- neural development must measure proxy alignment in addition to optimization and generalization;
- latent/world-model claims must specify the identifiable posterior/quotient, not anthropomorphize hidden state recovery;
- POMDP belief-state theory is the correct general object under partial observability.

## Claim ceiling

These are algebraic/identifiability corrections. They do not close nonlinear neural optimization, protected generalization or learned latent-state estimation.
