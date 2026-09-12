"""Is the 3-4 band's failure structural or just unlucky sampling?

Computes a CEILING, not a sample: the maximum members any world in a band can have,
by taking the union of ALL chunks in the band (k unbounded) and then the best
admissible k<=8 subsets by greedy + exhaustive check on the strongest candidates.
If even the unbounded union cannot clear members_min, no authored world in that band
can be viable and the infeasibility is structural, not a sampling artifact."""
import sys, itertools
from collections import defaultdict
from itertools import product, combinations

sys.path.insert(0, "src")
from ocm.learning import methods as M
sys.path.insert(0, "research/m2-traversal-capital-v1/m2p2")
import m2p2_compile as C

canonical = {}
for L in range(9):
    for prog in product(M.PRIMITIVES, repeat=L):
        nf = M.normal_form(prog)
        if nf not in canonical:
            canonical[nf] = prog
progs = list(canonical.values())
V = C.VIABILITY
OPS = tuple(C.OP_MAP)
print("canonical polys:", len(canonical), " floors:", V)

def members(motifs, mbl):
    return [p for p in progs if len(p) >= mbl and C.decomposable(p, motifs)]

for lo, hi in ((2, 3), (3, 4), (2, 4), (4, 4)):
    pool = [tuple(C.OP_MAP[o] for o in p) for L in range(lo, hi + 1) for p in product(OPS, repeat=L)]
    print("\n=== band %d-%d   (pool %d chunks)" % (lo, hi, len(pool)))
    for mbl in (4, 5, 6, 7, 8):
        allm = len(members(tuple(sorted(pool)), mbl))
        print("   mbl=%d  UNBOUNDED-union ceiling: %5d members   (floor %d) -> %s"
              % (mbl, allm, V["members_min"], "possible" if allm >= V["members_min"] else "STRUCTURALLY IMPOSSIBLE"))
    # for the loosest mbl, find the best legal k<=8 subset greedily
    mbl = 4
    chosen, cur = [], 0
    for _ in range(8):
        best, bestm = None, cur
        for c in pool:
            if c in chosen: continue
            m = len(members(tuple(sorted(chosen + [c])), mbl))
            if m > bestm: best, bestm = c, m
        if best is None: break
        chosen.append(best); cur = bestm
    print("   greedy best legal world (k<=8, mbl=4): %d members -> %s"
          % (cur, "VIABLE" if cur >= V["members_min"] else "below floor"))
    print("   chunks:", [list(c) for c in chosen])
