"""R2 — semantic remint / exact developmental-equivalence harness and the B0 calibration stage
(GMI_BIOSPHERE_SPECIES_EQUIVALENCE_HARDENING_V1 sections 2 and 9; GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1 stage B0;
GMI_BIOSPHERE_NO_FREE_LUNCH_AND_GOODHART_GATES_V1 section 7 remint set, section 13 resource matching).

Exact relation: M1 ~_{E,J} M2 iff the developmental response R_{E,J} (served trace under every registered ecology e and
intervention j, and the capability) is identical; rho_M (the resource vector) is excluded from identity and reported as a
separate directed burden difference. One (e, j) with a different response SPLITS the pair (split theorem, section 9).
Approximate similarity is never promoted to equivalence here: pairs are either EXACT_EQUAL_AT_SCOPE or SPLIT_BY (e, j), or
UNSEPARATED_AT_CURRENT_TEST_POWER when the registered (E, J) is declared incomplete for the pair.

B0.1 same semantics / different code: implementation-equivalent rewrites of a genotype (identity routing edge, identity
nonlinearity, additive zero, constant-flag select) must be merged (identical response) with their resource difference
reported. B0.2 collisions: pairs with identical present outputs whose future update response differs must be split by the
registered interventions. B0.3 hidden cost: the channels through which an unmetered win could enter are closed by
construction (no data payload in genotypes, fixed grammar order, charged materialization, no world-id input, no external
access); the init-state audit is recorded for every genotype.
"""
from __future__ import annotations

import json
import os

from . import bases, ecology, morph, zoo
from .core import sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
DEFAULT_SPECS = ("E_smooth3", "E_sym5", "E_parity")
DEFAULT_J = ("standard", "no_revoke", "shuffled_events", "extra_unseen_feedback")


def response_vector(g, specs=DEFAULT_SPECS, interventions=DEFAULT_J, basis_name="B0_LOCAL_ADAPTIVE_TRANSDUCERS", seed=0):
    basis = bases.ALL[basis_name]; out = {}
    for s in specs:
        for j in interventions:
            r = ecology.run_genotype(ecology.REGISTRY[s], g, basis, j, seed)
            out[f"{s}|{j}"] = {"sig": ecology.response_signature(r), "capability": r["capability"], "R": r["R"], "init_audit": r["init_audit"]}
    return out


def compare(g1, g2, specs=DEFAULT_SPECS, interventions=DEFAULT_J, basis_name="B0_LOCAL_ADAPTIVE_TRANSDUCERS"):
    r1 = response_vector(g1, specs, interventions, basis_name); r2 = response_vector(g2, specs, interventions, basis_name)
    splits = [k for k in r1 if r1[k]["sig"] != r2[k]["sig"]]
    rdiff = {k: {ph: r2[k]["R"][ph] - r1[k]["R"][ph] for ph in r1[k]["R"]} for k in r1}
    return {"exact_equal": not splits, "first_split": splits[0] if splits else None, "n_split_cells": len(splits), "n_cells": len(r1), "resource_difference_by_cell": rdiff,
            "canonical_identical": morph.canonical(g1) == morph.canonical(g2), "verdict": "EXACT_EQUAL_AT_SCOPE" if not splits else f"SPLIT_BY {splits[0]}"}


# ----------------------------------------------------------------------------------------------------- B0.1 rewrites
def rewrite_identity_edge(g):
    """insert an EDGE (identity routing) between INPUT and its first consumer."""
    nodes = {i: (k, dict(p)) for i, (k, p) in g["nodes"].items()}; edges = list(g["edges"])
    inp = [i for i, (k, _) in nodes.items() if k == "INPUT"][0]
    first = [e for e in edges if e[0] == inp][0]; edges.remove(first); nid = "edge_x"
    nodes[nid] = ("EDGE", {}); edges += [(inp, nid, 0), (nid, first[1], first[2])]
    return {"nodes": nodes, "edges": edges, "meta": dict(g["meta"])}


