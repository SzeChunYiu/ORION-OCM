from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import experiment as E
from ocm.learning import methods as M


class TestG2StrongParents(unittest.TestCase):
    def test_methods_blob_pinned(self):
        self.assertEqual(E.git_blob_sha1(E.SRC / "ocm" / "learning" / "methods.py"), E.METHOD_BLOB)

    def test_partitions_disjoint(self):
        pop = E.population(E.TEST_LEN)
        train = E.take(pop, E.TRAIN_LEN, E.TRAIN_SALT, E.TRAIN_N)
        test = E.take(pop, E.TEST_LEN, E.TEST_SALT, E.TEST_N)
        a = {t.fingerprint for t, _ in train}
        b = {t.fingerprint for t, _ in test}
        self.assertFalse(a & b)
        self.assertEqual(len(train), E.TRAIN_N)
        self.assertEqual(len(test), E.TEST_N)

    def test_placebo_is_not_the_real_fragment(self):
        real = ("square", "dec", "square")
        fake = E.placebo_fragment(real)
        self.assertNotEqual(fake, real)
        self.assertEqual(len(fake), len(real))

    def test_anti_unify_is_common_prefix(self):
        self.assertEqual(E.anti_unify([("inc", "double", "square"), ("inc", "double", "dec")]), ("inc", "double"))
        self.assertEqual(E.anti_unify([("inc",), ("dec",)]), ())

    def test_answer_cache_hits_on_held_out_are_zero(self):
        pop = E.population(E.TEST_LEN)
        train = E.take(pop, E.TRAIN_LEN, E.TRAIN_SALT, E.TRAIN_N)
        test = E.take(pop, E.TEST_LEN, E.TEST_SALT, E.TEST_N)
        hits = sum(1 for t, _ in test if t.fingerprint in {x.fingerprint for x, _ in train})
        self.assertEqual(hits, 0)

    def test_experiment_records_all_g25_controls(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = E.main(Path(tmp) / "RESULT.json")
        required = {
            "reset_OCM", "persistent_exemplar_memory", "persistent_method_library",
            "same_library_conventional_search", "domain_native_synthesis",
            "structural_placebo", "method_removed", "scope_conflicting_method",
            "harmful_transfer", "unrelated_method_growth",
        }
        self.assertEqual(required, set(result["controls"]))
        self.assertEqual(len(result["donors"]), 8)
        self.assertTrue(result["controls"]["persistent_exemplar_memory"]["excluded_as_answer_cache"])
        self.assertTrue(result["controls"]["same_library_conventional_search"]["parent_tied"])


if __name__ == "__main__":
    unittest.main()
