"""Tests for `gmi-833-body-residual-akl-v1`.

Run both ways:
  python3 -I -B  test_body_residual_akl_v1.py -v
  python3 -I -O -B test_body_residual_akl_v1.py -v

Every assertion is a unittest method call, so -O cannot silently disable any of
them. The receipts are read from the package; the semantics of the scanner, the
criterion and a live sub-census are re-derived here rather than trusted.
"""

from fractions import Fraction
import importlib.util
import json
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import body_residual_akl_v1 as A          # noqa: E402
import oracle_route_b_v1 as B             # noqa: E402

RESULT = json.load(open(os.path.join(HERE, "RESULT_V1.json")))
ORACLE = json.load(open(os.path.join(HERE, "ORACLE_RESULT_V1.json")))
ROWS = json.load(open(os.path.join(HERE, "FREEZE_ROWS_V1.json")))
RECON = json.load(open(os.path.join(HERE,
                                    "ISSUE_833_RECONCILIATION_BODY_RESIDUAL_V1.json")))

# The parent's own published non-degenerate point counts, used as an external
# cross-check on this package's counter.
PARENT_PUBLISHED = {"SIGMA_SYN2": 3872, "SIGMA_ARCH2": 2400}


class ScannerSemantics(unittest.TestCase):
    """Route B's hand-written scanner must agree with the parent gate pattern."""

    CASES = [
        ("an obligation here", 1),
        ("two obligations and one obligation", 2),
        ("obligational is not a hit", 0),
        ("Obligation at line start", 1),
        ("OBLIGATIONS shouted", 1),
        ("pre-obligation hyphenated", 1),
        ("noobligation glued", 0),
        ("obligation_suffix underscore", 0),
        ("`obligation` in backticks", 1),
        ("", 0),
        ("obligation", 1),
        ("obligations", 1),
        ("obligationss", 0),
    ]

    def test_agrees_with_the_parent_gate_pattern(self):
        rx = re.compile(A.ROW_A_PATTERN, re.IGNORECASE)
        for text, expected in self.CASES:
            self.assertEqual(len(rx.findall(text)), expected,
                             "parent pattern on %r" % text)
            self.assertEqual(B.count_term(text, B.TERM), expected,
                             "route B scanner on %r" % text)

    def test_route_a_uses_the_frozen_parent_pattern_unmodified(self):
        pattern, _mod = A.parent_gate_pattern()
        self.assertEqual(pattern, A.ROW_A_PATTERN)

    def test_null_control_terms_behave(self):
        self.assertEqual(B.count_term("nothing to see", A.NULL_ABSENT_TERM), 0)
        self.assertGreater(B.count_term("the cat sat on the mat", "the"), 1)


