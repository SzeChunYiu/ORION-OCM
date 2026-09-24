#!/usr/bin/env python3
"""Fixtures and differential runners for gmi-833-aa1-gap-graph-v1.

Shared by `test_gap_graph_v1.py` and `check_receipt_v1.py`. It imports both
routes; it is the harness, not a route. Three counterexample-generation methods
live here, each run against BOTH routes:

  * HAND_CONSTRUCTED_ADVERSARIAL - a clean fixture and a table of planted
    positives, one per finding code, each of which must fire;
  * BOUNDED_EXHAUSTIVE_ENUMERATION - every directed graph on 3 labelled gap
    nodes with self-loops (512) and on 4 without (4096), checked against a
    brute-force mutual-reachability oracle; and the full promotion cubes;
  * PROPERTY_BASED_RANDOMIZED - seeded random graphs and seeded random
    mutations of the real AD loop document, compared route A vs route B.
"""
import copy
import itertools
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import gap_graph_v1 as A                      # noqa: E402
import independent_gap_graph_oracle_v1 as B   # noqa: E402

SCHEMA = A.load_schema()
OGS = A.load_open_gap_schema()
TEMPLATE = A.load_template()
SEED_GRAPHS = 8390839
SEED_LOOPS = 8390840
GRADES = A.GRADES
FLAGS = A.CLOSURE_FLAGS

MAT = {
    "IMMATERIAL": {"severity": "INFO", "evidence_mode": "INDEPENDENTLY_REPLICATED", "scope": "LOCAL", "blast": 0},
    "MINOR": {"severity": "MAJOR", "evidence_mode": "INDEPENDENTLY_REPLICATED", "scope": "PACKAGE", "blast": 0},
    "MATERIAL": {"severity": "MAJOR", "evidence_mode": "FINITE_EXACT", "scope": "PACKAGE", "blast": 1},
    "CRITICAL": {"severity": "CRITICAL", "evidence_mode": "ASSERTED", "scope": "FLAGSHIP", "blast": 0},
}


def ev(*on):
    return dict((k, k in on) for k in FLAGS)


def gap(nid, claim, parent, grade_name, state="OPEN", evidence=None):
    mi = dict(MAT[grade_name])
    idx, grade = A.materiality_of(mi, OGS)
    return {"id": nid, "kind": "GAP", "key": nid[4:].split("#")[0], "occurrence": 1, "origin": "FIXTURE",
            "pointer": "fixture", "gap_kind": "FIXTURE", "claim_id": claim, "parent_result": parent,
            "materiality": grade, "materiality_index": idx, "materiality_inputs": mi,
            "closure_state": state, "closure_evidence": evidence or ev()}


def repair(nid, grade, assumptions, new_gaps):
    return {"closed_gap_id": nid, "repair_description": "fixture repair", "new_assumptions": list(assumptions),
            "new_gaps": list(new_gaps), "interrogation_answered": True, "closure_grade_awarded": grade}


def slot(i, cls=None, outcome=None, pointer=None, scope=None):
    if cls is None:
        return {"slot": i, "method_class": None, "evidence_pointer": None, "search_scope": None, "outcome": None}
    return {"slot": i, "method_class": cls, "evidence_pointer": pointer if pointer is not None else "fixture::slot",
            "search_scope": scope if scope is not None else "fixture scope",
            "outcome": outcome or "NO_COUNTEREXAMPLE_FOUND"}


def record(rid, flagship, slots, state="OPEN", evidence=None):
    return {
        "result_id": rid, "statement": "fixture result %s" % rid,
        "scope": "FLAGSHIP" if flagship else "PACKAGE", "is_flagship": flagship,
        "assumptions": ["fixture assumption"], "dependencies": ["fixture dependency"],
        "falsifiers": ["fixture falsifier"], "counterexample_methods": slots,
        "strongest_parents": ["fixture parent"],
        "prior_disclosure": {"freeze_pointer": "fixture/FREEZE_V1.md", "outcome_timing": "PRE_OUTCOME"},
        "evidence": {"evidence_level": "FINITE_EXACT", "maturity_level": "UNREGISTERED"},
        "forbidden_extrapolations": ["COMPLETE_GMI"], "closure_state": state,
        "closure_evidence": evidence or ev(), "provenance": {"statement": "fixture"},
    }


def result_node(rec):
    return {"id": "RESULT:" + rec["result_id"], "kind": "RESULT", "key": rec["result_id"],
            "closure_state": rec["closure_state"], "closure_evidence": dict(rec["closure_evidence"]),
            "record": rec}


def finish(graph):
    """Fill the derived fields (descendant_gaps, unresolved_descendant_gaps)
    exactly as the builder does, so a clean fixture is clean."""
    ctx = A.Context(graph, SCHEMA, OGS)
    for n in graph["nodes"]:
        if n.get("kind") == "GAP":
            n["descendant_gaps"] = sorted(ctx.closure(n["id"]))
        elif n.get("kind") == "CLAIM":
            n["unresolved_descendant_gaps"] = sorted(ctx.claim_unresolved(n["key"]))
    return graph


