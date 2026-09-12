import json
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
MANIFEST = HERE / "MASTER_DERIVED_LAW_MANIFEST_V2.json"


class TestMasterDerivedStackV2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_primitive_tuple_unchanged(self):
        self.assertFalse(self.manifest["primitive_tuple_changed"])

    def test_all_theorems_and_receipts_exist(self):
        for layer in self.manifest["layers"]:
            self.assertTrue((HERE / layer["theorem"]).is_file(), layer["theorem"])
            self.assertTrue((HERE / layer["receipt"]).is_file(), layer["receipt"])

    def test_all_receipt_terminals_match_manifest(self):
        for layer in self.manifest["layers"]:
            receipt = json.loads((HERE / layer["receipt"]).read_text(encoding="utf-8"))
            self.assertTrue(receipt["all_checks_green"], layer["id"])
            self.assertEqual(receipt["terminal"], layer["terminal"], layer["id"])

    def test_dependency_classes_are_nonempty(self):
        for layer in self.manifest["layers"]:
            self.assertTrue(layer["depends_on"], layer["id"])

    def test_negative_boundaries_not_empty(self):
        self.assertGreaterEqual(len(self.manifest["negative_boundaries_preserved"]), 8)


if __name__ == "__main__":
    unittest.main()
