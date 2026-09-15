# Bounded reaction-network carrier and reduction theorem v1

## Native state and operator

A bounded stochastic reaction network is

\[
\mathcal R=(S,B,n,\{(\nu_r,a_r)\}_{r=1}^m,t,\rho),
\]

where \(S\) is a finite species set, \(0\le n_i\le B_i\) are molecule
counts, \(\nu_r\) is an integer stoichiometric displacement, \(a_r(n)\ge0\)
its propensity, \(t\) the clock, and \(\rho\) the readout. Its native CTMC
operator has generator

\[
Q(n,n+\nu_r)=a_r(n),\qquad
Q(n,n)=-\sum_{r:n+\nu_r\ valid}a_r(n).
\]

A firing selects a valid reaction proportionally to propensity, applies
\(n\leftarrow n+\nu_r\), and advances time by the declared waiting-time law.
The state schema is `REACTION_NETWORK_SCHEMA_V1.json`.

## Theorem RN-1 — reduction to stochastic, dynamical, and program parents

The bounded state set has at most \(\prod_i(B_i+1)\) members. Enumerating it and
the valid reactions constructs \(Q\) in
\(O(|X|m)\) propensity/validity evaluations.

- D3 stores the current distribution and applies the Markov kernel/semigroup.
- D6 stores the count state and CTMC/discrete-event transition law.
- D4 stores the finite reaction list and interprets propensity, selection,
  stoichiometric update, clock, and readout instructions.

At rational generator/event-choice scope, the compiler is exact: the off-diagonal
rate for each target is the sum of precisely the source reactions reaching it,
the diagonal is the negative exit rate, and normalized event probabilities are
identical. Induction on event count preserves every state/readout distribution.
Waiting-time samples are exact only if the parent receives the same symbolic-real
or randomness instrument; otherwise precision/error must be declared.

Therefore bounded reaction-network cognition is absorbed by D3/D6/D4 under
matched instruments. Continuous deterministic mass-action flow is directly a
D6 ODE; a bounded-precision numerical realization inherits its discretization
and error bound rather than exact CTMC status.

## Exact certificate

For \(A\rightleftarrows B\) with conserved total \(1\le M\le6\) and both
integer rate constants in \(\{1,2,3\}\), the executable certificate exhausts
54 networks and 243 generator rows. It checks exact rational equality between
native and compiled generators, molecule conservation, zero row sums,
nonnegative off-diagonal rates, and normalized embedded event-choice
probabilities. All violation counts are zero.

## Resource theorem and claim boundary

Logical “one firing” is not a physical cost equivalence. Every comparison must
separately report species/reaction counts, molecule or concentration precision,
rate precision, state preparation, event and random-bit counts, simulation
error, horizon, readout, latency, wall time, physical volume, temperature,
energy, and waste/reset. Parallel molecular reactions, sensing, preparation, and
cleanup cannot be free.

`REACTION_RESOURCE_ACCOUNTING_V1.json` formalizes these coordinates and the
digital construction bound. No speed, energy, or latency advantage follows from
the carrier alone. Unbounded counts, exact real concentrations, and unmatched
physical substrates remain open rather than being declared equivalent.
