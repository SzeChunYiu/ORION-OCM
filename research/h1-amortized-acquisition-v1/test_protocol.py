"""H1 amortized-acquisition protocol tests. Production src is imported, not copied."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import experiment as E


FOREIGN_SALTS = set(E.FOREIGN_SALTS)


class TestH1AmortizedAcquisition(unittest.TestCase):
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

    def test_salts_are_new_and_not_g2(self):
        salts = {E.TRAIN_SALT, E.VAL_SALT, E.LATER_SALT}
        self.assertTrue(all(s.startswith("orion-ocm-h1-amortized-") for s in salts))
        self.assertTrue(all(s.endswith("-v1") for s in salts))
        self.assertEqual(len(salts), 3)
        self.assertTrue(salts.isdisjoint(FOREIGN_SALTS))
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
            self.skipTest("no earned macro")
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
        if terminal == "AMORTIZED_ACQUISITION_SUPPORTED_AT_POLYNOMIAL_SCOPE":
            self.assertTrue(self.result["h1_vector_strictly_less"] or later_cheaper(self.result))
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

    def test_macro_index_charges_duplicate_tokenizations(self):
        index = E.build_search_index(("inc", "inc"), 2)
        self.assertGreater(index["total_enumeration_attempts"], index["total_unique_candidates_checked"])

    def test_ordinary_persistence_roundtrip(self):
        macro = ("double", "square", "inc")
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "macro.json"
            E.ordinary_persist(path, macro)
            self.assertEqual(E.ordinary_load(path), macro)

    def test_ocm_macro_survives_restart_and_revocation_removes_authority(self):
        macro = ("inc", "double")
        training = {"schema": "test.training", "macro": list(macro)}
        utility = {"schema": "test.utility", "accepted": True}
        with tempfile.TemporaryDirectory() as temp:
            live, _atom, _te, _ue, live_bytes = E.admit_macro(
                Path(temp) / "live", macro, training, utility, revoke=False
            )
            dead, _atom2, _te2, _ue2, dead_bytes = E.admit_macro(
                Path(temp) / "dead", macro, training, utility, revoke=True
            )
        self.assertEqual(live, macro)
        self.assertIsNone(dead)
        self.assertGreater(live_bytes, 0)
        self.assertGreater(dead_bytes, 0)

    def test_capsule_does_not_patch_production_src(self):
        text = Path(E.__file__).read_text()
        self.assertNotIn("src/ocm", text)
        self.assertNotIn("monkeypatch", text)
        self.assertIn("from ocm.learning import methods as M", text)

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


def later_cheaper(result: dict) -> bool:
    return result["later"]["kt"]["compute"] < result["later"]["k0"]["compute"]


class TestH1ResultFreeze(unittest.TestCase):
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
        self.assertEqual(data["terminal"], "NO_AMORTIZED_ACQUISITION_LATER_NOT_CHEAPER")
        self.assertEqual(data["lifetime_terminal"], "LIBRARY_ACQUISITION_EXCEEDS_LATER_SAVINGS")
        self.assertEqual(
            data["earned"],
            ["H1/001-new_information", "H1/005-verifier_calls"],
        )


if __name__ == "__main__":
    unittest.main()
