import importlib.util
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("g3_independent_composition", HERE / "experiment.py")
E = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(E)


class TestProspectiveG3Protocol(unittest.TestCase):
    def test_g2_parent_and_production_source_are_pinned(self):
        self.assertEqual(E.git_blob_sha1(E.G2_PATH), E.G2_BLOB)
        method_path = E.SRC / "ocm" / "learning" / "methods.py"
        self.assertEqual(E.git_blob_sha1(method_path), E.G2.METHOD_BLOB)

    def test_partition_is_disjoint_and_prior_exposure_is_excluded(self):
        parts = E.frozen_partition()
        ids = [
            *(t.fingerprint for t in parts["a_train"]),
            *(t.fingerprint for t in parts["b_train"]),
            *(t.fingerprint for t in parts["a_validation"]),
            *(t.fingerprint for t in parts["b_validation"]),
            *(t.fingerprint for t in parts["test"]),
        ]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertFalse(parts["exposed6"] & {t.fingerprint for t in parts["a_train"] + parts["b_train"]})
        self.assertFalse(parts["exposed7"] & {t.fingerprint for t in parts["a_validation"] + parts["b_validation"]})
        self.assertFalse(parts["exposed8"] & {t.fingerprint for t in parts["test"]})
        self.assertEqual((len(parts["a_train"]), len(parts["b_train"])), (48, 48))
        self.assertEqual((len(parts["a_validation"]), len(parts["b_validation"])), (32, 32))
        self.assertEqual(len(parts["test"]), 256)

    def test_library_primitive_mode_matches_g2_primitive_index(self):
        library = E.build_library_index({}, 4)
        parent = E.G2.build_search_index(None, 4)
        programs = [(), ("inc",), ("square",), ("inc", "double"), ("dec", "square", "inc")]
        for i, program in enumerate(programs):
            task = E.G2.M.PolynomialTask(f"parity-{i}", E.G2.M.normal_form(program))
            row = E.solve_from_library(task, library)
            prow = E.G2.solve_from_index(task, parent)
            self.assertEqual(row["enumeration_attempts"], prow["enumeration_attempts"])
            self.assertEqual(row["unique_candidates_checked"], prow["unique_candidates_checked"])
            self.assertEqual(tuple(row["program"]), tuple(prow["program"]))
            self.assertEqual(row["macros_used"], ())

    def test_synthetic_a_plus_b_witness_is_detectable(self):
        macro_a = ("inc", "inc")
        macro_b = ("double", "double")
        task = E.G2.M.PolynomialTask(
            "synthetic-compose",
            E.G2.M.normal_form(macro_a + macro_b),
        )
        primitive = E.solve_from_library(task, E.build_library_index({}, 4))
        a_only = E.solve_from_library(task, E.build_library_index({E.LABEL_A: macro_a}, 4))
        b_only = E.solve_from_library(task, E.build_library_index({E.LABEL_B: macro_b}, 4))
        full = E.solve_from_library(
            task,
            E.build_library_index({E.LABEL_A: macro_a, E.LABEL_B: macro_b}, 4),
        )
        analysis = E.composition_analysis([primitive], [a_only], [b_only], [full])
        self.assertEqual(set(full["macros_used"]), {E.LABEL_A, E.LABEL_B})
        self.assertLess(full["enumeration_attempts"], primitive["enumeration_attempts"])
        self.assertLess(full["enumeration_attempts"], a_only["enumeration_attempts"])
        self.assertLess(full["enumeration_attempts"], b_only["enumeration_attempts"])
        self.assertEqual(len(analysis["strong_witnesses"]), 1)

    def test_ordinary_library_round_trip_preserves_labels(self):
        macro_a = ("inc", "inc")
        macro_b = ("double", "square")
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "library.json"
            E.ordinary_persist_library(path, macro_a, macro_b)
            loaded = E.ordinary_load_library(path)
        self.assertEqual(loaded, {E.LABEL_A: macro_a, E.LABEL_B: macro_b})

    def test_ocm_local_revocation_preserves_other_method(self):
        macro_a = ("inc", "inc")
        macro_b = ("double", "square")
        receipts = {
            E.LABEL_A: {
                "training": {"schema": "test.training", "label": "A"},
                "utility": {"schema": "test.utility", "label": "A", "accepted": True},
            },
            E.LABEL_B: {
                "training": {"schema": "test.training", "label": "B"},
                "utility": {"schema": "test.utility", "label": "B", "accepted": True},
            },
        }
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            full, *_ = E.admit_library(root / "full", macro_a, macro_b, receipts, ())
            no_a, *_ = E.admit_library(root / "no-a", macro_a, macro_b, receipts, (E.LABEL_A,))
            no_b, *_ = E.admit_library(root / "no-b", macro_a, macro_b, receipts, (E.LABEL_B,))
            none, *_ = E.admit_library(root / "none", macro_a, macro_b, receipts, E.LABEL_ORDER)
        self.assertEqual(full, {E.LABEL_A: macro_a, E.LABEL_B: macro_b})
        self.assertEqual(no_a, {E.LABEL_B: macro_b})
        self.assertEqual(no_b, {E.LABEL_A: macro_a})
        self.assertEqual(none, {})


if __name__ == "__main__":
    unittest.main()
