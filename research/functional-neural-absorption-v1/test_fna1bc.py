"""Tests for the engineered response to FNA-1's negative (FNA-1b, hostile v2, FNA-1c)."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "src"))

import experiment as E     # noqa: E402
import fna1b as B          # noqa: E402
import hostile_v2 as H2    # noqa: E402

B1 = json.loads((HERE / "FNA1B_METAPATH_V1.json").read_text())
H2R = json.loads((HERE / "FNA1B_HOSTILE_V2.json").read_text())
C1 = json.loads((HERE / "FNA1C_CHARGED_V1.json").read_text())


class PolicyIsNotAnOracle(unittest.TestCase):
    def test_the_policy_never_reads_the_decisive_atom(self):
        src = (HERE / "fna1b.py").read_text()
        body = src[src.index("def metapath_order"):src.index("def run(")]
        self.assertNotIn("DECISIVE", body)
        self.assertNotIn("decisive", body)

    def test_every_world_has_several_target_type_atoms(self):
        """Type must NARROW, never IDENTIFY. A unique target-type atom is an oracle."""
        for kind, n in B1["verdict"]["target_type_atom_counts"].items():
            self.assertGreater(n, 1, f"{kind}: type would identify the answer")

    def test_the_policy_is_defeated_by_the_signal_it_reads(self):
        """The load-bearing falsifier: being misleadable is the evidence of non-oracle."""
        self.assertTrue(H2R["verdict"]["falsifier_discriminates"])
        self.assertTrue(H2R["metapath_WORSE_than_naive"])


class V1DidNotDiscriminate(unittest.TestCase):
    """The first hostile failed, and that failure is retained, not overwritten."""

    def test_fna1b_returned_cannot_check_rather_than_banking_two_wins(self):
        self.assertEqual(B1["verdict"]["terminal"],
                         "CANNOT_CHECK_TYPE_DECOY_DID_NOT_DISCRIMINATE")
        self.assertFalse(B1["verdict"]["type_decoy_defeated_the_policy"])

    def test_the_confirmed_prediction_is_still_recorded(self):
        self.assertEqual(B1["verdict"]["worlds_where_metapath_beats_rarity"],
                         ["COMMON_DECISIVE", "RARE_DECOY"])

    def test_v2_declares_it_sharpened_the_falsifier_not_the_policy(self):
        self.assertEqual(H2R["analysis_status"],
                         "SHARPENED_FALSIFIER_AFTER_V1_DID_NOT_DISCRIMINATE")
        self.assertIn("cannot strengthen the policy", H2R["authority"])
        self.assertIn("retained", H2R["supersedes_note"])

    def test_the_sharpened_world_makes_the_answer_reachable_first_by_a_naive_order(self):
        ks = H2.type_decoy_sharp()
        self.assertEqual(ks.hyperedges[0].edge_id, "e_decisive")
        self.assertEqual(H2R["world"]["decisive_channel"], "DEPENDENCE")
        self.assertEqual(H2R["world"]["metapath_order"][0], B.DECOY_CHANNEL)


class ChargedAccounting(unittest.TestCase):
    def test_the_policy_never_pays_on_a_single_query(self):
        """Repaying a full-edge scan in one query would mean it was not charged."""
        self.assertEqual(C1["verdict"]["worlds_where_metapath_pays_on_a_SINGLE_query"], [])

    def test_single_query_payback_would_be_flagged_as_a_defect_not_a_result(self):
        doc = json.loads(json.dumps(C1))
        doc["worlds"]["RARE_DECISIVE"]["per_query"]["1"]["metapath_pays"] = True
        self.assertEqual(
            __import__("fna1c").verdict(doc)["terminal"],
            "CANNOT_CHECK_SINGLE_QUERY_PAYBACK_IMPLIES_UNCHARGED_PREPARATION")

    def test_preparation_cost_is_the_full_edge_scan(self):
        for kind, prep in C1["verdict"]["preparation_cost"].items():
            self.assertEqual(prep, C1["worlds"][kind]["edges"])

    def test_the_world_that_cannot_repay_has_no_break_even(self):
        self.assertIsNone(C1["verdict"]["break_even_queries"]["TYPE_DECOY"])
        self.assertLess(C1["verdict"]["expansions_saved"]["TYPE_DECOY"], 0)

    def test_break_even_is_ceiling_of_prep_over_saved(self):
        for kind, be in C1["verdict"]["break_even_queries"].items():
            saved = C1["verdict"]["expansions_saved"][kind]
            if be is not None:
                prep = C1["verdict"]["preparation_cost"][kind]
                self.assertEqual(be, -(-prep // saved))

    def test_the_uncharged_term_is_named_not_hidden(self):
        text = C1["verdict"]["what_this_does_not_establish"]
        self.assertIn("maintenance under revocation", text)
        self.assertIn("would be optimistic", text)


class NoOverclaim(unittest.TestCase):
    def test_no_receipt_asserts_a_forbidden_claim(self):
        import contract as C
        for name in ("FNA1B_METAPATH_V1.json", "FNA1B_HOSTILE_V2.json",
                     "FNA1C_CHARGED_V1.json"):
            body = (HERE / name).read_text()
            for claim in C.FORBIDDEN_CLAIMS:
                self.assertNotIn(f'"{claim}"', body, name)

    def test_no_model_or_router_in_any_engineered_module(self):
        for name in ("fna1b.py", "hostile_v2.py", "fna1c.py"):
            body = (HERE / name).read_text().lower()
            for banned in ("import torch", "sklearn", "def train(", "bandit"):
                self.assertNotIn(banned, body, f"{name} contains {banned}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
