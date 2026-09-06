import json
from pathlib import Path
import tempfile
import unittest
from graph import imports, signature, inventory
from native import EqualityTask
from seal import seal, export_anthropic_signature, isolation_probe


class SealControls(unittest.TestCase):
    def test_nested_comments_and_strings_do_not_import(self):
        source = '/- import Bad /- import Worse -/ -/\nimport Theorems.Thm_a\ndef x := "import Secret"\n'
        self.assertEqual(imports(source), ('Theorems.Thm_a',))

    def test_multiline_signature_with_default_binder(self):
        text = 'import P2M.Sol.S_t\ntheorem t\n (n : Nat := 0)\n : n = n := by rfl\n'
        got = signature(text)
        self.assertEqual(got['signature'], 'theorem t\n (n : Nat := 0)\n : n = n')
        self.assertNotIn('by rfl', got['signature'])
        with self.assertRaisesRegex(ValueError, 'CANNOT_CHECK'):
            export_anthropic_signature(got)

    def test_unsupported_signatures_fail_closed(self):
        for text in ('theorem t : True', 'theorem a : True := x\ntheorem b : True := y',
                     'theorem t : let x := True; x := z', '/- unclosed'):
            with self.assertRaises(ValueError): signature(text)

    def test_graph_comes_from_solution_imports_not_wrapper(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); (root/'Theorems').mkdir(); (root/'P2M/Sol').mkdir(parents=True)
            for key in ('a', 'b'):
                (root/f'Theorems/Thm_{key}.lean').write_text(f'import P2M.Sol.S_{key}\ntheorem {key} : True := trivial\n')
                (root/f'P2M/Sol/S_{key}.lean').write_text('import Theorems.Thm_a\n' if key == 'b' else '')
            row = inventory(root, expected_count=2)
            self.assertEqual(row['terminal'], 'SOURCE_DAG_INVENTORIED')
            self.assertEqual(row['nodes']['b']['dependencies'], ['a'])
            self.assertEqual(row['nodes']['a']['dependencies'], [])

    def test_public_never_copies_private_text_and_overlap_refused(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); private = root/'private.json'; private.write_text('{"solution":"SECRET_PROOF"}')
            task = EqualityTask(('x',), (), ('x', 'x'))
            row = seal(task, root/'public', private)
            public = (root/'public/challenge.json').read_text()
            self.assertNotIn('SECRET_PROOF', public)
            self.assertEqual(json.loads(public)['imports'], [])
            self.assertEqual(row['physical_isolation'], 'NOT_YET_CHECKED')
            with self.assertRaises(ValueError): seal(task, root, private)
            with self.assertRaises(FileExistsError): seal(task, root/'public', private)
            self.assertIn(isolation_probe(root/'public', private)['terminal'],
                          ('CANNOT_CHECK_ISOLATION_TOOL_UNAVAILABLE', 'CANNOT_CHECK_ISOLATION',
                           'PRIVATE_PATH_NOT_MOUNTED_AT_PROBE_SCOPE'))


if __name__ == '__main__': unittest.main()
