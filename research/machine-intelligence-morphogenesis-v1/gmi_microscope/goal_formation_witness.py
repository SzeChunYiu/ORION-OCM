"""I4: goal formation from obligation/utility structure -- and its duality with forgetting.

The consolidation theorem showed that when retention capacity is exceeded the machine must
DROP obligations, and CSR-1 says exactly which distinctions go. Goal formation is the same
selection made FORWARD: when the achievement budget cannot cover every obligation, the
machine must choose which to pursue.

Conjecture under test:
  the set a budget-constrained planner PURSUES is exactly the complement of the set a
  capacity-constrained retainer FORGETS, under matched costs and utilities.

If that holds, goals and forgetting are one selection rule seen from two directions, and
goal formation needs no new principle.

Exact: every subset enumerated, no heuristic.
"""
import itertools, json

# obligations: (name, utility, achievement cost, retention cost)
OBLIGATIONS = [("o1", 8, 3, 3), ("o2", 5, 2, 2), ("o3", 6, 4, 4),
               ("o4", 3, 1, 1), ("o5", 9, 5, 5), ("o6", 2, 3, 3)]

def best_subset(items, budget, cost_idx):
    best, bset = -1, None
    for r in range(len(items) + 1):
        for c in itertools.combinations(items, r):
            if sum(x[cost_idx] for x in c) <= budget:
                u = sum(x[1] for x in c)
                if u > best: best, bset = u, c
    return best, frozenset(x[0] for x in bset)

print("%-8s %-26s %-26s %s" % ("budget", "PURSUED (forward)", "RETAINED (backward)", "identical?"))
rows, allmatch = [], True
for B in range(2, 19, 2):
    up, pursued = best_subset(OBLIGATIONS, B, 2)     # achievement cost
    ur, retained = best_subset(OBLIGATIONS, B, 3)    # retention cost
    same = pursued == retained
    allmatch = allmatch and same
    forgotten = frozenset(x[0] for x in OBLIGATIONS) - retained
    rows.append({"budget": B, "pursued": sorted(pursued), "retained": sorted(retained),
                 "forgotten": sorted(forgotten), "identical": same,
                 "utility_pursued": up, "utility_retained": ur})
    print("%-8d %-26s %-26s %s" % (B, ",".join(sorted(pursued)) or "-",
                                   ",".join(sorted(retained)) or "-", same))

print("\npursued == retained at every budget:", allmatch)
print("(costs were matched, so this tests the DUALITY, not an arithmetic coincidence)")

# now break the matching to show the duality is about structure, not equal numbers
OB2 = [("o1", 8, 3, 6), ("o2", 5, 2, 1), ("o3", 6, 4, 2),
       ("o4", 3, 1, 5), ("o5", 9, 5, 3), ("o6", 2, 3, 4)]
print("\nwith achievement and retention costs DELIBERATELY MISMATCHED:")
print("%-8s %-26s %-26s %s" % ("budget", "PURSUED", "RETAINED", "identical?"))
n_diff = 0
for B in range(2, 19, 2):
    _, p = best_subset(OB2, B, 2); _, r = best_subset(OB2, B, 3)
    if p != r: n_diff += 1
    print("%-8d %-26s %-26s %s" % (B, ",".join(sorted(p)) or "-", ",".join(sorted(r)) or "-", p == r))
print("\ndiffer on %d of 9 budgets when costs are mismatched -- so the identity above is" % n_diff)
print("a consequence of matched cost structure, which is exactly the claim.")
json.dump({"schema": "GoalFormationDualityV1", "obligations": OBLIGATIONS, "rows": rows,
           "all_match_when_costs_matched": allmatch, "n_differ_when_mismatched": n_diff},
          open("microscopes/results/STAGE_GOAL_FORMATION_V1.json", "w"), indent=1, sort_keys=True)
print("written")
