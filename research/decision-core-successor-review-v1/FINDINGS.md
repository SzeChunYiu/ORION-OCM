# Three actionable source findings

Bound to PR154 `c8cc8ed14a1d3d3aaa8c13fc8b68df28f82bf8bd`; by-hand witnesses only.
All three are P2 for the stated mathematical/executable-reference scope.

## F1 — fix the adaptive transcript chain rule

[Formal core 393–410](https://github.com/SzeChunYiu/ORION-OCM/blob/c8cc8ed14a1d3d3aaa8c13fc8b68df28f82bf8bd/research/residual-strategy-regime-v1/FORMAL_DECISION_CORE_V2.md#L393)
asserts `I(Theta; Y_1,...,Y_n | P_1,...,P_n as generated)` equals
`sum_i I(Theta;Y_i | H_{i-1},P_i)`. Ordinary conditioning on the complete
probe sequence includes future probe choices, which can disclose past answers.
The phrase “as generated” does not define an alternative conditioning operation.

**Finite witness:** Theta is a fair bit; P1 is fixed; Y1=Theta;
P2 is the probe label chosen as Y1; Y2 is constant.
The displayed left side is 0 because P2 already determines Theta.
The first right-side term is 1 bit and the second is 0.
This meets the stated adaptive choice rule and directly contradicts the identity.

**Repair:** define `H_i=(H_{i-1},P_i,Y_i)` and require
`I(Theta;P_i | H_{i-1})=0` (no extra target information in probe selection).
Then use `I(Theta;H_n | H_0)=sum_i I(Theta;Y_i | H_{i-1},P_i)`.
Include any initial information and independent randomization in the explicit
history model. The conditional per-probe bound then gives the intended bound
on additional transcript information. No empirical bit bound was checked.

## F2 — approximate transition masses cannot certify exact bisimulation

[decision_core.py 168–197](https://github.com/SzeChunYiu/ORION-OCM/blob/c8cc8ed14a1d3d3aaa8c13fc8b68df28f82bf8bd/research/residual-strategy-regime-v1/decision_core.py#L168)
calls its check exact, but
[211–215](https://github.com/SzeChunYiu/ORION-OCM/blob/c8cc8ed14a1d3d3aaa8c13fc8b68df28f82bf8bd/research/residual-strategy-regime-v1/decision_core.py#L211) uses `isclose` with absolute and relative
`1e-12` tolerances. This differs from the exact equalities in
[Theorem 10, 480–512](https://github.com/SzeChunYiu/ORION-OCM/blob/c8cc8ed14a1d3d3aaa8c13fc8b68df28f82bf8bd/research/residual-strategy-regime-v1/FORMAL_DECISION_CORE_V2.md#L480).

**Valid-kernel witness:** put s,t in one block and u,v in separate blocks;
use the same sole action and immediate contract at s,t.
Let s move to u,v with probabilities `1/2+delta, 1/2-delta`, and t with
`1/2,1/2`, where `delta=2^-42`. These dyadic probabilities sum exactly to 1.
Give u,v distinct protected outputs and deterministic self-loops.
The mass comparison accepts both differences, although the probability of the
next protected u-output differs by delta. Thus an accepted partition need not
satisfy the exact finite-horizon preservation theorem. This witness is derived
from source; it is not an executed test or evidence about a deployed partition.

**Repair:** aggregate exact integer/rational probabilities and compare them
exactly, or expose an approximate relation with a separately proved finite-horizon
error contract. A tolerance alone cannot authorize equality of protected laws.
Interval overlap means unresolved equality, not certified equality.
The author-hosted [Givan–Dean–Greig paper, §3.3 and Theorems 5/7](https://cs.brown.edu/people/tdean/publications/archive/GivanetalAIJ-03.pdf)
uses equality of block masses; this supports the distinction, not a transferred
OCM implementation guarantee.

## F3 — forced floats can change the optimal finite stop decision

[decision_core.py 140–158](https://github.com/SzeChunYiu/ORION-OCM/blob/c8cc8ed14a1d3d3aaa8c13fc8b68df28f82bf8bd/research/residual-strategy-regime-v1/decision_core.py#L140)
casts both stop and cognitive costs to float before comparing them.
The finite-real-cost theorem supplies no representability or separation condition.

**Integer witness:** at s, stopping costs `2^53+1`; the sole computation costs
`2^53` and deterministically reaches t, whose stop cost is 0. Allow one
computation. All costs are finite, nonnegative integers. The mathematical optimum
computes and saves 1. Under binary64 round-to-nearest, `float(2^53+1)=2^53`;
the computed arms tie, so the strict comparison retains STOP. Thus even exact
input integers need not yield the theorem's optimal action. No code was run.

[74–97](https://github.com/SzeChunYiu/ORION-OCM/blob/c8cc8ed14a1d3d3aaa8c13fc8b68df28f82bf8bd/research/residual-strategy-regime-v1/decision_core.py#L74) also initializes feature cost with `0.0`
and clamps a small negative regret. Exact rational inputs therefore do not
provide an exact-output path merely by supplying rationals. The direct
`optimal_actions` equality at lines 40–43 is an improvement over epsilon ties,
but cannot repair upstream rounding or the unchanged historical selector.

**Repair:** preserve exact arithmetic in the reference implementation; otherwise
name approximate outputs and certify action margins and regret intervals before
using exact claims. Keep raw signed residuals. The single dyadic toy regret case
in [test 61–78](https://github.com/SzeChunYiu/ORION-OCM/blob/c8cc8ed14a1d3d3aaa8c13fc8b68df28f82bf8bd/research/residual-strategy-regime-v1/test_decision_core.py#L61) does not exercise this issue.
No claim is made that any frozen cost, collision count, regret, or threshold is
numerically wrong. Theorem 4's algebra can be exact while its computation is not.
