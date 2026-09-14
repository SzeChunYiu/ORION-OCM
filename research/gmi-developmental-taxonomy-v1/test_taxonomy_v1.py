"""14 exact controls for the developmental taxonomy (A3).

Covers: mutual exclusivity, joint exhaustiveness, hereditary orthogonality,
parent scaling, query fixture, equivalence, irreducibility, predicate
identity, interface refusal. Sibling source compiled explicitly; -I safe.
"""

from pathlib import Path
import importlib.util
import unittest

path = Path(__file__).with_name("taxonomy_v1.py")
spec = importlib.util.spec_from_loader("taxonomy_checked", loader=None)
mod = importlib.util.module_from_spec(spec)
exec(compile(path.read_bytes(), str(path), "exec"), mod.__dict__)


class WitnessLog(unittest.TestCase):
    def test_length_and_labels(self):
        self.assertEqual(len(mod.WITNESS_LOG), 15)
        labels = [lbl for _, _, lbl in mod.WITNESS_LOG]
        self.assertEqual(labels, ["INFO", "RECODE", "SKILL", "LAW", "MORPH"] * 3)

    def test_mutual_exclusivity(self):
        for before, after, _ in mod.WITNESS_LOG:
            hits = sum([
                mod.p_info(before, after),
                mod.p_recode(before, after),
                mod.p_skill(before, after),
                mod.p_law(before, after),
                mod.p_morph(before, after),
            ])
            self.assertEqual(hits, 1, msg="%r -> %r hits=%d" % (before, after, hits))

    def test_joint_exhaustiveness(self):
        for before, after, _ in mod.WITNESS_LOG:
            self.assertIsNotNone(mod.classify(before, after))

    def test_classify_matches_label(self):
        for before, after, lbl in mod.WITNESS_LOG:
            self.assertEqual(mod.classify(before, after), lbl)

    def test_hereditary_orthogonal(self):
        self.assertTrue(mod.is_hereditary(mod.HEREDITARY_BEFORE, mod.HEREDITARY_AFTER))
        # hereditary step does not fire any of the five g-preserving predicates
        self.assertIsNone(mod.classify(mod.HEREDITARY_BEFORE, mod.HEREDITARY_AFTER))
        # all witness log steps are g-preserving (no hereditary)
        for before, after, _ in mod.WITNESS_LOG:
            self.assertFalse(mod.is_hereditary(before, after))

    def test_p_meta_is_p_law(self):
        for before, after, _ in mod.WITNESS_LOG:
            self.assertEqual(mod.p_meta(before, after), mod.p_law(before, after))


class ParentScaling(unittest.TestCase):
    def test_counts_preserved(self):
        self.assertEqual(mod.global_state_count(), 27)
        self.assertEqual(mod.flat_transition_entries(), 162)
        self.assertEqual(mod.min_state_bits(), 5)

    def test_all_global_states(self):
        states = mod.all_global_states()
        self.assertEqual(len(states), 27)
        self.assertEqual(len(set(states)), 27)

    def test_local_law(self):
        self.assertEqual(mod.query_output(0), 0)
        self.assertEqual(mod.query_output(1), 0)
        self.assertEqual(mod.query_output(2), 1)
        self.assertEqual(mod.teach1_local(0), 2)
        self.assertEqual(mod.teach1_local(1), 1)
        self.assertEqual(mod.teach1_local(2), 2)


class BehaviourAndIrreducibility(unittest.TestCase):
    def test_query_indistinguishable_pair(self):
        self.assertEqual(mod.query_outputs(mod.S_A), (0, 0, 0))
        self.assertEqual(mod.query_outputs(mod.S_B), (0, 0, 0))

    def test_teach_distinguishes(self):
        w = mod.irreducibility_witness()
        self.assertTrue(w["query_match"])
        self.assertTrue(w["successors_differ"])
        self.assertEqual(w["succ_query_a"], (1, 0, 0))
        self.assertEqual(w["succ_query_b"], (0, 0, 0))

    def test_histories_equivalent_iff_same_landing(self):
        ca = mod.C_A
        cb = mod.C_B
        self.assertTrue(mod.histories_equivalent(ca, ca))
        self.assertFalse(mod.histories_equivalent(ca, cb))

    def test_successors_and_outputs_shape(self):
        info = mod.successors_and_outputs(mod.C_A)
        self.assertIn("query", info)
        self.assertIn("teach", info)
        self.assertEqual(len(info["teach"]), 3)

    def test_interfaces_refuse_bad_inputs(self):
        with self.assertRaises(ValueError):
            mod.make_config((0, 0), 0, frozenset(), 0, 0, 0)
        with self.assertRaises(ValueError):
            mod.teach1_global((0, 0, 0), 3)
        with self.assertRaises(ValueError):
            mod.query_output(3)
        with self.assertRaises(ValueError):
            mod.teach1_local(5)


if __name__ == "__main__":
    unittest.main()
