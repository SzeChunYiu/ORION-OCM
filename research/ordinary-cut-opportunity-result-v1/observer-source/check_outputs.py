"""Authored output-contract checks; no teaching/native input is opened."""
from pathlib import Path
import copy
import hashlib
import json
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import output_contract as C
ARTIFACTS = HERE / "qualification-01" / "fixtures"
REQPIN = {"bytes": 1, "sha256": "a" * 64}
REQUEST = {"qualified_native_trace_authority": {"AUTHORED_ONLY": "authority"},
           "P1_inventory": {"AUTHORED_ONLY": "inventory"}}


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def fixture(name, partial=False):
    folder = ARTIFACTS / name
    folder.mkdir(parents=True)
    rows = [{"ordinal": i, "label": "AUTHORED_" + str(i),
             "status": "NOT_REACHED_RESOURCE"} for i in range(4096, 4224)]
    rows[0].update(status="ENUMERATED", cuts=[])
    rows[1].update(status="UNKNOWN_INTERFACE", error="AUTHORED_INTERFACE_REFUSAL")
    rows[2].update(status="TRACE_UNUSABLE", P1_retained=True,
                   opportunity_coverage="UNKNOWN_INTERFACE", whole_contract={"AUTHORED_ONLY": True})
    if partial:
        rows = rows[:3]
    write(folder / "P1-CONTRACTS.json", [{"AUTHORED_ONLY": "not a native P1"}])
    result = {"schema": "ordinary.training-only-opportunity.v3", "roots": rows,
        "terminal": "AUDIT_FAILED" if partial else "TRAINING_ONLY_OPPORTUNITY_RECORDED",
        "pid": 123, "request": REQPIN, "native_calls": 0, "new_native_admissions": 0,
        "training_outcome_is_not_native_admission": True, **REQUEST,
        "P1_contracts": C.identity((folder / "P1-CONTRACTS.json").read_bytes()),
        "inputs_unchanged": True, "sources_unchanged": True, "request_unchanged": True}
    for row in rows:
        if row["status"] in {"ENUMERATED", "UNKNOWN_INTERFACE", "TRACE_UNUSABLE"}:
            write(folder / ("ROOT-" + str(row["ordinal"]) + ".json"), row)
    write(folder / "RESULT.json", result)
    return folder, result


class OutputControls(unittest.TestCase):
    def test_mixed_population_does_not_require_unreached_files(self):
        folder, _ = fixture(self._testMethodName)
        r = C.inspect_outputs(folder, 123, REQPIN, REQUEST)
        self.assertTrue(r["population_ok"])
        self.assertTrue(r["completed_contract"])
        self.assertEqual(r["status_counts"]["NOT_REACHED_RESOURCE"], 125)
        self.assertEqual(set(r["expected_files"]), {"RESULT.json", "P1-CONTRACTS.json",
            "ROOT-4096.json", "ROOT-4097.json", "ROOT-4098.json"})

    def test_missing_processed_root_refuses(self):
        folder, _ = fixture(self._testMethodName)
        (folder / "ROOT-4097.json").unlink()
        self.assertFalse(C.inspect_outputs(folder, 123, REQPIN, REQUEST)["population_ok"])

    def test_fabricated_unreached_root_refuses(self):
        folder, result = fixture(self._testMethodName)
        write(folder / "ROOT-4099.json", result["roots"][3])
        self.assertFalse(C.inspect_outputs(folder, 123, REQPIN, REQUEST)["population_ok"])

    def test_changed_root_payload_refuses(self):
        folder, result = fixture(self._testMethodName)
        row = copy.deepcopy(result["roots"][1])
        row["error"] = "CHANGED"
        write(folder / "ROOT-4097.json", row)
        self.assertFalse(C.inspect_outputs(folder, 123, REQPIN, REQUEST)["population_ok"])

    def test_unusable_requires_whole_theorem_retention(self):
        folder, result = fixture(self._testMethodName)
        result["roots"][2]["P1_retained"] = False
        write(folder / "ROOT-4098.json", result["roots"][2])
        write(folder / "RESULT.json", result)
        self.assertFalse(C.inspect_outputs(folder, 123, REQPIN, REQUEST)["population_ok"])

    def test_wrong_child_pid_cannot_complete(self):
        folder, _ = fixture(self._testMethodName)
        r = C.inspect_outputs(folder, 124, REQPIN, REQUEST)
        self.assertTrue(r["population_ok"])
        self.assertFalse(r["completed_contract"])

    def test_partial_failed_records_retained_without_completion(self):
        folder, _ = fixture(self._testMethodName, partial=True)
        r = C.inspect_outputs(folder, 123, REQPIN, REQUEST)
        self.assertTrue(r["population_ok"])
        self.assertFalse(r["completed_contract"])
        self.assertEqual(r["recorded_terminal"], "AUDIT_FAILED")

    def test_missing_position_cannot_complete(self):
        folder, result = fixture(self._testMethodName)
        result["roots"].pop()
        write(folder / "RESULT.json", result)
        r = C.inspect_outputs(folder, 123, REQPIN, REQUEST)
        self.assertTrue(r["population_ok"])
        self.assertFalse(r["completed_contract"])

    def test_cleanup_block_is_exact_reviewed_donor(self):
        old = (HERE / "DONOR-observe_ordinary_export_v1.py").read_text()
        new = (HERE / "observe_opportunity.py").read_text()
        def block(text, end):
            return text[text.index("    process_start = time.perf_counter()"):text.index(end)]
        self.assertEqual(block(old, "    unchanged, read_errors, output_files, output_entries = {}, {}, {}, []"),
                         block(new, "    unchanged, read_errors = {}, {}"))
        self.assertEqual(hashlib.sha256(old.encode()).hexdigest(),
                         "17cd28c890cabfd3f80e32fcd60d4991e7b5142cbb53c19bfb4e5970a9281fee")


if __name__ == "__main__":
    unittest.main(verbosity=2)
