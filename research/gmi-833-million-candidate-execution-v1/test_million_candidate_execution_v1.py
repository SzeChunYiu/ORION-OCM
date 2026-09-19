#!/usr/bin/env python3
"""Focused tests for the registered million-candidate executor."""

from __future__ import annotations

from collections import Counter
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "million_candidate_execution_v1.py"
SPEC = importlib.util.spec_from_file_location("gmi833_million_executor_tests", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load executor")
M = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


class MillionCandidateExecutorTests(unittest.TestCase):
    def test_protocol_and_dependency_are_pinned(self) -> None:
        protocol, raw, digest = M.load_protocol()
        self.assertEqual(protocol["sample_size"], 1_000_000)
        self.assertEqual(protocol["generator_dependency"]["exact_head"], M.EXPECTED_DEPENDENCY_HEAD)
        self.assertEqual(M.sha256_hex(raw), digest)
        dependency = HERE.parent / "gmi-833-scalable-morphology-sampling-v1" / "scalable_morphology_sampling_v1.py"
        self.assertEqual(M.git_blob_sha(dependency.read_bytes()), M.EXPECTED_DEPENDENCY_BLOB)

    def test_registered_population_is_large_enough(self) -> None:
        budget = M.SAMPLING.StructuralBudget(8, 4)
        population = M.SAMPLING.population_size(budget)
        self.assertEqual(population, 266_545_923_745_833_839_720)
        self.assertGreater(population, 1_000_000)
        self.assertEqual(len(M.SAMPLING.strata(budget)), 32)

    def test_direct_semantics_matches_parent_exhaustively_on_small_census(self) -> None:
        interface = M.SAMPLING.PARENT.ObservationInterface(((), (0,), (1,)), 6)
        for program in M.SAMPLING.PARENT.enumerate_candidates(
            M.SAMPLING.StructuralBudget(2, 2)
        ):
            direct = M.protected_semantic_key(program, interface.input_words, interface.step_cap)
            self.assertEqual(direct, M.SAMPLING.PARENT.semantic_key(program, interface))

    def test_rank_transcript_is_exact_and_byte_stable(self) -> None:
        ranks = (0, 12, 999)
        self.assertEqual(M.rank_transcript_bytes(ranks), b"0\n12\n999\n")
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory)
            budget = M.SAMPLING.StructuralBudget(2, 2)
            first = M.ensure_rank_transcript(run_dir, budget, 100, b"unit-test-seed")
            second = M.ensure_rank_transcript(run_dir, budget, 100, b"unit-test-seed")
            self.assertEqual(first, second)
            self.assertEqual(len(first[0]), len(set(first[0])))
            self.assertEqual(M.sha256_hex((run_dir / "ranks_v1.txt").read_bytes()), first[2])

    def test_chunk_receipt_is_deterministic_and_chained(self) -> None:
        budget = M.SAMPLING.StructuralBudget(2, 2)
        entropy = M.SAMPLING.CounterEntropy(b"chunk-test")
        ranks = M.SAMPLING.global_srswor(budget, 100, entropy.uniform_below)
        first, sequence = M.process_chunk(0, ranks, budget, ((), (0,), (1,)), 6, M.GENESIS_CHAIN)
        second, sequence_again = M.process_chunk(0, ranks, budget, ((), (0,), (1,)), 6, M.GENESIS_CHAIN)
        self.assertEqual(first, second)
        self.assertEqual(sequence, sequence_again)
        self.assertEqual(first["generated_count"], 100)
        self.assertEqual(sum(first["semantic_counts"].values()), 100)
        self.assertEqual(sum(first["resource_counts"].values()), 100)
        base = dict(first)
        chain = base.pop("chain_sha256")
        self.assertEqual(
            chain,
            M.sha256_hex(bytes.fromhex(M.GENESIS_CHAIN) + M.canonical_bytes(base)),
        )
        altered = dict(first)
        altered["first_rank"] = str(int(altered["first_rank"]) + 1)
        with self.assertRaises(RuntimeError):
            M._validate_chunk_shape(altered, first)

    def test_checkpoint_is_canonical_and_fail_closed(self) -> None:
        checkpoint = M._checkpoint_payload(
            "a" * 64,
            "b" * 64,
            1,
            3,
            Counter({"labels=1,registers=1": 3}),
            Counter({'[["HALTED",[]]]': 3}),
            {"3": 1},
            "c" * 64,
            0,
        )
        self.assertEqual(checkpoint["generated_count"], 3)
        self.assertEqual(checkpoint["validated_count"], 3)
        self.assertEqual(checkpoint["round_trip_count"], 3)
        self.assertEqual(json.loads(M.canonical_bytes(checkpoint)), checkpoint)


if __name__ == "__main__":
    unittest.main()
