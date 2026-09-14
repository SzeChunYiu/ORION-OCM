"""Test suite for Natural Intelligence Bridge Theorem V1."""
import importlib.util
import os
import sys
import unittest


def load_module_from_path(module_name: str, file_path: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for {module_name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


bridge = load_module_from_path(
    "bridge_witness",
    os.path.join(os.path.dirname(__file__), "bridge_witness.py"),
)


class TestMappingWellDefined(unittest.TestCase):
    def test_valid_mapping_is_well_defined(self):
        mapping = bridge.build_valid_mapping()
        self.assertEqual(len(mapping.morphology_to_taxon), 3)

    def test_inconsistent_mapping_is_well_defined(self):
        mapping = bridge.build_inconsistent_mapping()
        self.assertEqual(len(mapping.morphology_to_taxon), 3)

    def test_trivial_mapping_is_well_defined(self):
        mapping = bridge.build_trivial_mapping()
        self.assertEqual(len(mapping.morphology_to_taxon), 3)
        self.assertEqual(len(set(mapping.morphology_to_taxon.values())), 1)


class TestMappingConsistency(unittest.TestCase):
    def setUp(self):
        self.morphologies = bridge.ALL_MORPHOLOGIES
        self.ecologies = bridge.ALL_ECOLOGIES

    def test_valid_mapping_consistent(self):
        mapping = bridge.build_valid_mapping()
        self.assertTrue(bridge.verify_mapping_consistency(
            self.morphologies, self.ecologies, mapping))

    def test_inconsistent_mapping_fails_consistency(self):
        """alpha+beta share pressure class but map to different taxa."""
        mapping = bridge.build_inconsistent_mapping()
        self.assertFalse(bridge.verify_mapping_consistency(
            self.morphologies, self.ecologies, mapping))

    def test_trivial_mapping_passes_consistency(self):
        mapping = bridge.build_trivial_mapping()
        self.assertTrue(bridge.verify_mapping_consistency(
            self.morphologies, self.ecologies, mapping))


class TestMappingContent(unittest.TestCase):
    def setUp(self):
        self.morphologies = bridge.ALL_MORPHOLOGIES
        self.ecologies = bridge.ALL_ECOLOGIES

    def test_valid_mapping_has_content(self):
        mapping = bridge.build_valid_mapping()
        self.assertTrue(bridge.verify_mapping_content(
            self.morphologies, self.ecologies, mapping))

    def test_trivial_mapping_fails_content(self):
        mapping = bridge.build_trivial_mapping()
        self.assertFalse(bridge.verify_mapping_content(
            self.morphologies, self.ecologies, mapping))


class TestMappingNonTrivial(unittest.TestCase):
    def test_valid_mapping_non_trivial(self):
        self.assertTrue(bridge.verify_mapping_trivial(
            bridge.build_valid_mapping()))

    def test_trivial_mapping_fails_non_trivial(self):
        self.assertFalse(bridge.verify_mapping_trivial(
            bridge.build_trivial_mapping()))


class TestPVR3(unittest.TestCase):
    def test_deterministic(self):
        for m in bridge.ALL_MORPHOLOGIES:
            for e in bridge.ALL_ECOLOGIES:
                self.assertEqual(bridge.pvr3_satisfied(m, e),
                                 bridge.pvr3_satisfied(m, e))

    def test_valid_pairs(self):
        self.assertTrue(bridge.pvr3_satisfied(
            bridge.MORPH_ALPHA, bridge.ECO_SOCIAL))
        self.assertTrue(bridge.pvr3_satisfied(
            bridge.MORPH_BETA, bridge.ECO_SOCIAL))
        self.assertTrue(bridge.pvr3_satisfied(
            bridge.MORPH_GAMMA, bridge.ECO_PREDATOR))

    def test_invalid_pairs(self):
        self.assertFalse(bridge.pvr3_satisfied(
            bridge.MORPH_ALPHA, bridge.ECO_PREDATOR))
        self.assertFalse(bridge.pvr3_satisfied(
            bridge.MORPH_GAMMA, bridge.ECO_SOCIAL))


class TestNegativeTwin(unittest.TestCase):
    def test_inconsistent_mapping_rejected(self):
        result = bridge.verify_bridge_mapping(
            bridge.ALL_MORPHOLOGIES, bridge.ALL_ECOLOGIES,
            bridge.build_inconsistent_mapping())
        self.assertFalse(result["consistent"])
        self.assertTrue(result["content"])
        self.assertTrue(result["non_trivial"])

    def test_valid_mapping_accepted(self):
        result = bridge.verify_bridge_mapping(
            bridge.ALL_MORPHOLOGIES, bridge.ALL_ECOLOGIES,
            bridge.build_valid_mapping())
        self.assertTrue(result["consistent"])
        self.assertTrue(result["content"])
        self.assertTrue(result["non_trivial"])


class TestScopeG2(unittest.TestCase):
    def test_g2_documented(self):
        path = os.path.join(os.path.dirname(__file__),
                            "NATURAL_INTELLIGENCE_BRIDGE_THEOREM_V1.md")
        if os.path.exists(path):
            with open(path) as f:
                content = f.read()
            self.assertIn("G2", content)
            self.assertIn("Ceiling", content)


class TestWitnessIntegration(unittest.TestCase):
    def test_witness_produces_output(self):
        result = bridge.verify_bridge_mapping(
            bridge.ALL_MORPHOLOGIES, bridge.ALL_ECOLOGIES,
            bridge.build_valid_mapping())
        self.assertEqual(set(result.keys()),
                         {"consistent", "content", "non_trivial"})

    def test_witness_negative_fails(self):
        result = bridge.verify_bridge_mapping(
            bridge.ALL_MORPHOLOGIES, bridge.ALL_ECOLOGIES,
            bridge.build_inconsistent_mapping())
        self.assertFalse(result["consistent"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