def _clean_build():
    g1, g2 = "GAP:g1#1", "GAP:g2#1"
    n1 = gap(g1, "c1", "P", "MINOR", "LOCALLY_CLOSED", ev("local_checks_pass", "independent_route"))
    n1["repair_delta"] = repair(g1, "LOCALLY_CLOSED", ["A1"], [g2])
    n2 = gap(g2, "c2", "P", "CRITICAL")
    r1 = record("R1", True, [slot(1, "BOUNDED_EXHAUSTIVE_ENUMERATION"), slot(2, "PROPERTY_BASED_RANDOMIZED")],
                "HOSTILE_CLOSED", ev("local_checks_pass", "independent_route", "hostiles_detected"))
    r2 = record("R2", False, [slot(1)])
    graph = {
        "schema": "GMI_GAP_GRAPH_V3",
        "nodes": [
            {"id": "PARENT:P", "kind": "PARENT", "key": "P", "closure_state": "OPEN", "closure_evidence": ev()},
            {"id": "CLAIM:c1", "kind": "CLAIM", "key": "c1"},
            {"id": "CLAIM:c2", "kind": "CLAIM", "key": "c2"},
            n1, n2,
            {"id": "ASSUMPTION:A1", "kind": "ASSUMPTION", "key": "A1", "text": "fixture assumption"},
            result_node(r1), result_node(r2),
        ],
        "edges": [
            ["PARENT_OF", "PARENT:P", g1, "PARENT_RESULT_FIELD"],
            ["PARENT_OF", "PARENT:P", g2, "PARENT_RESULT_FIELD"],
            ["GAP_ON", g1, "CLAIM:c1", "CLAIM_ID_FIELD"],
            ["GAP_ON", g2, "CLAIM:c2", "CLAIM_ID_FIELD"],
            ["DEPENDS_ON", "CLAIM:c2", "CLAIM:c1", "REGISTER_DELTA_CLAIM_DEPENDENCIES"],
            ["DESCENDANT", g1, g2, "R2_DEPENDENCY_PROPAGATION"],
            ["INTRODUCES", g1, "ASSUMPTION:A1", "REPAIR_DELTA_NEW_ASSUMPTIONS"],
        ],
    }
    return finish(graph)


_BASE = []


def clean():
    """A deep copy of the clean fixture (built once)."""
    if not _BASE:
        _BASE.append(_clean_build())
    return copy.deepcopy(_BASE[0])


def node(graph, nid):
    for n in graph["nodes"]:
        if n.get("id") == nid:
            return n
    raise KeyError(nid)


def _drop_edge(graph, edge):
    graph["edges"] = [e for e in graph["edges"] if e[:3] != edge]


def _m(fn):
    def run():
        g = clean()
        fn(g)
        return g
    return run


def _dup(g):
    g["nodes"].append(copy.deepcopy(node(g, "GAP:g2#1")))


def _promote_g1_hostile(g):
    n = node(g, "GAP:g1#1")
    n["closure_state"] = "HOSTILE_CLOSED"
    n["closure_evidence"] = ev("local_checks_pass", "independent_route", "hostiles_detected")
    n["repair_delta"]["closure_grade_awarded"] = "HOSTILE_CLOSED"


def _set(nid, key, value):
    def f(g):
        node(g, nid)[key] = value
    return f


def _rec(rid, key, value):
    def f(g):
        n = node(g, "RESULT:" + rid)
        if value is _DELETE:
            del n["record"][key]
        else:
            n["record"][key] = value
    return f


_DELETE = object()


def _rd(key, value):
    def f(g):
        node(g, "GAP:g1#1")["repair_delta"][key] = value
    return f


def _replicated_r2(g):
    n = node(g, "RESULT:R2")
    full = ev(*FLAGS)
    n["closure_state"] = "REPLICATED_CLOSED"
    n["closure_evidence"] = dict(full)
    n["record"]["closure_state"] = "REPLICATED_CLOSED"
    n["record"]["closure_evidence"] = dict(full)


def _close_parent(g):
    n = node(g, "PARENT:P")
    n["closure_state"] = "LOCALLY_CLOSED"
    n["closure_evidence"] = ev("local_checks_pass", "independent_route")


def _r1_slots(slots):
    def f(g):
        node(g, "RESULT:R1")["record"]["counterexample_methods"] = slots
    return f


