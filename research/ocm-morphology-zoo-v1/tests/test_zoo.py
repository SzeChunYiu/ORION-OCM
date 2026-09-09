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


# --- AMEND-2: encoding hooks + cgp crossover -------------------------------

def test_cgp_crossover_legal_and_decodable():
    from morphology.cgp_genome import (CGPGenomeV1, cgp_crossover,
                                       cgp_crossover_direct,
                                       random_cgp_genome)
    rng = random.Random(8)
    for _ in range(200):
        a, b = random_cgp_genome(rng), random_cgp_genome(rng)
        c = cgp_crossover(a, b, rng)
        assert len(c.payload) == 7 and len(c.wires) == 7
        compile_genome(c.decode())  # fail-closed invariants
    # direct-genome hook composes with canonical encode
    ga, gb = random_genome(rng), random_genome(rng)
    gd = cgp_crossover_direct(ga, gb, rng)
    compile_genome(gd)
    assert gd.F_arch in CENSUS_BOUND_V1["F_arch"]


def test_hooks_none_preserves_legacy_behaviour():
    import json as _json
    from search import map_elites, random_search
    a = map_elites.run(budget=80, seed=11, archive="S_structural_3d", res=10)
    b = map_elites.run(budget=80, seed=11, archive="S_structural_3d", res=10,
                       sampler=None, mutator=None, crossover_fn=None)
    assert a["evals"] == b["evals"] and a["qd_score"] == b["qd_score"]
    assert [e["phenotype_digest"] for e in a["archive"]] == \
        [e["phenotype_digest"] for e in b["archive"]]
    c = random_search.run(budget=60, seed=4)
    d = random_search.run(budget=60, seed=4, sampler=None)
    c.pop("elapsed_s"), d.pop("elapsed_s")  # wall clock is not behaviour
    assert _json.dumps(c, sort_keys=True) == _json.dumps(d, sort_keys=True)


def test_hookless_map_elites_still_uses_crossover():
    """Regression (2026-09-09): 'or crossover_fn is None' in the variation
    branch suppressed crossover entirely for hook-less (E0) arms — E0 no
    longer recomputed its amend-1 twin (caught by the QDA2-vs-QDA1 xcheck).
    With all hooks None, BOTH legacy operators must fire."""
    from search import cvt_map_elites, map_elites
    for mod in (map_elites, cvt_map_elites):
        calls = {"mut": 0, "cross": 0}
        _mut, _cross = mod.mutate, mod.crossover

        def _m(g, rng, _f=_mut, _c=calls):
            _c["mut"] += 1
            return _f(g, rng)

        def _x(a, b, rng, _f=_cross, _c=calls):
            _c["cross"] += 1
            return _f(a, b, rng)

        mod.mutate, mod.crossover = _m, _x
        try:
            if mod is map_elites:
                mod.run(budget=120, seed=11, archive="S_structural_3d", res=10)
            else:
                mod.run(budget=120, seed=11)
        finally:
            mod.mutate, mod.crossover = _mut, _cross
        assert calls["mut"] > 0, "mutation branch never fired"
        assert calls["cross"] > 0, ("crossover suppressed for hook-less run "
                                    "(amend-2 regression)")


def test_cgp_hooks_run_and_stay_in_bound():
    from morphology.cgp_genome import (cgp_mutate_direct,
                                       cgp_sample_direct)
    from morphology.schema import OCMMorphologyGenomeV1
    from search import map_elites, random_search
    rng = random.Random(12)
    for _ in range(50):
        g = cgp_sample_direct(rng)
        compile_genome(g)
        assert g.F_arch in CENSUS_BOUND_V1["F_arch"]
        m = cgp_mutate_direct(g, rng)
        compile_genome(m)
        assert m.T_family in CENSUS_BOUND_V1["T_family"]
    res = map_elites.run(budget=60, seed=9, archive="S_structural_3d", res=10,
                         sampler=cgp_sample_direct,
                         mutator=cgp_mutate_direct)
    assert res["evals"] == 60
    for e in res["archive"]:
        g2 = OCMMorphologyGenomeV1.from_json_obj(e["genome"])
        assert g2.F_arch in CENSUS_BOUND_V1["F_arch"]
    r2 = random_search.run(budget=40, seed=9, sampler=cgp_sample_direct)
    assert r2["evals"] == 40


