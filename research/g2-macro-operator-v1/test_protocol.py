import importlib.util
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("g2_macro_operator", HERE / "experiment.py")
E = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(E)


class TestProspectiveMacroProtocol(unittest.TestCase):
    def test_production_source_is_pinned(self):
        path = E.SRC / "ocm" / "learning" / "methods.py"
        self.assertEqual(E.git_blob_sha1(path), E.METHOD_BLOB)

    def test_frozen_partitions_are_disjoint_and_declared_lengths(self):
        population, training, validation, test = E.frozen_partition()
        self.assertEqual((len(training), len(validation), len(test)), (48, 32, 64))
        ids = [task.fingerprint for task in training + validation + test]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(population[t.fingerprint][0] == 6 for t in training))
        self.assertTrue(all(population[t.fingerprint][0] == 7 for t in validation))
        self.assertTrue(all(population[t.fingerprint][0] == 8 for t in test))

    def test_candidate_pool_is_training_only_bounded_and_support_counted(self):
        rows = []
        programs = [
            ("inc", "double", "square", "dec", "inc", "double"),
            ("inc", "double", "square", "inc", "dec", "square"),
            ("dec", "inc", "double", "square", "inc", "square"),
        ]
        for i, program in enumerate(programs):
            rows.append((SimpleNamespace(fingerprint=f"task-{i}"), SimpleNamespace(program=program)))
        candidates, support = E.candidate_pool(rows)
        self.assertLessEqual(len(candidates), E.CANDIDATE_CAP)
        self.assertIn(("inc", "double", "square"), candidates)
        self.assertEqual(support[("inc", "double", "square")], 3)
        self.assertTrue(all(value >= E.MIN_SUPPORT for value in support.values()))

    def test_primitive_index_reproduces_existing_primitive_slot_order(self):
        index = E.build_search_index(None, 4)
        programs = [(), ("inc",), ("square",), ("inc", "double"), ("dec", "square", "inc")]
        for i, program in enumerate(programs):
            task = E.M.PolynomialTask(f"parity-{i}", E.M.normal_form(program))
            existing = E.M.solve(task, E.M.SearchBudget(slots=1000, max_length=4))
            row = E.solve_from_index(task, index)
            self.assertTrue(E.M.verify_solution(task, existing))
            self.assertEqual(row["enumeration_attempts"], existing.slots)
            self.assertEqual(tuple(row["program"]), tuple(existing.program))
            self.assertFalse(row["macro_used"])

    def test_macro_can_replace_multiple_primitive_decisions(self):
        task = E.M.PolynomialTask("macro-win", E.M.normal_form(("inc", "inc")))
        primitive = E.solve_from_index(task, E.build_search_index(None, 2))
        macro = E.solve_from_index(task, E.build_search_index(("inc", "inc"), 2))
        self.assertTrue(macro["macro_used"])
        self.assertLess(macro["enumeration_attempts"], primitive["enumeration_attempts"])
        self.assertEqual(tuple(macro["program"]), ("inc", "inc"))

    def test_duplicate_macro_tokenization_is_not_free(self):
        index = E.build_search_index(("inc", "inc"), 2)
        # MACRO and primitive inc/inc both expand to the same program. The complete
        # token words are both charged even though the exact expanded program is
        # checked only once.
        self.assertGreater(index["total_enumeration_attempts"], index["total_unique_candidates_checked"])

    def test_overlong_macro_words_are_pruned_before_attempt_count(self):
        index = E.build_search_index(("inc", "inc", "inc", "inc"), 2)
        # The 4-primitive macro cannot appear in any valid word at bound 2.
        target = E.M.PolynomialTask("two-inc", E.M.normal_form(("inc", "inc")))
        row = E.solve_from_index(target, index)
        self.assertFalse(row["macro_used"])

    def test_ordinary_persistence_preserves_macro_identity(self):
        macro = ("inc", "double", "square")
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "macro.json"
            E.ordinary_persist(path, macro)
            loaded = E.ordinary_load(path)
        self.assertEqual(loaded, macro)

    def test_ocm_macro_survives_restart_and_revocation_removes_authority(self):
        macro = ("inc", "double")
        training = {"schema": "test.training", "macro": list(macro)}
        utility = {"schema": "test.utility", "accepted": True}
        with tempfile.TemporaryDirectory() as temp:
            live, _atom, _te, _ue = E.admit_macro(
                Path(temp) / "live", macro, training, utility, revoke=False
            )
            dead, _atom2, _te2, _ue2 = E.admit_macro(
                Path(temp) / "dead", macro, training, utility, revoke=True
            )
        self.assertEqual(live, macro)
        self.assertIsNone(dead)


if __name__ == "__main__":
    unittest.main()