# name -> (builder, code that MUST fire). Every code in the schema has >= 1 row.
PLANTED = [
    ("duplicate_node", _m(_dup), "DUPLICATE_NODE_ID"),
    ("unknown_node_kind", _m(lambda g: g["nodes"].append({"id": "X:1", "kind": "FOO"})), "UNKNOWN_KIND"),
    ("unknown_edge_kind", _m(lambda g: g["edges"].append(["BAR", "GAP:g1#1", "GAP:g2#1", "x"])), "UNKNOWN_KIND"),
    ("malformed_edge", _m(lambda g: g["edges"].append(["DESCENDANT", "GAP:g1#1"])), "UNKNOWN_KIND"),
    ("edge_endpoint_kind", _m(lambda g: g["edges"].append(["DESCENDANT", "CLAIM:c1", "GAP:g2#1", "x"])),
     "EDGE_ENDPOINT_KIND"),
    ("dangling_edge", _m(lambda g: g["edges"].append(["DESCENDANT", "GAP:g1#1", "GAP:none#1", "x"])),
     "MISSING_PARENT"),
    ("missing_parent_field", _m(_set("GAP:g2#1", "parent_result", "Q")), "MISSING_PARENT"),
    ("missing_claim_field", _m(_set("GAP:g2#1", "claim_id", "c9")), "MISSING_PARENT"),
    ("missing_assumption_node", _m(_rd("new_assumptions", ["A7"])), "MISSING_PARENT"),
    ("orphan_gap", _m(lambda g: _drop_edge(g, ["PARENT_OF", "PARENT:P", "GAP:g2#1"])), "ORPHAN_GAP"),
    ("orphan_assumption", _m(lambda g: g["nodes"].append(
        {"id": "ASSUMPTION:A9", "kind": "ASSUMPTION", "key": "A9", "text": "x"})), "ORPHAN_ASSUMPTION"),
    ("orphan_claim", _m(lambda g: g["nodes"].append({"id": "CLAIM:c9", "kind": "CLAIM", "key": "c9"})),
     "ORPHAN_CLAIM"),
    ("descendant_cycle", _m(lambda g: g["edges"].append(["DESCENDANT", "GAP:g2#1", "GAP:g1#1", "x"])), "CYCLE"),
    ("dependency_cycle", _m(lambda g: g["edges"].append(["DEPENDS_ON", "CLAIM:c1", "CLAIM:c2", "x"])), "CYCLE"),
    ("self_loop", _m(lambda g: g["edges"].append(["DESCENDANT", "GAP:g2#1", "GAP:g2#1", "x"])), "SELF_LOOP"),
    ("bare_closed_lower", _m(_set("GAP:g2#1", "closure_state", "closed")), "BARE_CLOSED"),
    ("bare_closed_title", _m(_set("GAP:g2#1", "closure_state", "Closed")), "BARE_CLOSED"),
    ("bare_closed_parent", _m(_set("PARENT:P", "closure_state", "CLOSED")), "BARE_CLOSED"),
    ("unknown_state", _m(_set("GAP:g2#1", "closure_state", "DONE")), "UNKNOWN_CLOSURE_STATE"),
    ("closed_without_repair", _m(lambda g: node(g, "GAP:g1#1").pop("repair_delta")),
     "CLOSED_WITHOUT_REPAIR_DELTA"),
    ("repair_grade_mismatch", _m(_rd("closure_grade_awarded", "HOSTILE_CLOSED")), "CLOSED_WITHOUT_REPAIR_DELTA"),
    ("closed_without_new_assumptions", _m(_rd("new_assumptions", [])), "CLOSED_WITHOUT_NEW_ASSUMPTIONS"),
    ("new_gaps_mismatch", _m(_rd("new_gaps", [])), "DESCENDANT_RECORD_MISMATCH"),
    ("descendant_field_mismatch", _m(_set("GAP:g1#1", "descendant_gaps", [])), "DESCENDANT_RECORD_MISMATCH"),
    ("claim_cone_mismatch", _m(_set("CLAIM:c1", "unresolved_descendant_gaps", [])), "DESCENDANT_RECORD_MISMATCH"),
    ("lattice_evidence", _m(_set("GAP:g1#1", "closure_evidence", ev("local_checks_pass"))),
     "LATTICE_EVIDENCE_MISSING"),
    ("critical_descendant_blocks", _m(_promote_g1_hostile), "CRITICAL_DESCENDANT_BLOCKS_PROMOTION"),
    ("flagship_one_method", _m(_r1_slots([slot(1, "BOUNDED_EXHAUSTIVE_ENUMERATION"), slot(2)])),
     "FLAGSHIP_METHODS_MISSING"),
    ("flagship_same_class", _m(_r1_slots([slot(1, "BOUNDED_EXHAUSTIVE_ENUMERATION"),
                                          slot(2, "BOUNDED_EXHAUSTIVE_ENUMERATION")])),
     "FLAGSHIP_METHODS_MISSING"),
    ("flagship_counterexample_on_record", _m(_r1_slots([
        slot(1, "BOUNDED_EXHAUSTIVE_ENUMERATION"),
        slot(2, "PROPERTY_BASED_RANDOMIZED", "COUNTEREXAMPLE_FOUND")])), "FLAGSHIP_METHODS_MISSING"),
    ("flagship_slots_malformed", _m(_r1_slots("two methods")), "FLAGSHIP_METHODS_MISSING"),
    ("flagship_empty_pointer", _m(_r1_slots([slot(1, "BOUNDED_EXHAUSTIVE_ENUMERATION"),
                                             slot(2, "PROPERTY_BASED_RANDOMIZED", pointer="")])),
     "FLAGSHIP_METHODS_MISSING"),
    ("forbidden_grade", _m(_replicated_r2), "FORBIDDEN_GRADE_AWARDED"),
    ("parent_closed_with_critical", _m(_close_parent), "PARENT_CLOSED_WITH_CRITICAL_DESCENDANT"),
    ("materiality_mismatch", _m(_set("GAP:g2#1", "materiality", "MINOR")), "MATERIALITY_MISMATCH"),
    ("materiality_input_undeclared", _m(_set("GAP:g2#1", "materiality_inputs",
                                             {"severity": "HUGE", "evidence_mode": "ASSERTED",
                                              "scope": "LOCAL", "blast": 0})), "MATERIALITY_MISMATCH"),
    ("record_missing_prior_disclosure", _m(_rec("R2", "prior_disclosure", _DELETE)), "RESULT_RECORD_INVALID"),
    ("record_empty_list", _m(_rec("R2", "assumptions", [])), "RESULT_RECORD_INVALID"),
    ("record_partial_slot", _m(_rec("R2", "counterexample_methods", [
        {"slot": 1, "method_class": "PROOF_ASSISTANT", "evidence_pointer": None,
         "search_scope": None, "outcome": None}])), "RESULT_RECORD_INVALID"),
]


