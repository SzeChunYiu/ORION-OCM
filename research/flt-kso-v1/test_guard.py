import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from guard import check_imports, require_executable_package
from substrate import Refusal, build_graph, stage_challenge
from test_substrate import fixture

class GuardHostiles(unittest.TestCase):
    def test_hidden_import_rejected(self):
        for source in ('import Theorems.Thm_hidden\ntheorem x : True := by trivial',
                       'import P2M.Sol.S_hidden\ntheorem x : True := by trivial'):
            with self.assertRaises(Refusal):check_imports(source)
    def test_disallowed_shortcuts_rejected(self):
        for body in ('axiom x : False','theorem x : False := by sorry',
                     'theorem x : True := by native_decide'):
            with self.assertRaises(Refusal):check_imports('import Init\n'+body)
    def test_clean_data_never_becomes_unconfined_execution(self):
        with tempfile.TemporaryDirectory() as d:
            public=Path(d)/'public';private=Path(d)/'private'
            stage_challenge(build_graph(fixture(),expected_count=2),['b'],'b','R2',public,private)
            with self.assertRaises(Refusal) as captured:require_executable_package(public,(private,))
            self.assertEqual(captured.exception.terminal,'CANNOT_CHECK_ISOLATION_AND_BOUNDARY')
            (public/'hidden.lean').write_text('secret')
            with self.assertRaises(Refusal) as captured:require_executable_package(public,(private,))
            self.assertEqual(captured.exception.terminal,'SOLUTION_LEAKAGE_DETECTED')
    def test_duplicate_json_key_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d)/'PUBLIC.json').write_text('{"schema":"a","schema":"b"}')
            with self.assertRaises(Refusal):require_executable_package(Path(d))

if __name__=='__main__':unittest.main()
