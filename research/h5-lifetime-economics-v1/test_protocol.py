"""H5 lifetime-economics protocol tests. Frozen H1/G2 receipts are inputs."""
from __future__ import annotations

import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path

import experiment as E


FROZEN_DIRS = (
    E.REPO / "research" / "h1-amortized-rewrite-v2",
    E.REPO / "research" / "h1-amortized-acquisition-v1",
    E.REPO / "research" / "machine-epistemics-lifetime-v1",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TestH5LifetimeEconomics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before_frozen = {str(path): _tree_digest(path) for path in FROZEN_DIRS}
        cls.tmp = tempfile.TemporaryDirectory()
        cls.result = E.main(Path(cls.tmp.name) / "RESULT.json")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_methods_blob_pinned(self):
        self.assertEqual(E.git_blob_sha1(E.SRC / "ocm" / "learning" / "methods.py"), E.METHOD_BLOB)
        self.assertEqual(self.result["methods_blob"], E.METHOD_BLOB)
        self.assertEqual(tuple(E.H1.M.PRIMITIVES), ("inc", "dec", "double", "square"))

    def test_h1_capital_is_input_not_denied(self):
        h1 = self.result["h1_capital_input"]
        self.assertFalse(h1["denied"])
        self.assertEqual(h1["terminal"], "LIBRARY_ACQUISITION_EXCEEDS_LATER_SAVINGS")
        self.assertEqual(h1["library_compute"], 132863)
        self.assertEqual(h1["later_k0_compute"], 59929)
        self.assertEqual(h1["later_kt_compute"], 36289)
        self.assertEqual(h1["later_saving_compute"], 23640)
        self.assertEqual(h1["sha256"], E.H1_RESULT_SHA256)
        self.assertFalse(self.result["h1_v2_result_overwritten"])
        self.assertFalse(self.result["h1_v1_result_overwritten"])
        self.assertEqual(_sha256(E.H1_RESULT), E.H1_RESULT_SHA256)

    def test_g2_break_even_cited_not_rerun(self):
        g2 = self.result["g2_cited_not_rerun"]
        self.assertTrue(g2["cited_not_rerun"])
        self.assertEqual(g2["break_even_tasks_with_tournament"], 2136)
        self.assertEqual(g2["break_even_tasks_with_zero_search_acquisition"], 41)
        self.assertEqual(g2["tournament_acquisition_enumeration_attempts"], 9_010_526)
        self.assertEqual(g2["zero_search_acquisition_enumeration_attempts"], 0)
        self.assertEqual(g2["search_aware_token_operations"], 4608)
        source = Path(E.__file__).read_text(encoding="utf-8")
        self.assertNotIn("build_search_index", source)
        self.assertIn("is not rerun here", g2["note"])

    def test_search_aware_scan_is_zero_enumeration(self):
        scan = self.result["scan"]
        self.assertEqual(scan["enumeration_attempts"], 0)
        self.assertEqual(scan["unique_checks"], 0)
        self.assertEqual(scan["token_operations"], 512)
        self.assertFalse(
            scan["agrees_with_h1_admitted"],
            "H1 rewrite-benefit scan has no G2 widening term; it must not be silently treated as SEARCH_AWARE agreement",
        )
        cheap = self.result["arms"]["search_aware"]
        tourn = self.result["arms"]["tournament"]
        self.assertEqual(cheap["acquisition_compute"], 3866)
        self.assertEqual(tourn["acquisition_compute"], 132863)
        self.assertEqual(cheap["scan_token_operations"], scan["token_operations"])
        self.assertEqual(tourn["scan_token_operations"], 0)
        self.assertNotEqual(
            cheap["acquisition_compute"] + cheap["scan_token_operations"],
            cheap["lifetime_compute_kt"],
            "token operations must not be added into enumeration lifetime compute",
        )

    def test_no_dollar_scalarization(self):
        self.assertFalse(self.result["dollars_claimed"])
        self.assertFalse(self.result["scalarized_incommensurable_resources"])
        self.assertNotIn("dollars", self.result)
        self.assertNotIn("usd", self.result)
        self.assertNotIn("combined_score", self.result)
        self.assertNotIn("utility_scalar", self.result)
        self.assertIn("DOLLARS", self.result["not_issued"])
        self.assertIn("SCALARIZED_INCOMMENSURABLE_RESOURCES", self.result["not_issued"])
        cheap = self.result["arms"]["search_aware"]
        # Bytes and attempts remain distinct integers on their own keys.
        self.assertIsInstance(cheap["state_written"], int)
        self.assertIsInstance(cheap["acquisition_compute"], int)
        self.assertNotEqual(cheap["state_written"], cheap["acquisition_compute"])

    def test_coordinates_are_separate(self):
        self.assertEqual(self.result["coordinates"], list(E.COORDINATES))
        for arm in self.result["arms"].values():
            for key in (
                "acquisition_compute",
                "later_k0_compute",
                "later_kt_compute",
                "maintenance_work",
                "state_written",
                "scan_token_operations",
                "examples",
            ):
                self.assertIn(key, arm)
                self.assertIsInstance(arm[key], int)
                self.assertGreaterEqual(arm[key], 0)

    def test_tournament_net_negative_cheap_net_positive_on_compute(self):
        tourn = self.result["arms"]["tournament"]
        cheap = self.result["arms"]["search_aware"]
        self.assertEqual(tourn["later_saving_compute"], 23640)
        self.assertLess(tourn["compute_net_later_saving_minus_acquisition_minus_maintenance"], 0)
        self.assertGreater(cheap["compute_net_later_saving_minus_acquisition_minus_maintenance"], 0)
        self.assertTrue(self.result["sign_flips_vs_tournament_capital"])
        self.assertEqual(
            self.result["tournament_arm_terminal"],
            "LIFETIME_NET_NEGATIVE_AT_POLYNOMIAL_HORIZON",
        )
        self.assertEqual(
            self.result["search_aware_arm_terminal"],
            "LIFETIME_NET_POSITIVE_AFTER_CHEAP_ACQUISITION",
        )
        self.assertEqual(self.result["terminal"], "LIFETIME_NET_POSITIVE_AFTER_CHEAP_ACQUISITION")
        self.assertLess(tourn["maintenance_work"], 19774)

    def test_h1_horizon_sits_between_break_evens(self):
        tourn = self.result["arms"]["tournament"]
        cheap = self.result["arms"]["search_aware"]
        self.assertEqual(tourn["later_n"], 16)
        self.assertEqual(tourn["break_even_later_tasks"], 90)
        self.assertEqual(cheap["break_even_later_tasks"], 3)
        self.assertFalse(tourn["horizon_meets_break_even"])
        self.assertTrue(cheap["horizon_meets_break_even"])
        box = self.result["boxes"]["H5/004-crossover_horizon"]
        self.assertEqual(box["g2_cited_break_even_tournament_length8"], 2136)
        self.assertEqual(box["g2_cited_break_even_zero_search_length8"], 41)

    def test_maintenance_is_measured_and_cheap(self):
        maint = self.result["maintenance"]
        self.assertIn(maint["choice"], {"incremental_posting_update", "revocation_restore"})
        self.assertGreater(maint["work_units_charged"], 0)
        restore = maint["revocation_restore"]
        self.assertTrue(restore["restore_returned_fragment"])
        self.assertTrue(restore["revoked_equals_absent"])
        self.assertGreater(restore["live_bytes"], 0)
        self.assertGreater(restore["restore_bytes"], 0)
        posting = maint["posting"]
        self.assertEqual(posting["incremental_update_units"], 1)
        self.assertEqual(posting["rebuild_units"], posting["n"] + 1)
        self.assertGreater(posting["rebuild_units"], posting["cheap_maintenance_units"])
        self.assertEqual(
            maint["work_units_charged"],
            min(restore["work_units"], posting["cheap_maintenance_units"]),
        )

    def test_pareto_prices_one_coordinate_at_a_time(self):
        cheap_p = self.result["pareto"]["search_aware"]
        tourn_p = self.result["pareto"]["tournament"]
        self.assertEqual(set(cheap_p["coordinates"]), set(E.COORDINATES))
        self.assertTrue(cheap_p["any_one_coordinate_price_flips_sign"])
        self.assertFalse(cheap_p["survives_all_one_at_a_time_prices"])
        self.assertFalse(tourn_p["survives_all_one_at_a_time_prices"])
        state = cheap_p["coordinates"]["state_written"]
        self.assertTrue(state["sign_flips_for_some_lambda"])
        self.assertIsInstance(state["lambda_star_where_priced_net_zero"], float)
        self.assertGreater(state["lambda_star_where_priced_net_zero"], 0)
        compute = cheap_p["coordinates"]["acquisition_compute"]
        self.assertFalse(compute["sign_flips_for_some_lambda"])
        for row in compute["sweep"]:
            if row["lambda"] > 0:
                self.assertEqual(row["sign_positive"], cheap_p["compute_net"] > 0)
        box = self.result["boxes"]["H5/003-survives_pareto_resource_price"]
        self.assertEqual(box["status"], "PRICE_REGIME_ONLY")
        # Pricing state must not rewrite the raw compute net.
        self.assertEqual(
            cheap_p["compute_net"],
            self.result["arms"]["search_aware"]["compute_net_later_saving_minus_acquisition_minus_maintenance"],
        )

    def test_m12_v5_corpus_cannot_check_miniature_only(self):
        m12 = self.result["m12_lifetime_v5_n1_n2"]
        self.assertEqual(m12["status"], "CANNOT_CHECK_N1_N2_ACQUISITION_AT_CORPUS_SCALE")
        self.assertFalse(m12["claimed"])
        self.assertFalse(self.result["m12_v5_n1_n2_corpus_claimed"])
        self.assertIn("M12_LIFETIME_V5_WITH_N1_N2_CORPUS_COST", self.result["not_issued"])
        n1 = self.result["n1_n2_miniature"]
        self.assertEqual(n1["label"], "MINIATURE_ONLY")
        self.assertTrue(n1["not_m12_v5"])
        self.assertTrue(n1["not_corpus_n1_n2"])
        self.assertTrue(n1["amortization_present_vs_reset"])
        box = self.result["boxes"]["H5/002-m12_lifetime_v5_n1_n2_acquisition"]
        self.assertEqual(box["status"], "CANNOT_CHECK_N1_N2_ACQUISITION_AT_CORPUS_SCALE")
        self.assertEqual(box["miniature"]["label"], "MINIATURE_ONLY")
        # Do not add language observations to polynomial enumeration.
        cheap = self.result["arms"]["search_aware"]
        self.assertNotEqual(cheap["acquisition_compute"], n1["acquisition_observations_persistent"])

    def test_physical_denominator_not_claimed_clean(self):
        g5 = self.result["g5_physical_denominator"]
        self.assertEqual(g5["terminal"], "DATABASE_PARENT_SUFFICIENT")
        self.assertFalse(g5["physical_denominator_clean"])
        self.assertEqual(g5["cognitive_claim_if_jsonl_dominates"], "NOT_CLEAN")
        self.assertIn("PHYSICAL_DENOMINATOR_CLEAN", self.result["not_issued"])
        self.assertGreater(g5["jsonl_cumulative_rewrite_bytes_at_2048"], 10**8)

    def test_boxes_map_issue_165_remaining_gates(self):
        boxes = self.result["boxes"]
        self.assertIn("H5/001-lifetime_benefit_after_training_inference_update_maintenance", boxes)
        self.assertIn("H5/002-m12_lifetime_v5_n1_n2_acquisition", boxes)
        self.assertIn("H5/003-survives_pareto_resource_price", boxes)
        self.assertEqual(
            boxes["H5/001-lifetime_benefit_after_training_inference_update_maintenance"]["status"],
            "EARNED_AT_SCOPE_ON_COMPUTE_AFTER_CHEAP_ACQUISITION",
        )
        self.assertFalse(boxes["H5/001-lifetime_benefit_after_training_inference_update_maintenance"]["vector_strictly_positive"])
        self.assertFalse(self.result["programme_wide_close"])
        self.assertIn("PROGRAMME_WIDE_H5_CLOSE", self.result["not_issued"])
        self.assertIn(self.result["terminal"], E.ALLOWED_TERMINALS)

    def test_production_src_and_frozen_capsules_untouched(self):
        diff = subprocess.check_output(["git", "diff", "--", "src"], cwd=E.REPO, text=True)
        self.assertEqual(diff.strip(), "")
        self.assertFalse(self.result["production_src_edited"])
        self.assertFalse(self.result["machine_epistemics_lifetime_v1_overwritten"])
        for path in FROZEN_DIRS:
            self.assertEqual(_tree_digest(path), self.before_frozen[str(path)], path)
        me = E.REPO / "research" / "machine-epistemics-lifetime-v1" / "README.md"
        self.assertTrue(me.exists())

    def test_scope_is_polynomial_microworld_only(self):
        self.assertEqual(self.result["scope"], "polynomial-microworld-lifetime-only")
        self.assertIn("polynomial+microworld", self.result["claim_ceiling"])
        self.assertNotIn("corpus-scale N1", self.result["claim_ceiling"])


def _tree_digest(root: Path) -> str:
    hasher = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        hasher.update(str(path.relative_to(root)).encode())
        hasher.update(path.read_bytes())
    return hasher.hexdigest()


if __name__ == "__main__":
    unittest.main()
