"""Real historical input, original-checker replays and isolated semantic mutants."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("audit_v9", HERE / "r0_audit_v9.py")
A = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(A)
ROOT = HERE.parents[1]
AT, DAG, PA, TH, GA, RE = ("ATOMIC_CHECKLIST_V1.json", "THEORY_DAG_V1.json",
                          "PARENT_REGISTRY_V1.json", "THEOREM_STATUS_V1.json",
                          "MERGE_GATE_V1.json", "RESULT_V1.json")


def assign(bundle, path, value):
    node = bundle
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = value


class AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline, cls.raw = A.read_bundle(ROOT)

    def test_real_baseline_and_custody(self):
        result = A.evaluate(ROOT)
        self.assertEqual(result["counts"]["atomic_rows"], 205)
        self.assertEqual(set(result["atoms"]), {f"GMI2-R0-{i:03d}" for i in range(1, 9)})
        self.assertTrue(all(v["status"] == "VERIFIED_GOVERNANCE" for v in result["atoms"].values()))
        self.assertFalse(result["scientific_truth_certified"])
        self.assertEqual(result["overall_closure"], "OPEN")
        self.assertNotIn("head", result["custody"])
        self.assertEqual(result, A.evaluate(ROOT))

    def test_semantic_positive_control_reordering(self):
        b = copy.deepcopy(self.baseline)
        for name, field in ((AT, "rows"), (PA, "entries"), (TH, "entries"),
                            (TH, "allowed_status"), (GA, "requirements"), (DAG, "nodes")):
            b[name][field].reverse()
        for parents in b[DAG]["dependencies"].values():
            parents.reverse()
        self.assertEqual(A.validate(b), A.validate(self.baseline))

    def test_four_original_complete_checker_omissions(self):
        candidate = next(i for i, row in enumerate(self.baseline[TH]["entries"])
                         if row["id"] == "T-CAND-FIXED-POINT")
        mutations = [((AT, "rows", 0, "status"), "ABSOLUTE_TRUTH"),
                     ((AT, "rows", 0, "evidence_kind"), "INVALID_EVIDENCE"),
                     ((PA, "entries", 0, "role"), "GMI_NOVELTY"),
                     ((TH, "entries", candidate, "status"), "PROVED")]
        for path, value in [(None, None)] + mutations:
            b = copy.deepcopy(self.baseline)
            if path is not None:
                assign(b, path, value)
            historical = {"__file__": str(ROOT / A.C.BASE / "check_r0.py"), "__name__": "historical"}
            exec(compile(b["check_r0.py"], historical["__file__"], "exec"), historical)
            historical["load"] = lambda name: copy.deepcopy(b[name])
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(historical["main"](), 0)
            if path is None:
                A.validate(b)
            else:
                with self.subTest(path=path), self.assertRaises(A.Invalid):
                    A.validate(b)

    def test_real_baseline_semantic_mutants(self):
        candidate = next(i for i, row in enumerate(self.baseline[TH]["entries"])
                         if row["id"] == "T-CAND-FIXED-POINT")
        mutations = [
            ((AT, "rows"), self.baseline[AT]["rows"][1:]),
            ((AT, "rows", 1, "id"), self.baseline[AT]["rows"][0]["id"]),
            ((AT, "rows", 0, "authoritative_owner"), "#833/R0"),
            ((AT, "rows", 0, "round"), "R1"), ((AT, "rows", 0, "title"), "replacement"),
            ((AT, "rows", 0, "closes_by_prose"), 0), ((AT, "row_count"), True),
            ((AT, "rows", 0, "evidence_kind"), "FORMAL"),
            ((DAG, "dependencies", "R0"), ["R16"]),
            ((DAG, "dependencies", "R16"), ["R13", "R14", "UNKNOWN"]),
            ((DAG, "dependencies", "R16"), ["R13", "R14"]),
            ((DAG, "dependencies", "R1"), []),
            ((DAG, "dependencies", "R1"), ["R0", "R0"]),
            ((DAG, "nodes"), self.baseline[DAG]["nodes"][:-1]),
            ((PA, "entries", 0, "source_id"), ""),
            ((PA, "entries", 0, "source_id"), "arxiv:invented"),
            ((PA, "entries", 0, "role"), "GMI_NOVELTY"),
            ((PA, "entries", 0, "lane"), "R17"),
            ((PA, "entries", 1, "id"), "P01"),
            ((TH, "entries", candidate, "status"), "PROVED"),
            ((TH, "entries", 0, "status"), "ABSOLUTE_TRUTH"),
            ((TH, "allowed_status"), self.baseline[TH]["allowed_status"] + ["ABSOLUTE_TRUTH"]),
            ((TH, "entries"), self.baseline[TH]["entries"][:-1]),
            ((GA, "requirements"), self.baseline[GA]["requirements"][:-1]),
            ((GA, "valid_nonpositive_terminals"), ["PROVED"]),
            ((RE, "atomic_rows"), 204), ((RE, "claim_ceiling"), "FULL_GMI"),
            ((RE, "source_issue"), True), ((AT, "freeze_commit"), "0" * 40),
            (("FREEZE_V1.md",), self.baseline["FREEZE_V1.md"].replace("working hypothesis", "proved theorem")),
        ]
        for path, value in mutations:
            b = copy.deepcopy(self.baseline)
            assign(b, path, value)
            with self.subTest(path=path), self.assertRaises(A.Invalid):
                A.validate(b)
        for path in [(AT, "rows", 0, "authoritative_owner"), (DAG, "dependencies", "R16")]:
            b = copy.deepcopy(self.baseline)
            node = b
            for key in path[:-1]:
                node = node[key]
            del node[path[-1]]
            with self.subTest(missing=path), self.assertRaises(A.Invalid):
                A.validate(b)

    def test_closed_schemas_and_optional_authority(self):
        mutations = []
        for i, row in enumerate(self.baseline[TH]["entries"]):
            if "evidence" in row:
                mutations.extend([((TH, "entries", i, "evidence"), ""),
                                  ((TH, "entries", i, "evidence"), "FULL_GMI proven universally")])
        for i, row in enumerate(self.baseline[PA]["entries"]):
            if "source_type" in row:
                mutations.append(((PA, "entries", i, "source_type"), "PEER_REVIEWED_THEOREM"))
        mutations.extend([((name, "scientific_truth_certified"), True) for name in A.C.SCHEMAS])
        mutations.extend([((AT, "rows", 0, "scientific_truth_certified"), True),
                          ((TH, "entries", 0, "evidence"), "FULL_GMI proven universally"),
                          ((PA, "entries", 0, "source_type"), "PEER_REVIEWED_THEOREM"),
                          ((AT, "doctrine"), "All scientific claims already proved"),
                          ((DAG, "nodes", 0), False), ((AT, "rows", 0, "id"), []),
                          ((TH, "entries", 0, "owner_round"), 0)])
        for path, value in mutations:
            b = copy.deepcopy(self.baseline)
            assign(b, path, value)
            with self.subTest(path=path), self.assertRaises(A.Invalid):
                A.validate(b)
        for name, field in ((TH, "evidence"), (PA, "source_type")):
            b = copy.deepcopy(self.baseline)
            del next(row for row in b[name]["entries"] if field in row)[field]
            with self.subTest(missing=field), self.assertRaises(A.Invalid):
                A.validate(b)

    def test_custody_separate_from_semantics(self):
        raw = dict(self.raw)
        raw[AT] += b"\n"
        with patch.object(A, "read_bundle", return_value=(self.baseline, raw)):
            with self.assertRaisesRegex(A.Invalid, "FROZEN_CONTENT_DRIFT"):
                A.evaluate(ROOT)
        actual_git = A._git
        def broken(root, *args):
            if args[:2] == ("merge-base", A.C.BASELINE):
                return "0" * 40
            return actual_git(root, *args)
        with patch.object(A, "_git", side_effect=broken):
            with self.assertRaisesRegex(A.Invalid, "BASELINE_NOT_ANCESTOR"):
                A.evaluate(ROOT)

    def test_cli_distinguishes_missing_invalid_unavailable(self):
        with tempfile.TemporaryDirectory() as folder:
            def cli():
                return subprocess.run([sys.executable, "-I", "-B", str(HERE / "r0_audit_v9.py"), folder],
                                      capture_output=True, text=True)
            missing = cli()
            self.assertEqual(missing.returncode, 2)
            self.assertEqual(json.loads(missing.stdout)["status"], "CANNOT_CHECK")
            dest = Path(folder) / A.C.BASE
            dest.mkdir(parents=True)
            for name, data in self.raw.items():
                (dest / name).write_bytes(data)
            unavailable_git = cli()
            self.assertEqual(unavailable_git.returncode, 2)
            (dest / AT).write_text("{invalid")
            invalid = cli()
            self.assertEqual(invalid.returncode, 1)
            self.assertEqual(json.loads(invalid.stdout)["status"], "INVALID")
        with patch.object(Path, "read_bytes", side_effect=PermissionError("denied")):
            with self.assertRaises(A.CannotCheck):
                A.read_bundle(ROOT)


if __name__ == "__main__":
    unittest.main()
