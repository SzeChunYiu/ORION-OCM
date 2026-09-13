import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_consumer_repair_v1 import run
from contract_v1 import AuditError, strict_json
from scan_retained_v1 import scan_directory, scan_record
from source_contract_v1 import HERE, bound_files, current_contract, retained_inputs


class RetainedTests(unittest.TestCase):
    def test_full_real_no_alarm_and_independent_route_oracle(self):
        receipt = run()
        self.assertEqual(receipt["retained_source_rows"], 350)
        self.assertEqual(receipt["retained_grad_source_rows"], 8)
        self.assertEqual(receipt["prior_arm_and_legacy_role_comparisons"], 87)
        self.assertEqual(receipt["independent_reverse_route_comparisons"], 422)
        self.assertEqual(receipt["new_genotype_or_ecology_executions"], 0)

    def test_actual_arm_missing_genotype_is_not_absence(self):
        files = retained_inputs(); kinds, roles = current_contract()
        name = next(n for n in files if n.startswith("pr551/STAGE_B6_DEV_"))
        record = strict_json(files[name])
        record["first_admissible"].pop("atrophied_genotype")
        result = scan_record(name, json.dumps(record).encode(), kinds, roles)
        row = next(r for r in result["rows"] if r["source_fields"] ==
                   ["first_admissible", "atrophied_genotype"])
        self.assertEqual(row["status"], "NOT_RETAINED")

    def test_empty_missing_and_unsupported_have_distinct_states(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(scan_directory(tmp + "/missing")["status"], "INPUT_UNAVAILABLE")
            self.assertEqual(scan_directory(tmp)["status"], "NO_MATCHING_INPUTS")
            p = Path(tmp) / "STAGE_B6_DEV_unknown.json"; p.write_text('{"schema":"future"}')
            result = scan_directory(tmp)
            self.assertEqual(result["status"], "PARTIAL")
            self.assertEqual(result["records"][0]["status"], "INVALID_OR_UNSUPPORTED")

    def test_real_retained_directory_cli_no_alarm_and_no_import_execution(self):
        files = retained_inputs()
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            for name, data in files.items():
                if name.startswith(("sources/", "pr551/STAGE_B6_")):
                    (p / Path(name).name).write_bytes(data)
            output = subprocess.run([sys.executable, "-I", "-B", str(HERE / "scan_retained_v1.py"), tmp],
                                    capture_output=True, check=True, text=True)
            self.assertEqual(output.stderr, "")
            self.assertEqual(json.loads(output.stdout)["status"], "COMPLETE_SELECTED_FIELD_INSPECTION")
            imported = subprocess.run([sys.executable, "-I", "-B", "-c",
                "import runpy; runpy.run_path(" + repr(str(HERE / "scan_retained_v1.py")) + ")"],
                capture_output=True, check=True, text=True)
            self.assertEqual(imported.stdout + imported.stderr, "")

    def test_bound_native_drift_and_link_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "unit"; shutil.copytree(HERE, dest)
            vm = dest / "raw/native/vm.py"
            data = vm.read_bytes(); vm.write_bytes(data + b"\n")
            with self.assertRaises(AuditError): bound_files(dest)
            vm.unlink(); vm.symlink_to(HERE / "raw/native/vm.py")
            with self.assertRaises(AuditError): bound_files(dest)

    def test_json_duplicate_overflow_refused(self):
        for text in ('{"a":1,"a":2}', '{"a":1e999}'):
            with self.assertRaises(AuditError): strict_json(text)


if __name__ == "__main__":
    unittest.main()