def _close_g2(g):
    n = node(g, "GAP:g2#1")
    n["closure_state"] = "LOCALLY_CLOSED"
    n["closure_evidence"] = ev("local_checks_pass", "independent_route")
    n["repair_delta"] = repair("GAP:g2#1", "LOCALLY_CLOSED", ["A1"], [])
    g["edges"].append(["INTRODUCES", "GAP:g2#1", "ASSUMPTION:A1", "REPAIR_DELTA_NEW_ASSUMPTIONS"])


def _diamond(g):
    for name, claim in (("g3", "c2"), ("g4", "c2")):
        g["nodes"].append(gap("GAP:%s#1" % name, claim, "P", "MINOR"))
        g["edges"].append(["PARENT_OF", "PARENT:P", "GAP:%s#1" % name, "PARENT_RESULT_FIELD"])
        g["edges"].append(["GAP_ON", "GAP:%s#1" % name, "CLAIM:" + claim, "CLAIM_ID_FIELD"])
    g["edges"] += [["DESCENDANT", "GAP:g1#1", "GAP:g3#1", "x"], ["DESCENDANT", "GAP:g2#1", "GAP:g4#1", "x"],
                   ["DESCENDANT", "GAP:g3#1", "GAP:g4#1", "x"]]
    node(g, "GAP:g1#1")["repair_delta"]["new_gaps"] = ["GAP:g2#1", "GAP:g3#1"]


def _material_only(g):
    n = node(g, "GAP:g2#1")
    idx, grade = A.materiality_of(MAT["MATERIAL"], OGS)
    n["materiality_inputs"] = dict(MAT["MATERIAL"])
    n["materiality"], n["materiality_index"] = grade, idx


def _nonflagship_hostile(g):
    n = node(g, "RESULT:R2")
    e = ev("local_checks_pass", "independent_route", "hostiles_detected")
    n["closure_state"] = n["record"]["closure_state"] = "HOSTILE_CLOSED"
    n["closure_evidence"] = dict(e)
    n["record"]["closure_evidence"] = dict(e)


# name -> builder; each must raise NO finding in either route.
CLEAN = [
    ("clean_fixture", clean),
    ("resolved_critical_descendant_does_not_block",
     lambda: finish(_then(clean(), [_close_g2, _promote_g1_hostile]))),
    ("material_not_critical_does_not_block",
     lambda: finish(_then(clean(), [_material_only, _promote_g1_hostile]))),
    ("non_flagship_needs_no_methods", lambda: finish(_then(clean(), [_nonflagship_hostile]))),
    ("diamond_is_not_a_cycle", lambda: finish(_then(clean(), [_diamond]))),
    ("parent_open_with_critical_is_fine", clean),
]


def _then(g, fns):
    for f in fns:
        f(g)
    return g


# ---------------------------------------------------------------- runners
def codes(findings):
    return sorted(set(f[0] for f in findings))


def run_planted():
    rows = []
    for name, build, code in PLANTED:
        g = build()
        fa, fb = A.validate(g), B.validate(g)
        rows.append({"name": name, "expected": code, "route_a_fired": code in codes(fa),
                     "route_b_fired": code in codes(fb), "routes_identical": fa == fb})
    return rows


def run_clean():
    rows = []
    for name, build in CLEAN:
        g = build()
        fa, fb = A.validate(g), B.validate(g)
        rows.append({"name": name, "route_a_findings": len(fa), "route_b_findings": len(fb)})
    return rows


