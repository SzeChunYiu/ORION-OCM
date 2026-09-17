#!/usr/bin/env python3
"""Normal and optimized-safe tests for the independent million-run checker."""

from __future__ import annotations

from collections import Counter
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


I = _load("gmi833_million_independent_checker_tests", HERE / "independent_checker_v1.py")
S = _load(
    "gmi833_scalable_sampling_dependency_for_independent_tests",
    HERE.parent / "gmi-833-scalable-morphology-sampling-v1" / "scalable_morphology_sampling_v1.py",
)


class FrozenProtocolTests(unittest.TestCase):
    def test_registered_protocol_is_byte_locked_and_self_consistent(self):
        protocol = I.load_registered_protocol()
        self.assertEqual(protocol["sample_size"], 1_000_000)
        self.assertEqual(protocol["sample_size"], protocol["chunk_size"] * protocol["chunk_count"])
        self.assertEqual(protocol["budget"], {"code_cells": 8, "register_cells": 4})
        self.assertEqual(I.independent_population_size(8, 4), 266_545_923_745_833_839_720)

    def test_any_protocol_byte_tamper_fails_closed(self):
        payload = bytearray(I.PROTOCOL_PATH.read_bytes())
        payload[payload.index(b"1000000")] = ord("9")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tampered.json"
            path.write_bytes(payload)
            with self.assertRaisesRegex(I.VerificationError, "byte hash drift"):
                I.load_registered_protocol(path)


class IndependentCodecTests(unittest.TestCase):
    def test_digit_codec_is_a_bijection_without_dependency_calls(self):
        for labels, registers in ((1, 1), (2, 1), (3, 2), (8, 4)):
            alphabet = I.instruction_alphabet_size(labels, registers)
            decoded = [I.independent_digit_decode(digit, labels, registers) for digit in range(alphabet)]
            self.assertEqual(len(decoded), len(set(decoded)))
            self.assertEqual(
                [I.independent_digit_encode(code, labels, registers) for code in decoded],
                list(range(alphabet)),
            )

    def test_independent_codec_matches_registered_dependency_at_boundaries(self):
        budget = S.StructuralBudget(8, 4)
        table = I.independent_strata(8, 4)
        probes = {0, 1, I.independent_population_size(8, 4) - 1}
        for item in table:
            probes.add(item.offset)
            probes.add(item.stop - 1)
        for rank in sorted(probes):
            independent = I.independent_unrank(8, 4, rank)
            dependency = S.unrank_program(budget, rank).canonical_code()
            self.assertEqual(independent, dependency)
            self.assertEqual(I.independent_rank(8, 4, independent), rank)

    def test_canonical_candidate_transcript_has_a_fixed_vector(self):
        programs = [I.independent_unrank(2, 1, rank) for rank in range(10)]
        self.assertEqual(
            I.candidate_transcript_digest(programs),
            "9100ddf36f0ce6d73542294a6b67ffefe4e168eab33b71cbff9108d1cf55d460",
        )
        self.assertEqual(
            I.sha256_hex(I.chunk_rank_bytes(tuple(range(10)))),
            "7427877c40fb0361401248f9c96abe6117396bc6ab16811b5b1706274c02443e",
        )

    def test_rank_and_instruction_hostiles_fail_closed(self):
        for operation in (
            lambda: I.independent_unrank(1, 1, -1),
            lambda: I.independent_unrank(1, 1, 5),
            lambda: I.independent_digit_decode(5, 1, 1),
            lambda: I.independent_digit_encode(("HALT", 0, -1, -1), 1, 1),
            lambda: I.independent_digit_encode(("UNKNOWN", 0, 0, -1), 1, 1),
        ):
            with self.subTest(operation=operation), self.assertRaises(I.VerificationError):
                operation()


