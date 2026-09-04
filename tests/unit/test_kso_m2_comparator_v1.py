"""KSO M2 comparator harness: every checker must be able to fail on its plant, budget overrun is
exit 2 and never a score, the paired test is red on a planted systematic disagreement and quiet
on a copy, the positive control is exactly 1.0, the random control sits at the null, and every
arm reads one graph, one seed set and one status map per instance."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MOD = ROOT / "research" / "orion-machine" / "reference" / "kso_m2_comparator_v1.py"


@pytest.fixture(scope="module")
def m():
    spec = importlib.util.spec_from_file_location("kso_m2_comparator_v1", MOD)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["kso_m2_comparator_v1"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def body(m):
    return m.run()


def test_instance_set_is_the_m1_population_set(body):
    assert body["n_instances"] == 50
    ids = [r["instance_id"] for r in body["instances"]]
    assert ids[0] == "dev-X1-A_CLAIM_PROBLEM_IDENTITY-000" and len(set(ids)) == 50
    assert body["source"]["split_seed"] == "ME-X1-DEV-20260902" and body["source"]["per_family"] == 5


def test_every_arm_returns_the_oracle_answer_object(m, body):
    for r in body["instances"]:
        for name in m.ARMS:
            a = r["arms"][name]["answer"]
            assert set(a) == {"action", "reopened"} and isinstance(a["reopened"], list)
            assert r["arms"][name]["status"] in ("SCORED", "CANNOT_CHECK", "OBSTRUCTION")
            assert r["arms"][name]["attribution"] == ""


def test_positive_control_is_exactly_one_and_the_plant_breaks_it(m, body):
    k2 = body["checkers"]["K2_positive_control_exact"]
    assert body["per_arm"][m.ORACLE]["exact_rate"] == 1.0 and k2["pass"] and k2["plant_one_perturbed_breaks"]


def test_random_control_sits_at_the_null_and_the_oracle_does_not(m, body):
    k1 = body["checkers"]["K1_random_at_null"]
    assert k1["pass"] and k1["plant_oracle_outside_band"]
    assert k1["band"]["min"] <= k1["count"] <= k1["band"]["max"] < 50
    assert not m.at_null(50, k1["band"])


def test_ceiling_control_reproduces_the_oracle_on_the_dev_split(m, body):
    # ME_X1_OUTCOME_RECEIPT §3: B5 = 1.000 on the protected split; the dev split agrees
    assert body["per_arm"][m.B5]["exact_rate"] == 1.0 and body["per_arm"][m.B5]["role"] == "ceiling control"


def test_oracle_independent_comparators_are_below_the_ceiling_and_above_the_null(m, body):
    for name in (m.RWR, m.CBR):
        rate = body["per_arm"][name]["exact_rate"]
        assert 0 < rate < 1.0, (name, rate)
        assert body["per_arm"][name]["exact"] > body["checkers"]["K1_random_at_null"]["band"]["max"]


def test_paired_test_is_red_on_the_planted_disagreement_and_quiet_on_a_copy(m, body):
    k4 = body["checkers"]["K4_paired_red_on_planted_disagreement"]
    assert k4["pass"]
    assert k4["plant"]["discordant"] == 12 and k4["plant"]["exact_p_two_sided"] < 0.001 and k4["plant"]["red"]
    assert k4["no_alarm"]["discordant"] == 0 and k4["no_alarm"]["exact_p_two_sided"] == 1.0 and not k4["no_alarm"]["red"]


def test_paired_semantics_match_mex1_run(m):
    x = [True] * 10 + [False] * 2
    y = [True] * 12
    t = m.paired("x", "y", x, y)
    assert t["x_only"] == 0 and t["y_only"] == 2 and t["discordant"] == 2
    assert t["exact_p_two_sided"] == pytest.approx(0.5) and not t["red"]
    assert m.exact_binomial_two_sided(0, 0) == 1.0 and m.exact_binomial_two_sided(12, 0) < 0.001


def test_budget_recorded_per_instance_per_arm_and_within_caps(m, body):
    for r in body["instances"]:
        caps = r["caps"]
        assert caps["steps"] == 2 * r["graph"]["atoms"] and caps["edge_visits"] == 2 * r["graph"]["hyperedges"] and caps["restarts"] == 1
        for name in m.NAVIGATING:
            b = r["arms"][name]["budget"]
            assert b["capped"] and b["steps"] <= caps["steps"] and b["edge_visits"] <= caps["edge_visits"] and b["restarts"] <= caps["restarts"]
            assert b["ops"] == b["steps"] + b["edge_visits"]
        assert not r["arms"][m.B5]["budget"]["capped"]     # recorded, not capped: a JTMS does not navigate
    assert body["checkers"]["K3_budget_no_overrun"]["pass"] and body["checkers"]["K3_budget_no_overrun"]["cannot_check"] == []


def test_budget_overrun_is_cannot_check_never_scored_and_exit_2(m):
    over = m.run(cap_scale=0.0)
    for r in over["instances"]:
        for name in m.NAVIGATING:
            assert r["arms"][name]["status"] == "CANNOT_CHECK" and r["arms"][name]["exact"] is False
    assert over["per_arm"][m.RWR]["n_scored"] == 0 and over["per_arm"][m.RWR]["n_cannot_check"] == 50
    assert over["per_arm"][m.RWR]["exact_rate"] is None
    assert m.verdict(over) == 2
    assert over["per_arm"][m.B5]["n_cannot_check"] == 0       # uncapped arms are unaffected


def test_information_matching_one_graph_one_seed_one_status_map(m, body):
    k5 = body["checkers"]["K5_information_matching"]
    assert k5["pass"]
    for r in body["instances"]:
        g = r["graph"]
        assert len(g["sha256"]) == 64
        assert g["seed_atoms"][0] == f"req:{r['instance_id']}" and g["seed_atoms"][1].startswith("claim:")
        assert g["request_atoms"] in ("M1_ONLY", "kso_m2_solve_v1.add_request_atoms")


def test_graph_digest_is_content_bound(m):
    _, gen, model, _ = m._mex1()
    inst, _ = gen.generate_split("dev", "ME-X1-DEV-20260902", {model.FAMILIES[0]: 1})[0]
    fr = m.frame_for(inst)
    assert fr.graph_sha256 == m.graph_sha256(fr.pop.space)
    ks = fr.pop.space
    perturbed = m.kso.KnowledgeSpace(ks.atoms + (m.kso.Atom("planted:atom", "observation", ks.atoms[0].profile),), ks.hyperedges)
    assert m.graph_sha256(perturbed) != fr.graph_sha256


def test_kso_column_joins_the_table_and_a_bad_column_is_could_not_check(m, body, tmp_path):
    col = {"instances": [{"instance_id": r["instance_id"],
                          "arms": {m.KSO_COL: {"answer": r["arms"][m.B5]["answer"], "exact": r["arms"][m.B5]["exact"],
                                               "status": "SCORED", "attribution": "", "navigation_outcome": "FOUND",
                                               "translator_invariant": True, "budget": r["arms"][m.RWR]["budget"]}}}
                         for r in body["instances"]]}
    joined = m.run(kso_column={row["instance_id"]: row["arms"][m.KSO_COL] for row in col["instances"]})
    assert joined["per_arm"][m.KSO_COL]["exact"] == 50 and joined["terminals"]["PARENT_SUFFICIENT"] == "YES"
    assert any(t["x"] == m.KSO_COL and t["y"] == m.B5 for t in joined["paired"])
    partial = {k: v for k, v in list({row["instance_id"]: row["arms"][m.KSO_COL] for row in col["instances"]}.items())[:10]}
    with pytest.raises(m.CannotCheck):
        m.run(kso_column=partial)
    # the join is refused when the KSO column was scored on a different graph
    wrong_graph = {row["instance_id"]: {**row["arms"][m.KSO_COL], "_graph_sha256": "0" * 64} for row in col["instances"]}
    with pytest.raises(m.CannotCheck, match="did not see the same graph"):
        m.run(kso_column=wrong_graph)
    same_graph = {r["instance_id"]: {**col["instances"][i]["arms"][m.KSO_COL], "_graph_sha256": r["graph"]["sha256"]} for i, r in enumerate(body["instances"])}
    assert m.run(kso_column=same_graph)["per_arm"][m.KSO_COL]["exact"] == 50
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    proc = subprocess.run([sys.executable, str(MOD), "--no-repro-check", "--kso-column", str(bad)], capture_output=True, text=True)
    assert proc.returncode == 2 and "COULD NOT CHECK" in proc.stderr


def test_byte_reproducible_once_timing_is_zeroed(m, body):
    again = m.run()
    assert m.canonical(body) == m.canonical(again)
    assert m.strip_timing({"a": {"wall_ns": 5, "b": [{"wall_ns": 1}]}}) == {"a": {"wall_ns": 0, "b": [{"wall_ns": 0}]}}


def _fake_column(m, body, with_nav=True, nav_null_every=4):
    col = {}
    for i, r in enumerate(body["instances"]):
        cell = {"answer": r["arms"][m.B5]["answer"], "exact": r["arms"][m.B5]["exact"], "status": "SCORED", "attribution": "",
                "navigation_outcome": "FOUND", "translator_invariant": True, "budget": r["arms"][m.RWR]["budget"],
                "_graph_sha256": r["graph"]["sha256"]}
        if with_nav:
            null = (i % nav_null_every == 3)
            cell["store_read"] = null
            cell["navigation_only_answer"] = None if null else r["arms"][m.B5]["answer"]
        col[r["instance_id"]] = cell
    return col


def test_navigation_only_column_scores_extract_only_and_obstructs_on_null(m, body):
    joined = m.run(kso_column=_fake_column(m, body))
    nav = joined["per_arm"][m.KSO_NAV]
    assert nav["n_obstruction"] == 12 and nav["n_scored"] == 38 and nav["exact"] == 38 and nav["n_cannot_check"] == 0
    assert joined["per_arm"][m.KSO_COL]["exact"] == 50 and joined["per_arm"][m.KSO_COL]["store_read_rows"] == 12
    pairs = {(t["x"], t["y"]): t for t in joined["paired"]}
    assert (m.KSO_COL, m.B5) in pairs and (m.KSO_NAV, m.RWR) in pairs and (m.KSO_NAV, m.CBR) in pairs
    assert (m.KSO_COL, m.RWR) not in pairs          # the store-reading arm is never paired against a navigation-only parent
    assert joined["terminals"]["PARENT_SUFFICIENT"] == "YES" and joined["terminals"]["NAVIGATION_ONLY_VS_RETRIEVAL_PARENTS"] == "REPORTED"
    assert m.verdict(joined) == 0
    assert joined["store_read_permissions"][m.KSO_NAV].startswith("NO") and joined["store_read_permissions"][m.RWR].startswith("NO")


def test_navigation_only_column_without_the_field_is_cannot_check_and_exit_2(m, body):
    joined = m.run(kso_column=_fake_column(m, body, with_nav=False))
    assert joined["per_arm"][m.KSO_NAV]["n_cannot_check"] == 50 and joined["terminals"]["NAVIGATION_ONLY_VS_RETRIEVAL_PARENTS"] == "NOT_SCORED"
    assert m.verdict(joined) == 2


def test_joined_exact_flag_is_recomputed_not_trusted(m, body):
    col = _fake_column(m, body)
    first = next(iter(col))
    col[first]["exact"] = False                       # a lying flag on a correct answer
    joined = m.run(kso_column=col)
    assert joined["per_arm"][m.KSO_COL]["exact"] == 50 and joined["per_arm"][m.KSO_COL]["exact_declared_disagreements"] == 1
    assert not joined["checkers"]["K7_joined_exact_recomputed"]["pass"] and m.verdict(joined) == 1


def test_terminals_carry_no_superiority_language(body):
    t = body["terminals"]
    assert t["GENERAL_NOVELTY"] == "NOT_ESTABLISHED" and t["PARENT_SUFFICIENT"] == "EXPECTED_WHEN_KSO_COLUMN_MERGED"
    assert "NO NOVELTY OR BREAKTHROUGH CLAIM" in body["authority"]


def test_cli_exit_codes(tmp_path):
    ok = subprocess.run([sys.executable, str(MOD), "--no-repro-check"], capture_output=True, text=True)
    assert ok.returncode == 0, ok.stdout + ok.stderr
    assert "python 3.1" in ok.stdout
    over = subprocess.run([sys.executable, str(MOD), "--no-repro-check", "--cap-scale", "0"], capture_output=True, text=True)
    assert over.returncode == 2 and "COULD NOT CHECK" in over.stderr