def _digraph_fixture(k, bits):
    nodes = [{"id": "PARENT:P", "kind": "PARENT", "key": "P", "closure_state": "OPEN", "closure_evidence": ev()},
             {"id": "CLAIM:c", "kind": "CLAIM", "key": "c"}]
    edges = []
    names = ["GAP:v%d#1" % i for i in range(k)]
    for nm in names:
        nodes.append(gap(nm, "c", "P", "MINOR"))
        edges.append(["PARENT_OF", "PARENT:P", nm, "PARENT_RESULT_FIELD"])
        edges.append(["GAP_ON", nm, "CLAIM:c", "CLAIM_ID_FIELD"])
    for (i, j) in bits:
        edges.append(["DESCENDANT", names[i], names[j], "x"])
    return {"nodes": nodes, "edges": edges}, names


def _brute_cycles(k, bits, names):
    r = [[False] * k for _ in range(k)]
    for (i, j) in bits:
        r[i][j] = True
    for m in range(k):
        for i in range(k):
            for j in range(k):
                if r[i][m] and r[m][j]:
                    r[i][j] = True
    comps, done = [], set()
    for i in range(k):
        if i in done:
            continue
        comp = [j for j in range(k) if j == i or (r[i][j] and r[j][i])]
        done.update(comp)
        if len(comp) >= 2:
            comps.append("DESCENDANT:" + "|".join(sorted(names[j] for j in comp)))
    loops = ["DESCENDANT:" + names[i] for i in range(k) if (i, i) in bits]
    return sorted(comps), sorted(loops)


def exhaustive_digraphs():
    stats = {"graphs": 0, "with_cycle": 0, "with_self_loop": 0, "route_disagreements": 0,
             "oracle_disagreements": 0}
    for k, allow_self in ((3, True), (4, False)):
        pairs = [(i, j) for i in range(k) for j in range(k) if allow_self or i != j]
        for mask in range(1 << len(pairs)):
            bits = set(pairs[t] for t in range(len(pairs)) if mask >> t & 1)
            g, names = _digraph_fixture(k, bits)
            fa, fb = A.validate(g), B.validate(g)
            stats["graphs"] += 1
            if fa != fb:
                stats["route_disagreements"] += 1
            cyc = sorted(f[1] for f in fa if f[0] == "CYCLE")
            slf = sorted(f[1] for f in fa if f[0] == "SELF_LOOP")
            exp_c, exp_s = _brute_cycles(k, bits, names)
            if (cyc, slf) != (exp_c, exp_s):
                stats["oracle_disagreements"] += 1
            stats["with_cycle"] += int(bool(cyc))
            stats["with_self_loop"] += int(bool(slf))
    return stats


def exhaustive_gap_promotions():
    """g1 closed with descendant g2: every g2 state x g2 materiality x g1 evidence
    mask x g1 repair variant x requested grade."""
    stats = {"cases": 0, "granted": 0, "route_disagreements": 0, "blocked_by_critical": 0}
    states = list(SCHEMA["closure_states"]) + ["closed"]
    requested = GRADES + ["closed", "OPEN"]
    for st in states:
        for mname in MAT:
            for mask in range(32):
                for variant in ("valid", "missing", "no_assumptions"):
                    for req in requested:
                        g = clean()
                        n2 = node(g, "GAP:g2#1")
                        idx, grade = A.materiality_of(MAT[mname], OGS)
                        n2.update({"closure_state": st, "materiality_inputs": dict(MAT[mname]),
                                   "materiality": grade, "materiality_index": idx})
                        n1 = node(g, "GAP:g1#1")
                        n1["closure_evidence"] = dict((f, bool(mask >> i & 1)) for i, f in enumerate(FLAGS))
                        if variant == "missing":
                            n1.pop("repair_delta")
                        else:
                            n1["repair_delta"]["closure_grade_awarded"] = req
                            if variant == "no_assumptions":
                                n1["repair_delta"]["new_assumptions"] = []
                        ra = A.evaluate_promotion(g, "GAP:g1#1", req, SCHEMA, OGS)
                        rb = B.promote(g, "GAP:g1#1", req)
                        stats["cases"] += 1
                        stats["granted"] += int(ra["granted"])
                        stats["blocked_by_critical"] += int("CRITICAL_DESCENDANT_BLOCKS_PROMOTION" in ra["reasons"])
                        if ra != rb:
                            stats["route_disagreements"] += 1
    return stats


