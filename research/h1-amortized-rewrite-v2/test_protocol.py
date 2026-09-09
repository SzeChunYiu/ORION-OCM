"""H1 amortized-rewrite protocol tests. Production src is imported, not copied."""
from __future__ import annotations

import json
import tempfile
import unittest
from itertools import product
from pathlib import Path

import experiment as E


FOREIGN_SALTS = set(E.FOREIGN_SALTS)


class TestH1AmortizedRewrite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.result = E.main(Path(cls.tmp.name) / "RESULT.json")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_methods_blob_pinned(self):
        self.assertEqual(E.git_blob_sha1(E.SRC / "ocm" / "learning" / "methods.py"), E.METHOD_BLOB)
        self.assertEqual(self.result["methods_blob"], E.METHOD_BLOB)
        self.assertEqual(tuple(E.M.PRIMITIVES), ("inc", "dec", "double", "square"))

    def test_salts_are_new_not_v1_and_not_g2(self):
        salts = {E.TRAIN_SALT, E.VAL_SALT, E.LATER_SALT}
        self.assertTrue(all(s.startswith("orion-ocm-h1-rewrite-") for s in salts))
        self.assertTrue(all(s.endswith("-v2") for s in salts))
        self.assertEqual(len(salts), 3)
        self.assertTrue(salts.isdisjoint(FOREIGN_SALTS))
        self.assertNotIn("orion-ocm-h1-amortized-train-v1", salts)
        self.assertEqual(self.result["salts"]["train"], E.TRAIN_SALT)
        self.assertEqual(self.result["salts"]["val"], E.VAL_SALT)
        self.assertEqual(self.result["salts"]["later"], E.LATER_SALT)

    def test_partitions_disjoint_declared_lengths(self):
        pop = E.population(E.LATER_LEN)
        train = E.take(pop, E.TRAIN_LEN, E.TRAIN_SALT, E.TRAIN_N)
        val = E.take(pop, E.VAL_LEN, E.VAL_SALT, E.VAL_N)
        later = E.take(pop, E.LATER_LEN, E.LATER_SALT, E.LATER_N)
        ids = [t.fingerprint for t, _ in train + val + later]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(pop[t.fingerprint][0] == E.TRAIN_LEN for t, _ in train))
        self.assertTrue(all(pop[t.fingerprint][0] == E.VAL_LEN for t, _ in val))
        self.assertTrue(all(pop[t.fingerprint][0] == E.LATER_LEN for t, _ in later))

    def test_charged_coordinates_are_complete(self):
        for arm in (self.result["later"]["k0"], self.result["later"]["kt"], self.result["library"]["cost"]):
            self.assertEqual(set(arm), set(E.CHARGED))
            for key in E.CHARGED:
                self.assertIsInstance(arm[key], int)
                self.assertGreaterEqual(arm[key], 0)

    def test_h1_boxes_present_and_classified(self):
        boxes = self.result["boxes"]
        expected = {
            "H1/001-new_information",
            "H1/002-examples_demonstrations",
            "H1/004-compute",
            "H1/005-verifier_calls",
            "H1/008-state_written",
            "H1/003-environment_interactions",
            "H1/006-io_tool_calls",
            "H1/007-human_instructional_burden",
        }
        self.assertEqual(expected, set(boxes))
        for key in (
            "H1/001-new_information",
            "H1/002-examples_demonstrations",
            "H1/004-compute",
            "H1/005-verifier_calls",
            "H1/008-state_written",
        ):
            self.assertIn(boxes[key]["status"], {"EARNED_AT_SCOPE", "NO_STRICT_SAVING"})
        self.assertEqual(boxes["H1/003-environment_interactions"]["status"], "CANNOT_CHECK_NO_ENVIRONMENT_CHANNEL")
        self.assertEqual(boxes["H1/006-io_tool_calls"]["status"], "CANNOT_CHECK_NO_IO_TOOL_CHANNEL")
        self.assertEqual(
            boxes["H1/007-human_instructional_burden"]["status"],
            "CANNOT_CHECK_NO_HUMAN_INSTRUCTION_CHANNEL",
        )

    def test_examples_and_state_are_library_capital_not_later_savings(self):
        later = self.result["later"]
        library = self.result["library"]["cost"]
        self.assertEqual(later["kt"]["examples"], 0)
        self.assertEqual(later["k0"]["examples"], 0)
        self.assertEqual(later["kt"]["state_written"], 0)
        self.assertEqual(later["k0"]["state_written"], 0)
        if self.result["library"]["admitted"]:
            self.assertEqual(library["examples"], E.TRAIN_N)
            self.assertGreater(library["state_written"], 0)
        self.assertEqual(self.result["boxes"]["H1/002-examples_demonstrations"]["status"], "NO_STRICT_SAVING")
        self.assertEqual(self.result["boxes"]["H1/008-state_written"]["status"], "NO_STRICT_SAVING")

    def test_ordinary_parent_parity_and_revocation(self):
        later = self.result["later"]
        if not self.result["library"]["admitted"]:
            self.skipTest("no earned rewrite")
        self.assertTrue(later["ordinary_equals_ocm"])
        self.assertTrue(later["revoked_equals_primitive"])
        self.assertEqual(later["ordinary"]["compute"], later["kt"]["compute"])
        self.assertEqual(later["revoked"]["compute"], later["k0"]["compute"])
        self.assertTrue(self.result["ocm"]["restart_before_later"])
        self.assertTrue(self.result["ocm"]["support_withdrawal_ablation"])
        self.assertTrue(self.result["parent_sufficient"])

    def test_library_overrun_is_first_class_negative(self):
        terminal = self.result["terminal"]
        self.assertIn(terminal, self.result["negative_terminals_frozen"] + [
            "AMORTIZED_ACQUISITION_SUPPORTED_AT_POLYNOMIAL_SCOPE"
        ])
        lifetime = self.result["lifetime"]
        self.assertIn("not retuned", self.result["mechanism_comment"])
        self.assertEqual(self.result["grammar_width"], 4)
        self.assertEqual(self.result["serving"], "greedy-leftmost-rewrite-in-4-primitive-grammar")
        if terminal == "AMORTIZED_ACQUISITION_SUPPORTED_AT_POLYNOMIAL_SCOPE":
            self.assertTrue(later_cheaper(self.result))
            self.assertTrue(lifetime["library_pays_back_compute"])
        else:
            self.assertFalse(self.result["h1_vector_strictly_less"])
        if lifetime["kt"]["compute"] >= lifetime["k0"]["compute"]:
            self.assertEqual(self.result["lifetime_terminal"], "LIBRARY_ACQUISITION_EXCEEDS_LATER_SAVINGS")
            self.assertFalse(lifetime["library_pays_back_compute"])
        if later_cheaper(self.result) and lifetime["kt"]["compute"] >= lifetime["k0"]["compute"]:
            self.assertEqual(terminal, "LIBRARY_ACQUISITION_EXCEEDS_LATER_SAVINGS")
        elif not later_cheaper(self.result) and self.result["library"]["admitted"]:
            self.assertEqual(terminal, "NO_AMORTIZED_ACQUISITION_LATER_NOT_CHEAPER")
        self.assertFalse(self.result["programme_wide_close"])
        self.assertFalse(self.result["production_src_edited"])

    def test_primitive_index_matches_production_solve_order(self):
        index = E.build_search_index(None, 4)
        self.assertEqual(index["grammar_width"], 4)
        self.assertEqual(index["grammar_tokens"], list(E.M.PRIMITIVES))
        self.assertEqual(index["total_enumeration_attempts"], index["total_unique_candidates_checked"])
        programs = [(), ("inc",), ("square",), ("inc", "double"), ("dec", "square", "inc")]
        for i, program in enumerate(programs):
            task = E.M.PolynomialTask(f"parity-{i}", E.M.normal_form(program))
            existing = E.M.solve(task, E.M.SearchBudget(slots=1000, max_length=4))
            row = E.solve_from_index(task, index)
            self.assertTrue(E.M.verify_solution(task, existing))
            self.assertEqual(row["enumeration_attempts"], existing.slots)
            self.assertEqual(tuple(row["program"]), tuple(existing.program))
            self.assertFalse(row["rewrite_used"])

    def test_rewrite_replaces_primitive_sequence_without_fifth_token(self):
        fragment = ("dec", "square")
        task = E.M.PolynomialTask("rewrite-win", E.M.normal_form(fragment))
        primitive = E.solve_from_index(task, E.build_search_index(None, 2))
        rewritten = E.solve_from_index(task, E.build_search_index(fragment, 2))
        self.assertTrue(rewritten["rewrite_used"])
        self.assertLess(rewritten["enumeration_attempts"], primitive["enumeration_attempts"])
        self.assertEqual(tuple(rewritten["program"]), fragment)
        self.assertEqual(tuple(rewritten["token_word"]), fragment)
        self.assertEqual(tuple(rewritten["operator_word"]), (E.REWRITE_MARK,))
        self.assertTrue(all(token in E.M.PRIMITIVES for token in rewritten["program"]))

    def test_rewrite_index_does_not_charge_duplicate_tokenizations(self):
        index = E.build_search_index(("inc", "inc"), 2)
        expected = sum(4 ** depth for depth in range(3))
        self.assertEqual(index["total_enumeration_attempts"], expected)
        self.assertEqual(index["total_unique_candidates_checked"], expected)
        self.assertEqual(index["grammar_width"], 4)

    def test_five_ary_macro_product_is_wider_than_rewrite(self):
        """v1 root cause: MACRO in the product inflates complete-word count."""
        fragment = ("inc", "inc")
        rewrite = E.build_search_index(fragment, 3)
        macro_attempts = 0
        tokens = ("MACRO",) + E.M.PRIMITIVES
        for depth in range(4):
            for word in product(tokens, repeat=depth):
                expanded = []
                for token in word:
                    if token == "MACRO":
                        expanded.extend(fragment)
                    else:
                        expanded.append(token)
                if len(expanded) <= 3:
                    macro_attempts += 1
        self.assertGreater(macro_attempts, rewrite["total_enumeration_attempts"])
        self.assertEqual(rewrite["grammar_width"], 4)

    def test_ordinary_persistence_roundtrip(self):
        fragment = ("double", "square", "inc")
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "fragment.json"
            E.ordinary_persist(path, fragment)
            self.assertEqual(E.ordinary_load(path), fragment)

    def test_ocm_rewrite_survives_restart_and_revocation_removes_authority(self):
        fragment = ("inc", "double")
        training = {"schema": "test.training", "fragment": list(fragment)}
        utility = {"schema": "test.utility", "accepted": True}
        with tempfile.TemporaryDirectory() as temp:
            live, _atom, _te, _ue, live_bytes = E.admit_fragment(
                Path(temp) / "live", fragment, training, utility, revoke=False
            )
            dead, _atom2, _te2, _ue2, dead_bytes = E.admit_fragment(
                Path(temp) / "dead", fragment, training, utility, revoke=True
            )
        self.assertEqual(live, fragment)
        self.assertIsNone(dead)
        self.assertGreater(live_bytes, 0)
        self.assertGreater(dead_bytes, 0)

    def test_capsule_does_not_patch_production_src_or_add_macro_token(self):
        text = Path(E.__file__).read_text()
        self.assertNotIn("src/ocm", text)
        self.assertNotIn("monkeypatch", text)
        self.assertIn("from ocm.learning import methods as M", text)
        self.assertNotIn("MACRO_TOKEN", text)
        self.assertIn("four_primitive_words", text)
        self.assertIn("greedy_rewrite", text)

    def test_does_not_touch_v1_acquisition_tree(self):
        v1 = Path(__file__).resolve().parents[1] / "h1-amortized-acquisition-v1"
        capsule = Path(__file__).resolve().parent
        self.assertEqual(capsule.name, "h1-amortized-rewrite-v2")
        if v1.exists():
            self.assertNotEqual(v1.resolve(), capsule.resolve())

    def test_earned_boxes_match_later_task_inequality(self):
        boxes = self.result["boxes"]
        later = self.result["later"]
        for key, coord in (
            ("H1/001-new_information", "new_information"),
            ("H1/004-compute", "compute"),
            ("H1/005-verifier_calls", "verifier_calls"),
        ):
            if later["kt"][coord] < later["k0"][coord]:
                self.assertEqual(boxes[key]["status"], "EARNED_AT_SCOPE", key)
            else:
                self.assertEqual(boxes[key]["status"], "NO_STRICT_SAVING", key)

    def test_later_compute_equals_unique_programs_when_reset(self):
        k0 = self.result["later"]["k0"]
        self.assertEqual(k0["compute"], k0["new_information"])
        self.assertEqual(k0["compute"], k0["verifier_calls"])