class RowAResidual(unittest.TestCase):

    def setUp(self):
        self.ra = RESULT["ROW_A"]

    def test_two_routes_agree_on_every_scope(self):
        for scope in ("S1", "S2", "S3"):
            a = self.ra["RA-1"]["scopes"][scope]
            b = ORACLE["ROW_A"][scope]
            self.assertEqual(a["total_hits"], b["total_hits"], scope)
            self.assertEqual(a["files_with_hits"], b["files_with_hits"], scope)
            self.assertEqual(a["files_scanned"], b["files_scanned"], scope)

    def test_two_routes_agree_on_the_preservation_clause(self):
        self.assertEqual(self.ra["RA-2"]["required_to_remain_hits"],
                         ORACLE["ROW_A"]["required_to_remain_hits"])
        self.assertEqual(self.ra["RA-2"]["required_to_remain_files"],
                         ORACLE["ROW_A"]["required_to_remain_files"])

    def test_the_row_does_not_close(self):
        self.assertGreater(self.ra["RA-1"]["governing_residual"], 0)
        self.assertFalse(self.ra["RA-1"]["row_closes"])
        self.assertEqual(RESULT["DISPOSITION"]["ROW_A"], "OPEN")

    def test_scopes_are_nested_as_declared(self):
        s = self.ra["RA-1"]["scopes"]
        self.assertGreaterEqual(s["S1"]["total_hits"], s["S2"]["total_hits"])
        self.assertGreaterEqual(s["S2"]["total_hits"], s["S3"]["total_hits"])

    def test_s3_reconciles_with_s2_exactly(self):
        """A third handle: S3 = S2 - required_to_remain + repo-root markdown."""
        r = self.ra["RA-1"]
        self.assertTrue(r["S3_reconciles_with_S2"])
        self.assertEqual(r["scopes"]["S3"]["total_hits"],
                         r["scopes"]["S2"]["total_hits"]
                         - self.ra["RA-2"]["required_to_remain_hits"]
                         + r["repo_root_md_hits"])

    def test_the_scanner_nulls(self):
        n = self.ra["NULLS"]
        self.assertEqual(n["absent_control_term_hits"], 0)
        self.assertTrue(n["absent_is_zero"])
        self.assertGreater(n["present_control_term_hits"], 1000)

    def test_hostiles_move_their_own_quantity(self):
        h = self.ra["HOSTILES"]
        self.assertLess(h["HA1_singular_only_pattern_hits"],
                        self.ra["RA-1"]["governing_residual"])
        self.assertTrue(h["HA1_detected"])
        self.assertLess(h["HA2_dropped_package_file_census"],
                        self.ra["RA-1"]["scopes"]["S3"]["files_scanned"])
        self.assertTrue(h["HA2_detected"])
        self.assertEqual(h["HA4_true_pins_verify"], 0)
        self.assertGreater(h["HA4_fabricated_pin_refused"], 0)

    def test_required_to_remain_lies_only_in_authority_packages(self):
        self.assertEqual(sorted(self.ra["RA-2"]["authority_packages"]),
                         sorted(A.AUTHORITY_PACKAGES))
        for path in self.ra["_per_file_S3"]:
            pkg = A.top_package(path)
            self.assertNotIn(pkg, A.AUTHORITY_PACKAGES, path)
            self.assertNotEqual(pkg, A.SELF_PACKAGE, path)

    def test_pin_index_rejects_bare_basenames(self):
        ra3 = self.ra["RA-3"]
        self.assertGreater(ra3["bare_basename_pins_rejected"], 0)
        for p in RESULT["ROW_A"]["_pins"]:
            self.assertIn("/", p)

    def test_ra3_is_not_read_as_a_closure(self):
        self.assertTrue(self.ra["RA-3"]["not_a_closure_argument"])
        self.assertEqual(self.ra["RA-3"]["residual_files"],
                         self.ra["RA-3"]["content_hash_pinned_files"]
                         + self.ra["RA-3"]["unpinned_files"])

    def test_paper_facing_phrase_is_not_invented(self):
        self.assertIn("UNDEFINED", self.ra["RA-1"]["paper_facing_phrase"])


