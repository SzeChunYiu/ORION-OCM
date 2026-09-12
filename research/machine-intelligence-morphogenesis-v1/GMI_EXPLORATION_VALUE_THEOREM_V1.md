# GMI Exploration Value Theorem v1

Status: **FORMAL BAYES-ADAPTIVE CONTROL BASE LAW / R6**

Date: 2026-09-12.

Let hidden world state `Theta` have current belief `b`. A one-shot information-gathering action `e` produces observation `S`, costs `c_e`, and is followed by the best exploitation action.

Let exploitation utility be `u(a,Theta)`.

Without exploration,
\[
V_0(b)=\max_a E_b[u(a,\Theta)].
\]

After experiment `e`,
\[
V_e(b)=E_{S\sim b,e}
\left[
\max_a E[u(a,\Theta)\mid S]
\right]-c_e.
\]

## EV-1 — exact value-of-information criterion

Experiment `e` is optimal over immediate exploitation iff
\[
\boxed{
\operatorname{VoI}_e(b)
=
E_S[\max_a E(u\mid S)]
-
\max_a E(u)
-
c_e
>0.
}
\]

Before charging cost,
\[
E_S[\max_a E(u\mid S)]
\ge
\max_a E(u)
\]
by convexity of the maximum / conditioning, so the gross value of information is nonnegative.

This is the exact missing base law behind “exploration value”.

## EV-2 — binary diagnostic microscope

For `Theta in {0,1}`, reward `1` for choosing the matching action and `0` otherwise, prior `p=P(Theta=1)`, and a symmetric probe that reports the correct state with probability `q`, the post-probe expected exploitation success is

\[
\sum_s \max_\theta P(\Theta=\theta,S=s).
\]

Exploration is selected exactly when this improvement exceeds probe cost.

An exhaustive rational grid of 324 `(p,q,c)` cells gives 100 strict explore cells, 45 exact ties, and 179 immediate-exploit cells.

## GMI consequence

The control demand signature needs at least:

```text
current belief / uncertainty
decision-loss asymmetry
informativeness of legal probes
probe cost/risk
future reuse horizon of acquired information
model-update burden
```

A morphology that performs exploration is not justified by uncertainty alone; it is justified when the **decision value of information** exceeds its lifecycle cost.

## Claim ceiling

This is a one-step Bayes-adaptive base law. Multi-step exploration, unknown observation models, representation learning and real POMDP control remain open.
