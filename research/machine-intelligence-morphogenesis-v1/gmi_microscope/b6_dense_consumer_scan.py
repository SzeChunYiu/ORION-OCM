"""Does a DENSE-carrier graph in this corpus ever use DENSE as a coefficient?

The IR's coefficient uses of a dense parameter block are DOT (dot product with an input),
LINEAR (width x width map plus bias) and GRAD (reverse-mode update). This walks every
DENSE-carrier genotype available and asks, per graph, whether any DENSE node reaches one
of those consumers, and whether anything writes to the DENSE node at all.

Pure inspection of committed receipts: no search, no evaluation.
"""
import json, glob, sys, os

# CORRECTED: DOT is not a kind in this IR, and AFFINE was missing. Built from morph.KINDS
# (parameter-consuming transforms), not from a source comment. See the Z8 retraction.
NUMERIC = {"LINEAR", "AFFINE"}
GRADS = {"GRAD"}

def probe(g):
    nodes, edges = g["nodes"], g["edges"]
    dense = [i for i, (k, _) in nodes.items() if k == "DENSE"]
    if not dense:
        return None
    consumers, writers = set(), set()
    for a, b, pt in edges:
        if a in dense and b in nodes: consumers.add(nodes[b][0])
        if b in dense and a in nodes: writers.add(nodes[a][0])
    return {"n_dense": len(dense), "consumers": sorted(consumers), "writers": sorted(writers),
            "numeric_consumer": bool(consumers & NUMERIC), "grad_consumer": bool(consumers & GRADS),
            "has_writer": bool(writers),
            "coefficient_use": bool(consumers & (NUMERIC | GRADS))}

rows = []
for f in sorted(glob.glob(sys.argv[1] + "/STAGE_B6_DEV_*.json")):
    d = json.load(open(f))
    cell = (d.get("final_best_genotypes") or {}).get("DENSE")
    if cell:
        r = probe(json.loads(cell["genotype"]))
        if r: rows.append((f"archive best DENSE  {d['pair']}|{d['arm']}|S{d['seed']}", r))
    fa = d.get("first_admissible") or {}
    if fa.get("atrophied_genotype"):
        r = probe(json.loads(fa["atrophied_genotype"]))
        if r: rows.append((f"first-admissible atr {d['pair']}|{d['arm']}|S{d['seed']}", r))
for f in sorted(glob.glob(sys.argv[1] + "/STAGE_B6_DENSE_WITNESS_*.json")):
    d = json.load(open(f))
    for lab, key in (("witness raw", "genotype_raw"), ("witness atrophied", "genotype_atrophied")):
        if d.get(key):
            r = probe(json.loads(d[key]))
            if r: rows.append((f"{lab}          ", r))

print("%-38s %-7s %-9s %-9s %s" % ("graph", "coeff?", "numeric", "grad", "consumers of DENSE"))
for name, r in rows:
    print("%-38s %-7s %-9s %-9s %s" % (name, r["coefficient_use"], r["numeric_consumer"],
                                       r["grad_consumer"], ",".join(r["consumers"]) or "(none)"))
n = len(rows); c = sum(1 for _, r in rows if r["coefficient_use"]); w = sum(1 for _, r in rows if r["has_writer"])
print(f"\nDENSE-bearing graphs inspected: {n} | with any coefficient use (DOT/LINEAR/GRAD): {c} | with any writer: {w}")
