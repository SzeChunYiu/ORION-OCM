# Independence report for package B: shape and chunk-set overlap with M2-P2's authored worlds
# (the pre-registered measure), and with package A for the record.
import json, sys
def load(p): return [json.loads(l) for l in open(p) if l.strip()]
shape = lambda w: (len(w["chunks"]), tuple(sorted(len(c) for c in w["chunks"])), w["min_builder_length"],
                   tuple(round(w["part_fractions"][k], 4) for k in ("initial", "tuning", "future")))
cset = lambda w: frozenset(tuple(c) for c in w["chunks"])
B = load(sys.argv[1]); refs = [("M2-P2", load(sys.argv[2])), ("package A", load(sys.argv[3]))]
print("package B worlds:", len(B))
for name, R in refs:
    s = {shape(w) for w in R}; cs = [cset(w) for w in R]
    rows = []
    for w in B:
        j = max((len(cset(w) & c) / len(cset(w) | c), i) for i, c in enumerate(cs))
        rows.append((w["world_id"], shape(w) in s, cset(w) in cs, round(j[0], 3), R[j[1]]["world_id"]))
    print("\nvs %s (%d worlds)" % (name, len(R)))
    for r in rows: print("  %-28s shape collision: %-5s identical chunk set: %-5s nearest Jaccard %.3f (%s)" % r)
    med = sorted(r[3] for r in rows)[len(rows)//2]
    print("  totals: shape collisions %d/%d | identical chunk sets %d/%d | median nearest Jaccard %.3f"
          % (sum(r[1] for r in rows), len(rows), sum(r[2] for r in rows), len(rows), med))
