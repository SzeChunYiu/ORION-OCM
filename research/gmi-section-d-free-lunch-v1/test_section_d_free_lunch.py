import importlib.util
import json
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("section_d_witness", HERE / "section_d_free_lunch_witness.py")
W = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(W)


class SectionDFreeLunchTests(unittest.TestCase):
    def test_uniform_all_function_control_is_exact_nfl(self):
        rows = W.nfl_control()
        self.assertEqual(len(rows), 8)
        for row in rows:
            self.assertEqual(row["low_distribution"], row["high_distribution"])

    def test_structured_information_has_strict_registered_value(self):
        r = W.structured_free_lunch()
        self.assertEqual(r["best_constant"], "1/2")
        self.assertEqual(r["conditioned"], "8/9")
        self.assertEqual(r["free_lunch_gap"], "7/18")
        self.assertFalse(r["structured_class_closed_under_all_input_permutations"])

    def test_decision_theorem_and_strictness_criterion_exhaustively(self):
        r = W.decision_value_of_information_examples()
        self.assertEqual(r["tables_checked"], 3 ** 12)
        self.assertGreater(r["strict"], 0)
        self.assertGreater(r["equality"], 0)

    def test_four_coarse_collision_worlds_have_four_different_frontiers(self):
        r = W.morphology_phase_witness()
        self.assertTrue(r["coarse_map_has_four_distinct_frontiers"])
        self.assertEqual(r["common_morphology_across_all_four_frontiers"], [])
        got = {k: v["frontier_Q16_mem8"] for k, v in r["worlds"].items()}
        self.assertEqual(got, W.FROZEN_UNIQUE)

    def test_surface_remint_preserves_structural_verdicts(self):
        r = W.morphology_phase_witness()
        for row in r["worlds"].values():
            self.assertEqual(row["frontier_Q16_mem8"], row["remint_frontier_Q16_mem8"])
            for key in (
                "algebraic_degree",
                "algebraic_support_size_if_degree_le_1",
                "minority_count",
                "best_hamming_weight_step_residual",
            ):
                self.assertEqual(row["signature"][key], row["remint_signature"][key])

    def test_two_frontier_implementations_agree_on_every_registered_cell(self):
        for fn in W.WORLD_FNS.values():
            values = W.truth(fn)
            for q in range(1, 41):
                rows = W.candidates(values, q, 64)
                self.assertEqual(W.frontier_all_pairs(rows), W.frontier_incremental(rows))

    def test_committed_receipt_is_exact_reproduction(self):
        receipt = json.loads((HERE / "RESULT_V1.json").read_text())
        self.assertEqual(receipt["freeze_commit"], "3fc4ddb2af98f738e5898a63488341c0d11f4364")
        self.assertEqual(receipt["nfl_control"], W.nfl_control())
        self.assertEqual(receipt["structured_free_lunch"], W.structured_free_lunch())
        self.assertEqual(receipt["decision_theorem_exhaustion"], W.decision_value_of_information_examples())
        self.assertEqual(receipt["morphology_phase"], W.morphology_phase_witness())

    def test_hostile_remove_structure_destroys_unique_selection(self):
        r = W.morphology_phase_witness()
        fronts = [tuple(row["frontier_Q16_mem8"]) for row in r["worlds"].values()]
        self.assertEqual(len(set(fronts)), 4)
        self.assertFalse(set(fronts[0]).intersection(*map(set, fronts[1:])))


if __name__ == "__main__":
    unittest.main()
