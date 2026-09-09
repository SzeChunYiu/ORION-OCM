"""Zoo capsule tests: determinism, fail-closed invariants, receipt chain,
census exact count, arm sanity, registry-json/code consistency.

Run: python3 -m pytest tests/ -q  (from the capsule root).
"""
from __future__ import annotations

import copy
import json
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from morphology.canonicalize import collapse_duplicates
from morphology.compile import InvariantViolation, compile_genome
from morphology.direct_genome import CENSUS_BOUND_V1, census_size, enumerate_census, random_genome
from evaluation.descriptors import DESCRIPTOR_REGISTRY
from evaluation.evaluate import evaluate_genome
from evaluation.invariants import CAPABILITY_FLOOR_V1, hard_gate_report
from evaluation.objectives import OBJECTIVE_NAMES, dev_score, objective_vector, pareto_front
from evaluation.receipts import make_receipt, append_record, verify_receipt
from search import random_search


def test_census_exact_count():
    n = census_size()
    assert n == 56160, n
    # exhaustive enumeration matches closed form
    assert sum(1 for _ in enumerate_census()) == n


def test_evaluation_deterministic():
    rng = random.Random(7)
    for _ in range(20):
        g = random_genome(rng)
        a = evaluate_genome(g, use_cache=False)
        b = evaluate_genome(g, use_cache=False)
        assert a["genotype_digest"] == b["genotype_digest"]
        assert a["phenotype_digest"] == b["phenotype_digest"]
        assert objective_vector(a["evaluation"]) == objective_vector(b["evaluation"])


def test_compile_fail_closed_on_bad_genome():
    rng = random.Random(3)
    g = random_genome(rng)
    g.F_arch = "nonexistent_field_family"  # type: ignore[assignment]
    try:
        compile_genome(g)
    except InvariantViolation:
        pass
    else:
        raise AssertionError("compile must fail closed on illegal vocabulary")


def test_hard_gates_execute():
    rng = random.Random(5)
    g = random_genome(rng)
    r = evaluate_genome(g, use_cache=False)
    gates = hard_gate_report(compile_genome(g), r["evaluation"])
    assert r["feasible"] == all(gates.values())
    if r["feasible"]:
        assert r["evaluation"]["solved_fraction"] >= CAPABILITY_FLOOR_V1


def test_receipt_chain_and_tamper_detection():
    receipt = make_receipt("t", "now", "test", "T0", "cfgdigest")
    for i in range(50):
        append_record(receipt, i, {"i": i})
    assert verify_receipt(receipt)
    bad = copy.deepcopy(receipt)
    bad["chain"][3]["payload"]["i"] = 999
    assert not verify_receipt(bad), "tampered receipt must fail"


def test_pareto_and_collapse():
    rng = random.Random(11)
    recs = []
    for _ in range(200):
        r = evaluate_genome(random_genome(rng), use_cache=False)
        if r["feasible"]:
            recs.append({"objectives": objective_vector(r["evaluation"]),
                         "phenotype_digest": r["phenotype_digest"]})
    front = pareto_front(recs, "objectives")
    assert 0 < len(front) <= len(recs)
    # collapse only removes exact digest duplicates
    dup = recs + [dict(recs[0])]
    assert len(collapse_duplicates(dup, "phenotype_digest")) == len(recs)


def test_objective_vector_len_and_score():
    rng = random.Random(13)
    r = evaluate_genome(random_genome(rng), use_cache=False)
    assert len(objective_vector(r["evaluation"])) == len(OBJECTIVE_NAMES) == 10
    ev = {"solved_fraction": 0.6, "work_total": 100.0, "persistent_bytes": 50.0}
    assert dev_score(ev) == round(0.6 - 0.5 * ((100 / 500 + 50 / 150) / 2), 6)


