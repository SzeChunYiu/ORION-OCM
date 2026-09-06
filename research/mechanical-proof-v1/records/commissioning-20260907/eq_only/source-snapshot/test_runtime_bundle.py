"""File-boundary tests, not evidence that a fixture is an executable runtime."""
import tempfile
import unittest
from pathlib import Path
from runtime_bundle import copy_python, tree_manifest, verify_tree


class RuntimeBundleTests(unittest.TestCase):
    def seed(self, temp):
        prefix = Path(temp) / 'source'
        (prefix / 'bin').mkdir(parents=True)
        (prefix / 'bin/python3.11').write_bytes(b'fixture interpreter')
        std = prefix / 'lib/python3.11'
        (std / 'site-packages').mkdir(parents=True)
        (std / 'site-packages/unregistered_teacher.py').write_text('forbidden fixture')
        (std / '__pycache__').mkdir()
        (std / '__pycache__/stale.pyc').write_bytes(b'unbound bytecode')
        (std / 'json.py').write_text('registered fixture')
        return prefix

    def test_copied_boundary_excludes_site_packages_and_bytecode(self):
        with tempfile.TemporaryDirectory() as temp:
            prefix = self.seed(temp)
            dest = Path(temp) / 'copy'
            record = copy_python(prefix, dest)
            self.assertTrue((dest / 'bin/python3.11').is_file())
            self.assertTrue((dest / 'lib/python3.11/json.py').is_file())
            self.assertFalse((dest / 'lib/python3.11/site-packages').exists())
            self.assertFalse((dest / 'lib/python3.11/__pycache__').exists())
            verify_tree(dest, record['files'])

    def test_extra_and_modified_files_invalidate_registered_tree(self):
        with tempfile.TemporaryDirectory() as temp:
            prefix = self.seed(temp)
            dest = Path(temp) / 'copy'
            record = copy_python(prefix, dest)
            extra = dest / 'extra.py'
            extra.write_text('new module')
            with self.assertRaises(ValueError): verify_tree(dest, record['files'])
            extra.unlink()
            (dest / 'lib/python3.11/json.py').write_text('altered')
            with self.assertRaises(ValueError): verify_tree(dest, record['files'])

    def test_escaping_link_never_enters_the_runtime(self):
        with tempfile.TemporaryDirectory() as temp:
            prefix = self.seed(temp)
            outside = Path(temp) / 'outside'
            outside.write_text('not registered')
            (prefix / 'lib/python3.11/link.py').symlink_to(outside)
            with self.assertRaises(ValueError): copy_python(prefix, Path(temp) / 'copy')

    def test_manifest_binds_internal_links_and_detects_retargeting(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'one').write_bytes(b'one')
            (root / 'two').write_bytes(b'two')
            (root / 'link').symlink_to('one')
            manifest = tree_manifest(root)
            verify_tree(root, manifest)
            (root / 'link').unlink()
            (root / 'link').symlink_to('two')
            with self.assertRaises(ValueError): verify_tree(root, manifest)


if __name__ == '__main__': unittest.main()
