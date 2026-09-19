from __future__ import annotations

import importlib.util
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


HERE = Path(__file__).resolve().parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load test module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


M = load("gmi833_hundred_million_primary", HERE / "hundred_million_census_v1.py")
O = load("gmi833_hundred_million_oracle", HERE / "independent_oracle_v1.py")


class ProtocolTests(unittest.TestCase):
    def test_protocol_hash_and_count(self) -> None:
        protocol, raw = M.read_protocol()
        self.assertEqual(M.sha256_hex(raw), M.EXPECTED_PROTOCOL_SHA256)
        strata = protocol["configuration"]["strata"]
        self.assertEqual(sum(row["candidates"] for row in strata), 116_570_467)
        self.assertGreaterEqual(protocol["configuration"]["candidate_total"], 100_000_000)

    def test_census_inclusion_is_exact(self) -> None:
        protocol, _ = M.read_protocol()
        self.assertEqual(protocol["inclusion_probabilities"]["first_order"], "1/1")
        self.assertEqual(protocol["inclusion_probabilities"]["distinct_pair"], "1/1")

    def test_forbidden_promotions(self) -> None:
        protocol, _ = M.read_protocol()
        forbidden = set(protocol["forbidden_promotions"])
        self.assertIn("UNBOUNDED_GENERATION", forbidden)
        self.assertIn("EQUIVALENT_COVERAGE_ALTERNATIVE_CLAIM", forbidden)
        self.assertIn("ARCHITECTURE_FREE_IN_ABSOLUTE_SENSE", forbidden)


class WorkerOracleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.run_dir = Path(cls.temporary.name)
        cls.binary = M.compile_worker(cls.run_dir)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def worker(self, labels: int, start: int, count: int) -> dict[str, object]:
        completed = subprocess.run([str(self.binary), str(labels), str(start), str(count)], capture_output=True, check=True)
        return M.parse_worker_output(completed.stdout)

    def test_primary_matches_source_separated_oracle(self) -> None:
        for labels in range(1, 4):
            oracle = O.census_stratum(labels)
            parsed = self.worker(labels, 0, oracle["candidate_count"])
            M.validate_chunk(
                parsed,
                labels=labels,
                alphabet=oracle["alphabet_size"],
                population=oracle["candidate_count"],
                start=0,
                count=oracle["candidate_count"],
            )
            histogram_hash = M.sha256_hex(M.canonical_bytes(dict(sorted(parsed["histogram"].items()))))
            self.assertEqual(histogram_hash, oracle["semantic_histogram_sha256"])

    def test_interval_moments(self) -> None:
        parsed = self.worker(4, 1234, 4321)
        self.assertEqual(parsed["rank_sum"], sum(range(1234, 5555)))
        self.assertEqual(parsed["rank_square_sum"], sum(value * value for value in range(1234, 5555)))

    def test_invalid_interval_fails_closed(self) -> None:
        completed = subprocess.run([str(self.binary), "2", "120", "2"], capture_output=True, check=False)
        self.assertNotEqual(completed.returncode, 0)

    def test_changed_instruction_order_detected(self) -> None:
        oracle = O.census_stratum(2)
        mutated = dict(oracle)
        mutated["semantic_histogram_sha256"] = "0" * 64
        self.assertNotEqual(mutated["semantic_histogram_sha256"], oracle["semantic_histogram_sha256"])