def exhaustive_flagship_promotions():
    """Every slot pair x flagship-flag variant x requested grade x evidence."""
    options = [None, ("BOUNDED_EXHAUSTIVE_ENUMERATION", "NO_COUNTEREXAMPLE_FOUND"),
               ("BOUNDED_EXHAUSTIVE_ENUMERATION", "COUNTEREXAMPLE_FOUND"),
               ("PROPERTY_BASED_RANDOMIZED", "NO_COUNTEREXAMPLE_FOUND"), "partial"]
    flags = [True, False, "missing", "yes"]
    stats = {"cases": 0, "granted_hostile_or_higher": 0, "route_disagreements": 0,
             "flagship_granted_without_two_methods": 0}
    for o1, o2 in itertools.product(options, options):
        slots = []
        for i, o in ((1, o1), (2, o2)):
            if o is None:
                slots.append(slot(i))
            elif o == "partial":
                slots.append({"slot": i, "method_class": "PROOF_ASSISTANT", "evidence_pointer": None,
                              "search_scope": None, "outcome": None})
            else:
                slots.append(slot(i, o[0], o[1]))
        distinct_ok = len(set(o[0] for o in (o1, o2) if isinstance(o, tuple))) >= 2 and \
            not any(isinstance(o, tuple) and o[1] == "COUNTEREXAMPLE_FOUND" for o in (o1, o2))
        for fl in flags:
            for req in GRADES + ["closed"]:
                for full in (True, False):
                    g = clean()
                    rec = node(g, "RESULT:R1")["record"]
                    rec["counterexample_methods"] = copy.deepcopy(slots)
                    if fl == "missing":
                        rec.pop("is_flagship")
                    else:
                        rec["is_flagship"] = fl
                    node(g, "RESULT:R1")["closure_evidence"] = ev(*FLAGS) if full else ev()
                    ra = A.evaluate_promotion(g, "RESULT:R1", req, SCHEMA, OGS, forbidden=[])
                    rb = B.promote(g, "RESULT:R1", req, forbidden=[])
                    stats["cases"] += 1
                    if ra != rb:
                        stats["route_disagreements"] += 1
                    if ra["granted"] and req in GRADES[1:]:
                        stats["granted_hostile_or_higher"] += 1
                        treated_flagship = fl is not False
                        if treated_flagship and not distinct_ok:
                            stats["flagship_granted_without_two_methods"] += 1
    return stats


def exhaustive_parent_promotions():
    stats = {"cases": 0, "granted": 0, "route_disagreements": 0, "granted_with_open_critical": 0}
    for st in list(SCHEMA["closure_states"]) + ["closed"]:
        for mname in MAT:
            for mask in range(32):
                for req in GRADES:
                    g = clean()
                    n2 = node(g, "GAP:g2#1")
                    idx, grade = A.materiality_of(MAT[mname], OGS)
                    n2.update({"closure_state": st, "materiality_inputs": dict(MAT[mname]),
                               "materiality": grade, "materiality_index": idx})
                    node(g, "PARENT:P")["closure_evidence"] = dict(
                        (f, bool(mask >> i & 1)) for i, f in enumerate(FLAGS))
                    ra = A.evaluate_promotion(g, "PARENT:P", req, SCHEMA, OGS, forbidden=[])
                    rb = B.promote(g, "PARENT:P", req, forbidden=[])
                    stats["cases"] += 1
                    stats["granted"] += int(ra["granted"])
                    if ra != rb:
                        stats["route_disagreements"] += 1
                    if ra["granted"] and mname == "CRITICAL" and st not in GRADES:
                        stats["granted_with_open_critical"] += 1
    return stats


