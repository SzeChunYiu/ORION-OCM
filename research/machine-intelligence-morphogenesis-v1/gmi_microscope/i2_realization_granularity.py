"""I2's remaining boxes: concept REALIZATIONS, and concept GRANULARITY under pressure.

(a) REALIZATION. A concept is a retained equivalence class. Storing one admits three
    realizations, which are exactly the corpus's carrier classes:
      exemplar  (TABLE/KVSTORE) : keep every member          -> size ~ |class|
      prototype (DENSE)         : keep one representative + a metric
      rule      (PROGRAM)       : keep a predicate deciding membership -> size ~ description length
    Conjecture: none dominates; the winner is set by class size against description length,
    so the three are alternative realizations of one object rather than rival theories.

(b) GRANULARITY. Finer quotients fit better but cost more to retain. Under a storage
    budget the optimal number of retained classes should FALL as pressure rises --
    concepts coarsen when resources tighten.

Exact enumeration for both.
"""
import json

# ---------- (a) which realization wins ----------
PROTO_FIXED, METRIC = 2, 1          # prototype: representative + metric
def exemplar_cost(n, _d): return n
def prototype_cost(n, _d): return PROTO_FIXED + METRIC
def rule_cost(_n, d): return d      # description length of the membership predicate

print("(a) CONCEPT REALIZATIONS")
print("  %-12s %-12s %-10s %-11s %-8s %s" % ("class size", "descr len", "exemplar", "prototype", "rule", "winner"))
rows_a, winners = [], set()
for n in (1, 2, 5, 20):
    for d in (1, 3, 12):
        c = {"exemplar": exemplar_cost(n, d), "prototype": prototype_cost(n, d), "rule": rule_cost(n, d)}
        w = min(c, key=c.get)
        winners.add(w); rows_a.append({"n": n, "d": d, "costs": c, "winner": w})
        print("  %-12d %-12d %-10d %-11d %-8d %s" % (n, d, c["exemplar"], c["prototype"], c["rule"], w))
print("  distinct winners across the sweep: %s  (none dominates: %s)" % (sorted(winners), len(winners) > 1))

# ---------- (b) granularity under resource pressure ----------
# a target with 8 underlying distinctions; a quotient with k classes makes (8-k) merge errors
N_DISTINCT, ERR_PER_MERGE, STORE_PER_CLASS = 8, 3.0, 1.0
print("\n(b) CONCEPT GRANULARITY UNDER PRESSURE")
print("  %-10s %-28s %s" % ("budget", "cost by k (1..8)", "optimal k"))
rows_b = []
for budget in (10, 6, 4, 2, 1):
    costs = {}
    for k in range(1, N_DISTINCT + 1):
        store = k * STORE_PER_CLASS
        if store > budget:      # cannot afford this granularity
            continue
        costs[k] = store + (N_DISTINCT - k) * ERR_PER_MERGE
    best_k = min(costs, key=costs.get) if costs else None
    rows_b.append({"budget": budget, "costs": costs, "optimal_k": best_k})
    print("  %-10s %-28s %s" % (budget, [costs.get(k, "-") for k in range(1, N_DISTINCT + 1)], best_k))
ks = [r["optimal_k"] for r in rows_b if r["optimal_k"]]
mono = all(ks[i] >= ks[i + 1] for i in range(len(ks) - 1))
print("\n  optimal granularity falls monotonically as the budget tightens: %s  %s" % (mono, ks))
json.dump({"schema": "ConceptRealizationGranularityV1",
           "realizations": rows_a, "none_dominates": len(winners) > 1,
           "granularity": rows_b, "monotone_coarsening": mono, "optimal_k_sequence": ks},
          open("microscopes/results/STAGE_I2_REALIZATION_GRANULARITY_V1.json", "w"), indent=1, sort_keys=True)
print("written")
