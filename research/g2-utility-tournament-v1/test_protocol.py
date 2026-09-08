import importlib.util
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("g2_utility_tournament", HERE / "experiment.py")
E = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(E)


class TestProspectiveProtocol(unittest.TestCase):
    def test_production_method_source_is_pinned(self):
        path = E.SRC / "ocm" / "learning" / "methods.py"
        self.assertEqual(E.git_blob_sha1(path), E.METHOD_BLOB)

    def test_frozen_partitions_are_disjoint_and_have_declared_minimum_lengths(self):
        population, training, validation, test = E.frozen_partition()
        self.assertEqual((len(training), len(validation), len(test)), (48, 32, 64))
        ids = [task.fingerprint for task in training + validation + test]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(population[t.fingerprint][0] == 5 for t in training))
        self.assertTrue(all(population[t.fingerprint][0] == 6 for t in validation))
        self.assertTrue(all(population[t.fingerprint][0] == 7 for t in test))

    def test_hash_ranking_is_deterministic_and_partition_specific(self):
        fp = "task-fingerprint"
        self.assertEqual(E.stable_rank(E.TRAIN_SALT, fp), E.stable_rank(E.TRAIN_SALT, fp))
        self.assertNotEqual(E.stable_rank(E.TRAIN_SALT, fp), E.stable_rank(E.TEST_SALT, fp))

    def test_proper_fragments_never_include_whole_program_or_singletons(self):
        program = ("inc", "double", "square", "dec", "inc")
        got = E.proper_fragments(program)
        self.assertTrue(got)
        self.assertNotIn(program, got)
        self.assertTrue(all(2 <= len(fragment) <= 4 for fragment in got))

    def test_candidate_pool_counts_distinct_task_support_and_is_bounded(self):
        rows = []
        programs = [
            ("inc", "double", "square", "dec", "inc"),
            ("inc", "double", "square", "inc", "dec"),
            ("dec", "inc", "double", "square", "inc"),
        ]
        for i, program in enumerate(programs):
            rows.append((SimpleNamespace(fingerprint=f"task-{i}"), SimpleNamespace(program=program)))
        candidates, support = E.candidate_pool(rows)
        self.assertLessEqual(len(candidates), E.CANDIDATE_CAP)
        self.assertIn(("inc", "double", "square"), candidates)
        self.assertEqual(support[("inc", "double", "square")], 3)
        self.assertTrue(all(value >= E.MIN_SUPPORT for value in support.values()))

    def test_stream_trace_marks_primitive_solution_without_method(self):
        task = E.M.PolynomialTask("trace-control", E.M.normal_form(("inc",)))
        result, origin = E.checked_solve(task, E.M.SearchBudget(slots=20, max_length=1))
        self.assertTrue(E.M.verify_solution(task, result))
        self.assertEqual(origin, "primitive")

    def test_ordinary_persistence_preserves_method_identity(self):
        method = E.M.GeneratorMethod((("inc", "double"),), ("a", "b"))
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "method.json"
            E.ordinary_persist(path, method)
            loaded = E.ordinary_load(path)
        self.assertEqual(loaded, method)
        self.assertEqual(loaded.fingerprint, method.fingerprint)

    def test_ocm_research_adapter_survives_restart_and_fails_after_support_revoke(self):
        method = E.M.GeneratorMethod((("inc", "double"),), ("a", "b"))
        training = {"schema": "test.training", "candidate": ["inc", "double"]}
        utility = {"schema": "test.utility", "accepted": True}
        with tempfile.TemporaryDirectory() as temp:
            live, _atom, _te, _ue = E.admit_selected_method(
                Path(temp) / "live", method, training, utility, revoke=False
            )
            dead, _atom2, _te2, _ue2 = E.admit_selected_method(
                Path(temp) / "dead", method, training, utility, revoke=True
            )
        self.assertEqual(live, method)
        self.assertEqual(dead, E.M.GeneratorMethod())


if __name__ == "__main__":
    unittest.main()
