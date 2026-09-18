#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("finite_candidate_space_v1", HERE / "finite_candidate_space_v1.py")
M = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)

ORACLE_SPEC = importlib.util.spec_from_file_location("independent_oracle_v1_test", HERE / "independent_oracle_v1.py")
O = importlib.util.module_from_spec(ORACLE_SPEC)
assert ORACLE_SPEC and ORACLE_SPEC.loader
ORACLE_SPEC.loader.exec_module(O)


class FiniteCandidateSpaceTests(unittest.TestCase):
    def setUp(self):
        self.interface = M.ObservationInterface(((), (0,), (1,)), 6)

    def test_parent_artifacts_are_exactly_pinned(self):
        audit = M.audit_parents()
        self.assertTrue(audit["all_ok"])
        self.assertEqual(len(audit["rows"]), 5)

    def test_parent_mutation_fails_closed(self):
        root = M.repo_root()
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            for _, relative, _, _, _ in M.PARENT_PINS:
                target = tmp / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(root / relative, target)
            victim = tmp / M.PARENT_PINS[1][1]
            victim.write_bytes(victim.read_bytes() + b"\n")
            self.assertFalse(M.audit_parents(tmp)["all_ok"])

    def test_exact_additive_resource_vector(self):
        program = M.CandidateProgram(2, (M.Instruction("HALT"), M.Instruction("INC", 1, 0)))
        M.validate_program(program)
        self.assertEqual(program.resource_vector(), (2, 2))
        code_atoms = [(1, 0) for _ in program.instructions]
        register_atoms = [(0, 1) for _ in range(program.register_count)]
        self.assertEqual(tuple(sum(row[i] for row in code_atoms + register_atoms) for i in range(2)), (2, 2))

    def test_closed_form_counts_and_registered_126_slice(self):
        expected = {(1, 1): 5, (2, 1): 126, (1, 2): 14, (2, 2): 576, (3, 1): 6985}
        for pair, count in expected.items():
            with self.subTest(budget=pair):
                budget = M.StructuralBudget(*pair)
                self.assertEqual(M.candidate_count(budget), count)
                self.assertEqual(O.closed_form_count(*pair), count)

    def test_constructive_enumerator_matches_independent_cartesian_oracle(self):
        for pair in ((1, 1), (2, 1), (1, 2), (2, 2), (3, 1)):
            with self.subTest(budget=pair):
                actual = M.enumerate_candidates(M.StructuralBudget(*pair))
                actual_codes = {row.canonical_code() for row in actual}
                oracle_codes = set(O.enumerate_raw_codes(*pair))
                self.assertEqual(actual_codes, oracle_codes)
                self.assertEqual(len(actual), len(actual_codes))

    def test_budget_and_small_enumeration_contracts_fail_closed(self):
        for values in ((0, 1), (1, 0), (-1, 1), (1, True), (1.0, 1)):
            with self.subTest(values=values), self.assertRaises(ValueError):
                M.StructuralBudget(*values)
        with self.assertRaises(ValueError):
            M.enumerate_candidates(M.StructuralBudget(3, 2), max_candidates=10)
        with self.assertRaises(ValueError):
            M.enumerate_candidates(M.StructuralBudget(1, 1), max_candidates=True)

    def test_program_typing_fails_closed(self):
        bad = (
            M.CandidateProgram(0, (M.Instruction("HALT"),)),
            M.CandidateProgram(1, ()),
            M.CandidateProgram(1, (M.Instruction("OTHER"),)),
            M.CandidateProgram(1, (M.Instruction("HALT", 0),)),
            M.CandidateProgram(1, (M.Instruction("INC", 1, 0),)),
            M.CandidateProgram(1, (M.Instruction("INC", 0, 1),)),
            M.CandidateProgram(1, (M.Instruction("DECJZ", 0, 0, None),)),
        )
        for program in bad:
            with self.subTest(program=program), self.assertRaises(ValueError):
                M.validate_program(program)

    def test_execution_is_exactly_the_parent_semantics(self):
        program = M.CandidateProgram(
            1,
            (
                M.Instruction("READ", 0, 1),
                M.Instruction("EMIT", 0, 2),
                M.Instruction("HALT"),
            ),
        )
        self.assertEqual(M.protected_observation(program, (7,), 6), ("HALTED", (7,)))
        self.assertEqual(M.protected_observation(program, (), 6), ("BLOCKED_INPUT", ()))
        loop = M.CandidateProgram(1, (M.Instruction("INC", 0, 0),))
        self.assertEqual(M.protected_observation(loop, (), 3), ("STEP_LIMIT", ()))

    def test_interface_contract_fails_closed(self):
        for words, cap in (((), 1), (((), ()), 1), (((-1,),), 1), (((True,),), 1), (((),), 0)):
            with self.subTest(words=words, cap=cap), self.assertRaises(ValueError):
                M.ObservationInterface(words, cap)

    def test_semantic_equivalence_is_an_equivalence_relation(self):
        programs = M.enumerate_candidates(M.StructuralBudget(2, 1))
        keys = [M.semantic_key(program, self.interface) for program in programs]
        for i, left in enumerate(programs):
            self.assertTrue(M.semantic_equivalent(left, left, self.interface))
            for j, right in enumerate(programs):
                self.assertEqual(
                    M.semantic_equivalent(left, right, self.interface),
                    M.semantic_equivalent(right, left, self.interface),
                )
                if keys[i] == keys[j]:
                    for k, third in enumerate(programs):
                        if keys[j] == keys[k]:
                            self.assertTrue(M.semantic_equivalent(left, third, self.interface))

    def test_semantic_quotient_collapses_duplicates_exactly_once(self):
        programs = M.enumerate_candidates(M.StructuralBudget(2, 1))
        quotient = M.semantic_quotient(programs, self.interface)
        self.assertEqual(len(programs), 126)
        self.assertEqual(len(quotient), 18)
        self.assertEqual(sum(row["multiplicity"] for row in quotient), 126)
        self.assertEqual(len({row["semantic_key"] for row in quotient}), 18)
        for row in quotient:
            self.assertEqual(row["representative"], min(row["members"], key=lambda item: item.canonical_code()))
        with self.assertRaises(ValueError):
            M.semantic_quotient((programs[0], programs[0]), self.interface)

    def test_equivalence_is_interface_relative_not_global(self):
        halt_after_increment = M.CandidateProgram(
            1,
            (M.Instruction("INC", 0, 1), M.Instruction("HALT")),
        )
        emit_after_increment = M.CandidateProgram(
            1,
            (M.Instruction("INC", 0, 1), M.Instruction("EMIT", 0, 1)),
        )
        cap_one = M.ObservationInterface(((),), 1)
        cap_two = M.ObservationInterface(((),), 2)
        self.assertNotEqual(halt_after_increment, emit_after_increment)
        self.assertTrue(M.semantic_equivalent(halt_after_increment, emit_after_increment, cap_one))
        self.assertFalse(M.semantic_equivalent(halt_after_increment, emit_after_increment, cap_two))

    def test_descriptor_factors_only_through_declared_invariants(self):
        observations = (("HALTED", (0,)), ("STEP_LIMIT", ()))
        descriptor = M.morphology_descriptor_from_invariants(observations, (2, 1), 4)
        self.assertEqual(descriptor["resource_vector"], [2, 1])
        self.assertEqual(descriptor["developmental_distance"], 4)
        forbidden_keys = {"architecture", "family", "implementation_name", "source_token", "program"}
        self.assertTrue(forbidden_keys.isdisjoint(descriptor))
        self.assertEqual(
            descriptor,
            M.morphology_descriptor_from_invariants(observations, (2, 1), 4),
        )

    def test_descriptor_keeps_behavior_resources_and_development_distinct(self):
        halt1 = M.CandidateProgram(1, (M.Instruction("HALT"),))
        halt2 = M.CandidateProgram(1, (M.Instruction("HALT"), M.Instruction("HALT")))
        self.assertTrue(M.semantic_equivalent(halt1, halt2, self.interface))
        self.assertNotEqual(M.morphology_descriptor(halt1, self.interface, 0), M.morphology_descriptor(halt2, self.interface, 0))
        self.assertNotEqual(M.morphology_descriptor(halt1, self.interface, 0), M.morphology_descriptor(halt1, self.interface, 1))

    def test_descriptor_contract_fails_closed(self):
        bad = (
            ((), (1, 1), 0),
            (("OTHER", ()), (1, 1), 0),
            (("HALTED", [0]), (1, 1), 0),
            (("HALTED", (-1,)), (1, 1), 0),
            (("HALTED", ()), (0, 1), 0),
            (("HALTED", ()), (1, 1), -1),
        )
        for observations, resources, distance in bad:
            with self.subTest(case=(observations, resources, distance)), self.assertRaises(ValueError):
                M.morphology_descriptor_from_invariants(observations, resources, distance)

    def test_all_surface_remints_roundtrip_and_preserve_descriptors(self):
        programs = M.enumerate_candidates(M.StructuralBudget(2, 1))
        tokens = ("u0", "u1", "u2", "u3", "u4")
        checks = 0
        from itertools import permutations
        for permuted in permutations(tokens):
            remint = dict(zip(M.SEMANTIC_OPS, permuted))
            for program in programs:
                decoded = M.decode_reminted(M.remint_program(program, remint), remint)
                self.assertEqual(decoded, program)
                distance = sum(program.resource_vector())
                self.assertEqual(
                    M.morphology_descriptor(decoded, self.interface, distance),
                    M.morphology_descriptor(program, self.interface, distance),
                )
                checks += 1
        self.assertEqual(checks, 15_120)

    def test_malformed_remints_fail_closed_and_semantic_hostile_is_detected(self):
        good = dict(zip(M.SEMANTIC_OPS, ("a", "b", "c", "d", "e")))
        program = M.CandidateProgram(1, (M.Instruction("HALT"),))
        for bad in (
            {},
            {**good, "EXTRA": "f"},
            {**good, "HALT": "a"},
            {**good, "HALT": ""},
        ):
            with self.subTest(remint=bad), self.assertRaises(ValueError):
                M.remint_program(program, bad)
        original = M.CandidateProgram(1, (M.Instruction("INC", 0, 0),))
        surface = M.remint_program(original, good)
        dishonest_decoder = dict(good)
        dishonest_decoder["INC"], dishonest_decoder["READ"] = dishonest_decoder["READ"], dishonest_decoder["INC"]
        changed = M.decode_reminted(surface, dishonest_decoder)
        self.assertNotEqual(original, changed)
        self.assertNotEqual(M.semantic_key(original, self.interface), M.semantic_key(changed, self.interface))

    def test_register_relabeling_is_semantics_and_descriptor_invariant(self):
        programs = M.enumerate_candidates(M.StructuralBudget(2, 2))
        checked = 0
        nontrivial = 0
        for program in programs:
            if program.register_count != 2:
                continue
            relabelled = M.relabel_registers(program, (1, 0))
            nontrivial += int(relabelled != program)
            self.assertEqual(M.semantic_key(program, self.interface), M.semantic_key(relabelled, self.interface))
            distance = sum(program.resource_vector())
            self.assertEqual(
                M.morphology_descriptor(program, self.interface, distance),
                M.morphology_descriptor(relabelled, self.interface, distance),
            )
            checked += 1
        self.assertEqual(checked, 450)
        self.assertEqual(nontrivial, 448)
        with self.assertRaises(ValueError):
            M.relabel_registers(M.CandidateProgram(2, (M.Instruction("HALT"),)), (0, 0))

        control = M.CandidateProgram(
            2,
            (M.Instruction("READ", 0, 1), M.Instruction("EMIT", 0, 2), M.Instruction("HALT")),
        )
        inconsistent = M.CandidateProgram(
            2,
            (M.Instruction("READ", 1, 1), M.Instruction("EMIT", 0, 2), M.Instruction("HALT")),
        )
        self.assertNotEqual(M.semantic_key(control, self.interface), M.semantic_key(inconsistent, self.interface))

    def test_registered_census_counts(self):
        census = M.registered_census()
        self.assertEqual(census["independent_oracle_candidate_comparisons"], 721)
        self.assertEqual(census["registered_candidates"], 126)
        self.assertEqual(census["registered_semantic_classes"], 18)
        self.assertEqual(census["registered_collapse_count"], 108)
        self.assertEqual(census["syntax_remint_descriptor_checks"], 15_120)
        self.assertEqual(census["register_relabel_descriptor_checks"], 450)
        self.assertEqual(census["nontrivial_register_relabels"], 448)
        self.assertTrue(census["semantics_changing_hostile_detected"])
        self.assertTrue(census["inconsistent_register_rename_hostile_detected"])

    def test_scientific_ledger_and_package_contracts(self):
        self.assertEqual(
            M.validate_scientific_ledger(),
            {"claim_ledgers": 4, "open_gaps": 7, "closure_level": "REGISTERED_FINITE_SCOPE_ONLY"},
        )
        self.assertEqual(
            M.validate_package_contracts(),
            {"manifest_ok": True, "reconciliation_ok": True, "reconciliation_rows": 4, "source_pr": M.SOURCE_PR},
        )

    def test_receipt_is_green_and_byte_stable(self):
        receipt = M.build_receipt()
        self.assertEqual(receipt["verdict"], "GREEN")
        self.assertTrue(all(receipt["checks"].values()))
        checked_in = (HERE / "RESULT_V1.json").read_text(encoding="utf-8")
        self.assertEqual(M.canonical_json(receipt), checked_in)
        self.assertEqual(json.loads(checked_in), receipt)

    def test_claim_boundary_keeps_large_scale_work_open(self):
        receipt = M.build_receipt({"all_ok": True, "rows": []})
        self.assertEqual(receipt["claim_ceiling"], M.CLAIM_CEILING)
        self.assertIn("UNBOUNDED_PROGRAM_EQUIVALENCE_DECIDED", receipt["forbidden_promotions"])
        self.assertIn("SCALABLE_LARGE_BUDGET_SAMPLING", receipt["forbidden_promotions"])
        self.assertIn("MILLION_SCALE_GENERATION", receipt["forbidden_promotions"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
