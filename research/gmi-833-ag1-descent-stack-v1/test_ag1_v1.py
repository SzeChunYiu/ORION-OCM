# -*- coding: utf-8 -*-
"""AG1/AG8 tests: two-route agreement, detected hostiles, null, no-alarm case.

Every hostile is applied to a deep copy of the registry and paired with the
clean counter value, so the test proves the check MOVES the quantity the
hostile perturbs rather than merely reporting a rejection.

    python3 -I -O -B test_ag1_v1.py
"""

import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import foundation_dag_v1 as A   # noqa: E402

FAIL = []


def check(name, cond, detail=""):
    if not cond:
        FAIL.append("%s %s" % (name, detail))
    return cond


def load():
    dag = json.load(open(os.path.join(HERE, "FOUNDATION_DEPENDENCY_DAG_V1.json")))
    obl = json.load(open(os.path.join(HERE, "AG8_DESCENT_OBLIGATIONS_V1.json")))
    return dag, obl


def edge_index(dag, frm, to):
    for i, e in enumerate(dag["edges"]):
        if e["from"] == frm and e["to"] == to:
            return i
    raise KeyError((frm, to))


def node_index(dag, nid):
    for i, n in enumerate(dag["nodes"]):
        if n["id"] == nid:
            return i
    raise KeyError(nid)


