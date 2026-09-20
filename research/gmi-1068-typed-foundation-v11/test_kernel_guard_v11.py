"""Actual source-valid corruptions must fail the explicit theorem-type audit."""
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

import check_lean_v11 as kernel

COVERAGE = {}


class KernelGuardTests(unittest.TestCase):
    def test_registered_statement_types_reject_source_valid_mutants(self):
        original = {p.name: p.read_text() for p in kernel.SOURCES}
        mutations = []
        mutations.append({name: "import Std\n" for name in original})
        changed = dict(original)
        changed["QuotientPathsV11.lean"], replacements = re.subn(
            r"def presentationIso[\s\S]*?(?=\nend TypedPathsV11)",
            "def presentationIso : True := True.intro\n",
            changed["QuotientPathsV11.lean"])
        self.assertEqual(replacements, 1)
        mutations.append(changed)
        changed = dict(original)
        changed["RecoverabilityV9.lean"], replacements = re.subn(
            r"theorem actual_ranking_reversal[\s\S]*?(?=\ntheorem actual_admission_difference)",
            "theorem actual_ranking_reversal : True := True.intro\n",
            changed["RecoverabilityV9.lean"])
        self.assertEqual(replacements, 1)
        mutations.append(changed)
        rejected = 0
        for index, mutation in enumerate(mutations):
            with self.subTest(mutation=index), tempfile.TemporaryDirectory(prefix="v11-kernel-hostile-") as directory:
                root = Path(directory)
                paths = tuple(root / p.name for p in kernel.SOURCES)
                for path in paths:
                    path.write_text(mutation[path.name])
                with patch.object(kernel, "ROOT", root), patch.object(kernel, "SOURCES", paths):
                    with self.assertRaises(kernel.InvalidProof) as failure:
                        kernel.evaluate()
                    # Reaching AUDIT proves all three mutated source modules compiled.
                    self.assertEqual(failure.exception.stage, "AUDIT")
                    rejected += 1
        self.assertEqual(rejected, 3)
        COVERAGE["kernel_registration_rejections"] = rejected


if __name__ == "__main__":
    unittest.main()
