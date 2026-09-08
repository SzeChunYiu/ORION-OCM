import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("g2_length_scaling_experiment", HERE / "experiment.py")
E = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(E)


class TestFrozenDesign(unittest.TestCase):
    def test_method_source_is_pinned(self):
        path = E.SRC / "ocm" / "learning" / "methods.py"
        self.assertEqual(E.git_blob_sha1(path), E.METHOD_BLOB)

    def test_partition_is_disjoint_and_minimum_length_bound(self):
        validation, test = E.frozen_partition()
        population = E.minimal_length_population(6)
        self.assertEqual(len(validation), E.VALIDATION_N)
        self.assertEqual(len(test), E.TEST_N)
        self.assertTrue({t.fingerprint for t in validation}.isdisjoint(
            {t.fingerprint for t in test}
        ))
        self.assertTrue(all(population[t.fingerprint][0] == 5 for t in validation))
        self.assertTrue(all(population[t.fingerprint][0] == 6 for t in test))

    def test_partition_excludes_acquisition_and_legacy_validation(self):
        validation, test = E.frozen_partition()
        excluded = {
            t.fingerprint for t in E.TRAINING_TASKS + E.LEGACY_VALIDATION
        }
        self.assertFalse(excluded & {t.fingerprint for t in validation + test})

    def test_rank_is_deterministic_and_salt_specific(self):
        fingerprint = E.TRAINING_TASKS[0].fingerprint
        self.assertEqual(
            E.stable_rank(E.VALIDATION_SALT, fingerprint),
            E.stable_rank(E.VALIDATION_SALT, fingerprint),
        )
        self.assertNotEqual(
            E.stable_rank(E.VALIDATION_SALT, fingerprint),
            E.stable_rank(E.TEST_SALT, fingerprint),
        )

    def test_existing_training_still_yields_a_nonempty_method(self):
        _training, method, _slots = E.learn_fixed_method()
        self.assertTrue(method.fragments)

    def test_trace_attributes_unlearned_solution_to_primitive_stream(self):
        task = E.M.PolynomialTask(
            "trace-control",
            E.M.normal_form(("inc",)),
        )
        result, origin = E.checked_solve(
            task, E.M.SearchBudget(slots=20, max_length=1)
        )
        self.assertTrue(E.M.verify_solution(task, result))
        self.assertEqual(origin, "primitive")

    def test_compare_rows_counts_only_guided_strict_wins(self):
        baseline = [
            {"task": "a", "slots": 10, "program": ("inc",), "origin": "primitive"},
            {"task": "b", "slots": 10, "program": ("inc",), "origin": "primitive"},
            {"task": "c", "slots": 10, "program": ("inc",), "origin": "primitive"},
        ]
        candidate = [
            {"task": "a", "slots": 8, "program": ("inc",), "origin": "guided"},
            {"task": "b", "slots": 8, "program": ("inc",), "origin": "primitive"},
            {"task": "c", "slots": 12, "program": ("inc",), "origin": "guided"},
        ]
        out = E.compare_rows(baseline, candidate)
        self.assertEqual(out["strict_improvement_tasks"], 2)
        self.assertEqual(out["guided_wins"], 1)
        self.assertEqual(out["harmful_tasks"], 1)


if __name__ == "__main__":
    unittest.main()
