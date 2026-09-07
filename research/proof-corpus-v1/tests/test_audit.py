import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from helpers import api, wrapper, solution
from git_fixture import repository

HERE = Path(__file__).resolve().parents[1]


def files():
    return {"Theorems/Thm_A.lean": wrapper(), "P2M/Sol/S_A.lean": solution(),
            "Definitions/Context.lean": "def contextual : Nat := 1\n",
            "P2M/Util.lean": "-- evaluator context only\n",
            "lean-toolchain": "leanprover/lean4:v4.33.1\n",
            "lake-manifest.json": json.dumps({"packages": [{"name": "mathlib",
                "rev": "db584cd6d46c92f209a44c0f1c829460d327499d"}]})}


class AuditControls(unittest.TestCase):
    def test_tiny_inventory_binds_code_corpus_rows_and_costs_without_solver(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            pin = repository(base / "repo", files())
            report = api("corpus_audit").run_audit(base / "repo", base / "out", commit=pin,
                                                 expected_count=1)
            self.assertEqual(report["terminal"], "LEXICAL_INVENTORY_VALIDATED")
            self.assertFalse(report["solver_launched"])
            self.assertFalse(report["target_selection_performed"])
            self.assertEqual(report["kernel_elaboration"], "NOT_RUN")
            self.assertEqual(report["rows_accounted"]["wrappers"],
                             {"listed": 1, "examined": 1, "accepted": 1, "refused": 0, "unread": 0})
            self.assertIn("Definitions/Context.lean",
                          json.loads((base / "out/CORPUS_SOURCE.json").read_text())["files"])
            self.assertGreater(report["resources"]["blob_bytes_read"], 0)
            self.assertGreaterEqual(report["resources"]["wall_seconds"], 0)
            for name, expected in report["artifact_sha256"].items():
                self.assertEqual(hashlib.sha256((base / "out" / name).read_bytes()).hexdigest(), expected)
            self.assertEqual(report["source_inventory_sha256"],
                             api("corpus_contract").digest(json.loads((base / "out/CODE_SOURCE.json").read_text())))
            self.assertFalse(any(p.name.lower() in {"public", "private", "challenge.json"} for p in (base / "out").iterdir()))

    def test_all_rows_accounted_when_one_wrapper_refuses(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source = files()
            source.update({"Theorems/Thm_B.lean": wrapper("B", body="by assumption"),
                           "P2M/Sol/S_B.lean": solution("A")})
            pin = repository(base / "repo", source)
            report = api("corpus_audit").run_audit(base / "repo", base / "out", commit=pin,
                                                 expected_count=2)
            self.assertEqual(report["terminal"], "CANNOT_CHECK_LEXICAL_COVERAGE")
            self.assertEqual(report["rows_accounted"]["wrappers"],
                             {"listed": 2, "examined": 2, "accepted": 1, "refused": 1, "unread": 0})
            rows = json.loads((base / "out/WRAPPERS.json").read_text())
            self.assertEqual(set(rows), {"A", "B"})
            self.assertEqual(rows["B"]["failure_code"], "BRIDGE_COUNT")
            self.assertNotIn("GRAPH.json", report["artifact_sha256"])

    def test_cycle_and_environment_drift_cannot_be_validated(self):
        for mode in ("cycle", "environment"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temp:
                base = Path(temp)
                source = files()
                source["P2M/Sol/S_A.lean"] = solution("A") if mode == "cycle" else solution()
                if mode == "environment":
                    source["lean-toolchain"] = "leanprover/lean4:v4.19.0\n"
                pin = repository(base / "repo", source)
                report = api("corpus_audit").run_audit(base / "repo", base / "out",
                                                     commit=pin, expected_count=1)
                self.assertNotEqual(report["terminal"], "LEXICAL_INVENTORY_VALIDATED")
                self.assertEqual(report["failure_code"],
                                 "IMPORT_CYCLE" if mode == "cycle" else "ENVIRONMENT_IDENTITY")

    def test_output_cannot_overwrite_a_previous_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            pin = repository(base / "repo", files())
            (base / "out").mkdir()
            (base / "out/preserved").write_text("keep")
            with self.assertRaises(FileExistsError):
                api("corpus_audit").run_audit(base / "repo", base / "out",
                                            commit=pin, expected_count=1)
            self.assertEqual((base / "out/preserved").read_text(), "keep")

    def test_source_drift_refuses_instead_of_reusing_old_binding(self):
        with self.assertRaisesRegex(api("corpus_contract").CorpusError, "SOURCE_DRIFT"):
            api("corpus_audit").require_same_source({"a.py": "a"}, {"a.py": "b"})

    def test_cli_has_no_selection_staging_or_solver_arguments(self):
        self.assertTrue((HERE / "audit.py").is_file(), "inventory CLI not implemented")
        for option in ("--select", "--stage", "--target", "--solve"):
            with self.subTest(option=option):
                result = subprocess.run([sys.executable, str(HERE / "audit.py"), option],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
                self.assertIn("usage:", result.stderr)


if __name__ == "__main__":
    unittest.main()
