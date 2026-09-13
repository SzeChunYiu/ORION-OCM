"""Items 18 and 19: teaching, imitation and cultural accumulation as reuse ACROSS AGENTS.

Claim under test: the same break-even that governs reuse within one agent across time
(PVR-3) governs transmission across agents, with the population as the reuse count.

  fresh   = n * C                      every agent derives the skill alone
  taught  = C + S + (n-1) * U          one derives, pays S to transmit, each other absorbs at U

which is PVR-3 verbatim with r = n. If that is right, teaching pays exactly when
n > 1 + S/(C-U), never when U >= C, and imitation is the S -> 0 special case.

Extends to generations: a retained skill serves later cohorts at U as well, so with G
generations of n agents the reuse count is G*n.

Complete enumeration; no sampling.
"""
import json

def taught(n, C, S, U, G=1):
    return C + S + (G * n - 1) * U

def fresh(n, C, G=1):
    return G * n * C

def threshold(C, S, U):
    return None if U >= C else 1 + S / (C - U)

print("=== 1. teaching break-even is PVR-3 with r = population")
print("  C   S   U   threshold n   first n where taught<fresh   match?")
ok = True
for C, S, U in ((10, 3, 1), (10, 12, 1), (6, 3, 2), (5, 1, 5), (8, 0, 2), (20, 30, 4)):
    thr = threshold(C, S, U)
    first = next((n for n in range(1, 2000) if taught(n, C, S, U) < fresh(n, C)), None)
    pred = None if thr is None else int(thr) + 1
    agree = (first == pred)
    ok = ok and agree
    print("  %-3d %-3d %-3d %-13s %-27s %s" % (C, S, U, "never" if thr is None else round(thr, 3),
                                               first, agree))
print(f"  all cells agree with the closed form: {ok}")

print("\n=== 2. imitation is the zero-sender-cost case (S -> 0)")
for C, U in ((10, 1), (10, 5), (10, 9), (10, 10)):
    thr = threshold(C, 0, U)
    print("  C=%-3d U=%-3d  threshold n = %s" % (C, U, "never" if thr is None else round(thr, 3)))
print("  with S = 0 the threshold collapses to n > 1: imitation pays from the SECOND learner,")
print("  whenever observing is cheaper than deriving.")

print("\n=== 3. cultural accumulation: saving grows without bound in generations")
C, S, U, n = 10, 3, 1, 4
rows = []
for G in (1, 2, 5, 10, 50, 100):
    f, t = fresh(n, C, G), taught(n, C, S, U, G)
    rows.append({"G": G, "fresh": f, "taught": t, "saving": f - t, "ratio": round(f / t, 2)})
    print("  G=%-4d fresh=%-6d taught=%-5d saving=%-6d ratio=%.2f" % (G, f, t, f - t, f / t))
print("  per-agent cost tends to U, so the population's amortised cost -> the invocation cost,")
print("  independent of C. That is the accumulation claim, and it is just PVR-3 in the limit.")

print("\n=== 4. what the law does NOT say")
C, S, U, n = 10, 3, 1, 4
print("  population saving at n=4: %d" % (fresh(n, C) - taught(n, C, S, U)))
print("  sender's own ledger      : pays C+S = %d, would have paid C = %d alone -> WORSE by %d" % (C + S, C, S))
print("  so teaching is population-rational and sender-irrational unless the sender shares the")
print("  obligation or is compensated. The incentive question is item 16, not item 18.")

json.dump({"schema": "TeachingCultureWitnessV1",
           "closed_form": "n > 1 + S/(C-U), never if U>=C  (PVR-3 with r = population)",
           "all_cells_agree": ok,
           "imitation": "S=0 collapses the threshold to n>1",
           "accumulation": rows,
           "sender_incentive": {"sender_cost_taught": C + S, "sender_cost_alone": C,
                                "sender_delta": S,
                                "note": "population-rational, sender-irrational without shared obligation"}},
          open("microscopes/results/STAGE_TEACHING_CULTURE_WITNESS_V1.json", "w"), indent=1, sort_keys=True)
print("\nwritten")
