"""Hostile custody controls plus a portable full-payload replay."""
import copy
import gzip
import io
import json
from pathlib import Path
import shutil
import tarfile
import tempfile
import unittest
from unittest.mock import patch
from subprocess import CompletedProcess
from contract_v1 import AuditError, sha, strict_json
from inputs_v1 import HERE, load_inputs, read_archive
from cohorts_v1 import read_cohorts, source_rows
from native_roles_v1 import native_contract
from graph_census_v1 import describe
from source_population_v1 import population_evidence
from replay_v1 import replay, verify_manifest


class CustodyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.binding, cls.files = load_inputs()

    def test_strict_json_rejects_duplicate_and_nonfinite(self):
        for text in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":1e999}'):
            with self.assertRaises((AuditError, ValueError)): strict_json(text)

    def test_archive_byte_mutation_rejected(self):
        data = (HERE / self.binding["archive"]).read_bytes()
        with self.assertRaises(AuditError): read_archive(data + b"extra", self.binding)

    def test_duplicate_traversal_and_link_members_rejected(self):
        for names, symlink in ((["x", "x"], False), (["../x"], False), (["x"], True)):
            buf = io.BytesIO()
            with tarfile.open(fileobj=buf, mode="w") as tf:
                for name in names:
                    info = tarfile.TarInfo(name)
                    if symlink: info.type = tarfile.SYMTYPE; info.linkname = "outside"
                    else: info.size = 1
                    tf.addfile(info, None if symlink else io.BytesIO(b"a"))
            data = gzip.compress(buf.getvalue(), mtime=0)
            binding = {"archive_sha256": sha(data), "members":
                       {name: {"bytes": 1, "sha256": sha(b"a")} for name in names}}
            with self.assertRaises(AuditError): read_archive(data, binding)

    def test_source_self_hash_mutation_rejected(self):
        files = dict(self.files)
        name = next(n for n in files if n.startswith("sources/"))
        value = strict_json(files[name]); value["seed"] += 99
        files[name] = json.dumps(value).encode()
        with self.assertRaises(AuditError): source_rows(files)

    def test_arm_manifest_or_internal_mutation_rejected(self):
        files = dict(self.files)
        name = "pr551/STAGE_B6_DEV_SAME_TWIN_S1_billy.json"
        value = strict_json(files[name]); value["first_dense_admissible"]["found"] = False
        files[name] = json.dumps(value).encode()
        with self.assertRaises(AuditError): read_cohorts(files)

    def test_selected_source_fingerprint_spoof_rejected(self):
        arms, _, _ = read_cohorts(self.files); sources, rows = source_rows(self.files)
        kinds, roles = native_contract(self.files)
        descriptions = []
        for row in rows:
            d = describe(row["label"], row["text"], kinds, roles)
            d.update({k: row[k] for k in ("origin", "recorded_fingerprint")}); descriptions.append(d)
        arms["SAME/CONTINUED/S1"]["seeding"]["seed_fingerprints"][0] = "0" * 64
        with self.assertRaises(AuditError): population_evidence(arms, sources, descriptions)

    def test_prior_witness_identity_mutation_rejected(self):
        files = dict(self.files)
        value = strict_json(files["prior/WITNESS.json"]); value["raw_genotype"] += " "
        files["prior/WITNESS.json"] = json.dumps(value).encode()
        with self.assertRaises(AuditError): read_cohorts(files)

    def test_portable_unit_replays_without_git_or_repository(self):
        with tempfile.TemporaryDirectory(prefix="b6-census-portable-") as tmp:
            target = Path(tmp) / "unit"; shutil.copytree(HERE, target)
            self.assertFalse((target / ".git").exists())
            result = replay(target)
            self.assertEqual(result["status"], "FULL_STATIC_PAYLOAD_REPLAY_PASS")
            self.assertEqual(result["independent_graph_comparisons"], 437)

    def test_worker_cannot_rebind_mutated_manifest(self):
        with tempfile.TemporaryDirectory(prefix="b6-census-rebind-") as tmp:
            target = Path(tmp) / "unit"; shutil.copytree(HERE, target)
            expected = (target / "CONSUMER_CENSUS_RECEIPT_V1.json").read_text()
            before = (target / "MANIFEST.json").read_bytes()
            def mutate_then_return(cmd, **kwargs):
                core = target / "CORE.md"; core.write_bytes(core.read_bytes() + b"extra\n")
                path = target / "MANIFEST.json"; manifest = strict_json(path.read_bytes())
                manifest["files"]["CORE.md"] = {"bytes": core.stat().st_size,
                                                "sha256": sha(core.read_bytes())}
                path.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
                verify_manifest(target)  # The altered manifest is self-consistent.
                return CompletedProcess(cmd, 0, expected, "")
            with patch("replay_v1.subprocess.run", side_effect=mutate_then_return) as worker:
                with self.assertRaisesRegex(AuditError, "manifest changed during worker"):
                    replay(target)
                self.assertEqual(worker.call_count, 1)
            self.assertNotEqual(before, (target / "MANIFEST.json").read_bytes())
            self.assertEqual(expected, (target / "CONSUMER_CENSUS_RECEIPT_V1.json").read_text())

    def test_unbound_file_and_modified_receipt_rejected(self):
        with tempfile.TemporaryDirectory(prefix="b6-census-hostile-") as tmp:
            target = Path(tmp) / "unit"; shutil.copytree(HERE, target)
            extra = target / "unrecorded.txt"; extra.write_text("extra")
            with self.assertRaises(AuditError): verify_manifest(target)
            extra.unlink()
            path = target / "CONSUMER_CENSUS_RECEIPT_V1.json"; path.write_bytes(path.read_bytes() + b" ")
            with self.assertRaises(AuditError): verify_manifest(target)


if __name__ == "__main__": unittest.main()
