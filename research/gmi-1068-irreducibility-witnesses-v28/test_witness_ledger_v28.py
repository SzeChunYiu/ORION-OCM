"""Exact original five witness statements and hostile ledger/source controls."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import audit_witnesses_v28 as audit
COVERAGE = {}
IDS = ("ctx0_prefers_a0", "ctx1_prefers_a1", "same_process_different_context",
       "process_models_differ_under_same_context", "scalarization_can_reverse_incomparables")
OLD = ("original_id", "original_statement", "original_source", "original_paper_section")
NEW = ("observer", "constructor_bridge", "omitted_data", "positive_converse", "premises",
       "proof_level", "strongest_parent", "falsifier", "details")


class WitnessLedgerTests(unittest.TestCase):
    def test_actual_witnesses_and_source_mutations(self):
        actual = json.loads((HERE / "WITNESS_TRANSLATIONS_V28.json").read_text())
        expected = {"original_theorems": list(IDS), "reconciled_rows": 5}
        self.assertEqual(audit.verify(ROOT), expected)
        invalid = []
        for field in actual:
            bad = deepcopy(actual); del bad[field]; invalid.append(bad)
        bad = deepcopy(actual); bad["extra"] = ""; invalid.append(bad)
        for value in ("wrong", None, True, 1):
            bad = deepcopy(actual); bad["schema"] = value; invalid.append(bad)
        for value in ([], None, {}, 1):
            bad = deepcopy(actual); bad["rows"] = value; invalid.append(bad)
        for source in ("lean", "paper"):
            bad = deepcopy(actual); del bad["source"][source]; invalid.append(bad)
            for field in ("path", "sha256"):
                bad = deepcopy(actual); del bad["source"][source][field]; invalid.append(bad)
                for value in ("", "changed", None, True, 1, []):
                    bad = deepcopy(actual); bad["source"][source][field] = value; invalid.append(bad)
            bad = deepcopy(actual); bad["source"][source]["extra"] = ""; invalid.append(bad)
        for index, row in enumerate(actual["rows"]):
            self.assertEqual(set(row), set(OLD + NEW))
            for field in OLD + NEW:
                bad = deepcopy(actual); del bad["rows"][index][field]; invalid.append(bad)
                for value in ("", " ", None, True, 0, 1.0, []):
                    bad = deepcopy(actual); bad["rows"][index][field] = value; invalid.append(bad)
            for field in OLD:
                bad = deepcopy(actual); bad["rows"][index][field] += " changed"; invalid.append(bad)
            bad = deepcopy(actual); bad["rows"][index]["extra"] = ""; invalid.append(bad)
            bad = deepcopy(actual); bad["rows"][index] = deepcopy(actual["rows"][(index + 1) % 5]); invalid.append(bad)
            bad = deepcopy(actual); del bad["rows"][index]; invalid.append(bad)
        bad = deepcopy(actual); bad["rows"].reverse(); invalid.append(bad)
        bad = deepcopy(actual); bad["rows"].append(deepcopy(actual["rows"][0])); invalid.append(bad)
        rejected = 0
        with tempfile.TemporaryDirectory(prefix="gmi-v28-witness-") as tmp:
            root = Path(tmp)
            for record in actual["source"].values():
                p = root / record["path"]; p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes((ROOT / record["path"]).read_bytes())
            ledger = root / audit.PACKAGE / "WITNESS_TRANSLATIONS_V28.json"
            ledger.parent.mkdir(parents=True, exist_ok=True)
            ledger.write_text(json.dumps(actual))
            self.assertEqual(audit.verify(root), expected)
            for i, bad in enumerate(invalid):
                ledger.write_text(json.dumps(bad))
                with self.subTest(case=i), self.assertRaises(ValueError):
                    audit.verify(root)
                rejected += 1
            for key in ("lean", "paper"):
                record = actual["source"][key]; p = root / record["path"]
                original = p.read_bytes()
                p.write_bytes(original + b"\n")
                bad = deepcopy(actual)
                bad["source"][key]["sha256"] = hashlib.sha256(p.read_bytes()).hexdigest()
                ledger.write_text(json.dumps(bad))
                with self.assertRaises(ValueError):
                    audit.verify(root)
                rejected += 1
                p.write_bytes(original)
        COVERAGE.update(valid_witness_ledger_controls=1, witness_ledger_mutation_rejections=rejected)
