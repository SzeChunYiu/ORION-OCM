"""Source-valid proof weakenings must fail the registered statement audit."""
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

import check_lean_v12 as kernel

COVERAGE = {}


class KernelGuardTests(unittest.TestCase):
    def test_registered_statement_types_reject_source_valid_mutants(self):
        original = {path.name: path.read_text() for path in kernel.SOURCES}
        mutations = [{name: "import Std\n" for name in original}]
        changed = dict(original)
        changed["ScalarizationV12.lean"], count = re.subn(
            r"theorem positive_minimizer_efficient[\s\S]*?(?=\nend ScalarV12)",
            "theorem positive_minimizer_efficient : True := True.intro\n",
            changed["ScalarizationV12.lean"])
        self.assertEqual(count, 1)
        mutations.append(changed)
        changed = dict(original)
        changed["ScalarLawsV12.lean"], count = re.subn(
            r"instance intScalar[\s\S]*?(?=\nend ScalarV12)",
            "def intScalar : True := True.intro\n",
            changed["ScalarLawsV12.lean"])
        self.assertEqual(count, 1)
        mutations.append(changed)
        rejected = 0
        for index, mutation in enumerate(mutations):
            with self.subTest(mutation=index), tempfile.TemporaryDirectory(prefix="v12-kernel-hostile-") as directory:
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