class IndependentSemanticTests(unittest.TestCase):
    def test_semantics_match_parent_on_cross_stratum_probes(self):
        budget = S.StructuralBudget(8, 4)
        interface = S.PARENT.ObservationInterface(((), (0,), (1,)), 6)
        probes = (0, 1, 2, 4, 5, 100, 1000, 1_000_000, I.independent_population_size(8, 4) - 1)
        for rank in probes:
            independent = I.independent_unrank(8, 4, rank)
            expected = S.PARENT.semantic_key(S.unrank_program(budget, rank), interface)
            expected_text = json.dumps(
                [[status, list(output)] for status, output in expected], separators=(",", ":")
            )
            self.assertEqual(
                I.independent_semantic_key(independent, [[], [0], [1]], 6),
                expected_text,
            )

    def test_semantic_fixed_vectors(self):
        expected = {
            0: '[["BLOCKED_INPUT",[]],["BLOCKED_INPUT",[]],["BLOCKED_INPUT",[]]]',
            1: '[["STEP_LIMIT",[]],["STEP_LIMIT",[]],["STEP_LIMIT",[]]]',
            4: '[["HALTED",[]],["HALTED",[]],["HALTED",[]]]',
            100: '[["STEP_LIMIT",[0,0,0,0,0,0]],["STEP_LIMIT",[0,0,0,0,0,0]],["STEP_LIMIT",[0,0,0,0,0,0]]]',
        }
        for rank, vector in expected.items():
            self.assertEqual(
                I.independent_semantic_key(I.independent_unrank(8, 4, rank), [[], [0], [1]], 6),
                vector,
            )


class IndependentSamplingTests(unittest.TestCase):
    def test_counter_entropy_has_a_fixed_vector(self):
        entropy = I.IndependentCounterEntropy(
            b"gmi-833-f-million-candidate-execution-v1-registered-replay"
        )
        observed = [entropy.uniform_below(upper) for upper in (2, 3, 5, 17, 257, 65537)]
        self.assertEqual(observed, [0, 1, 3, 13, 172, 24776])
        self.assertEqual((entropy.counter, entropy.raw_candidates, entropy.rejections), (11, 11, 5))

    def test_floyd_small_vector_and_sampler_hostiles(self):
        sample, entropy = I.independent_floyd_sample(10, 4, b"test-vector")
        self.assertEqual(sample, (2, 4, 5, 6))
        self.assertGreater(entropy.raw_candidates, 0)
        with self.assertRaises(I.VerificationError):
            I.independent_floyd_sample(3, 4, b"x")
        with self.assertRaises(I.VerificationError):
            I.IndependentCounterEntropy(b"")

    def test_rank_transcript_parser_is_canonical_and_strict(self):
        self.assertEqual(
            I.parse_rank_transcript(b"0\n2\n9\n", expected_count=3, population=10),
            (0, 2, 9),
        )
        hostile = (
            b"0\n2\n9",
            b"0\n02\n9\n",
            b"0\n2\n2\n",
            b"0\n2\n10\n",
            b"0\n-2\n9\n",
        )
        for payload in hostile:
            with self.subTest(payload=payload), self.assertRaises(I.VerificationError):
                I.parse_rank_transcript(payload, expected_count=3, population=10)

    def test_deterministic_spot_replay_has_fixed_positions_and_digest(self):
        self.assertEqual(
            I.deterministic_spot_indices(100, 10),
            (0, 2, 20, 35, 43, 51, 56, 63, 76, 99),
        )
        self.assertEqual(
            I.deterministic_spot_replay(
                tuple(range(100)),
                code_cells=2,
                register_cells=1,
                input_words=[[], [0], [1]],
                step_cap=6,
                count=10,
            ),
            (10, "fe4336b8cc6c4ba59dbd1a463faeb39d6b2ccae5c596f605bc5f7b268cc675fe"),
        )
        altered = tuple(range(99)) + (100,)
        self.assertNotEqual(
            I.deterministic_spot_replay(
                altered,
                code_cells=2,
                register_cells=1,
                input_words=[[], [0], [1]],
                step_cap=6,
                count=10,
            )[1],
            "fe4336b8cc6c4ba59dbd1a463faeb39d6b2ccae5c596f605bc5f7b268cc675fe",
        )


