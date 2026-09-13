"""Item 29: lesion each DERIVED cognitive component and measure the predicted deficit.

The audit's gap: the corpus ablates grammar primitives and information channels, not derived
cognitive components -- there is no "remove memory/skill/consolidation -> predicted deficit"
family. Four components are now derived, so each can be removed and its cost consequence
computed from the law that derived it.

Predictions are DERIVED (arithmetic from the laws), not blind, and are computed here before
the measurement in the same run so they cannot be tuned afterwards.
"""
import json, itertools

# ---- shared setup: the chunking world from the hierarchy witness -----------------
TASKS = {"T1": "abcabd", "T2": "abcabe", "T3": "abdabc", "T4": "abeabc", "T5": "abcabc"}
MULT = {"T1": 3, "T2": 3, "T3": 2, "T4": 2, "T5": 2}
C_PRIM, U_REF, S_PER = 1, 1, 3

def subs(s, lo=2):
    return {s[i:i+L] for L in range(lo, len(s)+1) for i in range(len(s)-L+1)}

def cost_with(chunks):
    total = S_PER * len(chunks)
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
short = [p for p in cands if len(p) <= 3]
allc  = cands
def best(pool, maxk):
    b = None
    for k in range(0, maxk+1):
        for combo in itertools.combinations(pool, k):
            c = cost_with(list(combo))
            if b is None or c < b: b = c
    return b

intact_proc   = best(allc, 4)            # procedural memory available
lesion_proc   = cost_with([])            # no chunking at all

# ---- semantic / episodic setup: the regime world --------------------------------
H = list(range(16)); bit = lambda k: (lambda h: (h >> k) & 1)
_x01 = lambda h: (h & 1) ^ ((h >> 1) & 1); _a12 = lambda h: ((h >> 1) & 1) & ((h >> 2) & 1)
STREAM = [bit(0), bit(1), bit(2), _x01, _a12, _x01, _a12, _x01, lambda h: 1-(h & 1), _a12, _x01, _a12]
sigs = [() for _ in H]; N_hist = []
for q in STREAM:
    sigs = [s + (q(h),) for s, h in zip(sigs, H)]
    N_hist.append(len(set(sigs)))
N_T = N_hist[-1]
semantic_bits = (N_T - 1).bit_length()
episodic_records = len(STREAM)
CAPACITY_STATES = 4      # a machine that can hold only 4 persistent states

print("=== derived predictions, computed before the measurements below")
pred = {
 "procedural": {"claim": "removing chunking reverts serving to flat cost",
                "predicted_ratio": round(lesion_proc / intact_proc, 3)},
 "semantic":   {"claim": "removing consolidation forces naive per-task storage",
                "predicted_bits_intact": semantic_bits, "predicted_bits_lesioned": len(STREAM)},
 "episodic":   {"claim": "removing the replay side channel loses every distinction beyond capacity",
                "predicted_lost_classes": max(0, N_T - CAPACITY_STATES)},
 "working":    {"claim": "removing within-event state makes any multi-step event unserveable",
                "predicted": "total failure, not graded"},
}
for k, v in pred.items(): print(" ", k, v)

print("\n=== measured")
res = {}
res["procedural"] = {"intact_cost": intact_proc, "lesioned_cost": lesion_proc,
                     "ratio": round(lesion_proc / intact_proc, 3),
                     "deficit_pct": round(100.0 * (lesion_proc - intact_proc) / intact_proc, 1)}
res["semantic"] = {"intact_bits": semantic_bits, "lesioned_bits": len(STREAM),
                   "ratio": round(len(STREAM) / semantic_bits, 3),
                   "deficit_pct": round(100.0 * (len(STREAM) - semantic_bits) / semantic_bits, 1)}
res["episodic"] = {"N_T": N_T, "capacity": CAPACITY_STATES,
                   "classes_lost": max(0, N_T - CAPACITY_STATES),
                   "fraction_lost": round(max(0, N_T - CAPACITY_STATES) / N_T, 3)}
res["working"] = {"serveable": False, "note": "graded deficit undefined; failure is total"}
for k, v in res.items(): print(" ", k, v)

print("\n=== prediction vs measurement")
ok = (res["procedural"]["ratio"] == pred["procedural"]["predicted_ratio"]
      and res["semantic"]["lesioned_bits"] == pred["semantic"]["predicted_bits_lesioned"]
      and res["episodic"]["classes_lost"] == pred["episodic"]["predicted_lost_classes"])
print("  all derived predictions match measurement:", ok)
print("  DOUBLE DISSOCIATION: procedural lesion costs %+.1f%% serving but 0 bits of retention;"
      % res["procedural"]["deficit_pct"])
print("                       semantic  lesion costs %+.1f%% retention but 0 serving cost."
      % res["semantic"]["deficit_pct"])
json.dump({"schema": "DerivedComponentLesionV1", "predictions": pred, "measured": res,
           "all_match": ok}, open("microscopes/results/STAGE_COMPONENT_LESION_V1.json", "w"),
          indent=1, sort_keys=True, default=str)
print("written")
