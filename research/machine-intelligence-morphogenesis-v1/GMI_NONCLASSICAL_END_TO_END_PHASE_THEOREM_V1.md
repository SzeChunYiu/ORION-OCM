# GMI nonclassical end-to-end phase theorem v1

Status: **FORMAL ACCOUNTING LAW / T10 NARROWING**

Date: 2026-09-12.

Purpose: prevent physical/analog/quantum core-compute speedups from being promoted to intelligence-domain advantages before input, precision, reliability and readout are charged.

## 1. Matched semantic obligation

Compare a candidate carrier `Q` with strongest parent `P` on the same registered semantic/risk contract. Decompose candidate burden as

\[
C_Q=C_{encode}+C_{native}+C_{precision}+C_{reliability}+C_{decode}+C_{verify}.
\]

Parent burden `C_P` must include the analogous necessary costs under the same lifecycle price vector.

## 2. Theorem NC-1 — end-to-end advantage criterion

A native-core advantage is scientifically relevant only if

\[
C_Q<C_P.
\]

Equivalently, if the native core saves

\[
S=C_{native,P}-C_{native,Q},
\]

then the candidate wins only when

\[
S>
\Delta C_{encode}+\Delta C_{precision}+\Delta C_{reliability}+\Delta C_{decode}+\Delta C_{verify}.
\]

This is algebraically trivial but epistemically essential: an unpriced transduction or precision channel is not a domain separation.

## 3. Theorem NC-2 — stochastic reliability amplification cost

Suppose one independent native trial returns the correct binary decision with probability

\[
\frac12+\gamma,
\qquad \gamma>0.
\]

By Hoeffding, majority vote over `m` independent trials has error at most

\[
\exp(-2m\gamma^2).
\]

Thus error at most `delta` requires

\[
m\ge \frac{\log(1/\delta)}{2\gamma^2}.
\]

Any claimed native latency/energy must be multiplied by the reliability repetitions actually required by the protected risk constitution.

## 4. Theorem NC-3 — shot/sample readout scaling

For a bounded observable `X in [a,b]`, estimating its expectation to additive error `epsilon` with failure probability at most `delta` from independent samples requires, by Hoeffding sufficiency,

\[
m\ge\frac{(b-a)^2}{2\epsilon^2}\log\frac{2}{\delta}.
\]

Therefore a representation with a large hidden state space does not make all of that information freely readable. Measurement/sample complexity is part of serving burden.

## 5. Precision gate

If a physical state coordinate spans a bounded range `W` and must distinguish `M` semantic values robustly with minimum spacing, required precision scales at least with the packing density. Existing `GMI_PHYSICAL_CARRIER_PRECISION_THEOREMS_V1.md` supplies the finite packing bound; arbitrary information cannot be hidden in an uncharged real number.

## 6. Input/output gate

When arbitrary classical input of size `n` must be encoded into the candidate substrate, any assumption that input preparation is `O(1)` must be explicitly registered and justified. Otherwise the end-to-end comparison must charge the actual data movement/preparation interface. The same applies to extracting an `n`-bit classical answer.

## 7. GMI consequence

Nonclassical/physical capability envelopes must expose at least:

```text
native compute burden
input/state preparation
precision and calibration
noise/repetition/error correction
measurement/readout
verification
energy and wall clock
strongest matched classical parent
```

## Claim ceiling

This closes the accounting structure and reliability/sample base laws. It does not establish or refute a practical quantum/analog/molecular advantage on any real intelligence workload; T10 remains empirically OPEN-BLOCKING.
