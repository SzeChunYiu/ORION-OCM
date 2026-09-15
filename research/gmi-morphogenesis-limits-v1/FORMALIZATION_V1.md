# H morphogenesis regimes and finite-state limits v1

## Expansion law

For horizon `H`, retaining the current morphology incurs `H L_current`. Expanding incurs one-time cost `X` plus per-task expanded residual loss `L_expanded` and added maintenance `M_expanded`:

`C_expand = X + H(L_expanded + M_expanded)`.

Expand iff `C_expand < H L_current`; equality is a tie. This makes expansion a lifecycle decision, not an automatic response to any present deficit.

## Pruning law

Keeping old structure incurs

`C_keep = H(M_old + L_keep)`.

Pruning incurs

`C_prune = P + H L_post`.

Prune iff `C_prune < C_keep`. Thus non-load-bearing old structure can become worth removing after maintenance amortizes the prune transition, while load-bearing structure can rationally remain even when it is costly to maintain.

## Self-compilation law

For reuse count `N`, interpreted execution costs `N i`. Self-compilation costs build/compile `B` plus compiled per-use cost `c` and verification `v`:

`C_compile = B + N(c+v)`.

Self-compilation is favored exactly when `B + N(c+v) < N i`. Verification is load-bearing; ignoring it can manufacture a false compilation regime.

## Local morphogenesis law

Let global rebuild cost `G`. A local patch costs `P`, local verification `V`, and leaves residual per-task loss `L`. The local total is

`C_local = P + V + H L`.

Local morphogenesis may enter the comparison only when the patch is obligation-sufficient. Conditional on sufficiency, choose local iff `C_local < G`. A cheap but semantically insufficient patch is the negative twin and must not be admitted.

## Multi-generation recurrence

The registered bounded microscope uses

`b_{g+1} = max(0, b_g - s) + m`,

where `b_g` is developmental/search burden, `s` inherited burden reduction and `m` maintenance burden. This is not asserted as a universal inheritance law; it is an exact finite trajectory object for distinguishing regimes.

Example: `b_0=10`, `s=3`, `m=1` gives

`10, 8, 6, 4, 2, 1, 1`.

When `m>s`, burden can grow rather than improve across generations; for example `b_0=2`, `s=1`, `m=3` yields `2,4,6,8`. Multi-generation development therefore does not imply monotone improvement.

## Finite deterministic open-endedness impossibility theorem

Let `X` be a finite developmental state set with `|X|=n` and deterministic closed transition `F:X->X`. Starting from any `x_0`, consider `x_0,x_1,...` with `x_{t+1}=F(x_t)`.

Among the first `n+1` visited states, two must be equal by the pigeonhole principle. If `x_i=x_j` for `i<j`, determinism implies `x_{i+k}=x_{j+k}` for every `k>=0`. Hence the trajectory is eventually periodic, with prefix length `i` and cycle length `j-i`.

Therefore a fixed finite deterministic developmental system cannot produce infinitely many distinct developmental states or morphologies. Any claim of open-ended distinct-state growth must break at least one premise: allow the state space to grow, admit stochastic/external novelty, or change the transition law/state definition.

The executable suite exhausts every deterministic map and every start state for `n=1,2,3,4`: `1 + 8 + 81 + 1024 = 1,114` start-map certificates. No trajectory visits more than `n` distinct states before repeating.

## Additional exhaustive lifecycle control

The expansion decision is independently exhausted over 768 small integer lifecycle tuples. Every executable verdict equals direct charged-cost comparison.

## Claim boundary

These are bounded finite G2 laws. They do not establish empirical G7 developmental prediction or open-ended evolution. In particular, the finite-state impossibility theorem is a boundary result, not evidence that systems with expanding state spaces are open-ended.
