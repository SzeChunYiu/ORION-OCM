#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("ecology_sampling_v1", HERE / "ecology_sampling_v1.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load ecology sampling module")
M = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


class EcologySamplingV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = M.build_ledger()

    def test_freeze_scope_and_prospective_history_are_exact(self):
        freeze = (HERE / "FREEZE_V1.md").read_text(encoding="utf-8")
        self.assertEqual(M.TARGET_ROWS, (
            "Sample enough ecology space to avoid hand-picked niche bias.",
            "Quantify ecology sampling bias and uncertainty.",
        ))
        self.assertEqual(M.FREEZE_COMMIT, "18615590d16af8c0e69e7e259dc2b96abe479832")
        self.assertEqual(M.DRAW_COMMIT, "90f1250b91bce637a64fc06e001d046d0c6961dc")
        self.assertIn("No redraw\nis permitted", freeze)
        self.assertIn("unregistered, infinite, natural, deployed, or real-world", freeze)

    def test_rank_bijection_round_trips_all_registered_ranks(self):
        seen = bytearray(M.POPULATION_SIZE)
        for rank in range(M.POPULATION_SIZE):
            indices = M.rank_to_indices(rank)
            self.assertEqual(M.indices_to_rank(indices), rank)
            seen[rank] = 1
        self.assertTrue(all(seen))

    def test_rank_interfaces_reject_bool_float_and_bounds(self):
        for bad in (True, False, -1, M.POPULATION_SIZE, 0.0, "0"):
            with self.subTest(bad=repr(bad)), self.assertRaises(ValueError):
                M.rank_to_indices(bad)
        for bad in (True, False, 0.0, "0", -1, 2):
            values = [0] * M.AXIS_COUNT
            values[4] = bad
            with self.subTest(bad=repr(bad)), self.assertRaises(ValueError):
                M.indices_to_rank(values)

    def test_frozen_diagnostics_are_exact_and_architecture_neutral(self):
        zeros = M.diagnostic_values((0,) * M.AXIS_COUNT)
        ones = M.diagnostic_values((1,) * M.AXIS_COUNT)
        self.assertEqual(zeros, {name: Fraction(0, 1) for name in M.DIAGNOSTIC_NAMES})
        self.assertEqual(ones, {
            "axis_load": Fraction(1, 1),
            "rare_niche": Fraction(1, 1),
            "global_parity": Fraction(1, 1),
            "cross_pair": Fraction(1, 1),
        })

    def test_dependency_basis_and_factorized_semantics_are_valid(self):
        audit = self.ledger["dependency_basis_audit"]
        self.assertTrue(audit["passes"])
        self.assertEqual(audit["basis_level_count"], 34)
        self.assertEqual(audit["dependency_witness_count"], 19)
        self.assertTrue(all(all(row[key] for key in row if key != "rank") for row in audit["rows"]))

    def test_census_is_complete_unique_semantic_and_analytically_checked(self):
        census = self.ledger["census"]
        self.assertEqual(census["arithmetic_product"], 131072)
        self.assertEqual(census["recursive_product"], 131072)
        self.assertEqual(census["iterator_count"], 131072)
        self.assertEqual(census["unique_rank_count"], 131072)
        self.assertTrue(census["complete_integer_interval"])
        self.assertEqual(census["compact_semantic_failures"], 0)
        self.assertEqual(census["compact_target_failures"], 0)
        self.assertEqual(census["means"], {
            "axis_load": "1/2",
            "rare_niche": "1/32",
            "global_parity": "1/2",
            "cross_pair": "1/4",
        })
        self.assertTrue(census["means_match_independent_analytic_values"])

    def test_prospective_draw_receipt_replays_and_is_canonical(self):
        receipt = json.loads((HERE / "PROSPECTIVE_DRAW_V1.json").read_text(encoding="utf-8"))
        validation = M.DRAW.validate_receipt(receipt)
        self.assertTrue(validation["valid"])
        self.assertEqual(validation["distinct_ranks"], 4096)
        self.assertEqual(M.DRAW.reconstruct_ranks(receipt["offsets"]), receipt["sampled_ranks"])
        self.assertEqual(M.canonical(receipt), (HERE / "PROSPECTIVE_DRAW_V1.json").read_bytes())

    def test_draw_provenance_metadata_fails_closed(self):
        receipt = json.loads((HERE / "PROSPECTIVE_DRAW_V1.json").read_text(encoding="utf-8"))
        for field, hostile in (
            ("generated_at_utc", "not-a-time"),
            ("generated_at_utc", "2026-09-17T07:45:52"),
            ("entropy_source", "hand selected"),
            ("entropy_boundary", "entropy is proved ideal"),
        ):
            changed = deepcopy(receipt)
            changed[field] = hostile
            with self.subTest(field=field, hostile=hostile), self.assertRaises(ValueError):
                M.DRAW.validate_receipt(changed)

    def test_partial_fisher_yates_rejects_invalid_offsets(self):
        for offsets in ([True], [-1], [M.POPULATION_SIZE], [0, M.POPULATION_SIZE - 1]):
            with self.subTest(offsets=offsets), self.assertRaises(ValueError):
                M.DRAW.reconstruct_ranks(offsets)
        self.assertEqual(M.DRAW.reconstruct_ranks([0, 0, 0], 4), [0, 1, 2])
        self.assertEqual(len(set(M.DRAW.reconstruct_ranks([3, 0, 0], 4))), 3)

    def test_draw_interface_has_no_outcome_or_score_channel(self):
        audit = self.ledger["draw_independence_audit"]
        self.assertTrue(audit["passes"])
        self.assertEqual(audit["forbidden_outcome_term_hits"], [])
        self.assertEqual(audit["create_receipt_parameters"], [])
        self.assertEqual(audit["reconstruct_ranks_parameters"], ["offsets", "population_size"])

    def test_all_preregistered_coverage_gates_pass(self):
        coverage = self.ledger["coverage"]
        self.assertTrue(coverage["passes"])
        self.assertTrue(all(coverage["checks"].values()))
        self.assertGreaterEqual(coverage["minimum_axis_cell_count"], 1600)
        self.assertGreaterEqual(coverage["minimum_pair_cell_count"], 700)
        self.assertGreaterEqual(coverage["rare_niche_sample_count"], 64)
        self.assertLessEqual(Fraction(coverage["hamming_total_variation"]), Fraction(1, 20))
        self.assertEqual(len(coverage["axis_cells"]), 17)
        self.assertEqual(len(coverage["pair_cells"]), 136)

    def test_statistics_keep_design_bias_and_realized_error_distinct(self):
        y = [Fraction(0), Fraction(0), Fraction(1), Fraction(1)]
        stats = M.sampling_statistics(y, [0, 2])
        self.assertEqual(stats["population_mean"], "1/2")
        self.assertEqual(stats["sample_mean"], "1/2")
        self.assertEqual(stats["design_bias"], "0/1")
        self.assertEqual(stats["signed_realized_sampling_error"], "0/1")
        nonzero = M.sampling_statistics(y, [0, 1])
        self.assertEqual(nonzero["design_bias"], "0/1")
        self.assertEqual(nonzero["signed_realized_sampling_error"], "-1/2")

    def test_horvitz_thompson_and_inclusion_probabilities_are_exact(self):
        for name, row in self.ledger["sampling_statistics"].items():
            with self.subTest(name=name):
                self.assertTrue(row["ht_equals_sample_mean"])
                self.assertEqual(row["first_order_inclusion_probability"], "1/32")
                self.assertEqual(row["second_order_inclusion_probability"], "4095/4194272")
                self.assertEqual(row["finite_population_correction"], "31/32")
                self.assertEqual(row["design_bias"], "0/1")

    def test_finite_population_correction_is_not_with_replacement_variance(self):
        for name, row in self.ledger["sampling_statistics"].items():
            with self.subTest(name=name):
                self.assertTrue(row["finite_population_correction_is_load_bearing"])
                self.assertNotEqual(row["unbiased_design_variance_estimate"], row["with_replacement_variance_estimate_hostile"])

    def test_small_exhaustive_design_oracle_confirms_all_formulas(self):
        oracle = self.ledger["small_population_oracle"]
        self.assertEqual(oracle["enumerated_samples"], 10)
        self.assertEqual(oracle["design_bias"], "0/1")
        self.assertEqual(oracle["enumerated_design_variance"], "3/64")
        self.assertEqual(oracle["formula_design_variance"], "3/64")
        self.assertEqual(oracle["mean_variance_estimate"], "3/64")
        self.assertTrue(oracle["unbiased_mean"])
        self.assertTrue(oracle["variance_formula_exact"])
        self.assertTrue(oracle["variance_estimator_unbiased"])

    def test_hand_picked_and_outcome_selected_hostiles_are_exposed(self):
        audit = self.ledger["hostile_panels"]
        self.assertTrue(audit["all_panels_exposed"])
        self.assertTrue(audit["outcome_selected_panel_is_labeled_invalid_for_prospective_inference"])
        self.assertEqual({row["panel"] for row in audit["rows"]}, {
            "all_zero_prefix",
            "low_hamming_weight_niche",
            "outcome_selected_axis_load_top",
        })
        self.assertTrue(all(row["exposed_by"] for row in audit["rows"]))

    def test_malformed_samples_and_outcomes_fail_closed(self):
        self.assertTrue(self.ledger["hostile_inputs"]["passes"])
        self.assertTrue(all(self.ledger["hostile_inputs"]["checks"].values()))

    def test_scope_expansion_fails_closed(self):
        self.assertTrue(M.validate_scope(M.REGISTERED_SCOPE))
        for hostile in ("real_world", "unregistered", "all_possible_ecologies", ""):
            with self.subTest(hostile=hostile), self.assertRaises(ValueError):
                M.validate_scope(hostile)

    def test_manifest_and_reconciliation_target_exactly_two_rows(self):
        self.assertEqual(M.validate_package_contracts(), {"artifacts": 11, "target_rows": 2})
        reconciliation = json.loads((HERE / "ISSUE_833_RECONCILIATION_ECOLOGY_SAMPLING_V1.json").read_text())
        self.assertEqual(len(reconciliation["replacements"]), 2)
        self.assertTrue(all("PR #985" in row["new"] and "#982" in row["new"] for row in reconciliation["replacements"]))
        self.assertTrue(all("Scope is the registered finite product only" in row["new"] or "No unregistered-universe inference" in row["new"] for row in reconciliation["replacements"]))

    def test_ledger_is_canonical_and_claim_boundary_is_explicit(self):
        self.assertEqual(M.canonical(self.ledger), (HERE / "SCIENTIFIC_LEDGER_V1.json").read_bytes())
        boundary = self.ledger["claim_boundary"]
        self.assertTrue(any("unregistered" in row for row in boundary["not_claimed"]))
        self.assertTrue(any("4096" in row for row in boundary["not_claimed"]))

    def test_result_is_green_and_byte_stable(self):
        result = M.run()
        self.assertEqual(result["status"], "GREEN")
        self.assertEqual(result["terminal"], M.TERMINAL)
        self.assertTrue(all(result["checks"].values()))
        self.assertEqual(result["counts"]["registered_population"], 131072)
        self.assertEqual(result["counts"]["census_members"], 131072)
        self.assertEqual(result["counts"]["prospective_sample_members"], 4096)
        self.assertEqual(M.canonical(result), (HERE / "RESULT_V1.json").read_bytes())


if __name__ == "__main__":
    unittest.main()
