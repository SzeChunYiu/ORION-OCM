import json
import sys
import unittest
from itertools import permutations
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from remint_equivariance_v1 import (
    CLAIM_CEILING,
    RemintError,
    _fixture,
    audit_claimed_remint,
    canonical_fingerprint,
    compose_remints,
    finite_certificate,
    identity_remint,
    inverse_remint,
    remint,
    semantic_equal_up_to_presentation,
)


class RemintEquivarianceTests(unittest.TestCase):
    def setUp(self):
        self.a, self.b, self.c = _fixture()
        self.r = {"s0": "alpha", "s1": "beta", "s2": "gamma"}

    def test_identity_inverse_composition(self):
        ar = remint(self.a, self.r, name="AR")
        self.assertEqual(remint(self.a, identity_remint(self.a), name="A"), self.a)
        self.assertEqual(remint(ar, inverse_remint(self.r), name="A"), self.a)
        r2 = {"alpha": "u", "beta": "v", "gamma": "w"}
        self.assertEqual(
            remint(ar, r2, name="A2"),
            remint(self.a, compose_remints(self.r, r2), name="A2"),
        )

    def test_canonical_fingerprint_all_state_remints(self):
        fp = canonical_fingerprint(self.a)
        fps = set()
        for perm in permutations(("p", "q", "r")):
            m = dict(zip(self.a.states, perm, strict=True))
            fps.add(canonical_fingerprint(remint(self.a, m, name="X")))
        self.assertEqual(fps, {fp})

    def test_semantic_equivalence_up_to_presentation(self):
        ar = remint(self.a, self.r, name="AR")
        self.assertTrue(semantic_equal_up_to_presentation(self.a, ar))

    def test_clean_claimed_remint(self):
        target = remint(self.a, self.r, name="TARGET")
        self.assertEqual(audit_claimed_remint(self.a, target, self.r), (True, "CLEAN_SEMANTIC_REMINT"))

    def test_non_bijection_fails_closed(self):
        with self.assertRaisesRegex(RemintError, "NON_BIJECTIVE_REMINT"):
            remint(self.a, {"s0": "z", "s1": "z", "s2": "w"})

    def test_semantic_mutation_is_not_remint(self):
        target = remint(self.a, self.r, name="TARGET")
        outputs = target.output_map()
        outputs["alpha"] = "changed"
        from remint_equivariance_v1 import make_mechanism
        mutant = make_mechanism(
            "TARGET", target.states, target.initial, target.actions, target.interventions,
            outputs, target.transition_map(), target.intervention_map(), target.developmental_edges, target.resources,
        )
        clean, reason = audit_claimed_remint(self.a, mutant, self.r)
        self.assertFalse(clean)
        self.assertEqual(reason, "SEMANTIC_MUTATION:outputs")

    def test_receipt_green(self):
        r = finite_certificate()
        self.assertEqual(r["claim_ceiling"], CLAIM_CEILING)
        self.assertEqual(r["verdict"], "GREEN")
        self.assertTrue(all(r["checks"].values()))
        self.assertEqual(r["counts"]["three_state_remints_exhausted"], 6)
        json.dumps(r, sort_keys=True, separators=(",", ":"))


if __name__ == "__main__":
    unittest.main()
