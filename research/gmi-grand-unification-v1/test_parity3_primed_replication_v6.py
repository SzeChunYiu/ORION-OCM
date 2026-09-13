import importlib.util
import json
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent


def _load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V6 = _load("nn_nonnn_point_parity3_experiment_v6")
V5 = _load("nn_nonnn_point_parity3_experiment_v5")
V4 = _load("nn_nonnn_point_parity3_experiment_v4")


class PrimedInstrumentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.self_test = V6.deterministic_self_test()

    def test_self_test_green_without_timing(self):
        self.assertEqual(self.self_test["terminal"], "PARITY3_V6_INSTRUMENT_SELF_TEST_GREEN")
        self.assertFalse(self.self_test["protected_timing_measurement_executed"])
        self.assertFalse(self.self_test["full_registered_experiment_executed"])

    def test_instrument_is_supported_on_every_tested_interpreter(self):
        # The point of V6: the recorded witness is complete even where the
        # first-ever trace of a code object loses its first frame.
        self.assertTrue(self.self_test["opcode_instrument_supported_on_this_interpreter"])
        for cid, row in self.self_test["witness_diagnostics"].items():
            self.assertEqual(row["complete_frames"], 8, cid)
            self.assertEqual(row["empty_frames"], 0, cid)

    def test_priming_witness_is_recorded_either_way(self):
        priming = self.self_test["priming_witness_diagnostics"]
        self.assertEqual(sorted(priming), sorted(V6.CANDIDATES))
        required = self.self_test["priming_was_required_on_this_interpreter"]
        empty = {cid: row["empty_frames"] for cid, row in priming.items()}
        if required:
            # Where priming matters, the discarded session shows the defect.
            self.assertTrue(any(v > 0 for v in empty.values()), empty)
        else:
            self.assertTrue(all(v == 0 for v in empty.values()), empty)

    def test_priming_does_not_change_the_recorded_count(self):
        # Two independent recorded witnesses must agree exactly.
        for cid, row in V6.CANDIDATES.items():
            first, _ = V6.trace_candidate_opcodes(row["fn"])
            second, _ = V6.trace_candidate_opcodes(row["fn"])
            self.assertEqual(V6.validate_opcode_witness(row["fn"], first),
                             V6.validate_opcode_witness(row["fn"], second), cid)

    def test_candidates_byte_identical_to_both_parent_harnesses(self):
        identity = V6.candidate_identity_record()
        self.assertTrue(identity["byte_identical_to_parent"])
        self.assertEqual(sorted(identity["parent_harnesses"]),
                         ["nn_nonnn_point_parity3_experiment_v4.py",
                          "nn_nonnn_point_parity3_experiment_v5.py"])
        for name, hashes in identity["parent_source_sha256"].items():
            self.assertEqual(hashes, identity["local_source_sha256"], name)

    def test_schedule_and_rule_unchanged_from_v5(self):
        v5 = json.loads((HERE / "NN_NONNN_POINT_PARITY3_PREREG_V5.json").read_text())
        v6 = json.loads((HERE / "NN_NONNN_POINT_PARITY3_PREREG_V6.json").read_text())
        self.assertEqual(v6["measurement_schedule"], v5["measurement_schedule"])
        self.assertEqual(v6["registered_resource_coordinates"],
                         v5["registered_resource_coordinates"])
        self.assertEqual(v6["selection_rule"], v5["selection_rule"])
        self.assertEqual(v6["development_accounting"], v5["development_accounting"])
        self.assertEqual(v6["candidates"], v5["candidates"])

    def test_registration_is_frozen_unexecuted_and_discloses_its_status(self):
        v6 = json.loads((HERE / "NN_NONNN_POINT_PARITY3_PREREG_V6.json").read_text())
        V6.validate_preregistration(v6)
        self.assertEqual(v6["status"], "PREREGISTERED_NOT_EXECUTED")
        self.assertFalse(v6["independent_prospective_prediction"])
        self.assertTrue(v6["prior_diagnostic_knowledge"]["no_timing_observed_on_3_13"])
        self.assertIn("v6_self_test_executed_before_freeze", v6["prior_diagnostic_knowledge"])

    def test_adjudication_rule_matches_v5_and_v4(self):
        boxes = {
            "N_THRESHOLD_DNF4_V1": {"python_opcode_count_per_full_domain_sweep": [440, 440],
                                    "wall_block_ns": [50, 53], "process_block_ns": [50, 53]},
            "X_XOR2_V1": {"python_opcode_count_per_full_domain_sweep": [72, 72],
                          "wall_block_ns": [10, 12], "process_block_ns": [10, 12]},
            "N_SUM_THRESHOLD3_V3": {"python_opcode_count_per_full_domain_sweep": [288, 288],
                                    "wall_block_ns": [37, 40], "process_block_ns": [37, 40]},
            "X_LOOKUP8_V3": {"python_opcode_count_per_full_domain_sweep": [128, 128],
                             "wall_block_ns": [13, 14], "process_block_ns": [13, 14]},
        }
        for module in (V6, V5, V4):
            verdict = module.adjudicate(boxes)
            self.assertEqual(verdict["terminal"], "DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE")
            self.assertEqual(verdict["frontier_candidate_ids"], ["X_XOR2_V1"])

    def test_capability_null_and_balanced_order(self):
        for cid in V6.CANDIDATES:
            self.assertTrue(V6.capability_record(cid)["exact_gate_pass"])
        self.assertEqual(V6.constant_zero_null_record()["correct"], 4)
        counts = {cid: [0] * 4 for cid in V6.CANDIDATES}
        for block in range(32):
            for position, cid in enumerate(V6.candidate_order(block)):
                counts[cid][position] += 1
        for cid, row in counts.items():
            self.assertEqual(row, [8, 8, 8, 8], cid)


if __name__ == "__main__":
    unittest.main()
