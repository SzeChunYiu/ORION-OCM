"""Hostile evidence controls; synthetic inputs are never labelled empirical observations."""
import copy
import unittest
from frozen_contract_v1 import AuditError, IDS, Unverifiable, strict_json
from packet_content_v6 import audit_packet
from synthetic_fixture_v1 import packet


class PacketTests(unittest.TestCase):
    def setUp(self):
        self.p = packet()

    def test_complete_synthetic_control(self):
        report = audit_packet(self.p)
        self.assertEqual(report["frontier_candidate_ids"], ["X_XOR2_V1"])
        self.assertEqual(report["timed_blocks"], 128)
        self.assertFalse(report["timing_rerun"])

    def reject(self, change):
        change(self.p)
        with self.assertRaises(AuditError):
            audit_packet(self.p)

    def test_flags_cannot_replace_evidence(self):
        for key in ("environment_gate_pass", "instrumentation_gate_pass",
                    "protected_timing_measurement_executed", "protected_resource_measurement_executed"):
            p = copy.deepcopy(self.p); p[key] = False
            with self.subTest(key=key), self.assertRaises(AuditError):
                audit_packet(p)

    def test_changed_frozen_bindings_rejected(self):
        for key in ("harness_sha256", "preregistration_sha256"):
            p = copy.deepcopy(self.p); p["environment"][key] = "0" * 64
            with self.subTest(key=key), self.assertRaises(AuditError):
                audit_packet(p)

    def test_empty_measurements_rejected(self):
        self.reject(lambda p: p.update(measurements={}))

    def test_omitted_capability_rejected(self):
        self.reject(lambda p: p["capability"].pop(IDS[0]))

    def test_wrong_output_rejected(self):
        self.reject(lambda p: p["capability"][IDS[0]]["outputs"].__setitem__(0, 1))

    def test_unknown_source_map_rejected(self):
        self.reject(lambda p: p["candidate_identity"].update(local_source_sha256={}))

    def test_omitted_forward_opcode_rejected(self):
        self.reject(lambda p: p["instrumentation"]["forward_witnesses"][IDS[0]]["calls"][0]
                    ["opcode_offsets"].pop())

    def test_wrong_reverse_output_rejected(self):
        self.reject(lambda p: p["instrumentation"]["reverse_witnesses"][IDS[1]]["calls"][0]
                    .update(output=True))

    def test_diagnostic_disagreement_rejected(self):
        self.reject(lambda p: p["instrumentation"]["witness_diagnostics"][IDS[2]]
                    .update(complete_frames=7))

    def test_missing_timing_block_rejected(self):
        self.reject(lambda p: p["measurements"][IDS[3]].pop())

    def test_order_corruption_rejected(self):
        self.reject(lambda p: p["measurements"][IDS[0]][0].update(order_index=1))

    def test_boolean_checksum_rejected(self):
        self.reject(lambda p: p["measurements"][IDS[0]][0].update(checksum=True))

    def test_zero_duration_rejected(self):
        self.reject(lambda p: p["measurements"][IDS[0]][0].update(wall_block_ns=0))

    def test_narrowed_envelope_rejected(self):
        self.reject(lambda p: p["resource_boxes"][IDS[0]]["wall_block_ns"].__setitem__(1, 1))

    def test_false_frontier_and_terminal_rejected(self):
        self.reject(lambda p: p.update(frontier_candidate_ids=[IDS[0]],
                    frontier_families=["NEURAL"], terminal="DERIVED_NEURAL_AT_REGISTERED_SCOPE"))

    def test_scope_overclaim_rejected(self):
        self.reject(lambda p: p.update(independent_prospective_prediction=True))

    def test_other_interpreter_is_unverifiable(self):
        self.p["environment"]["python_version"] = "3.12.999"
        with self.assertRaises(Unverifiable):
            audit_packet(self.p)

    def test_duplicate_nonfinite_unknown_fields(self):
        for raw in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":1e999}'):
            with self.subTest(raw=raw), self.assertRaises(AuditError):
                strict_json(raw)
        self.reject(lambda p: p.update(unregistered_claim=True))


if __name__ == "__main__":
    unittest.main()
