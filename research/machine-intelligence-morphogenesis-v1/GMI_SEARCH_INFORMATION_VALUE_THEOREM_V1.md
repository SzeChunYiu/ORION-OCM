# GMI search information-value theorem v1

Status: **FORMAL SEARCH/HEURISTIC LOWER BOUND / GKF-09 NARROWING**

Date: 2026-09-12.

Purpose: replace vague “heuristic quality” with an obligation-relative information quantity that lower-bounds the number of search observations needed to identify a successful candidate.

## 1. Hidden candidate

Let the correct/admissible candidate be random variable `G` over `N` possibilities with prior entropy

\[
H(G).
\]

For the uniform case, `H(G)=\log_2 N`.

A search procedure receives adaptive heuristic/verifier observations `Y_1,...,Y_T` and finally outputs estimate `\hat G`.

## 2. Theorem SI-1 — exact identification information lower bound

If search identifies the correct candidate with zero error, then

\[
H(G\mid Y_{1:T})=0
\]

and therefore

\[
I(G;Y_{1:T})=H(G).
\]

By the chain rule,

\[
I(G;Y_{1:T})
=
\sum_{t=1}^T I(G;Y_t\mid Y_{<t}).
\]

If every registered heuristic/search observation supplies at most `kappa` bits conditionally,

\[
I(G;Y_t\mid Y_{<t})\le\kappa,
\]

then

\[
\boxed{T\ge H(G)/\kappa}.
\]

For a uniform `N`-candidate search space this becomes

\[
T\ge\frac{\log_2 N}{\kappa}.
\]

## 3. Theorem SI-2 — approximate identification / Fano bound

If final error probability is at most `delta`, Fano's inequality gives

\[
H(G\mid Y_{1:T})
\le h_2(\delta)+\delta\log_2(N-1)
\]

for uniform finite `G`. Hence

\[
I(G;Y_{1:T})
\ge
\log_2N-h_2(\delta)-\delta\log_2(N-1).
\]

With per-observation conditional information at most `kappa`,

\[
T\ge
\frac{\log_2N-h_2(\delta)-\delta\log_2(N-1)}{\kappa}.
\]

## 4. Resource consequence

If one heuristic observation costs `c_h` and one candidate expansion/check costs `c_e`, then information rate per priced burden is a relevant zero-prior descriptor:

\[
\eta_h=\frac{I(G;Y_t\mid Y_{<t})}{c_h+c_e}
\]

or its registered expectation/interval.

A heuristic with high raw accuracy but tiny conditional information after previous observations can have low marginal search value. Conversely, a rare decisive test can have high value even if it is not a smooth score.

## 5. Relation to branching

An uninformative exact search over a uniform `b^d` leaf space begins with `d log_2 b` bits of target uncertainty. A sequence of branch decisions that perfectly reveals one base-`b` digit per level provides `log_2 b` bits per decision and meets the information requirement in `d` decisions. If the heuristic reveals less, additional expansions/queries are unavoidable.

This information lower bound does not by itself account for the computational cost of *finding* the informative query or for structural reuse across queries; those belong in lifecycle burden.

## 6. Negative twins

- Heuristic output independent of the target: `kappa=0`; no finite information-based identification guarantee follows.
- Redundant repeated heuristic: high first-step information can be followed by zero conditional information; raw per-query accuracy overstates value.
- Highly nonuniform target prior: use `H(G)`, not `log N`.
- Search with a merely satisfying rather than unique target should quotient candidates by acceptable semantic equivalence before measuring uncertainty.

## GMI consequence

GKF-09 pre-outcome search descriptors should include:

```text
semantic candidate entropy / acceptable quotient
conditional heuristic information gain
information per priced expansion/check
proposal correlation/redundancy
reuse horizon and compile/cache alternative
verifier error and risk constitution
```

## Claim ceiling

This closes an information-theoretic lower bound for heuristic/search value. Estimating conditional information prospectively in large real search spaces and choosing the best heuristic/search policy remain OPEN-BLOCKING.