def later_cheaper(result: dict) -> bool:
    return result["later"]["kt"]["compute"] < result["later"]["k0"]["compute"]


class TestH1RewriteResultFreeze(unittest.TestCase):
    def test_written_result_matches_schema(self):
        path = Path(__file__).resolve().parent / "RESULT.json"
        if not path.exists():
            self.skipTest("RESULT.json not yet written")
        data = json.loads(path.read_text())
        self.assertEqual(data["schema"], E.SCHEMA)
        self.assertEqual(data["issue"], 165)
        self.assertFalse(data["programme_wide_close"])
        self.assertIn("mechanism_comment", data)
        self.assertEqual(data["methods_blob"], E.METHOD_BLOB)
        self.assertEqual(data["grammar_width"], 4)
        self.assertEqual(data["serving"], "greedy-leftmost-rewrite-in-4-primitive-grammar")
        self.assertEqual(data["predecessor_v1_terminal"], "NO_AMORTIZED_ACQUISITION_LATER_NOT_CHEAPER")
        self.assertIn(data["terminal"], data["negative_terminals_frozen"] + [
            "AMORTIZED_ACQUISITION_SUPPORTED_AT_POLYNOMIAL_SCOPE"
        ])
        self.assertIn("not retuned", data["mechanism_comment"])


if __name__ == "__main__":
    unittest.main()
