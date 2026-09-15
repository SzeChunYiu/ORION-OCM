# H developmental amortization laws v1

## Common lifecycle theorem

For a fixed future horizon of `H >= 1` tasks, let reset pay per-task cost `c0`, while continued development pays fixed maintenance/revision `M` plus per-task cost `c1`:

`C_reset(H) = H c0`

`C_continue(H) = M + H c1`.

Define per-task saving `Delta = c0 - c1`.

Then:

- continued development strictly wins iff `H Delta > M`;
- reset strictly wins iff `H Delta < M`;
- equality gives a tie.

If `Delta > 0`, the smallest integer horizon with a strict continue win is

`H* = floor(M / Delta) + 1`.

If `Delta <= 0`, no finite horizon yields a strict continued-development win under this fixed-cost model.

The test suite exhaustively checks this verdict over 2,376 small integer `(H,c0,c1,M)` combinations.

## Learned representation acquisition law

Suppose raw future acquisition requires distinguishing `R` cases. A previously learned obligation-preserving representation reduces these to `Q` quotient classes and incurs charged per-task representation-use cost `u`.

`c0 = R`, `c1 = Q + u`.

Thus future acquisition is cheaper exactly when

`Q + u < R`,

with per-task saving `Delta_rep = R - Q - u`.

The word obligation-preserving is load-bearing: arbitrary compression that aliases future distinctions does not satisfy the premise.

## Learned operator search law

Let baseline future search require `B` candidate expansions. A learned operator/macro reduces this to `L` expansions but each use incurs verification cost `v`.

`c0 = B`, `c1 = L + v`.

The learned operator makes future search cheaper exactly when

`L + v < B`.

A raw expansion saving that is fully consumed by verification (`L+v=B`) is the registered negative twin.

## Learned search-prior discovery law

For a finite prospectively fixed candidate ordering, let the target morphology have baseline rank `r0`. A learned search prior moves it to rank `r1` and costs `p` to evaluate/apply.

`c0 = r0`, `c1 = r1 + p`.

The prior improves future discovery exactly when

`r1 + p < r0`.

A prior that misranks the target or costs more than its rank saving is harmful at this scope.

## Maintenance/revision reversal and reset decision

Each asset-specific per-task law plugs directly into the common lifecycle theorem. Positive per-task saving is necessary but not sufficient for a finite horizon: fixed maintenance/revision must also be amortized.

Example: `c0=8`, `c1=5`, `M=9` gives `Delta=3`. At `H=2`, reset costs 16 and continued costs 19, so reset wins. At `H=3`, both cost 24. At `H=4`, reset costs 32 and continued costs 29, so continued development wins. The exact strict break-even is `floor(9/3)+1=4`.

This gives an explicit answer to when maintenance/revision reverses inheritance benefit and when reset should beat continued development under the registered fixed-horizon assumptions.

## Scope

These are exact finite amortization laws at **G2**. They do not claim that real future-task costs are stationary, that representation/operator/prior quality is known prospectively in open domains, or that continued development is globally preferable. Architecture expansion/pruning, self-compilation, local morphogenesis, multi-generation trajectories, and finite/open-endedness limits remain separate H obligations.
