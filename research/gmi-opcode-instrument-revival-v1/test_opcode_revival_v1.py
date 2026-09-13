"""Static evidence tests: these never invoke a candidate or rerun the experiment."""
import copy
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from opcode_sources_v1 import ADDED_LINE, PARENT_SHA, PARENT, collector_source, parent, sha
from opcode_witness_v1 import expectation, inspect_calls


class OpcodeRevivalTests(unittest.TestCase):
    def setUp(self):
        path = HERE / "raw/repaired_forward_execution.json"
        self.packet = json.loads(json.loads(path.read_text())["stdout"])
        self.row = self.packet["rows"][0]
        self.expected = self.packet["expectations"][self.row["candidate"]]
        self.inputs = self.packet["inputs"]

    def result(self, calls):
        return inspect_calls(calls, self.expected, self.inputs)

    def test_frozen_parent_bytes(self):
        self.assertEqual(sha(PARENT), PARENT_SHA)

    def test_only_one_setter_insertion(self):
        original, changed = collector_source(False), collector_source(True)
        self.assertEqual(changed.count(ADDED_LINE), 1)
        self.assertEqual(changed.replace(ADDED_LINE, "", 1), original)

    def test_real_complete_packet(self):
        self.assertEqual(self.result(self.row["calls"])["errors"], [])

    def test_real_original_first_call_is_retained(self):
        p = json.loads(json.loads((HERE / "raw/original_forward_execution.json").read_text())["stdout"])
        self.assertEqual(p["rows"][0]["calls"][0]["opcode_offsets"], [])
        self.assertEqual(p["rows"][0]["calls"][0]["returned"], True)
        self.assertEqual(len(p["rows"]), 8)

    def test_actual_original_pattern_in_both_orders(self):
        for order in ("forward", "reverse"):
            path = HERE / "raw" / f"original_{order}_execution.json"
            packet = json.loads(json.loads(path.read_text())["stdout"])
            for row in packet["rows"]:
                result = inspect_calls(row["calls"], packet["expectations"][row["candidate"]],
                                       packet["inputs"])
                errors = ["frame 0: offset sequence"] if row["pass_index"] == 0 else []
                self.assertEqual(result["errors"], errors)

    def test_missing_first_frame(self):
        self.assertTrue(self.result(self.row["calls"][1:])["errors"])

    def test_missing_first_offset(self):
        calls = copy.deepcopy(self.row["calls"])
        calls[0]["opcode_offsets"].pop(0)
        self.assertTrue(self.result(calls)["errors"])

    def test_duplicate_offset(self):
        calls = copy.deepcopy(self.row["calls"])
        calls[0]["opcode_offsets"].append(calls[0]["opcode_offsets"][-1])
        self.assertTrue(self.result(calls)["errors"])

    def test_reordered_offsets(self):
        calls = copy.deepcopy(self.row["calls"])
        calls[0]["opcode_offsets"].reverse()
        self.assertTrue(self.result(calls)["errors"])

    def test_wrong_parity(self):
        calls = copy.deepcopy(self.row["calls"])
        calls[0]["output"] = 1 - calls[0]["output"]
        self.assertTrue(self.result(calls)["errors"])

    def test_boolean_output_not_integer_witness(self):
        calls = copy.deepcopy(self.row["calls"])
        calls[0]["output"] = bool(calls[0]["output"])
        self.assertTrue(self.result(calls)["errors"])

    def test_missing_return(self):
        calls = copy.deepcopy(self.row["calls"])
        calls[0]["returned"] = False
        self.assertTrue(self.result(calls)["errors"])

    def test_reject_branching_oracle_scope(self):
        def branch(x):
            return 1 if x else 0
        with self.assertRaises(ValueError):
            expectation(branch)

    def test_native_disassembly_matches_when_exact_version(self):
        if tuple(sys.version_info[:3]) != (3, 13, 12):
            self.skipTest("native offset audit needs the recorded CPython 3.13.12")
        module = parent()
        self.assertEqual({cid: expectation(row["fn"]) for cid, row in module.CANDIDATES.items()},
                         self.packet["expectations"])

    def test_exact_receipt_replay_when_exact_version(self):
        if tuple(sys.version_info[:3]) != (3, 13, 12):
            self.skipTest("native receipt replay needs the recorded CPython 3.13.12")
        from opcode_audit_v1 import audit
        self.assertEqual(audit(), json.loads((HERE / "OPCODE_REVIVAL_RECEIPT_V1.json").read_text()))


if __name__ == "__main__":
    unittest.main()
