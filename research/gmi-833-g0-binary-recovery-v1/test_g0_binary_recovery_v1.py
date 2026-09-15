import json
import sys
import unittest
from itertools import product
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from g0_binary_recovery_v1 import (
    CLAIM_CEILING,
    GRAMMARS,
    candidate_space,
    cross_compiler_check,
    delay1_target,
    exact_solutions,
    finite_certificate,
    identity_target,
    nand_via_nor,
    nor_via_nand,
    pareto_solutions,
    reexecute_synthesis,
    synthesize,
    universal_delay1_check,
)


class G0BinaryRecoveryTests(unittest.TestCase):
    def test_both_gate_grammars_close_registered_boolean_semantics(self):
        for kind in GRAMMARS:
            unary = synthesize(kind, ("X",))
            binary = synthesize(kind, ("S", "X"))
            self.assertEqual(len(unary), 4)
            self.assertEqual(len(binary), 16)
            self.assertTrue(reexecute_synthesis(unary, ("X",)))
            self.assertTrue(reexecute_synthesis(binary, ("S", "X")))

    def test_bounded_cross_compilers(self):
        self.assertTrue(cross_compiler_check())
        for a, b in product((0, 1), repeat=2):
            _, c1 = nand_via_nor(a, b)
            _, c2 = nor_via_nand(a, b)
            self.assertEqual(c1, 4)
            self.assertEqual(c2, 4)

    def test_candidate_space_exact_size(self):
        for kind in GRAMMARS:
            candidates = candidate_space(kind)
            self.assertEqual(len(candidates), 260)
            self.assertEqual(len({c.semantic_id for c in candidates}), 260)

    def test_delay_recovery_unique_and_same_across_grammars(self):
        recovered = []
        for kind in GRAMMARS:
            solutions = exact_solutions(kind, delay1_target)
            self.assertEqual(len(solutions), 1)
            c = solutions[0]
            self.assertEqual(c.state_bits, 1)
            self.assertEqual(c.next_truth, (0, 1, 0, 1))
            self.assertEqual(c.output_truth, (0, 0, 1, 1))
            self.assertEqual(c.gate_count, 0)
            self.assertEqual(universal_delay1_check(c, 8), 510)
            recovered.append(c.semantic_id)
        self.assertEqual(recovered[0], recovered[1])

    def test_delay_matched_no_state_negative(self):
        for kind in GRAMMARS:
            stateless = [c for c in candidate_space(kind) if c.state_bits == 0]
            self.assertEqual(sum(1 for c in stateless if all(
                __import__('g0_binary_recovery_v1').execute(c, seq) == delay1_target(seq)
                for seq in product((0, 1), repeat=4)
            )), 0)
        self.assertNotEqual(delay1_target((0, 0))[1], delay1_target((1, 0))[1])

    def test_identity_selects_stateless_despite_state_availability(self):
        semantic_ids = []
        for kind in GRAMMARS:
            exact = exact_solutions(kind, identity_target)
            self.assertEqual(len(exact), 29)
            pf = pareto_solutions(exact)
            self.assertEqual(len(pf), 1)
            c = pf[0]
            self.assertEqual(c.state_bits, 0)
            self.assertIsNone(c.next_truth)
            self.assertEqual(c.output_truth, (0, 1))
            self.assertEqual(c.resources, (0, 0))
            semantic_ids.append(c.semantic_id)
        self.assertEqual(semantic_ids[0], semantic_ids[1])

    def test_exhaustive_reverse_enumeration_same_pareto_semantics(self):
        for kind in GRAMMARS:
            for target in (delay1_target, identity_target):
                fwd = pareto_solutions(exact_solutions(kind, target, reverse=False))
                rev = pareto_solutions(exact_solutions(kind, target, reverse=True))
                self.assertEqual(fwd, rev)

    def test_receipt_green(self):
        r = finite_certificate()
        self.assertEqual(r["claim_ceiling"], CLAIM_CEILING)
        self.assertEqual(r["verdict"], "GREEN")
        self.assertTrue(all(r["checks"].values()))
        self.assertEqual(r["counts"]["candidates_per_grammar"], 260)
        json.dumps(r, sort_keys=True, separators=(",", ":"))


if __name__ == "__main__":
    unittest.main()
