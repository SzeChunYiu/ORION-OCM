from pathlib import Path
import shutil
import tempfile
import unittest

import replay


class CustodyTests(unittest.TestCase):
    def test_complete_inventory_verifies(self):
        self.assertEqual(len(replay.verify()["files"]), 39)

    def test_missing_changed_or_forged_source_is_refused(self):
        for mutation in ("missing", "bytes", "inventory", "adapter", "symlink"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as td:
                copy = Path(td) / "package"
                shutil.copytree(replay.PACKAGE, copy)
                manifest = replay.verify(copy)
                source = copy / manifest["files"][0]["archive_path"]
                if mutation == "missing": source.unlink()
                if mutation == "bytes": source.write_bytes(source.read_bytes() + b"\n")
                if mutation == "inventory":
                    path = copy / "MANIFEST_V1.json"
                    path.write_bytes(path.read_bytes() + b"\n")
                if mutation == "adapter":
                    (copy / manifest["adapter"]["path"]).write_text("# not the tested adapter\n")
                if mutation == "symlink":
                    data = source.read_bytes(); source.unlink()
                    other = Path(td) / "elsewhere"; other.write_bytes(data)
                    source.symlink_to(other)
                with self.assertRaises(replay.CannotCheck): replay.verify(copy)


if __name__ == "__main__":
    unittest.main()
