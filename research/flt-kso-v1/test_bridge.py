"""Mocked boundary tests never count as mathematics outcomes."""
import tempfile
import unittest
from native import EqualityTask
from bridge import run_ocm


class BridgeControls(unittest.TestCase):
    def test_missing_kernel_does_not_admit_truth(self):
        task = EqualityTask(('x', 'y'), (('x', 'y'),), ('y', 'x'))
        with tempfile.TemporaryDirectory() as d:
            row = run_ocm(task, {'identity': 'development-no-kernel'}, d, None, 32)
            self.assertEqual(row['terminal'], 'CANNOT_CHECK_KERNEL_UNAVAILABLE')
            self.assertEqual(row['truth_liveness'], 'UNKNOWN')
            self.assertEqual(row['new_theorems_admitted'], 0)
            self.assertTrue(row['restart_identical'])
            self.assertGreater(len(row['construction']['events']), 0)

    def test_forged_environment_and_source_receipts_are_not_accepted(self):
        from native import identity, render
        from bridge import identity_source
        task = EqualityTask(('x', 'y'), (('x', 'y'),), ('y', 'x'))
        environment = {'identity': 'test-only-mock'}
        for field in ('environment_id', 'source_sha256', 'statement_id'):
            def fake(t, proof):
                receipt = {'terminal': 'KERNEL_ACCEPTED',
                           'environment_id': identity(environment),
                           'source_sha256': identity_source(render(t, proof)),
                           'statement_id': t.statement_id}
                receipt[field] = 'stale-or-forged'
                return receipt
            with tempfile.TemporaryDirectory() as d:
                row = run_ocm(task, environment, d, fake, 32)
                self.assertEqual(row['terminal'], 'CHECKER_OR_ENVIRONMENT_MISMATCH')
                self.assertEqual(row['new_theorems_admitted'], 0)
                self.assertEqual(row['truth_liveness'], 'UNKNOWN')


if __name__ == '__main__':
    unittest.main()
