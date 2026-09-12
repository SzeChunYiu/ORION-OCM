"""Band feasibility probe: can worlds with chunk-length bands other than 2-3 pass
the frozen M2-P2 viability floors?  Pure measurement over the REGISTERED substrate;
no authoring, no scored arm, no claim.  Reuses m2p2_compile's own logic verbatim
(canonical enumeration -> decomposable -> per-length hashed quotas -> floors)."""
import hashlib, json, random, sys
from collections import Counter, defaultdict
from itertools import product

sys.path.insert(0, "src")
from ocm.learning import methods as M
sys.path.insert(0, "research/m2-traversal-capital-v1/m2p2")
import m2p2_compile as C

print("compile module :", C.__file__)
print("OP_MAP         :", C.OP_MAP)
print("VIABILITY      :", C.VIABILITY)
print("PRIMITIVES     :", M.PRIMITIVES)

# one canonical enumeration, shared by every sampled world (exactly compile_world's)
canonical = {}
slot = 0
for L in range(9):
    for prog in product(M.PRIMITIVES, repeat=L):
        slot += 1
        nf = M.normal_form(prog)
        if nf not in canonical:
            canonical[nf] = prog
print("canonical polys:", len(canonical))

OPS = tuple(C.OP_MAP)          # spec-side op names, mapped by OP_MAP like the compiler
PF = {"initial": 0.50, "tuning": 0.25, "future": 0.25}
V = C.VIABILITY

def members_for(motifs, mbl):
    return [nf for nf, prog in canonical.items()
            if len(prog) >= mbl and C.decomposable(prog, motifs)]

def split_sizes(members, pf):
    by_len = defaultdict(list)
    for nf in members:
        by_len[len(canonical[nf])].append(nf)
    for L in by_len:
        by_len[L].sort(key=lambda nf: hashlib.sha256(str(nf).encode()).hexdigest())
    quota = {C.STREAM_NAME[k]: v for k, v in pf.items()}
    streams = {"train": [], "validation": [], "protected": []}
    for L, nfs in sorted(by_len.items()):
        i = 0
        for name, frac in quota.items():
            k = int(round(len(nfs) * frac))
            streams[name].extend(nfs[i:i + k]); i += k
        streams["train"].extend(nfs[i:])
    return {k: len(v) for k, v in streams.items()}, by_len

def viable(members, sizes):
    return (len(members) >= V["members_min"] and sizes["train"] >= V["initial_min"]
            and sizes["validation"] >= V["tuning_min"] and sizes["protected"] >= V["future_min"])

BANDS = {"2-3 (registered control)": (2, 3), "3-4": (3, 4), "2-4": (2, 4), "4 only": (4, 4)}
N = int(sys.argv[1]) if len(sys.argv) > 1 else 400
rng = random.Random(20260912)
report = {}
for label, (lo, hi) in BANDS.items():
    pool = [tuple(p) for L in range(lo, hi + 1) for p in product(OPS, repeat=L)]
    rows, lens_seen = [], Counter()
    for _ in range(N):
        k = rng.randint(4, 8)
        chunks = rng.sample(pool, k)
        mbl = rng.randint(4, 8)
        motifs = tuple(sorted(tuple(C.OP_MAP[o] for o in c) for c in chunks))
        mem = members_for(motifs, mbl)
        sizes, by_len = split_sizes(mem, PF)
        ok = viable(mem, sizes)
        rows.append({"k": k, "mbl": mbl, "members": len(mem), "sizes": sizes, "viable": ok})
        if ok:
            lens_seen.update(by_len.keys())
    nv = sum(r["viable"] for r in rows)
    med = sorted(r["members"] for r in rows)[len(rows) // 2]
    best = max(r["members"] for r in rows)
    report[label] = {"sampled": len(rows), "viable": nv, "viable_frac": round(nv / len(rows), 4),
                     "median_members": med, "max_members": best,
                     "canonical_lengths_in_viable_worlds": dict(sorted(lens_seen.items()))}
    print("\n== band %s" % label)
    print("   viable %d/%d (%.1f%%)  median members %d  max %d"
          % (nv, len(rows), 100.0 * nv / len(rows), med, best))
    print("   canonical lengths present in viable worlds:", dict(sorted(lens_seen.items())))
    # viable worlds only, by min_builder_length
    bym = defaultdict(lambda: [0, 0])
    for r in rows:
        bym[r["mbl"]][0] += 1; bym[r["mbl"]][1] += int(r["viable"])
    print("   by mbl (sampled/viable):", {m: "%d/%d" % (a, b) for m, (a, b) in sorted(bym.items())})

json.dump(report, open("BAND_PROBE.json", "w"), indent=1, sort_keys=True)
print("\nwrote BAND_PROBE.json")
