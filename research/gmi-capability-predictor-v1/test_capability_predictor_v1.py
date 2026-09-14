"""10 exact controls for the capability predictor contract skeleton (602 F4).

Structural only: sibling source compiled explicitly (no absolute import,
-I safe). Asserts PASS on frozen CONTRACT_V1.json + SCHEMA_V1.json.
Toy remints exercised inside the validator itself. No sampling,
no network, CPython 3.8 safe.
"""

from pathlib import Path
import importlib.util
import json
import unittest

path = Path(__file__).with_name("capability_predictor_v1.py")
spec = importlib.util.spec_from_loader("capability_predictor_checked", loader=None)
mod = importlib.util.module_from_spec(spec)
mod.__file__ = str(path)
exec(compile(path.read_bytes(), str(path), "exec"), mod.__dict__)


class SchemaAndContract(unittest.TestCase):
    def test_schema_passes(self):
        s = mod.load_schema()
        out = mod.validate_schema(s)
        self.assertEqual(out["status"], "PASS")
        self.assertEqual(out["descriptor_fields"], 8)

    def test_contract_passes(self):
        c = mod.load_contract()
        out = mod.validate_contract(c)
        self.assertEqual(out["status"], "PASS")
        self.assertEqual(out["descriptor_fields"], 8)

    def test_claim_ceiling_is_g1(self):
        c = mod.load_contract()
        self.assertEqual(c["claim_ceiling"], "G1")
        self.assertEqual(c["claim_ceiling_intended"], "G6")

    def test_run_combined(self):
        out = mod.run()
        self.assertEqual(out["status"], "PASS")
        self.assertEqual(out["contract"]["status"], "PASS")
        self.assertEqual(out["schema"]["status"], "PASS")
        self.assertEqual(out["remint_toy"]["status"], "PASS")


class InterfaceAndFreeze(unittest.TestCase):
    def test_abstention_gate_has_triggers(self):
        c = mod.load_contract()
        fc = c["predictor_interface"]["abstention_gate"]["firing_condition"]
        low = fc.lower()
        for needle in ("out-of-support", "underspec", "non-identif", "parent", "remint"):
            self.assertIn(needle.lower(), low, msg="missing trigger %r" % needle)

    def test_no_brand_labels_in_descriptor(self):
        c = mod.load_contract()
        for field, entry in c["descriptor_schema"]["fields_detail"].items():
            hit = mod._contains_brand(entry["definition"])
            self.assertIsNone(hit, msg="brand label %r found in %r" % (hit, field))

    def test_freeze_rule_mentions_per_family_and_bijection(self):
        c = mod.load_contract()
        fr = c["freeze_rule"]
        self.assertIn("before", fr["rule"].lower())
        self.assertIn("held", fr["rule"].lower())
        self.assertTrue("per family" in fr["per_family"].lower()
                        or "per-family" in fr["per_family"].lower())
        self.assertTrue("bijection" in fr["remint"].lower()
                        or "bijective" in fr["remint"].lower())

    def test_loss_is_proper_on_held_only(self):
        c = mod.load_contract()
        loss = c["predictor_interface"]["loss"]
        self.assertIn("proper", loss["primary"].lower())
        self.assertIn("held", loss["scope"].lower())

    def test_resource_order_parent(self):
        c = mod.load_contract()
        parent = c["descriptor_schema"]["fields_detail"]["resource_profile"]["strongest_parent"]
        self.assertGreaterEqual(len(parent), 20)
        self.assertTrue(any(k in parent.lower() for k in
                            ("blackwell", "bounded", "landauer", "resource-rational")))

    def test_toy_remints(self):
        out = mod.check_toy_remints()
        self.assertEqual(out["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
