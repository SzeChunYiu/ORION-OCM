#!/usr/bin/env python3
"""Declared write-graph vs edges that actually fire on a MicroEarth run.

PR #316 (check_noninterference.py) decides BIO-T1 on the *declared* kernel
graph. MicroEarth carries a run-level write_graph. If those two drift, or if
assay-conditioned harvest/birth fire while the assay edges were discarded,
BIO-T1 can HOLD on a stale declaration. This checker is the residual:
executed history must agree with the declared graph.

Exits are distinct on purpose. CANNOT_CHECK is never folded into PASS:

    PASS          declared graph covers executed leak/clean behaviour
    VIOLATION     leak dynamics fired on discarded assay edges (H-LEAK-HIDDEN-EDGE)
    CANNOT_CHECK  no birth occurred; a birth/death decision was never live
"""
from __future__ import annotations

import json
import sys

import micro_earth as me

PASS = "PASS"
VIOLATION = "VIOLATION"
CANNOT_CHECK = "CANNOT_CHECK"

ASSAY_EDGES = frozenset((("assay", "energy"), ("assay", "birth")))
HOSTILE_HIDDEN = "H-LEAK-HIDDEN-EDGE"

# History kind -> write-graph edges that must have been live for that event.
# Social kinds are recorded but are not assay/selection edges on this graph.
KIND_EDGES = {
    "harvest": frozenset((("resource", "energy"),)),
    "birth": frozenset((("energy", "birth"),)),
    "death": frozenset((("energy", "birth"),)),
}


def _kinds(history):
    return [h[0] for h in history]


def _births(history):
    return sum(1 for h in history if h[0] == "birth")


def _edge_list(edges):
    return sorted(tuple(e) for e in edges)


def implied_edges(history, leak_energy=False, leak_birth=False):
    """Map executed event kinds onto write-graph edges that must have been live."""
    edges = set()
    for h in history:
        kind = h[0]
        edges.update(KIND_EDGES.get(kind, ()))
        if kind == "harvest" and leak_energy:
            edges.add(("assay", "energy"))
        if kind == "birth" and leak_birth:
            edges.add(("assay", "birth"))
        if kind == "harvest" and len(h) > 2 and h[2] > 2:
            # Clean harvest is min(2, resource). take>2 is the assay bonus.
            edges.add(("assay", "energy"))
    return edges


def collect_executed(earth, ticks):
    """Step `ticks` times; record which assay-conditioned paths actually fired."""
    leak_energy = False
    leak_birth = False
    for _ in range(ticks):
        assay_at = dict((c.uid, c.assay) for c in earth.cells)
        n0 = len(earth.history)
        earth.step()
        for ev in earth.history[n0:]:
            kind = ev[0]
            uid = ev[1] if len(ev) > 1 else None
            if kind == "harvest" and assay_at.get(uid, 0) > 0:
                leak_energy = True
            if kind == "birth" and assay_at.get(uid, 0) > 0:
                leak_birth = True
    executed = implied_edges(earth.history, leak_energy=leak_energy,
                             leak_birth=leak_birth)
    return {
        "kinds": sorted(set(_kinds(earth.history))),
        "births": _births(earth.history),
        "leak_energy": leak_energy,
        "leak_birth": leak_birth,
        "executed_edges": executed,
        "declared_edges": set(earth.write_graph),
    }


def _arm_leak(earth):
    """Make assay-conditioned harvest/birth live so leak is not a stale flag."""
    for c in earth.cells:
        c.assay = 1
        c.method = earth.useful_method


def judge(declared, executed, births, leak_energy=False, leak_birth=False):
    """Compare declared write_graph to edges implied by execution."""
    declared = set(declared)
    executed = set(executed)
    if births == 0:
        return {
            "verdict": CANNOT_CHECK,
            "reason": "no births; BIO-T1 would be vacuous on this run",
            "hostile": None,
            "declared_edges": _edge_list(declared),
            "executed_edges": _edge_list(executed),
            "hidden_edges": [],
            "births": 0,
            "leak_energy": leak_energy,
            "leak_birth": leak_birth,
        }
    hidden = executed - declared
    hidden_assay = hidden & ASSAY_EDGES
    if hidden_assay:
        return {
            "verdict": VIOLATION,
            "reason": "leak dynamics fired while assay edges were discarded",
            "hostile": HOSTILE_HIDDEN,
            "declared_edges": _edge_list(declared),
            "executed_edges": _edge_list(executed),
            "hidden_edges": _edge_list(hidden_assay),
            "births": births,
            "leak_energy": leak_energy,
            "leak_birth": leak_birth,
        }
    if hidden:
        return {
            "verdict": VIOLATION,
            "reason": "executed edges missing from declared write_graph",
            "hostile": HOSTILE_HIDDEN,
            "declared_edges": _edge_list(declared),
            "executed_edges": _edge_list(executed),
            "hidden_edges": _edge_list(hidden),
            "births": births,
            "leak_energy": leak_energy,
            "leak_birth": leak_birth,
        }
    return {
        "verdict": PASS,
        "reason": "declared write_graph covers executed leak/clean behaviour",
        "hostile": None,
        "declared_edges": _edge_list(declared),
        "executed_edges": _edge_list(executed),
        "hidden_edges": [],
        "births": births,
        "leak_energy": leak_energy,
        "leak_birth": leak_birth,
    }


