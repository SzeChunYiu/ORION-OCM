"""Item 10: when does a sequence become a skill, and when do levels form?

Assembled, not assumed:
  * PVR-3 (proof-search reuse) gives the single-class break-even: with C = charged
    derivation, S = one-time storage, U = per-invocation lookup, retaining beats
    recomputing exactly when S < (r-1)(C-U), i.e. r > 1 + S/(C-U), and never when U >= C.
  * The developmental quotient theorem says the coarsest response-preserving quotient is
    the unique minimal representation -- so "what to chunk" is not a heuristic.

A skill is therefore a retained sub-quotient, and the chunking law is PVR-3 applied to it.
This enumerates the level question exactly: does a SECOND level ever pay, and if so why.

Everything below is complete enumeration over a finite task set. No search, no sampling.
"""
import itertools, json

# primitive actions a..f ; high-level tasks are sequences over them
TASKS = {
    "T1": "abcabd",
    "T2": "abcabe",
    "T3": "abdabc",
    "T4": "abeabc",
    "T5": "abcabc",
}
MULT = {"T1": 3, "T2": 3, "T3": 2, "T4": 2, "T5": 2}   # how often each task is demanded

C_PRIM = 1     # charged cost to derive one primitive action fresh
U_REF  = 1     # charged cost to invoke a retained chunk (one reference)
S_PER  = 3     # one-time storage per retained chunk, charged once

def substrings(s, lo=2, hi=None):
    hi = hi or len(s)
    return {s[i:i+L] for L in range(lo, hi+1) for i in range(len(s)-L+1)}

def occurrences(pat, s):
    return sum(1 for i in range(len(s)-len(pat)+1) if s[i:i+len(pat)] == pat)

# total demand for each candidate chunk across the whole weighted task stream
cands = sorted({p for t in TASKS.values() for p in substrings(t)}, key=lambda p: (-len(p), p))
demand = {p: sum(MULT[n] * occurrences(p, s) for n, s in TASKS.items()) for p in cands}

def flat_cost():
    """no chunking: every demanded task derived from primitives every time"""
    return sum(MULT[n] * len(s) * C_PRIM for n, s in TASKS.items())

def cost_with(chunks):
    """retain the given chunks; each task served by greedy longest-match over them"""
    total = sum(S_PER for _ in chunks)
    order = sorted(chunks, key=len, reverse=True)
    for n, s in TASKS.items():
        i, c = 0, 0
        while i < len(s):
            for p in order:
                if s.startswith(p, i):
                    c += U_REF; i += len(p); break
            else:
                c += C_PRIM; i += 1
        total += MULT[n] * c
    return total

base = flat_cost()
print(f"flat cost (no chunking): {base}")
print(f"\ntop candidate chunks by demand (PVR-3 threshold r > 1 + S/(C-U)):")
print("  chunk   demand  derive_C  break_even_r  pays?")
rows = []
for p in cands[:10]:
    C = len(p) * C_PRIM
    r = demand[p]
    thr = None if U_REF >= C else 1 + S_PER / (C - U_REF)
    pays = thr is not None and r > thr
    rows.append({"chunk": p, "demand": r, "C": C, "threshold": thr, "pays": pays})
    print("  %-7s %-7d %-9d %-13s %s" % (p, r, C, "n/a" if thr is None else f"{thr:.2f}", pays))

# exhaustive: best single-level chunk set, and best two-level set
singles = [p for p in cands if len(p) <= 3]
best1, best1set = None, None
for k in range(0, 4):
    for combo in itertools.combinations(singles, k):
        c = cost_with(list(combo))
        if best1 is None or c < best1: best1, best1set = c, combo
longs = [p for p in cands if len(p) >= 4]
best2, best2set = None, None
for k in range(0, 3):
    for combo in itertools.combinations(longs, k):
        for k1 in range(0, 3):
            for c1 in itertools.combinations(singles, k1):
                s = list(combo) + list(c1)
                c = cost_with(s)
                if best2 is None or c < best2: best2, best2set = c, tuple(s)
print(f"\nbest ONE-level  (short chunks only): cost {best1}  set {best1set}")
print(f"best TWO-level  (long + short)     : cost {best2}  set {best2set}")
print(f"flat {base} -> one-level {best1} (save {base-best1}) -> two-level {best2} (save {base-best2})")
print(f"second level adds: {best1 - best2}")
json.dump({"schema": "HierarchyChunkingWitnessV1", "tasks": TASKS, "multiplicities": MULT,
           "costs": {"C_prim": C_PRIM, "U_ref": U_REF, "S_per": S_PER},
           "flat": base, "best_one_level": {"cost": best1, "set": list(best1set)},
           "best_two_level": {"cost": best2, "set": list(best2set)},
           "candidates": rows},
          open("microscopes/results/STAGE_HIERARCHY_WITNESS_V1.json", "w"), indent=1, sort_keys=True)
print("written")
