# Pre-registered independence report: M2-P3 authored worlds vs M2-P2 authored worlds.
import json, sys
R = sys.argv[1]
def load(p): return [json.loads(l) for l in open(p) if l.strip()]
p2 = load(R + "/research/m2-traversal-capital-v1/m2p2/authored/worlds.jsonl")
p3 = load(R + "/research/m2-traversal-capital-v1/m2p3/authored/worlds.jsonl")
shape = lambda w: (len(w["chunks"]), tuple(sorted(len(c) for c in w["chunks"])), w["min_builder_length"],
                   tuple(round(w["part_fractions"][k], 4) for k in ("initial", "tuning", "future")))
cset = lambda w: frozenset(tuple(c) for c in w["chunks"])
s2 = {shape(w) for w in p2}; c2 = [cset(w) for w in p2]
print("M2-P2 worlds", len(p2), "| M2-P3 worlds", len(p3))
rows = []
for w in p3:
    j = [(len(cset(w) & c) / len(cset(w) | c), i) for i, c in enumerate(c2)]
    best, bi = max(j)
    rows.append((w["world_id"], shape(w) in s2, cset(w) in c2, round(best, 3), p2[bi]["world_id"]))
    print("%-24s shape in P2: %-5s | identical chunk set: %-5s | nearest P2 Jaccard %.3f (%s)" % rows[-1])
print("shape collisions %d / %d | identical chunk sets %d / %d | median nearest Jaccard %.3f" % (
    sum(r[1] for r in rows), len(rows), sum(r[2] for r in rows), len(rows), sorted(r[3] for r in rows)[len(rows) // 2]))
