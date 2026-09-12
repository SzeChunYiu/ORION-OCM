# GMI generalization certificate envelope v1

Status: **FORMAL GENERALIZATION-MECHANISM SELECTION LAW / T2 NARROWING**

Date: 2026-09-12.

Purpose: avoid requiring GMI to guess one universal explanation of generalization when several rigorously valid mechanisms can coexist.

## Theorem GC-1 — simultaneous certificate envelope

Let `R` be protected population risk of one developed predictor. Before protected evaluation, register `K` certificate procedures. Procedure `k` returns an upper bound `U_k(D,delta_k)` and satisfies

\[
Pr\{R>U_k(D,\delta_k)\}\le \delta_k
\]

under its explicitly registered assumptions.

Then, by the union bound,

\[
Pr\left\{R\le \min_{k\le K}U_k(D,\delta_k)\right\}
\ge 1-\sum_k\delta_k.
\]

In particular, setting `delta_k=delta/K` gives an overall `1-delta` certificate while allowing the tightest valid mechanism-specific bound to be selected after the bounds are computed.

## Interpretation

The registered certificate portfolio may include, when their assumptions apply:

```text
finite/description-complexity bounds
algorithmic stability bounds
margin/norm bounds
PAC-Bayes bounds
spectral/effective-dimension bounds
feature/source-alignment bounds
compression/prequential bounds
```

GMI need not assert that the smallest bound is the metaphysical cause of generalization. It predicts protected risk through the tightest simultaneously valid certificate available in the registered regime.

## Assumption gate

A certificate is admissible only if its assumptions are frozen and satisfied without using protected outcomes to retrofit them. Data-dependent assumption tests require their own error budget or an independent split. A vacuous certificate remains valid but scientifically uninformative.

## Negative twin / no-free-selector result

If no registered certificate is valid/nonvacuous in a regime, the envelope gives no guarantee. The theorem does not manufacture a distribution-free modern deep-learning bound. It turns mechanism selection into an auditable certification problem rather than a forced single-mechanism theory.

## GMI consequence

For GKF-03, the pre-outcome response object becomes

\[
U_{GMI}(D)=\min_{k\in\mathcal A(D)}U_k(D,\delta_k),
\]

where `A(D)` is the set of certificates whose registered assumptions pass independently. Held-family calibration must test coverage and sharpness, not just rank models by training loss.

## Claim ceiling

This closes a logical mechanism-selection gap. It does not establish that any existing certificate is tight for modern nonlinear neural networks; protected coverage/sharpness remains OPEN-BLOCKING.
