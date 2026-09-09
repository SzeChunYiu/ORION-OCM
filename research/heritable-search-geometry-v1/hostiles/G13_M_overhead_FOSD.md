# Hostile — G13: R2 net-dominance fails under acquisition overhead M > 0

Atom: G13 (A_t ⊆ A_{t+1} + M overhead). Rung: R2. Verdict: LIFT_FAILS.
Assumption removed: viii (M = 0).

## Claim under attack
The available-strategy sets grow, A_t ⊆ A_{t+1}; claim: the strategy-value
distributions μ_t are first-order stochastically ordered, μ_{t+1} FOSD μ_t,
even when per-step overhead M > 0 is charged (viii removed).

## Minimal counterexample
World: deterministic single-criterion scores; archive value = value of the best
available strategy minus accumulated overhead.

- t = 1: A_1 = {s1}, gross value v(s1) = 10. Overhead charged so far: 0.
  Net value V_1 = 10. μ_1 = δ_10.
- t = 2: A_2 = A_1 ∪ {s2} ⊇ A_1 (growth holds), v(s2) = 10 + ε with 0 < ε < M
  (e.g. ε = 1, M = 2). Step-2 overhead M charged at the step.
  Net value V_2 = max(10, 10+ε) − M = 10 + ε − M < 10. μ_2 = δ_{10+ε−M}.

FOSD of μ_2 over μ_1 requires ℙ_2(X ≥ v) ≥ ℙ_1(X ≥ v) for every v. Take
v = 10 − δ, δ ∈ (0, M − ε): ℙ_1(X ≥ v) = 1, ℙ_2(X ≥ v) = 0. Violated.

The gross half survives: distributions of *un-overheaded* values are FOSD-
ordered (growing support, same incumbent), parent FOSD — but the atom's
statement includes the overhead, and net ordering is what burden B cares about.

## Rescue condition (named, not asserted as holding)
Net FOSD is restored when acquisition is voluntary and the acceptance rule
takes an option only when gross gain ≥ M (myopic suffices one step;
intertemporal acceptance adds option value and only helps). Dominance is then a
property of an acceptance *policy*, not of the growth law A_t ⊆ A_{t+1}. Any
statement keeping the bare growth law as the dominance premise is false.

## Propagation note
Any HST theorem consuming "monotone strategy availability ⇒ monotone net
value" inherits this counterexample whenever M > 0 (lanes F/G check consumers).