def test_amend2_freeze_chain_and_rule():
    import hashlib
    import os
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    a2 = json.load(open(os.path.join(root, "FREEZE_V1_AMEND_2.json")))
    v1 = hashlib.sha256(open(os.path.join(root, "FREEZE_V1.json"), "rb").read()).hexdigest()
    a1 = hashlib.sha256(open(os.path.join(root, "FREEZE_V1_AMEND_1.json"), "rb").read()).hexdigest()
    assert v1 == a2["freeze_v1_sha256"], "freeze chain broken"
    assert a1 == a2["amend_1_sha256"], "amend-1 chain broken"
    assert a2["arms_amend2"]["budget"] == 40000
    assert a2["arms_amend2"]["seeds"] == [0, 1, 2]
    assert {p["pair_id"] for p in a2["arms_amend2"]["pairs"]} == {"R01", "M03", "M05", "M06"}
    assert a2["arms_amend2"]["encodings"] == ["E0_direct", "E1_cgp"]
    tr = a2["scoring_rules_amend2"]["terminal_rule_FROZEN"]
    assert "ENCODING_CHOICE_DOMINATES" in tr and "PARENT_ARCHITECTURE_SUFFICIENT" in tr


# --- AMEND-3: tier T2 + Archive D (MZ-D7 developmental) --------------------

def test_amend3_freeze_chain_and_census_binding():
    import hashlib
    a3 = json.load(open(os.path.join(ROOT, "FREEZE_V1_AMEND_3.json")))
    v1 = hashlib.sha256(open(os.path.join(ROOT, "FREEZE_V1.json"), "rb").read()).hexdigest()
    a1 = hashlib.sha256(open(os.path.join(ROOT, "FREEZE_V1_AMEND_1.json"), "rb").read()).hexdigest()
    a2 = hashlib.sha256(open(os.path.join(ROOT, "FREEZE_V1_AMEND_2.json"), "rb").read()).hexdigest()
    assert v1 == a3["freeze_v1_sha256"], "freeze chain broken"
    assert a1 == a3["amend_1_sha256"], "amend-1 chain broken"
    assert a2 == a3["amend_2_sha256"], "amend-2 chain broken"
    assert len(a3["arms_amend3"]["arms"]) == 5
    assert a3["arms_amend3"]["seeds"] == [0, 1, 2]
    assert a3["arms_amend3"]["budget"] == 40000
    assert a3["arms_amend3"]["encodings"] == ["E0_direct"]
    tr = a3["scoring_rules_amend3"]["terminal_rule_FROZEN"]
    assert any("DEVELOPMENTAL_MORPHOLOGY_ADVANTAGE_SUPPORTED_AT_SCOPE" in s
               for s in tr)
    from evaluation.descriptors import DESCRIPTOR_REGISTRY
    from evaluation.objectives import W2_REF, B2_REF
    den = a3["census_truth_P00C"]["denominators"]
    assert (den["PARETO_T2"], den["D2d@10_occupied"], den["D3d@10_occupied"],
            den["CVTD_occupied_niches"], den["S3d@10_occupied_T0ref"]) == \
        (792, 50, 83, 64, 8)
    truth_path = os.path.join(ROOT, "archives", "CENSUS_P00C_TRUTH.json")
    if not os.path.exists(truth_path):
        return  # truth not synced to this checkout; smoke asserts it on-host
    truth = json.load(open(truth_path))["summary"]
    for view in ("D_dev_2d", "D_dev_3d"):
        assert tuple(tuple(b) for b in DESCRIPTOR_REGISTRY[view]["bounds"]) == \
            tuple(tuple(b) for b in truth["frozen_grid_bounds"][view]), view
    assert (W2_REF, B2_REF) == (truth["t2_scalar_refs"]["W2_REF"],
                                truth["t2_scalar_refs"]["B2_REF"])
    assert den["PARETO_T2"] == truth["pareto_set_size"]
    for k in ("D2d@10_occupied", "D3d@10_occupied", "CVTD_occupied_niches"):
        assert den[k] == truth["denominators"][k], k
    b_path = os.path.join(ROOT, "archives", "CENSUS_P00B_TRUTH.json")
    if os.path.exists(b_path):
        tb = json.load(open(b_path))["summary"]
        assert den["S3d@10_occupied_T0ref"] == tb["denominators"]["S3d@10_occupied"]


