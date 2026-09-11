"""Band 3-4: is the floor reachable once the chunk-count cap is raised?

Two things, in order:
 (1) VALIDATE the analytic bound members <= f + k^2 (f = #length-4 chunks, k = #chunks)
     against exact counts from the registered compiler. Any violation invalidates the
     bound and is reported loudly -- the bound is the whole argument, so it is checked
     before it is used.
 (2) MEASURE viability for k = 4..16, which is where the bound says the floor becomes
     reachable (k^2 + f >= 90 needs k >= 10).
No authoring, no scored arm, no claim -- feasibility measurement only."""
import hashlib, json, random, sys
from collections import defaultdict
from itertools import product

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
progs = list(canonical.items())
V = C.VIABILITY
OPS = tuple(C.OP_MAP)
PF = {"initial": 0.50, "tuning": 0.25, "future": 0.25}
print("canonical polys:", len(canonical), "floors:", V)

POOL34 = [tuple(C.OP_MAP[o] for o in p) for L in (3, 4) for p in product(OPS, repeat=L)]
print("band 3-4 pool:", len(POOL34))

def members(motifs, mbl):
    return [nf for nf, prog in progs if len(prog) >= mbl and C.decomposable(prog, motifs)]

def sizes_of(mem, pf):
    by_len = defaultdict(list)
    for nf in mem:
        by_len[len(canonical[nf])].append(nf)
    for L in by_len:
        by_len[L].sort(key=lambda nf: hashlib.sha256(str(nf).encode()).hexdigest())
    quota = {C.STREAM_NAME[k]: v for k, v in pf.items()}
    st = {"train": [], "validation": [], "protected": []}
    for L, nfs in sorted(by_len.items()):
        i = 0
        for name, frac in quota.items():
            n = int(round(len(nfs) * frac)); st[name].extend(nfs[i:i + n]); i += n
        st["train"].extend(nfs[i:])
    return {k: len(v) for k, v in st.items()}, sorted(by_len)

def viable(mem, sz):
    return (len(mem) >= V["members_min"] and sz["train"] >= V["initial_min"]
            and sz["validation"] >= V["tuning_min"] and sz["protected"] >= V["future_min"])

rng = random.Random(20260912)
print("\n### (1) analytic bound check:  members <= f + k^2   (mbl=4)")
violations = 0; checked = 0
for k in range(4, 17):
    for _ in range(12):
        chunks = rng.sample(POOL34, k)
        f = sum(1 for c in chunks if len(c) == 4)
        mem = len(members(tuple(sorted(chunks)), 4))
        bound = f + k * k
        checked += 1
        if mem > bound:
            violations += 1
            print("   VIOLATION k=%d f=%d members=%d > bound=%d" % (k, f, mem, bound))
print("   checked %d worlds, %d violations -> %s" % (checked, violations,
      "BOUND HOLDS" if violations == 0 else "BOUND INVALID"))

print("\n### (2) viability by chunk count (band 3-4)")
report = {}
for k in range(4, 17):
    for mbl in (4, 5):
        nv = 0; best = 0; N = 60
        for _ in range(N):
            chunks = rng.sample(POOL34, k)
            mem = members(tuple(sorted(chunks)), mbl)
            sz, lens = sizes_of(mem, PF)
            best = max(best, len(mem))
            if viable(mem, sz): nv += 1
        report["k%d_mbl%d" % (k, mbl)] = {"viable": nv, "n": N, "max_members": best}
        print("   k=%-2d mbl=%d   viable %2d/%d   max members %4d %s"
              % (k, mbl, nv, N, best, "<-- clears floor" if best >= V["members_min"] else ""))
json.dump(report, open("BAND_K.json", "w"), indent=1, sort_keys=True)
print("\nwrote BAND_K.json")
