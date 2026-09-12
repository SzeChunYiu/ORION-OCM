# GMI prequential compression estimator v1

Status: **FORMAL PORTFOLIO ESTIMATOR / GKF-01, GKF-08 NARROWING**

Date: 2026-09-12.

Purpose: replace an unobservable statement such as “the target is compressible” with a prospective, grammar-relative semantic code that can be evaluated without using future protected outcomes to choose the grammar.

## 1. Frozen semantic model portfolio

Before protected evaluation, register probabilistic semantic models

\[
P_1(D),\ldots,P_M(D)
\]

and prior weights `w_j>0`, `sum_j w_j=1`. A model may be a coefficient family, tree/program grammar, memory model, latent model, residual model, or other admissible semantics-preserving predictor. Model search/training cost is accounted separately in the lifecycle meter.

Define the frozen mixture

\[
P_{mix}(D)=\sum_j w_jP_j(D)
\]

and code length

\[
L_{mix}(D)=-\log P_{mix}(D).
\]

## 2. Theorem PC-1 — exact portfolio oracle inequality

For every dataset/semantic sequence `D` and every registered model `j`,

\[
L_{mix}(D)\le -\log P_j(D)-\log w_j.
\]

Therefore

\[
L_{mix}(D)\le \min_j\{L_j(D)-\log w_j\}.
\]

### Proof

`P_mix(D)>=w_jP_j(D)` for every `j`. Apply `-log`, then minimize. QED.

The prior penalty prevents adding an unlimited number of models for free.

## 3. Sequential/prequential interpretation

If the portfolio is updated by Bayes/exponential weighting using only the past, the cumulative one-step predictive log loss equals the negative log marginal mixture probability. Thus the same inequality gives a genuinely prospective code: each next semantic observation is predicted before it is revealed.

Define the bit-valued semantic compression estimator

\[
\widehat K_{preq}(D)=L_{mix}(D)/\log 2.
\]

Compare it with a frozen explicit-record/null code `L_mem(D)` and all lifecycle costs. A shared-law realization has evidence for compression only when its prospective code saving survives model-prior, search, update, verification and serving burden.

## 4. Expected semantic meaning

If the protected source is `P*`, expected log loss satisfies

\[
E_{P*}[-\log Q(D)] = H(P*) + KL(P*\|Q)
\]

for a fixed admissible distribution `Q`. Therefore excess prequential log loss estimates model mismatch under log-loss semantics rather than merely parameter count.

This is a noisy/approximate analogue of the finite exact family-count laws already in GMI.

## 5. Negative twins and kill conditions

1. **Independent random labels:** a frozen small grammar portfolio should show no stable code saving over an appropriately charged record/null code except finite-sample fluctuation.
2. **World-ID leakage:** any model receiving a protected family identifier invalidates the estimator.
3. **Portfolio chosen after protected outcomes:** invalidates prospective status.
4. **Uncharged grammar expansion:** invalidates comparisons; each extra language/model must pay prior/search/description cost.
5. **Semantic mismatch:** lower code length is irrelevant if the model violates the registered target/verifier contract.

## 6. What this closes

This supplies a measurable, assumption-indexed pre-outcome quantity for GKF-01 and part of GKF-08:

```text
prospective semantic code length
portfolio-relative compressibility
residual code saving
uncertainty through predictive probability
```

It does not prove that the portfolio contains the best unknown representation. Grammar expansion remains part of B3/B5.

## 7. Executed finite calibration

`run_gmi_prequential_compression_v1.py` checks the oracle inequality for all binary sequences of lengths 1 through 12 against five frozen Bernoulli source models. Receipt: `GMI_PREQUENTIAL_COMPRESSION_RECEIPT_V1.json`.

Executed total: 8,190 complete sequences; zero violations.

## 8. Claim ceiling

This establishes a portfolio-relative prospective compression estimator and exact oracle inequality. It is not a real high-dimensional semantic-complexity estimator, does not solve representation discovery, and does not establish coefficient/memory crossover on protected real families.
