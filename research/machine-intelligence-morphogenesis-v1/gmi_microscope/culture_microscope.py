"""I9: an exact cumulative-culture microscope.

Closes four boxes at once: the ratchet-vs-loss condition, division of cognitive labour,
when collective culture exceeds any individual's rediscovery budget, and the microscope
itself.

Deterministic recursion over expected counts -- no sampling, so every number is exact.

Population: n agents per generation, each with capacity K retained skills and per-generation
budget B. Skill pool M, derivation cost C, transmission cost U, transmission fidelity p
(the fraction of learners who successfully acquire a demonstrated skill).

Each generation the incoming cohort:
  * acquires by transmission: each skill currently held is passed to p*n learners, but each
    agent can hold at most K, so the population retains min(held, n*K) skill-slots;
  * derives afresh whatever budget remains allows: floor(B/C) new skills per agent.
"""
import json, math

def run(G, n, K, M, C, U, p, B):
    held = 0.0            # distinct skills alive in the population
    hist = []
    for g in range(G):
        # transmission: a skill survives into the next cohort if at least one learner gets it
        surviving = held * (1 - (1 - p) ** n)
        # capacity ceiling: the cohort can carry at most n*K skill-slots, distinct <= M
        capacity = min(n * K, M)
        surviving = min(surviving, capacity)
        # derivation with leftover budget, after paying U per transmitted skill per agent
        spent_on_transmission = min(surviving, K) * U
        left = max(0.0, B - spent_on_transmission)
        new = min(math.floor(left / C), max(0, M - surviving))
        held = min(surviving + new, capacity)
        hist.append(round(held, 3))
    return held, hist

M, C, U, B, K, G = 40, 6, 1, 12, 8, 12

print("(a) RATCHET vs LOSS -- sweep transmission fidelity p, n = 5 agents")
print("  %-6s %-46s %s" % ("p", "skills held by generation", "outcome"))
rows_a = []
for p in (0.05, 0.15, 0.3, 0.6, 0.95):
    fin, hist = run(G, 5, K, M, C, U, p, B)
    outcome = "RATCHET" if hist[-1] > hist[0] else ("steady" if abs(hist[-1] - hist[0]) < 1e-9 else "LOSS")
    rows_a.append({"p": p, "hist": hist, "final": fin, "outcome": outcome})
    print("  %-6s %-46s %s" % (p, hist[:8], outcome))

print("\n(b) DIVISION OF COGNITIVE LABOUR -- population vs the best individual")
print("  %-6s %-12s %-16s %-16s %s" % ("n", "capacity nK", "population holds", "individual holds", "collective > individual?"))
rows_b = []
for n in (1, 2, 5, 10):
    fin, _ = run(G, n, K, M, C, U, 0.6, B)
    indiv = min(K, fin)
    rows_b.append({"n": n, "nK": n * K, "population": round(fin, 2), "individual": indiv,
                   "exceeds": fin > indiv})
    print("  %-6d %-12d %-16.2f %-16d %s" % (n, n * K, fin, indiv, fin > indiv))

print("\n(c) COLLECTIVE CULTURE vs ONE AGENT'S LIFETIME REDISCOVERY BUDGET")
lifetime = G * math.floor(B / C)
print("  one agent deriving alone for %d generations at budget %d, cost %d -> %d skills" % (G, B, C, lifetime))
rows_c = []
for n in (1, 2, 5, 10):
    fin, _ = run(G, n, K, M, C, U, 0.6, B)
    rows_c.append({"n": n, "culture": round(fin, 2), "lifetime_solo": lifetime, "exceeds": fin > lifetime})
    print("  n=%-3d culture holds %-8.2f vs solo %-4d -> exceeds: %s" % (n, fin, lifetime, fin > lifetime))

json.dump({"schema": "CumulativeCultureMicroscopeV1",
           "params": {"M": M, "C": C, "U": U, "B": B, "K": K, "G": G},
           "ratchet": rows_a, "division_of_labour": rows_b, "collective_vs_solo": rows_c},
          open("microscopes/results/STAGE_CULTURE_MICROSCOPE_V1.json", "w"), indent=1, sort_keys=True)
print("\nwritten")
