"""Exact registered witnesses, premise mutations, relocation and authority checks."""
from pathlib import Path
from fractions import Fraction as F
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_finite_quantum_v1 import HERE, assumptions, decisive_relation, run
from classical_parent_v1 import classical_optimum
from finite_witnesses_v1 import (assistance_control, factor_orientation_control,
    mixed_support_controls, random_access_controls, relation_census, shared_seed_control)
from hostile_controls_v1 import NAMES, example, run_hostile_controls
from quantum_parent_v1 import quantum_parent, verify_sources
from quantum_witness_v1 import task_shape, task_fingerprint, verify, verify_registered
from rational_matrix_v1 import identity, multiply, ray_state, transpose


class FiniteQuantumTests(unittest.TestCase):
    def test_full_relational_census_matches_independent_bounds(self):
        result = relation_census()
        self.assertEqual(result["dimension_histogram"], {1: 169, 2: 168, 3: 6})
        self.assertEqual(result["promised_pairs_checked"], 1029)

    def test_pairwise_compatibility_does_not_replace_common_intersection(self):
        result = decisive_relation()
        self.assertTrue(result["pairwise_compatible"])
        self.assertFalse(result["common_action_exists"])
        self.assertEqual(result["dimension"], 2)

    def test_mixed_support_preserves_adequacy_not_distribution(self):
        self.assertEqual(mixed_support_controls()["response_distributions_changed"], 24)

    def test_query_owner_and_time_change_the_protocol_class(self):
        result = random_access_controls()
        self.assertEqual(result["original_quantum_lower_dimension"], 4)
        self.assertEqual(result["sender_also_knows_index_dimension"], 2)
        self.assertFalse(result["same_interface"])

    def test_shared_seed_is_fixed_not_independently_averaged(self):
        result = shared_seed_control()
        self.assertEqual(result["fixed_seed_dimensions"], [2, 2])
        self.assertEqual(result["correlated_success_each_input"], (F(1), F(1)))
        self.assertEqual(result["independently_averaged_success_each_input"], [F(1, 2), F(1, 2)])
        self.assertFalse(result["independent_averaging_preserves_protocol"])

    def test_general_factors_require_correct_adjoint_orientation(self):
        self.assertTrue(factor_orientation_control()["non_symmetric_factor_control"])

    def test_declared_assistance_changes_resource_boundary(self):
        result = assistance_control()
        self.assertEqual((result["sent_subsystem_dimension"], result["joint_receiver_dimension"]),
                         (2, 4))
        self.assertFalse(result["unassisted_protocol_class"])

    def test_strong_quantum_parent_and_legal_isometries(self):
        result = quantum_parent()
        self.assertEqual((result["classical_minimum_alphabet"], result["quantum_minimum_dimension"]),
                         (5, 4))
        self.assertEqual((result["promised_pairs_checked"], result["compiled_isometries"]), (74, 37))

    def test_every_hostile_control_rejects(self):
        rejected = run_hostile_controls()
        self.assertEqual(rejected, list(NAMES))
        self.assertEqual(len(set(rejected)), 15)

    def test_basis_encoding_constructs_arbitrary_finite_promise(self):
        task = {"actions": 3, "allowed": ((frozenset((0,)), None),
                (frozenset((1, 2)), frozenset((0, 2))),
                (None, frozenset((1,))))}
        parent = classical_optimum(task)
        self.assertLessEqual(parent["dimension"], len(task["allowed"]))
        self.assertEqual(verify(task, parent["rays"], parent["factors"])["promised_pairs_checked"], 4)

    def test_nonprojective_effects_are_admitted(self):
        task = {"actions": 3, "allowed": ((frozenset((0, 1)),), (frozenset((2,)),))}
        factors = ((((F(3, 5), 0), (0, 0)), ((F(4, 5), 0), (0, 0)),
                    ((0, 0), (0, 1))),)
        result = verify(task, identity(2), factors)
        self.assertEqual(result["probabilities"][0][2], (F(9, 25), F(16, 25), F(0)))
        v = result["isometries"][0]
        self.assertEqual(multiply(transpose(v), v), identity(2))

    def test_rays_are_normalized_by_exact_denominator(self):
        task, _, factors = example()
        result = verify(task, ((7, 0), (0, 11)), factors)
        self.assertEqual(result["probabilities"][0][2], (F(1), F(0)))

    def test_task_registration_blocks_coverage_weakening(self):
        task, rays, factors = example()
        signature = task_fingerprint(task)
        task["allowed"][1][0] = None
        self.assertEqual(verify(task, rays, factors)["promised_pairs_checked"], 1)
        with self.assertRaisesRegex(ValueError, "registered obligation"):
            verify_registered(task, rays, factors, signature)

    def test_empty_registers_are_separate_from_main_theorem(self):
        for task in ({"actions": 0, "allowed": ((frozenset((0,)),),)},
                     {"actions": 2, "allowed": ((None,),)},
                     {"actions": 2, "allowed": ()}):
            with self.subTest(task=task), self.assertRaises(ValueError):
                task_shape(task)

    def test_source_bound_parent_inputs(self):
        self.assertEqual(len(verify_sources()["files"]), 4)

    def test_assumption_drift_does_not_license_assistance(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            data = assumptions()
            data["preshared_entanglement"] = True
            (target / "ASSUMPTIONS_V1.json").write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "assumption register drift"):
                assumptions(target)

    def test_parent_source_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "unit"
            shutil.copytree(HERE, target)
            path = target / "raw/grand_gmi_quantum_cut_scope_checks_v1.py"
            path.write_bytes(path.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "archived parent drift"):
                verify_sources(target)

    def test_receipt_exact_replay(self):
        expected = json.loads((HERE / "FINITE_QUANTUM_COVER_RECEIPT_V1.json").read_bytes())
        self.assertEqual(run(), expected)

    def test_relocation_and_isolated_imports(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "copied"
            shutil.copytree(HERE, target)
            command = [sys.executable, "-I", "-B"] + (["-O"] if sys.flags.optimize else [])
            command += [str(target / "check_finite_quantum_v1.py")]
            result = subprocess.run(command, cwd=directory, capture_output=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, (HERE / "FINITE_QUANTUM_COVER_RECEIPT_V1.json").read_bytes())


if __name__ == "__main__":
    unittest.main()
