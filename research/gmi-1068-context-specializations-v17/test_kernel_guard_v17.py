"""Source-valid proof weakenings must fail exact registered statement checks."""
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

import check_lean_v17 as kernel

COVERAGE = {}


class KernelGuardTests(unittest.TestCase):
    def test_registered_statement_types_reject_source_valid_mutants(self):
        original = {path.name: path.read_text() for path in kernel.SOURCES}
        mutations = [{name: "import Std\n" for name in original}]
        changes = [
            [("ProductContextsV17.lean",
              r"theorem shared_defined[\s\S]*?(?=\ntheorem shared_projection)",
              "theorem shared_defined : True := True.intro\n")],
            [("ViabilityV17.lean",
              r"theorem trajectory_to_viable[\s\S]*?(?=\ntheorem viable_iff_trajectory)",
              "theorem trajectory_to_viable : True := True.intro\n"),
             ("ViabilityV17.lean",
              r"theorem viable_iff_trajectory[\s\S]*?(?=\nnoncomputable def viabilityContext)",
              "theorem viable_iff_trajectory : True := True.intro\n")],
        ]
        for replacements in changes:
            changed = dict(original)
            for filename, pattern, replacement in replacements:
                changed[filename], count = re.subn(pattern, replacement, changed[filename])
                self.assertEqual(count, 1)
            mutations.append(changed)
        rejected = 0
        for index, mutation in enumerate(mutations):
            with self.subTest(mutation=index), tempfile.TemporaryDirectory(prefix="v17-kernel-hostile-") as directory:
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
