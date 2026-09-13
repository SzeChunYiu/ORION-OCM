"""Item 11 / I4: planning stopping rule -- third model, with a genuine greedy trap.

Two earlier attempts were vacuous and are recorded as such: the first charged executed cost
at the true optimum regardless of depth, the second used a tail estimate tight enough that
depth-1 already chose correctly. In both, "stop at depth 1" won by construction.

Corrected: the depth-limited planner is OPTIMISTIC past its horizon (tail charged 0), which
is what makes shallow search genuinely misleading. Now a cheap-looking immediate move can
foreclose a far cheaper long skill, so deeper search buys real reduction in executed cost
and trades against its own charge.
"""
import json

C_SEARCH = 1

def options(t, p, skills):
    o = [("prim:" + t[p], 1, p + 1)]
    for s, u in skills.items():
        if t.startswith(s, p): o.append(("skill:" + s, u, p + len(s)))
    return o

def lookahead(t, p, d, skills):
    """best cost over at most d committed moves; OPTIMISTIC past the horizon (tail = 0)"""
    if p >= len(t): return 0
    if d == 0: return 0
    return min(c + lookahead(t, q, d - 1, skills) for _, c, q in options(t, p, skills))

def execute(t, d, skills):
    p, cost, dec, firsts = 0, 0, 0, []
    while p < len(t):
        best, pick = None, None
        for name, c, q in options(t, p, skills):
            v = c + lookahead(t, q, d - 1, skills)
            if best is None or v < best: best, pick = v, (name, c, q)
        firsts.append(pick[0]); cost += pick[1]; p = pick[2]; dec += 1
    return cost, dec, firsts

def optimal(t, skills):
    n = len(t); b = [0] * (n + 1)
    for q in range(n - 1, -1, -1):
        b[q] = min(c + b[nq] for _, c, nq in options(t, q, skills))
    return b[0]

CASES = [
    ("abcd",      {"ab": 1, "abcd": 1}),
    ("abcdabcd",  {"ab": 1, "abcd": 1}),
    ("abcdef",    {"ab": 1, "abcdef": 1}),
    ("abcabc",    {"ab": 1, "abcabc": 1}),
]
rows = []
for t, skills in CASES:
    maxd = len(t)
    ex = {d: execute(t, d, skills) for d in range(1, maxd + 1)}
    exec_cost = {d: ex[d][0] for d in ex}
    total = {d: exec_cost[d] + ex[d][1] * d * C_SEARCH for d in ex}
    deepest = ex[maxd][2]
    stab = next(d for d in range(1, maxd + 1) if all(ex[k][2] == deepest for k in range(d, maxd + 1)))
    best_d = min(total, key=total.get)
    opt = optimal(t, skills)
    rows.append({"target": t, "skills": skills, "true_optimum": opt,
                 "exec_by_depth": exec_cost, "total_by_depth": total,
                 "stabilises_at": stab, "cost_optimal_depth": best_d, "match": stab == best_d})
    print("%-10s optimum %d | exec %s" % (t, opt, [exec_cost[d] for d in sorted(exec_cost)]))
    print("%-10s           total %s | stabilises %d | optimal %d | match %s"
          % ("", [total[d] for d in sorted(total)], stab, best_d, stab == best_d))

allm = all(r["match"] for r in rows)
nontriv = sum(1 for r in rows if len(set(r["exec_by_depth"].values())) > 1)
print("\nexecuted cost actually varies with depth on %d of %d cases (non-vacuous)" % (nontriv, len(rows)))
print("action-invariance depth == cost-optimal stopping depth:", allm)
json.dump({"schema": "PlanningStoppingRuleV3", "C_search": C_SEARCH, "rows": rows,
           "all_match": allm, "nonvacuous_cases": nontriv},
          open("microscopes/results/STAGE_PLANNING_STOP_V3.json", "w"), indent=1, sort_keys=True)
print("written")
