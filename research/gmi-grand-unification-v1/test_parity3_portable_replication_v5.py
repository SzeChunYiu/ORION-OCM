import importlib.util
import json
import pathlib
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent


def _load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V5 = _load("nn_nonnn_point_parity3_experiment_v5")
ADJ = _load("parity3_cross_envelope_adjudicate_v5")
V4 = _load("nn_nonnn_point_parity3_experiment_v4")


def _packet(host, version, terminal, *, opcodes=None, families=None, identity=True):
    """A minimal well-formed V5 packet shell for adjudicator tests."""
    packet = {
        "schema": "NN_NONNN_POINT_PARITY3_RESULT_V5",
        "environment": {
            "host_label": host,
            "execution_context": "INTERACTIVE_OR_LOCAL",
            "python_implementation": "CPython",
            "python_version": version,
            "platform": "Linux-test",
            "processor": "",
            "cpu_count": 4,
        },
        "candidate_identity": {
            "byte_identical_to_parent": identity,
            "local_source_sha256": V5.candidate_source_hashes(
                HERE / "nn_nonnn_point_parity3_experiment_v5.py"
            ) if identity else {"X_XOR2_V1": "0" * 64},
        },
        "terminal": terminal,
    }
    if terminal == ADJ.INVALID_TERMINAL:
        packet.update({"environment_gate_failures": [],
                       "instrumentation_gate_failure": "incomplete or reordered opcode events",
                       "instrumentation_gate_pass": False,
                       "protected_timing_measurement_executed": False})
    else:
        packet.update({
            "frontier_candidate_ids": ["X_XOR2_V1"],
            "frontier_families": families or ["NON_NEURAL"],
            "opcode_counts": opcodes or {"N_THRESHOLD_DNF4_V1": 472, "X_XOR2_V1": 88,
                                         "N_SUM_THRESHOLD3_V3": 312, "X_LOOKUP8_V3": 136},
            "instrumentation_gate_pass": True,
            "protected_timing_measurement_executed": True,
        })
    return packet


def _write(tmp, name, packet):
    path = pathlib.Path(tmp) / name
    path.write_text(json.dumps(packet), encoding="utf-8")
    return path


class PortableInstrumentTests(unittest.TestCase):
    def test_self_test_runs_on_this_interpreter_without_timing(self):
        result = V5.deterministic_self_test()
        self.assertEqual(result["terminal"], "PARITY3_V5_INSTRUMENT_SELF_TEST_GREEN")
        self.assertFalse(result["protected_timing_measurement_executed"])
        self.assertFalse(result["full_registered_experiment_executed"])
        self.assertIn("opcode_instrument_supported_on_this_interpreter", result)

    def test_candidates_are_byte_identical_to_the_v4_harness(self):
        identity = V5.candidate_identity_record()
        self.assertTrue(identity["parent_harness_available"])
        self.assertTrue(identity["byte_identical_to_parent"])
        self.assertEqual(identity["local_source_sha256"], identity["parent_source_sha256"])

    def test_candidate_families_and_universe_match_v4(self):
        self.assertEqual(list(V5.CANDIDATES), list(V4.CANDIDATES))
        for cid in V5.CANDIDATES:
            self.assertEqual(V5.CANDIDATES[cid]["family"], V4.CANDIDATES[cid]["family"])

    def test_registration_validates_and_is_frozen_unexecuted(self):
        prereg = json.loads((HERE / "NN_NONNN_POINT_PARITY3_PREREG_V5.json").read_text())
        V5.validate_preregistration(prereg)
        self.assertEqual(prereg["status"], "PREREGISTERED_NOT_EXECUTED")
        self.assertFalse(prereg["independent_prospective_prediction"])
        self.assertFalse(prereg["prior_diagnostic_knowledge"]["no_timing_observed"] is False)
        self.assertEqual(sorted(prereg["replication_targets"]["named_outstanding_hosts"]),
                         ["laptop-billy", "lunarc", "old"])

    def test_registration_rejects_a_changed_schedule(self):
        prereg = json.loads((HERE / "NN_NONNN_POINT_PARITY3_PREREG_V5.json").read_text())
        prereg["measurement_schedule"]["timed_blocks"] = 8
        with self.assertRaises(V5.MeasurementIntegrityError):
            V5.validate_preregistration(prereg)

    def test_registration_rejects_a_changed_candidate_source(self):
        prereg = json.loads((HERE / "NN_NONNN_POINT_PARITY3_PREREG_V5.json").read_text())
        prereg["candidates"][1]["source_sha256"] = "0" * 64
        with self.assertRaises(V5.MeasurementIntegrityError):
            V5.validate_preregistration(prereg)

    def test_capability_and_null_baseline(self):
        for cid in V5.CANDIDATES:
            self.assertTrue(V5.capability_record(cid)["exact_gate_pass"])
        self.assertEqual(V5.constant_zero_null_record()["correct"], 4)

    def test_balanced_candidate_order_is_uniform_over_positions(self):
        counts = {cid: [0] * 4 for cid in V5.CANDIDATES}
        for block in range(32):
            for position, cid in enumerate(V5.candidate_order(block)):
                counts[cid][position] += 1
        for cid, row in counts.items():
            self.assertEqual(row, [8, 8, 8, 8], cid)

    def test_environment_is_recorded_not_gated(self):
        valid, failures = V5.protocol_environment_valid()
        self.assertTrue(valid, failures)
        self.assertEqual(failures, [])
        env = V5.environment_record("unit-test")
        self.assertEqual(env["host_label"], "unit-test")
        for key in ("execution_context", "python_version", "platform", "slurm", "github"):
            self.assertIn(key, env)

    def test_v4_harness_refuses_to_run_outside_github_actions(self):
        # The portability defect V5 exists to repair: V1-V4 cannot produce a
        # valid packet on any independent machine.
        valid, failures = V4.protocol_environment_valid()
        self.assertFalse(valid)
        self.assertIn("not_github_actions_hosted_execution", failures)


