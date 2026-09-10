"""G5.3 warrant-adoption protocol. Loads experiment by file location."""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SRC = REPO / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _load_experiment():
    path = HERE / "experiment.py"
    spec = importlib.util.spec_from_file_location("g5_warrant_adoption_v1_experiment", path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["g5_warrant_adoption_v1_experiment"] = mod
    spec.loader.exec_module(mod)
    return mod


E = _load_experiment()
HONEST = {
    "PRODUCTION_WARRANT_UNCHANGED",
    "DATABASE_PARENT_SUFFICIENT",
    "PARENT_SUFFICIENT",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TestImportIsolation(unittest.TestCase):
    def test_experiment_loaded_from_this_capsule_not_packed_field(self):
        self.assertEqual(Path(E.__file__).resolve(), HERE / "experiment.py")
        self.assertIn("g5-warrant-adoption-v1", str(E.__file__))
        self.assertNotIn("g5-packed-field", str(E.__file__))
        packed = REPO / "research" / "g5-packed-field-v1" / "experiment.py"
        self.assertTrue(packed.is_file())
        self.assertNotEqual(_sha256(HERE / "experiment.py"), _sha256(packed))
        source = (HERE / "experiment.py").read_text()
        self.assertIn("spec_from_file_location", source)
        self.assertIn("g5_factored_warrant_v1", source)
        self.assertIn("g5_bdd_warrant_v2", source)
        self.assertIn("g5_zdd_warrant_v3", source)
        self.assertNotIn("sys.path.insert(0, str(PRED", source)

    def test_tests_do_not_import_bare_experiment(self):
        tree = ast.parse((HERE / "test_protocol.py").read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = {alias.name.split(".")[0] for alias in node.names}
                self.assertNotIn("experiment", names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                self.assertFalse(node.module.startswith("experiment"))

    def test_stdlib_only_no_bdd_package(self):
        text = (HERE / "experiment.py").read_text()
        for banned in ("import dd", "from dd", "import cudd", "import pyeda", "from pyeda", "numpy", "sklearn"):
            self.assertNotIn(banned, text)


class TestPredecessorsFrozen(unittest.TestCase):
    def test_cited_terminals_and_hashes_match_disk(self):
        cited = E.predecessor_citations()
        v1 = REPO / "research" / "g5-factored-warrant-v1" / "RESULT.json"
        v2 = REPO / "research" / "g5-bdd-warrant-v2" / "RESULT.json"
        v3 = REPO / "research" / "g5-zdd-warrant-v3" / "RESULT.json"
        self.assertEqual(cited["g5-factored-warrant-v1"]["terminal"], "FACTORED_WARRANT_VALUE_SUPPORTED")
        self.assertEqual(cited["g5-bdd-warrant-v2"]["terminal"], "BDD_PARENT_N3_PARITY_SUPPORTED")
        self.assertEqual(cited["g5-zdd-warrant-v3"]["terminal"], "ZDD_PARENT_N3_PARITY_SUPPORTED")
        self.assertEqual(cited["g5-factored-warrant-v1"]["sha256"], _sha256(v1))
        self.assertEqual(cited["g5-bdd-warrant-v2"]["sha256"], _sha256(v2))
        self.assertEqual(cited["g5-zdd-warrant-v3"]["sha256"], _sha256(v3))
        self.assertIn("FACTORED_WARRANT_VALUE_SUPPORTED", v1.read_text())
        self.assertIn("BDD_PARENT_N3_PARITY_SUPPORTED", v2.read_text())
        self.assertIn('"zdd_parent": "OPEN"', v2.read_text())
        self.assertIn("ZDD_PARENT_N3_PARITY_SUPPORTED", v3.read_text())
        self.assertIn('"G5.3/008": "NOT_ADOPTED"', v3.read_text())
        g51 = json.loads((REPO / "research" / "g5-physical-denominator-v1" / "SUMMARY.json").read_text())
        self.assertEqual(g51["execution_terminal"], "DATABASE_PARENT_SUFFICIENT")


class TestProductionUnchanged(unittest.TestCase):
    def test_production_warrant_is_antichain_oracle(self):
        from ocm.kso import warrant as W

        self.assertTrue(hasattr(W, "WarrantProfile"))
        self.assertNotEqual(Path(W.__file__).resolve(), Path(__file__).resolve())
        text = Path(W.__file__).read_text()
        self.assertNotIn("zdd_warrant", text)
        self.assertNotIn("bdd_warrant", text)
        self.assertNotIn("factored_warrant", text)
        self.assertIn("antichain", W.__doc__.lower())
        self.assertIn("g5-warrant-adoption", str(HERE))


class TestEconomicsProtocol(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.live_path = Path(cls.tmp.name) / "RESULT.json"
        cls.live = E.main(cls.live_path)
        cls.frozen_path = HERE / "RESULT.json"
        cls.frozen = json.loads(cls.frozen_path.read_text()) if cls.frozen_path.is_file() else None

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_parent_sufficient_class_is_not_failure(self):
        self.assertIn(self.live["terminal"], HONEST | {"CANNOT_CHECK_PARITY_FAILED"})
        if self.live["terminal"] in HONEST:
            self.assertTrue(self.live["parent_sufficient_is_not_failure"])
        self.assertFalse(self.live["programme_tick"])
        self.assertFalse(self.live["production_adoption"])
        self.assertFalse(self.live["production_warrant_switched"])
        self.assertFalse(self.live["physical_denominator_clean"])
        self.assertFalse(self.live["dollars"])
        self.assertFalse(self.live["coordinates_scalarized"])
        self.assertNotIn("PHYSICAL_DENOMINATOR_CLEAN", self.live["terminal"])
        self.assertIn("PHYSICAL_DENOMINATOR_CLEAN", self.live["not_issued"])

    def test_four_coordinates_charged_separately(self):
        coords = ["construction_ns", "query_ns", "revocation_ns", "bytes"]
        self.assertGreaterEqual(len(self.live["rows"]), 4)
        for row in self.live["rows"]:
            self.assertEqual(row["coordinates"], coords)
            self.assertFalse(row["coordinates_scalarized"])
            for name, parent in row["parents"].items():
                for c in coords:
                    self.assertIn(c, parent, msg=name)
                    self.assertIsInstance(parent[c], int)
                    self.assertGreaterEqual(parent[c], 0)
            anti = row["parents"]["antichain-oracle"]
            self.assertFalse(anti["conversion_from_antichain"])
            self.assertTrue(anti["expand_is_identity"])
            for name in ("support-DAG-hashcons", "research-ROBDD", "research-ZDD"):
                self.assertTrue(row["parents"][name]["conversion_from_antichain"])
                self.assertFalse(row["parents"][name]["expand_is_identity"])

    def test_n3_parity_holds_and_economics_do_not_switch_src(self):
        self.assertTrue(self.live["n3_parity"]["parity"])
        self.assertEqual(self.live["n3_parity"]["n3_legal_intervals"], 168)
        self.assertEqual(self.live["g5_3_boxes"]["G5.3/008"], "ECONOMICS_DO_NOT_SUPPORT_PRODUCTION_SWITCH")
        self.assertFalse(self.live["decision"]["economics_support_switch"])
        self.assertTrue(self.live["decision"]["toy_scope_only"])

    def test_live_run_does_not_rewrite_capsule_or_predecessors(self):
        v1 = REPO / "research" / "g5-factored-warrant-v1" / "RESULT.json"
        v2 = REPO / "research" / "g5-bdd-warrant-v2" / "RESULT.json"
        v3 = REPO / "research" / "g5-zdd-warrant-v3" / "RESULT.json"
        self.assertEqual(self.live_path.parent, Path(self.tmp.name))
        self.assertNotEqual(self.live_path.resolve(), (HERE / "RESULT.json").resolve())
        self.assertIn("FACTORED_WARRANT_VALUE_SUPPORTED", v1.read_text())
        self.assertIn("BDD_PARENT_N3_PARITY_SUPPORTED", v2.read_text())
        self.assertIn("ZDD_PARENT_N3_PARITY_SUPPORTED", v3.read_text())

    def test_frozen_result_agrees_on_terminal_class(self):
        self.assertIsNotNone(self.frozen)
        self.assertIn(self.frozen["terminal"], HONEST)
        self.assertEqual(self.frozen["schema"], "ocm.g5.warrant-adoption.v1")
        self.assertEqual(self.live["schema"], self.frozen["schema"])
        self.assertEqual(self.live["terminal"], self.frozen["terminal"])
        self.assertEqual(self.frozen["g5_3_boxes"]["G5.3/008"], "ECONOMICS_DO_NOT_SUPPORT_PRODUCTION_SWITCH")
        self.assertFalse(self.frozen["production_warrant_switched"])
        self.assertFalse(self.frozen["physical_denominator_clean"])
        self.assertIn("PHYSICAL_DENOMINATOR_CLEAN", self.frozen["claim_ceiling"])
        self.assertIn("not claimed", self.frozen["claim_ceiling"].lower())


if __name__ == "__main__":
    unittest.main()
