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
    "finite_morphology_metrics_v1_tested", HERE / "finite_morphology_metrics_v1.py"
)
M = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)

ORACLE_SPEC = importlib.util.spec_from_file_location(
    "independent_collapse_oracle_v1_tested", HERE / "independent_collapse_oracle_v1.py"
)
O = importlib.util.module_from_spec(ORACLE_SPEC)
assert ORACLE_SPEC and ORACLE_SPEC.loader
ORACLE_SPEC.loader.exec_module(O)


class FiniteMorphologyMetricTests(unittest.TestCase):
    def test_parent_artifacts_are_exactly_pinned(self):
        audit = M.audit_parents()
        self.assertTrue(audit["all_ok"])
        self.assertEqual(len(audit["rows"]), 3)

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

    def test_exact_collapse_measurements_and_direct_oracle(self):
        census = M.collapse_census()
        rows = {tuple(row["budget"]): row for row in census["budget_rows"]}
        expected = {
            (1, 1): (5, 4, 1, "1/5", 1, "1/10"),
            (2, 1): (126, 18, 108, "6/7", 1838, "1838/7875"),
            (1, 2): (14, 4, 10, "5/7", 22, "22/91"),
            (2, 2): (576, 21, 555, "185/192", 42091, "42091/165600"),
        }
        for budget, values in expected.items():
            row = rows[budget]
            self.assertEqual(
                (
                    row["presentation_count"],
                    row["semantic_class_count"],
                    row["collapsed_presentation_count"],
                    row["collapse_fraction"],
                    row["equivalent_unordered_pair_count"],
                    row["pair_collision_fraction"],
                ),
                values,
            )
            self.assertTrue(row["independent_oracle_exact_match"])
            self.assertEqual(
                sum(int(size) * count for size, count in row["multiplicity_histogram"].items()),
                row["presentation_count"],
            )

    def test_independent_oracle_counts_pairs_directly(self):
        result = O.direct_collapse_statistics(("a", "a", "b", "c", "c", "c"))
        self.assertEqual(result["semantic_class_count"], 3)
        self.assertEqual(result["collapsed_presentation_count"], 3)
        self.assertEqual(result["equivalent_unordered_pair_count"], 4)
        self.assertEqual(result["multiplicity_histogram"], ((1, 1), (2, 1), (3, 1)))
        with self.assertRaises(ValueError):
            O.direct_collapse_statistics(())

    def test_collapse_rejects_duplicate_presentations(self):
        program = M.F.CandidateProgram(1, (M.F.Instruction("HALT"),))
        with self.assertRaises(ValueError):
            M.collapse_statistics((program, program))
        with self.assertRaises(ValueError):
            M.collapse_statistics(())

    def test_canonical_histories_are_legal_bounded_and_realized(self):
        programs = M.registered_programs()
        histories = [M.canonical_history(program) for program in programs]
        self.assertEqual(max(map(len, histories)), 4)
        candidate_milestones = {
            M.program_milestone(program)
            for program in programs
        }
        for program, history in zip(programs, histories):
            self.assertEqual(history[0], M.seed_milestone())
            self.assertEqual(history[-1], M.program_milestone(program))
            self.assertTrue(set(history).issubset(candidate_milestones))

    def test_record_contracts_fail_closed(self):
        seed = M.seed_milestone()
        observations = seed.observations
        for resources in ((0, 1), (1, 0), (3, 1), (True, 1), [1, 1]):
            with self.subTest(resources=resources), self.assertRaises(ValueError):
                M.Milestone(observations, resources)
        bad_observations = (
            (),
            (("HALTED", ()),),
            (("OTHER", ()), ("HALTED", ()), ("HALTED", ())),
            (("HALTED", [0]), ("HALTED", ()), ("HALTED", ())),
            (("HALTED", (-1,)), ("HALTED", ()), ("HALTED", ())),
        )
        for value in bad_observations:
            with self.subTest(observations=value), self.assertRaises(ValueError):
                M.Milestone(value, (1, 1))
        target = M.program_milestone(M.all_halt_program((2, 1)))
        with self.assertRaises(ValueError):
            M.MorphologyRecord(target.observations, target.resources, ())
        with self.assertRaises(ValueError):
            M.MorphologyRecord(target.observations, target.resources, (target,))
        illegal = M.Milestone(target.observations, (2, 2))
        with self.assertRaises(ValueError):
            M.MorphologyRecord(illegal.observations, illegal.resources, (seed, illegal))

    def test_metric_weights_require_positive_exact_fractions(self):
        for values in (
            (0, Fraction(1), Fraction(1)),
            (Fraction(0), Fraction(1), Fraction(1)),
            (Fraction(-1), Fraction(1), Fraction(1)),
            (Fraction(1), 1, Fraction(1)),
            (Fraction(1), Fraction(1), 1.0),
        ):
            with self.subTest(values=values), self.assertRaises(ValueError):
                M.MetricWeights(*values)

    def test_atomic_semantic_hamming_has_exact_maximum_three(self):
        records = M.distinct_registered_records()
        observed = max(M.semantic_component(a.observations, b.observations) for a in records for b in records)
        self.assertEqual(observed, 3)
        self.assertEqual(len(M.REGISTERED_INTERFACE_WORDS), 3)

    def test_all_factor_and_product_metric_axioms(self):
        census = M.metric_axiom_census()
        self.assertEqual(census["semantic_factor"]["domain_size"], 21)
        self.assertEqual(census["resource_factor"]["domain_size"], 4)
        self.assertEqual(census["developmental_factor"]["domain_size"], 47)
        self.assertEqual(census["weighted_product"]["domain_size"], 47)
        self.assertEqual(census["weighted_product"]["triangle_checks"], 47**3)
        self.assertTrue(all(row["all_metric_axioms_hold"] for row in census.values()))

    def test_novelty_is_archive_exact_lipschitz_and_not_syntax(self):
        census = M.novelty_census()
        self.assertEqual(census["archive_morphology_count"], 4)
        self.assertEqual(census["distinct_registered_morphology_count"], 47)
        self.assertEqual(census["novelty_zero_exact_checks"], 47)
        self.assertEqual(census["novelty_lipschitz_checks"], 47**2)
        self.assertGreater(census["zero_distance_distinct_syntax_pair_count"], 0)
        self.assertEqual(census["development_only_witness_distance"], "2/1")

    def test_novelty_archive_contract_fails_closed(self):
        record = M.distinct_registered_records()[0]
        with self.assertRaises(ValueError):
            M.novelty_score(record, ())
        with self.assertRaises(ValueError):
            M.novelty_score(record, (record, record))
        with self.assertRaises(ValueError):
            M.novelty_score("not-a-record", (record,))

    def test_all_surface_remints_and_semantic_hostile(self):
        census = M.remint_census()
        self.assertEqual(census["certified_surface_remint_count"], 120)
        self.assertEqual(census["registered_presentation_count"], 576)
        self.assertEqual(census["morphology_record_invariance_checks"], 69_120)
        self.assertEqual(census["implied_ordered_distance_invariance_checks"], 39_813_120)
        self.assertTrue(census["semantics_changing_hostile_detected"])
        self.assertGreater(Fraction(census["hostile_morphology_distance"]), 0)

    def test_registered_metric_perturbation_bound_and_exact_margin_audit(self):
        census = M.perturbation_census()
        self.assertEqual(census["analytic_uniform_bound"], "9/100")
        self.assertEqual(census["distinct_morphology_pair_checks"], 47 * 46 // 2)
        self.assertEqual(census["candidate_novelty_bound_checks"], 576)
        self.assertEqual(census["threshold_classification_checks"], 576)
        self.assertGreater(census["strict_novelty_order_checks"], 0)
        self.assertGreater(
            Fraction(census["minimum_base_strict_novelty_gap"]),
            Fraction(census["required_two_sided_order_margin"]),
        )
        self.assertGreater(
            Fraction(census["minimum_base_threshold_margin"]),
            Fraction(census["analytic_uniform_bound"]),
        )
        self.assertLessEqual(Fraction(census["observed_max_pair_change"]), Fraction(9, 100))
        self.assertLessEqual(Fraction(census["observed_max_novelty_change"]), Fraction(9, 100))
        self.assertTrue(census["all_registered_stability_checks"])

    def test_scientific_ledger_and_package_contracts(self):
        self.assertEqual(
            M.validate_scientific_ledger(),
            {"claim_ledgers": 5, "open_gaps": 10, "closure_level": "REGISTERED_FINITE_SCOPE_ONLY"},
        )
        self.assertEqual(
            M.validate_package_contracts(),
            {"manifest_ok": True, "reconciliation_ok": True, "reconciliation_rows": 3, "source_pr": 984},
        )

    def test_receipt_is_green_and_byte_stable(self):
        receipt = M.build_receipt()
        self.assertEqual(receipt["verdict"], "GREEN")
        self.assertTrue(all(receipt["checks"].values()))
        checked_in = (HERE / "RESULT_V1.json").read_text(encoding="utf-8")
        self.assertEqual(M.canonical_json(receipt), checked_in)
        self.assertEqual(json.loads(checked_in), receipt)

    def test_claim_boundary_keeps_clustering_and_scale_open(self):
        receipt = M.build_receipt({"all_ok": True, "rows": []})
        self.assertEqual(receipt["claim_ceiling"], M.CLAIM_CEILING)
        self.assertIn("CLUSTERING_STABILITY_VALIDATED", receipt["forbidden_promotions"])
        self.assertIn("SCALABLE_LARGE_BUDGET_SAMPLING", receipt["forbidden_promotions"])
        self.assertIn("ALL_SEARCH_LAW_REACHABILITY_MEASURED", receipt["forbidden_promotions"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
