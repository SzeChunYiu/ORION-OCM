"""Challenge custody is independent of the candidate's claimed type."""
import tempfile
import unittest
from pathlib import Path

from proof_check import stage_candidate

HERE = Path(__file__).resolve().parent


class StageTests(unittest.TestCase):
    def test_fixed_target_and_closed_term_are_staged_separately(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'attempt'
            record = stage_candidate(['const', 0], target)
            self.assertTrue(record['target_sha256'])
            text = (target / 'Candidate.lean').read_text()
            self.assertIn('theorem constructed : F0Target.statement :=', text)
            self.assertIn('(@Eq.{1})', text)
            self.assertIn('def proposed :=', text)
            self.assertIn(':= @proposed', text)
            self.assertNotIn('Composition', text)
            self.assertEqual(set(p.name for p in target.iterdir()),
                             {'Foundation.lean', 'Target.lean', 'Candidate.lean', 'candidate.json'})

    def test_refuses_replacement_of_independent_target(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'source'
            root.mkdir()
            (root / 'Target.lean').write_text('def statement : Prop := True\n')
            with self.assertRaisesRegex(ValueError, 'target'):
                stage_candidate(['const', 0], Path(temp) / 'attempt', root=root)

    def test_invalid_input_does_not_create_artifacts(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'attempt'
            with self.assertRaises(ValueError):
                stage_candidate(['const', 'sorryAx'], target)
            self.assertFalse(target.exists())

    def test_existing_attempt_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'attempt'
            stage_candidate(['const', 0], target)
            before = (target / 'Candidate.lean').read_bytes()
            with self.assertRaises(FileExistsError):
                stage_candidate(['const', 1], target)
            self.assertEqual((target / 'Candidate.lean').read_bytes(), before)

    def test_target_symlink_is_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'source'
            root.mkdir()
            (root / 'Target.lean').symlink_to(HERE / 'Target.lean')
            with self.assertRaises(ValueError):
                stage_candidate(['const', 0], Path(temp) / 'attempt', root=root)


if __name__ == '__main__':
    unittest.main()
