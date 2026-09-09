"""H1 examples-charge protocol. Experiment imported via spec_from_file_location."""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SPEC = importlib.util.spec_from_file_location("h1_examples_charge_v1", HERE / "experiment.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load experiment.py")
E = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(E)

V1 = REPO / "research" / "h1-amortized-acquisition-v1"
V2 = REPO / "research" / "h1-amortized-rewrite-v2"
V3 = REPO / "research" / "h1-amortized-lifetime-v3"
H5 = REPO / "research" / "h5-lifetime-economics-v1"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TestH1ExamplesCharge(unittest.TestCase):
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

    def test_v3_imported_not_copied(self):
        source = (HERE / "experiment.py").read_text(encoding="utf-8")
        self.assertIn("spec_from_file_location", source)
        self.assertIn("h1-amortized-lifetime-v3", source)
        tree = ast.parse(source)
        names = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
        self.assertNotIn("build_search_index", names)
        self.assertNotIn("four_primitive_words", names)
        self.assertNotIn("score_search_aware", names)
        self.assertNotIn("greedy_rewrite", names)
        self.assertNotIn("def greedy_rewrite", source)
        self.assertIn("V3.population", source)
        self.assertIn("V3.take", source)
        self.assertIn("V3.greedy_rewrite", source)

    def test_no_later_search_or_tournament_rerun(self):
        self.assertFalse(self.result["later_search_rerun"])
        self.assertFalse(self.result["tournament_rerun"])
        g2 = self.result["g2_cited_not_rerun"]
        self.assertTrue(g2["cited_not_rerun"])
        self.assertEqual(g2["tournament_acquisition_enumeration_attempts"], 9_010_526)
        self.assertEqual(g2["break_even_tasks_with_tournament"], 2136)
        self.assertEqual(g2["break_even_tasks_with_zero_search_acquisition"], 41)
        self.assertEqual(g2["sha256"], E.G2_RESULT_SHA256)
        self.assertEqual(_sha256(E.G2_RESULT), E.G2_RESULT_SHA256)
        self.assertTrue(self.result["v3_capital_input"]["cited_not_rerun"])

    def test_v3_capital_frozen(self):
        v3 = self.result["v3_capital_input"]
        self.assertFalse(v3["denied"])
        self.assertEqual(v3["terminal"], "AMORTIZED_ACQUISITION_SUPPORTED_AT_POLYNOMIAL_SCOPE")
        self.assertEqual(v3["later_k0_compute"], 183463)
        self.assertEqual(v3["later_kt_compute"], 144623)
        self.assertEqual(v3["library_compute"], 27919)
        self.assertEqual(v3["library_examples_count_only"], 16)
        self.assertEqual(v3["admitted"], ["double", "square"])
        self.assertEqual(v3["sha256"], E.V3_RESULT_SHA256)
        self.assertEqual(_sha256(E.V3_RESULT), E.V3_RESULT_SHA256)
        self.assertEqual(
            v3["earned"],
            ["H1/001-new_information", "H1/004-compute", "H1/005-verifier_calls"],
        )
        self.assertEqual(
            v3["not_earned"],
            ["H1/002-examples_demonstrations", "H1/008-state_written"],
        )

    def test_salts_are_frozen_v3_not_retuned(self):
        self.assertFalse(self.result["salts_retuned"])
        self.assertEqual(self.result["salts"]["train"], "orion-ocm-h1-lifetime-train-v3")
        self.assertEqual(self.result["salts"]["val"], "orion-ocm-h1-lifetime-val-v3")
        self.assertEqual(self.result["salts"]["later"], "orion-ocm-h1-lifetime-later-v3")
        self.assertEqual(self.result["predecessor_v1_terminal"], "NO_AMORTIZED_ACQUISITION_LATER_NOT_CHEAPER")
        self.assertEqual(self.result["predecessor_v2_terminal"], "LIBRARY_ACQUISITION_EXCEEDS_LATER_SAVINGS")
        self.assertEqual(self.result["predecessor_v3_terminal"], "AMORTIZED_ACQUISITION_SUPPORTED_AT_POLYNOMIAL_SCOPE")
        self.assertEqual(self.result["predecessor_h5_terminal"], "LIFETIME_NET_POSITIVE_AFTER_CHEAP_ACQUISITION")

    def test_predecessors_not_overwritten(self):
        self.assertFalse(self.result["h1_v1_result_overwritten"])
        self.assertFalse(self.result["h1_v2_result_overwritten"])
        self.assertFalse(self.result["h1_v3_result_overwritten"])
        self.assertFalse(self.result["h5_result_overwritten"])
        self.assertEqual(HERE.name, "h1-examples-charge-v1")
        self.assertNotEqual(HERE.resolve(), V1.resolve())
        self.assertNotEqual(HERE.resolve(), V2.resolve())
        self.assertNotEqual(HERE.resolve(), V3.resolve())
        self.assertNotEqual(HERE.resolve(), H5.resolve())

    def test_demonstrations_are_first_class_count_and_bytes(self):
        demo = self.result["demonstrations"]
        self.assertEqual(demo["channel"], "demonstration")
        self.assertEqual(demo["count"], 16)
        self.assertEqual(demo["later_n"], 48)
        self.assertGreater(demo["canonical_bytes"], 0)
        self.assertGreater(demo["ordinary_bytes"], 0)
        self.assertGreater(demo["ocm_bytes"], 0)
        self.assertGreater(demo["revoked_bytes"], 0)
        self.assertEqual(demo["lookup_hit_count"], 0)
        self.assertEqual(demo["lookup_hits"], [])
        self.assertEqual(demo["live_demo_records"], 16)
        self.assertEqual(demo["evidence_n"], 16)
        self.assertTrue(demo["ordinary_equals_ocm"])
        self.assertTrue(demo["revoked_equals_empty"])
        self.assertTrue(demo["restart_before_lookup"])
        self.assertNotEqual(
            demo["canonical_bytes"],
            0,
            "bytes must be charged; predecessor left them at 0",
        )
        free = self.result["free_residue_parent"]
        self.assertEqual(free["library_count"], 16)
        self.assertEqual(free["library_bytes_charged"], 0)

    def test_later_task_example_inequality_is_zero_equals_zero(self):
        later = self.result["later"]
        self.assertEqual(later["k0_examples"]["count"], 0)
        self.assertEqual(later["kt_examples"]["count"], 0)
        self.assertEqual(later["k0_examples"]["bytes"], 0)
        self.assertEqual(later["kt_examples"]["bytes"], 0)
        self.assertFalse(later["strict_example_count_saving"])
        self.assertFalse(later["strict_example_bytes_saving"])
        self.assertFalse(later["strict_state_saving"])
        self.assertEqual(later["k0_state_written"], 0)
        self.assertEqual(later["kt_state_written"], 0)
        self.assertEqual(later["cited_k0_compute"], 183463)
        self.assertEqual(later["cited_kt_compute"], 144623)

    def test_teach_later_parent_is_rejected(self):
        rejected = self.result["rejected_teach_later_parent"]
        self.assertTrue(rejected["rejected"])
        self.assertEqual(rejected["later_k0_count"], 48)
        self.assertEqual(rejected["later_kt_count"], 48)
        self.assertGreater(rejected["later_k0_bytes"], 0)
        self.assertGreater(rejected["later_kt_bytes"], 0)
        self.assertIn("TEACH_LATER_FAKE_EARNING", self.result["not_issued"])
        self.assertIn("search", rejected["reason"])

    def test_h1_boxes_classified(self):
        boxes = self.result["boxes"]
        expected = {
            "H1/001-new_information",
            "H1/002-examples_demonstrations",
            "H1/003-environment_interactions",
            "H1/004-compute",
            "H1/005-verifier_calls",
            "H1/006-io_tool_calls",
            "H1/007-human_instructional_burden",
            "H1/008-state_written",
        }
        self.assertEqual(expected, set(boxes))
        self.assertEqual(boxes["H1/001-new_information"]["status"], "CITED_EARNED_AT_SCOPE_FROM_V3")
        self.assertEqual(boxes["H1/004-compute"]["status"], "CITED_EARNED_AT_SCOPE_FROM_V3")
        self.assertEqual(boxes["H1/005-verifier_calls"]["status"], "CITED_EARNED_AT_SCOPE_FROM_V3")
        self.assertEqual(boxes["H1/003-environment_interactions"]["status"], "CANNOT_CHECK_NO_ENVIRONMENT_CHANNEL")
        self.assertEqual(boxes["H1/006-io_tool_calls"]["status"], "CANNOT_CHECK_NO_IO_TOOL_CHANNEL")
        self.assertEqual(
            boxes["H1/007-human_instructional_burden"]["status"],
            "CANNOT_CHECK_NO_HUMAN_INSTRUCTION_CHANNEL",
        )
        self.assertEqual(boxes["H1/002-examples_demonstrations"]["status"], "NO_STRICT_SAVING")
        self.assertEqual(boxes["H1/008-state_written"]["status"], "NO_STRICT_SAVING")
        self.assertEqual(self.result["earned"], [])
        self.assertEqual(
            self.result["not_earned"],
            ["H1/002-examples_demonstrations", "H1/008-state_written"],
        )
        self.assertEqual(
            self.result["cannot_check"],
            [
                "H1/003-environment_interactions",
                "H1/006-io_tool_calls",
                "H1/007-human_instructional_burden",
            ],
        )
        self.assertEqual(
            self.result["cited_earned_from_v3"],
            ["H1/001-new_information", "H1/004-compute", "H1/005-verifier_calls"],
        )

    def test_terminal_is_library_capital(self):
        self.assertEqual(self.result["terminal"], "EXAMPLES_ARE_LIBRARY_CAPITAL")
        self.assertIn(self.result["terminal"], E.ALLOWED_TERMINALS)
        self.assertFalse(self.result["programme_wide_close"])
        self.assertFalse(self.result["production_src_edited"])
        self.assertFalse(self.result["m12_v5_claimed"])
        self.assertFalse(self.result["h1_vector_strictly_less"])
        self.assertTrue(self.result["parent_sufficient"])
        self.assertIn("not retuned", self.result["mechanism_comment"])
        self.assertIn("M12_LIFETIME_V5", self.result["not_issued"])
        self.assertIn("HUMAN_INSTRUCTIONAL_BURDEN", self.result["not_issued"])
        self.assertIn("NINE_E6_TOURNAMENT_RERUN", self.result["not_issued"])

    def test_lifetime_examples_are_capital_not_later_savings(self):
        lifetime = self.result["lifetime"]
        self.assertEqual(lifetime["k0_examples_count"], 0)
        self.assertEqual(lifetime["kt_examples_count"], 16)
        self.assertEqual(lifetime["k0_examples_bytes"], 0)
        self.assertGreater(lifetime["kt_examples_bytes"], 0)
        self.assertEqual(lifetime["k0_state_written"], 0)
        self.assertGreater(lifetime["kt_state_written"], 0)
        box = self.result["boxes"]["H1/002-examples_demonstrations"]
        self.assertEqual(box["library_count"], 16)
        self.assertEqual(box["later_k0_count"], 0)
        self.assertEqual(box["later_kt_count"], 0)
        self.assertGreater(box["library_bytes"], 0)

    def test_ordinary_corpus_roundtrip_and_disjoint_lookup(self):
        train = [("inc", "double"), ("square", "dec")]
        records = []
        for i, program in enumerate(train):
            task = E.M.PolynomialTask(f"demo-{i}", E.M.normal_form(program))
            records.append(E.demonstration_record(task, program))
        payload = E.corpus_payload(records)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "demos.json"
            E.ordinary_persist_corpus(path, payload)
            loaded = E.ordinary_load_corpus(path)
        self.assertEqual(loaded["count"], 2)
        later_task = E.M.PolynomialTask("later", E.M.normal_form(("inc", "inc", "inc")))
        hits = E.lookup_hits(((later_task, ("inc", "inc", "inc")),), {r["fingerprint"]: r for r in records})
        self.assertEqual(hits, [])
        same = E.M.PolynomialTask("same", E.M.normal_form(("inc", "double")))
        hits_same = E.lookup_hits(((same, ("inc", "double")),), {r["fingerprint"]: r for r in records})
        self.assertEqual(hits_same, [same.fingerprint])

    def test_ocm_demonstrations_survive_restart_and_revocation_clears_them(self):
        program = ("double", "square")
        task = E.M.PolynomialTask("persist", E.M.normal_form(program))
        records = [E.demonstration_record(task, program)]
        with tempfile.TemporaryDirectory() as temp:
            live, _atom, eids, live_bytes, live_n = E.admit_demonstrations(
                Path(temp) / "live", records, revoke=False
            )
            dead, _atom2, _eids2, dead_bytes, dead_n = E.admit_demonstrations(
                Path(temp) / "dead", records, revoke=True
            )
        self.assertEqual(live, [task.fingerprint])
        self.assertIsNone(dead)
        self.assertEqual(live_n, 1)
        self.assertEqual(dead_n, 0)
        self.assertGreater(live_bytes, 0)
        self.assertGreater(dead_bytes, 0)
        self.assertEqual(len(eids), 1)

    def test_examples_earned_requires_both_count_and_bytes(self):
        self.assertFalse(E.examples_earned({"count": 0, "bytes": 0}, {"count": 0, "bytes": 0}))
        self.assertFalse(E.examples_earned({"count": 0, "bytes": 10}, {"count": 1, "bytes": 10}))
        self.assertTrue(E.examples_earned({"count": 0, "bytes": 5}, {"count": 1, "bytes": 10}))

    def test_no_src_edits_and_no_macro_token(self):
        text = Path(E.__file__).read_text(encoding="utf-8")
        self.assertNotIn("monkeypatch", text)
        self.assertIn("from ocm.learning import methods as M", text)
        self.assertIn("Channel.DEMONSTRATION", text)
        self.assertNotIn("MACRO_TOKEN", text)
        self.assertFalse(self.result["production_src_edited"])

    def test_capsule_does_not_claim_human_or_m12(self):
        self.assertIn("HUMAN_INSTRUCTIONAL_BURDEN", self.result["not_issued"])
        self.assertIn("IO_TOOL_CALLS", self.result["not_issued"])
        self.assertIn("ENVIRONMENT_INTERACTIONS", self.result["not_issued"])
        self.assertIn("M12_LIFETIME_V5", self.result["not_issued"])
        self.assertFalse(self.result["m12_v5_claimed"])


