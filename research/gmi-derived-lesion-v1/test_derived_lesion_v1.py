"""10 exact controls for derived lesion matrix (L5). Sibling-compiled; -I safe."""

from pathlib import Path
import importlib.util
import unittest

path = Path(__file__).with_name("derived_lesion_v1.py")
spec = importlib.util.spec_from_loader("lesion_checked", loader=None)
mod = importlib.util.module_from_spec(spec)
mod.__file__ = str(path)
exec(compile(path.read_bytes(), str(path), "exec"), mod.__dict__)


class TableShape(unittest.TestCase):
    def test_counts(self):
        self.assertEqual(len(mod.LESIONS), 8)
        self.assertEqual(len(mod.TASKS), 6)
        t = mod.table()
        self.assertEqual(len(t), 8)
        for row in t.values():
            self.assertEqual(len(row), 6)

    def test_intact_all_one(self):
        for task in mod.TASKS:
            self.assertEqual(mod.success(task, "none"), 1)

    def test_each_derived_lesion_hurts_its_primary(self):
        mapping = {
            "L_mem": "T_mem",
            "L_att": "T_att",
            "L_plan": "T_plan",
            "L_causal": "T_causal",
            "L_social": "T_social",
            "L_consol": "T_consol",
        }
        for lesion, task in mapping.items():
            self.assertEqual(mod.success(task, lesion), 0)

    def test_basis_control_distinct_from_derived(self):
        # L_basis hurts T_plan but is not a derived lesion
        self.assertEqual(mod.success("T_plan", "L_basis"), 0)
        self.assertFalse(mod.is_derived_lesion("L_basis"))
        self.assertTrue(mod.is_derived_lesion("L_plan"))

    def test_row_copy_is_copy(self):
        r = mod.row("L_mem")
        r["T_mem"] = 99
        self.assertEqual(mod.success("T_mem", "L_mem"), 0)


class Dissociation(unittest.TestCase):
    def test_memory_vs_attention(self):
        self.assertTrue(mod.double_dissociated("L_mem", "L_att", "T_mem", "T_att"))

    def test_planning_vs_causal(self):
        self.assertTrue(mod.double_dissociated("L_plan", "L_causal", "T_plan", "T_causal"))

    def test_social_vs_planning(self):
        self.assertTrue(mod.double_dissociated("L_social", "L_plan", "T_social", "T_plan"))

    def test_consol_vs_mem_single_step(self):
        # L_mem hurts both T_mem and T_consol; L_consol hurts only T_consol
        self.assertTrue(mod.double_dissociated("L_mem", "L_consol", "T_mem", "T_consol") is False)
        # but L_consol vs L_att on consol vs att is a dissociation
        self.assertTrue(mod.double_dissociated("L_consol", "L_att", "T_consol", "T_att"))

    def test_all_dissociations_enumerated(self):
        pairs = mod.all_double_dissociations()
        self.assertGreaterEqual(len(pairs), 3)
        self.assertIn(("L_att", "L_mem", "T_att", "T_mem"), pairs)

    def test_summary_counts(self):
        s = mod.summary()
        self.assertEqual(s["lesions"], 8)
        self.assertEqual(s["tasks"], 6)
        self.assertEqual(s["derived_lesions"], 6)

    def test_interfaces_refuse_bad_inputs(self):
        with self.assertRaises(ValueError):
            mod.success("T_mem", "L_unknown")
        with self.assertRaises(ValueError):
            mod.success("T_unknown", "L_mem")
        with self.assertRaises(ValueError):
            mod.mechanism("L_unknown")


if __name__ == "__main__":
    unittest.main()
