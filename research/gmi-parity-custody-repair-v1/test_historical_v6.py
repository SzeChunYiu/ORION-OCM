"""Actual preserved packet checks, executed via matching static-audit interpreters only."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

from frozen_contract_v1 import HERE, sha, strict_json
from cross_envelope_v6 import collect
from resource_evidence_v6 import derive_frontier, reconstruct_boxes
from packet_content_v6 import audit_packet
from synthetic_fixture_v1 import packet

INTERPRETERS = {
    "3.11.15": Path("/home/billy/ocm-verify/work/parity-audit-interpreters/"
                    "cpython-3.11.15-linux-x86_64-gnu/bin/python3.11"),
    "3.12.3": Path("/home/billy/ocm-verify/work/parity-audit-interpreters/"
                   "cpython-3.12.3-linux-x86_64-gnu/bin/python3.12"),
    "3.13.12": Path("/home/billy/.local/share/uv/python/"
                    "cpython-3.13-linux-x86_64-gnu/bin/python3.13"),
}


class HistoricalTests(unittest.TestCase):
    def test_imported_bytes_are_exactly_bound(self):
        binding = strict_json((HERE / "raw/IMPORTED_V5_PACKET_BINDINGS_V1.json").read_bytes())
        self.assertEqual(len(binding["packet_sha256"]), 3)
        for name, expected in binding["packet_sha256"].items():
            self.assertEqual(sha((HERE / "raw" / name).read_bytes()), expected)

    def test_same_host_different_valid_interpreters_agree_with_refusal_retained(self):
        missing = [str(p) for p in INTERPRETERS.values() if not p.is_file()]
        if missing:
            self.skipTest("matching static-audit interpreters unavailable: " + ", ".join(missing))
        paths = sorted((HERE / "raw").glob("NN_NONNN_POINT_PARITY3_RESULT_V5_*.json"))
        result = collect([], [str(p) for p in INTERPRETERS.values()], paths)
        self.assertEqual(len(result["valid_attempts"]), 2)
        self.assertEqual(len(result["nonvalid_attempts"]), 1)
        self.assertEqual(result["cross_envelope_stability"],
                         "STABLE_ACROSS_ENVELOPES__DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE")
        self.assertFalse(result["replication_obligation_discharged"])
        self.assertEqual(next(row for row in result["per_attempt"].values() if not row["valid"])
                         ["status"], "REPORTED_INSTRUMENT_REFUSAL")
        for row in result["per_attempt"].values():
            self.assertFalse(row["first_attempt_custody_verified"])

    def test_real_packet_semantic_mutation_not_just_hash_rejection(self):
        executable = INTERPRETERS["3.12.3"]
        if not executable.is_file():
            self.skipTest("matching CPython3.12.3 unavailable")
        path = next((HERE / "raw").glob("*CPython3.12.3.json"))
        code = (
            "import copy,json,sys;from pathlib import Path;"
            "sys.path.insert(0,sys.argv[1]);"
            "from packet_content_v6 import audit_packet;"
            "from frozen_contract_v1 import AuditError;"
            "p=json.loads(Path(sys.argv[2]).read_bytes());"
            "assert audit_packet(p)['status']=='COMPLETE_STATIC_V5_EVIDENCE_PASS';"
            "p['measurements']['X_XOR2_V1'].pop();"
            "\ntry: audit_packet(p)\nexcept AuditError: print('REAL_MISSING_BLOCK_REJECTED')"
            "\nelse: raise RuntimeError('mutated real packet admitted')"
        )
        result = subprocess.run([str(executable), "-I", "-B", "-c", code, str(HERE), str(path)],
                                capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertEqual(result.stdout.strip(), b"REAL_MISSING_BLOCK_REJECTED")

    def test_mixed_frontier_preserved_when_timing_tradeoff_is_synthetic(self):
        p = packet()
        cid = "N_THRESHOLD_DNF4_V1"
        for row in p["measurements"][cid]:
            row["wall_block_ns"] = row["process_block_ns"] = 1
        p["resource_boxes"] = reconstruct_boxes(p["measurements"], p["opcode_counts"])
        p.update(derive_frontier(p["resource_boxes"]))
        report = audit_packet(p)
        self.assertEqual(report["frontier_candidate_ids"], [cid, "X_XOR2_V1"])
        self.assertEqual(report["terminal"], "UNDECIDED_FROM_CURRENT_EVIDENCE")


if __name__ == "__main__":
    unittest.main()
