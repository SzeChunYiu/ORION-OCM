#!/usr/bin/env python3
"""RV-377-160 IG-5 coverage check: does the independently selected alphabet cover every registered carrier class?

Mechanical checks on the blind author's alphabet (GMIIG5IndependentAlphabetV1):
  1. schema fields present; label and served_model recorded;
  2. no kind name contains a forbidden architecture-macro token;
  3. required classes non-empty; type closure (no dead types);
  4. every EXPRESSED parent compilation typechecks against the author's OWN signatures
     (ports typed, each input port bound exactly once, parameters exactly as declared, acyclic,
     exactly one served-output node);
  5. description overhead = independent node count / native reference node count, per parent;
     class COVERED iff every parent of the class is EXPRESSED, typechecks and overhead <= 2.0;
     a parent declared NOT_EXPRESSIBLE makes its class NAMED_INEXPRESSIBLE (recorded, not RED);
     any EXPRESSED parent that fails typecheck or exceeds 2x makes its class RED.

Native reference sizes: the seven R4 zoo adapters (node counts of the registered genotypes) and two
native genotypes for the belief and dynamical parents written here in the native alphabet and typechecked
by the native typechecker (the zoo has no belief or dynamical adapter; these are description-level
references, not behavioural ones, and are recorded as such).
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
M = os.path.dirname(HERE)
sys.path.insert(0, M)
from gmi_microscope import morph, zoo  # noqa: E402

FORBIDDEN = {"TRANSFORMER", "RAG", "MIXTURE_OF_EXPERTS", "MOE", "VRQM", "VGSC", "RQM", "IQL", "LMHM", "SCDI", "CNN", "LSTM",
             "GRU", "NEURON", "BACKPROP", "ATTENTION", "KNN", "GRADIENT_NET", "BAYES", "PARTICLE_FILTER", "RETRIEVAL_AUGMENTED",
             "CONVOLUTION", "RECURRENT_UNIT", "PERCEPTRON", "DIFFUSION_MODEL", "AUTOREGRESSIVE"}
REQUIRED_CLASSES = ("state", "routing", "transform", "update", "verification", "interface")
CLASSES = {"memory": ("m1_exact_table", "m2_nearest_exemplar", "m3_soft_retrieval"),
           "coefficient": ("c1_threshold_net",),
           "program_search": ("p1_program_search", "p2_population_search", "p3_compile_then_serve"),
           "belief": ("b1_finite_belief",), "dynamical": ("d1_linear_recurrence",)}


def native_belief():
    """Native-alphabet belief carrier: posterior weights as a DENSE block gating per-hypothesis affine
    predictions, linear readout, multiplicative reweighting approximated by GRAD on the posterior block."""
    return morph.make({0: ("INPUT", {"width": 4}), 1: ("DENSE", {"width": 4}), 2: ("DENSE", {"width": 20}),
                       3: ("AFFINE", {"width": 4}), 4: ("GATE", {}), 5: ("DENSE", {"width": 5}), 6: ("LINEAR", {}),
                       7: ("OUTPUT", {}), 8: ("TARGET", {}), 9: ("GRAD", {"lr": 4}), 10: ("GRAD", {"lr": 4})},
                      [(2, 3, 0), (0, 3, 1), (1, 4, 0), (3, 4, 1), (4, 6, 0), (5, 6, 1), (6, 7, 0),
                       (1, 9, 0), (6, 9, 1), (8, 9, 2), (5, 10, 0), (6, 10, 1), (8, 10, 2)],
                      meta={"zoo": "native_belief_reference"})


def native_dynamical():
    """Native-alphabet dynamical carrier: a persistent scalar state read (LOOKUP), advanced by a linear map of the
    input (LINEAR over a DENSE block) summed with the previous state (SUM), written back (INSERT); read-modify-write
    phase of the memory carrier, served directly."""
    return morph.make({0: ("INPUT", {"width": 4}), 1: ("TABLE", {"keybits": 1}), 2: ("LOOKUP", {}), 3: ("DENSE", {"width": 4}),
                       4: ("LINEAR", {}), 5: ("SUM", {}), 6: ("INSERT", {}), 7: ("OUTPUT", {}), 8: ("TARGET", {}),
                       9: ("GRAD", {"lr": 4})},
                      [(1, 2, 0), (0, 2, 1), (0, 4, 0), (3, 4, 1), (2, 5, 0), (4, 5, 1), (1, 6, 0), (0, 6, 1), (5, 6, 2),
                       (5, 7, 0), (3, 9, 0), (5, 9, 1), (8, 9, 2)],
                      meta={"zoo": "native_dynamical_reference"})


NATIVE_REF = {
    "m1_exact_table": ("zoo.exemplar_table", zoo.exemplar_table), "m2_nearest_exemplar": ("zoo.hamming_knn_k3", lambda: zoo.hamming_knn(3)),
    "m3_soft_retrieval": ("zoo.soft_retrieval", zoo.soft_retrieval), "c1_threshold_net": ("zoo.gradient_net_h2", lambda: zoo.gradient_net(2)),
    "p1_program_search": ("zoo.program_search", zoo.program_search), "p2_population_search": ("zoo.particles_p4", lambda: zoo.particles(4)),
    "p3_compile_then_serve": ("zoo.compiled_search", zoo.compiled_search),
    "b1_finite_belief": ("native_belief_reference(this script)", native_belief),
    "d1_linear_recurrence": ("native_dynamical_reference(this script)", native_dynamical),
}


def typecheck_independent(comp: dict, kinds: dict, served_kind: str) -> list[str]:
    errs = []
    nodes = comp.get("nodes", {})
    edges = comp.get("edges", [])
    for nid, spec in nodes.items():
        if not (isinstance(spec, list) and len(spec) == 2 and spec[0] in kinds and isinstance(spec[1], dict)):
            errs.append(f"node {nid}: malformed or unknown kind {spec!r}")
            continue
        k, params = spec
        want = list(kinds[k].get("params", []))
        if sorted(params) != sorted(want):
            errs.append(f"node {nid} ({k}): params {sorted(params)} != declared {sorted(want)}")
        if any(not isinstance(v, int) or isinstance(v, bool) for v in params.values()):
            errs.append(f"node {nid} ({k}): non-integer parameter")
    if errs:
        return errs
    bound = {}
    preds = {n: [] for n in nodes}
    for e in edges:
        if not (isinstance(e, list) and len(e) == 3):
            errs.append(f"malformed edge {e!r}")
            continue
        a, b, pt = e
        if a not in nodes or b not in nodes:
            errs.append(f"edge {e}: unknown node")
            continue
        ka, kb = nodes[a][0], nodes[b][0]
        ins = kinds[kb]["inputs"]
        if not isinstance(pt, int) or pt < 0 or pt >= len(ins):
            errs.append(f"edge {e}: port {pt} out of range for {kb} ({len(ins)} inputs)")
            continue
        if kinds[ka]["output"] != ins[pt]:
            errs.append(f"edge {e}: type {kinds[ka]['output']} into port {pt} of {kb} expecting {ins[pt]}")
        if (b, pt) in bound:
            errs.append(f"node {b} port {pt} bound twice")
        bound[(b, pt)] = a
        preds[b].append(a)
    for nid, (k, _) in nodes.items():
        for pt in range(len(kinds[k]["inputs"])):
            if (nid, pt) not in bound:
                errs.append(f"node {nid} ({k}) port {pt} unbound")
    served = [n for n, (k, _) in nodes.items() if k == served_kind]
    if len(served) != 1:
        errs.append(f"expected exactly one served-output node of kind {served_kind}, found {len(served)}")
    # acyclicity
    state = {}

    def visit(n, stack):
        if n in stack:
            raise ValueError("cycle")
        if state.get(n):
            return
        for p in preds[n]:
            visit(p, stack | {n})
        state[n] = True
    try:
        for n in nodes:
            visit(n, frozenset())
    except ValueError:
        errs.append("cycle in dataflow graph")
    return errs


def main() -> int:
    alpha_path, out_path = sys.argv[1], sys.argv[2]
    raw = open(alpha_path, "rb").read()
    rep = {"schema": "GMIIG5IndependentAlphabetCoverageV1", "revival_id": "RV-377-160",
           "label": "HUMAN_GATE_BYPASSED__MODEL_PROXY", "host": platform.node(), "python": platform.python_version(),
           "alphabet_sha256": hashlib.sha256(raw).hexdigest(), "structural_errors": []}
    try:
        alpha = json.loads(raw)
    except Exception as e:  # noqa: BLE001
        rep["structural_errors"].append(f"json parse failure: {e!r}")
        rep["P2_STATUS"] = "RED__ALPHABET_UNPARSEABLE"
        json.dump(rep, open(out_path, "w"), indent=1, sort_keys=True)
        print(json.dumps({"P2_STATUS": rep["P2_STATUS"]}))
        return 2
    errs = rep["structural_errors"]
    for k in ("schema", "served_model", "label", "types", "answer_type", "kinds", "parent_compilations", "served_output_kind"):
        if k not in alpha:
            errs.append(f"missing top-level key {k}")
    if errs:
        rep["P2_STATUS"] = "RED__ALPHABET_SCHEMA"
        json.dump(rep, open(out_path, "w"), indent=1, sort_keys=True)
        print(json.dumps({"P2_STATUS": rep["P2_STATUS"], "errors": errs}))
        return 2
    kinds = alpha["kinds"]
    rep["served_model_asserted_by_blind_author"] = alpha["served_model"]
    rep["label_recorded_by_blind_author"] = alpha["label"]
    rep["n_kinds"] = len(kinds)
    rep["n_types"] = len(alpha["types"])
    # macro check
    macro_hits = [k for k in kinds if any(tok in k.upper() for tok in FORBIDDEN)]
    rep["forbidden_macro_kind_names"] = macro_hits
    # classes
    by_class = {}
    for k, spec in kinds.items():
        by_class.setdefault(spec.get("class"), []).append(k)
    rep["kinds_by_class"] = by_class
    rep["required_classes_missing"] = [c for c in REQUIRED_CLASSES if not by_class.get(c)]
    # type closure
    produced = {spec["output"] for spec in kinds.values()}
    consumed = {t for spec in kinds.values() for t in spec["inputs"]}
    declared = set(alpha["types"])
    rep["type_closure"] = {
        "dead_outputs(not consumed, not answer)": sorted(produced - consumed - {alpha["answer_type"]}),
        "unproducible_inputs": sorted(consumed - produced),
        "undeclared_types": sorted((produced | consumed) - declared),
    }
    # parents
    parents = {}
    class_status = {}
    for cls, pids in CLASSES.items():
        statuses = []
        for pid in pids:
            comp = alpha["parent_compilations"].get(pid)
            ref_name, ref_fn = NATIVE_REF[pid]
            ref_g = ref_fn()
            morph.typecheck(ref_g)
            n_native = len(ref_g["nodes"])
            row = {"class": cls, "native_reference": ref_name, "native_nodes": n_native}
            if comp is None:
                row.update({"status": "MISSING", "verdict": "RED"})
            elif comp.get("status") == "NOT_EXPRESSIBLE":
                row.update({"status": "NOT_EXPRESSIBLE", "note": comp.get("note"), "verdict": "NAMED_INEXPRESSIBLE"})
            else:
                te = typecheck_independent(comp, kinds, alpha["served_output_kind"])
                n_ind = len(comp.get("nodes", {}))
                overhead = n_ind / n_native
                row.update({"status": "EXPRESSED", "independent_nodes": n_ind, "overhead": overhead,
                            "typecheck_errors": te,
                            "verdict": "COVERED" if not te and overhead <= 2.0 else "RED"})
            parents[pid] = row
            statuses.append(row["verdict"])
        class_status[cls] = ("RED" if "RED" in statuses else "NAMED_INEXPRESSIBLE" if "NAMED_INEXPRESSIBLE" in statuses else "COVERED")
    rep["parents"] = parents
    rep["class_status"] = class_status
    hard_red = bool(macro_hits) or bool(rep["required_classes_missing"]) or bool(rep["type_closure"]["unproducible_inputs"]) \
        or bool(rep["type_closure"]["undeclared_types"]) or any(v == "RED" for v in class_status.values())
    if hard_red:
        rep["P2_STATUS"] = "RED"
    elif all(v == "COVERED" for v in class_status.values()):
        rep["P2_STATUS"] = "GREEN__ALL_FIVE_CLASSES_COVERED"
    else:
        rep["P2_STATUS"] = "NAMED_LIMIT__" + "_".join(c for c, v in class_status.items() if v != "COVERED")
    rep["dead_output_types_note"] = "dead output types are reported as a defect but are not a RED condition for coverage"
    json.dump(rep, open(out_path, "w"), indent=1, sort_keys=True)
    print(json.dumps({"P2_STATUS": rep["P2_STATUS"], "class_status": class_status,
                      "overheads": {p: r.get("overhead") for p, r in parents.items()},
                      "typecheck_errors": {p: len(r.get("typecheck_errors", [])) for p, r in parents.items()},
                      "macros": macro_hits, "closure": rep["type_closure"]}, sort_keys=True))
    return 0 if not hard_red else 2


if __name__ == "__main__":
    raise SystemExit(main())