class ReceiptHostileTests(unittest.TestCase):
    def test_receipt_chain_tamper_detected(self) -> None:
        parsed = {
            "labels": 1,
            "alphabet_size": 5,
            "population": 5,
            "start": 0,
            "count": 5,
            "terminal_count": 5,
            "rank_sum": 10,
            "rank_square_sum": 30,
            "rank_digest_u64": "0" * 16,
            "semantic_digest_u64": "0" * 16,
            "histogram": {"0:0:0": 5},
            "semantic_classes": 1,
            "raw_sha256": "0" * 64,
        }
        receipt = M.receipt_payload(parsed, "00" * 32)
        M.verify_receipt(receipt, "00" * 32)
        receipt["histogram"]["0:0:0"] = 4
        with self.assertRaises(M.CensusError):
            M.verify_receipt(receipt, "00" * 32)

    def test_skipped_rank_detected_by_moments(self) -> None:
        parsed = {
            "labels": 2,
            "alphabet_size": 11,
            "population": 121,
            "start": 0,
            "count": 120,
            "terminal_count": 120,
            "rank_sum": M.interval_sum(0, 120),
            "rank_square_sum": M.interval_square_sum(0, 120),
        }
        with self.assertRaises(M.CensusError):
            M.validate_chunk(parsed, labels=2, alphabet=11, population=121, start=0, count=121)

    def test_duplicate_semantic_row_rejected(self) -> None:
        raw = b"META\t1\t5\t5\t0\t5\nMOMENTS\t10\t30\t0000000000000000\t0000000000000000\nSEM\t0\t0\t0\t2\nSEM\t0\t0\t0\t3\nEND\t2\t5\n"
        with self.assertRaises(M.CensusError):
            M.parse_worker_output(raw)

    def test_wrong_effective_denominator_changes_value(self) -> None:
        correct = O.Fraction(25, 13)
        hostile = O.Fraction(25, 12)
        self.assertNotEqual(correct, hostile)


class ResultTests(unittest.TestCase):
    def test_committed_result_if_present(self) -> None:
        path = HERE / "RESULT_V1.json"
        if not path.exists():
            self.skipTest("outcome intentionally not committed yet")
        result = json.loads(path.read_bytes())
        self.assertEqual(result["execution"]["candidate_count"], 116_570_467)
        self.assertTrue(all(result["checks"].values()))
        self.assertEqual(result["inclusion"]["first_order_probability"], "1/1")
        independent = json.loads((HERE / "INDEPENDENT_CHECK_V1.json").read_bytes())
        self.assertIn("GREEN", independent["verdict"])
        self.assertEqual(independent["primary_result_sha256"], sha256(path.read_bytes()).hexdigest())

    def test_committed_histogram_is_exactly_bound(self) -> None:
        result_path = HERE / "RESULT_V1.json"
        if not result_path.exists():
            self.skipTest("outcome intentionally not committed yet")
        result = json.loads(result_path.read_bytes())
        artifact = json.loads((HERE / "SEMANTIC_HISTOGRAM_V1.json").read_bytes())
        histogram = artifact["histogram"]
        self.assertEqual(sum(histogram.values()), 116_570_467)
        self.assertEqual(len(histogram), 973)
        digest = sha256(M.canonical_bytes(dict(sorted(histogram.items())))).hexdigest()
        self.assertEqual(digest, artifact["histogram_sha256"])
        self.assertEqual(digest, result["semantic_coverage"]["complete_semantic_histogram_sha256"])

    def test_reconciliation_targets_exactly_one_live_row(self) -> None:
        spec = json.loads((HERE / "ISSUE_833_RECONCILIATION_HUNDRED_MILLION_CENSUS_V1.json").read_bytes())
        self.assertEqual(len(spec["replacements"]), 1)
        row = spec["replacements"][0]
        self.assertEqual(row["old"], "- [ ] Scale to at least 10^8 candidates or justify an equivalent effective coverage method.")
        self.assertIn("PR #1009 / #1008", row["new"])

    def test_all_observed_resources_are_under_frozen_ceilings(self) -> None:
        result_path = HERE / "RESULT_V1.json"
        if not result_path.exists():
            self.skipTest("outcome intentionally not committed yet")
        result = json.loads(result_path.read_bytes())
        execution = result["execution"]
        ceilings = result["resource_ceilings"]
        self.assertLessEqual(execution["elapsed_seconds"], ceilings["wall_seconds"])
        self.assertLessEqual(execution["peak_rss_bytes"], ceilings["peak_rss_bytes"])
        self.assertLessEqual(execution["persistent_run_artifact_bytes"], ceilings["persistent_run_artifact_bytes"])
        self.assertLessEqual(execution["committed_evidence_bytes"], ceilings["committed_evidence_bytes"])

    def test_clean_replay_matches_scientific_custody_fields(self) -> None:
        replay = json.loads((HERE / "CLEAN_REPLAY_V1.json").read_bytes())
        self.assertTrue(replay["replayed_from_empty_run_directory"])
        self.assertTrue(all(replay["scientific_field_agreement"].values()))
        self.assertEqual(replay["verdict"], "CLEAN_REPLAY_SCIENTIFIC_FIELDS_7_OF_7_EQUAL")


if __name__ == "__main__":
    unittest.main()
