import importlib.util
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("g3_representation", HERE / "experiment.py")
E = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(E)


class TestProspectiveRepresentationProtocol(unittest.TestCase):
    def test_production_source_and_representation_schema_are_pinned(self):
        method_path = E.SRC / "ocm" / "learning" / "methods.py"
        schema_path = E.G2_COG / "schemas" / "representation_change_v1.json"
        self.assertEqual(E.git_blob_sha1(method_path), E.METHOD_BLOB)
        self.assertEqual(E.git_blob_sha1(schema_path), E.REPR_SCHEMA_BLOB)

    def test_language_is_registered_before_partition_and_includes_required_candidates(self):
        language = E.REGISTERED_LANGUAGE
        ids = [row["id"] for row in language["candidates"]]
        self.assertEqual(ids, list(E.ID_ORDER))
        self.assertEqual(language["incumbent_id"], "A_COEFFICIENT_TUPLE")
        self.assertEqual(language["candidates"][1]["points"], E.B_POINTS)
        self.assertEqual(language["candidates"][2]["kind"], "misleading")
        self.assertEqual(language["probe_operator"]["x"], E.PROBE_POINT)
        self.assertEqual(E.language_fingerprint(), E.content_hash(language))
        self.assertTrue(language["exact_identity_requirement"])

    def test_frozen_partitions_are_disjoint_and_declared_lengths(self):
        population, training, validation, test = E.frozen_partition()
        self.assertEqual((len(training), len(validation), len(test)), (48, 32, 64))
        ids = [task.fingerprint for task in training + validation + test]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(population[t.fingerprint][0] == 4 for t in training))
        self.assertTrue(all(population[t.fingerprint][0] == 5 for t in validation))
        self.assertTrue(all(population[t.fingerprint][0] == 6 for t in test))

    def test_incumbent_is_exact_identity_on_the_validation_grammar(self):
        catalog = E.grammar_catalog(E.VALIDATION_MIN_LENGTH)
        index = E.build_repr_index(catalog["identities"], E.key_A)
        self.assertTrue(index["injective"])
        self.assertEqual(index["collision_keys"], 0)

    def test_b_fits_short_grammar_and_disagrees_on_registered_witness_pair(self):
        injective, collisions, n = E.short_grammar_injective(E.key_B, E.SHORT_FIT_MAX_LENGTH)
        self.assertTrue(injective)
        self.assertEqual(collisions, 0)
        self.assertGreater(n, 0)
        witness = E.b_witness_pair()
        self.assertFalse(witness["same_A"])
        self.assertTrue(witness["same_B"])
        self.assertTrue(witness["probe_distinguishes"])
        left = E.M.normal_form(witness["left_program"])
        right = E.M.normal_form(witness["right_program"])
        self.assertEqual(E.key_B(left), E.key_B(right))
        self.assertNotEqual(E.key_A(left), E.key_A(right))

    def test_c_is_misleading_and_collapses_distinct_short_tasks(self):
        injective, collisions, _n = E.short_grammar_injective(E.key_C, E.SHORT_FIT_MAX_LENGTH)
        self.assertFalse(injective)
        self.assertGreater(collisions, 0)
        left = E.M.normal_form(("inc",))
        right = E.M.normal_form(("dec",))
        self.assertNotEqual(E.key_A(left), E.key_A(right))
        self.assertEqual(E.key_C(left), E.key_C(right))

    def test_selection_uses_only_identity_safe_candidates_and_ignores_test(self):
        reports = [
            {
                "id": "A_COEFFICIENT_TUPLE",
                "identity_safe": True,
                "selection_cost": 100,
            },
            {
                "id": "B_EVAL_VECTOR",
                "identity_safe": False,
                "selection_cost": 1,
            },
            {
                "id": "C_DEGREE_LEADING",
                "identity_safe": False,
                "selection_cost": 2,
            },
            {
                "id": "D_MONOMIAL_SUPPORT",
                "identity_safe": True,
                "selection_cost": 100,
            },
        ]
        selected, eligible = E.select_representation(reports)
        self.assertEqual(selected["id"], "A_COEFFICIENT_TUPLE")
        self.assertEqual(eligible, ("A_COEFFICIENT_TUPLE", "D_MONOMIAL_SUPPORT"))
        cheaper_b = dict(reports[1])
        cheaper_b["identity_safe"] = True
        reports[1] = cheaper_b
        selected_b, eligible_b = E.select_representation(reports)
        self.assertEqual(selected_b["id"], "B_EVAL_VECTOR")
        self.assertIn("B_EVAL_VECTOR", eligible_b)

    def test_distinguishing_operator_invalidates_b_without_keeping_lifecycle_identity(self):
        result = E.distinguishing_operator_invalidation()
        self.assertTrue(result["current_answer_equivalent_under_B"])
        self.assertTrue(result["probe_distinguishes"])
        self.assertFalse(result["identified_after_probe"])
        self.assertTrue(result["representation_invalidated"])
        self.assertTrue(result["representation_reopened"])
        self.assertEqual(result["lifecycle_equivalence"], "MEASURED")

    def test_ordinary_persistence_preserves_representation_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "repr.json"
            E.ordinary_persist(path, "B_EVAL_VECTOR")
            loaded = E.ordinary_load(path)
        self.assertEqual(loaded, "B_EVAL_VECTOR")

    def test_ocm_representation_survives_restart_and_revocation_returns_to_incumbent(self):
        training = {"schema": "test.training", "selected": "B_EVAL_VECTOR"}
        utility = {"schema": "test.utility", "accepted": True}
        with tempfile.TemporaryDirectory() as temp:
            live, _atom, _te, _ue, probe = E.admit_representation(
                Path(temp) / "live", "B_EVAL_VECTOR", training, utility, revoke=False
            )
            dead, _atom2, _te2, _ue2, _probe2 = E.admit_representation(
                Path(temp) / "dead", "B_EVAL_VECTOR", training, utility, revoke=True
            )
        self.assertEqual(live, "B_EVAL_VECTOR")
        self.assertIsNone(dead)
        self.assertTrue(probe.startswith("g3-probe:"))

    def test_emitted_representation_change_validates_g21_schema(self):
        invalidation = E.distinguishing_operator_invalidation()
        record = E.emit_representation_change(
            "A_COEFFICIENT_TUPLE",
            "PARENT_SUFFICIENT",
            {
                "first_test_id": "task-1",
                "training_ids": [f"train-{i}" for i in range(8)],
                "invocation_witness_id": "UNKNOWN",
                "ablation_witness_id": "ablate-1",
                "restart_witness_id": "restart-1",
                "discovery_evidence_id": "discover-1",
                "correctness_evidence_id": "proof-1",
                "training_evidence_id": "te-1",
                "utility_evidence_id": "ue-1",
            },
            invalidation,
            E.ResourceVector(notes=("test",)),
        )
        self.assertEqual(record["schema"], "ocm.g2.representation-change.v1")
        self.assertEqual(record["lifecycle_equivalence"], "MEASURED")
        self.assertEqual(record["before_representation_id"], "A_COEFFICIENT_TUPLE")
        self.assertTrue(record["correctness"]["independent_of_usefulness"])
        self.assertTrue(record["usefulness"]["independent_of_correctness"])


if __name__ == "__main__":
    unittest.main()
