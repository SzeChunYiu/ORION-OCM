import hashlib
import io
from pathlib import Path
import tempfile
import unittest
from helpers import api
from git_fixture import repository, git


def oid(body):
    return hashlib.sha1(b"blob " + str(len(body)).encode() + b"\0" + body).hexdigest()


class GitControls(unittest.TestCase):
    def test_pinned_objects_ignore_dirty_working_tree_and_extra_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            pin = repository(root, {"Theorems/Thm_A.lean": "original\n",
                                    "html/answer.txt": "must not read"})
            (root / "Theorems/Thm_A.lean").write_text("dirty\n")
            (root / "Theorems/Thm_UNTRACKED.lean").write_text("untracked\n")
            with api("corpus_git").Snapshot(root, pin) as snap:
                rows = list(snap.blobs())
                self.assertEqual([r["path"] for r in rows], ["Theorems/Thm_A.lean"])
                self.assertEqual(rows[0]["body"], b"original\n")
                self.assertEqual(rows[0]["sha256"], hashlib.sha256(b"original\n").hexdigest())
                self.assertEqual(snap.commit, pin)
                self.assertEqual(snap.metrics["blob_bytes_read"], len(b"original\n"))
                self.assertEqual(snap.metrics["largest_blob_bytes"], len(b"original\n"))

    def test_replacement_refs_cannot_change_pinned_blob(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            pin = repository(root, {"Definitions/A.lean": "original"})
            old = git(root, "rev-parse", pin + ":Definitions/A.lean").decode().strip()
            new = git(root, "hash-object", "-w", "--stdin", data=b"replacement").decode().strip()
            git(root, "replace", old, new)
            with api("corpus_git").Snapshot(root, pin) as snap:
                self.assertEqual(list(snap.blobs())[0]["body"], b"original")

    def test_selected_symlink_refuses_before_materializing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            pin = repository(root, {"Definitions/A.lean": ("120000", "../secret")})
            with self.assertRaisesRegex(api("corpus_contract").CorpusError, "SOURCE_MODE"):
                with api("corpus_git").Snapshot(root, pin):
                    self.fail("symlink snapshot accepted")

    def test_tree_paths_and_duplicate_entries_refuse(self):
        module = api("corpus_git")
        error = api("corpus_contract").CorpusError
        good = b"100644 blob " + b"a" * 40 + b"\tTheorems/A.lean\0"
        self.assertEqual(module.parse_tree(good)[0]["path"], "Theorems/A.lean")
        for data in (good + good, good.replace(b"Theorems/A.lean", b"../outside")):
            with self.subTest(data=data), self.assertRaises(error):
                module.parse_tree(data)

    def test_batch_frame_hash_type_size_and_terminator_are_checked(self):
        module = api("corpus_git")
        error = api("corpus_contract").CorpusError
        body = b"abc"
        expected = oid(body)
        header = expected.encode() + b" blob 3\n"
        self.assertEqual(module.read_blob_reply(io.BytesIO(header + body + b"\n"), expected), body)
        bad = [header + b"abd\n", header.replace(b"blob", b"tree") + body + b"\n",
               header + b"ab", header + body + b"x",
               b"0" * 40 + b" blob 3\nabc\n"]
        for data in bad:
            with self.subTest(data=data), self.assertRaises(error):
                module.read_blob_reply(io.BytesIO(data), expected)

    def test_local_reader_environment_excludes_external_git_configuration(self):
        env = api("corpus_git").git_environment("/tmp/fixture")
        self.assertEqual(env["GIT_NO_REPLACE_OBJECTS"], "1")
        self.assertEqual(env["GIT_NO_LAZY_FETCH"], "1")
        self.assertEqual(env["GIT_CONFIG_GLOBAL"], "/dev/null")
        self.assertNotIn("GIT_CONFIG_COUNT", env)
        self.assertNotIn("PYTHONPATH", env)

    def test_non_hex_commit_refuses_without_git_execution(self):
        with self.assertRaisesRegex(api("corpus_contract").CorpusError, "COMMIT_IDENTITY"):
            api("corpus_git").Snapshot(Path("/unavailable"), "main")


if __name__ == "__main__":
    unittest.main()