def random_graph(rng):
    """A seeded random graph. About a third are DISCIPLINED (declared parents and
    claims, acyclic descendant edges, valid repair records, correct derived
    fields, OPEN/LOCALLY_CLOSED only) so that clean cases are exercised too; the
    rest are NOISY and hit every finding code."""
    disciplined = rng.random() < 0.35
    states = list(SCHEMA["closure_states"]) + ["closed", "DONE"]
    parents = ["P", "Q"]
    claims = ["c1", "c2", "c3"]
    nodes, edges = [], []
    for p in parents:
        st = "OPEN" if disciplined else rng.choice(["OPEN", "OPEN", "LOCALLY_CLOSED", "HOSTILE_CLOSED"])
        nodes.append({"id": "PARENT:" + p, "kind": "PARENT", "key": p, "closure_state": st,
                      "closure_evidence": dict((f, rng.random() < 0.6) for f in FLAGS)})
    for c in claims:
        nodes.append({"id": "CLAIM:" + c, "kind": "CLAIM", "key": c})
    for a in ("A1", "A2"):
        nodes.append({"id": "ASSUMPTION:" + a, "kind": "ASSUMPTION", "key": a, "text": a})
    k = rng.randint(2, 7)
    gids = ["GAP:r%d#1" % i for i in range(k)]
    for nid in gids:
        mname = rng.choice(sorted(MAT))
        if disciplined:
            st = rng.choice(["OPEN", "LOCALLY_CLOSED"])
            evid = ev("local_checks_pass", "independent_route") if st != "OPEN" else ev()
            n = gap(nid, rng.choice(claims), rng.choice(parents), mname, st, evid)
        else:
            st = rng.choice(states)
            n = gap(nid, rng.choice(claims + ["c9"] if rng.random() < 0.1 else claims),
                    rng.choice(parents + ["Z"] if rng.random() < 0.1 else parents), mname, st,
                    dict((f, rng.random() < 0.6) for f in FLAGS))
            if rng.random() < 0.1:
                n["materiality"] = rng.choice(sorted(MAT))
        nodes.append(n)
        if disciplined or rng.random() < 0.9:
            edges.append(["PARENT_OF", "PARENT:" + n["parent_result"], nid, "x"])
        edges.append(["GAP_ON", nid, "CLAIM:" + n["claim_id"], "x"])
    for _ in range(rng.randint(0, 2 * k)):
        i, j = rng.randrange(k), rng.randrange(k)
        if disciplined and i >= j:
            continue
        edges.append(["DESCENDANT", gids[i], gids[j], "x"])
    for _ in range(rng.randint(0, 3)):
        i, j = rng.randrange(3), rng.randrange(3)
        if disciplined and i >= j:
            continue
        edges.append(["DEPENDS_ON", "CLAIM:" + claims[i], "CLAIM:" + claims[j], "x"])
    if not disciplined and rng.random() < 0.1:
        edges.append([rng.choice(["BAR", "DESCENDANT"]), rng.choice(gids), rng.choice(["CLAIM:c1", "GAP:zz#1"]), "x"])
    ctx = A.Context({"nodes": nodes, "edges": edges}, SCHEMA, OGS)
    for n in nodes:
        if n["kind"] == "GAP":
            if n["closure_state"] != "OPEN" and (disciplined or rng.random() < 0.85):
                if disciplined:
                    assumptions = rng.choice([["A1"], ["A2"], ["A1", "A2"]])
                else:
                    assumptions = rng.choice([["A1"], ["A2"], ["A1", "A2"], [], ["A9"]])
                succ = sorted(ctx.succ("DESCENDANT", n["id"]))
                keep = disciplined or rng.random() < 0.9
                n["repair_delta"] = repair(n["id"], n["closure_state"] if keep else "LOCALLY_CLOSED",
                                           assumptions, succ if (disciplined or rng.random() < 0.85) else [])
                for a in assumptions:
                    if disciplined or rng.random() < 0.9:
                        edges.append(["INTRODUCES", n["id"], "ASSUMPTION:" + a, "x"])
            if rng.random() < 0.5:
                n["descendant_gaps"] = []
    for a in ("A1", "A2"):
        if disciplined and not any(e[0] == "INTRODUCES" and e[2] == "ASSUMPTION:" + a for e in edges):
            nodes = [n for n in nodes if n["id"] != "ASSUMPTION:" + a]
    ctx = A.Context({"nodes": nodes, "edges": edges}, SCHEMA, OGS)
    for n in nodes:
        if n["kind"] == "GAP" and "descendant_gaps" in n and (disciplined or rng.random() < 0.8):
            n["descendant_gaps"] = sorted(ctx.closure(n["id"]))
        if n["kind"] == "CLAIM" and rng.random() < 0.5:
            n["unresolved_descendant_gaps"] = sorted(ctx.claim_unresolved(n["key"])) \
                if (disciplined or rng.random() < 0.8) else []
    if disciplined:
        used = set()
        for e in edges:
            used.add(e[1])
            used.add(e[2])
        nodes = [n for n in nodes if n["kind"] != "CLAIM" or n["id"] in used]
    for i in range(rng.randint(0, 2)):
        opts = [None, ("BOUNDED_EXHAUSTIVE_ENUMERATION", "NO_COUNTEREXAMPLE_FOUND"),
                ("PROPERTY_BASED_RANDOMIZED", "NO_COUNTEREXAMPLE_FOUND"),
                ("PROPERTY_BASED_RANDOMIZED", "COUNTEREXAMPLE_FOUND")]
        slots = []
        for j in (1, 2):
            o = rng.choice(opts)
            slots.append(slot(j) if o is None else slot(j, o[0], o[1]))
        st = "OPEN" if disciplined else rng.choice(states[:5])
        rec = record("X%d" % i, rng.random() < 0.6, slots, st, dict((f, rng.random() < 0.6) for f in FLAGS))
        if not disciplined and rng.random() < 0.15:
            rec.pop(rng.choice(sorted(rec)))
        nodes.append(result_node(rec) if "closure_state" in rec and "result_id" in rec and "closure_evidence" in rec
                     else {"id": "RESULT:broken%d" % i, "kind": "RESULT", "key": "broken%d" % i,
                           "closure_state": "OPEN", "closure_evidence": ev(), "record": rec})
    if not disciplined and rng.random() < 0.1:
        nodes.append(copy.deepcopy(rng.choice(nodes)))
    return {"nodes": nodes, "edges": edges}


def randomized_graphs(trials=300, seed=SEED_GRAPHS):
    rng = random.Random(seed)
    stats = {"trials": trials, "seed": seed, "route_disagreements": 0, "trials_with_findings": 0,
             "trials_without_findings": 0, "codes_exercised": []}
    seen = set()
    for _ in range(trials):
        g = random_graph(rng)
        fa, fb = A.validate(g), B.validate(g)
        if fa != fb:
            stats["route_disagreements"] += 1
        if fa:
            stats["trials_with_findings"] += 1
        else:
            stats["trials_without_findings"] += 1
        seen.update(f[0] for f in fa)
    stats["codes_exercised"] = sorted(seen)
    return stats


