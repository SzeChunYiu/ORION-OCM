"""Source-valid proof weakenings must fail exact registered statement checks."""
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

import check_lean_v14 as kernel

COVERAGE = {}


class KernelGuardTests(unittest.TestCase):
    def test_registered_statement_types_reject_source_valid_mutants(self):
        original = {path.name: path.read_text() for path in kernel.SOURCES}
        mutations = [{name: "import Std\n" for name in original}]
        for filename, pattern, replacement in (
            ("SupportV14.lean", r"theorem support_comp[\s\S]*?(?=\ntheorem support_embed)",
             "theorem support_comp : True := True.intro\n"),
            ("RationalModelV14.lean", r"theorem support_probability_loss[\s\S]*?(?=\nend StochasticV14.RationalModel)",
             "theorem support_probability_loss : True := True.intro\n"),
        ):
            changed = dict(original)
            changed[filename], count = re.subn(pattern, replacement, changed[filename])
            self.assertEqual(count, 1)
            mutations.append(changed)
        rejected = 0
        for index, mutation in enumerate(mutations):
            with self.subTest(mutation=index), tempfile.TemporaryDirectory(prefix="v14-kernel-hostile-") as directory:
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
