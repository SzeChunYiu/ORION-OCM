"""Hostile protocol tests for G7 primitive-pressure measurement."""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SPEC = importlib.util.spec_from_file_location("g7_primitive_pressure", HERE / "experiment.py")
assert SPEC is not None and SPEC.loader is not None
E = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(E)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TestLoadContract(unittest.TestCase):
    def test_experiment_loaded_via_spec_from_file_location(self):
        source = (HERE / "test_protocol.py").read_text(encoding="utf-8")
        self.assertIn("spec_from_file_location", source)
        self.assertIn("experiment.py", source)

    def test_experiment_is_stdlib_json_only_and_does_not_import_src(self):
        source = (HERE / "experiment.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertTrue(imported.issubset({"argparse", "hashlib", "json", "subprocess", "sys", "pathlib", "typing"}))
        self.assertNotIn("ocm", imported)
        self.assertNotIn("from ocm", source)
        self.assertNotIn("sys.path.insert", source)
        self.assertIn("Historical M11 generations are not relabeled", source)


class TestFrozenCitations(unittest.TestCase):
    def test_pinned_hashes_match_disk_and_are_not_overwritten_by_a_run(self):
        before = {spec["capsule"]: _sha256(REPO / spec["capsule"]) for spec in E.CITATIONS}
        for spec in E.CITATIONS:
            self.assertEqual(before[spec["capsule"]], spec["sha256"], spec["capsule"])
        with tempfile.TemporaryDirectory() as tmp:
            E.write_outputs(Path(tmp) / "RESULT.json")
        after = {spec["capsule"]: _sha256(REPO / spec["capsule"]) for spec in E.CITATIONS}
        self.assertEqual(before, after)

    def test_predecessors_are_phased_same_lineage_and_not_m11(self):
        rows = E.cite_predecessors()
        self.assertEqual(len(rows), 6)
        self.assertTrue(rows[-1]["primary"])
        for row in rows:
            self.assertEqual(row["lineage_id"], E.LINEAGE_ID)
            self.assertEqual(row["terminal"], "PHASED_COGNITIVE_DEVELOPMENT")
            self.assertFalse(row["historical_m11_relabeled"])


class TestMetricAndDecision(unittest.TestCase):
    def test_t0_seed_primitives_count_and_already_earned_are_excluded(self):
        t0 = {
            "source_stage": "EMPTY",
            "imported_donor_identities": [
                "donor:primitive:inc",
                "donor:primitive:dec",
                "donor:primitive:double",
                "donor:primitive:square",
            ],
            "primitive_operators_added": [],
        }
        self.assertEqual(len(E.new_hand_authored(t0)), 4)
        t5 = {
            "source_stage": "OCM_4",
            "imported_donor_identities": [],
            "primitive_operators_added": [
                "donor:already-earned:TRY_LEFT",
                "donor:already-earned:TRY_RIGHT",
                "donor:cue-read",
            ],
        }
        self.assertEqual(E.new_hand_authored(t5), ["donor:cue-read"])

    def test_kendall_tau_and_mean_difference(self):
        xs = [0.0, 1.0, 2.0, 3.0]
        self.assertEqual(E.kendall_tau(xs, [1.0, 0.5, 0.25, 0.1]), -1.0)
        self.assertEqual(E.kendall_tau(xs, [0.0, 1.0, 2.0, 3.0]), 1.0)
        self.assertEqual(E.mean_first_difference([1.0, 0.5, 0.0]), -0.5)

    def test_decision_rule_decline_persist_and_parent(self):
        decline = [1.0, 0.0, 0.6, 0.2, 0.12, 0.05, 0.19]
        reset = [1.0] * 7
        self.assertEqual(E.decide(decline, reset), E.TERMINAL_DECLINES)
        persist = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
        self.assertEqual(E.decide(persist, [1.0] * 7), E.TERMINAL_PERSISTS)
        self.assertEqual(E.decide(reset, reset), E.TERMINAL_PARENT)


class TestLiveStudy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as tmp:
            cls.result = E.write_outputs(Path(tmp) / "RESULT.json")
        cls.disk = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))

    def test_terminal_is_allowed_and_not_programme_wide(self):
        self.assertIn(self.result["terminal"], E.ALLOWED_TERMINALS)
        self.assertEqual(self.result["terminal"], E.TERMINAL_DECLINES)
        self.assertFalse(self.result["programme_tick"])
        self.assertFalse(self.result["issue_73"])
        self.assertFalse(self.result["historical_m11_relabeled"])
        self.assertFalse(self.result["src_edited"])
        self.assertFalse(self.result["lineage_rerun"])
        self.assertFalse(self.result["ml_trained"])
        self.assertEqual(self.result["earned_transitions"], 7)
        self.assertEqual(self.result["lineage_id"], E.LINEAGE_ID)
        for banned in E.NOT_ISSUED:
            self.assertIn(banned, self.result["not_issued"])
        self.assertNotEqual(self.result["terminal"], "PHASED_COGNITIVE_DEVELOPMENT")
        self.assertNotEqual(self.result["terminal"], "DEVELOPMENTAL_EVOLVABILITY_SUPPORTED")

    def test_seven_earned_stages_and_reset_contrast(self):
        self.assertEqual(len(self.result["series"]), 7)
        for row, (source, target) in zip(self.result["series"], E.EXPECTED_STAGES):
            self.assertEqual((row["source_stage"], row["target_stage"]), (source, target))
        self.assertEqual(self.result["series"][0]["n_new"], 4)
        self.assertEqual(self.result["series"][1]["n_new"], 0)
        self.assertNotIn("donor:already-earned:TRY_LEFT", self.result["series"][5]["new_hand_authored"])
        self.assertEqual(self.result["p_stack_reset"], [1.0] * 7)
        self.assertTrue(self.result["later_continued_beats_reset"])
        self.assertTrue(self.result["t6_stack_lt_t0"])
        self.assertLess(self.result["kendall_tau_stack_continued"], 0)
        self.assertLess(self.result["mean_first_difference_stack_continued"], 0)
        self.assertLess(self.result["p_stack_continued"][-1], self.result["p_stack_continued"][0])
        for row in self.result["series"][1:]:
            self.assertLess(row["p_stack_continued"], row["p_stack_reset"])
            self.assertTrue(row["reset_costs_more_or_fails_reuse"])
            self.assertGreater(row["reset_work_units"], row["continued_work_units"])

    def test_committed_result_matches_live_terminal(self):
        self.assertEqual(self.disk["schema"], E.SCHEMA)
        self.assertEqual(self.disk["terminal"], self.result["terminal"])
        self.assertEqual(self.disk["p_stack_continued"], self.result["p_stack_continued"])
        self.assertEqual(self.disk["lineage_id"], E.LINEAGE_ID)
        self.assertEqual(self.disk["earned_transitions"], 7)


if __name__ == "__main__":
    unittest.main()
