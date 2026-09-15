import json
import tempfile
import unittest
from pathlib import Path

import section_e_reachability_witness as w


class E1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = w.build_results()

    def test_all_frozen_predictions(self):
        self.assertTrue(self.r["all_frozen_predictions_pass"])
        self.assertTrue(all(self.r["assertions"].values()))

    def test_affine_error_plateau_is_exhaustive(self):
        profile = w.all_error_profile(w.TARGET)
        self.assertEqual(profile[w.TARGET], 0)
        self.assertEqual(set(err for mask, err in profile.items() if mask != w.TARGET), {16})
        self.assertEqual(len(profile), 32)

    def test_pair_flip_global_unreachability_is_parity_invariant(self):
        pair = w.bfs(w.TARGET, w.pair_neighbors, stop_on_target=False)
        self.assertFalse(pair["found"])
        self.assertEqual(pair["verifications"], 16)
        self.assertTrue(all(mask.bit_count() % 2 == 0 for mask in pair["evaluated"]))
        self.assertNotIn(w.TARGET, pair["evaluated"])
        self.assertEqual(pair["burden"], 672)

    def test_adding_single_flip_restores_reachability(self):
        single = w.bfs(w.TARGET, w.single_neighbors)
        self.assertTrue(single["found"])
        self.assertEqual((single["verifications"], single["proposals"], single["burden"]), (21, 100, 772))

    def test_operator_hostile_single_flip_breaks_negative_terminal(self):
        def pair_plus_bridge(mask):
            yield from w.pair_neighbors(mask)
            yield mask ^ 1
        result = w.bfs(w.TARGET, pair_plus_bridge)
        self.assertTrue(result["found"])

    def test_reachable_but_strict_local_search_is_plateau_blocked(self):
        local = w.strict_local_search(w.TARGET)
        self.assertFalse(local["found"])
        self.assertEqual(local["terminal"], w.PLATEAU_TERMINAL)
        self.assertEqual((local["verifications"], local["proposals"], local["burden"]), (6, 5, 197))

    def test_prefix_code_is_complete_and_encoding_changes_burden(self):
        self.assertEqual(w.prefix_kraft_sum(), 1)
        short = w.levin_best_first(w.TARGET, "ENC_SHORT")
        long = w.levin_best_first(w.TARGET, "ENC_LONG")
        self.assertEqual((short["verifications"], short["code_length"], short["burden"]), (1, 1, 33))
        self.assertEqual((long["verifications"], long["code_length"], long["burden"]), (32, 31, 1056))
        self.assertEqual(1 << (long["code_length"] - short["code_length"]), 1 << 30)

    def test_finite_budget_changes_observed_recovery_not_target_semantics(self):
        short = w.levin_best_first(w.TARGET, "ENC_SHORT", w.BUDGET_VERIFICATIONS)
        long = w.levin_best_first(w.TARGET, "ENC_LONG", w.BUDGET_VERIFICATIONS)
        bfs = w.bfs(w.TARGET, w.single_neighbors)
        self.assertTrue(short["found"])
        self.assertFalse(long["found"])
        self.assertGreater(bfs["verifications"], w.BUDGET_VERIFICATIONS)
        self.assertEqual(w.levin_best_first(w.TARGET, "ENC_LONG")["tested"][-1], w.TARGET)

    def test_remint_preserves_reachability_class_but_changes_raw_bfs_burden(self):
        target, support = w.remint_target()
        self.assertEqual((target, support), (11, [0, 1, 3]))
        pair = w.bfs(target, w.pair_neighbors, stop_on_target=False)
        single = w.bfs(target, w.single_neighbors)
        local = w.strict_local_search(target)
        self.assertFalse(pair["found"])
        self.assertEqual(pair["verifications"], 16)
        self.assertEqual(local["terminal"], w.PLATEAU_TERMINAL)
        self.assertEqual((single["verifications"], single["proposals"], single["burden"]), (18, 85, 661))
        self.assertNotEqual(single["burden"], self.r["single_bfs"]["burden"])

    def test_receipt_reproduction(self):
        here = Path(__file__).resolve().parent
        committed = json.loads((here / "RESULT_E1.json").read_text())
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "result.json"
            out.write_text(json.dumps(w.receipt(w.build_results()), indent=2, sort_keys=True) + "\n")
            reproduced = json.loads(out.read_text())
        self.assertEqual(committed, reproduced)


if __name__ == "__main__":
    unittest.main()
