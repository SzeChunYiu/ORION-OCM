"""Source custody/status attribution only; no experimental validation."""
import hashlib
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
GMI = REPO / "research/gmi-grand-unification-v1"
BINDINGS = json.loads((HERE / "SOURCE_BINDINGS_V1.json").read_text())


def bound_bytes(root, records):
    """Read exact regular source files; missing or changed bytes are errors."""
    result = {}
    for rel, digest in records.items():
        path = root / rel
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"missing or indirect source: {rel}")
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != digest:
            raise ValueError(f"source drift: {rel}")
        result[rel] = data
    return result


class SourceAttributionControls(unittest.TestCase):
    def test_actual_parent_sources_match(self):
        self.assertEqual(len(bound_bytes(REPO, BINDINGS["parents"])),
                         len(BINDINGS["parents"]))

    def test_all_five_original_files_and_commit_match(self):
        records = BINDINGS["originals"]
        self.assertEqual(len(records), 6)
        self.assertEqual(len(bound_bytes(HERE, records)), 6)

    def test_general_self_test_is_not_an_execution_block(self):
        data = json.loads((GMI / BINDINGS["general_receipt"]).read_text())
        self.assertEqual(data["terminal"],
                         "GRAND_GMI_NN_NONNN_EMPIRICAL_PROTOCOL_SELF_TEST_ALL_GREEN")
        self.assertIs(data["real_empirical_measurements_executed"], False)

    def test_inventory_status_belongs_to_distinct_historical_record(self):
        inventory = json.loads((GMI / "THEOREM_REPLAY_INVENTORY_V1.json").read_text())
        matches = [r for r in inventory["non_replayed_records"]
                   if r["path"] == BINDINGS["registration_receipt"]]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["status"], "PREREGISTRATION_ONLY_NOT_MEASUREMENT")
        general = [r for r in inventory["checkers"]
                   if r["receipt"] == BINDINGS["general_receipt"]]
        self.assertEqual(len(general), 1)
        self.assertNotEqual(general[0]["terminal"], matches[0]["status"])

    def test_wrong_status_and_missing_source_do_not_pass_custody(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = (GMI / BINDINGS["general_receipt"]).read_bytes()
            (root / "source.json").write_bytes(data)
            digest = hashlib.sha256(data).hexdigest()
            self.assertEqual(bound_bytes(root, {"source.json": digest})["source.json"], data)
            changed = json.loads(data)
            changed["terminal"] = "PREREGISTRATION_ONLY_NOT_MEASUREMENT"
            (root / "source.json").write_text(json.dumps(changed))
            with self.assertRaises(ValueError):
                bound_bytes(root, {"source.json": digest})
            (root / "source.json").unlink()
            with self.assertRaises(ValueError):
                bound_bytes(root, {"source.json": digest})


if __name__ == "__main__":
    unittest.main()
