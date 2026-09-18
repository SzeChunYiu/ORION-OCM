#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "finite_pareto_density_v1_tested", HERE / "finite_pareto_density_v1.py"
)
M = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)

ORACLE_SPEC = importlib.util.spec_from_file_location(
    "independent_frontier_oracle_v1_tested", HERE / "independent_frontier_oracle_v1.py"
)
O = importlib.util.module_from_spec(ORACLE_SPEC)
assert ORACLE_SPEC and ORACLE_SPEC.loader
ORACLE_SPEC.loader.exec_module(O)


class FiniteParetoDensityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.census = M.registered_census()

    def test_parent_artifact_is_exactly_pinned(self):
        audit = M.audit_parents()
        self.assertTrue(audit["all_ok"])
        self.assertEqual(audit["rows"][0]["actual_blob"], M.PARENT_PINS[0][2])

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

    def test_behavioral_objectives_are_exactly_preregistered(self):
        observations = (
            ("HALTED", ()),
            ("BLOCKED_INPUT", (0,)),
            ("STEP_LIMIT", (2,)),
        )
        self.assertEqual(M.behavioral_objectives(observations), (1, 1, 2))

    def test_malformed_points_fail_closed(self):
        valid = (("HALTED", ()), ("HALTED", ()), ("HALTED", ()))
        for observations in (
            (),
            (("HALTED", ()),),
            (("OTHER", ()), ("HALTED", ()), ("HALTED", ())),
            (("HALTED", [0]), ("HALTED", ()), ("HALTED", ())),
        ):
            with self.subTest(observations=observations), self.assertRaises(ValueError):
                M.MorphologyPoint(observations, (1, 1))
        for resources in ((0, 1), (1, 0), (True, 1), [1, 1]):
            with self.subTest(resources=resources), self.assertRaises(ValueError):
                M.MorphologyPoint(valid, resources)

    def test_dominance_is_oriented_without_scalarization(self):
        strong = M.MorphologyPoint(
            (("HALTED", ()), ("HALTED", (0,)), ("HALTED", (1,))), (1, 1)
        )
        weak = M.MorphologyPoint(
            (("STEP_LIMIT", ()), ("STEP_LIMIT", ()), ("STEP_LIMIT", ())), (2, 2)
        )
        self.assertTrue(M.dominates(strong, weak))
        self.assertFalse(M.dominates(weak, strong))
        self.assertFalse(M.dominates(strong, strong))

    def test_duplicate_morphology_inputs_fail_closed(self):
        point = M.MorphologyPoint(
            (("HALTED", ()), ("HALTED", ()), ("HALTED", ())), (1, 1)
        )
        with self.assertRaises(ValueError):
            M.pareto_front(())
        with self.assertRaises(ValueError):
            M.pareto_front((point, point))

    def test_independent_oracle_contract_and_simple_frontier(self):
        rows = ((0, 0), (1, 0), (0, 1), (1, 1))
        self.assertEqual(O.maximal_indices(rows), (3,))
        with self.assertRaises(ValueError):
            O.maximal_indices(())
        with self.assertRaises(ValueError):
            O.maximal_indices(((1, 2), (1, 2)))
        with self.assertRaises(ValueError):
            O.maximal_indices(((1,), (1, 2)))

    def test_exact_registered_frontier_densities(self):
        rows = {tuple(row["budget"]): row for row in self.census["budget_rows"]}
        expected = {
            (1, 1): (5, 4, 2, "1/2"),
            (2, 1): (126, 22, 4, "2/11"),
            (1, 2): (14, 8, 2, "1/4"),
            (2, 2): (576, 47, 4, "4/47"),
        }
        for budget, values in expected.items():
            row = rows[budget]
            self.assertEqual(
                (
                    row["presentation_count"],
                    row["morphology_count"],
                    row["frontier_morphology_count"],
                    row["density"],
                ),
                values,
            )
            self.assertTrue(row["independent_oracle_exact_match"])
            self.assertEqual(Fraction(row["density"]), Fraction(values[3]))

    def test_exhaustive_strict_order_and_frontier_certificates(self):
        rows = {tuple(row["budget"]): row for row in self.census["budget_rows"]}
        largest = rows[(2, 2)]
        self.assertEqual(largest["transitive_checks"], 47**3)
        self.assertEqual(largest["irreflexive_checks"], 47)
        self.assertEqual(largest["maximal_cover_checks"], 47)
        self.assertGreater(largest["antichain_ordered_checks"], 0)
        self.assertEqual(self.census["total_transitive_checks"], 115_047)

    def test_duplicate_injection_exposes_presentation_bias(self):
        hostile = self.census["duplicate_injection"]
        self.assertEqual(hostile["quotient_density"], "1/2")
        self.assertEqual(hostile["presentation_density_baseline"], "1/2")
        self.assertEqual(hostile["presentation_density_after_front_duplicate"], "2/3")
        self.assertEqual(hostile["presentation_density_after_dominated_duplicate"], "1/3")
        self.assertTrue(hostile["presentation_estimator_representation_sensitive"])

    def test_all_certified_surface_remints_preserve_points(self):
        remint = self.census["remint"]
        self.assertEqual(remint["certified_surface_remint_count"], 120)
        self.assertEqual(remint["registered_presentation_count"], 576)
        self.assertEqual(remint["morphology_point_invariance_checks"], 69_120)
        self.assertTrue(remint["frontier_and_density_invariant_by_factorization"])

    def test_scientific_ledger_and_package_contracts(self):
        self.assertEqual(
            M.validate_scientific_ledger(),
            {"claim_ledgers": 3, "open_gaps": 9, "closure_level": "REGISTERED_FINITE_SCOPE_ONLY"},
        )
        self.assertEqual(
            M.validate_package_contracts(),
            {"manifest_ok": True, "reconciliation_ok": True, "reconciliation_rows": 1, "source_pr": 996},
        )

    def test_receipt_is_green_and_byte_stable(self):
        receipt = M.build_receipt()
        self.assertEqual(receipt["verdict"], "GREEN")
        self.assertTrue(all(receipt["checks"].values()))
        checked_in = (HERE / "RESULT_V1.json").read_text(encoding="utf-8")
        self.assertEqual(M.canonical_json(receipt), checked_in)
        self.assertEqual(json.loads(checked_in), receipt)

    def test_claim_boundary_keeps_all_adjacent_rows_open(self):
        receipt = M.build_receipt({"all_ok": True, "rows": []})
        self.assertEqual(receipt["claim_ceiling"], M.CLAIM_CEILING)
        self.assertIn("ALL_SEARCH_LAW_REACHABILITY_MEASURED", receipt["forbidden_promotions"])
        self.assertIn("CLUSTERING_PERFORMED", receipt["forbidden_promotions"])
        self.assertIn("UNKNOWN_CLUSTER_VALIDATED", receipt["forbidden_promotions"])
        self.assertIn("UNIVERSAL_PARETO_DENSITY", receipt["forbidden_promotions"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
