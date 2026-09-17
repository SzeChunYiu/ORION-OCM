#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import obstruction_census_v1 as core


def load_oracle_module():
    spec = importlib.util.spec_from_file_location("h_obstruction_oracle", HERE / "independent_oracle_v1.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ObstructionCensusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = core.load_registry()
        cls.best, cls.exact = core.enumerate_minimum_semantics(5)
        cls.records = core.candidate_records(cls.best)
        cls.result = core.build_result()

    def test_01_frozen_registry_hash(self):
        self.assertEqual(core.file_sha256(core.REGISTRY_PATH), core.REGISTRY_SHA256)

    def test_02_complete_exact_family_registry(self):
        families = self.registry["families"]
        self.assertEqual(len(families), 43)
        self.assertEqual(tuple(row["row"] for row in families), core.EXPECTED_ROWS)
        self.assertEqual(len({row["id"] for row in families}), 43)

    def test_03_frozen_prediction_counts(self):
        predicted = Counter(
            self.registry["target_contracts"][row["contract"]]["predicted_disposition"]
            for row in self.registry["families"]
        )
        self.assertEqual(dict(predicted), self.registry["predicted_counts"])

    def test_04_semantic_quotient_counts(self):
        self.assertEqual({cost: len(layer) for cost, layer in self.exact.items()}, {1: 6, 2: 4, 3: 12, 4: 24, 5: 50})
        self.assertEqual(len(self.best), 96)
        self.assertEqual(len(self.records), 22)

    def test_05_positive_control_minimum_costs(self):
        targets = core.target_tables()
        expected = {"COPY_SIGNAL": 1, "INVERT_SIGNAL": 2, "PAIR_PARITY": 3, "PAIR_CONJUNCTION": 3}
        for name, cost in expected.items():
            self.assertEqual(self.best[targets[name]].cost, cost)
            self.assertTrue(core.classify_from_records(self.records, targets[name])["identified"])

    def test_06_resource_lower_bounds_and_witnesses(self):
        targets = core.target_tables()
        for name in ("TRIPLE_PARITY", "TRIPLE_CONJUNCTION"):
            self.assertNotIn(targets[name], {row["table"] for row in self.records})
            self.assertEqual(self.best[targets[name]].cost, 5)

    def test_07_structural_expressivity_invariant(self):
        for table in self.best:
            for coordinate in core.UNAVAILABLE_COORDS:
                self.assertTrue(core.flip_invariant(table, coordinate))
        for coordinate, name in zip(
            core.UNAVAILABLE_COORDS,
            ("HISTORY_STATE_CHANNEL", "STOCHASTIC_SOURCE_CHANNEL", "UPDATE_FEEDBACK_CHANNEL", "EXTERNAL_PEER_TOOL_CHANNEL"),
        ):
            self.assertFalse(core.flip_invariant(core.target_tables()[name], coordinate))

    def test_08_identifiability_counterexample(self):
        target = core.target_tables()["UNEXCITED_CONTEXT"]
        selection = core.classify_from_records(self.records, target)
        self.assertEqual(selection["minimum_fit_cost"], 1)
        self.assertEqual(set(selection["minimum_fit_tables"]), {0, target})
        self.assertFalse(selection["identified"])

    def test_09_target_dispositions_are_exhaustive(self):
        dispositions = {row["disposition"] for row in self.result["target_results"].values()}
        self.assertEqual(dispositions, set(core.DISPOSITIONS))

    def test_10_family_census_counts(self):
        self.assertEqual(self.result["counts"], self.registry["predicted_counts"])
        self.assertEqual(len(self.result["family_census"]), 43)

    def test_11_no_named_family_row_is_closed(self):
        self.assertEqual(self.result["family_gate_audit"]["eligible_named_family_rows"], 0)
        self.assertTrue(all(row["named_family_checkbox"] == "MUST_REMAIN_OPEN" for row in self.result["family_census"]))

    def test_12_remint_reverse(self):
        targets = core.target_tables()
        reminted = core.remint_records(self.records, "reverse")
        for target in targets.values():
            self.assertEqual(core.classify_from_records(self.records, target), core.classify_from_records(reminted, target))

    def test_13_remint_digest(self):
        targets = core.target_tables()
        reminted = core.remint_records(self.records, "digest")
        for target in targets.values():
            self.assertEqual(core.classify_from_records(self.records, target), core.classify_from_records(reminted, target))

    def test_14_independent_oracle_agrees(self):
        oracle = load_oracle_module().build()
        for name, primary in self.result["target_results"].items():
            independent = oracle["target_results"][name]
            self.assertEqual(primary["target_digest"], independent["target_digest"])
            self.assertEqual(
                self.best.get(core.target_tables()[name]).cost if core.target_tables()[name] in self.best else None,
                independent["minimum_full_cost"],
            )
            primary_selection = core.classify_from_records(self.records, core.target_tables()[name])
            self.assertEqual(primary_selection["minimum_fit_cost"], independent["minimum_fit_cost"])
            self.assertEqual(primary_selection["minimum_fit_digests"], independent["minimum_fit_digests"])
            self.assertEqual(primary_selection["identified"], independent["identified"])

    def test_15_oracle_source_is_separated(self):
        source = (HERE / "independent_oracle_v1.py").read_text(encoding="utf-8")
        self.assertNotIn("import obstruction_census_v1", source)
        self.assertNotIn("from obstruction_census_v1", source)

    def test_16_canonical_result_is_current(self):
        self.assertEqual((HERE / "RESULT_V1.json").read_bytes(), core.canonical_bytes(core.build_result()))

    def test_17_normal_cli_checks_both_results(self):
        subprocess.run([sys.executable, str(HERE / "obstruction_census_v1.py"), "--check"], check=True)
        subprocess.run([sys.executable, str(HERE / "independent_oracle_v1.py"), "--check"], check=True)

    def test_18_bool_coordinate_fails_closed(self):
        with self.assertRaises(core.CensusError):
            core.variable_table(True)

    def test_19_malformed_registry_fails_closed(self):
        broken = json.loads(core.REGISTRY_PATH.read_text(encoding="utf-8"))
        broken["families"] = broken["families"][:-1]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "registry.json"
            path.write_text(json.dumps(broken), encoding="utf-8")
            with self.assertRaises(core.CensusError):
                core.load_registry(path)

    def test_20_no_family_macro_in_grammar_signature(self):
        self.assertEqual(self.result["scope"]["leaves"], ["0", "1", "x0", "x1", "x2", "x3"])
        self.assertEqual(self.result["scope"]["operators"], ["NOT", "XOR", "AND"])

    def test_21_registry_is_explicit_authored_prior(self):
        self.assertEqual(self.result["registry_prior"]["status"], "AUTHORED_POSTHOC_EVALUATION_PRIOR")
        self.assertTrue(all(row["registered_hallmark"] for row in self.result["family_census"]))

    def test_22_budget_expansion_hostile(self):
        hostile = self.result["theorems"]["SCOPE_SENSITIVITY_HOSTILES"]["budget_expansion"]
        self.assertEqual(hostile["baseline"], "RESOURCE_OBSTRUCTION_AT_B3")
        self.assertTrue(hostile["expanded_result"]["identified"])

    def test_23_ecology_expansion_hostile(self):
        hostile = self.result["theorems"]["SCOPE_SENSITIVITY_HOSTILES"]["ecology_expansion"]
        self.assertTrue(hostile["expanded_result"]["identified"])

    def test_24_grammar_ecology_expansion_hostile(self):
        hostile = self.result["theorems"]["SCOPE_SENSITIVITY_HOSTILES"]["grammar_and_ecology_expansion"]
        self.assertTrue(hostile["expanded_result"]["identified"])

    def test_25_manifest_hashes(self):
        manifest = json.loads((HERE / "MANIFEST_V1.json").read_text(encoding="utf-8"))
        for name, expected in manifest["artifacts"].items():
            self.assertEqual(core.file_sha256(HERE / name), expected, name)


if __name__ == "__main__":
    unittest.main()
