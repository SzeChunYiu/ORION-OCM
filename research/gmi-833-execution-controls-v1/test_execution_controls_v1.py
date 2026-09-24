#!/usr/bin/env python3
"""Tests for #859 execution controls (route A, route B agreement, validator, custody).

Run in both modes:
    python3 -I -B   research/gmi-833-execution-controls-v1/test_execution_controls_v1.py -v
    python3 -I -O -B research/gmi-833-execution-controls-v1/test_execution_controls_v1.py -v
"""
from __future__ import annotations

import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


EC = _load("gmi859_test_execution_controls_v1", "execution_controls_v1.py")
R = EC.R
ROUTE_A_MODULES = ("robustness_record_v1", "substrate_v1", "encoding_e2_v1", "search_procedures_v1", "execution_controls_v1")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imported_modules(path: Path) -> set:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module.split(".")[0])
    return out


class ExecutionControlsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = EC.outputs()
        cls.result = json.loads(cls.outputs[EC.RESULT_FILE])
        cls.positive = json.loads(cls.outputs[EC.RECORD_FILE])
        cls.oracle = json.loads((HERE / "ORACLE_RESULT_V1.json").read_text(encoding="utf-8"))
        cls.manifest = json.loads((HERE / "MANIFEST_V1.json").read_text(encoding="utf-8"))

    # ------------------------------------------------------------ verdict and bytes
    def test_verdict_green_every_check(self):
        self.assertEqual(self.result["verdict"], "GREEN", self.result["failed_checks"])
        self.assertEqual(self.result["failed_checks"], [])
        self.assertTrue(all(self.result["checks"].values()))

    def test_committed_receipts_are_byte_identical(self):
        for name, text in sorted(self.outputs.items()):
            with self.subTest(file=name):
                self.assertEqual((HERE / name).read_text(encoding="utf-8"), text)

    def test_route_b_shared_facts_equal_route_a(self):
        self.assertEqual(self.oracle["verdict"], "GREEN")
        self.assertEqual(set(self.oracle["shared_facts"]), set(self.result["shared_facts"]))
        for key in sorted(self.result["shared_facts"]):
            with self.subTest(fact=key):
                self.assertEqual(self.oracle["shared_facts"][key], self.result["shared_facts"][key])

    def test_route_b_imports_no_route_a_and_no_parent_code(self):
        src = (HERE / "independent_oracle_v1.py").read_text(encoding="utf-8")
        mods = imported_modules(HERE / "independent_oracle_v1.py")
        self.assertTrue(mods <= {"__future__", "fractions", "math", "hashlib", "json", "pathlib", "re", "sys"}, mods)
        for name in ROUTE_A_MODULES + ("full_enumeration_v1", "frontier_branch_bound_v1", "heldout_transition_v1", "audit_core_v1"):
            self.assertNotIn(name + ".py", src.replace("independent_oracle_v1.py", ""))
            self.assertNotIn("import " + name, src)

    # ------------------------------------------------------------ custody and pins
    def test_freeze_and_parent_pins(self):
        self.assertEqual(self.manifest["freeze_commit"], EC.FREEZE_COMMIT)
        self.assertEqual(self.result["freeze_commit"], EC.FREEZE_COMMIT)
        for path, digest in sorted(self.manifest["freeze_pins"].items()):
            with self.subTest(pin=path):
                self.assertEqual(sha256_file(HERE / path), digest)
        for pin in self.manifest["parent_pins"]:
            with self.subTest(parent=pin["path"]):
                self.assertEqual(sha256_file(RESEARCH.parent / pin["path"]), pin["sha256"])

    def test_no_float_literal_in_any_package_source(self):
        for path in sorted(HERE.glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            floats = [n.lineno for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, float)]
            with self.subTest(file=path.name):
                self.assertEqual(floats, [])

    def test_validator_is_stdlib_only_and_substrate_free(self):
        mods = imported_modules(HERE / "robustness_record_v1.py")
        self.assertTrue(mods <= {"__future__", "fractions", "hashlib", "json", "typing", "copy"}, mods)
        for path in ("encoding_e2_v1.py", "search_procedures_v1.py"):
            with self.subTest(module=path):
                self.assertTrue(imported_modules(HERE / path) <= {"__future__", "fractions", "hashlib", "heapq", "itertools", "json", "typing"})

    def test_claim_ceiling_forbidden_promotions_and_no_reconciliation(self):
        self.assertEqual(self.result["claim_ceiling"], "GMI_DERIVATION_ROBUSTNESS_CONTROLS_ENFORCED_AT_REGISTERED_FINITE_SCOPE")
        self.assertEqual(self.manifest["claim_ceiling"], self.result["claim_ceiling"])
        for f in ("ALL_GMI_DERIVATIONS_ROBUST", "ARCHITECTURE_PRIOR_FREE_UNIVERSALLY", "REPRESENTATION_INDEPENDENT_UNIVERSALLY",
                  "SEARCH_INDEPENDENT_UNIVERSALLY", "RESOURCE_PRICE_INDEPENDENT_UNIVERSALLY", "KNOWN_FAMILY_RECOVERY_COMPLETE", "COMPLETE_GMI"):
            self.assertIn(f, self.result["forbidden_promotions"])
        self.assertIs(self.result["reconciliation"]["emitted"], False)
        self.assertEqual(sorted(HERE.glob("ISSUE_833_RECONCILIATION*")), [])

    # ------------------------------------------------------------ validator (checker validated first)
    def test_validator_self_test_no_alarm_and_alarms(self):
        st = R.self_test()
        self.assertTrue(st["toy_positive_is_robust"])
        self.assertTrue(all(st.values()), st)
        self.assertEqual(self.result["admission"]["validator_self_test"], st)

    def test_schema_file_matches_validator_module(self):
        self.assertEqual(json.loads((HERE / EC.SCHEMA_FILE).read_text(encoding="utf-8")), json.loads(R.canonical_json(R.SCHEMA)))

    def test_committed_positive_record_is_robust_from_the_file(self):
        rec = json.loads((HERE / EC.RECORD_FILE).read_text(encoding="utf-8"))
        v = R.validate_record(rec)
        self.assertEqual(v["terminal"], R.ROBUST)
        self.assertTrue(all(v["conditions"].values()))

    def test_mutations_of_the_committed_record_fail_closed(self):
        base = json.loads((HERE / EC.RECORD_FILE).read_text(encoding="utf-8"))
        cases = []
        r = copy.deepcopy(base)
        r["controls"]["MATCHED_TWIN"]["descriptor_twin"]["budget"] = 32776
        cases.append((r, "MATCHED_TWIN", R.UNMATCHED))
        r = copy.deepcopy(base)
        r["controls"]["ENCODING"]["projection_mismatches"] = 1
        cases.append((r, "ENCODING", R.ENC_NOT_EQUIVALENT))
        r = copy.deepcopy(base)
        r["controls"]["SEARCH"]["searchers"][2]["conclusion_by_world"]["c01_low"]["properties"] = ["STATELESS"]
        cases.append((r, "SEARCH", R.SEARCH_SENSITIVE))
        r = copy.deepcopy(base)
        r["controls"]["SCALARIZATION"]["scalarizations"][0]["weights"][0] = float(1) / 20  # a runtime float: the hostile input
        cases.append((r, "SCALARIZATION", R.CONTROL_MALFORMED))
        r = copy.deepcopy(base)
        del r["controls"]["NO_SMUGGLING"]["arms"]["G_MINUS"]
        cases.append((r, "MATCHED_TWIN", R.TWIN_AUDIT_NOT_EVALUABLE))
        r = copy.deepcopy(base)
        r["controls"]["SCALARIZATION"]["pareto_set"] = ["s1n0d0"]
        cases.append((r, "SCALARIZATION", R.SCAL_INCONSISTENT))
        for i, (rec, control, terminal) in enumerate(cases):
            with self.subTest(case=i, control=control):
                v = R.validate_record(rec)
                self.assertNotEqual(v["terminal"], R.ROBUST)
                self.assertEqual(v["control_terminals"][control], terminal)

    def test_admission_census_exact(self):
        census = self.result["admission"]["census"]
        self.assertEqual(len(census), 22)
        for e in census:
            with self.subTest(record=e["record_id"]):
                self.assertTrue(e["exact_match"])
                self.assertEqual(e["terminal"], e["expected_terminal"])
                self.assertEqual(e["failing_controls"], e["expected_failing_controls"])
        by = {e["record_id"]: e for e in census}
        self.assertEqual(by["GMI859_POSITIVE_WITNESS_901_FAMILY"]["terminal"], "ROBUST_AT_REGISTERED_D_CONTROLS_SCOPE")
        for ctl in R.CONTROL_ORDER:
            self.assertEqual(by["DELETE_" + ctl]["terminal"], "CANNOT_ESTABLISH_D_ROBUSTNESS_" + ctl)

    # ------------------------------------------------------------ D-X1
    def test_dx1_matched_twin_and_hostiles(self):
        g = self.result["d_x1_matched_twin"]["gates"]
        self.assertEqual(g["G_MINUS"]["terminal"], "MATCHED_MECHANISM_TWIN")
        self.assertEqual(g["G_MINUS"]["mismatched_coordinates"], [])
        self.assertEqual(g["G_MINUS"]["candidate_count"], 65552)
        self.assertIs(g["G_MINUS"]["k_target_realizable"], False)
        self.assertEqual(g["G_MINUS"]["k_fingerprint_count"], 0)
        for twin in ("H1A_CAPACITY_DELETE_STATEFUL", "H1B_MACRO_PREV", "H1C_HALVED_SEQUENCE_SET", "H1D_HALVED_BUDGET"):
            with self.subTest(twin=twin):
                self.assertEqual(g[twin]["terminal"], "UNMATCHED_MECHANISM_TWIN")
        self.assertIn("candidate_count", g["H1A_CAPACITY_DELETE_STATEFUL"]["mismatched_coordinates"])
        self.assertEqual(g["H1A_CAPACITY_DELETE_STATEFUL"]["low_endpoint_best_rises_vs_g_plus"], 20)
        self.assertIn("COMPENSATING_OPERATOR:READ_PREV", g["H1B_MACRO_PREV"]["reasons"])
        self.assertIn("sequence_set", g["H1C_HALVED_SEQUENCE_SET"]["mismatched_coordinates"])
        self.assertEqual(g["H1D_HALVED_BUDGET"]["mismatched_coordinates"], ["budget"])
        d = self.result["d_x1_matched_twin"]
        self.assertEqual(d["phase_law_on_g_plus"], {"transitions_persistent_to_stateless": 20, "boundary_ties": 20})
        self.assertEqual(d["phase_law_on_matched_twin"]["worlds_stateless"], 60)
        self.assertEqual(d["k_free_multiplicity_reweighting"]["G_MINUS"]["min_per_class"], 4097)
        self.assertEqual(d["k_free_multiplicity_reweighting"]["G_PLUS"]["min_per_class"], 33)

    def test_dx1e_ecology_twin(self):
        e = self.result["d_x1e_ecology_twin"]
        self.assertEqual(e["gates"]["E_MINUS"]["terminal"], "MATCHED_ECOLOGY_TWIN")
        self.assertEqual(e["gates"]["E_MINUS_HOSTILE_HALVED_SEQUENCES"]["terminal"], "ECOLOGY_TWIN_UNMATCHED")
        self.assertEqual(e["gates"]["E_MINUS_HOSTILE_ETA_RESCALED"]["terminal"], "ECOLOGY_TWIN_UNMATCHED")
        self.assertEqual(e["g_plus_in_e_minus"]["worlds_stateless"], 60)

    # ------------------------------------------------------------ D-X2
    def test_dx2_encoding_gate(self):
        d = self.result["d_x2_encoding"]
        self.assertEqual(d["projection_mismatches"], 0)
        self.assertEqual(d["bijection"], {"domain_size": 65552, "codomain_size": 65552, "injective": True, "surjective": True})
        self.assertEqual(d["worlds_with_phi_mapped_winner_ids_equal"], 60)
        self.assertEqual(d["gates"]["E1_E2_REGISTERED"]["terminal"], "ENCODING_ROBUST_AT_REGISTERED_FINITE_SCOPE")
        self.assertEqual(d["gates"]["H2A_DELETION"]["terminal"], "ENCODING_NOT_SEMANTICALLY_EQUIVALENT")
        self.assertTrue(d["h2a"]["conclusions_still_agree_after_projection"])
        self.assertEqual(d["gates"]["H2B_COST_MUTATION"]["terminal"], "ENCODING_NOT_SEMANTICALLY_EQUIVALENT")
        self.assertEqual(d["gates"]["H2C_SURFACE_TIE"]["terminal"], "ENCODING_SENSITIVE")
        self.assertEqual(d["h2c"]["worlds_where_lexicographic_rule_disagrees"], 20)

    def test_e2_is_syntactically_disjoint(self):
        E2 = EC.E2
        self.assertEqual(set(E2.SURFACE_ALPHABET) & {"0", "1"}, set())
        self.assertEqual(E2.surface_id(0), "WAAAA")
        self.assertTrue(all(E2.gray_inverse(E2.gray(n)) == n for n in range(256)))
        ids = {E2.surface_id(j) for j in range(E2.CENSUS)}
        self.assertEqual(len(ids), 65552)
        self.assertFalse(any(i.startswith("q") for i in ids))

    # ------------------------------------------------------------ D-X3
    def test_dx3_search_gate(self):
        d = self.result["d_x3_search"]
        self.assertEqual(d["registered_triple"]["terminal"], "SEARCH_ROBUST")
        self.assertTrue(all(p["distinct"] for p in d["registered_triple"]["distinctness"]))
        self.assertEqual(d["s1_trace_matches_901_counters_worlds"], 60)
        self.assertEqual(d["s2_trace_matches_901_counters_worlds"], 60)
        self.assertEqual(d["h3a_early_stop"]["terminal"], "SEARCH_SENSITIVE")
        self.assertEqual(d["h3a_early_stop"]["low_endpoints_wrong"], 20)
        self.assertEqual(d["h3b_reencoding_masquerade"]["terminal"], "SEARCHERS_NOT_MATERIALLY_DISTINCT")
        self.assertTrue(d["h3b_reencoding_masquerade"]["distinctness"][0]["reencoding"])
        for key, proc in d["procedures"].items():
            with self.subTest(procedure=key):
                self.assertIn("evaluations_total", proc["search_cost"])

    # ------------------------------------------------------------ D-X4 and perturbations
    def test_dx4_pareto_gate(self):
        d = self.result["d_x4_scalarization"]
        self.assertEqual([p["point_id"] for p in d["pareto_set"]], ["s0n0d8", "s1n0d0"])
        self.assertEqual(d["registered_scalarizations"]["strictly_positive"], 30)
        self.assertTrue(d["positive_winners_all_on_frontier"])
        self.assertEqual(d["registered_price_conditional_terminal"], "PARETO_CONSISTENT_AT_REGISTERED_SCALARIZATIONS")
        self.assertEqual(d["universal_winner_wording"]["terminal"], "SCALARIZATION_SENSITIVE")
        self.assertEqual(d["literal_issue_hostile_1_4_vs_4_1"]["terminal"], "SCALARIZATION_SENSITIVE")
        self.assertEqual(d["invariant_claims"], ["I1_FRONTIER_ED_BELOW_8_IMPLIES_STATE", "I2_FRONTIER_NOW_ERROR_ZERO"])

    def test_metric_perturbation_control(self):
        p = self.result["metric_perturbation_control"]
        self.assertEqual(p["perturbed_worlds"], p["winner_state_partition_stable_all_three_encodings"])
        self.assertEqual(p["exact_boundary_ties_all_three_encodings"], 40)
        self.assertEqual(p["mirrored_price_flips_all_three_encodings"], 40)
        self.assertTrue(p["risk_clustering_146_classes_identical_across_encodings"])
        self.assertTrue(p["analytic_bound_abs_dprice_minus_half_ddelay_below_margin"])

    def test_literal_scalarization_hostile_standalone(self):
        claim = {"wording": "UNIVERSAL_WINNER", "frontier_invariants": []}
        block = {"coordinates": ["r1", "r2"],
                 "raw_vectors": [{"point_id": "a", "vector": ["1", "4"], "multiplicity": 1, "property": "A"},
                                 {"point_id": "b", "vector": ["4", "1"], "multiplicity": 1, "property": "B"}],
                 "pareto_set": ["a", "b"],
                 "scalarizations": [{"scalarization_id": "w41", "weights": ["4", "1"], "boundary_probe": False, "winners": ["a"]},
                                    {"scalarization_id": "w14", "weights": ["1", "4"], "boundary_probe": False, "winners": ["b"]}],
                 "declared_terminal": R.SCAL_SENSITIVE}
        self.assertEqual(R.evaluate_scalarization(block, claim)["terminal"], R.SCAL_SENSITIVE)
        conditional = dict(claim, wording="PRICE_CONDITIONAL")
        block2 = copy.deepcopy(block)
        block2["declared_terminal"] = R.PARETO_OK
        block2["scalarizations"][0]["claimed_properties"] = ["A"]
        block2["scalarizations"][1]["claimed_properties"] = ["B"]
        self.assertEqual(R.evaluate_scalarization(block2, conditional)["terminal"], R.PARETO_OK)


if __name__ == "__main__":
    unittest.main()
