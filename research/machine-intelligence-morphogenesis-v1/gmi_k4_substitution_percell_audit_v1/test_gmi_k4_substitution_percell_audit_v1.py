"""Hostile tests for K4 per-cell audit under repaired pricing (22/23/35-a)."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import gmi_k4_substitution_percell_audit_v1 as audit  # noqa: E402


class TestPercellAudit(unittest.TestCase):
    def test_bundle_has_exactly_159_theory_red(self):
        bundle = audit.load_theory_red_bundle()
        self.assertEqual(bundle["n_theory_red"], 159)
        self.assertEqual(len(bundle["cells"]), 159)
        self.assertTrue(all(c["verdict"] == "THEORY_RED" for c in bundle["cells"]))

    def test_repair_stage_material_trade_control(self):
        info = audit.load_repair_admission()
        self.assertTrue(info["repaired_material_trade"])
        self.assertFalse(info["frozen_material_trade"])

    def test_audit_partitions_159(self):
        receipt = audit.run_audit()
        self.assertEqual(receipt["schema"], audit.SCHEMA)
        self.assertEqual(receipt["summary"]["n_cells"], 159)
        s = receipt["summary"]
        self.assertEqual(
            s["targets_substitution_yes"] + s["targets_substitution_no"], 159
        )
        self.assertEqual(
            s["admits_under_repaired_yes"] + s["admits_under_repaired_no"], 159
        )
        self.assertGreater(s["targets_substitution_yes"], 0)
        self.assertGreater(s["admits_under_repaired_yes"], 0)
        self.assertGreaterEqual(
            s["targets_substitution_yes"], s["admits_under_repaired_yes"]
        )
        self.assertFalse(receipt["frozen_verdicts_rewritten"])
        self.assertFalse(receipt["frozen_model_mutated"])

    def test_retrieval_families_target_yes(self):
        bundle = audit.load_theory_red_bundle()
        for fam, pv in bundle["family_property_vectors"].items():
            if pv.get("retrieval", "none") != "none":
                cls = audit.classify_property_vector(pv)
                self.assertTrue(cls["targets_substitution"], msg=fam)
                self.assertIn("retention_caching", cls["substitution_kinds"])

    def test_latent_only_targets_but_does_not_admit(self):
        cls = audit.classify_property_vector(
            {
                "external_authority": False,
                "retrieval": "none",
                "routing": "none",
                "serve_iterations": "one",
                "serve_scales_with": "decoder_size",
                "sharing": "shared",
                "state_scales_with": "latent_dim_plus_decoder",
                "stochastic_serve": True,
                "update_locality": "global",
                "verifier_gated": False,
            }
        )
        self.assertTrue(cls["targets_substitution"])
        self.assertEqual(cls["substitution_kinds"], ["latent_compression"])
        expressed = audit.repair_expressed_kinds(cls["substitution_kinds"])
        self.assertEqual(expressed, [])

    def test_sparsity_alone_does_not_admit_without_expressed_kind(self):
        cls = audit.classify_property_vector(
            {
                "external_authority": False,
                "retrieval": "none",
                "routing": "none",
                "serve_iterations": "one",
                "serve_scales_with": "n_positions_times_window",
                "sharing": "unshared",
                "state_scales_with": "n_positions_times_window",
                "stochastic_serve": False,
                "update_locality": "global",
                "verifier_gated": False,
            }
        )
        self.assertTrue(cls["targets_substitution"])
        self.assertIn("sparsity_specialisation", cls["substitution_kinds"])
        self.assertEqual(audit.repair_expressed_kinds(cls["substitution_kinds"]), [])

    def test_amortisation_admits_under_repair(self):
        cell = {
            "family": "K4-A07",
            "grammar": "G2_SYMBOLIC_PROGRAM",
            "cell": "w1",
            "verdict": "THEORY_RED",
            "status": "OK",
        }
        vectors = {
            "K4-A07": {
                "external_authority": False,
                "retrieval": "none",
                "routing": "none",
                "serve_iterations": "many",
                "serve_scales_with": "hidden_width_times_length",
                "sharing": "shared",
                "state_scales_with": "hidden_width",
                "stochastic_serve": False,
                "update_locality": "global",
                "verifier_gated": False,
            }
        }
        out = audit.classify_cell(cell, vectors, repair_ok=True)
        self.assertTrue(out["targets_substitution"])
        self.assertTrue(out["admits_substitution_under_repaired_pricing"])
        self.assertIn("amortisation", out["repair_expressed_kinds"])

    def test_verifier_gated_is_not_a_channel_substitution(self):
        cls = audit.classify_property_vector(
            {
                "external_authority": False,
                "retrieval": "none",
                "routing": "none",
                "serve_iterations": "many",
                "serve_scales_with": "n_proposals_times_check",
                "sharing": "shared",
                "state_scales_with": "proposer_plus_verifier",
                "stochastic_serve": True,
                "update_locality": "none",
                "verifier_gated": True,
            }
        )
        self.assertFalse(cls["targets_substitution"])
        self.assertIn("within-serve", cls["reason"])

    def test_family_constant_admission(self):
        receipt = audit.run_audit()
        by_fam = {}
        for cell in receipt["cells"]:
            by_fam.setdefault(cell["family"], set()).add(
                cell["admits_substitution_under_repaired_pricing"]
            )
        for fam, vals in by_fam.items():
            self.assertEqual(len(vals), 1, msg="%s mixed admission" % fam)

    def test_claim_ceiling_parent_subtraction_and_reachable_refusal(self):
        receipt = audit.run_audit()
        ceiling = receipt["claim_ceiling"]
        self.assertIn("INCONCLUSIVE_GRAMMAR", ceiling["admissible"])
        self.assertIn("does not claim", ceiling["reachable"].lower())
        self.assertIn("first refusal", ceiling["parent_subtraction"].lower())
        self.assertIn("NS-1", ceiling["parent_subtraction"])

    def test_main_writes_receipt_and_stage(self):
        out = HERE / "_TEST_RECEIPT.json"
        try:
            rc = audit.main([str(out)])
            self.assertEqual(rc, 0)
            written = json.loads(out.read_text())
            self.assertEqual(written["summary"]["n_cells"], 159)
            stage = json.loads(audit.OUT_STAGE_PATH.read_text())
            self.assertEqual(stage["audit_id"], audit.AUDIT_ID)
            self.assertEqual(stage["summary"]["n_cells"], 159)
        finally:
            if out.exists():
                out.unlink()

    def test_ledger_matches_live_audit(self):
        ledger = json.loads((HERE / "AUDIT_LEDGER_V1.json").read_text())
        receipt = audit.run_audit()
        self.assertEqual(ledger["n_theory_red"], 159)
        self.assertEqual(
            ledger["summary"]["admits_under_repaired_yes"],
            receipt["summary"]["admits_under_repaired_yes"],
        )
        self.assertEqual(
            ledger["summary"]["targets_substitution_yes"],
            receipt["summary"]["targets_substitution_yes"],
        )
        self.assertEqual(
            ledger["summary"]["families_admits_yes"],
            receipt["summary"]["families_admits_yes"],
        )
        self.assertEqual(
            ledger["summary"]["families_targets_yes_admits_no"],
            receipt["summary"]["families_targets_yes_admits_no"],
        )
        self.assertEqual(receipt["summary"]["admits_under_repaired_yes"], 96)
        self.assertEqual(receipt["summary"]["families_targets_yes_admits_no"], ["K4-A22"])

    def test_committed_cells_json_matches_live_audit(self):
        cells_doc = json.loads(
            (HERE / "STAGE_K4_SUBSTITUTION_PERCELL_AUDIT_V1.json").read_text()
        )
        self.assertEqual(cells_doc["n_cells"], 159)
        self.assertEqual(len(cells_doc["cells"]), 159)
        receipt = audit.run_audit()
        live = {
            (c["family"], c["grammar"], c["cell"]): (
                c["targets_substitution"],
                c["admits_substitution_under_repaired_pricing"],
                c["primary_kind"],
            )
            for c in receipt["cells"]
        }
        for row in cells_doc["cells"]:
            key = (row["family"], row["grammar"], row["cell"])
            self.assertIn(key, live)
            self.assertEqual(
                live[key],
                (
                    row["targets_substitution"],
                    row["admits_substitution_under_repaired_pricing"],
                    row["primary_kind"],
                ),
                msg=str(key),
            )
        self.assertEqual(len(live), 159)

    def test_repair_ok_false_admits_nothing(self):
        bundle = audit.load_theory_red_bundle()
        cells = [
            audit.classify_cell(c, bundle["family_property_vectors"], repair_ok=False)
            for c in bundle["cells"]
        ]
        self.assertTrue(any(c["targets_substitution"] for c in cells))
        self.assertFalse(
            any(c["admits_substitution_under_repaired_pricing"] for c in cells)
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
