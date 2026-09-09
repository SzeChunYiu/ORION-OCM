"""Tests for FNA-2: R3/R6 built so APPROXIMATE_RETRIEVAL_NOT_SAFE is reachable."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "src"))

import fna2 as F     # noqa: E402
import fna1b as B    # noqa: E402
import experiment as E  # noqa: E402

R = json.loads((HERE / "FNA2_APPROXIMATE_V1.json").read_text())


class NotMachineLearning(unittest.TestCase):
    def test_the_projection_has_no_training_objective_or_parameter(self):
        """Checks CODE, not prose. A crude substring scan flags the module's own
        sentence 'no gradient', which is a disclaimer rather than a violation."""
        import ast
        tree = ast.parse((HERE / "fna2.py").read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [a.name for a in node.names] + ([node.module] if
                                                        isinstance(node, ast.ImportFrom) else [])
                for n in filter(None, names):
                    self.assertFalse(
                        n.split(".")[0] in {"torch", "sklearn", "numpy", "scipy", "jax"},
                        f"learning library imported: {n}")
            if isinstance(node, ast.FunctionDef):
                self.assertNotIn(node.name, {"train", "fit", "backward", "update_weights"})

    def test_the_projection_is_deterministic_in_symbol_and_salt(self):
        a = F.symbol_vector("SUPPORT", 64)
        b = F.symbol_vector("SUPPORT", 64)
        self.assertEqual(a, b)
        self.assertNotEqual(a, F.symbol_vector("DEPENDENCE", 64))


class VSANotAHash(unittest.TestCase):
    """The defect that would have produced a false terminal."""

    def test_bundling_makes_shared_structure_similar(self):
        """A hash of the tuple gives ~0 cosine; a bundle must give a positive one."""
        q = F.hypervector(("counterexample",), 512)
        near = F.hypervector(("counterexample", "SUPPORT"), 512)
        unrelated = F.hypervector(("proof", "EMBEDDING"), 512)
        self.assertGreater(F.cosine(q, near), F.cosine(q, unrelated))
        self.assertGreater(F.cosine(q, near), 0.3)

    def test_the_hash_defect_is_recorded_in_the_docstring(self):
        doc = F.hypervector.__doc__
        self.assertIn("DEFECT IS RECORDED HERE", doc)
        flat = " ".join(doc.split())
        self.assertIn("hash masquerading as a vector-symbolic architecture", flat)


class InformationSurface(unittest.TestCase):
    def test_the_signature_carries_no_atom_identity(self):
        ks = B.world("RARE_DECISIVE")
        sig = F.signature(ks, E.DECISIVE)
        self.assertNotIn(E.DECISIVE, sig)
        for part in sig:
            self.assertFalse(part.startswith("d") and part[1:].isdigit())

    def test_the_query_is_the_target_type_not_the_answers_signature(self):
        src = (HERE / "fna2.py").read_text()
        body = src[src.index("def propose("):src.index("def twin_field(")]
        self.assertIn("query = (target_type,)", body)
        self.assertNotIn("DECISIVE", body)


class TerminalDiscipline(unittest.TestCase):
    def test_the_terminal_is_now_reachable(self):
        self.assertTrue(R["verdict"]["terminal_is_now_reachable"])

    def test_the_failure_profile_is_reported_as_not_a_capacity_boundary(self):
        reason = R["verdict"]["terminal_reason"]
        self.assertIn("NOT as a capacity boundary", reason)
        self.assertIn("the opposite of one", reason)

    def test_the_failure_rate_rises_with_dimension(self):
        """A capacity effect would fall. This one rises, which is the finding."""
        rates = R["near_twin_capacity_sweep"]["by_dimension"]
        lo = rates["2"]["failure_rate"]
        hi = rates["512"]["failure_rate"]
        self.assertGreater(hi, lo)
        self.assertEqual(hi, 1.0)

    def test_rates_come_from_many_seeds_not_one_draw(self):
        sweep = R["near_twin_capacity_sweep"]
        self.assertGreaterEqual(sweep["seeds_per_dimension"], 20)
        self.assertIn("non-monotone", sweep["method"])
        for row in sweep["by_dimension"].values():
            self.assertEqual(row["seeds"], sweep["seeds_per_dimension"])

    def test_both_missing_would_indict_the_surface_not_the_approximation(self):
        doc = json.loads(json.dumps(R))
        doc.pop("capacity_sweep"); doc.pop("near_twin_capacity_sweep")
        for kind in doc["worlds"]:
            doc["worlds"][kind]["k_where_R6_finds_decisive"] = []
            doc["worlds"][kind]["k_where_R3_finds_decisive"] = []
        self.assertEqual(F.verdict(doc)["terminal"], "REPRESENTATION_INSUFFICIENT")

    def test_no_cost_claim_is_made(self):
        text = R["verdict"]["what_this_does_not_establish"]
        self.assertIn("NOT charged", text)
        self.assertIn("no payback claim", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
