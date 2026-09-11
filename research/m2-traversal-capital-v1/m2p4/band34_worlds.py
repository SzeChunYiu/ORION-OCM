"""Search viable band-3-4 chunk sets at k=13..16 and emit worlds.jsonl.

Feasibility follow-up only: these are candidate worlds for INSTRUMENT CALIBRATION
(does G-SURF false-fire on band 3-4?), not an authored package and not a scored run.
Authored by this lane acting as a fake author, exactly as the VAL-A..VAL-H worlds in
M2P2_GSURF_CALIBRATION.md were."""
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
V, OPS = C.VIABILITY, tuple(C.OP_MAP)
SPEC_OPS = {v: k for k, v in C.OP_MAP.items()}      # registered -> spec names
POOL = [tuple(C.OP_MAP[o] for o in p) for L in (3, 4) for p in product(OPS, repeat=L)]
PF = {"initial": 0.50, "tuning": 0.25, "future": 0.25}

def members(motifs, mbl):
    return [nf for nf, pr in progs if len(pr) >= mbl and C.decomposable(pr, motifs)]

def sizes_of(mem):
    by_len = defaultdict(list)
    for nf in mem:
        by_len[len(canonical[nf])].append(nf)
    for L in by_len:
        by_len[L].sort(key=lambda nf: hashlib.sha256(str(nf).encode()).hexdigest())
    quota = {C.STREAM_NAME[k]: v for k, v in PF.items()}
    st = {"train": [], "validation": [], "protected": []}
    for L, nfs in sorted(by_len.items()):
        i = 0
        for name, frac in quota.items():
            n = int(round(len(nfs) * frac)); st[name].extend(nfs[i:i + n]); i += n
        st["train"].extend(nfs[i:])
    return {k: len(v) for k, v in st.items()}

def viable(mem, sz):
    return (len(mem) >= V["members_min"] and sz["train"] >= V["initial_min"]
            and sz["validation"] >= V["tuning_min"] and sz["protected"] >= V["future_min"])

rng = random.Random(20260912)
found, tries = [], 0
want = 6
while len(found) < want and tries < 20000:
    tries += 1
    k = rng.choice([13, 14, 15, 16])
    mbl = rng.choice([4, 5])
    chunks = rng.sample(POOL, k)
    motifs = tuple(sorted(chunks))
    mem = members(motifs, mbl)
    sz = sizes_of(mem)
    if not viable(mem, sz):
        continue
    if any(set(motifs) == set(f["motifs"]) for f in found):
        continue
    found.append({"motifs": motifs, "k": k, "mbl": mbl, "members": len(mem), "sizes": sz})
    print("  found k=%-2d mbl=%d  members=%4d  sizes=%s (try %d)" % (k, mbl, len(mem), sz, tries))

print("\nfound %d viable band-3-4 worlds in %d tries" % (len(found), tries))
with open("worlds_band34.jsonl", "w", encoding="utf-8", newline="\n") as fh:
    for i, f in enumerate(found, 1):
        w = {"world_id": "b34-%02d-k%d-m%d" % (i, f["k"], f["mbl"]),
             "chunks": [[SPEC_OPS[o] for o in c] for c in f["motifs"]],
             "min_builder_length": f["mbl"],
             "part_fractions": PF,
             "surface": {"name": "band 3-4 calibration world %d" % i,
                         "note": "lane-authored instrument-calibration world, never a scored package"},
             "intent": {"intent_role": "audit_only",
                        "expected_members": f["members"], "chunk_count": f["k"]}}
        fh.write(json.dumps(w) + "\n")
print("wrote worlds_band34.jsonl")
