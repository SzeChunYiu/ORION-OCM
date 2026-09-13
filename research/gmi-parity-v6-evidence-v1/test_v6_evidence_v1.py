"""Static controls on real packets, portable relocation, and unavailable runtimes."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parent))
from authority_v1 import HERE, VERSIONS, load_authority, read_packet, verify_inputs
from countercontrols_v1 import MUTATIONS, run_controls
from frozen_contract_v1 import AuditError, Unverifiable, strict_json
from packet_audit_v1 import audit_content
from replay_v1 import collect, PASS


class PortableControls(unittest.TestCase):
    def test_all_archived_bytes_bound(self):
        self.assertEqual(len(verify_inputs()["files"]), 16)

    def test_missing_interpreters_are_unknown(self):
        r = collect({})
        self.assertEqual((r["status"], r["validated_packets"]), ("UNVERIFIABLE", 0))

    def test_nonexistent_interpreter_is_unknown(self):
        r = collect({VERSIONS[0]: "/nonexistent/exact/python"})
        self.assertEqual(r["records"][VERSIONS[0]]["status"], "UNVERIFIABLE")

    def test_worker_failure_never_counts_as_valid(self):
        with patch("replay_v1.subprocess.run",
                   return_value=subprocess.CompletedProcess([], 1, "not json", "")):
            r = collect({VERSIONS[0]: sys.executable})
        self.assertEqual((r["status"], r["validated_packets"]), ("REJECTED", 0))

    def test_status_exit_contradiction_rejected(self):
        fake = subprocess.CompletedProcess([], 1, json.dumps({"status": PASS}), "")
        with patch("replay_v1.subprocess.run", return_value=fake):
            self.assertEqual(collect({VERSIONS[0]: sys.executable})["status"], "REJECTED")

    def test_status_only_success_is_not_complete_evidence(self):
        fake = subprocess.CompletedProcess([], 0, json.dumps({"status": PASS}), "")
        with patch("replay_v1.subprocess.run", return_value=fake):
            result = collect({VERSIONS[0]: sys.executable})
        self.assertEqual((result["status"], result["validated_packets"]), ("REJECTED", 0))

    def test_unregistered_interpreter_rejected(self):
        with self.assertRaises(AuditError):
            collect({"3.99": sys.executable})

    def test_duplicate_and_nonfinite_json_rejected(self):
        for raw in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":1e999}'):
            with self.subTest(raw=raw), self.assertRaises(AuditError):
                strict_json(raw)

    def test_altered_source_binding_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "unit"
            shutil.copytree(HERE, target)
            source = target / "raw/frozen/nn_nonnn_point_parity3_experiment_v6.py"
            source.write_bytes(source.read_bytes() + b"\n")
            with self.assertRaisesRegex(AuditError, "frozen input drift"):
                load_authority(target)

    def test_altered_input_authority_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "unit"
            shutil.copytree(HERE, target)
            source = target / "FROZEN_INPUTS_V1.json"
            source.write_bytes(source.read_bytes() + b"\n")
            with self.assertRaisesRegex(AuditError, "input authority drift"):
                verify_inputs(target)


class NativePacketControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.version = platform.python_version()
        if cls.version not in VERSIONS or platform.python_implementation() != "CPython":
            raise unittest.SkipTest("UNVERIFIABLE: matching recorded CPython release unavailable")
        cls.authority = load_authority()
        cls.packet = read_packet(cls.version)

    def test_actual_retained_packet_no_alarm(self):
        result = audit_content(self.packet, self.authority)
        self.assertEqual(result["status"], PASS)
        self.assertEqual(result["complete_recorded_frames"], 64)
        self.assertFalse(result["historical_first_attempt_authenticated"])

    def test_50_malformed_copies_rejected(self):
        rejected = run_controls(self.packet, self.authority)
        self.assertEqual(len(rejected), len(MUTATIONS) + 5)
        self.assertEqual(len(rejected), 50)

    def test_mismatched_interpreter_unknown(self):
        bad = copy.deepcopy(self.packet)
        bad["environment"]["python_version"] = "3.0.0"
        with self.assertRaises(Unverifiable):
            audit_content(bad, self.authority)

    def test_observed_priming_scope_is_explicit(self):
        r = audit_content(self.packet, self.authority)["priming"]
        self.assertFalse(r["forward_priming_raw_traces_available"])
        self.assertFalse(r["reverse_priming_summaries_available"])
        self.assertFalse(r["priming_necessity_or_causality_established"])
        self.assertEqual(bool(r["reported_incomplete_candidates"]), self.version == "3.13.12")

    def test_metadata_checks_do_not_depend_on_ambient_ci(self):
        with patch.dict("os.environ", {"GITHUB_ACTIONS": "true", "CI": "true",
                                     "GITHUB_RUN_ATTEMPT": "7", "SLURM_JOB_ID": "123"}, clear=True):
            self.assertEqual(audit_content(self.packet, self.authority)["status"], PASS)

    def test_source_legal_context_precedence_positive_controls(self):
        for context, job in (("SLURM_BATCH", "123"), ("GITHUB_ACTIONS", "123"),
                             ("GITHUB_ACTIONS", None)):
            with self.subTest(context=context, job=job):
                packet = copy.deepcopy(self.packet)
                packet["environment"]["execution_context"] = context
                packet["environment"]["slurm"]["job_id"] = job
                self.assertEqual(audit_content(packet, self.authority)["status"], PASS)

    def test_interval_corners_distinguish_possible_and_necessary_lookup(self):
        boxes = self.packet["resource_boxes"]
        def point_frontier(best):
            costs = {cid: {k: pair[0 if cid == best else 1] for k, pair in box.items()}
                     for cid, box in boxes.items()}
            return [cid for cid in costs if not any(
                all(costs[other][k] <= costs[cid][k] for k in costs[cid]) and
                any(costs[other][k] < costs[cid][k] for k in costs[cid])
                for other in costs if other != cid)]
        possible = point_frontier("X_LOOKUP8_V3")
        adverse = point_frontier("X_XOR2_V1")
        self.assertEqual("X_LOOKUP8_V3" in possible, self.version == "3.11.15")
        self.assertNotIn("X_LOOKUP8_V3", adverse)
        self.assertIn("X_XOR2_V1", possible)
        self.assertIn("X_XOR2_V1", adverse)

    def test_no_candidate_or_measurement_code_enters_during_full_census(self):
        module = self.authority[2]
        codes = {row["fn"].__code__ for row in module.CANDIDATES.values()}
        for name in ("run_experiment", "instrumentation_preflight", "_trace_session",
                     "trace_candidate_opcodes", "warmup", "timed_block", "outputs",
                     "capability_record", "constant_zero_null_record"):
            codes.add(getattr(module, name).__code__)
        entered = []
        def guard(frame, event, arg):
            if event == "call" and frame.f_code in codes:
                entered.append(frame.f_code.co_name)
                raise RuntimeError("forbidden measurement execution")
        previous = sys.getprofile()
        try:
            sys.setprofile(guard)
            audit_content(self.packet, self.authority)
            run_controls(self.packet, self.authority)
        finally:
            sys.setprofile(previous)
        self.assertEqual(entered, [])

    def test_relocation_independent_of_checkout_or_cwd(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "relocated"
            shutil.copytree(HERE, target)
            command = [sys.executable, "-I", "-B"] + (["-O"] if sys.flags.optimize else [])
            command += [str(target / "audit_v1.py"), "--version", self.version]
            run = subprocess.run(command, cwd=directory, capture_output=True, text=True, timeout=30)
            self.assertEqual(run.returncode, 0, run.stderr + run.stdout)
            self.assertEqual(strict_json(run.stdout)["status"], PASS)


if __name__ == "__main__":
    unittest.main()