def main():
    dag, obl = load()
    res = json.load(open(os.path.join(HERE, "RESULT_V1.json")))
    ora = json.load(open(os.path.join(HERE, "ORACLE_RESULT_V1.json")))

    clean, first, n_nodes, n_edges = A.audit(dag, obl)

    # ---------------- no-alarm case on the real registry ------------------
    check("NO_ALARM_ALL_COUNTERS_ZERO", all(x == 0 for x in clean.values()), str(clean))
    check("NO_ALARM_STATUS_GREEN", res["status"] == "GREEN" and res["failed_gates"] == [])
    check("NO_ALARM_TEN_LAYERS", res["layers_populated"] == 10)

    # ---------------- two materially independent routes -------------------
    check("ROUTE_NODES", res["nodes"] == ora["nodes"] == 32)
    check("ROUTE_EDGES", res["edges"] == ora["edges"] == 37)
    check("ROUTE_ACYCLIC", clean["cycles"] == 0 and ora["acyclic_by_kahn"]
          and ora["kahn_nodes_removed"] == 32)
    check("ROUTE_G0_LAYER", res["g0_layer"] == ora["g0_layer"] == "F4")
    check("ROUTE_G0_REACHES_F0", ora["g0_reaches_F0_by_transitive_closure"])
    check("ROUTE_LAYER_HISTOGRAM", res["nodes_per_layer"] == ora["nodes_per_layer"])
    check("ROUTE_DIVERGENCE", res["first_divergence_layer"] == ora["first_divergence_layer"] == "F6")
    check("ROUTE_UPWARD", clean["monotonicity_violations"] == ora["upward_edges"] == 0)
    check("ROUTE_WITNESS", clean["missing_witness_field"] == ora["missing_witness_fields"] == 0)
    check("ROUTE_PINS", clean["pin_violations"] == ora["pin_violations"] == 0)
    check("ROUTE_BOTTOMS", clean["bottom_exposure_violations"] == ora["bottom_without_assumptions"] == 0)
    check("ROUTE_PRIMITIVE", clean["primitive_provenance_violations"]
          == ora["primitive_provenance_violations"] == 0)

    # ---------------- hostiles, each with a moved counter -----------------
    detected = {}

    def hostile(name, counter, mutate, obl_mutate=None):
        d = copy.deepcopy(dag)
        o = copy.deepcopy(obl)
        mutate(d)
        if obl_mutate:
            obl_mutate(o)
        v, _f, _n, _e = A.audit(d, o)
        moved = v[counter] > clean[counter]
        detected[name] = moved
        check("%s_MOVES" % name, moved,
              "%s clean=%d hostile=%d" % (counter, clean[counter], v[counter]))
        return v

    # H1 pure intra-layer 2-cycle: the place a cycle can actually hide.
    def m1(d):
        e = d["edges"][edge_index(d, "THR_DISTINGUISHABILITY", "THR_OPERATIONAL_EQUIVALENCE")]
        back = dict(e)
        back["from"], back["to"] = e["to"], e["from"]
        d["edges"].append(back)
    v1 = hostile("H1_INTRA_LAYER_CYCLE", "cycles", m1)
    check("H1_IS_A_PURE_CYCLE",
          v1["monotonicity_violations"] == 0 and v1["undeclared_intra_layer"] == 0,
          "the cycle hostile must not also trip the layer gates")

    # H2 an arrow pointing up a layer.
    def m2(d):
        i = edge_index(d, "OPF_PROCESS_FRAME", "FND_SET_RELATION")
        d["edges"][i]["from"], d["edges"][i]["to"] = "FND_SET_RELATION", "OPF_PROCESS_FRAME"
    hostile("H2_UPWARD_EDGE", "monotonicity_violations", m2)

    # H3 a silent same-layer edge.
    def m3(d):
        d["edges"][edge_index(d, "CAP_PREDICTOR", "CAP_AJ8_BOUNDARY")].pop("intra_layer")
    hostile("H3_UNDECLARED_INTRA_LAYER", "undeclared_intra_layer", m3)

    # H4 a bottom node that hides its metatheoretic assumptions.
    def m4(d):
        d["nodes"][node_index(d, "PHY_SUBSTRATE_LAW")]["metatheoretic_assumptions"] = []
    hostile("H4_BOTTOM_ASSUMPTIONS_STRIPPED", "bottom_exposure_violations", m4)

    # H5 a primitive that does not name the lower layer it comes from.
    def m5(d):
        d["nodes"][node_index(d, "ADM_S")]["introduced_from_layer"] = None
    hostile("H5_PRIMITIVE_WITHOUT_PROVENANCE", "primitive_provenance_violations", m5)

    # H6 a one-way "mutual" interpretation.
    def m6(d):
        d["edges"].pop(edge_index(d, "FND_TYPED_ALGEBRAIC", "FND_SET_RELATION"))
    hostile("H6_ASYMMETRIC_MUTUAL_INTERPRETATION", "mutual_symmetry_violations", m6)

    # H7 G0 re-promoted to the bottom layer.
    def m7(d):
        d["nodes"][node_index(d, "GRM_G0")]["layer"] = "F0"
    hostile("H7_G0_PROMOTED_TO_F0", "demotion_violations", m7)

    # H8 an arrow outside the closed vocabulary.
    def m8(d):
        d["edges"][edge_index(d, "GRM_G0", "SIG_G0")]["kind"] = "IS_RELATED_TO"
    hostile("H8_UNTYPED_ARROW", "unknown_edge_kind", m8)

    # H9 an arrow with no witness.
    def m9(d):
        d["edges"][edge_index(d, "MDL_G0_LOWERED", "GRM_G0")]["witness"] = {}
    hostile("H9_WITNESSLESS_ARROW", "missing_edge_witness", m9)

    # H10 a witness field that is not in the cited receipt.
    def m10(d):
        d["edges"][edge_index(d, "MDL_G0_LOWERED", "GRM_G0")]["witness"]["field"] = "not_a_field"
    hostile("H10_WITNESS_FIELD_ABSENT", "missing_witness_field", m10)

    # H11 a corrupted parent pin.
    def m11(d):
        k = sorted(d["parent_pins"])[0]
        d["parent_pins"][k]["blob_sha"] = "0" * 40
    hostile("H11_CORRUPTED_PARENT_PIN", "pin_violations", m11)

    # H12 an AG8 obligation with no discharge.
    hostile("H12_UNDISCHARGED_OBLIGATION", "obligation_violations",
            lambda d: None,
            lambda o: o["obligations"][3].__setitem__("discharge", {}))

    # H13 an assumption tagged outside the AJ12 class vocabulary.
    def m13(d):
        d["nodes"][node_index(d, "RES_COST_MODEL")]["metatheoretic_assumptions"][0]["class"] = "VIBES"
    hostile("H13_UNTAGGED_ASSUMPTION_CLASS", "untagged_assumption_class", m13)

    # H14 a tampered divergence profile: the first-divergence answer must move.
    d14 = copy.deepcopy(dag)
    d14["divergence_profile"]["SYS_ONE_EDIT"]["F5"] = "MDL_SOMETHING_ELSE"
    _v, f14, _n, _e = A.audit(d14, obl)
    detected["H14_TAMPERED_DIVERGENCE_PROFILE"] = (f14 != first and f14 == "F5")
    check("H14_MOVES", f14 == "F5" and first == "F6", "%s -> %s" % (first, f14))

    check("ALL_HOSTILES_DETECTED", all(detected.values()),
          str([k for k in detected if not detected[k]]))
    check("HOSTILE_COUNT", len(detected) == 14, str(len(detected)))

    # ---------------- null: 200 randomised registries ---------------------
    ids = [n["id"] for n in dag["nodes"]]
    pkgs = sorted(dag["parent_pins"])
    kinds = [k for k in dag["arrow_vocabulary"] if k != "MUTUAL_INTERPRETATION"]
    seed = 4241963
    passes = 0
    for _ in range(200):
        d = copy.deepcopy(dag)
        for n in d["nodes"]:
            seed = (1103515245 * seed + 12345) % (2 ** 31)
            n["layer"] = A.LAYER_ORDER[seed % 10]
        new_edges = []
        for _k in range(37):
            seed = (1103515245 * seed + 12345) % (2 ** 31)
            a = ids[seed % len(ids)]
            seed = (1103515245 * seed + 12345) % (2 ** 31)
            b = ids[seed % len(ids)]
            seed = (1103515245 * seed + 12345) % (2 ** 31)
            k = kinds[seed % len(kinds)]
            seed = (1103515245 * seed + 12345) % (2 ** 31)
            p = pkgs[seed % len(pkgs)]
            new_edges.append({"from": a, "to": b, "kind": k,
                              "witness": {"package": p, "field": "status"}})
        d["edges"] = new_edges
        v, f, _n, _e = A.audit(d, obl)
        if all(x == 0 for x in v.values()) and f == "F6":
            passes += 1
    check("NULL_ZERO", passes == 0, "passes=%d/200" % passes)

    if FAIL:
        for f in FAIL:
            sys.stderr.write("FAIL %s\n" % f)
        return 1
    summary = {"tests": "PASS", "hostiles_detected": len(detected),
               "null_passes": passes, "routes": 2, "nodes": n_nodes, "edges": n_edges,
               "first_divergence_layer": first}
    with open(os.path.join(HERE, "TEST_RESULT_V1.json"), "w") as fh:
        json.dump(summary, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
