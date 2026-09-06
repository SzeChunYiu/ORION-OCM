import tempfile
from pathlib import Path
import unittest
from native import EqualityTask, construct
from kernel import check


class KernelControls(unittest.TestCase):
    def setUp(self):
        self.task = EqualityTask(('x', 'y'), (('x', 'y'),), ('y', 'x'))
        self.proof = construct(self.task)['proof']

    def test_absent_toolchain_is_not_mock_success(self):
        row = check(self.task, self.proof)
        self.assertEqual(row['terminal'], 'CANNOT_CHECK_LEAN_ARCHIVE_UNAVAILABLE')
        self.assertEqual(row['lean_checker_calls'], 0)
        self.assertFalse(row['fresh_kernel'])

    def test_changed_toolchain_fails_before_execution(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'fake.tar.zst'; p.write_bytes(b'not a Lean archive')
            row = check(self.task, self.proof, p)
            self.assertEqual(row['terminal'], 'CHECKER_OR_ENVIRONMENT_MISMATCH')
            self.assertEqual(row['processes'], [])

    def test_injected_axiom_sorry_native_decide_are_not_ast(self):
        for forbidden in ('axiom', 'sorry', 'native_decide', 'import', '#eval'):
            with self.assertRaises(ValueError):
                check(self.task, [forbidden])


if __name__ == '__main__':
    unittest.main()
