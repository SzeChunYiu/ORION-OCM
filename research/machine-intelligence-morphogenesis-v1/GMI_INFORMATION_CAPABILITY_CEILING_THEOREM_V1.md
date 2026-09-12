# GMI information capability-ceiling theorem v1

Status: **FORMAL WEAK/NARROW-CARRIER CAPABILITY LOWER BOUND**

Date: 2026-09-12.

Purpose: prove when an intelligence carrier/species has an obligation-relative performance ceiling that cannot be removed by more downstream computation unless additional semantic information/state capacity is supplied.

## 1. Protected semantic identification obligation

Let target semantic class `S` take `N>=2` values. A machine develops/receives internal state `Z` and must output estimate `\hat S=g(Z)`.

Let protected classification error be

\[
P_e=P(\hat S\ne S).
\]

## 2. Theorem CC-1 — Fano capability ceiling

Fano's inequality gives

\[
H(S\mid Z)
\le h_2(P_e)+P_e\log_2(N-1).
\]

Since

\[
I(S;Z)=H(S)-H(S\mid Z),
\]

any representation satisfying

\[
I(S;Z)\le C
\]

must obey the implicit lower bound

\[
H(S)-C
\le h_2(P_e)+P_e\log_2(N-1).
\]

For uniform `S`, using `h_2(P_e)<=1`,

\[
\boxed{
P_e\ge
\frac{\log_2N-C-1}{\log_2(N-1)}
}
\]

whenever the right side is positive.

Thus if the native carrier, communication interface or retained developmental state conveys less than the required semantic information, protected error has a hard floor even with unlimited computation after `Z` is fixed.

## 3. Finite-state corollary

If the machine has at most `M` reliably distinguishable internal states available to this obligation, then

\[
I(S;Z)\le H(Z)\le\log_2M.
\]

Substitute `C=log_2M` into the bound.

This is the approximate/noisy companion to the exact quotient cardinality theorem.

## 4. Conditional side-information version

If side information `X` is freely available to the decoder, replace the required information by conditional uncertainty. The general Fano relation applies to `H(S|X)` and residual information `I(S;Z|X)`.

This connects directly to residual memory/adapters:

```text
broad core/side information X
remaining target uncertainty H(S|X)
residual carrier Z
error floor if residual information is insufficient
```

## 5. Developmental-potential consequence

Suppose every state reachable within priced development budget `B` satisfies

\[
I(S;Z_B)\le C(B).
\]

If the serious-intelligence constitution demands error below a threshold that violates the Fano lower bound at `C(B)`, then that budget is provably insufficient.

If `sup_B C(B)` remains below the required information level for all finite legal budgets of a fixed morphology, then that morphology's critical developmental burden is infinite at the registered obligation scope unless morphology changes or new information channels are added.

## 6. Weak domain versus useful organ

A carrier can have a severe standalone ceiling on a broad `S` while still have high complementarity in a composite species if it cheaply provides a small but decisive residual distinction. Capability ceiling and module value are different objects.

This formalizes why narrow theorem provers, verifiers, databases or exact controllers should not be filtered merely because they fail broad standalone obligations.

## 7. Negative twins

- If additional development expands `C(B)`, the ceiling moves; this is not an asymptotic claim without a capacity-growth law.
- If the target distribution is highly nonuniform, use actual `H(S)`/conditional Fano rather than `log N`.
- If the task accepts many equivalent answers, quotient the target first; counting surface labels overstates required information.
- High information capacity is necessary, not sufficient: search/optimization/serving burden can still prevent intelligence.

## Claim ceiling

This proves an obligation-relative information ceiling, not a universal scalar intelligence threshold or a universal ranking of domains.
