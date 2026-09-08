"""Differential controls against the real, source-pinned production implementation.

Run from a repository checkout with PYTHONPATH=src:research/ocm-foundation-audit-v1.
Absence of the production package is an error, not a silently skipped control.
The cases are small authored controls; no new protected population is selected.
"""
from fractions import Fraction
import hashlib
from itertools import product
from pathlib import Path
import unittest

import audit_g2 as A
from ocm.learning import methods as M


class ProductionRefinement(unittest.TestCase):
    def test_source_is_the_registered_blob(self):
        raw = Path(M.__file__).read_bytes()
        self.assertEqual(hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest(), A.METHOD_BLOB)

    def test_independent_polynomial_identity_and_hash_refine_production(self):
        for n in range(4):
            for word in product(A.OPS, repeat=n):
                with self.subTest(word=word):
                    self.assertEqual(tuple(map(Fraction, A.coefficients(word))), M.normal_form(word))
                    task = M.PolynomialTask("authored-refinement-control", M.normal_form(word))
                    self.assertEqual(task.fingerprint, A.task_id(word))

    def test_slot_rank_and_first_program_refine_production(self):
        tasks = {}
        for n in range(4):
            for word in product(A.OPS, repeat=n):
                t = M.PolynomialTask("authored-refinement-control", M.normal_form(word))
                tasks.setdefault(t.fingerprint, t)
        for fragments in ((), (("inc", "square"),), (("dec", "double"),), (("square", "inc"),)):
            method = M.GeneratorMethod(fragments, ("authored-training-control",))
            self.assertEqual(method.fingerprint, A.method_id(fragments, ["authored-training-control"]))
            hits = A.first_hits(list(tasks), 3, fragments, 2000)
            for fp, task in tasks.items():
                result = M.solve(task, M.SearchBudget(slots=2000, max_length=3), method)
                with self.subTest(task=fp, fragments=fragments):
                    self.assertTrue(M.verify_solution(task, result))
                    self.assertEqual(result.slots, hits[fp]["slots"])
                    self.assertEqual(result.program, tuple(hits[fp]["program"]))


if __name__ == "__main__":
    unittest.main()