class TestH1ExamplesChargeResultFreeze(unittest.TestCase):
    def test_written_result_matches_schema(self):
        path = HERE / "RESULT.json"
        if not path.exists():
            self.skipTest("RESULT.json not yet written")
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], E.SCHEMA)
        self.assertEqual(data["issue"], 165)
        self.assertEqual(data["methods_blob"], E.METHOD_BLOB)
        self.assertEqual(data["terminal"], "EXAMPLES_ARE_LIBRARY_CAPITAL")
        self.assertFalse(data["programme_wide_close"])
        self.assertFalse(data["m12_v5_claimed"])
        self.assertFalse(data["later_search_rerun"])
        self.assertFalse(data["tournament_rerun"])
        self.assertEqual(data["demonstrations"]["count"], 16)
        self.assertEqual(data["demonstrations"]["lookup_hit_count"], 0)
        self.assertEqual(data["demonstrations"]["canonical_bytes"], 2914)
        self.assertEqual(data["demonstrations"]["ordinary_bytes"], 4969)
        self.assertEqual(data["demonstrations"]["ocm_bytes"], 39695)
        self.assertEqual(data["rejected_teach_later_parent"]["rewrite_shortened_identities"], 20)
        self.assertFalse(data["rejected_teach_later_parent"]["would_appear_earned"])
        self.assertEqual(data["earned"], [])
        self.assertEqual(
            data["not_earned"],
            ["H1/002-examples_demonstrations", "H1/008-state_written"],
        )
        self.assertIn("not retuned", data["mechanism_comment"])
        self.assertTrue(data["parent_sufficient"])
        self.assertEqual(data["v3_capital_input"]["sha256"], E.V3_RESULT_SHA256)
        self.assertEqual(data["g2_cited_not_rerun"]["sha256"], E.G2_RESULT_SHA256)


if __name__ == "__main__":
    unittest.main()
