"""I1's two remaining boxes: retrieval policy, and unified vs differentiated memory.

(a) RETRIEVAL POLICY. Retrieval is PVR-3's U term. Which stored item to try is a stopping
    problem: try candidates in some order, each costing c_r, stopping when the expected gain
    from another try falls below its cost. Conjecture: the optimal order is decreasing
    p/c (match probability per retrieval cost), and the stopping rule is the same
    value-aware rule derived for planning and replanning.

(b) UNIFIED vs DIFFERENTIATED. The partition gave four regimes with different growth laws.
    A unified store must serve every regime at a single per-item cost -- necessarily the
    most expensive one any regime requires. Differentiated stores pay each regime's own.
    Conjecture: differentiation pays exactly when per-item costs differ across regimes,
    and the saving scales with that spread.

Exact enumeration for both.
"""
import itertools, json

# ---------- (a) retrieval order and stopping ----------
CANDS = [("c1", 0.5, 1.0), ("c2", 0.3, 1.0), ("c3", 0.1, 0.5), ("c4", 0.05, 4.0)]
MISS = 6.0     # cost of failing to retrieve at all

def cost_of_order(order, stop_after):
    """expected cost: try in order, stop after k tries, pay MISS if never found"""
    total, p_reach = 0.0, 1.0
    for i, (n, p, c) in enumerate(order):
        if i >= stop_after: break
        total += p_reach * c
        p_reach *= (1 - p)
    total += p_reach * MISS
    return total

best = None
for order in itertools.permutations(CANDS):
    for k in range(1, len(CANDS) + 1):
        c = cost_of_order(order, k)
        if best is None or c < best[0]: best = (c, [x[0] for x in order], k)
pc_order = sorted(CANDS, key=lambda x: -(x[1] / x[2]))
pc_best = min(((cost_of_order(pc_order, k), k) for k in range(1, len(CANDS) + 1)))
print("(a) RETRIEVAL")
print("  exhaustive optimum        : cost %.4f  order %s  stop after %d" % (best[0], best[1], best[2]))
print("  p/c ordering              : cost %.4f  order %s  stop after %d"
      % (pc_best[0], [x[0] for x in pc_order], pc_best[1]))
print("  p/c ordering is optimal   :", abs(best[0] - pc_best[0]) < 1e-12)
# does the value-aware stopping rule pick the same k?
va_k = 0
p_reach = 1.0
for n, p, c in pc_order:
    gain = p_reach * p * MISS      # expected saving from trying this one
    if gain > p_reach * c: va_k += 1; p_reach *= (1 - p)
    else: break
print("  value-aware stop picks k  : %d   (optimum k = %d)  match: %s"
      % (va_k, pc_best[1], va_k == pc_best[1]))

# ---------- (b) unified vs differentiated ----------
print("\n(b) UNIFIED vs DIFFERENTIATED")
print("  %-28s %-12s %-14s %s" % ("per-item costs by regime", "unified", "differentiated", "winner"))
rows = []
ITEMS = {"episodic": 12, "semantic": 3, "procedural": 2, "working": 1}
for costs in ({"episodic": 1, "semantic": 1, "procedural": 1, "working": 1},
              {"episodic": 1, "semantic": 2, "procedural": 3, "working": 1},
              {"episodic": 1, "semantic": 4, "procedural": 8, "working": 1},
              {"episodic": 1, "semantic": 8, "procedural": 16, "working": 1}):
    unified = sum(ITEMS.values()) * max(costs.values())
    diff = sum(ITEMS[r] * costs[r] for r in ITEMS)
    w = "differentiated" if diff < unified else "unified"
    spread = max(costs.values()) / min(costs.values())
    rows.append({"costs": costs, "spread": spread, "unified": unified, "differentiated": diff, "winner": w})
    print("  %-28s %-12d %-14d %s" % (str(list(costs.values())), unified, diff, w))
print("\n  differentiation wins on %d of %d cost profiles" % (sum(1 for r in rows if r["winner"] == "differentiated"), len(rows)))
print("  saving grows with cost spread:", [r["unified"] - r["differentiated"] for r in rows])
json.dump({"schema": "I1RetrievalAndUnificationV1",
           "retrieval": {"optimum": best[0], "pc_order_cost": pc_best[0],
                         "pc_optimal": abs(best[0] - pc_best[0]) < 1e-12,
                         "value_aware_k": va_k, "optimum_k": pc_best[1],
                         "stop_matches": va_k == pc_best[1]},
           "unification": rows},
          open("microscopes/results/STAGE_I1_RETRIEVAL_UNIFICATION_V1.json", "w"), indent=1, sort_keys=True)
print("\nwritten")
