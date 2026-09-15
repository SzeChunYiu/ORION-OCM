from __future__ import annotations

import itertools
import sys
import unittest
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import uncertainty_composition_v1 as uc


BINARY = (F(0), F(1))
ROOT_SETS = (
    ((F(0),),),
    ((F(1),),),
    ((F(0),), (F(1),)),
)


def unary_relation(outputs):
    return (
        ((F(0),), outputs[0]),
        ((F(1),), outputs[1]),
    )


def binary_relation(outputs):
    parent_rows = tuple(itertools.product(BINARY, BINARY))
    return tuple((tuple(parents), outputs[i]) for i, parents in enumerate(parent_rows))


class ExhaustiveSharedAncestorCensus(unittest.TestCase):
    def test_uc3_global_projection_is_always_inside_local_cartesian_set(self):
        """Exhaust all deterministic binary x->a, x->b, (a,b)->y maps.

        There are 4 unary functions for a, 4 for b, 16 Boolean functions of
        (a,b), and 3 nonempty root-confidence subsets: 4*4*16*3 = 768 cases.
        The test is an independent finite oracle for UC-3, not a new theorem.
        """
        unary_functions = tuple(itertools.product(BINARY, repeat=2))
        binary_functions = tuple(itertools.product(BINARY, repeat=4))
        cases = 0

        for f_a, f_b, f_y, root_joint in itertools.product(
            unary_functions, unary_functions, binary_functions, ROOT_SETS
        ):
            campaign = uc.CompositionCampaign()
            campaign.register_node("x", BINARY)
            campaign.register_node("a", BINARY, ("x",), unary_relation(f_a))
            campaign.register_node("b", BINARY, ("x",), unary_relation(f_b))
            campaign.register_node("y", BINARY, ("a", "b"), binary_relation(f_y))
            campaign.set_outputs(("y",))
            campaign.activate(root_joint, F(0))

            local = campaign.local_sets()
            for node in campaign.specs:
                self.assertTrue(
                    campaign.global_set(node).issubset(local[node]),
                    msg="UC-3 failed for node=%s f_a=%r f_b=%r f_y=%r roots=%r"
                    % (node, f_a, f_b, f_y, root_joint),
                )
            cases += 1

        self.assertEqual(cases, 768)

    def test_shared_ancestor_exact_assignments_match_independent_bruteforce(self):
        campaign = uc._build_shared_ancestor()
        actual = {
            (row["x"], row["a"], row["b"], row["y"])
            for row in campaign.global_assignments()
        }
        expected = set()
        for x, a, b, y in itertools.product(
            (F(-1), F(1)),
            (F(-1), F(1)),
            (F(-1), F(1)),
            (F(-2), F(0), F(2)),
        ):
            if a == x and b == x and y == a - b:
                expected.add((x, a, b, y))
        self.assertEqual(actual, expected)
        self.assertEqual({row[-1] for row in actual}, {F(0)})


if __name__ == "__main__":
    unittest.main(verbosity=2)
