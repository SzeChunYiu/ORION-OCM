"""Hostile tests for the K4 substitution per-cell audit (items 22/23/35-a)."""

from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import cell_audit_v1 as audit  # noqa: E402

INPUT = json.loads((HERE / "AUDIT_INPUT_V1.json").read_text())


class TestSubstitutionCellAudit(unittest.TestCase):
    def test_input_has_exactly_159_theory_red_cells(self):
        self.assertEqual(INPUT["schema"], "GMIK4SubstitutionCellAuditInputV1")
        self.assertEqual(INPUT["n_theory_red"], 159)
        self.assertEqual(len(INPUT["cells"]), 159)
        self.assertTrue(all(c["verdict"] == "THEORY_RED" for c in INPUT["cells"]))
        self.assertTrue(all(c["status"] == "OK" for c in INPUT["cells"]))

    def test_frozen_pins_match_bytes_on_disk(self):
        pins = audit.assert_frozen_untouched()
        for name, row in pins.items():
            self.assertTrue(row["ok"], msg="%s pin drifted" % name)

    def test_audit_partitions_159_without_rewriting_verdicts(self):
        receipt = audit.run_audit(INPUT)
        self.assertEqual(receipt["schema"], audit.SCHEMA)
        self.assertEqual(receipt["summary"]["n_cells"], 159)
        yes = receipt["summary"]["targets_substitution_yes"]
        no = receipt["summary"]["targets_substitution_no"]
        self.assertEqual(yes + no, 159)
        self.assertGreater(yes, 0)
        self.assertGreater(no, 0)
        self.assertFalse(receipt["frozen_verdicts_rewritten"])
        self.assertFalse(receipt["frozen_model_mutated"])
        self.assertFalse(receipt["claim_ceiling"]["frozen_verdicts_rewritten"])
        self.assertEqual(receipt["claim_ceiling"]["reachable"][:9], "Does NOT ")
        self.assertIn("admissibly", receipt["claim_ceiling"]["admissible"].lower())
        self.assertEqual(receipt["cells"][0]["claim_label"], "admissible")
        for cell in receipt["cells"]:
            self.assertEqual(cell["frozen_verdict"], "THEORY_RED")
            self.assertFalse(cell["frozen_verdict_rewritten"])
            self.assertEqual(cell["claim_label"], "admissible")
            self.assertIsInstance(cell["targets_substitution"], bool)
            self.assertTrue(cell["reason"])

    def test_retrieval_families_are_yes(self):
        vectors = INPUT["family_property_vectors"]
        for fam, pv in vectors.items():
            if pv.get("retrieval", "none") != "none":
                cls = audit.classify_property_vector(pv)
                self.assertTrue(
                    cls["targets_substitution"],
                    msg="%s has retrieval=%r but classified no" % (fam, pv.get("retrieval")),
                )
                self.assertIn("retention_caching", cls["substitution_kinds"])

    def test_equal_scale_no_retrieval_families_are_no(self):
        vectors = INPUT["family_property_vectors"]
        for fam, pv in vectors.items():
            if (
                pv.get("retrieval", "none") == "none"
                and pv.get("state_scales_with") == pv.get("serve_scales_with")
                and not pv.get("external_authority")
                and "latent" not in str(pv.get("state_scales_with", ""))
                and "window" not in str(pv.get("serve_scales_with", ""))
            ):
                cls = audit.classify_property_vector(pv)
                self.assertFalse(
                    cls["targets_substitution"],
                    msg="%s should be non-substitution but got yes (%s)"
                    % (fam, cls["reason"]),
                )

    def test_amortisation_detects_recurrent_and_cnn_scales(self):
        yes = audit.classify_property_vector(
            {
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
        )
        self.assertTrue(yes["targets_substitution"])
        self.assertIn("amortisation", yes["substitution_kinds"])

        cnn = audit.classify_property_vector(
            {
                "external_authority": False,
                "retrieval": "none",
                "routing": "none",
                "serve_iterations": "one",
                "serve_scales_with": "kernel_size_times_positions",
                "sharing": "shared",
                "state_scales_with": "kernel_size",
                "stochastic_serve": False,
                "update_locality": "global",
                "verifier_gated": False,
            }
        )
        self.assertTrue(cnn["targets_substitution"])
        self.assertIn("parameter_sharing", cnn["substitution_kinds"])

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

    def test_family_constant_classification(self):
        receipt = audit.run_audit(INPUT)
        by_fam = {}
        for cell in receipt["cells"]:
            by_fam.setdefault(cell["family"], set()).add(cell["targets_substitution"])
        for fam, vals in by_fam.items():
            self.assertEqual(len(vals), 1, msg="%s mixed yes/no across cells" % fam)

    def test_receipt_sha_of_input_is_stable(self):
        receipt = audit.run_audit(INPUT)
        expected = hashlib.sha256((HERE / "AUDIT_INPUT_V1.json").read_bytes()).hexdigest()
        self.assertEqual(receipt["source_input"]["sha256"], expected)

    def test_main_writes_receipt_with_counts(self):
        out = HERE / "_TEST_RECEIPT.json"
        try:
            rc = audit.main([str(out)])
            self.assertEqual(rc, 0)
            written = json.loads(out.read_text())
            self.assertEqual(written["summary"]["n_cells"], 159)
            self.assertEqual(
                written["summary"]["targets_substitution_yes"]
                + written["summary"]["targets_substitution_no"],
                159,
            )
        finally:
            if out.exists():
                out.unlink()

    def test_claim_ceiling_labels_admissible_not_reachable(self):
        receipt = audit.run_audit(INPUT)
        ceiling = receipt["claim_ceiling"]
        self.assertIn("INCONCLUSIVE_GRAMMAR", ceiling["admissible"])
        self.assertIn("clause (c)", ceiling["reachable"].lower().replace("(", "("))
        # Hostile: reachable text must refuse green claims.
        low = ceiling["reachable"].lower()
        self.assertIn("does not claim", low)
        self.assertNotIn("cells are green", low)

    def test_optimized_mode_assertions_still_fire(self):
        # Under python -O assert statements are stripped; pin check uses raise.
        with self.assertRaises(AssertionError):
            bad = dict(audit.FROZEN_PINS)
            # Temporarily break one pin via a local monkeypatch path check.
            original = audit.FROZEN_PINS["gmi_k4_resource_native_v4.py"]
            try:
                audit.FROZEN_PINS["gmi_k4_resource_native_v4.py"] = "0" * 64
                audit.assert_frozen_untouched()
            finally:
                audit.FROZEN_PINS["gmi_k4_resource_native_v4.py"] = original
                _ = bad  # silence lint


if __name__ == "__main__":
    unittest.main(verbosity=2)
