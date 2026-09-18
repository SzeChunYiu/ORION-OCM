# -*- coding: utf-8 -*-
"""AG1/AG8 route A -- validate the F0..F9 FOUNDATION_DEPENDENCY_DAG_V1.

Route A walks the graph with depth-first search (colour-marking cycle
detection, DFS reachability) and checks each gate directly on the node/edge
records.  The independent oracle (independent_oracle_v1.py) recomputes the same
quantities by Kahn in-degree peeling and boolean transitive closure over an
adjacency matrix, reading the JSON with its own parser and importing nothing
from this file.

Stdlib only.  All arithmetic is integer or fractions.Fraction.

    python3 -I -B foundation_dag_v1.py
"""

import hashlib
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
DAG_PATH = os.path.join(HERE, "FOUNDATION_DEPENDENCY_DAG_V1.json")
OBL_PATH = os.path.join(HERE, "AG8_DESCENT_OBLIGATIONS_V1.json")

LAYER_ORDER = ["F0", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"]


def blob_sha(path):
    with open(path, "rb") as fh:
        data = fh.read()
    h = hashlib.sha1()
    h.update(b"blob " + str(len(data)).encode("ascii") + b"\x00")
    h.update(data)
    return h.hexdigest()


def rank(layer):
    return LAYER_ORDER.index(layer)


def audit(dag, obligations, repo=REPO):
    """Return a dict of violation COUNTS.  Every gate is a count so that a
    hostile can be shown to move it."""
    nodes = dag["nodes"]
    edges = dag["edges"]
    vocab = set(dag["arrow_vocabulary"])
    classes = set(dag["assumption_classes"])
    lowering = set(dag["lowering_vocabulary"])
    by_id = {}
    v = dict((k, 0) for k in (
        "duplicate_node_ids", "unknown_layer", "empty_layer",
        "unknown_edge_kind", "missing_edge_endpoint", "missing_edge_witness",
        "unresolved_witness_package", "missing_witness_field",
        "monotonicity_violations", "undeclared_intra_layer", "declared_intra_layer_not_same_layer",
        "cycles",
        "mutual_symmetry_violations", "mutual_layer_violations",
        "primitive_provenance_violations", "bottom_exposure_violations",
        "untagged_assumption_class", "unknown_lowering_status",
        "demotion_violations", "pin_violations", "obligation_violations",
    ))

    for n in nodes:
        if n["id"] in by_id:
            v["duplicate_node_ids"] += 1
        by_id[n["id"]] = n
        if n["layer"] not in LAYER_ORDER:
            v["unknown_layer"] += 1
    populated = set(n["layer"] for n in nodes)
    for lay in LAYER_ORDER:
        if lay not in populated:
            v["empty_layer"] += 1

    # --- edges: typing, endpoints, witnesses, layer monotonicity ----------
    receipt_cache = {}

    def receipt(pkg):
        if pkg not in receipt_cache:
            p = os.path.join(repo, "research", pkg, "RESULT_V1.json")
            try:
                with open(p) as fh:
                    receipt_cache[pkg] = json.load(fh)
            except Exception:
                receipt_cache[pkg] = None
        return receipt_cache[pkg]

    out_edges = {}
    for e in edges:
        if e["kind"] not in vocab:
            v["unknown_edge_kind"] += 1
        if e["from"] not in by_id or e["to"] not in by_id:
            v["missing_edge_endpoint"] += 1
            continue
        out_edges.setdefault(e["from"], []).append(e)
        w = e.get("witness") or {}
        if not w.get("package") or not w.get("field"):
            v["missing_edge_witness"] += 1
        else:
            doc = receipt(w["package"])
            if doc is None:
                v["unresolved_witness_package"] += 1
            elif w["field"] not in doc:
                v["missing_witness_field"] += 1
        a, b = by_id[e["from"]], by_id[e["to"]]
        if e["kind"] == "MUTUAL_INTERPRETATION":
            if rank(a["layer"]) != rank(b["layer"]):
                v["mutual_layer_violations"] += 1
            back = [x for x in edges
                    if x["from"] == e["to"] and x["to"] == e["from"]
                    and x["kind"] == "MUTUAL_INTERPRETATION"]
            if not back:
                v["mutual_symmetry_violations"] += 1
        else:
            ra, rb = rank(a["layer"]), rank(b["layer"])
            if ra < rb:
                # an arrow pointing UP a layer is never admissible
                v["monotonicity_violations"] += 1
            elif ra == rb:
                # same-layer refinement: must be declared, never silent
                if not e.get("intra_layer"):
                    v["undeclared_intra_layer"] += 1
            else:
                if e.get("intra_layer"):
                    v["declared_intra_layer_not_same_layer"] += 1

    # --- cycles over non-MUTUAL edges (DFS colouring) ---------------------
    adj = {}
    for e in edges:
        if e["kind"] == "MUTUAL_INTERPRETATION":
            continue
        if e["from"] in by_id and e["to"] in by_id:
            adj.setdefault(e["from"], []).append(e["to"])
    colour = {}
    cycle_nodes = []

    def dfs(u):
        colour[u] = 1
        for w in adj.get(u, []):
            c = colour.get(w, 0)
            if c == 1:
                cycle_nodes.append((u, w))
            elif c == 0:
                dfs(w)
        colour[u] = 2

    for n in nodes:
        if colour.get(n["id"], 0) == 0:
            dfs(n["id"])
    v["cycles"] = len(cycle_nodes)

    # --- primitive provenance and bottom exposure -------------------------
    for n in nodes:
        if n.get("lowering_status") is not None and n["lowering_status"] not in lowering:
            v["unknown_lowering_status"] += 1
        if n.get("primitive"):
            frm = n.get("introduced_from_layer")
            if frm not in LAYER_ORDER or not rank(frm) < rank(n["layer"]):
                v["primitive_provenance_violations"] += 1
        has_out = bool(out_edges.get(n["id"]))
        if not has_out:
            assum = n.get("metatheoretic_assumptions") or []
            if not assum:
                v["bottom_exposure_violations"] += 1
            for a in assum:
                if a.get("class") not in classes:
                    v["untagged_assumption_class"] += 1

    # --- G0 demotion gate --------------------------------------------------
    dem = dag["g0_demotion"]
    g0 = by_id.get(dem["node"])
    if g0 is None or g0["layer"] != dem["required_layer"] or g0["layer"] in dem["forbidden_layers"]:
        v["demotion_violations"] += 1
    else:
        # G0 must be reachable down to some F0 node along derived-from edges
        seen, stack, hit_f0 = set(), [dem["node"]], False
        while stack:
            u = stack.pop()
            if u in seen:
                continue
            seen.add(u)
            if by_id[u]["layer"] == "F0":
                hit_f0 = True
            for w in adj.get(u, []):
                stack.append(w)
        if not hit_f0:
            v["demotion_violations"] += 1

    # --- parent pin integrity ---------------------------------------------
    for pkg, pin in sorted(dag["parent_pins"].items()):
        full = os.path.join(repo, pin["path"])
        if not os.path.exists(full) or pin["blob_sha"] is None:
            v["pin_violations"] += 1
        elif blob_sha(full) != pin["blob_sha"]:
            v["pin_violations"] += 1

    # --- AG8 obligations ---------------------------------------------------
    up = obligations["upward_counterparts"]
    obs = obligations["obligations"]
    if obligations.get("direction") != "DOWNWARD" or len(obs) != 8:
        v["obligation_violations"] += 1
    steps = sorted(o["step"] for o in obs)
    if steps != list(range(1, 9)):
        v["obligation_violations"] += 1
    for o in obs:
        if not o.get("text"):
            v["obligation_violations"] += 1
        if o.get("upward_counterpart") not in up:
            v["obligation_violations"] += 1
        d = o.get("discharge") or {}
        if not d.get("check") or not d.get("package"):
            v["obligation_violations"] += 1
    hsg = up.get("HSG_REFLEXIVE_GENERALIZATION_CLOSURE", {})
    for rel in [hsg.get("ledger")] + list(hsg.get("pinned_artifacts") or []):
        if not rel or not os.path.exists(os.path.join(repo, rel)):
            v["obligation_violations"] += 1

    # --- AG7 first-divergence layer ---------------------------------------
    prof = dag["divergence_profile"]
    a, b = prof["systems"]
    first = None
    for lay in prof["layers"]:
        if prof[a][lay] != prof[b][lay]:
            first = lay
            break
    return v, first, len(nodes), len(edges)


def main():
    with open(DAG_PATH) as fh:
        dag = json.load(fh)
    with open(OBL_PATH) as fh:
        obl = json.load(fh)
    v, first, n_nodes, n_edges = audit(dag, obl)

    prof = dag["divergence_profile"]
    cap_a = Fraction(prof["capability_at_divergence"][prof["systems"][0]])
    cap_b = Fraction(prof["capability_at_divergence"][prof["systems"][1]])

    aj6 = json.load(open(os.path.join(
        REPO, "research/gmi-833-aj6-hst-layer-map-v1/RESULT_V1.json")))
    aj6_ok = (
        aj6.get("current_organization_same") is True
        and Fraction(str(aj6.get("frozen_future_best_identity_error"))) == cap_a
        and Fraction(str(aj6.get("one_edit_future_best_identity_error"))) == cap_b
    )

    layer_hist = {}
    for n in dag["nodes"]:
        layer_hist[n["layer"]] = layer_hist.get(n["layer"], 0) + 1
    kind_hist = {}
    for e in dag["edges"]:
        kind_hist[e["kind"]] = kind_hist.get(e["kind"], 0) + 1

    open_nodes = [n["id"] for n in dag["nodes"] if n.get("lowering_status") == "UNKNOWN"]

    result = {
        "schema": "AG1_DESCENT_STACK_RESULT_V1",
        "issue": 833,
        "claim_ceiling": ("AG1_AG8_TYPED_F0_F9_FOUNDATION_DEPENDENCY_DAG_AND_PRIMITIVE_"
                          "PROVENANCE_AT_REGISTERED_833_OBJECT_SCOPE"),
        "results": ["AG1-1", "AG1-2", "AG1-3", "AG1-4", "AG1-5"],
        "nodes": n_nodes,
        "edges": n_edges,
        "layers_populated": len(layer_hist),
        "nodes_per_layer": layer_hist,
        "edges_per_kind": kind_hist,
        "cross_layer_edges": sum(1 for e in dag["edges"]
                                 if e["kind"] != "MUTUAL_INTERPRETATION" and not e.get("intra_layer")),
        "intra_layer_refinement_edges": sum(1 for e in dag["edges"] if e.get("intra_layer")),
        "arrow_vocabulary": dag["arrow_vocabulary"],
        "violations": v,
        "parent_packages_pinned": len(dag["parent_pins"]),
        "g0_layer": next(n["layer"] for n in dag["nodes"] if n["id"] == "GRM_G0"),
        "g0_demotion_statement": dag["g0_demotion"]["statement"],
        "first_divergence_layer": first,
        "divergence_capability": {
            prof["systems"][0]: str(cap_a), prof["systems"][1]: str(cap_b)},
        "divergence_consistent_with_aj6_receipt": aj6_ok,
        "ag8_obligations": len(obl["obligations"]),
        "open_provenance_nodes": open_nodes,
        "forbidden_promotions": [
            "ABSOLUTE_BOTTOM_LAYER_PROVEN", "F0_IS_UNIQUE", "LAYER_ASSIGNMENT_IS_ONTOLOGY",
            "DAG_ACYCLICITY_PROVES_FOUNDATIONAL_PRIORITY",
            "G0_IRREDUCIBILITY_DISPROVED_IN_GENERAL", "COMPLETE_GMI"],
    }
    gates = [
        ("no_violations", all(x == 0 for x in v.values())),
        ("all_ten_layers_populated", len(layer_hist) == 10),
        ("g0_at_F4", result["g0_layer"] == "F4"),
        ("first_divergence_is_F6", first == "F6"),
        ("divergence_matches_aj6", aj6_ok),
        ("eight_obligations", len(obl["obligations"]) == 8),
        ("open_provenance_declared", len(open_nodes) >= 1),
    ]
    failed = [g for g, ok in gates if not ok]
    result["gates"] = dict(gates)
    result["failed_gates"] = failed
    result["status"] = "GREEN" if not failed else "RED"
    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as fh:
        json.dump(result, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps({"status": result["status"], "failed_gates": failed,
                      "violations": v, "first_divergence_layer": first},
                     sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
