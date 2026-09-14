import copy
import importlib.util
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("morphology_descriptor_v1", ROOT / "morphology_descriptor_v1.py")
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


def neutral_descriptor():
    features = {}
    for row in mod.REGISTRY["coordinates"]:
        features[row["id"]] = {
            field: index + 1
            for index, field in enumerate(row["required_fields"])
        }
    return {
        "specimen_id": "opaque-001",
        "source_ref": "private/source/path",
        "features": features,
    }


class RegistryTests(unittest.TestCase):
    def test_exact_twelve_coordinates(self):
        ids = [row["id"] for row in mod.REGISTRY["coordinates"]]
        self.assertEqual(12, len(ids))
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(
            {
                "state_carrier", "operator_structure", "control_routing", "update_channel",
                "memory_organization", "sharing_symmetry", "communication_channel", "tool_channel",
                "verification_path", "resource_footprint", "development_law", "interface_geometry",
            },
            set(ids),
        )
        self.assertEqual("G1", mod.REGISTRY["claim_ceiling"])

    def test_registry_coordinate_language_has_no_forbidden_family_token(self):
        forbidden = [token.casefold() for token in mod.REGISTRY["forbidden_feature_tokens"]]
        for row in mod.REGISTRY["coordinates"]:
            text = json.dumps(row, sort_keys=True).casefold()
            for token in forbidden:
                self.assertNotIn(token, text, (row["id"], token))


class DescriptorTests(unittest.TestCase):
    def test_neutral_descriptor_valid(self):
        mod.validate_descriptor(neutral_descriptor())

    def test_metadata_remint_invariance(self):
        left = neutral_descriptor()
        right = copy.deepcopy(left)
        right["specimen_id"] = "completely-different-id"
        right["source_ref"] = "renamed/source"
        self.assertEqual(mod.predictor_projection(left), mod.predictor_projection(right))
        self.assertEqual(mod.morphology_fingerprint(left), mod.morphology_fingerprint(right))

    def test_identity_fields_never_enter_projection(self):
        specimen = neutral_descriptor()
        projection = mod.predictor_projection(specimen)
        encoded = json.dumps(projection, sort_keys=True)
        self.assertNotIn(specimen["specimen_id"], encoded)
        self.assertNotIn(specimen["source_ref"], encoded)
        self.assertEqual(set(mod.coordinate_contract()), set(projection))

    def test_family_name_in_feature_value_rejected(self):
        for leaked in ("transformer", "CNN", "backpropagation", "random forest"):
            specimen = neutral_descriptor()
            specimen["features"]["state_carrier"]["kind"] = leaked
            with self.assertRaises(ValueError, msg=leaked):
                mod.validate_descriptor(specimen)

    def test_family_name_only_in_excluded_metadata_cannot_affect_projection(self):
        left = neutral_descriptor()
        right = copy.deepcopy(left)
        right["specimen_id"] = "transformer"
        right["source_ref"] = "models/cnn/example"
        self.assertEqual(mod.predictor_projection(left), mod.predictor_projection(right))

    def test_missing_coordinate_rejected(self):
        specimen = neutral_descriptor()
        del specimen["features"]["verification_path"]
        with self.assertRaises(ValueError):
            mod.validate_descriptor(specimen)

    def test_extra_coordinate_rejected(self):
        specimen = neutral_descriptor()
        specimen["features"]["family_name"] = {"value": 1}
        with self.assertRaises(ValueError):
            mod.validate_descriptor(specimen)

    def test_extra_field_rejected(self):
        specimen = neutral_descriptor()
        specimen["features"]["state_carrier"]["architecture"] = 1
        with self.assertRaises(ValueError):
            mod.validate_descriptor(specimen)

    def test_negative_numeric_resource_rejected(self):
        specimen = neutral_descriptor()
        specimen["features"]["resource_footprint"]["compute_units"] = -1
        with self.assertRaises(ValueError):
            mod.validate_descriptor(specimen)

    def test_feature_change_changes_fingerprint(self):
        left = neutral_descriptor()
        right = copy.deepcopy(left)
        right["features"]["resource_footprint"]["compute_units"] += 1
        self.assertNotEqual(mod.morphology_fingerprint(left), mod.morphology_fingerprint(right))


if __name__ == "__main__":
    unittest.main()
