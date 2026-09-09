from __future__ import annotations

import json
import random
import tempfile
import unittest
from pathlib import Path

import experiment as E
from parents import BO_LIBRARIES, automl_bo_status, gf2_dot, identify_matrix
from plant import LAB_DIR, load_lab


class TestG6InterventionParentsV2(unittest.TestCase):
    def test_v1_laboratory_is_not_this_tree(self):
        here = Path(__file__).resolve().parent
        self.assertEqual(here.name, "g6-intervention-parents-v2")
        self.assertTrue(LAB_DIR.is_dir())
        self.assertNotEqual(here, LAB_DIR)
        self.assertTrue((LAB_DIR / "world.py").is_file())
        self.assertTrue((LAB_DIR / "RESULT.json").is_file())

    def test_salt_is_not_v1(self):
        self.assertNotEqual(E.SALT, "orion-ocm-g6-intervention-lab-v1")
        self.assertTrue(E.SALT.endswith("-v2"))

    def test_no_bo_library_invented(self):
        src = (Path(__file__).resolve().parent / "parents.py").read_text()
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
        self.assertEqual(status["tried"], list(BO_LIBRARIES))
        if not status["present"]:
            self.assertEqual(status["status"], "CANNOT_CHECK_NO_BO_LIBRARY")

    def test_grid_transcripts_have_no_root_cause_labels(self):
        Lab = load_lab()
        incidents = Lab.make_incidents(0, 3, "label-check", disjoint_from=set())
        rng = random.Random(0)
        for incident in incidents:
            Lab.diagnose_and_repair(incident, "grid", rng)
            t = incident.transcript
            self.assertNotIn("stuck", t)
            self.assertNotIn("hidden", t)
            self.assertIn("probes", t)
            self.assertIn("syndrome", t)

    def test_system_id_recovers_xor_windows(self):
        Lab = load_lab()
        seen: set = set()
        train = Lab.make_incidents(0, 12, "sysid-check", disjoint_from=seen)
        rng = random.Random(1)
        transcripts = []
        for incident in train:
            Lab.diagnose_and_repair(incident, "grid", rng)
            transcripts.append(incident.transcript)
        matrix = identify_matrix(transcripts, Lab.N_MODULES)
        self.assertEqual(len(matrix), 3)
        self.assertEqual(len(matrix[0]), Lab.N_MODULES)
        # True plant: each syndrome bit is XOR of a disjoint pair.
        for row in matrix:
            self.assertEqual(sum(row) % 2, 0)
            self.assertGreaterEqual(sum(row), 2)
        failed = []
        syndromes = []
        for t in transcripts:
            fv = [0] * Lab.N_MODULES
            for p in t["probes"]:
                if not p["ok"]:
                    fv[p["index"]] = 1
            failed.append(tuple(fv))
            syndromes.append(tuple(t["syndrome"]))
        err = 0
        for f, s in zip(failed, syndromes):
            pred = tuple(gf2_dot(row, f) for row in matrix)
            err += sum(a ^ b for a, b in zip(pred, s))
        self.assertEqual(err, 0)

    def test_experiment_earns_five_parents_and_cannot_check_bo(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "RESULT.json"
            result = E.main(path)
            self.assertTrue(path.exists())
            disk = json.loads(path.read_text())
        self.assertEqual(result["schema"], E.SCHEMA)
        self.assertTrue(result["v1_frozen"]["not_overwritten"])
        self.assertFalse(result["root_cause_labels_supplied"])
        self.assertTrue(result["disjoint"])
        earned = set(result["earned_bullets"])
        self.assertEqual(
            earned,
            {
                "system-identification",
                "structured surrogate",
                "ATMS/change-impact",
                "evolutionary search",
                "program repair",
                "learned selector",
            },
        )
        self.assertIn("AutoML/BO", result["cannot_check"])
        self.assertEqual(result["automl_bo"]["status"], "CANNOT_CHECK_NO_BO_LIBRARY")
        self.assertFalse(result["automl_bo"]["invented"])
        for key in (
            "system_id",
            "structured_surrogate",
            "atms_change_impact",
            "evolutionary",
            "program_repair",
        ):
            self.assertGreater(result["scores"][key]["n"], 0)
            self.assertIn("cost", result["scores"][key])
        self.assertIn(result["terminal"], {"PARENT_SUFFICIENT", "NO_MULTI_GENERATION_IMPROVEMENT", "CANNOT_CHECK_NO_BO_LIBRARY"})
        self.assertEqual(disk["terminal"], result["terminal"])
        self.assertIn("graph", result["models"]["atms_change_impact"])
        self.assertIn("A", result["models"]["system_id"])
        self.assertIn("factors", result["models"]["structured_surrogate"])
        self.assertIn("perm", result["models"]["evolutionary"])
        self.assertIn("seeds", result["models"]["program_repair"])

    def test_atms_uses_production_impact_cone(self):
        src = (Path(__file__).resolve().parent / "parents.py").read_text()
        self.assertIn("from ocm.kso.revocation import impact_cone", src)
        self.assertIn("from ocm.kso.nogoods import NogoodSet", src)


if __name__ == "__main__":
    unittest.main()
