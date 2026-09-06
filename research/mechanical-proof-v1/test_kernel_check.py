"""Protocol-unit tests; actual kernel commissioning is a separate native run."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from kernel_check import check_staged
from proof_check import stage_candidate

VERSION = 'Lean (version 4.33.1, x86_64-unknown-linux-gnu, commit 819816b2e0a3bf405af45ae5c7af2491d8f5bee6, Release)\n'


def completed(stdout='', returncode=0, stderr=''):
    return {'terminal': 'COMPLETED', 'returncode': returncode, 'stdout': stdout,
            'stderr': stderr, 'cleanup': {'reaped': True, 'group_absent': True}}


class KernelProtocolTests(unittest.TestCase):
    def staged(self, temp):
        return stage_candidate(['const', 0], Path(temp) / 'attempt')

    def test_changed_source_refused_before_dispatch(self):
        with tempfile.TemporaryDirectory() as temp:
            stage = self.staged(temp)
            (Path(stage['directory']) / 'Target.lean').write_text('def statement : Prop := True')
            with patch('kernel_check.run_isolated') as runner:
                result = check_staged(stage, Path(temp), [])
            self.assertEqual(result['terminal'], 'CANNOT_CHECK')
            runner.assert_not_called()

    def test_missing_or_wrong_version_is_not_invalid_proof(self):
        for first in [{'terminal': 'CANNOT_CHECK', 'returncode': None}, completed('Lean 4.19.0')]:
            with self.subTest(first=first), tempfile.TemporaryDirectory() as temp:
                with patch('kernel_check.run_isolated', return_value=first):
                    result = check_staged(self.staged(temp), Path(temp), [])
                self.assertEqual(result['terminal'], 'CANNOT_CHECK')

    def test_forged_target_metadata_is_refused_before_dispatch(self):
        with tempfile.TemporaryDirectory() as temp:
            stage = self.staged(temp)
            stage['formal_target'] = 'False'
            with patch('kernel_check.run_isolated') as runner:
                result = check_staged(stage, Path(temp), [])
            runner.assert_not_called()
            self.assertEqual(result['terminal'], 'CANNOT_CHECK')

    def test_compiler_failure_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as temp:
            outputs = [completed(VERSION), completed('', 1, 'dependency unavailable')]
            with patch('kernel_check.run_isolated', side_effect=outputs):
                result = check_staged(self.staged(temp), Path(temp), [])
            self.assertEqual(result['terminal'], 'CANNOT_CHECK')

    def test_incomplete_timeout_or_output_limit_cannot_pass(self):
        for terminal in ['TIMEOUT', 'OUTPUT_LIMIT', 'REFUSED']:
            with self.subTest(terminal=terminal), tempfile.TemporaryDirectory() as temp:
                with patch('kernel_check.run_isolated', return_value={'terminal': terminal, 'returncode': 0}):
                    result = check_staged(self.staged(temp), Path(temp), [])
                self.assertEqual(result['terminal'], 'CANNOT_CHECK')

    def test_bad_candidate_error_is_rejected_but_wrapper_error_cannot_check(self):
        for error, expected in [('Candidate.lean:4:2: error: type mismatch', 'REJECTED'),
                                ('Candidate.lean:4:2: error: maximum recursion depth reached', 'CANNOT_CHECK'),
                                ('Candidate.lean:4:2: error: internal exception', 'CANNOT_CHECK'),
                                ('bwrap: cannot mount runtime', 'CANNOT_CHECK')]:
            with self.subTest(error=error), tempfile.TemporaryDirectory() as temp:
                outputs = [completed(VERSION), completed(), completed(), completed(error, 1)]
                with patch('kernel_check.run_isolated', side_effect=outputs):
                    result = check_staged(self.staged(temp), Path(temp), [])
                self.assertEqual(result['terminal'], expected)

    def test_successful_exit_without_axiom_report_is_incomplete(self):
        with tempfile.TemporaryDirectory() as temp:
            outputs = [completed(VERSION), completed(), completed(), completed()]
            with patch('kernel_check.run_isolated', side_effect=outputs):
                result = check_staged(self.staged(temp), Path(temp), [])
            self.assertEqual(result['terminal'], 'CANNOT_CHECK')


if __name__ == '__main__': unittest.main()
