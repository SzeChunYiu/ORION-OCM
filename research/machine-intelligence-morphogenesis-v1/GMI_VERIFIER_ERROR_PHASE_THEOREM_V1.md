# GMI verifier error phase theorem v1

Status: **FORMAL VERIFIER RESPONSE LAW / B6 NARROWING**

Date: 2026-09-12.

Purpose: separate proposal quality, verifier false positives and verifier false negatives in admission/verification morphology.

## 1. Registered proposal/checker model

Each independent proposal is semantically correct with probability `p`.

Verifier error rates:

```text
alpha = P(accept | incorrect)   false-positive rate
beta  = P(reject | correct)     false-negative rate
```

Then one proposal is accepted with probability

\[
a=p(1-\beta)+(1-p)\alpha.
\]

## 2. Theorem VE-1 — accepted bad-state risk

Conditioned on admission,

\[
q_{bad}=P(incorrect\mid accept)
=\frac{(1-p)\alpha}{p(1-\beta)+(1-p)\alpha}.
\]

Thus a registered maximum accepted-error risk `r_*` is satisfied iff

\[
(1-p)\alpha\le r_*\,[p(1-\beta)+(1-p)\alpha].
\]

A verifier is not safe merely because its overall accuracy is high; the false-positive channel is weighted by proposal failure prevalence.

## 3. Theorem VE-2 — retry burden under independent proposals

If rejected proposals are independently regenerated until one is accepted, the number of proposal/check cycles is geometric with mean

\[
E[N]=\frac1a.
\]

For generation cost `c_g` and checking cost `c_v`, expected pre-admission compute burden is

\[
\frac{c_g+c_v}{a}.
\]

False negatives therefore increase developmental/serving burden even when they improve neither admitted semantic quality nor false-positive risk.

## 4. Lifecycle comparison to direct admission

Let an incorrect admitted result incur expected protected loss `L_bad`. Under repeated verify-until-admit,

\[
C_{verify}=\frac{c_g+c_v}{a}+q_{bad}L_{bad}.
\]

Under direct one-shot admission,

\[
C_{direct}=c_g+(1-p)L_{bad}.
\]

Verification is lifecycle-favorable in this registered base model iff

\[
\frac{c_g+c_v}{a}+q_{bad}L_{bad}
<
c_g+(1-p)L_{bad}.
\]

A risk constitution may require verification even when this scalar inequality does not favor it; hard admissibility and scalarized cost are separate.

## 5. Dependence caveat

The geometric retry theorem requires independent repeated proposal/check outcomes with stationary rates. Correlated candidate generation, verifier drift, adaptive search and checker-generator coupling invalidate the simple `1/a` law and must be measured separately.

## 6. Negative twins

- `alpha=0,beta=0`: exact checker; admitted risk is zero and retry price is `1/p`.
- high `beta`: safe but potentially unusably expensive admission.
- high `alpha` with low `p`: verifier can admit mostly bad results despite apparently moderate raw accuracy.
- `p=1`: verification cannot improve semantics; it only adds cost unless constitutionally required as evidence.

## 7. Executed finite check

A finite rational grid over proposal quality and verifier error rates checks the accepted-risk identity and equivalent risk-threshold inequality. 320 risk-threshold cells, zero violations.

## Claim ceiling

This closes the stationary independent proposal/checker base law. Proposal correlation, adaptive verifier dependence, real checker scaling and protected transfer remain OPEN-BLOCKING.
