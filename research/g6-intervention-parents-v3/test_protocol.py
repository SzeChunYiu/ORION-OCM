from __future__ import annotations

import json
import random
import tempfile
import unittest
from pathlib import Path

import experiment as E
from parents import (
    AUTHORED_WINDOWS,
    BO_LIBRARIES,
    automl_bo_status,
    fit_generate_and_test,
    fit_one_parameter_surrogate,
    fit_random_evolutionary,
)
from plant import LAB_DIR, V2_DIR, V2_RESULT, load_lab


HERE = Path(__file__).resolve().parent
V2_PARENTS = V2_DIR / "parents.py"


class TestG6InterventionParentsV3(unittest.TestCase):
    def test_v1_and_v2_are_not_this_tree(self):
        self.assertEqual(HERE.name, "g6-intervention-parents-v3")
        self.assertTrue(LAB_DIR.is_dir())
        self.assertTrue(V2_DIR.is_dir())
        self.assertNotEqual(HERE, LAB_DIR)
        self.assertNotEqual(HERE, V2_DIR)
        self.assertTrue((LAB_DIR / "RESULT.json").is_file())
        self.assertTrue(V2_RESULT.is_file())

    def test_salt_is_v3_not_predecessors(self):
        self.assertNotEqual(E.SALT, "orion-ocm-g6-intervention-lab-v1")
        self.assertNotEqual(E.SALT, "orion-ocm-g6-intervention-parents-v2")
        self.assertTrue(E.SALT.endswith("-v3"))
        self.assertFalse(E.ML_SELECTOR_TRAINED)

    def test_does_not_train_ml_selector(self):
        src = (HERE / "parents.py").read_text() + (HERE / "experiment.py").read_text()
        for needle in (
            "fit_learned_selector",
            "sklearn",
            "GaussianProcess",
            "neural",
            "torch",
            "RandomForest",
        ):
            self.assertNotIn(needle, src)

    def test_no_bo_library_invented_and_theta_grid_is_not_bo(self):
        src = (HERE / "parents.py").read_text()
        for needle in (
            "expected_improvement",
            "GaussianProcess",
            "acquisition_function",
            "def bayesian_optimize",
            "def auto_ml",
        ):
            self.assertNotIn(needle, src)
        status = automl_bo_status()
        self.assertFalse(status["invented"])
        self.assertTrue(status["grid_search_is_not_bo"])
        self.assertEqual(status["tried"], list(BO_LIBRARIES))
        if not status["present"]:
            self.assertEqual(status["status"], "CANNOT_CHECK_NO_BO_LIBRARY")

    def test_random_evolutionary_has_no_crossover(self):
        src = (HERE / "parents.py").read_text()
        self.assertNotIn("def _ox", src)
        self.assertNotIn("order_crossover", src)
        self.assertNotIn("def _crossover", src)
        self.assertIn("swap_mutate", src)
        self.assertIn('"crossover": False', src)

    def test_one_parameter_surrogate_fits_a_single_theta(self):
        Lab = load_lab()
        seen: set = set()
        train = Lab.make_incidents(0, 6, "theta-check", disjoint_from=seen)
        rng = random.Random(2)
        transcripts = []
        for incident in train:
            Lab.diagnose_and_repair(incident, "grid", rng)
            transcripts.append(incident.transcript)
        model = fit_one_parameter_surrogate(transcripts, Lab)
        self.assertEqual(model["n_parameters"], 1)
        self.assertIsInstance(model["theta"], int)
        self.assertGreaterEqual(model["theta"], 0)
        self.assertLessEqual(model["theta"], Lab.N_MODULES)
        self.assertIn("not-BO", model["theta_fit"])
        self.assertEqual(len(model["grid"]), Lab.N_MODULES + 1)

    def test_generate_and_test_enumerates_a_finite_power_set(self):
        Lab = load_lab()
        seen: set = set()
        train = Lab.make_incidents(0, 4, "gat-check", disjoint_from=seen)
        rng = random.Random(3)
        transcripts = []
        for incident in train:
            Lab.diagnose_and_repair(incident, "grid", rng)
            transcripts.append(incident.transcript)
        model = fit_generate_and_test(transcripts, Lab)
        self.assertTrue(model["finite"])
        self.assertEqual(model["n_patches"], 2 ** Lab.N_MODULES)
        self.assertEqual(model["max_size"], Lab.N_MODULES)

    def test_human_designed_is_authored_windows(self):
        self.assertEqual(AUTHORED_WINDOWS, ((0, 1), (2, 3), (4, 5)))
        src = (LAB_DIR / "world.py").read_text()
        self.assertIn("for start in (0, 2, 4)", src)

    def test_grid_transcripts_have_no_root_cause_labels(self):
        Lab = load_lab()
        incidents = Lab.make_incidents(0, 3, "label-check-v3", disjoint_from=set())
        rng = random.Random(0)
        for incident in incidents:
            Lab.diagnose_and_repair(incident, "grid", rng)
            t = incident.transcript
            self.assertNotIn("stuck", t)
            self.assertNotIn("hidden", t)

    def test_random_evolutionary_improves_or_holds_train_cost(self):
        Lab = load_lab()
        seen: set = set()
        train = Lab.make_incidents(0, 6, "evo-check", disjoint_from=seen)
        rng = random.Random(4)
        transcripts = []
        for incident in train:
            Lab.diagnose_and_repair(incident, "grid", rng)
            transcripts.append(incident.transcript)
        model = fit_random_evolutionary(transcripts, Lab, random.Random(5))
        self.assertFalse(model["crossover"])
        self.assertEqual(model["history"][0]["kind"], "random_init")
        self.assertLessEqual(model["train_cost"], model["history"][0]["best_cost"])

    def test_experiment_earns_remainder_and_cites_v2(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "RESULT.json"
            result = E.main(path)
            self.assertTrue(path.exists())
            disk = json.loads(path.read_text())
        self.assertEqual(result["schema"], E.SCHEMA)
        self.assertTrue(result["v1_frozen"]["not_overwritten"])
        self.assertTrue(result["v2_frozen"]["not_overwritten"])
        self.assertEqual(result["v2_frozen"]["cited"]["terminal"], "PARENT_SUFFICIENT")
        self.assertFalse(result["ml_selector_trained"])
        self.assertFalse(result["root_cause_labels_supplied"])
        self.assertTrue(result["disjoint"])
        earned = set(result["earned_bullets"])
        self.assertEqual(
            earned,
            {
                "structured surrogate",
                "ATMS/change-impact",
                "evolutionary search",
                "program repair",
                "human-designed repair",
            },
        )
        self.assertEqual(set(result["cited_v2_bullets"]), {"system-identification", "learned selector"})
        self.assertIn("AutoML/BO", result["cannot_check"])
        self.assertEqual(result["automl_bo"]["status"], "CANNOT_CHECK_NO_BO_LIBRARY")
        self.assertFalse(result["automl_bo"]["invented"])
        self.assertTrue(result["compare_against"]["structured surrogate"]["theta_grid_is_not_bo"])
        self.assertTrue(result["compare_against"]["human-designed repair"]["charged_as_prior"])
        self.assertGreater(
            result["scores"]["human_designed_repair"]["cost"],
            result["scores"]["human_designed_repair"]["operational_cost"],
        )
        self.assertEqual(result["models"]["one_parameter_structured_surrogate"]["n_parameters"], 1)
        self.assertFalse(result["models"]["random_evolutionary"]["crossover"])
        self.assertEqual(
            result["models"]["generate_and_test_program_repair"]["n_patches"],
            2 ** load_lab().N_MODULES,
        )
        self.assertIn(result["terminal"], {"PARENT_SUFFICIENT", "NO_MULTI_GENERATION_IMPROVEMENT", "CANNOT_CHECK_NO_BO_LIBRARY"})
        self.assertEqual(disk["terminal"], result["terminal"])
        self.assertEqual(result["g61_source_bound_incidents"]["status"], "SEPARATE_WORKER")
        if result["atms_still_cheapest"]:
            self.assertEqual(result["terminal"], "PARENT_SUFFICIENT")
            self.assertEqual(result["winner"], "atms_change_impact")

    def test_v2_atms_import_uses_production_impact_cone(self):
        src = V2_PARENTS.read_text()
        self.assertIn("from ocm.kso.revocation import impact_cone", src)
        self.assertIn("from ocm.kso.nogoods import NogoodSet", src)


if __name__ == "__main__":
    unittest.main()
