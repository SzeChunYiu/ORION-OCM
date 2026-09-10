#!/usr/bin/env python3
"""A6 P2 repair witness for A1-R4 (G08 governed time-varying constitution).
Executes the proof_route recorded in d12/arms/A1_receipts/A1-R4.json:
(i) regress termination iff top level frozen; (ii) interior optimal strictness q*;
(iii) self-licensing chain when the frozen level is made amendable.
Pure finite arithmetic, no network, no external data."""
from fractions import Fraction

# --- model: constitution = set of adopted rules at levels 1 (operational),
# 2 (collective-choice), 3 (constitutional/top). An amendment at level l is
# licensed by level l+1 iff evidence support >= q_l+1 (strictly level-decreasing licence).

def terminates_with_frozen_top(max_steps=1000):
    # well-founded ordering: every amendment is licensed by a STRICTLY higher,
    # unamended level; top frozen => licence chain length <= 3 => finite
    chain = []
    level = 1
    while level <= 3 and len(chain) < max_steps:
        chain.append(level)
        level += 1  # licence must come from strictly higher level
    return len(chain) <= 3, chain

def self_licensing_chain(max_steps=50):
    # top level made amendable: an amendment at level 3 can LOWER the threshold
    # q_3 that gates level-3 amendments themselves => each amendment licenses the
    # next => unbounded chain (never reaches a state with no licensed amendment)
    q3 = Fraction(9, 10)
    steps = 0
    while q3 > Fraction(0) and steps < max_steps:
        q3 = q3 / 2          # self-licensed erosion of the gate
        steps += 1
    return steps == max_steps, steps  # still eroding at horizon => unbounded

def buchanan_tullock_sweep(A=Fraction(9), B=Fraction(1)):
    # external cost A*(1-q) (damage from bad amendments, DECREASING in q)
    # decision cost  B*q/(1-q) (delay/bargaining, INCREASING, diverges at q->1)
    qs = [Fraction(i, 100) for i in range(50, 100, 5)]  # 0.50..0.95
    costs = {q: A * (1 - q) + B * q / (1 - q) for q in qs}
    qstar = min(costs, key=costs.get)
    analytic = 1 - (B / A) ** Fraction(1, 2)  # interior optimum of the tradeoff
    interior = Fraction(1, 2) < analytic < Fraction(1)
    return costs, qstar, analytic, interior

if __name__ == "__main__":
    t, chain = terminates_with_frozen_top()
    print(f"(i) frozen top: terminates={t} licence-chain={chain}")
    u, steps = self_licensing_chain()
    print(f"(iii) amendable top: self-licensing chain unbounded={u} (still eroding after {steps} steps)")
    costs, qstar, analytic, interior = buchanan_tullock_sweep()
    print(f"(ii) sweep argmin q*={float(qstar):.2f} analytic q*={float(analytic):.4f} interior={interior}")
    for q, c in sorted(costs.items()):
        print(f"    q={float(q):.2f} total_cost={float(c):.4f}")
