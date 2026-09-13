"""Audit the retained first packet and reject substantive tampering; never time."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'verify_parity3_hosted_v4.py'
SPEC = importlib.util.spec_from_file_location('hosted_audit_v4', SOURCE)
V = importlib.util.module_from_spec(SPEC)
exec(compile(SOURCE.read_bytes(), str(SOURCE), 'exec'), V.__dict__)


class HostedV4AuditTests(unittest.TestCase):
    def setUp(self):
        self.raw = (HERE / V.PACKET).read_bytes()
        self.packet = V.strict_json(self.raw.decode())
        self.provenance = V.strict_json((HERE / V.PROVENANCE).read_text())

    def reject_changed_packet(self):
        # Supply self-consistent rewritten bytes and custody hashes. The semantic
        # checks must still reject this forged evidence, not just a stale hash.
        raw = (json.dumps(self.packet, indent=2, sort_keys=True) + '\n').encode()
        self.provenance['packet_sha256'] = V.sha(raw)
        self.provenance['source_log_excerpt'] = ''.join('2026-09-13T09:13:00Z ' + line + '\n'
                                                       for line in raw.decode().splitlines())
        self.provenance['source_log_excerpt_sha256'] = V.sha(self.provenance['source_log_excerpt'].encode())
        with self.assertRaises(V.AuditError):
            V.validate(self.packet, self.provenance, raw)

    def test_first_hosted_packet_passes_without_rerun(self):
        report = V.validate(self.packet, self.provenance, self.raw)
        self.assertEqual(report['frontier_candidate_ids'], ['X_XOR2_V1'])
        self.assertEqual(report['timed_candidate_calls'], 20480000)
        self.assertIs(report['timing_rerun'], False)

    def test_incomplete_trace_cannot_hide_behind_rehashed_custody(self):
        self.packet['instrumentation']['forward_witnesses'][V.IDS[2]]['calls'][0]['opcode_offsets'].pop()
        self.reject_changed_packet()

    def test_missing_timing_block_rejected(self):
        self.packet['measurements'][V.IDS[3]].pop()
        self.reject_changed_packet()

    def test_changed_order_rejected(self):
        self.packet['measurements'][V.IDS[0]][0]['order_index'] = 1
        self.reject_changed_packet()

    def test_boolean_checksum_rejected(self):
        self.packet['measurements'][V.IDS[0]][0]['checksum'] = True
        self.reject_changed_packet()

    def test_false_frontier_rejected(self):
        self.packet['frontier_candidate_ids'].append(V.IDS[2])
        self.reject_changed_packet()

    def test_narrowed_envelope_rejected(self):
        self.packet['resource_boxes'][V.IDS[1]]['wall_block_ns'][1] -= 1
        self.reject_changed_packet()

    def test_new_scope_claim_rejected(self):
        self.packet['independent_prospective_prediction'] = True
        self.reject_changed_packet()

    def test_wrong_source_and_rerun_rejected(self):
        original = copy.deepcopy(self.provenance)
        for key, value in (('tested_github_sha', '0' * 40), ('run_attempt', 2), ('job_id', 0)):
            self.provenance = {**original, key: value}
            with self.subTest(key=key), self.assertRaises(V.AuditError):
                V.validate(self.packet, self.provenance, self.raw)

    def test_duplicate_nonfinite_and_unknown_fields_rejected(self):
        for raw in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":1e999}'):
            with self.assertRaises(V.AuditError):
                V.strict_json(raw)
        self.packet['unregistered_claim'] = True
        self.reject_changed_packet()


if __name__ == '__main__':
    unittest.main()
