"""15 exact controls for the capability contract (A4).

Covers: contract/schema loading, row count, id set, field presence and
thin-column floors, twin/parent/falsifier/atlas completeness, scope,
and interface refusal. Sibling source compiled explicitly; -I safe.
"""

from pathlib import Path
import importlib.util
import json
import unittest

path = Path(__file__).with_name("capability_contract_v1.py")
spec = importlib.util.spec_from_loader("capability_checked", loader=None)
mod = importlib.util.module_from_spec(spec)
mod.__file__ = str(path)
exec(compile(path.read_bytes(), str(path), "exec"), mod.__dict__)


class ContractShape(unittest.TestCase):
    def test_loads_and_counts(self):
        data = mod.load_contract()
        self.assertEqual(len(data["rows"]), 27)
        self.assertEqual(data["schema"], "CapabilityContractV1")

    def test_expected_ids_exact(self):
        data = mod.load_contract()
        ids = {r["id"] for r in data["rows"]}
        self.assertEqual(ids, set(mod.EXPECTED_IDS))

    def test_validate_contract_pass(self):
        result = mod.validate_contract()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["rows"], 27)

    def test_validate_schema_pass(self):
        result = mod.validate_schema()
        self.assertEqual(result["status"], "PASS")
        self.assertGreaterEqual(result["schema_fields"], 11)

    def test_scope_present(self):
        data = mod.load_contract()
        self.assertGreaterEqual(len(data["scope"]), 20)
        self.assertIn("Admissibility", data["scope"])

    def test_json_round_trips(self):
        data = mod.load_contract()
        text = json.dumps(data)
        reloaded = json.loads(text)
        self.assertEqual(reloaded["rows"][0]["id"], data["rows"][0]["id"])


class FieldFloors(unittest.TestCase):
    def test_no_thin_inputs(self):
        data = mod.load_contract()
        for row in data["rows"]:
            for col in ("inputs", "allowed_info", "required_behaviour",
                        "success_metric", "resource_metric"):
                self.assertGreaterEqual(len(row[col]), 15,
                                        msg="%s %s too short" % (row["id"], col))

    def test_no_thin_twin_parent_falsifier(self):
        data = mod.load_contract()
        for row in data["rows"]:
            for col in ("negative_twin", "strongest_parent", "falsifier", "atlas_reduction"):
                self.assertGreaterEqual(len(row[col].strip()), 10,
                                        msg="%s %s too short" % (row["id"], col))

    def test_each_row_has_all_required_fields(self):
        data = mod.load_contract()
        for row in data["rows"]:
            for field in mod.REQUIRED_FIELDS:
                self.assertIn(field, row)
                self.assertTrue(row[field].strip())

    def test_twin_parent_falsifier_completeness(self):
        result = mod.check_twin_parent_falsifier_present()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["checked"], 27)

    def test_run_aggregates_all(self):
        result = mod.run()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["contract"]["rows"], 27)


class AtlasAndParents(unittest.TestCase):
    def test_every_row_cites_atlas(self):
        data = mod.load_contract()
        for row in data["rows"]:
            self.assertTrue(row["atlas_reduction"].strip())
            self.assertGreaterEqual(len(row["atlas_reduction"].strip()), 15,
                                    msg=row["id"] + " atlas_reduction too short")

    def test_every_row_has_parent(self):
        data = mod.load_contract()
        for row in data["rows"]:
            self.assertGreaterEqual(len(row["strongest_parent"]), 10)

    def test_interfaces_refuse_bad_inputs(self):
        with self.assertRaises(ValueError):
            mod.validate_contract({"schema": "Wrong", "rows": []})
        with self.assertRaises(ValueError):
            mod.validate_contract({"schema": "CapabilityContractV1", "rows": []})
        with self.assertRaises(ValueError):
            mod.validate_contract({
                "schema": "CapabilityContractV1",
                "scope": "short",
                "rows": [{"id": "cap-perception"}]
            })

    def test_schema_json_valid(self):
        raw = (Path(__file__).with_name("SCHEMA_V1.json")).read_bytes()
        data = json.loads(raw)
        self.assertEqual(data["title"], "CapabilityContractV1")


if __name__ == "__main__":
    unittest.main()
