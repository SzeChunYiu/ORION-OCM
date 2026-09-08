"""Governance interface tests, NOT evidence of cognitive self-improvement.

Initial incidents come from the actual blinded development intake. The runner
below is an explicitly mocked measurement interface with authored outcomes; its
successes test admission plumbing and must never enter a cognitive result table.
No protected observations or experiments are executed.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evolution import Candidate, EvolutionCell, digest
from intake import ingest_case, load_cases
from ocm.selfmodel.diagnose import diagnose
from ocm.selfmodel.govern import ExternalAdopter
from ocm.selfmodel.model import Layer


PROTOCOL = {
    "resource_keys": ["work", "bytes"], "budgets": {"work": 1000, "bytes": 1000},
    "probe_limit": 3, "proposal_budget": 100, "adoption_budget": 100,
    "quality_margin": 0, "edit_classes": {"mode": ["C0"]},
}
CONFIG = {"mode": "slow"}
EDITS = {"mode": ["slow", "fast", "bad"]}


def tasks(prefix, values):
    return [{"task_id": f"{prefix}-{v}", "semantic_id": digest({"mock_input": v}),
             "ecology": "development", "input": v} for v in values]


class MockMeasurementInterface:
    """Authored outcomes for SOFTWARE CONTRACT TESTING ONLY."""

    def __init__(self, cell=None, *, shadow_regression=False, invalid_resource=None):
        self.calls = []
        self.cell = cell
        self.shadow_regression = shadow_regression
        self.invalid_resource = invalid_resource

    def __call__(self, config, supplied):
        is_shadow = all(t["input"] >= 100 for t in supplied)
        if is_shadow and self.cell is not None:
            registered = [e for e in self.cell.runtime.events
                          if "prediction_receipt" in e.payload.get("payload", {})]
            if not registered:
                raise AssertionError("shadow runner called before prediction registration")
        self.calls.append({"config": copy.deepcopy(config), "tasks": copy.deepcopy(supplied)})
        n = len(supplied)
        work = (1 if config["mode"] == "fast" else 2) * n
        if is_shadow and self.shadow_regression and config["mode"] == "fast":
            work = 3 * n
        resources = {"work": work, "bytes": 10}
        if self.invalid_resource is not None:
            resources["work"] = self.invalid_resource
        return {"n": n, "success": n - int(config["mode"] == "bad"),
                "preservation_violations": 0, "resources": resources,
                "measurement_origin": "MOCK_INTERFACE_TEST_ONLY"}


class EvolutionGovernanceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.cell = self.open_cell()
        self.case = load_cases()[0]

    def tearDown(self):
        self.directory.cleanup()

    def open_cell(self):
        return EvolutionCell(self.root, CONFIG, allowed_edits=EDITS, protocol=PROTOCOL)

    def observation(self):
        return {"ecology": "development", "failure_id": self.case["case_id"],
                "observations": copy.deepcopy(self.case["observations"]),
                "observed": "actual historical development summary; raw trace unavailable",
                "resources": {}}

    def candidate(self, mode="fast", **kwargs):
        return Candidate("mock-" + mode, kwargs.get("change_class", "C0"),
                         kwargs.get("target_component", "search.configuration"),
                         kwargs.get("edits", {"mode": mode}),
                         origin="existing_alternative", origin_ref="MOCK_INTERFACE_TEST_ONLY")

    def cycle(self, *, runner=None, adopter=None, candidates=None, dev=None, shadow=None):
        return self.cell.develop(self.observation(), candidates or [self.candidate()],
            dev_tasks=dev or tasks("dev", [1, 2]),
            shadow_suites=shadow or {"target": tasks("shadow", [101, 102])},
            runner=runner or MockMeasurementInterface(self.cell),
            external_adopter=adopter or ExternalAdopter("test-host-external-token"))

    def test_actual_intake_has_nine_unknown_layers_and_no_supplied_ablation(self):
        cases = load_cases()
        self.assertEqual(len(cases), 6)
        for case in cases:
            failure = ingest_case(self.cell.self_model, case)
            assessment = diagnose(failure)
            self.assertEqual(set(assessment.unknown), {layer.value for layer in Layer})
            self.assertEqual(assessment.weights, {})
            self.assertIsNone(assessment.minimum_sufficient)
            self.assertFalse(assessment.architecture_alarm)
            self.assertEqual(failure.ablations, ())
            self.assertEqual(failure.uncertainty, "UNKNOWN")
            self.assertTrue(all(e in self.cell.runtime.state.evidence.records for e in failure.trace_ids))

    def test_protected_observation_and_task_intake_refused_before_runner(self):
        runner = MockMeasurementInterface()
        observation = self.observation()
        observation["ecology"] = "protected"
        with self.assertRaises(PermissionError):
            self.cell.develop(observation, [self.candidate()], dev_tasks=tasks("d", [1]),
                shadow_suites={"target": tasks("s", [101])}, runner=runner,
                external_adopter=ExternalAdopter("test"))
        bad = tasks("d", [1])
        bad[0]["ecology"] = "protected"
        with self.assertRaises(ValueError):
            self.cycle(dev=bad, runner=runner)
        self.assertEqual(runner.calls, [])
        self.assertEqual(self.cell.generation, 0)

    def test_human_diagnosis_label_refused(self):
        observation = self.observation()
        observation["oracle_layer"] = "D0"
        runner = MockMeasurementInterface()
        with self.assertRaises(ValueError):
            self.cell.develop(observation, [self.candidate()], dev_tasks=tasks("d", [1]),
                shadow_suites={"target": tasks("s", [101])}, runner=runner,
                external_adopter=ExternalAdopter("test"))
        self.assertEqual(runner.calls, [])

    def test_semantic_aliases_and_missing_semantic_identity_refused(self):
        runner = MockMeasurementInterface()
        with self.assertRaises(ValueError):
            self.cycle(dev=tasks("d", [1]), shadow={"target": tasks("renamed", [1])}, runner=runner)
        missing = tasks("d", [2])
        del missing[0]["semantic_id"]
        with self.assertRaises(ValueError):
            self.cycle(dev=missing, runner=runner)
        self.assertEqual(runner.calls, [])

    def test_seen_semantics_survive_restart_and_relabelling(self):
        self.cycle(candidates=[self.candidate("bad")])
        self.cell = self.open_cell()
        runner = MockMeasurementInterface()
        with self.assertRaises(ValueError):
            self.cycle(dev=tasks("new-label", [1, 2]),
                       shadow={"target": tasks("new-shadow", [103, 104])}, runner=runner)
        self.assertEqual(runner.calls, [])

    def test_constitution_and_protected_writes_refused(self):
        candidates = [self.candidate(change_class="C6"),
                      self.candidate(target_component="constitution.policy"),
                      self.candidate(edits={"nested": {"Meter": {"charge": 0}}}),
                      self.candidate(edits={"mode": "replace evaluator"})]
        for candidate in candidates:
            with self.subTest(candidate=candidate):
                with self.assertRaises((ValueError, PermissionError)):
                    self.cell.apply_candidate(CONFIG, candidate)
        self.assertEqual(self.cell.config, CONFIG)
        self.assertEqual(self.cell.generation, 0)

    def test_paid_probes_follow_measured_results_and_prediction_precedes_shadow(self):
        runner = MockMeasurementInterface(self.cell)
        result = self.cycle(runner=runner, candidates=[self.candidate("bad"), self.candidate("fast")])
        self.assertEqual(result["terminal"], "DEVELOPMENT_CHANGE_ADOPTED")
        self.assertEqual(self.cell.generation, 1)
        self.assertEqual(set(result["initial_diagnosis"]["unknown"]), {layer.value for layer in Layer})
        observed = {p["candidate"]["edits"]["mode"]: p for p in result["probes"]}
        self.assertFalse(observed["bad"]["restored_contract"])
        self.assertTrue(observed["fast"]["restored_contract"])
        self.assertEqual(len(runner.calls), 5)  # baseline + two probes + both shadow arms
        expected_cost = sum((1 if c["config"]["mode"] == "fast" else 2) * len(c["tasks"]) for c in runner.calls)
        self.assertEqual(result["measured_runner_cost"]["work"], expected_cost)
        self.assertNotIn("bytes", result["measured_runner_cost"])
        self.assertEqual(result["peak_runner_resources"]["bytes"], 10)
        self.assertTrue(result["external_decision"]["approved"])
        self.assertTrue(result["assurance"]["passed"])

    def test_shadow_regression_blocks_even_permissive_external_adopter(self):
        result = self.cycle(runner=MockMeasurementInterface(self.cell, shadow_regression=True),
                            adopter=ExternalAdopter("test", policy=lambda assurance: True))
        self.assertEqual(result["terminal"], "SELF_EVOLUTION_REGRESSES")
        self.assertTrue(result["external_decision"]["approved"])
        self.assertFalse(result["assurance"]["passed"])
        self.assertEqual(self.cell.generation, 0)
        self.assertEqual(self.cell.config, CONFIG)

    def test_preservation_suite_resource_regression_blocks_admission(self):
        measured = MockMeasurementInterface(self.cell)

        def preservation_regression(config, supplied):
            result = measured(config, supplied)
            if config["mode"] == "fast" and all(t["input"] >= 200 for t in supplied):
                result["resources"]["bytes"] = 11
            return result

        result = self.cycle(runner=preservation_regression, shadow={
            "target": tasks("target", [101, 102]),
            "preserve": tasks("preserve", [201, 202]),
        })
        self.assertEqual(result["terminal"], "SELF_EVOLUTION_REGRESSES")
        self.assertFalse(result["assurance"]["checks"]["external_preservation_resource_noninferiority"])
        self.assertEqual(self.cell.generation, 0)

    def test_external_rejection_blocks_generation_increment(self):
        result = self.cycle(adopter=ExternalAdopter("test", policy=lambda assurance: False))
        self.assertEqual(result["terminal"], "EXTERNAL_ADOPTION_REJECTED")
        self.assertTrue(result["assurance"]["passed"])
        self.assertEqual(self.cell.generation, 0)

    def test_mutable_candidate_alias_cannot_install_unmeasured_edit(self):
        candidate = self.candidate()
        measured = MockMeasurementInterface(self.cell)

        def alias_mutating_interface(config, supplied):
            result = measured(config, supplied)
            if config["mode"] == "fast" and all(t["input"] >= 100 for t in supplied):
                candidate.edits["mode"] = "bad"
            return result

        try:
            self.cycle(runner=alias_mutating_interface, candidates=[candidate])
        except (ValueError, PermissionError):
            pass  # Refusing a changed input is also a valid boundary behavior.
        self.assertNotEqual(self.cell.config, {"mode": "bad"})
        if self.cell.generation:
            self.assertEqual(self.cell.config, {"mode": "fast"})

    def test_quality_and_all_resource_dimensions_must_be_noninferior(self):
        baseline = {"n": 2, "success": 2, "preservation_violations": 0,
                    "resources": {"work": 10, "bytes": 10}}
        for changed in ({"resources": {"work": 9, "bytes": 11}},
                        {"success": 1, "resources": {"work": 9, "bytes": 9}},
                        {"preservation_violations": 1}, {}):
            challenger = {**copy.deepcopy(baseline), **changed}
            self.assertFalse(self.cell._dominates(challenger, baseline))
        challenger = {**baseline, "resources": {"work": 9, "bytes": 10}}
        self.assertTrue(self.cell._dominates(challenger, baseline))

    def test_nonfinite_negative_and_boolean_resource_measurements_refused(self):
        for value in (float("nan"), float("inf"), -1, True):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    self.cell._measure(MockMeasurementInterface(invalid_resource=value), CONFIG, tasks("d", [1]))

    def test_failed_runner_does_not_erase_task_exposure(self):
        with self.assertRaises(ValueError):
            self.cycle(runner=MockMeasurementInterface(invalid_resource=-1))
        self.cell = self.open_cell()
        runner = MockMeasurementInterface()
        with self.assertRaises(ValueError):
            self.cycle(runner=runner)
        self.assertEqual(runner.calls, [])

    def test_unsuccessful_second_cycle_cannot_increment_generation(self):
        self.cycle()
        self.assertEqual(self.cell.generation, 1)
        result = self.cycle(candidates=[self.candidate("bad")],
            dev=tasks("dev2", [3, 4]), shadow={"target": tasks("shadow2", [103, 104])})
        self.assertEqual(result["terminal"], "SELF_DIAGNOSIS_NOT_IDENTIFIABLE")
        self.assertNotIn("external_decision", result)
        self.assertEqual(self.cell.generation, 1)

    def test_cold_restart_rollback_and_cache_reopening(self):
        self.cell.state["cache"] = {"old-derived-method": {"value": 1}}
        self.cell._save()
        result = self.cycle()
        self.assertEqual(result["reopened_cache_keys"], ["old-derived-method"])
        self.assertEqual(self.cell.state["cache"], {})
        self.cell = self.open_cell()
        self.assertEqual(self.cell.generation, 1)
        self.assertEqual(self.cell.config, {"mode": "fast"})
        rollback = self.cell.rollback_latest()
        self.assertTrue(rollback["exact"])
        self.assertEqual(self.cell.config, CONFIG)
        self.cell = self.open_cell()
        self.assertEqual(self.cell.generation, 0)
        self.assertEqual(self.cell.config, CONFIG)

    def test_recomputed_snapshot_checksum_cannot_rewrite_history_or_config(self):
        envelope = json.loads(self.cell.path.read_text())
        envelope["machine"]["config"] = {"mode": "fast"}
        envelope["machine"]["history"] = [{"terminal": "fabricated"}]
        envelope["sha256"] = digest(envelope["machine"])
        self.cell.path.write_text(json.dumps(envelope))
        with self.assertRaises(ValueError):
            self.open_cell()

    def test_protected_freeze_prevents_new_development_and_rollback(self):
        self.cycle()
        frozen = self.cell.freeze_for_protected(comparator={"id": "matched-parent"},
            budgets={"work": 100}, protected_protocol_hash="identified-not-executed")
        self.cell = self.open_cell()
        self.assertEqual(frozen, self.cell.state["freeze"])
        with self.assertRaises(PermissionError):
            self.cycle(dev=tasks("d2", [3, 4]), shadow={"target": tasks("s2", [103, 104])})
        with self.assertRaises(PermissionError):
            self.cell.rollback_latest()


if __name__ == "__main__":
    unittest.main(verbosity=2)