LOOP_MUTATIONS = [
    "drop_step", "swap_steps", "status_bad", "evidence_blank", "reason_blank", "s12_not_run",
    "gaps_empty", "gap_field_blank", "gap_severity_mismatch", "gap_inputs_undeclared", "gap_duplicate_id",
    "assumption_silent_add", "assumption_silent_remove", "change_bad_ref", "continuity_break",
    "iteration_number", "stop_reason_bad", "stop_no_material_while_material", "repeat_with_reason",
    "decision_bad", "iteration_after_stop", "source_rule_bad",
]


def mutate_loop(doc, name, rng):
    d = copy.deepcopy(doc)
    loop = d["loops"][0]
    it = loop["iterations"][rng.randrange(len(loop["iterations"]))]
    if name == "drop_step":
        it["steps"].pop(rng.randrange(len(it["steps"])))
    elif name == "swap_steps":
        i = rng.randrange(len(it["steps"]) - 1)
        it["steps"][i], it["steps"][i + 1] = it["steps"][i + 1], it["steps"][i]
    elif name == "status_bad":
        rng.choice(it["steps"])["status"] = "SKIPPED"
    elif name == "evidence_blank":
        s = [x for x in it["steps"] if x["status"] == "DONE"]
        rng.choice(s)["evidence"] = " "
    elif name == "reason_blank":
        s = [x for x in it["steps"] if x["status"] != "DONE"]
        if s:
            rng.choice(s)["reason"] = ""
    elif name == "s12_not_run":
        it["steps"][-1] = {"step": "S12_NEW_GAP_EXTRACTION", "status": "NOT_RUN", "reason": "no time"}
    elif name == "gaps_empty":
        it["extracted_gaps"] = []
    elif name == "gap_field_blank":
        rng.choice(it["extracted_gaps"])[rng.choice(["premise", "evidence_needed", "owner_role"])] = ""
    elif name == "gap_severity_mismatch":
        rng.choice(it["extracted_gaps"])["severity"] = "INFO"
    elif name == "gap_inputs_undeclared":
        rng.choice(it["extracted_gaps"])["materiality_inputs"]["scope"] = "GALAXY"
    elif name == "gap_duplicate_id":
        it["extracted_gaps"].append(copy.deepcopy(it["extracted_gaps"][0]))
    elif name == "assumption_silent_add":
        it["assumptions_after"] = it["assumptions_after"] + ["A-SILENT: an edited assumption"]
    elif name == "assumption_silent_remove":
        it["assumptions_after"] = it["assumptions_after"][1:]
    elif name == "change_bad_ref":
        if it["assumption_changes"]:
            rng.choice(it["assumption_changes"])["gap_ref"] = "GAP-NOWHERE"
    elif name == "continuity_break":
        loop["iterations"][-1]["assumptions_before"] = loop["iterations"][-1]["assumptions_before"][:-1]
    elif name == "iteration_number":
        it["iteration"] = 7
    elif name == "stop_reason_bad":
        loop["iterations"][-1]["stop_reason"] = "CHECKLIST_TOO_LONG"
    elif name == "stop_no_material_while_material":
        loop["iterations"][-1]["stop_reason"] = "NO_MATERIAL_GAP_AT_THRESHOLD"
    elif name == "repeat_with_reason":
        loop["iterations"][0]["stop_reason"] = "DECLARED_EVIDENCE_CEILING_REACHED"
    elif name == "decision_bad":
        it["decision"] = "PAUSE"
    elif name == "iteration_after_stop":
        extra = copy.deepcopy(loop["iterations"][-1])
        extra["iteration"] = len(loop["iterations"]) + 1
        extra["assumptions_before"] = list(loop["iterations"][-1]["assumptions_after"])
        extra["assumptions_after"] = list(extra["assumptions_before"])
        extra["assumption_changes"] = []
        for gi, gg in enumerate(extra["extracted_gaps"]):
            gg["id"] = gg["id"] + "-X%d" % gi
        loop["iterations"].append(extra)
    elif name == "source_rule_bad":
        rng.choice(it["extracted_gaps"])["source_rule"] = "EVERYTHING"
    return d


def randomized_loops(trials=200, seed=SEED_LOOPS):
    doc = A.load_json(A.OWN["loops"])
    rng = random.Random(seed)
    stats = {"trials": trials, "seed": seed, "route_disagreements": 0, "trials_rejected": 0,
             "mutations_never_rejected": []}
    rejected = dict((m, 0) for m in LOOP_MUTATIONS)
    applied = dict((m, 0) for m in LOOP_MUTATIONS)
    for t in range(trials):
        name = LOOP_MUTATIONS[t % len(LOOP_MUTATIONS)]
        d = mutate_loop(doc, name, rng)
        fa, fb = A.validate_loops(d), B.validate_loops(d)
        applied[name] += 1
        if fa != fb:
            stats["route_disagreements"] += 1
        if fa:
            stats["trials_rejected"] += 1
            rejected[name] += 1
    stats["mutations_never_rejected"] = sorted(m for m in LOOP_MUTATIONS if applied[m] and not rejected[m])
    return stats


if __name__ == "__main__":
    print(json.dumps({"planted": run_planted(), "clean": run_clean()}, indent=1))