class RowKBridge(unittest.TestCase):

    def setUp(self):
        self.rk = RESULT["ROW_K"]

    def test_no_machine_has_a_positive_singleton_admissible_set(self):
        self.assertTrue(self.rk["BR-1"]["holds"])
        for pop in self.rk["BR-1"]["per_population"]:
            self.assertEqual(pop["machines_with_positive_singleton_admissible_set"], 0)

    def test_admissible_sets_are_recomputed_here(self):
        """BR-1 re-derived in this file, from MU and the contract table only."""
        mu = (Fraction(8, 17), Fraction(6, 17), Fraction(3, 17))
        for contract, verified in (("E_full", (True, True, True)),
                                   ("E_v0", (False, True, True))):
            for h in (1, 3, 5, 7):
                machine = ("GRU", 16, 0, h)
                vals = set(A.cap_of_bits(mu, verified, b)
                           for b in A.admissible_bits(machine, "CB-PROTO", 3))
                positive_singleton = len(vals) == 1 and min(vals) > 0
                self.assertFalse(positive_singleton,
                                 "%s h=%d admissible values %r" % (contract, h, vals))

    def test_census_is_zero_and_the_row_does_not_close(self):
        self.assertEqual(self.rk["BR-2"]["non_degenerate_total"], 0)
        self.assertEqual(self.rk["BR-2"]["inputs_total"], 155520)
        self.assertFalse(self.rk["BR-2"]["row_closes"])
        self.assertEqual(RESULT["DISPOSITION"]["ROW_K"], "OPEN")

    def test_route_b_black_box_agrees(self):
        self.assertEqual(ORACLE["ROW_K"]["TOTAL"]["world_invariant_non_degenerate"],
                         self.rk["BR-2"]["non_degenerate_total"])
        self.assertEqual(ORACLE["ROW_K"]["TOTAL"]["inputs"],
                         self.rk["BR-2"]["inputs_total"])
        for name in ("SIGMA_REAL", "SIGMA_REAL2", "SIGMA_REAL3"):
            self.assertEqual(
                ORACLE["ROW_K"][name]["fitted_law_positive_control_non_degenerate"],
                self.rk["populations"][name][
                    "HB1_fitted_law_positive_control_non_degenerate"], name)

    def test_the_counter_can_count(self):
        for name, v in self.rk["hostiles"]["HB1_positive_control"].items():
            self.assertTrue(v["counter_can_count"], name)
            self.assertGreater(v["non_degenerate"], 0, name)

    def test_counter_reproduces_the_parents_published_numbers(self):
        got = self.rk["hostiles"]["HB1b_counter_validation"]
        for name, expected in PARENT_PUBLISHED.items():
            self.assertEqual(got[name]["non_degenerate"], expected, name)

    def test_widening_the_bridge_cannot_raise_the_census(self):
        for name, v in self.rk["hostiles"]["HB2_widened_to_CB_MAX"].items():
            self.assertTrue(v["detected_no_rise"], name)
            self.assertEqual(v["non_degenerate"], 0, name)

    def test_counting_degenerate_points_raises_the_census(self):
        for name, v in self.rk["hostiles"]["HB3_degenerate_counted"].items():
            self.assertTrue(v["detected"], name)
            self.assertGreater(v["points"], 0, name)

    def test_resolution_curve_starts_at_zero_and_is_order_dependent(self):
        rc = self.rk["resolution_curve"]
        for order in rc["orders"].values():
            self.assertEqual(order["curve"]["0"], 0)
        self.assertTrue(rc["order_dependent"])

    def test_br3_states_the_conditioning_without_claiming_a_defect(self):
        br3 = self.rk["BR-3"]
        self.assertEqual(br3["truthful_systems"], 73)
        self.assertEqual(br3["real_systems"], 96)
        self.assertFalse(br3["claims_defect_in_F"])

    def test_live_sub_census_on_one_population(self):
        """Not receipt-trusted: recompute the census for SIGMA_REAL here."""
        hu, hv2, hv3, hv4, parent = A.load_k_parents()
        spec = hu.sigma_real()
        cen = A.census_for(hu, parent, spec, hu.REAL_MACHINES, hu.MU_REAL,
                           hu.real_solved_law, "CB-PROTO", 0, 3)
        self.assertEqual(cen["point_non_degenerate"], 0)
        self.assertEqual(cen["inputs"], 51840)


class RowLFuturity(unittest.TestCase):

    def setUp(self):
        self.rl = RESULT["ROW_L"]

    def test_criterion_has_recall(self):
        self.assertTrue(self.rl["FC-1"]["recall_ok"])

    def test_criterion_has_the_no_alarm_case(self):
        self.assertTrue(self.rl["FC-1"]["no_alarm_ok"])
        self.assertTrue(self.rl["FC-1"]["all_fixtures_agree"])

    def test_clause_logic_recomputed_here(self):
        t = 1000
        self.assertTrue(A.ffa1({"dated": True, "timestamp_epoch": t + 1,
                                "exogenous": True,
                                "independently_attested": True}, t)[0])
        for bad in ({"dated": False, "timestamp_epoch": t + 1, "exogenous": True,
                     "independently_attested": True},
                    {"dated": True, "timestamp_epoch": t - 1, "exogenous": True,
                     "independently_attested": True},
                    {"dated": True, "timestamp_epoch": t + 1, "exogenous": False,
                     "independently_attested": True},
                    {"dated": True, "timestamp_epoch": t + 1, "exogenous": True,
                     "independently_attested": False}):
            self.assertFalse(A.ffa1(bad, t)[0], bad)

    def test_no_in_session_candidate_is_admissible(self):
        self.assertEqual(self.rl["FC-2"]["admissible_candidates"], 0)
        self.assertGreater(self.rl["FC-2"]["candidates_checked"], 0)
        self.assertFalse(self.rl["FC-2"]["row_closes"])
        self.assertEqual(RESULT["DISPOSITION"]["ROW_L"], "OPEN")

    def test_the_absence_has_a_second_independent_route(self):
        second = self.rl["FC-2"]["second_route_to_the_absence"]
        self.assertTrue(second["no_exogenous_candidate_in_repository"])
        self.assertGreater(second["tracked_paths_at_head"], 0)
        self.assertEqual(second["exogenous_candidates_in_repository"], 0)
        self.assertEqual(second["endogenous_by_clause_3"],
                         second["tracked_paths_at_head"])
        self.assertEqual(ORACLE["ROW_L"]["admissible_candidates"], 0)

    def test_the_second_route_is_stable_while_main_moves(self):
        """It must not depend on which commits landed after the freeze."""
        second = self.rl["FC-2"]["second_route_to_the_absence"]
        self.assertNotIn("no_exogenous_posterior_blob", second)
        self.assertIn("informational", " ".join(second.keys()))

    def test_out_of_sample_is_not_accepted_as_future(self):
        """A repo blob is out-of-sample for a later prediction but is not future."""
        for c in self.rl["FC-2"]["candidates"]:
            if c["kind"] == "repo_blob":
                self.assertFalse(c["clauses"]["c3_exogenous"], c["id"])
                self.assertFalse(c["admissible"], c["id"])


