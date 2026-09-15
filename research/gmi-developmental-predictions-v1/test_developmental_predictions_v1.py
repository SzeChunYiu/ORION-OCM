"""Exact controls for developmental predictions V1 (602 L4).

Sibling-compiled; python -I -B safe; CPython 3.8 compatible.
"""

from pathlib import Path
import importlib.util
import unittest

path = Path(__file__).with_name("developmental_predictions_v1.py")
spec = importlib.util.spec_from_loader("devpred_checked", loader=None)
mod = importlib.util.module_from_spec(spec)
mod.__file__ = str(path)
exec(compile(path.read_bytes(), str(path), "exec"), mod.__dict__)


class ScheduleShape(unittest.TestCase):
    def test_stage_ecology_alignment(self):
        self.assertEqual(len(mod.STAGES), 5)
        self.assertEqual(len(mod.STAGE_ECOLOGY), 5)
        self.assertEqual(len(mod.STRUCTURE_AT_STAGE), 5)

    def test_ecology_monotone_R_V_S(self):
        Rs = [e[1] for e in mod.STAGE_ECOLOGY]
        Vs = [e[2] for e in mod.STAGE_ECOLOGY]
        Ss = [e[3] for e in mod.STAGE_ECOLOGY]
        self.assertEqual(Rs, sorted(Rs))
        self.assertEqual(Vs, sorted(Vs))
        self.assertEqual(Ss, sorted(Ss))

    def test_structure_skill_nondecreasing(self):
        skills = [s[0] for s in mod.STRUCTURE_AT_STAGE]
        self.assertEqual(skills, sorted(skills))

    def test_capability_gate_catalogue_closed(self):
        self.assertEqual(set(mod.CAPABILITIES), set(mod.GATES))


class EmergenceOrdering(unittest.TestCase):
    def test_all_capabilities_emerge(self):
        ordering = mod.predict_emergence_ordering()
        for cap in mod.CAPABILITIES:
            self.assertIsNotNone(ordering[cap], cap)

    def test_perception_before_working_memory(self):
        o = mod.predict_emergence_ordering()
        self.assertLess(
            mod.STAGES.index(o["cap-perception"]),
            mod.STAGES.index(o["cap-working-memory"]),
        )

    def test_procedural_before_composition(self):
        o = mod.predict_emergence_ordering()
        self.assertLess(
            mod.STAGES.index(o["cap-procedural-memory"]),
            mod.STAGES.index(o["cap-compositional-reasoning"]),
        )

    def test_ordered_sequence_sorted(self):
        seq = mod.ordered_emergence_sequence()
        idxs = [mod.STAGES.index(st) for _cap, st in seq]
        self.assertEqual(idxs, sorted(idxs))

    def test_composition_not_before_child(self):
        stage = mod.predict_compositional_abstraction_stage()
        self.assertGreaterEqual(mod.STAGES.index(stage), mod.STAGES.index("child"))


class PriorStructure(unittest.TestCase):
    def test_composition_depends_on_structure(self):
        self.assertTrue(
            mod.depends_on_accumulated_structure("cap-compositional-reasoning")
        )

    def test_perception_does_not_depend_on_structure(self):
        self.assertFalse(mod.depends_on_accumulated_structure("cap-perception"))

    def test_metacognition_needs_law(self):
        deps = mod.prior_structure_dependencies()
        self.assertEqual(deps["cap-metacognition"]["need_law"], 1)
        self.assertTrue(deps["cap-metacognition"]["depends_on_accumulated_structure"])


class SensitivePeriods(unittest.TestCase):
    def test_morph_window_is_selective(self):
        periods = mod.predict_sensitive_periods()
        win = periods["MORPH"]["window"]
        self.assertIsNotNone(win)
        self.assertEqual(win[0], "child")
        self.assertEqual(win[1], "adolescent")

    def test_adult_morph_locked_by_verifier(self):
        self.assertFalse(mod.morph_admissible("adult"))
        self.assertTrue(mod.morph_admissible("child"))


class SocialDepth(unittest.TestCase):
    def test_trajectory_nondecreasing_and_increases(self):
        traj = mod.predict_social_depth_trajectory()
        depths = [d for _s, d in traj]
        self.assertEqual(depths[0], 0)
        for i in range(len(depths) - 1):
            self.assertLessEqual(depths[i], depths[i + 1])
        self.assertGreater(depths[-1], depths[0])

    def test_nested_depth_requires_composition(self):
        # depth >= 3 needs composition; composition emerges at adolescent
        self.assertLess(
            mod.social_inference_depth_at("toddler"),
            mod.SOCIAL_DEPTH_NEEDS_COMPOSITION,
        )
        self.assertGreaterEqual(
            mod.social_inference_depth_at("adolescent"),
            mod.SOCIAL_DEPTH_NEEDS_COMPOSITION,
        )


class HeldOutRegistry(unittest.TestCase):
    def test_registry_loads_and_fit_forbidden(self):
        reg = mod.load_heldout_registry()
        self.assertEqual(reg["schema"], "HeldOutDevelopmentalRegistryV1")
        self.assertTrue(reg["fit_forbidden"])
        self.assertGreaterEqual(len(reg["entries"]), 6)

    def test_fit_refuses_heldout_fields(self):
        with self.assertRaises(ValueError):
            mod.refuse_fit_record({"R": 1, "heldout_outcome": 1})
        with self.assertRaises(ValueError):
            mod.refuse_fit_record({"citation": "smuggle"})
        self.assertTrue(mod.refuse_fit_record({"R": 1, "V": 2, "S": 0}))

    def test_compare_heldout_all_match(self):
        report = mod.compare_heldout()
        self.assertEqual(report["n_mismatch"], 0)
        self.assertEqual(report["n_abstain"], 0)
        self.assertEqual(report["n_match"], report["n_entries"])
        self.assertGreaterEqual(report["n_match"], 6)

    def test_compare_does_not_mutate_gates(self):
        before = dict(mod.GATES)
        mod.compare_heldout()
        self.assertEqual(mod.GATES, before)


class TaxonomyParent(unittest.TestCase):
    def test_taxonomy_crosscheck(self):
        # parent is present in this worktree / CI checkout
        self.assertTrue(mod.crosscheck_taxonomy_structure_kinds())


class Refusals(unittest.TestCase):
    def test_bad_capability_refused(self):
        with self.assertRaises(ValueError):
            mod.emergence_stage("cap-not-real")
        with self.assertRaises(ValueError):
            mod.depends_on_accumulated_structure("nope")

    def test_bad_stage_refused(self):
        with self.assertRaises(ValueError):
            mod.ecology_at("embryo")
        with self.assertRaises(ValueError):
            mod.structure_at(99)


if __name__ == "__main__":
    unittest.main()