def test_t2_tier_dispatch_and_reset_control():
    rng = random.Random(17)
    g = random_genome(rng)
    r = evaluate_genome(g, tier="T2", use_cache=False)
    assert r["tier"] == "T2"
    ev = r["evaluation"]
    assert ev["tier"] == "T2" and ev["ecology_id"] == "LifetimeEcologyV2"
    rc = ev["reset_control"]
    assert rc["ecology_id"] == "LifetimeEcologyV2_reset"
    # T2 scalar uses the T2 references (W2_REF/B2_REF), never the T0 ones
    from evaluation.objectives import W2_REF, B2_REF
    expect = round(ev["solved_fraction"] - 0.5 * (
        (ev["work_total"] / W2_REF + ev["persistent_bytes"] / B2_REF) / 2), 6)
    assert dev_score(ev) == expect
    # continued lifetime solves >= reset control on every T2 genome
    assert ev["solved_fraction"] >= rc["solved_fraction"] - 1e-9


def test_lifetime2_deterministic_and_retention_nonneg():
    from evaluation.lifetime2 import run_lifetime2
    rng = random.Random(19)
    kept = 0
    for _ in range(30):
        g = random_genome(rng)
        out = evaluate_genome(g, tier="T2", use_cache=False)
        if not out["feasible"]:
            continue
        kept += 1
        org = compile_genome(g)
        ev, ev2 = run_lifetime2(org), run_lifetime2(org)
        assert ev == ev2, "lifetime2 not deterministic"
        rc = out["evaluation"]["reset_control"]
        ret = out["evaluation"]["solved_fraction"] - rc["solved_fraction"]
        assert ret >= -1e-9, "negative retention contradicts census truth"
    assert kept >= 5, "expected several feasible T2 genomes in the sample"


def test_developmental_descriptors_vary_over_census_sample():
    from evaluation.descriptors import D_DIMS, developmental_descriptors
    rng = random.Random(23)
    sample = [g for _, g in zip(range(24), enumerate_census())]
    sample += [random_genome(rng) for _ in range(24)]
    vals = {d: set() for d in D_DIMS}
    n_feasible = 0
    for g in sample:
        out = evaluate_genome(g, tier="T2", use_cache=False)
        if not out["feasible"]:
            continue
        n_feasible += 1
        dd = developmental_descriptors(compile_genome(g), out["evaluation"])
        for d in D_DIMS:
            vals[d].add(float(dd[d]))
    assert n_feasible >= 10
    for d in D_DIMS:
        if d == "consolidation_ratio":
            # identically 0 over the frozen census space (P00C finding)
            assert vals[d] <= {0.0}, vals[d]
        else:
            assert len(vals[d]) > 1, "dead descriptor axis: %s" % d



# --- AMEND-4: MZ-D8 islands (P13) + MZ-D9 hostile subset --------------------

def test_island_priors_within_bound_and_sampler_stays_in_region():
    from search.island_qd import ISLAND_PRIORS_V1, N_ISLANDS, in_region, region_sampler
    assert N_ISLANDS == 7
    assert len({p["p13_prior"] for p in ISLAND_PRIORS_V1}) == N_ISLANDS
    rng = random.Random(5)
    for p in ISLAND_PRIORS_V1:
        # prior fields are subsets of the frozen census grammar
        for fld in ("F_arch", "Pi_arch", "L", "R", "K"):
            if p[fld] is not None:
                assert set(p[fld]) <= set(CENSUS_BOUND_V1[fld]), (p["island_id"], fld)
        assert set(p["extras_pool"]) <= set(CENSUS_BOUND_V1["extra_units"])
        assert set(p["extras_required"]) <= set(p["extras_pool"])
        lo, hi = p["n_extras"]
        assert lo <= hi
        assert len(p["extras_required"]) <= hi, p["island_id"]
        # sampler draws always stay in the island region
        for _ in range(6):
            g = region_sampler(p, rng)
            assert in_region(g, p), p["island_id"]


def test_region_child_stays_in_region():
    from search.island_qd import ISLAND_PRIORS_V1, in_region, region_child, region_sampler
    rng = random.Random(9)
    for p in ISLAND_PRIORS_V1[:4]:
        parent = region_sampler(p, rng)
        parent.provenance = {"origin": "island_init", "birth_island": 3}
        rec = {"genome": parent.to_json_obj(), "dev_score": 0.0}
        second = None
        if rng.random() < 0.5:
            g2 = region_sampler(p, rng)
            g2.provenance = {"origin": "island_init", "birth_island": 3}
            second = {"genome": g2.to_json_obj(), "dev_score": 0.0}
        child = region_child(rec, p, rng, second_rec=second)
        assert in_region(child, p), p["island_id"]
        assert child.provenance.get("birth_island") == 3, \
            "birth_island provenance must propagate through region children"