def _valid_chunk_fixture() -> tuple[dict[str, object], tuple[int, ...]]:
    ranks = tuple(range(10))
    programs = tuple(I.independent_unrank(2, 1, rank) for rank in ranks)
    resources = Counter(f"labels={len(program[1])},registers={program[0]}" for program in programs)
    semantics = Counter(I.independent_semantic_key(program, [[], [0], [1]], 6) for program in programs)
    receipt: dict[str, object] = {
        "schema": "GMI833MillionCandidateChunkReceiptV1",
        "index": 0,
        "sample_start": 0,
        "sample_stop": len(ranks),
        "first_rank": str(ranks[0]),
        "last_rank": str(ranks[-1]),
        "rank_transcript_sha256": I.sha256_hex(I.chunk_rank_bytes(ranks)),
        "candidate_transcript_sha256": I.candidate_transcript_digest(programs),
        "semantic_counts_sha256": I.sha256_hex(I.canonical_json_bytes(dict(sorted(semantics.items())))),
        "generated_count": len(ranks),
        "validated_count": len(ranks),
        "round_trip_count": len(ranks),
        "resource_counts": dict(sorted(resources.items())),
        "semantic_counts": dict(sorted(semantics.items())),
        "prior_chain_sha256": I.GENESIS_CHAIN_SHA256,
    }
    receipt["chain_sha256"] = I.chunk_chain_hash(I.GENESIS_CHAIN_SHA256, receipt)
    return receipt, ranks


class ReceiptAndTamperTests(unittest.TestCase):
    def _verify(self, receipt: dict[str, object], ranks: tuple[int, ...]) -> None:
        I.verify_chunk_receipt(
            receipt,
            ranks,
            expected_index=0,
            prior_chain_sha256=I.GENESIS_CHAIN_SHA256,
            code_cells=2,
            register_cells=1,
            input_words=[[], [0], [1]],
            step_cap=6,
        )

    def test_valid_chunk_is_recomputed_independently(self):
        receipt, ranks = _valid_chunk_fixture()
        chain, resources, semantics, sequence = I.verify_chunk_receipt(
            receipt,
            ranks,
            expected_index=0,
            prior_chain_sha256=I.GENESIS_CHAIN_SHA256,
            code_cells=2,
            register_cells=1,
            input_words=[[], [0], [1]],
            step_cap=6,
        )
        self.assertEqual(chain, receipt["chain_sha256"])
        self.assertEqual(sum(resources.values()), 10)
        self.assertEqual(sum(semantics.values()), 10)
        self.assertEqual(len(sequence), 10)

    def test_each_protected_chunk_surface_detects_tampering(self):
        receipt, ranks = _valid_chunk_fixture()
        mutations = (
            ("rank hash", lambda row: row.__setitem__("rank_transcript_sha256", "0" * 64)),
            ("candidate hash", lambda row: row.__setitem__("candidate_transcript_sha256", "0" * 64)),
            ("semantic hash", lambda row: row.__setitem__("semantic_counts_sha256", "0" * 64)),
            ("resource count", lambda row: row["resource_counts"].__setitem__("labels=1,registers=1", 9)),
            ("boolean resource count", lambda row: row["resource_counts"].__setitem__("labels=1,registers=1", True)),
            ("semantic count", lambda row: next(iter(row["semantic_counts"])) and row["semantic_counts"].__setitem__(next(iter(row["semantic_counts"])), 99)),
            ("prior chain", lambda row: row.__setitem__("prior_chain_sha256", "1" * 64)),
            ("terminal chain", lambda row: row.__setitem__("chain_sha256", "2" * 64)),
        )
        for label, mutate in mutations:
            hostile = copy.deepcopy(receipt)
            mutate(hostile)
            with self.subTest(label=label), self.assertRaises(I.VerificationError):
                self._verify(hostile, ranks)

    def test_rank_substitution_detected_even_if_chunk_metadata_is_unchanged(self):
        receipt, ranks = _valid_chunk_fixture()
        hostile_ranks = ranks[:-1] + (10,)
        with self.assertRaises(I.VerificationError):
            self._verify(receipt, hostile_ranks)

    def test_checkpoint_validates_custody_and_aggregates(self):
        receipt, ranks = _valid_chunk_fixture()
        _, resources, semantics, sequence = I.verify_chunk_receipt(
            receipt,
            ranks,
            expected_index=0,
            prior_chain_sha256=I.GENESIS_CHAIN_SHA256,
            code_cells=2,
            register_cells=1,
            input_words=[[], [0], [1]],
            step_cap=6,
        )
        checkpoint = {
            "schema": "GMI833MillionCandidateCheckpointV1",
            "protocol_sha256": I.REGISTERED_PROTOCOL_SHA256,
            "dependency_module_git_blob": "a" * 40,
            "next_chunk_index": 1,
            "rank_transcript_sha256": "b" * 64,
            "generated_count": 10,
            "validated_count": 10,
            "round_trip_count": 10,
            "resource_counts": dict(sorted(resources.items())),
            "semantic_counts": dict(sorted(semantics.items())),
            "discovery_checkpoints": {"10": len(semantics)},
            "terminal_chunk_chain_sha256": receipt["chain_sha256"],
            "restart_count": 0,
        }
        kwargs = dict(
            protocol_sha256=I.REGISTERED_PROTOCOL_SHA256,
            dependency_blob="a" * 40,
            rank_transcript_sha256="b" * 64,
            expected_chunks=1,
            expected_count=10,
            terminal_chain_sha256=str(receipt["chain_sha256"]),
            resource_counts=resources,
            semantic_counts=semantics,
            discovery_checkpoints={"10": len(set(sequence))},
        )
        I.verify_checkpoint(checkpoint, **kwargs)
        for field in ("protocol_sha256", "dependency_module_git_blob", "next_chunk_index", "semantic_counts"):
            hostile = copy.deepcopy(checkpoint)
            hostile[field] = {} if field == "semantic_counts" else "tampered"
            with self.subTest(field=field), self.assertRaises(I.VerificationError):
                I.verify_checkpoint(hostile, **kwargs)


