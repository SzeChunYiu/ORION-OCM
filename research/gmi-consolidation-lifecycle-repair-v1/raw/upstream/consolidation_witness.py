"""Item 7: consolidation vs forgetting, derived from CSR-1 + the quotient theorem.

CSR-1 (Continual Semantic Retention Theorem) fixes the exact minimum persistent memory:
after retaining tasks 1..t, the histories fall into N_t retention-equivalence classes and
the minimum number of persistent states is exactly N_t, i.e. ceil(log2 N_t) bits. N_t is
monotone, and N_{t+1} = N_t exactly when the new task is already a function of the retained
semantic state.

That is the whole lever. This enumerates it exactly on a finite history set and reports
when naive per-task storage is wasteful, when consolidation is free, and when forgetting
is forced by a capacity bound.

No approximation: |H| = 16, every quantity computed by complete enumeration.
"""
import itertools, json

H = list(range(16))                      # 16 possible histories

def classes(sigs):
    """number of retention-equivalence classes given a joint signature per history"""
    return len(set(sigs))

def run(tasks, name, capacity_bits=None):
    """tasks: list of callables H -> {0,1}"""
    rows = []
    sigs = [() for _ in H]
    for t, q in enumerate(tasks, 1):
        sigs = [s + (q(h),) for s, h in zip(sigs, H)]
        N = classes(sigs)
        bits = (N - 1).bit_length()                    # ceil(log2 N)
        naive = t                                      # one bit stored per task, no sharing
        rows.append({"t": t, "N_t": N, "min_bits": bits, "naive_bits": naive,
                     "saving_bits": naive - bits,
                     "new_distinctions": None if t == 1 else N - rows[-1]["N_t"]})
    out = {"name": name, "H": len(H), "T": len(tasks), "rows": rows,
           "final_N": rows[-1]["N_t"], "final_min_bits": rows[-1]["min_bits"],
           "naive_bits": len(tasks), "total_saving_bits": len(tasks) - rows[-1]["min_bits"]}
    if capacity_bits is not None:
        cap_states = 2 ** capacity_bits
        first_over = next((r["t"] for r in rows if r["N_t"] > cap_states), None)
        out["capacity_bits"] = capacity_bits
        out["capacity_states"] = cap_states
        out["first_task_exceeding_capacity"] = first_over
        out["forgetting_forced"] = first_over is not None
    return out

# --- three exactly-enumerated regimes -------------------------------------------------
bit = lambda k: (lambda h: (h >> k) & 1)

# A. independent tasks: each new task refines maximally. Consolidation cannot help.
A = run([bit(0), bit(1), bit(2), bit(3)], "A_independent", capacity_bits=3)

# B. redundant tasks: later tasks are functions of earlier ones. Consolidation is free.
B = run([bit(0), bit(1),
         lambda h: (h & 1) ^ ((h >> 1) & 1),          # XOR of tasks 1,2 -> no new distinction
         lambda h: 1 - (h & 1),                        # negation of task 1 -> no new distinction
         lambda h: ((h & 1) | ((h >> 1) & 1))],        # OR of tasks 1,2 -> no new distinction
        "B_redundant", capacity_bits=3)

# C. mixed: two independent, then three derived, then one genuinely new
C = run([bit(0), bit(1),
         lambda h: (h & 1) ^ ((h >> 1) & 1),
         lambda h: 1 - ((h >> 1) & 1),
         bit(2),
         lambda h: ((h >> 2) & 1) & (h & 1)],
        "C_mixed", capacity_bits=2)

for r in (A, B, C):
    print(f"\n=== {r['name']}  (|H|={r['H']}, T={r['T']})")
    print("  t  N_t  min_bits  naive_bits  saving  new_distinctions")
    for row in r["rows"]:
        print("  %-2d %-4d %-9d %-11d %-7d %s" % (row["t"], row["N_t"], row["min_bits"],
                                                  row["naive_bits"], row["saving_bits"],
                                                  row["new_distinctions"]))
    print(f"  final: N={r['final_N']} min_bits={r['final_min_bits']} naive={r['naive_bits']} "
          f"total_saving={r['total_saving_bits']} bits")
    if r.get("capacity_bits") is not None:
        print(f"  capacity {r['capacity_bits']} bits = {r['capacity_states']} states -> "
              f"forgetting forced: {r['forgetting_forced']}"
              + (f" (first at task {r['first_task_exceeding_capacity']})" if r["forgetting_forced"] else ""))
json.dump({"schema": "ConsolidationForgettingWitnessV1", "regimes": [A, B, C]},
          open("microscopes/results/STAGE_CONSOLIDATION_WITNESS_V1.json", "w"), indent=1, sort_keys=True)
print("\nwritten")
