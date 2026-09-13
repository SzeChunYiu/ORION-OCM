"""Instrument integrity and historical custody; never run protected timing."""

import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "nn_nonnn_point_parity3_experiment_v2.py"
SPEC = importlib.util.spec_from_file_location("parity3_instrument_v2", SOURCE)
MOD = importlib.util.module_from_spec(SPEC)
exec(compile(SOURCE.read_bytes(), str(SOURCE), "exec"), MOD.__dict__)


@unittest.skipUnless(sys.implementation.name == "cpython" and sys.version_info[:2] == (3, 12),
                     "registered instrument substrate is CPython 3.12")
class Parity3InstrumentV2Tests(unittest.TestCase):
    def fresh(self, code, optimized=False):
        setup = ("from pathlib import Path\n"
                 f"ns={{'__file__':{str(SOURCE)!r},'__name__':'isolated_test'}}\n"
                 "exec(compile(Path(ns['__file__']).read_bytes(),ns['__file__'],'exec'),ns)\n")
        flags = ["-I", "-B"] + (["-O"] if optimized else [])
        return json.loads(subprocess.check_output([sys.executable, *flags, "-c", setup + code],
                                                 text=True, timeout=10))

    def test_fresh_process_first_candidate_is_complete_in_both_orders(self):
        for order in (list(MOD.CANDIDATES), list(reversed(MOD.CANDIDATES))):
            with self.subTest(order=order):
                got = self.fresh("import json\nprint(json.dumps({cid:ns['count_candidate_opcodes']"
                                 f"(ns['CANDIDATES'][cid]['fn']) for cid in {order!r}}}))\n")
                self.assertEqual(got, {"N_THRESHOLD_DNF4_V1": 472, "X_XOR2_V1": 88})

    def test_old_v1_first_candidate_zero_reproduces_without_timing(self):
        old = HERE / "nn_nonnn_point_parity3_experiment_v1.py"
        code = ("from pathlib import Path\nimport json\n"
                f"ns={{'__file__':{str(old)!r},'__name__':'diagnostic'}}\n"
                "exec(compile(Path(ns['__file__']).read_bytes(),ns['__file__'],'exec'),ns)\n"
                "print(json.dumps([ns['count_candidate_opcodes'](row['fn']) "
                "for row in ns['CANDIDATES'].values()]))\n")
        got = json.loads(subprocess.check_output([sys.executable, "-I", "-B", "-c", code],
                                                text=True, timeout=10))
        self.assertEqual(got, [0, 88])

    def test_truncated_empty_extra_and_reordered_opcode_witnesses_fail(self):
        fn = MOD.non_neural_xor_parity3
        calls = MOD.trace_candidate_opcodes(fn)["calls"]
        changes = [[], calls[:-1]]
        for offsets in ([], calls[0]["opcode_offsets"][:-1],
                        calls[0]["opcode_offsets"] + [999],
                        list(reversed(calls[0]["opcode_offsets"]))):
            damaged = copy.deepcopy(calls)
            damaged[0]["opcode_offsets"] = offsets
            changes.append(damaged)
        for bad in changes:
            with self.subTest(bad=bad), self.assertRaises(MOD.MeasurementIntegrityError):
                MOD.validate_opcode_witness(fn, bad)

    def test_boolean_offsets_and_missing_or_wrong_returns_fail(self):
        fn = MOD.non_neural_xor_parity3
        original = MOD.trace_candidate_opcodes(fn)["calls"]
        for key, value in (("opcode_offsets", [True] * len(original[0]["opcode_offsets"])),
                           ("returned", False), ("returned", 1), ("output", True), ("output", 1)):
            bad = copy.deepcopy(original)
            bad[0][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(MOD.MeasurementIntegrityError):
                MOD.validate_opcode_witness(fn, bad)

    def test_foreign_tracer_is_refused_and_preserved(self):
        def foreign(frame, event, arg):
            return foreign
        sys.settrace(foreign)
        try:
            with self.assertRaisesRegex(MOD.MeasurementIntegrityError, "another trace"):
                MOD.trace_candidate_opcodes(MOD.non_neural_xor_parity3)
            self.assertIs(sys.gettrace(), foreign)
        finally:
            sys.settrace(None)

    def test_candidate_exception_restores_trace_state(self):
        def broken(x):
            raise RuntimeError("candidate broke")
        with self.assertRaisesRegex(RuntimeError, "candidate broke"):
            MOD.trace_candidate_opcodes(broken)
        self.assertIsNone(sys.gettrace())
        self.assertEqual(MOD.count_candidate_opcodes(MOD.non_neural_xor_parity3), 88)

    def test_branching_candidate_is_outside_static_validator(self):
        def branching(x):
            return 1 if x[0] else 0
        with self.assertRaisesRegex(MOD.MeasurementIntegrityError, "straight-line"):
            MOD.expected_opcode_offsets(branching)

    def test_order_dependent_instrument_fails(self):
        witnesses = [MOD.trace_candidate_opcodes(row["fn"]) for row in MOD.CANDIDATES.values()]
        damaged = copy.deepcopy(witnesses[0])
        damaged["count"] += 1
        with patch.object(MOD, "trace_candidate_opcodes", side_effect=[*witnesses, witnesses[1], damaged]):
            with self.assertRaisesRegex(MOD.MeasurementIntegrityError, "candidate-order"):
                MOD.instrumentation_preflight()

    def test_instrument_failure_abstains_before_any_timed_block(self):
        with patch.object(MOD, "protocol_environment_valid", return_value=(True, [])), \
             patch.object(MOD, "warmup", return_value=20000), \
             patch.object(MOD, "instrumentation_preflight", side_effect=MOD.MeasurementIntegrityError("zero events")), \
             patch.object(MOD, "timed_block", side_effect=AssertionError("timing forbidden")) as timed:
            packet = MOD.run_experiment()
        timed.assert_not_called()
        self.assertEqual(packet["terminal"], "INVALID_RECEIPT_OR_PROTOCOL_VIOLATION")
        self.assertEqual(packet["winner_candidate_id"], "NONE")
        self.assertFalse(packet["protected_timing_measurement_executed"])
        self.assertFalse(packet["instrumentation_gate_pass"])

    def test_unregistered_environment_stops_before_warmup_and_timing(self):
        with patch.object(MOD, "protocol_environment_valid", return_value=(False, ["test"])), \
             patch.object(MOD, "warmup") as warmup, patch.object(MOD, "timed_block") as timed:
            packet = MOD.run_experiment()
        warmup.assert_not_called()
        timed.assert_not_called()
        self.assertEqual(packet["terminal"], "INVALID_RECEIPT_OR_PROTOCOL_VIOLATION")

    def test_selftest_survives_optimized_python_and_never_times(self):
        packet = self.fresh("import json\nprint(json.dumps(ns['deterministic_self_test']()))\n", optimized=True)
        self.assertEqual(packet["opcode_counts"], {"N_THRESHOLD_DNF4_V1": 472, "X_XOR2_V1": 88})
        self.assertFalse(packet["protected_timing_measurement_executed"])
        self.assertFalse(packet["independent_prospective_prediction"])


class Parity3CustodyV2Tests(unittest.TestCase):
    def test_candidate_implementations_and_registered_schedule_are_unchanged(self):
        def candidates(path):
            return {n.name: ast.dump(n, include_attributes=False)
                    for n in ast.parse(path.read_text()).body
                    if isinstance(n, ast.FunctionDef) and n.name in
                    ("neural_threshold_parity3", "non_neural_xor_parity3")}
        self.assertEqual(candidates(SOURCE), candidates(HERE / "nn_nonnn_point_parity3_experiment_v1.py"))
        old = json.loads((HERE / "NN_NONNN_POINT_PARITY3_PREREG_V1.json").read_text())
        new = json.loads(MOD.PREREG.read_text())
        for key in ("candidates", "problem", "measurement_schedule", "registered_resource_coordinates",
                    "selection_rule", "substrate", "candidate_expansion_attack"):
            self.assertEqual(old[key], new[key], key)
        self.assertIs(new["independent_prospective_prediction"], False)

    def test_both_hosted_packets_preserve_outcomes_and_exact_log_custody(self):
        provenance = json.loads((HERE / "NN_NONNN_POINT_PARITY3_HOSTED_PROVENANCE_V1.json").read_text())
        self.assertEqual(len(provenance["records"]), 2)
        for row in provenance["records"]:
            data = (HERE / row["packet"]).read_bytes()
            packet = json.loads(data)
            self.assertEqual(hashlib.sha256(data).hexdigest(), row["packet_sha256"])
            excerpt = row["source_log_excerpt"]
            self.assertEqual(hashlib.sha256(excerpt.encode()).hexdigest(), row["source_log_excerpt_sha256"])
            stripped = "\n".join(re.sub(r"^\ufeff?\d{4}-\d\d-\d\dT\S+Z\s?", "", line)
                                 for line in excerpt.splitlines()) + "\n"
            self.assertEqual(stripped.encode(), data)
            self.assertEqual(row["evidence_classification"], "EXECUTED_WITH_PROTOCOL_DEFECT")
            self.assertEqual(packet["schema"], "NN_NONNN_POINT_PARITY3_RESULT_V1")
            self.assertIs(packet["protected_resource_measurement_executed"], True)
            self.assertEqual(packet["terminal"], "UNDECIDED_FROM_CURRENT_EVIDENCE")
            self.assertIs(packet["prospective_prediction_passed"], False)
            self.assertEqual(packet["opcode_counts"], {"N_THRESHOLD_DNF4_V1": 0, "X_XOR2_V1": 88})
            self.assertEqual(packet["environment"]["github_sha"], row["tested_github_sha"])
            self.assertEqual(packet["environment"]["harness_sha256"], row["harness_sha256"])
            self.assertEqual(hashlib.sha256((HERE / "nn_nonnn_point_parity3_experiment_v1.py").read_bytes()).hexdigest(),
                             row["harness_sha256"])

    def test_archived_v1_cannot_rerun_and_v2_times_only_main_commits(self):
        workflows = HERE.parent.parent / ".github" / "workflows"
        old = (workflows / "grand-gmi-nn-nonnn-point-parity3.yml").read_text()
        new = (workflows / "grand-gmi-nn-nonnn-point-parity3-v2.yml").read_text()
        self.assertNotIn("  push:", old)
        self.assertNotIn("  pull_request:", old)
        self.assertIn("if: ${{ false }}", old)
        self.assertNotIn("  pull_request:", new)
        self.assertIn("branches: [main]", new)
        self.assertNotIn("experiment_v1.py", new)


if __name__ == "__main__":
    unittest.main()