def rewrite_identity_nonlin(g):
    """insert NONLIN1(identity) before OUTPUT."""
    nodes = {i: (k, dict(p)) for i, (k, p) in g["nodes"].items()}; edges = list(g["edges"])
    out = [i for i, (k, _) in nodes.items() if k == "OUTPUT"][0]; e = [e for e in edges if e[1] == out][0]; edges.remove(e)
    nodes["idn"] = ("NONLIN1", {"fn": 2}); edges += [(e[0], "idn", 0), ("idn", out, 0)]
    return {"nodes": nodes, "edges": edges, "meta": dict(g["meta"])}


def rewrite_add_zero(g):
    """insert SUM(., CONST 0) before OUTPUT (same map; one charged ADD per query)."""
    nodes = {i: (k, dict(p)) for i, (k, p) in g["nodes"].items()}; edges = list(g["edges"])
    out = [i for i, (k, _) in nodes.items() if k == "OUTPUT"][0]; e = [e for e in edges if e[1] == out][0]; edges.remove(e)
    nodes["zero"] = ("CONST", {"value": 0}); nodes["plus"] = ("SUM", {}); edges += [(e[0], "plus", 0), ("zero", "plus", 1), ("plus", out, 0)]
    return {"nodes": nodes, "edges": edges, "meta": dict(g["meta"])}


def rewrite_const_select(g):
    """insert SELECT(v, CONST 0, flag=NOUPDATE... ) — a constant-flag select choosing the live branch; flag from a MORPH_RULE node (evaluates to 1)."""
    nodes = {i: (k, dict(p)) for i, (k, p) in g["nodes"].items()}; edges = list(g["edges"])
    out = [i for i, (k, _) in nodes.items() if k == "OUTPUT"][0]; e = [e for e in edges if e[1] == out][0]; edges.remove(e)
    nodes["zero"] = ("CONST", {"value": 0}); nodes["flag"] = ("MORPH_RULE", {"rule": 0}); nodes["sel"] = ("SELECT", {})
    edges += [(e[0], "sel", 0), ("zero", "sel", 1), ("flag", "sel", 2), ("sel", out, 0)]
    return {"nodes": nodes, "edges": edges, "meta": dict(g["meta"])}


REWRITES = {"identity_edge": rewrite_identity_edge, "identity_nonlin": rewrite_identity_nonlin, "add_zero": rewrite_add_zero, "const_select": rewrite_const_select}


# ----------------------------------------------------------------------------------------------------- B0.2 collision pairs
def collision_pairs():
    """pairs with identical present outputs (at t = 0 and/or on seen inputs) but different future update response."""
    return {"gradient_lr4_vs_lr2": (zoo.gradient_net(2, lr=4), zoo.gradient_net(2, lr=2)),
            "table_vs_knn1": (zoo.exemplar_table(), zoo.hamming_knn(1)),
            "knn1_vs_knn3": (zoo.hamming_knn(1), zoo.hamming_knn(3)),
            "particles4_vs_particles8": (zoo.particles(4), zoo.particles(8)),
            "search_full_vs_search_budget": (zoo.program_search(2401), zoo.program_search(400))}


