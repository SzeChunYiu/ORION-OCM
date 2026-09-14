"""15 exact controls for the ecology extension contract (A2). Sibling-compiled; -I safe."""

from pathlib import Path
import importlib.util
import json
import unittest

path = Path(__file__).with_name("ecology_extension_v1.py")
spec = importlib.util.spec_from_loader("ecology_checked", loader=None)
mod = importlib.util.module_from_spec(spec)
mod.__file__ = str(path)
exec(compile(path.read_bytes(), str(path), "exec"), mod.__dict__)


class ContractShape(unittest.TestCase):
    def test_loads_and_counts(self):
        data = mod.load_contract()
        self.assertEqual(len(data["coordinates"]), 15)
        self.assertEqual(data["schema"], "EcologyExtensionContractV1")

    def test_expected_coords_exact(self):
        data = mod.load_contract()
        self.assertEqual(set(data["coordinates"].keys()), set(mod.REQUIRED_COORDS))

    def test_validate_contract_pass(self):
        result = mod.validate_contract()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["coords"], 15)

    def test_validate_schema_pass(self):
        result = mod.validate_schema()
        self.assertEqual(result["status"], "PASS")
        self.assertGreaterEqual(result["schema_coords"], 15)

    def test_scope_and_extends(self):
        data = mod.load_contract()
        self.assertGreaterEqual(len(data["scope"]), 20)
        self.assertGreaterEqual(len(data["extends"]), 2)
        self.assertTrue(any("ECOLOGY_CONTRACT" in e for e in data["extends"]))

    def test_json_round_trips(self):
        data = mod.load_contract()
        text = json.dumps(data)
        reloaded = json.loads(text)
        self.assertEqual(reloaded["coordinates"]["other_agents"]["values"],
                         data["coordinates"]["other_agents"]["values"])


class FieldFloors(unittest.TestCase):
    def test_no_thin_definitions(self):
        data = mod.load_contract()
        for name, entry in data["coordinates"].items():
            self.assertGreaterEqual(len(entry["definition"]), 20, msg=name)
            self.assertGreaterEqual(len(entry["parent"]), 10, msg=name)
            self.assertGreaterEqual(len(entry["falsifier"]), 20, msg=name)

    def test_other_agents_values_include_required(self):
        data = mod.load_contract()
        vals = data["coordinates"]["other_agents"]["values"]
        self.assertIn("NONE", vals)
        self.assertIn("ADAPTIVE_OPPONENTS", vals)
        self.assertGreaterEqual(len(vals), 2)

    def test_equivalence_booleans_true(self):
        data = mod.load_contract()
        eq = data["equivalence_remint_rules"]
        self.assertTrue(eq["remint_is_bijection"])
        self.assertTrue(eq["label_leakage_forbidden"])
        self.assertGreaterEqual(len(eq["definition"]), 20)
        self.assertGreaterEqual(len(eq["falsifier"]), 20)

    def test_run_aggregates_all(self):
        result = mod.run()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["contract"]["coords"], 15)


class RemintAndRefusal(unittest.TestCase):
    def test_is_bijection_true_cases(self):
        self.assertTrue(mod.is_bijection({0: 0, 1: 1, 2: 2}, 3))
        self.assertTrue(mod.is_bijection({0: 2, 1: 0, 2: 1}, 3))

    def test_is_bijection_false_cases(self):
        self.assertFalse(mod.is_bijection({0: 0, 1: 0, 2: 2}, 3))
        self.assertFalse(mod.is_bijection({0: 0, 1: 0, 2: 1}, 3))
        self.assertFalse(mod.is_bijection({0: 0, 1: 1}, 3))

    def test_toy_remints(self):
        result = mod.check_toy_remints()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["toy_checks"], 4)

    def test_interfaces_refuse_bad_inputs(self):
        with self.assertRaises(ValueError):
            mod.validate_contract({"schema": "Wrong", "coordinates": {}, "extends": [], "scope": "x", "equivalence_remint_rules": {}})
        with self.assertRaises(ValueError):
            mod.validate_contract({"schema": "EcologyExtensionContractV1", "scope": "short", "extends": ["a"], "coordinates": {}, "equivalence_remint_rules": {"definition": "x", "parent": "x", "falsifier": "x", "remint_is_bijection": True, "label_leakage_forbidden": True}})

    def test_schema_json_valid(self):
        raw = (Path(__file__).with_name("SCHEMA_V1.json")).read_bytes()
        data = json.loads(raw)
        self.assertEqual(data["title"], "EcologyExtensionContractV1")


if __name__ == "__main__":
    unittest.main()