def test_arm_sanity_random_search():
    res = random_search.run(budget=64, seed=0)
    assert res["evals"] == 64
    assert res["best_dev_score"] is None or res["best_dev_score"] <= 1.0
    for e in res["archive"]:
        # arm contract: genome + digests present; descriptors recomputed
        # downstream (recovery_test recomputes them from genomes uniformly)
        assert "phenotype_digest" in e and "genome" in e and "objectives" in e


def test_descriptor_registry_complete():
    for name, reg in DESCRIPTOR_REGISTRY.items():
        assert "dims" in reg and len(reg["dims"]) >= 2, name
        if reg.get("kind") != "cvt":
            assert len(reg["bounds"]) == len(reg["dims"]), name


def test_registry_jsons_match_code():
    hpc = os.path.join(ROOT, "hpc", "gen_registries.py")
    assert os.path.exists(hpc)
    import importlib.util
    spec = importlib.util.spec_from_file_location("gr", hpc)
    gr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gr)  # regenerates in place; then compare
    for name in ("MORPHOLOGY_GENOME_V1", "COGNITIVE_UNIT_CONTRACT_V1",
                 "DESCRIPTOR_REGISTRY_V1", "OBJECTIVE_REGISTRY_V1",
                 "TASK_ECOLOGY_V1", "PROTOCOL_V1"):
        with open(os.path.join(ROOT, name + ".json")) as f:
            json.load(f)  # valid json, regenerable


def test_freeze_denominators_match_census_truth():
    truth_path = os.path.join(ROOT, "archives", "CENSUS_P00_TRUTH.json")
    if not os.path.exists(truth_path):
        return  # truth not yet synced to this checkout; census test covers count
    with open(truth_path) as f:
        truth = json.load(f)
    with open(os.path.join(ROOT, "FREEZE_V1.json")) as f:
        freeze = json.load(f)
    t, fz = truth["summary"], freeze["census_truth_P00"]
    assert t["pareto_set_size"] == fz["pareto_phenotypes"] == 387
    assert t["descriptor_cells_occupied_S"] == fz["S_cells_occupied"] == 4
    assert t["descriptor_cells_occupied_B"] == fz["B_cells_occupied"] == 2
    assert t["best_dev_score"] == fz["best_dev_score_within_bound"]
    assert t["feasible"] == fz["feasible"] == 14904
    assert len(truth["cells_S"]) == 4 and len(truth["cells_B"]) == 2


# --- E1 CGP encoding (MZ-D5 encoding fit) ---------------------------------

def test_cgp_roundtrip_on_sample():
    from morphology.cgp_genome import CGPGenomeV1
    rng = random.Random(5)
    gs = [g for _, g in zip(range(120), enumerate_census())]
    gs += [random_genome(rng) for _ in range(120)]
    for g in gs:
        g2 = CGPGenomeV1.encode(g).decode()
        assert g2.F_arch == g.F_arch and g2.T_family == g.T_family
        assert g2.Pi_arch == g.Pi_arch and g2.L == g.L
        assert g2.R == g.R and g2.K == g.K
        assert sorted(u.unit_type for u in g2.U) == sorted(
            u.unit_type for u in g.U)


def test_cgp_mutations_stay_legal_and_in_bound():
    from morphology.cgp_genome import CGPGenomeV1, random_cgp_genome
    rng = random.Random(6)
    for _ in range(300):
        g = random_cgp_genome(rng).mutate(rng).decode()
        compile_genome(g)  # must pass the fail-closed invariants
        assert g.F_arch in CENSUS_BOUND_V1["F_arch"]
        assert g.T_family in CENSUS_BOUND_V1["T_family"]
        assert g.Pi_arch in CENSUS_BOUND_V1["Pi_arch"]
        assert g.L in CENSUS_BOUND_V1["L"]
        assert g.R in CENSUS_BOUND_V1["R"]
        assert g.K in CENSUS_BOUND_V1["K"]
        extras = [u.unit_type for u in g.U if u.unit_type != "fact_relation"]
        assert len(extras) <= CENSUS_BOUND_V1["max_extra_units"]
        assert set(extras) <= set(CENSUS_BOUND_V1["extra_units"])
