import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("cross_domain_transfer", HERE / "experiment.py")
E = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(E)


class TestCrossDomainTransferProtocol(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.correspondence = E.load_correspondence()
        cls.source = E.freeze_source_method()
        cls.population = E.frozen_ribbon_population()
        cls.color_tasks, cls.color_table = E.frozen_color_tasks()

    def test_source_method_blob_and_fragment_are_frozen(self):
        path = E.SRC / "ocm" / "learning" / "methods.py"
        self.assertEqual(E.git_blob_sha1(path), E.METHOD_BLOB)
        self.assertEqual(tuple(self.source["fragment"]), ("square", "dec", "square"))
        self.assertEqual(self.source["source_checker"], E.SOURCE_CHECKER)
        program = E.M.checked_program(E.SOURCE_FRAGMENT)
        self.assertEqual(E.M.normal_form(program), E.M.normal_form(("square", "dec", "square")))

    def test_correspondence_maps_compose_fragment_to_compose_rewrite(self):
        witness = self.correspondence["witness"]
        self.assertIn("compose learned fragment", witness["maps"])
        self.assertIn("compose learned rewrite", witness["maps"])
        self.assertEqual(witness["operator"], "apply-fragment")
        self.assertEqual(self.correspondence["target"]["method_operator"], "apply-rewrite")
        self.assertTrue(witness["does_not_encode_target_solution"])

    def test_source_and_target_checkers_differ(self):
        self.assertNotEqual(
            self.correspondence["source"]["checker"],
            self.correspondence["target"]["checker"],
        )
        self.assertEqual(self.correspondence["target"]["checker"], "exact-tape-equality.v1")
        self.assertNotEqual(E.TARGET_CHECKER, E.SOURCE_CHECKER)

    def test_target_vocabulary_is_reminted(self):
        self.assertTrue(E.remint_ok())
        self.assertFalse(set(E.TARGET_PRIMITIVES) & set(E.M.PRIMITIVES))
        self.assertFalse(set(E.TAPE_SYMBOLS) & set(E.M.PRIMITIVES))
        self.assertFalse(set(E.COLOR_VOCAB) & set(E.M.PRIMITIVES))
        fragment = E.instantiate_transfer_fragment(self.correspondence)
        self.assertTrue(set(fragment) <= set(E.TARGET_PRIMITIVES))
        self.assertEqual(fragment, ("plait", "nick", "plait"))

    def test_correspondence_file_does_not_contain_target_answers(self):
        hits = E.correspondence_encodes_target_solution(
            self.correspondence, self.population["test"], self.color_tasks,
        )
        self.assertEqual(hits, [])
        raw = (HERE / "correspondence.json").read_text(encoding="utf-8")
        for task in self.population["test"]:
            self.assertNotIn(task.fingerprint, raw)
            self.assertNotIn(json.dumps(list(task.goal), separators=(",", ":")), raw)
        for task in self.color_tasks:
            self.assertNotIn(task.fingerprint, raw)
            # Companion answers must not be recorded as a table in correspondence.
        self.assertNotIn("color_table", raw)
        self.assertNotIn(json.dumps(self.color_table, sort_keys=True), raw)

    def test_train_and_test_are_disjoint_distance_strata(self):
        self.assertEqual(len(self.population["train"]), 34)
        self.assertEqual(len(self.population["test"]), 16)
        train_ids = {task.fingerprint for task in self.population["train"]}
        test_ids = {task.fingerprint for task in self.population["test"]}
        self.assertFalse(train_ids & test_ids)
        for task in self.population["test"]:
            program = E.shortest_program(task.start, task.goal)
            self.assertEqual(len(program), E.TEST_DISTANCE)
            self.assertEqual(E.apply_program(task.start, program), task.goal)

    def test_candidate_operations_are_the_issue_165_set(self):
        self.assertEqual(tuple(self.correspondence["cognitive_operations"]), E.CANDIDATE_OPERATIONS)

    def test_unrelated_color_domain_has_no_sequential_structure(self):
        self.assertEqual(len(self.color_tasks), 8)
        reset_rows, reset_total = E.evaluate_color(self.color_tasks, waste=0)
        xfer_rows, xfer_total = E.evaluate_color(self.color_tasks, waste=len(E.SOURCE_FRAGMENT))
        self.assertGreaterEqual(xfer_total, reset_total)
        self.assertTrue(all(row["checker"] == "exact-name-table.v1" for row in reset_rows))
        self.assertNotEqual(reset_rows[0]["checker"], E.TARGET_CHECKER)

    def test_harmful_fragment_lengthens_held_out_search(self):
        reset_rows, reset_total = E.evaluate_ribbon(self.population["test"], None)
        harmful_rows, harmful_total = E.evaluate_ribbon(self.population["test"], E.HARMFUL_FRAGMENT)
        self.assertTrue(all(row["verified"] for row in reset_rows + harmful_rows))
        self.assertGreater(harmful_total, reset_total)
        self.assertGreater(E.compare_rows(reset_rows, harmful_rows)["harmful_tasks"], 0)

    def test_source_method_ablation_restores_reset_search(self):
        fragment = E.instantiate_transfer_fragment(self.correspondence)
        receipts = {
            "source": self.source,
            "correspondence": {
                "correspondence_id": self.correspondence["correspondence_id"],
                "maps": self.correspondence["witness"]["maps"],
                "fingerprint": E.content_hash(self.correspondence),
            },
        }
        sample = self.population["test"][:3]
        with tempfile.TemporaryDirectory(prefix="ocm-xd-ablate-") as temp:
            live, *_ = E.admit_fragment(Path(temp) / "live", fragment, receipts, revoke_source=False)
            dead, *_ = E.admit_fragment(Path(temp) / "dead", fragment, receipts, revoke_source=True)
        self.assertEqual(live, fragment)
        self.assertIsNone(dead)
        reset_rows, _ = E.evaluate_ribbon(sample, None)
        ablated_rows, _ = E.evaluate_ribbon(sample, dead)
        self.assertTrue(E.rows_equal(reset_rows, ablated_rows))

    def test_neural_parent_is_cannot_check_without_nn_library(self):
        status = E.neural_parent_status()
        self.assertEqual(status["terminal"], "CANNOT_CHECK_NEURAL")
        self.assertEqual(status["modules"], [])

    def test_task_specific_miner_keeps_proper_suffixes(self):
        chosen, support = E.mine_task_specific_fragment(
            self.population["train"], self.population["train_programs"]
        )
        program = next(p for p in self.population["train_programs"].values() if len(p) >= 4)
        self.assertIn(program[-2:], support)
        src = (HERE / "experiment.py").read_text()
        self.assertIn("range(start + 2, len(program) + 1)", src)
        self.assertIn("end - start < len(program)", src)
        self.assertEqual(chosen, ("plait", "nick"))
        self.assertGreaterEqual(support[chosen], 20)

    def test_full_study_terminal_and_protocol_order(self):
        result = E.run()
        required = [
            "freeze_source_method_identity",
            "freeze_typed_correspondence",
            "verify_correspondence_does_not_encode_target_solution",
            "remint_target_vocabulary",
            "compare_reset_ocm",
            "compare_task_specific_ocm",
            "compare_knn_prototype_parent",
            "include_unrelated_transfer",
            "include_harmful_transfer",
            "causal_method_removal_ablation",
        ]
        for step in required:
            self.assertIn(step, result["protocol_order"])
        self.assertLess(
            result["protocol_order"].index("freeze_source_method_identity"),
            result["protocol_order"].index("load_target_protected_tasks"),
        )
        self.assertLess(
            result["protocol_order"].index("freeze_typed_correspondence"),
            result["protocol_order"].index("load_target_protected_tasks"),
        )
        self.assertLess(
            result["protocol_order"].index("verify_correspondence_does_not_encode_target_solution"),
            result["protocol_order"].index("load_target_protected_tasks"),
        )
        self.assertLess(
            result["protocol_order"].index("remint_target_vocabulary"),
            result["protocol_order"].index("load_target_protected_tasks"),
        )
        self.assertEqual(result["terminal"], E.POSITIVE_TERMINAL)
        self.assertTrue(result["supported"])
        self.assertTrue(result["ribbon"]["ablation_equals_reset"])
        self.assertLess(
            result["ribbon"]["transfer_total_attempts"],
            result["ribbon"]["reset_total_attempts"],
        )
        self.assertLess(
            result["ribbon"]["transfer_total_attempts"],
            result["ribbon"]["task_specific_total_attempts"],
        )
        self.assertGreater(
            result["ribbon"]["harmful_total_attempts"],
            result["ribbon"]["reset_total_attempts"],
        )
        self.assertEqual(result["unrelated"]["usefulness"], "NO_BENEFIT")
        self.assertEqual(result["parents"]["neural"]["terminal"], "CANNOT_CHECK_NEURAL")
        self.assertFalse(result["parents"]["knn_prototype"]["sufficient"])
        self.assertFalse(result["parents"]["task_specific_ocm"]["sufficient"])


if __name__ == "__main__":
    unittest.main()