def main(tag="V1"):
    out = {"schema": "StageB0EquivalenceMeteringV1", "issue": [377, 422], "stage": "B0", "specs": list(DEFAULT_SPECS), "interventions": list(DEFAULT_J), "B0_1_rewrites": {}, "B0_2_collisions": {}, "B0_3_hidden_cost": {}}
    ok = True
    # B0.1: every implementation-equivalent rewrite of every zoo genotype is merged (identical response) with its resource difference reported
    for zname in ("gradient_net_h2", "hamming_knn_k3", "exemplar_table", "particles_p4"):
        g = zoo.ZOO[zname]()
        for rname, rw in REWRITES.items():
            g2 = rw(g); morph.typecheck(g2); c = compare(g, g2)
            res = {"verdict": c["verdict"], "canonical_identical": c["canonical_identical"], "exec_difference_standard_E_smooth3": c["resource_difference_by_cell"]["E_smooth3|standard"]}
            out["B0_1_rewrites"][f"{zname}|{rname}"] = res; ok &= c["exact_equal"] and not c["canonical_identical"]
    # B0.2: every collision pair is split by some registered (e, j); record where
    for pname, (g1, g2) in collision_pairs().items():
        c = compare(g1, g2); r1 = response_vector(g1, ("E_smooth3",), ("standard",)); r2 = response_vector(g2, ("E_smooth3",), ("standard",))
        # 'identical present outputs': the first served trace row (before any feedback) is identical
        first1 = ecology.run_genotype(ecology.REGISTRY["E_smooth3"], g1, bases.ALL["B0_LOCAL_ADAPTIVE_TRANSDUCERS"])["trace"][0]
        first2 = ecology.run_genotype(ecology.REGISTRY["E_smooth3"], g2, bases.ALL["B0_LOCAL_ADAPTIVE_TRANSDUCERS"])["trace"][0]
        out["B0_2_collisions"][pname] = {"identical_before_any_feedback": first1 == first2, "verdict": c["verdict"], "n_split_cells": c["n_split_cells"], "n_cells": c["n_cells"]}
        ok &= (not c["exact_equal"])
    # B0.3: hidden-cost channels
    audits = {zname: response_vector(fn(), ("E_smooth3",), ("standard",))["E_smooth3|standard"]["init_audit"] for zname, fn in zoo.ZOO.items()}
    out["B0_3_hidden_cost"] = {"init_state_audit_by_genotype": audits, "all_stores_empty_at_init": all(a["stores_nonempty_at_init"] == 0 for a in audits.values()),
                               "channels_closed_by_construction": ["precomputation: genotypes carry no data payload (parameters are small integers; CONST cells are charged description)",
                                                                   "external files/models: the VM has no external access primitive",
                                                                   "compiler tables: MATERIALIZE is charged one store insert per compiled key",
                                                                   "search prior: grammar enumeration order is fixed and the budget is a charged parameter",
                                                                   "precision/world-ID channel: the VM receives only the 4 input bits; no ecology identifier is an input",
                                                                   "human intervention: none (B_human = 0 for every genotype)"],
                               "open": ["as-of / history query intervention not yet in the registered J (needed to split VERSIONED wrappers from plain tables): OPEN_NONBLOCKING for B0, blocking for lineage-form species claims"]}
    ok &= out["B0_3_hidden_cost"]["all_stores_empty_at_init"]
    out["status"] = "GREEN" if ok else "RED"; out["terminal"] = "BIOSPHERE_B0_EQUIVALENCE_AND_METERING_GREEN" if ok else "BIOSPHERE_B0_FAILED"
    out["claim_ceiling"] = "exact developmental equivalence on the registered (E, J) at the exact layer; rewrites merge, collisions split, init audited; approximate similarity not used"
    out["receipt_sha256"] = sha256_of({k: v for k, v in out.items() if k != "receipt_sha256"})
    json.dump(out, open(os.path.join(RES, f"STAGE_B0_EQUIVALENCE_METERING_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    return out


if __name__ == "__main__":
    o = main()
    print(o["terminal"])
    for k, v in o["B0_1_rewrites"].items(): print("  B0.1", k, v["verdict"], "canon-same:", v["canonical_identical"], "exec diff:", v["exec_difference_standard_E_smooth3"]["exec"])
    for k, v in o["B0_2_collisions"].items(): print("  B0.2", k, "identical-at-t0:", v["identical_before_any_feedback"], v["verdict"], f"{v['n_split_cells']}/{v['n_cells']}")
    print("  B0.3 stores empty at init:", o["B0_3_hidden_cost"]["all_stores_empty_at_init"])
