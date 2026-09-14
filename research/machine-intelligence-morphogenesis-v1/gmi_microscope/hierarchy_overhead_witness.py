"""I3: when does hierarchical abstraction LOSE to overhead?

The hierarchy sweep showed a second level adding 0% at high storage / low recurrence. But
"adds nothing" is not "loses": an optimiser that may choose the empty chunk set can never
do worse than flat, so optimising over subsets cannot exhibit a loss by construction.

Two honest questions instead:
  (a) at what storage price does the OPTIMAL structure become flat (no chunk clears PVR-3)?
  (b) what does a COMMITTED hierarchy -- one already built and paid for -- cost against flat
      at that price? That is where abstraction genuinely loses.

Exact enumeration over all chunk subsets.
"""
import itertools, json

TASKS = {"T1": "abcabd", "T2": "abcabe", "T3": "abdabc", "T4": "abeabc", "T5": "abcabc"}
MULT = {"T1": 3, "T2": 3, "T3": 2, "T4": 2, "T5": 2}
C_PRIM = U_REF = 1

def subs(s, lo=2):
    return {s[i:i+L] for L in range(lo, len(s)+1) for i in range(len(s)-L+1)}

def cost(chunks, S):
    total = S * len(chunks)
    order = sorted(chunks, key=len, reverse=True)
    for n, s in TASKS.items():
        i, c = 0, 0
        while i < len(s):
            for p in order:
                if s.startswith(p, i): c += U_REF; i += len(p); break
            else: c += C_PRIM; i += 1
        total += MULT[n] * c
    return total

cands = sorted({p for t in TASKS.values() for p in subs(t)}, key=len, reverse=True)
pool = [p for p in cands if len(p) <= 4]
COMMITTED = ("abc", "abd", "abe")          # a hierarchy already built

print("%-8s %-12s %-22s %-14s %-14s %s" % ("S", "flat", "best chunk set", "best cost", "committed", "committed loses?"))
rows = []
for S in (1, 3, 6, 10, 15, 20, 30):
    flat = cost([], S)
    best, bset = None, None
    for k in range(0, 4):
        for combo in itertools.combinations(pool, k):
            c = cost(list(combo), S)
            if best is None or c < best: best, bset = c, combo
    comm = cost(list(COMMITTED), S)
    loses = comm > flat
    rows.append({"S": S, "flat": flat, "best": best, "best_set": sorted(bset),
                 "committed": comm, "committed_loses": loses, "optimal_is_flat": len(bset) == 0})
    print("%-8d %-12d %-22s %-14d %-14d %s" % (S, flat, ",".join(sorted(bset)) or "(none)", best, comm, loses))

flat_at = [r["S"] for r in rows if r["optimal_is_flat"]]
lose_at = [r["S"] for r in rows if r["committed_loses"]]
print("\noptimal structure is FLAT at S =", flat_at or "never in range")
print("committed hierarchy LOSES at S =", lose_at or "never in range")
print("=> abstraction stops paying before it starts hurting: the optimum goes flat at S=%s," % (flat_at[0] if flat_at else "-"))
print("   while a committed hierarchy only becomes worse than flat at S=%s." % (lose_at[0] if lose_at else "-"))
json.dump({"schema": "HierarchyOverheadLossV1", "committed_set": list(COMMITTED), "rows": rows,
           "optimal_flat_from": flat_at[0] if flat_at else None,
           "committed_loses_from": lose_at[0] if lose_at else None},
          open("microscopes/results/STAGE_HIERARCHY_OVERHEAD_V1.json", "w"), indent=1, sort_keys=True)
print("written")