def check_earth(earth, ticks=8):
    """Run one world and judge declared vs executed edges."""
    collected = collect_executed(earth, ticks)
    report = judge(
        collected["declared_edges"],
        collected["executed_edges"],
        collected["births"],
        leak_energy=collected["leak_energy"],
        leak_birth=collected["leak_birth"],
    )
    report["kinds"] = collected["kinds"]
    report["leak"] = bool(earth.leak)
    return report


def check_pair(n=2, seed=0, ticks=8):
    """Clean world plus leaky world. Combined verdict is the worse of the two."""
    clean = me.MicroEarth(n, seed=seed, leak=False)
    leaky = me.MicroEarth(n, seed=seed, leak=True)
    _arm_leak(leaky)
    clean_rep = check_earth(clean, ticks=ticks)
    leak_rep = check_earth(leaky, ticks=ticks)
    order = {VIOLATION: 2, CANNOT_CHECK: 1, PASS: 0}
    combined = clean_rep["verdict"]
    if order[leak_rep["verdict"]] > order[combined]:
        combined = leak_rep["verdict"]
    hostile = None
    if combined == VIOLATION:
        hostile = HOSTILE_HIDDEN
    return {
        "verdict": combined,
        "hostile": hostile,
        "clean": clean_rep,
        "leak": leak_rep,
    }


def selftest():
    """Both directions: clean PASS, leak PASS, hidden-edge VIOLATION, birth-free CANNOT_CHECK."""
    cases = {}

    clean = me.MicroEarth(2, seed=0, leak=False)
    r = check_earth(clean, ticks=8)
    assert r["verdict"] == PASS, "clean case returned %s (%s)" % (r["verdict"], r["reason"])
    assert r["births"] > 0, "clean PASS was vacuous: no births"
    assert not (set(map(tuple, r["executed_edges"])) & ASSAY_EDGES)
    cases["clean_pass"] = r["verdict"]

    leaky = me.MicroEarth(2, seed=0, leak=True)
    _arm_leak(leaky)
    r = check_earth(leaky, ticks=8)
    assert r["verdict"] == PASS, "leak case returned %s (%s)" % (r["verdict"], r["reason"])
    assert r["births"] > 0, "leak PASS was vacuous: no births"
    assert r["leak_energy"] or r["leak_birth"], "leak PASS did not fire leak dynamics"
    executed = set(map(tuple, r["executed_edges"]))
    declared = set(map(tuple, r["declared_edges"]))
    assert executed & ASSAY_EDGES, "leak PASS executed no assay edges"
    assert ASSAY_EDGES <= declared, "leak PASS dropped assay edges from the declaration"
    cases["leak_pass"] = r["verdict"]

    hidden = me.MicroEarth(2, seed=0, leak=True)
    _arm_leak(hidden)
    collected = collect_executed(hidden, 8)
    hidden.write_graph.discard(("assay", "energy"))
    hidden.write_graph.discard(("assay", "birth"))
    r = judge(hidden.write_graph, collected["executed_edges"], collected["births"],
              leak_energy=collected["leak_energy"], leak_birth=collected["leak_birth"])
    assert r["verdict"] == VIOLATION, "hidden-edge case returned %s" % r["verdict"]
    assert r["hostile"] == HOSTILE_HIDDEN
    assert r["hidden_edges"], "VIOLATION emitted no hidden assay edges"
    cases["hidden_edge_violation"] = r["verdict"]

    barren = me.MicroEarth(2, seed=0, leak=False, kernels={"K_birthdeath": False})
    r = check_earth(barren, ticks=8)
    assert r["verdict"] == CANNOT_CHECK, "birth-free case returned %s" % r["verdict"]
    assert r["births"] == 0
    cases["birth_free_cannot_check"] = r["verdict"]

    pair = check_pair()
    assert pair["verdict"] == PASS, "paired clean+leak returned %s" % pair["verdict"]
    cases["paired_pass"] = pair["verdict"]

    return {"GRAPH_AGREEMENT_SELFTEST": "OK", "cases": cases}


def main(argv):
    if len(argv) > 2:
        print("usage: graph_agreement.py [--selftest]", file=sys.stderr)
        return 4
    if len(argv) == 2 and argv[1] == "--selftest":
        print(json.dumps(selftest(), indent=1, sort_keys=True))
        return 0
    if len(argv) == 2:
        print("usage: graph_agreement.py [--selftest]", file=sys.stderr)
        return 4
    selftest()
    report = check_pair()
    print(json.dumps(report, indent=1, sort_keys=True))
    return {"PASS": 0, "VIOLATION": 2, "CANNOT_CHECK": 3}[report["verdict"]]


if __name__ == "__main__":
    sys.exit(main(sys.argv))