class CrossEnvelopeAdjudicationTests(unittest.TestCase):
    def test_single_valid_envelope_is_not_replication(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, "a.json", _packet("h1", "3.12.3",
                                                 "DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE"))
            result = ADJ.adjudicate({ADJ.envelope_label(ADJ.load_packet(path)):
                                     ADJ.load_packet(path)}, ["lunarc"])
        self.assertEqual(result["cross_envelope_stability"], "SINGLE_ENVELOPE_NO_REPLICATION")
        self.assertFalse(result["replication_obligation_discharged"])
        self.assertEqual(result["named_outstanding_hosts"], ["lunarc"])

    def test_agreeing_envelopes_are_stable(self):
        with tempfile.TemporaryDirectory() as tmp:
            packets = {}
            for name, version in (("a.json", "3.11.15"), ("b.json", "3.12.3")):
                path = _write(tmp, name, _packet("h1", version,
                                                 "DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE"))
                loaded = ADJ.load_packet(path)
                packets[ADJ.envelope_label(loaded)] = loaded
            result = ADJ.adjudicate(packets, [])
        self.assertEqual(result["cross_envelope_stability"],
                         "STABLE_ACROSS_ENVELOPES__DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE")
        self.assertEqual(len(result["valid_envelopes"]), 2)

    def test_disagreeing_envelopes_are_unstable(self):
        with tempfile.TemporaryDirectory() as tmp:
            packets = {}
            rows = (("a.json", "3.11.15", "DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE", None),
                    ("b.json", "3.12.3", "UNDECIDED_FROM_CURRENT_EVIDENCE",
                     ["NEURAL", "NON_NEURAL"]))
            for name, version, terminal, families in rows:
                path = _write(tmp, name, _packet("h1", version, terminal, families=families))
                loaded = ADJ.load_packet(path)
                packets[ADJ.envelope_label(loaded)] = loaded
            result = ADJ.adjudicate(packets, [])
        self.assertEqual(result["cross_envelope_stability"], "UNSTABLE_ACROSS_ENVELOPES")
        self.assertEqual(len(result["distinct_valid_terminals"]), 2)

    def test_invalid_packets_are_retained_and_never_counted_as_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            packets = {}
            for name, version, terminal in (
                ("a.json", "3.12.3", "DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE"),
                ("b.json", "3.13.12", ADJ.INVALID_TERMINAL),
            ):
                path = _write(tmp, name, _packet("h1", version, terminal))
                loaded = ADJ.load_packet(path)
                packets[ADJ.envelope_label(loaded)] = loaded
            result = ADJ.adjudicate(packets, [])
        self.assertEqual(len(result["valid_envelopes"]), 1)
        self.assertEqual(len(result["invalid_envelopes"]), 1)
        self.assertEqual(result["cross_envelope_stability"], "SINGLE_ENVELOPE_NO_REPLICATION")
        invalid = result["per_envelope"][result["invalid_envelopes"][0]]
        self.assertIn("gate_failures", invalid)

    def test_interpreter_dependent_opcode_counts_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            packets = {}
            rows = (("a.json", "3.11.15", {"N_THRESHOLD_DNF4_V1": 512, "X_XOR2_V1": 88,
                                           "N_SUM_THRESHOLD3_V3": 344, "X_LOOKUP8_V3": 136}),
                    ("b.json", "3.12.3", {"N_THRESHOLD_DNF4_V1": 472, "X_XOR2_V1": 88,
                                          "N_SUM_THRESHOLD3_V3": 312, "X_LOOKUP8_V3": 136}))
            for name, version, opcodes in rows:
                path = _write(tmp, name, _packet("h1", version,
                                                 "DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE",
                                                 opcodes=opcodes))
                loaded = ADJ.load_packet(path)
                packets[ADJ.envelope_label(loaded)] = loaded
            result = ADJ.adjudicate(packets, [])
        self.assertTrue(result["opcode_counts_are_interpreter_dependent"])
        # The cheapest-to-costliest ordering is what the verdict depends on.
        self.assertEqual(len(result["distinct_opcode_orderings"]), 1)

    def test_packets_with_different_candidates_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            packets = {}
            for name, identity in (("a.json", True), ("b.json", False)):
                path = _write(tmp, name, _packet("h1", f"3.12.{int(identity)}",
                                                 "DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE",
                                                 identity=identity))
                loaded = ADJ.load_packet(path)
                packets[ADJ.envelope_label(loaded)] = loaded
            with self.assertRaises(ADJ.AdjudicationError):
                ADJ.adjudicate(packets, [])

    def test_malformed_packets_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = pathlib.Path(tmp) / "bad.json"
            bad.write_text("{not json", encoding="utf-8")
            with self.assertRaises(ADJ.AdjudicationError):
                ADJ.load_packet(bad)
            wrong = _write(tmp, "wrong.json", {"schema": "SOMETHING_ELSE"})
            with self.assertRaises(ADJ.AdjudicationError):
                ADJ.load_packet(wrong)
            unknown = _packet("h1", "3.12.3", "DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE")
            unknown["terminal"] = "MADE_UP"
            path = _write(tmp, "unknown.json", unknown)
            with self.assertRaises(ADJ.AdjudicationError):
                ADJ.load_packet(path)
            with self.assertRaises(ADJ.AdjudicationError):
                ADJ.load_packet(pathlib.Path(tmp) / "absent.json")


if __name__ == "__main__":
    unittest.main()
