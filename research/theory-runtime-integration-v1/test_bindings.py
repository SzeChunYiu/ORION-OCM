"""Known-answer and drift controls for the source-bound integration packet."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("integration_check", HERE / "check.py")
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)


class BindingChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="ocm-intake-controls-")
        root = Path(cls.temporary.name)
        sources = {"runtime": HERE.parents[1],
                   "theory": Path(os.environ.get("OCM_THEORY_ROOT", str(HERE.parents[2] / "ORION-V2")))}
        cls.roots = {}
        for role, source in sources.items():
            target = root / role
            subprocess.run(["git", "clone", "-q", "--shared", "--no-checkout", str(source), str(target)], check=True)
            subprocess.run(["git", "-C", str(target), "checkout", "-q", C.ANCHORS[role]], check=True)
            cls.roots[role] = target
        cls.original = json.loads((HERE / "MANIFEST_V1.json").read_text())

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def setUp(self):
        self.manifest = copy.deepcopy(self.original)

    def rejected(self, status, **kwargs):
        with self.assertRaises(C.CheckError) as caught:
            C.verify_bindings(self.manifest, kwargs.pop("roots", self.roots), **kwargs)
        self.assertEqual(caught.exception.status, status)

    def test_real_packet_keeps_authority_separate(self):
        result = C.verify_bindings(self.manifest, self.roots)
        self.assertEqual(result["status"], "SOURCE_BINDINGS_VERIFIED")
        self.assertEqual(result["authority"]["runtime_adoption"], "NOT_GRANTED")
        self.assertEqual(result["authority"]["M12"], "PROTECTED_REEVALUATION_REQUIRED")

    def test_other_revision_cannot_reuse_packet(self):
        self.manifest["repositories"]["runtime"]["commit"] = "0" * 40
        self.rejected("REJECTED")

    def test_well_formed_wrong_digest_is_not_source_verification(self):
        row = self.manifest["repositories"]["theory"]["files"][C.THEORY_PREFIX + "THEORY.md"]
        row["sha256"] = "0" * 64
        self.rejected("REJECTED")

    def test_missing_file_binding_cannot_pass(self):
        self.manifest["repositories"]["runtime"]["files"].pop("src/ocm/learning/methods.py")
        self.rejected("REJECTED")

    def test_scope_cannot_be_broadened(self):
        self.manifest["rows"][0]["source_scope"] += "\nThis solves every mathematical problem."
        self.rejected("REJECTED")

    def test_parent_result_cannot_be_promoted(self):
        self.manifest["rows"][0]["parent_status"] = "OCM_SUPERIORITY_PROVED"
        self.rejected("REJECTED")

    def test_unknown_theorem_status_cannot_pass(self):
        self.manifest["rows"][0]["source_status"] = "SUPPORTED"
        self.rejected("REJECTED")

    def test_mapping_to_different_runtime_component_is_not_parity(self):
        self.manifest["rows"][0]["consumer_paths"] = ["src/ocm/science/finite_identification.py"]
        self.rejected("REJECTED")

    def test_current_runtime_drift_reopens(self):
        path = self.roots["runtime"] / "src/ocm/learning/methods.py"
        before = path.read_bytes()
        try:
            path.write_bytes(before + b"\n# changed runtime control\n")
            self.assertNotEqual(path.read_bytes(), before)
            self.rejected("REVALIDATION_REQUIRED")
        finally:
            path.write_bytes(before)

    def test_missing_theory_is_cannot_check(self):
        path = self.roots["theory"] / (C.THEORY_PREFIX + "THEORY.md")
        before = path.read_bytes()
        try:
            path.unlink()
            self.assertFalse(path.exists())
            self.rejected("CANNOT_CHECK")
        finally:
            path.write_bytes(before)

    def test_extra_importable_source_reopens(self):
        path = self.roots["runtime"] / "src/ocm/extra_source_control.py"
        try:
            path.write_text("VALUE = 1\n")
            self.rejected("REVALIDATION_REQUIRED")
        finally:
            path.unlink()

    def test_unrelated_note_does_not_reopen_runtime(self):
        path = self.roots["runtime"] / "unrelated-note.txt"
        try:
            path.write_text("A note outside the bound code.\n")
            self.assertEqual(C.verify_bindings(self.manifest, self.roots)["status"], "SOURCE_BINDINGS_VERIFIED")
        finally:
            path.unlink()

    def test_revoked_row_reopens_without_editing_history(self):
        before = copy.deepcopy(self.manifest)
        self.rejected("REVALIDATION_REQUIRED", revoked=("M3",))
        self.assertEqual(self.manifest, before)

    def test_unknown_revocation_is_not_ignored(self):
        self.rejected("CANNOT_CHECK", revoked=("unknown",))

    def test_unknown_authority_fields_are_rejected(self):
        self.manifest["authority"]["self_approved"] = True
        self.rejected("REJECTED")

    def test_missing_repository_is_not_an_empty_success(self):
        self.rejected("CANNOT_CHECK", roots={"runtime": self.roots["runtime"]})

    def test_reference_paths_are_canonical(self):
        for relative in ("../outside", "/absolute", "a//b", "./file", "a\\b"):
            with self.subTest(path=relative), self.assertRaises(C.CheckError):
                C.safe_path(self.roots["runtime"], relative)

    def test_execution_copy_uses_only_bound_sources_without_caches(self):
        cache = self.roots["runtime"] / "src/ocm/__pycache__/unused-control.pyc"
        cache.parent.mkdir(exist_ok=True)
        cache.write_bytes(b"not executable; copy-selection control")
        try:
            with tempfile.TemporaryDirectory() as temporary:
                clean = C.prepare_clean_sources(self.manifest, self.roots, Path(temporary))
                self.assertFalse(list((clean["runtime"] / "src").rglob("*.pyc")))
                self.assertEqual((clean["runtime"] / "src/ocm/learning/methods.py").read_bytes(),
                                 (self.roots["runtime"] / "src/ocm/learning/methods.py").read_bytes())
                with self.assertRaises(FileExistsError):
                    C.prepare_clean_sources(self.manifest, self.roots, Path(temporary))
        finally:
            cache.unlink()

    def test_json_unknown_shape_is_rejected(self):
        self.manifest["rows"] = {"M1": "passed"}
        self.rejected("REJECTED")


if __name__ == "__main__":
    unittest.main()
