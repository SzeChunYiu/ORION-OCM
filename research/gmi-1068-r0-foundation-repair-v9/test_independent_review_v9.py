"""Independent review: actual historical data, semantic mutations, and source blobs."""
import copy
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SPEC = importlib.util.spec_from_file_location("independent_r0_subject_v9", HERE / "r0_audit_v9.py")
A = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(A)
AT, PA, TH, DAG = ("ATOMIC_CHECKLIST_V1.json", "PARENT_REGISTRY_V1.json",
                   "THEOREM_STATUS_V1.json", "THEORY_DAG_V1.json")
COVERAGE = {"semantic_positive_controls": 2, "id_schema_cycle_mutations": 255,
            "authority_metadata_mutations": 18, "introduction_blob_bindings": 8}


def change(bundle, path, value, delete=False):
    out = copy.deepcopy(bundle)
    node = out
    for key in path[:-1]:
        node = node[key]
    if delete:
        del node[path[-1]]
    else:
        node[path[-1]] = value
    return out


class IndependentReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline, cls.raw = A.read_bundle(ROOT)

    def require_invalid(self, label, bundle):
        try:
            A.validate(bundle)
        except A.Invalid:
            return
        except Exception as exc:
            self.fail(f"{label}: unexpected exception {type(exc).__name__}: {exc}")
        self.fail(f"{label}: semantic validator accepted the mutation")

    def test_real_control_without_hashes(self):
        with patch.object(A.hashlib, "sha256", side_effect=AssertionError("semantic hash lookup")):
            counts = A.validate(self.baseline)
            self.assertEqual(counts, {"atomic_rows": 205, "rounds": 17, "parent_entries": 13,
                                     "theorem_entries": 9, "dag_nodes": 17, "expected_hostiles": 6})
            reordered = copy.deepcopy(self.baseline)
            for name, field in ((AT, "rows"), (PA, "entries"), (TH, "entries"),
                                (TH, "allowed_status"), (DAG, "nodes")):
                reordered[name][field].reverse()
            for parents in reordered[DAG]["dependencies"].values():
                parents.reverse()
            self.assertEqual(A.validate(reordered), counts)

    def test_255_independent_semantic_mutations(self):
        cases = []
        for name in A.C.SCHEMAS:
            for field in ("source_issue", "schema"):
                if field in self.baseline[name]:
                    cases.append((name + ":" + field, (name, field), True))
        for name, collection in ((AT, "rows"), (PA, "entries"), (TH, "entries")):
            for index in range(len(self.baseline[name][collection])):
                cases.append((f"{name}:{index}:id", (name, collection, index, "id"),
                              "FORGED_SAME_COUNT"))
        for node in self.baseline[DAG]["nodes"]:
            cases.append(("self_cycle:" + node, (DAG, "dependencies", node), [node]))
        self.assertEqual(len(cases), COVERAGE["id_schema_cycle_mutations"])
        with patch.object(A.hashlib, "sha256", side_effect=AssertionError("semantic hash lookup")):
            for label, path, value in cases:
                with self.subTest(mutation=label):
                    self.require_invalid(label, change(self.baseline, path, value))

    def test_authority_metadata_repairs(self):
        cases = []
        for index, row in enumerate(self.baseline[TH]["entries"]):
            if "evidence" in row:
                path = (TH, "entries", index, "evidence")
                for value in ("", "FULL_GMI proven by authoritative source"):
                    cases.append((row["id"] + ":" + repr(value), path, value, False))
                cases.append((row["id"] + ":missing_evidence", path, None, True))
        for index, row in enumerate(self.baseline[PA]["entries"]):
            if "source_type" in row:
                path = (PA, "entries", index, "source_type")
                cases.append((row["id"] + ":false_authority", path, "PEER_REVIEWED_THEOREM", False))
                cases.append((row["id"] + ":missing_source_type", path, None, True))
        cases.append(("extra_truth_authority", (TH, "scientific_truth_certified"), True, False))
        self.assertEqual(len(cases), COVERAGE["authority_metadata_mutations"])
        with patch.object(A.hashlib, "sha256", side_effect=AssertionError("semantic hash lookup")):
            for label, path, value, delete in cases:
                with self.subTest(mutation=label):
                    self.require_invalid(label, change(self.baseline, path, value, delete))

    def test_actual_introduction_blobs(self):
        self.assertEqual(len(A.C.CUSTODY), COVERAGE["introduction_blob_bindings"])
        for name, (commit, expected_digest) in A.C.CUSTODY.items():
            with self.subTest(artifact=name):
                blob = subprocess.check_output(
                    ["/usr/bin/git", "-C", str(ROOT), "show", commit + ":" + A.C.BASE + name])
                self.assertEqual(blob, self.raw[name])
                self.assertEqual(hashlib.sha256(blob).hexdigest(), expected_digest)


if __name__ == "__main__":
    unittest.main()
