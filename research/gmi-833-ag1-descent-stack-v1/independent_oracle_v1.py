# -*- coding: utf-8 -*-
"""AG1/AG8 route B -- materially independent recomputation.

Route A uses DFS colour-marking for cycles and DFS for reachability.  Route B
uses:

  * Kahn in-degree peeling for cycle detection (a graph is acyclic iff peeling
    removes every node);
  * boolean transitive closure by repeated adjacency-matrix squaring for the
    G0 -> F0 reachability question;
  * integer bitmask prefix comparison for the first-divergence layer;
  * its own pass over the JSON for layer/witness/provenance counts.

It imports nothing from foundation_dag_v1.py.  Stdlib only.

    python3 -I -B independent_oracle_v1.py
"""

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
LAYERS = ["F0", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"]


def sha(path):
    d = open(path, "rb").read()
    h = hashlib.sha1()
    h.update(b"blob " + str(len(d)).encode("ascii") + b"\x00")
    h.update(d)
    return h.hexdigest()


def main():
    dag = json.load(open(os.path.join(HERE, "FOUNDATION_DEPENDENCY_DAG_V1.json")))
    obl = json.load(open(os.path.join(HERE, "AG8_DESCENT_OBLIGATIONS_V1.json")))

    ids = [n["id"] for n in dag["nodes"]]
    idx = dict((x, i) for i, x in enumerate(ids))
    lay = dict((n["id"], LAYERS.index(n["layer"])) for n in dag["nodes"])
    size = len(ids)

    plain = [e for e in dag["edges"] if e["kind"] != "MUTUAL_INTERPRETATION"]
    mutual = [e for e in dag["edges"] if e["kind"] == "MUTUAL_INTERPRETATION"]

    # ---- Kahn peeling ----------------------------------------------------
    indeg = dict((x, 0) for x in ids)
    succ = dict((x, []) for x in ids)
    for e in plain:
        succ[e["from"]].append(e["to"])
        indeg[e["to"]] += 1
    queue = sorted(x for x in ids if indeg[x] == 0)
    removed = 0
    while queue:
        u = queue.pop()
        removed += 1
        for w in succ[u]:
            indeg[w] -= 1
            if indeg[w] == 0:
                queue.append(w)
    acyclic = (removed == size)

    # ---- boolean transitive closure by matrix squaring -------------------
    rows = [0] * size
    for e in plain:
        rows[idx[e["from"]]] |= (1 << idx[e["to"]])
    reach = list(rows)
    for _ in range(size.bit_length() + 1):
        nxt = []
        for i in range(size):
            acc = reach[i]
            bits = reach[i]
            j = 0
            while bits:
                if bits & 1:
                    acc |= reach[j]
                bits >>= 1
                j += 1
            nxt.append(acc)
        if nxt == reach:
            break
        reach = nxt
    f0_mask = 0
    for n in dag["nodes"]:
        if n["layer"] == "F0":
            f0_mask |= (1 << idx[n["id"]])
    g0_reaches_f0 = bool(reach[idx["GRM_G0"]] & f0_mask)

    # ---- independent violation recount -----------------------------------
    up_edges = sum(1 for e in plain if lay[e["from"]] < lay[e["to"]])
    same_undeclared = sum(1 for e in plain
                          if lay[e["from"]] == lay[e["to"]] and not e.get("intra_layer"))
    mutual_bad = 0
    for e in mutual:
        if lay[e["from"]] != lay[e["to"]]:
            mutual_bad += 1
        if not any(x["from"] == e["to"] and x["to"] == e["from"] for x in mutual):
            mutual_bad += 1

    out_ids = set(e["from"] for e in dag["edges"])
    bottoms = [n for n in dag["nodes"] if n["id"] not in out_ids]
    bottom_bad = sum(1 for n in bottoms if not n.get("metatheoretic_assumptions"))
    prim_bad = 0
    for n in dag["nodes"]:
        if n.get("primitive"):
            f = n.get("introduced_from_layer")
            if f not in LAYERS or LAYERS.index(f) >= lay[n["id"]]:
                prim_bad += 1

    field_bad = 0
    cache = {}
    for e in dag["edges"]:
        w = e["witness"]
        p = os.path.join(REPO, "research", w["package"], "RESULT_V1.json")
        if p not in cache:
            cache[p] = json.load(open(p)) if os.path.exists(p) else None
        doc = cache[p]
        if doc is None or w["field"] not in doc:
            field_bad += 1

    pin_bad = 0
    for _pkg, pin in sorted(dag["parent_pins"].items()):
        full = os.path.join(REPO, pin["path"])
        if not os.path.exists(full) or sha(full) != pin["blob_sha"]:
            pin_bad += 1

    # ---- divergence layer by bitmask prefix ------------------------------
    prof = dag["divergence_profile"]
    a, b = prof["systems"]
    mask = 0
    for i, lname in enumerate(prof["layers"]):
        if prof[a][lname] != prof[b][lname]:
            mask |= (1 << i)
    first = prof["layers"][(mask & -mask).bit_length() - 1] if mask else None

    per_layer = {}
    for n in dag["nodes"]:
        per_layer[n["layer"]] = per_layer.get(n["layer"], 0) + 1

    out = {
        "schema": "AG1_ORACLE_RESULT_V1",
        "route": "KAHN_PEELING_PLUS_BOOLEAN_TRANSITIVE_CLOSURE",
        "nodes": size,
        "edges": len(dag["edges"]),
        "acyclic_by_kahn": acyclic,
        "kahn_nodes_removed": removed,
        "g0_layer": dag["nodes"][[n["id"] for n in dag["nodes"]].index("GRM_G0")]["layer"],
        "g0_reaches_F0_by_transitive_closure": g0_reaches_f0,
        "upward_edges": up_edges,
        "undeclared_intra_layer": same_undeclared,
        "mutual_violations": mutual_bad,
        "bottom_nodes": len(bottoms),
        "bottom_without_assumptions": bottom_bad,
        "primitive_provenance_violations": prim_bad,
        "missing_witness_fields": field_bad,
        "pin_violations": pin_bad,
        "nodes_per_layer": per_layer,
        "layers_populated": len(per_layer),
        "first_divergence_layer": first,
        "ag8_obligations": len(obl["obligations"]),
    }
    with open(os.path.join(HERE, "ORACLE_RESULT_V1.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps(out, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
