# GMI adaptive verifier bounds v2

Status: **FORMAL DEPENDENCE-ROBUST VERIFIER LAW / B6 NARROWING**

Date: 2026-09-12.

Purpose: extend the iid verifier phase theorem to adaptive proposal/check sequences whose quality can depend on all previous rejections.

## 1. Adaptive attempt process

At attempt `t`, let `H_{t-1}` be the complete previous search/check history, `C_t` indicate proposal correctness, and `A_t` indicate verifier acceptance.

Define conditional quantities

\[
p_t=P(C_t=1\mid H_{t-1}),
\]

\[
\alpha_t=P(A_t=1\mid C_t=0,H_{t-1}),
\]

\[
\beta_t=P(A_t=0\mid C_t=1,H_{t-1}).
\]

No independence or stationarity across attempts is assumed.

Assume prospectively justified uniform bounds while the process has not yet stopped:

\[
p_t\ge p_{min}>0,
\qquad
\alpha_t\le\alpha_{max},
\qquad
\beta_t\le\beta_{max}<1.
\]

## 2. Theorem AV-1 — adaptive stopping-time tail bound

Conditional acceptance probability at attempt `t` is

\[
a_t=p_t(1-\beta_t)+(1-p_t)\alpha_t
\ge p_{min}(1-\beta_{max})=:a_{min}.
\]

Let `T` be the first accepted attempt. By iterated conditioning,

\[
P(T>n)
\le (1-a_{min})^n.
\]

Therefore

\[
E[T]\le \frac1{a_{min}}.
\]

The proof does not require independent proposals; only the conditional lower bound must remain valid after every possible history.

## 3. Theorem AV-2 — adaptive accepted-error bound

At any still-live attempt,

\[
P(C_t=0,A_t=1\mid H_{t-1})
=(1-p_t)\alpha_t
\le (1-p_{min})\alpha_{max}=:b_{max}.
\]

The conditional bad fraction among accepted proposals at that attempt is at most

\[
q_{max}
=
\min\left(1,
\frac{(1-p_{min})\alpha_{max}}
{p_{min}(1-\beta_{max})}
\right).
\]

The eventual first accepted result is a mixture over stopping times of those conditional accepted distributions, so

\[
P(C_T=0)\le q_{max}.
\]

A tighter bound is available whenever a stronger lower bound on total `a_t` includes measured false-positive mass.

## 4. Lifecycle bound

If per-attempt proposal+check burden is bounded above by `c_max`, then

\[
E[C_{pre-admit}]\le \frac{c_{max}}{a_{min}}.
\]

If cost varies with history, the corresponding predictable conditional cost bound can replace `c_max` and be accumulated by optional-stopping/supermartingale tools when their assumptions are registered.

## 5. Negative twins

- If adaptive search can enter a history where `p_t -> 0`, no finite restart/admission guarantee follows from this theorem.
- If verifier false-positive rate can spike after adversarial generator adaptation, a global raw average `alpha` is insufficient.
- If the verifier and proposal share hidden correlated failure modes not covered by the conditional bounds, the guarantee is invalid.

## 6. GMI consequence

Verification morphology should report **history-conditional lower/upper envelopes**, not only aggregate accuracy:

```text
proposal quality floor p_min
false-positive ceiling alpha_max
false-negative ceiling beta_max
accepted-risk constitution
search/check stopping burden
conditions under which the envelopes remain valid
```

## Claim ceiling

This closes an adaptive dependence-robust upper-bound law. Estimating valid conditional envelopes under real generator/verifier co-adaptation and distribution shift remains OPEN-BLOCKING.
