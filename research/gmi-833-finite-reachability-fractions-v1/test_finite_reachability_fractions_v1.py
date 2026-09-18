#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


M = load("finite_reachability_fractions_v1_tested", HERE / "finite_reachability_fractions_v1.py")
O = load("independent_reachability_oracle_v1_tested", HERE / "independent_reachability_oracle_v1.py")


class FiniteReachabilityFractionTests(unittest.TestCase):
    def test_parent_artifacts_are_exactly_pinned(self):
        audit = M.audit_parents()
        self.assertTrue(audit["all_ok"])
        self.assertEqual(len(audit["rows"]), 2)

    def test_parent_mutation_fails_closed(self):
        root = M.repo_root()
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            for _, relative, _, _, _ in M.PARENT_PINS:
                target = tmp / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(root / relative, target)
            victim = tmp / M.PARENT_PINS[0][1]
            victim.write_bytes(victim.read_bytes() + b"\n")
            self.assertFalse(M.audit_parents(tmp)["all_ok"])

    def test_frozen_registry_is_exact_and_complete_only_locally(self):
        laws = M.load_registry()
        self.assertEqual(tuple(law.law_id for law in laws), M.EXPECTED_LAW_IDS)
        payload = json.loads((HERE / "LAW_REGISTRY_V1.json").read_text())
        self.assertTrue(payload["registry_is_complete_only_for_this_tranche"])
        self.assertIn("COMPLETE_REGISTRY_OF_ALL_DEVELOPMENTAL_OR_SEARCH_LAWS", payload["forbidden_promotions"])

    def test_exact_reachable_quotient_fractions(self):
        rows = {row["law_id"]: row for row in M.reachability_census()["laws"]}
        expected = {
            "REWRITE_11": (5, "5/576", 4, "4/21"),
            "CODE_GROWTH_R1": (126, "7/32", 18, "6/7"),
            "REGISTER_GROWTH_N1": (14, "7/288", 4, "4/21"),
            "JOINT_GROWTH_22": (576, "1/1", 21, "1/1"),
        }
        for law_id, values in expected.items():
            row = rows[law_id]
            self.assertEqual(
                (
                    row["reachable_presentation_count"],
                    row["reachable_presentation_fraction"],
                    row["reachable_quotient_class_count"],
                    row["reachable_quotient_fraction"],
                ),
                values,
            )

    def test_bfs_equals_analytic_characterization_for_each_law(self):
        for law in M.load_registry():
            bfs = {program.canonical_code() for program in M.bfs_reachable(law)}
            direct = {program.canonical_code() for program in M.analytic_reachable(law)}
            self.assertEqual(bfs, direct)

    def test_independent_interpreter_matches_parent_on_whole_universe(self):
        interface = M.registered_interface()
        universe = M.F.enumerate_candidates(M.F.StructuralBudget(2, 2))
        for program in universe:
            raw = program.canonical_code()
            expected = tuple(O.execute(raw, word) for word in O.WORDS)
            self.assertEqual(M.F.semantic_key(program, interface), expected)

    def test_independent_direct_product_oracle_matches_all_laws(self):
        oracle = O.oracle_census()
        self.assertEqual(oracle["universe_presentation_count"], 576)
        self.assertEqual(oracle["universe_quotient_count"], 21)
        self.assertEqual(
            [(row["reachable_presentation_count"], row["reachable_quotient_class_count"]) for row in oracle["laws"]],
            [(5, 4), (126, 18), (14, 4), (576, 21)],
        )

    def test_reachability_is_reflexive_and_successors_stay_bounded(self):
        start = M.start_program()
        for law in M.load_registry():
            reached = M.bfs_reachable(law)
            self.assertIn(start, reached)
            for program in reached:
                for successor in M.presentation_successors(program, law):
                    self.assertLessEqual(len(successor.instructions), law.max_code_cells)
                    self.assertLessEqual(successor.register_count, law.max_register_cells)

    def test_registry_rejects_duplicate_law_and_unknown_operator(self):
        source = json.loads((HERE / "LAW_REGISTRY_V1.json").read_text())
        variants = []
        duplicate = json.loads(json.dumps(source)); duplicate["laws"].append(duplicate["laws"][0]); variants.append(duplicate)
        unknown = json.loads(json.dumps(source)); unknown["laws"][0]["operators"] = ["TELEPORT"]; variants.append(unknown)
        with tempfile.TemporaryDirectory() as td:
            for index, payload in enumerate(variants):
                path = Path(td) / f"{index}.json"
                path.write_text(json.dumps(payload), encoding="utf-8")
                with self.assertRaises(ValueError):
                    M.load_registry(path)

    def test_analytic_completeness_rejects_missing_required_operator(self):
        with self.assertRaises(ValueError):
            M.analytic_reachable(M.DevelopmentLaw("X", ("GROW_CODE",), 2, 1))
        with self.assertRaises(ValueError):
            M.analytic_reachable(M.DevelopmentLaw("X", ("REWRITE",), 2, 1))

    def test_successor_generation_rejects_out_of_scope_source(self):
        outside = M.F.CandidateProgram(2, (M.F.Instruction("HALT"),))
        with self.assertRaises(ValueError):
            M.presentation_successors(outside, M.load_registry()[0])

    def test_presentation_and_quotient_mass_are_not_confused(self):
        rows = M.reachability_census()["laws"]
        self.assertTrue(any(row["reachable_presentation_fraction"] != row["reachable_quotient_fraction"] for row in rows))
        code = next(row for row in rows if row["law_id"] == "CODE_GROWTH_R1")
        self.assertEqual(code["reachable_presentation_fraction"], "7/32")
        self.assertEqual(code["reachable_quotient_fraction"], "6/7")

    def test_all_surface_remints_and_semantic_hostile(self):
        census = M.remint_census()
        self.assertEqual(census["certified_surface_remint_count"], 120)
        self.assertEqual(census["presentation_law_membership_checks"], 276_480)
        self.assertTrue(census["semantics_changing_hostile_detected"])

    def test_all_registered_hostiles_are_detected(self):
        self.assertTrue(all(M.hostile_census().values()))

    def test_scientific_ledger_and_package_contracts(self):
        self.assertEqual(
            M.validate_scientific_ledger(),
            {"claim_ledgers": 3, "open_gaps": 7, "closure_level": "REGISTERED_FINITE_SCOPE_ONLY"},
        )
        self.assertEqual(
            M.validate_package_contracts(),
            {"manifest_ok": True, "reconciliation_ok": True, "reconciliation_rows": 1, "source_pr": 1001},
        )

    def test_receipt_is_green_and_byte_stable(self):
        receipt = M.build_receipt()
        self.assertEqual(receipt["verdict"], "GREEN")
        self.assertTrue(all(receipt["checks"].values()))
        checked_in = (HERE / "RESULT_V1.json").read_text(encoding="utf-8")
        self.assertEqual(M.canonical_json(receipt), checked_in)
        self.assertEqual(json.loads(checked_in), receipt)

    def test_claim_boundary_forbids_all_laws_promotion(self):
        receipt = M.build_receipt({"all_ok": True, "rows": []})
        self.assertEqual(receipt["claim_ceiling"], M.CLAIM_CEILING)
        self.assertIn("COMPLETE_REGISTRY_OF_ALL_DEVELOPMENTAL_OR_SEARCH_LAWS", receipt["forbidden_promotions"])
        self.assertIn("UNIVERSAL_REACHABILITY", receipt["forbidden_promotions"])
        self.assertIn("COMPLETE_GMI", receipt["forbidden_promotions"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
