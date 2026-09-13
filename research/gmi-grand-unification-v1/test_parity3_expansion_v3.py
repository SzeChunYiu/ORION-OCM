"""Frozen expansion controls. These tests never collect timing measurements."""
import ast
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'nn_nonnn_point_parity3_experiment_v3.py'
SPEC = importlib.util.spec_from_file_location('parity_expansion_v3', SOURCE)
M = importlib.util.module_from_spec(SPEC)
exec(compile(SOURCE.read_bytes(), str(SOURCE), 'exec'), M.__dict__)
IDS = list(M.CANDIDATES)
KEYS = ('python_opcode_count_per_full_domain_sweep', 'wall_block_ns', 'process_block_ns')


def box(a, b=None):
    return {k: [a, a if b is None else b] for k in KEYS}


class ExpansionV3Tests(unittest.TestCase):
    def test_exact_truth_table_and_shared_sum_proof(self):
        for x, y in zip(M.INPUTS, M.EXPECTED):
            s = sum(x)
            self.assertEqual(int(int(s >= 1) - int(s >= 2) + int(s >= 3) >= 1), y)
            for row in M.CANDIDATES.values():
                got = row['fn'](x)
                self.assertIs(type(got), int)
                self.assertEqual(got, y)

    def test_old_candidates_are_ast_identical(self):
        old = ast.parse((HERE / 'nn_nonnn_point_parity3_experiment_v2.py').read_text())
        new = ast.parse(SOURCE.read_text())
        for name in ('neural_threshold_parity3', 'non_neural_xor_parity3'):
            a = next(n for n in old.body if isinstance(n, ast.FunctionDef) and n.name == name)
            b = next(n for n in new.body if isinstance(n, ast.FunctionDef) and n.name == name)
            self.assertEqual(ast.dump(a), ast.dump(b))

    def test_candidate_hash_and_family_drift_rejected(self):
        p = json.loads(M.PREREG.read_text())
        M.validate_preregistration(p)
        for field, value in (('ast_sha256', '0' * 64), ('family', 'NEURAL'),
                             ('implementation', 'unknown')):
            bad = copy.deepcopy(p)
            bad['candidates'][1][field] = value
            with self.subTest(field=field), self.assertRaises(M.MeasurementIntegrityError):
                M.validate_preregistration(bad)

    def test_complete_balanced_order(self):
        orders = [M.candidate_order(i) for i in range(32)]
        for order in orders:
            self.assertEqual(set(order), set(IDS))
        for cid in IDS:
            self.assertEqual([sum(order[pos] == cid for order in orders) for pos in range(4)], [8] * 4)
        self.assertEqual(len({tuple(o) for o in orders}), 8)

    def test_same_family_frontier_does_not_invent_unique_winner(self):
        got = M.adjudicate({IDS[0]: box(10), IDS[1]: box(1, 3), IDS[2]: box(10), IDS[3]: box(2, 4)})
        self.assertEqual(got['frontier_candidate_ids'], [IDS[1], IDS[3]])
        self.assertEqual(got['terminal'], 'DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE')
        self.assertEqual(got['winner_candidate_id'], 'NONE')

    def test_neural_expansion_can_reopen_old_family_winner(self):
        got = M.adjudicate({IDS[0]: box(10), IDS[1]: box(1, 3), IDS[2]: box(2, 4), IDS[3]: box(10)})
        self.assertEqual(got['frontier_candidate_ids'], [IDS[1], IDS[2]])
        self.assertEqual(got['terminal'], 'UNDECIDED_FROM_CURRENT_EVIDENCE')

    def test_family_neutral_neural_winner(self):
        boxes = {cid: box(9) for cid in IDS}
        boxes[IDS[2]] = box(1)
        got = M.adjudicate(boxes)
        self.assertEqual(got['terminal'], 'DERIVED_NEURAL_AT_REGISTERED_SCOPE')
        self.assertEqual(got['winner_candidate_id'], IDS[2])

    def test_equal_boxes_keep_both_families(self):
        got = M.adjudicate({cid: box(1) for cid in IDS})
        self.assertEqual(got['frontier_candidate_ids'], IDS)
        self.assertEqual(got['terminal'], 'UNDECIDED_FROM_CURRENT_EVIDENCE')

    def test_incomplete_or_malformed_evidence_is_rejected(self):
        good = {cid: box(1) for cid in IDS}
        bads = [{cid: good[cid] for cid in IDS[:-1]}]
        for interval in ([True, 2], [0, 1], [2, 1], [1.0, 2.0], [1], [1, float('inf')]):
            bad = copy.deepcopy(good)
            bad[IDS[0]][KEYS[0]] = interval
            bads.append(bad)
        bad = copy.deepcopy(good)
        del bad[IDS[0]][KEYS[1]]
        bads.append(bad)
        for bad in bads:
            with self.assertRaises(M.MeasurementIntegrityError):
                M.adjudicate(bad)

    def test_rerun_and_non_main_execution_are_rejected(self):
        env = {'GITHUB_ACTIONS': 'true', 'GITHUB_REF': 'refs/heads/main',
               'GITHUB_EVENT_NAME': 'push', 'GITHUB_RUN_ATTEMPT': '1',
               'GITHUB_SHA': 'a' * 40, 'GITHUB_RUN_ID': '1', 'RUNNER_OS': 'Linux'}
        for key, value in (('GITHUB_RUN_ATTEMPT', '2'), ('GITHUB_REF', 'refs/heads/other'),
                           ('GITHUB_EVENT_NAME', 'pull_request'), ('GITHUB_SHA', '')):
            with patch.dict(M.os.environ, {**env, key: value}, clear=True):
                self.assertFalse(M.protocol_environment_valid()[0])

    def test_bad_environment_does_not_warm_or_time(self):
        with patch.object(M, 'protocol_environment_valid', return_value=(False, ['test'])), \
             patch.object(M, 'warmup') as warm, patch.object(M, 'timed_block') as timed:
            result = M.run_experiment()
        warm.assert_not_called()
        timed.assert_not_called()
        self.assertEqual(result['terminal'], 'INVALID_RECEIPT_OR_PROTOCOL_VIOLATION')

    def test_instrument_failure_stops_timing(self):
        with patch.object(M, 'protocol_environment_valid', return_value=(True, [])), \
             patch.object(M, 'warmup', return_value=20000), \
             patch.object(M, 'instrumentation_preflight', side_effect=M.MeasurementIntegrityError('bad trace')), \
             patch.object(M, 'timed_block') as timed:
            result = M.run_experiment()
        timed.assert_not_called()
        self.assertIs(result['instrumentation_gate_pass'], False)

    @unittest.skipUnless(sys.implementation.name == 'cpython' and sys.version_info[:2] == (3, 12), 'CPython 3.12 instrument')
    def test_complete_new_candidate_traces_without_timing(self):
        with patch.object(M, 'timed_block', side_effect=AssertionError('timing forbidden')):
            result = M.deterministic_self_test()
        self.assertEqual(set(result['opcode_counts']), set(IDS))
        self.assertTrue(all(v > 0 for v in result['opcode_counts'].values()))
        self.assertIs(result['protected_timing_measurement_executed'], False)


if __name__ == '__main__':
    unittest.main()