class CommittedIndependentEvidenceTests(unittest.TestCase):
    def test_independent_receipt_is_canonical_and_bound_to_final_result(self):
        receipt_path = HERE / "INDEPENDENT_CHECK_V1.json"
        raw = receipt_path.read_bytes()
        receipt = json.loads(raw)
        self.assertEqual(raw, json.dumps(receipt, indent=2, sort_keys=True).encode("utf-8") + b"\n")
        result_raw = (HERE / "RESULT_V1.json").read_bytes()
        result = json.loads(result_raw)
        execution = result["execution"]
        protocol = I.load_registered_protocol()
        dependency_path = HERE.parent.parent / protocol["generator_dependency"]["module"]
        self.assertEqual(receipt["schema"], I.CHECKER_SCHEMA)
        self.assertEqual(receipt["verdict"], "INDEPENDENT_CHECKS_PASS")
        self.assertTrue(receipt["registered_sample_replayed"])
        self.assertEqual(receipt["protocol_sha256"], I.REGISTERED_PROTOCOL_SHA256)
        self.assertEqual(receipt["result_sha256"], I.sha256_hex(result_raw))
        self.assertEqual(receipt["sample_size"], protocol["sample_size"])
        self.assertEqual(receipt["chunks_verified"], protocol["chunk_count"])
        self.assertEqual(receipt["population"], result["population"]["exact_size"])
        self.assertEqual(receipt["observed_semantic_keys"], result["semantic_metrics"]["observed_semantic_keys"])
        self.assertEqual(receipt["rank_transcript_sha256"], execution["rank_transcript_sha256"])
        self.assertEqual(receipt["terminal_chunk_chain_sha256"], execution["terminal_chunk_chain_sha256"])
        self.assertEqual(receipt["final_checkpoint_sha256"], execution["final_checkpoint_sha256"])
        self.assertEqual(
            receipt["dependency_module_git_blob"],
            I.git_blob_sha1(dependency_path.read_bytes()),
        )
        self.assertEqual(receipt["deterministic_spot_replay_count"], 256)
        self.assertEqual(len(bytes.fromhex(receipt["deterministic_spot_replay_sha256"])), 32)


if __name__ == "__main__":
    unittest.main(verbosity=2)