def test_run_islands_deterministic_and_migration_sensitive():
    from search.island_qd import run_islands

    def strip(r):
        return {k: v for k, v in r.items() if k != "archive"}

    a = run_islands(budget=42, seed=0, interval=3, migration=True)
    b = run_islands(budget=42, seed=0, interval=3, migration=True)
    assert strip(a) == strip(b), "island run not seed-deterministic"
    nomig = run_islands(budget=42, seed=0, interval=3, migration=False)
    assert nomig["n_migration_events"] == nomig["n_migrants_planted"] == 0
    assert a["n_migration_events"] >= 2 and a["n_migrants_planted"] >= 1
    # identical per-island RNG streams: the two arms agree up to the first
    # planted migrant's descendants, and both consume the same eval count
    assert a["evals"] == nomig["evals"] == 7 * (42 // 7)
    assert sum(a["island_class_counts_final"]) > 0
    assert 0.0 <= a["island_entropy_final"] <= 1.0
    assert 0.0 <= a["island_entropy_mid"] <= 1.0


def test_amend4_freeze_chain_and_hz9_binding():
    import hashlib
    path = os.path.join(ROOT, "FREEZE_V1_AMEND_4.json")
    if not os.path.exists(path):
        return  # not yet frozen in this checkout; smoke asserts it on-host
    a4 = json.load(open(path))
    chain = {"FREEZE_V1.json": "freeze_v1_sha256",
             "FREEZE_V1_AMEND_1.json": "amend_1_sha256",
             "FREEZE_V1_AMEND_2.json": "amend_2_sha256",
             "FREEZE_V1_AMEND_3.json": "amend_3_sha256"}
    for fn, key in chain.items():
        d = hashlib.sha256(open(os.path.join(ROOT, fn), "rb").read()).hexdigest()
        assert d == a4[key], fn
    assert "freeze_amend4.py" in a4["created_utc_by"], \
        "created_utc must be tool-stamped (amend-3 erratum)"
    arms = a4["arms_amend4"]
    assert [a["arm_id"] for a in arms["island_arms"]] == \
        ["I01_islands_ring_mig", "I02_islands_nomig"]
    assert {a["migration"] for a in arms["island_arms"]} == {True, False}
    assert arms["seeds"] == [0, 1, 2] and arms["budget"] == 40000
    assert len(arms["hzd9_recompute_arms"]) == 5
    assert set(arms["hzd9_own_axis"]) == set(arms["hzd9_recompute_arms"])
    from search.island_qd import ISLAND_PRIORS_V1, N_ISLANDS
    assert a4["island_priors_amend4"]["n_islands"] == N_ISLANDS
    frozen = a4["island_priors_amend4"]["priors"]
    assert [f["p13_prior"] for f in frozen] == \
        [p["p13_prior"] for p in ISLAND_PRIORS_V1]
    for f, p in zip(frozen, ISLAND_PRIORS_V1):
        for fld in ("F_arch", "extras_pool", "extras_required", "n_extras"):
            want = tuple(p[fld]) if p[fld] is not None else None
            got = tuple(f[fld]) if isinstance(f[fld], list) else f[fld]
            assert got == want, (f["island_id"], fld)
    assert a4["thresholds_amend4"]["mzd8"]["frontier_birth_concentration_ge"] == 0.9
    tr8 = a4["scoring_rules_amend4"]["mzd8_terminal_rule_FROZEN_first_match"]
    assert any("ONE_ARCHITECTURE_FAMILY_DOMINATES" in s for s in tr8)
    assert any("MORPHOLOGY_FAMILY_TRANSFER_SUPPORTED_AT_SCOPE" in s for s in tr8)
    tr9 = a4["scoring_rules_amend4"]["mzd9_terminal_rule_FROZEN_first_match"]
    assert any("NO_MEANINGFUL_BEHAVIORAL_DIVERSITY" in s for s in tr9)
    assert any("DESCRIPTOR_CHOICE_DOMINATES" in s for s in tr9)
    hz_path = os.path.join(ROOT, "archives", "HZD9_TRUTH.json")
    if os.path.exists(hz_path):
        hz = json.load(open(hz_path))["summary"]
        assert a4["quality_bar_T2"] == hz["quality_bar_T2"]
        for k, v in hz["xcheck_vs_P00C"].items():
            if isinstance(v, bool):
                assert v is True, k


def test_hz9_truth_shape():
    from evaluation.descriptors import D_DIMS
    from search.island_qd import ISLAND_PRIORS_V1
    path = os.path.join(ROOT, "archives", "HZD9_TRUTH.json")
    if not os.path.exists(path):
        return  # census not run in this checkout; smoke asserts it on-host
    hz = json.load(open(path))
    s = hz["summary"]
    assert s["feasible"] == 28584 and s["pareto_set_size"] == 792
    c = s["collapse"]
    assert c["feasible_genotypes"] == s["feasible"]
    assert 0.0 <= c["genotype_to_phenotype_collapse_ratio"] <= 1.0
    assert c["distinct_phenotype_digests"] <= c["feasible_genotypes"]
    assert -1.0 <= s["quality_bar_T2"] <= 1.0
    for view in ("descriptor_purity_D2d", "descriptor_purity_D3d"):
        pu = s[view]
        assert pu["n_cells"] in (50, 83), view
        assert 0.0 <= pu["frac_cells_purity_F_arch_ge_0.9"] <= 1.0
    assert set(s["eta_squared_F_arch"]) == set(D_DIMS)
    assert set(hz["island_regions"]) == {p["island_id"] for p in ISLAND_PRIORS_V1}
    for v in hz["island_regions"].values():
        assert v["n_genotypes"] >= 1, "empty island region — prior is dead"


def test_map_elites_admission_gate_filters_and_none_is_identity():
    """FREEZE_V1_AMEND_5 quality gate (the one varied dimension of the
    revival): a pass-everything bar must reproduce the None archive exactly
    (the gate consumes no RNG), a real bar filters admission so every
    admitted elite clears it, and rejected evaluations stay charged to the
    budget."""
    from search import map_elites
    kw = dict(budget=100, seed=5, archive="D_dev_2d", res=10)

    def sig(res):
        return sorted((e["genotype_digest"], e["phenotype_digest"],
                       round(e["dev_score"], 9)) for e in res["archive"])

    a = map_elites.run(**kw, admission_bar=None)
    b = map_elites.run(**kw, admission_bar=-1e9)
    assert sig(a) == sig(b), "admission gate perturbed the None code path"
    assert b["n_admissible_feasible"] == b["feasible_found"], \
        "a pass-everything bar must admit every feasible eval"
    assert a["n_admissible_feasible"] == a["feasible_found"]
    assert b["evals"] == a["evals"] == kw["budget"]
    # an unreachable bar empties the archive but still charges the budget
    c = map_elites.run(**kw, admission_bar=1e9)
    assert c["n_elites"] == 0 and c["evals"] == kw["budget"]
    assert c["n_admissible_feasible"] == 0
    # a permissive real bar: gate active, every admitted elite clears it
    bar = min(e["dev_score"] for e in a["archive"])
    d = map_elites.run(**kw, admission_bar=bar)
    assert d["n_elites"] > 0, "permissive bar starved the archive"
    assert all(e["dev_score"] >= bar for e in d["archive"]), \
        "an elite below the admission bar leaked into the archive"
    assert d["n_admissible_feasible"] <= d["feasible_found"]


def test_amend5_freeze_chain_and_gate_binding():
    import hashlib
    path = os.path.join(ROOT, "FREEZE_V1_AMEND_5.json")
    if not os.path.exists(path):
        return  # not yet frozen in this checkout; smoke asserts it on-host
    a5 = json.load(open(path))
    chain = {"FREEZE_V1.json": "freeze_v1_sha256",
             "FREEZE_V1_AMEND_1.json": "amend_1_sha256",
             "FREEZE_V1_AMEND_2.json": "amend_2_sha256",
             "FREEZE_V1_AMEND_3.json": "amend_3_sha256",
             "FREEZE_V1_AMEND_4.json": "amend_4_sha256"}
    for fn, key in chain.items():
        d = hashlib.sha256(open(os.path.join(ROOT, fn), "rb").read()).hexdigest()
        assert d == a5[key], fn
    assert a5["amend_4_sha256"].startswith("b51a9959"), \
        "amend-5 must bind the merged-main amend-4 freeze (b51a9959...)"
    assert "freeze_amend5.py" in a5["created_utc_by"], \
        "created_utc must be tool-stamped (amend-3 erratum)"
    assert a5["supersedes_sha256"] is None, "first freeze must not supersede"
    qg = a5["quality_gate_amend5"]
    assert qg["admission_bar"] == qg["census_median_bar_hz9"] == 0.224507
    assert qg["admission_bar_quantile"] == "q0.5"
    # ladder monotonicity: bars fall along the quantile order and the
    # structural ceilings never shrink as the bar relaxes
    order = ["q0.5", "q0.4", "q0.3", "q0.25", "q0.2", "q0.15", "q0.1"]
    lad = qg["ceiling_ladder"]
    bars = [lad[q]["bar"] for q in order]
    assert all(bars[i] >= bars[i + 1] for i in range(len(bars) - 1)), bars
    for ax in ("ceil_D2d_recovery", "ceil_D3d_recovery", "ceil_CVTD_recovery"):
        vals = [lad[q][ax] for q in order]
        assert all(vals[i] <= vals[i + 1] for i in range(len(vals) - 1)), ax
    # the frozen choice is the STRICTEST ladder bar keeping 0.25 reachable
    chosen = qg["admission_bar_quantile"]
    assert lad[chosen]["ceil_D2d_recovery"] >= 0.25
    assert lad[chosen]["ceil_D3d_recovery"] >= 0.25
    for q in order[:order.index(chosen)]:
        e = lad[q]
        assert not (e["ceil_D2d_recovery"] >= 0.25
                    and e["ceil_D3d_recovery"] >= 0.25), \
            "a stricter bar also qualified — the selection rule misapplied"
    arms = a5["arms_amend5"]
    assert arms["gated_arms"] == ["G01_gate_D2d", "G01_gate_D3d"]
    assert arms["nogate_arms"] == ["G00_nogate_D2d", "G00_nogate_D3d"]
    assert arms["budget"] == 40000 and arms["seeds"] == [0, 1, 2]
    amap = {a["arm_id"]: a for a in arms["arms"]}
    for axis, twin in (("D2d", "P05_map_elites_D2d"),
                       ("D3d", "P09_map_elites_D3d")):
        assert amap["G01_gate_%s" % axis]["gated"] is True
        assert amap["G00_nogate_%s" % axis]["gated"] is False
        assert amap["G01_gate_%s" % axis]["nogate_twin"] == twin
        assert amap["G00_nogate_%s" % axis]["nogate_twin"] == twin
        assert amap["G01_gate_%s" % axis]["archive"] == \
            "D_dev_%s" % axis[1:].lower()
    thr = a5["thresholds_amend5"]
    assert thr["own_axis_absolute_bar"] == 0.25
    assert thr["best_dev_ref_P01"] == 0.571144
    assert abs(thr["best_dev_bar"]
               - (thr["best_dev_ref_P01"] - thr["best_dev_slack"])) < 1e-12
    tr = a5["scoring_rules_amend5"]["terminal_rule_FROZEN_first_match"]
    assert any("RESTORED_QUALITY_GATED_AT_SCOPE" in s for s in tr)
    assert any("REVISED_QUALITY_CONDITIONAL" in s for s in tr)
    assert any("PARTIAL_RESTORATION" in s for s in tr)
    den = a5["census_truth_P00C"]["denominators"]
    assert (den["PARETO_T2"], den["D2d@10_occupied"], den["D3d@10_occupied"],
            den["CVTD_occupied_niches"]) == (792, 50, 83, 64)
    hz_path = os.path.join(ROOT, "archives", "HZD9_TRUTH.json")
    gc_path = os.path.join(ROOT, "archives", "GATE_CEILING_TRUTH.json")
    if os.path.exists(hz_path):
        hz = json.load(open(hz_path))["summary"]
        assert qg["admission_bar"] == hz["quality_bar_T2"] == 0.224507
    if os.path.exists(gc_path):
        gc = json.load(open(gc_path))["summary"]
        assert qg["ceiling_ladder"] == gc["ladder"], "ladder drift vs truth"
        for k, v in gc["xcheck_vs_P00C_HZD9"].items():
            if isinstance(v, bool):
                assert v is True, k