class CustodyAndScope(unittest.TestCase):

    def test_no_markdown_of_this_package_carries_the_audited_term(self):
        rx = re.compile(A.ROW_A_PATTERN, re.IGNORECASE)
        found = []
        for fn in sorted(os.listdir(HERE)):
            if fn.endswith(".md"):
                with open(os.path.join(HERE, fn), "rb") as fh:
                    if rx.search(fh.read().decode("utf-8", "replace")):
                        found.append(fn)
        self.assertEqual(found, [])

    def test_frozen_row_texts_are_byte_identical_to_the_reconciliation(self):
        left = sorted(r["row"] for r in RECON["rows_deliberately_left_open"])
        frozen = sorted(ROWS["rows"][k]["old"] for k in ROWS["rows"])
        self.assertEqual(left, frozen)

    def test_the_reconciliation_closes_no_row(self):
        self.assertEqual(RECON["replacements"], [])
        self.assertEqual(RECON["schema"], "GMI_ISSUE_RECONCILIATION_V2")
        self.assertEqual(RECON["issue"], 833)

    def test_no_section_m_row_is_touched(self):
        """Another lane's row text must not appear anywhere in this artifact."""
        import hashlib
        blob = json.dumps(RECON)
        for key in ("ROW_M1", "ROW_M2", "ROW_M3"):
            self.assertNotIn(ROWS["out_of_scope_rows"][key], blob, key)
        self.assertNotIn("#927", blob)
        listed = dict((r["row_id"], r["row_sha256"])
                      for r in RECON["rows_not_in_scope"])
        for key in ("ROW_M1", "ROW_M2", "ROW_M3"):
            self.assertEqual(
                listed[key],
                hashlib.sha256(
                    ROWS["out_of_scope_rows"][key].encode("utf-8")).hexdigest(), key)

    def test_freeze_order_gate_passes(self):
        spec = importlib.util.spec_from_file_location(
            "freeze_order_check", os.path.join(HERE, "check_freeze_order_v1.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertEqual(mod.check(REPO), [])

    def test_every_result_id_appears_in_the_theorem_note(self):
        text = open(os.path.join(HERE, "BODY_RESIDUAL_AKL_THEOREMS_V1.md")).read()
        for rid in ("RA-1", "RA-2", "RA-3", "BR-1", "BR-2", "BR-3", "FC-1", "FC-2"):
            self.assertIn(rid, text, rid)

    def test_manifest_pins_every_parent_it_uses(self):
        man = json.load(open(os.path.join(HERE, "MANIFEST_V1.json")))
        self.assertEqual(man["source_main"], A.SOURCE_MAIN)
        self.assertEqual(man["freeze_commit"], A.FREEZE_COMMIT)
        self.assertGreater(len(man["parents"]), 3)
        for parent in man["parents"]:
            self.assertTrue(os.path.exists(os.path.join(REPO, parent["path"])),
                            parent["path"])
            self.assertEqual(A.git_blob_sha1(
                open(os.path.join(REPO, parent["path"]), "rb").read()),
                parent["blob_sha"], parent["path"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
