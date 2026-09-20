"""Source-valid new proof weakenings must fail registered statement checks."""
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

import check_lean_v13 as kernel

COVERAGE = {}


class KernelGuardTests(unittest.TestCase):
    def test_registered_statement_types_reject_source_valid_mutants(self):
        original = {path.name: path.read_text() for path in kernel.SOURCES}
        mutations = [{name: "import Std\n" for name in original}]
        changed = dict(original)
        changed["LoopMonoidalV13.lean"], count = re.subn(
            r"theorem no_braiding :[\s\S]*?(?=\nend LoopHom)",
            "theorem no_braiding : True := True.intro\n",
            changed["LoopMonoidalV13.lean"])
        self.assertEqual(count, 1)
        mutations.append(changed)
        changed = dict(original)
        changed["InterchangeV13.lean"], count = re.subn(
            r"theorem no_any_tensor[\s\S]*?(?=\n/-- Clean scalar control:)",
            "theorem no_any_tensor : True := True.intro\n",
            changed["InterchangeV13.lean"])
        self.assertEqual(count, 1)
        mutations.append(changed)
        rejected = 0
        for index, mutation in enumerate(mutations):
            with self.subTest(mutation=index), tempfile.TemporaryDirectory(prefix="v13-kernel-hostile-") as directory:
                root = Path(directory)
                paths = tuple(root / path.name for path in kernel.SOURCES)
                for path in paths:
                    path.write_text(mutation[path.name])
                with patch.object(kernel, "ROOT", root), patch.object(kernel, "SOURCES", paths):
                    with self.assertRaises(kernel.InvalidProof) as failure:
                        kernel.evaluate()
                    self.assertEqual(failure.exception.stage, "AUDIT")
                    rejected += 1
        self.assertEqual(rejected, 3)
        COVERAGE["kernel_registration_rejections"] = rejected


if __name__ == "__main__":
    unittest.main()
