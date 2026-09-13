"""Item 10 phase law: when does a SECOND level of chunking pay?

Same exact enumeration as the witness, swept over the storage price S and the recurrence
of the meta-pattern. Reports the boundary where depth-2 stops being decoration.
"""
import itertools, json

BASE = {"T1": "abcabd", "T2": "abcabe", "T3": "abdabc", "T4": "abeabc", "T5": "abcabc"}
C_PRIM, U_REF = 1, 1

def subs(s, lo=2):
    return {s[i:i+L] for L in range(lo, len(s)+1) for i in range(len(s)-L+1)}

def cost_with(chunks, tasks, mult, S):
    total = S * len(chunks)
    order = sorted(chunks, key=len, reverse=True)
    for n, s in tasks.items():
        i, c = 0, 0
        while i < len(s):
            for p in order:
                if s.startswith(p, i): c += U_REF; i += len(p); break
            else: c += C_PRIM; i += 1
        total += mult[n] * c
    return total

def best(tasks, mult, S, pool, maxk):
    b, bs = None, None
    for k in range(0, maxk + 1):
        for combo in itertools.combinations(pool, k):
            c = cost_with(list(combo), tasks, mult, S)
            if b is None or c < b: b, bs = c, combo
    return b, bs

print("%-5s %-5s %-7s %-9s %-9s %-10s %s" % ("S", "rep", "flat", "1-level", "2-level", "L2 gain", "L2 gain %"))
rows = []
for S in (1, 2, 3, 6, 10):
    for rep in (2, 4, 8, 16):
        mult = {"T1": rep, "T2": rep, "T3": 2, "T4": 2, "T5": 2}
        cands = sorted({p for t in BASE.values() for p in subs(t)}, key=lambda p: (-len(p), p))
        short = [p for p in cands if len(p) <= 3]
        long_ = [p for p in cands if len(p) >= 4]
        flat = sum(mult[n] * len(s) * C_PRIM for n, s in BASE.items())
        b1, _ = best(BASE, mult, S, short, 3)
        b2, s2 = best(BASE, mult, S, short + long_, 4)
        gain = b1 - b2
        pct = 100.0 * gain / max(1, flat - b1)
        rows.append({"S": S, "rep": rep, "flat": flat, "one": b1, "two": b2,
                     "l2_gain": gain, "l2_gain_pct_of_l1": round(pct, 1), "two_set": list(s2)})
        print("%-5d %-5d %-7d %-9d %-9d %-10d %.1f%%" % (S, rep, flat, b1, b2, gain, pct))
json.dump({"schema": "HierarchyPhaseSweepV1", "C_prim": C_PRIM, "U_ref": U_REF,
           "tasks": BASE, "rows": rows},
          open("microscopes/results/STAGE_HIERARCHY_PHASE_V1.json", "w"), indent=1, sort_keys=True)
print("\nwritten")
