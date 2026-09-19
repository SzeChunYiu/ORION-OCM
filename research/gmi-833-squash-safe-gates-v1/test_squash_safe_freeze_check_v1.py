"""Tests for squash_safe_freeze_check_v1.py on throw-away git repositories.

Run:  python3 -I -B test_squash_safe_freeze_check_v1.py -v
      python3 -I -O -B test_squash_safe_freeze_check_v1.py -v
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "squash_safe_freeze_check_v1.py")
GIT = "/usr/bin/git" if os.path.exists("/usr/bin/git") else "git"
PKG = "research/gmi-833-fixture-pkg-v1"
IDENT = ["-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
         "-c", "commit.gpgsign=false"]


def git(repo, *args):
    return subprocess.check_output([GIT, "-C", repo] + IDENT + list(args)).decode().strip()


def new_repo():
    d = tempfile.mkdtemp(prefix="ssfc-")
    subprocess.check_call([GIT, "init", "-q", d])
    return d


def commit(repo, files, msg):
    for rel, body in files.items():
        p = os.path.join(repo, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as fh:
            fh.write(body)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", msg)
    return git(repo, "rev-parse", "HEAD")


def delete(repo, rel, msg):
    git(repo, "rm", "-q", rel)
    git(repo, "commit", "-q", "-m", msg)
    return git(repo, "rev-parse", "HEAD")


def run(repo, *extra, freeze="FREEZE_V1.md", impl=("impl_v1.py", "RESULT_V1.json")):
    cmd = [sys.executable, "-I", "-B", SCRIPT, "--repo", repo, "--pkg", PKG,
           "--freeze", freeze]
    for i in impl:
        cmd += ["--impl", i]
    cmd += list(extra)
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = p.stdout.decode().strip().splitlines()
    return p.returncode, (out[-1] if out else "")


def pk(rel):
    return PKG + "/" + rel


class SquashSafeFreezeCheckTests(unittest.TestCase):
    def setUp(self):
        self._dirs = []

    def tearDown(self):
        for d in self._dirs:
            shutil.rmtree(d, ignore_errors=True)

    def repo(self):
        d = new_repo()
        self._dirs.append(d)
        return d

    # --- linear histories: the strict proof must run unchanged ---------------

    def test_linear_freeze_then_impl_ok(self):
        r = self.repo()
        fz = commit(r, {pk("FREEZE_V1.md"): "freeze\n"}, "research(#833): FREEZE_V1")
        commit(r, {pk("impl_v1.py"): "print(1)\n", pk("RESULT_V1.json"): "{}\n"}, "impl")
        rc, line = run(r)
        self.assertEqual(rc, 0, line)
        self.assertTrue(line.startswith("FREEZE_ORDER_OK:" + fz), line)
        self.assertIn("strict_order:2", line)
        self.assertNotIn("NOT_REDERIVABLE", line)

    def test_impl_before_freeze_is_a_violation(self):
        r = self.repo()
        commit(r, {pk("impl_v1.py"): "print(1)\n", pk("RESULT_V1.json"): "{}\n"}, "impl first")
        commit(r, {pk("FREEZE_V1.md"): "freeze\n"}, "research(#833): FREEZE_V1 (late)")
        rc, line = run(r)
        self.assertEqual(rc, 1, line)
        self.assertIn("FREEZE_ORDER_VIOLATION:FREEZE_DOES_NOT_PRECEDE", line)

    def test_linear_with_pinned_freeze_commit_ok(self):
        # The PR #946 shape: freeze commit pinned, reachable, on HEAD's history.
        r = self.repo()
        fz = commit(r, {pk("FREEZE_V1.md"): "freeze\n", pk("PROTOCOL_V1.json"): "{}\n"},
                    "research(#833): freeze protocol")
        commit(r, {pk("impl_v1.py"): "print(1)\n", pk("RESULT_V1.json"): "{}\n"}, "impl")
        rc, line = run(r, "--freeze-commit", fz, "--present-at-freeze", "PROTOCOL_V1.json")
        self.assertEqual(rc, 0, line)
        self.assertTrue(line.startswith("FREEZE_ORDER_OK:" + fz), line)
        for tok in ("freeze_tree_clean:" + fz[:8], "freeze_blob_matches_pinned_commit",
                    "pinned_commit_ancestor_of_head", "frozen_artifacts_present_at_head:1"):
            self.assertIn(tok, line)

    def test_every_other_file_shape(self):
        r = self.repo()
        commit(r, {pk("FREEZE_V3.md"): "freeze\n", pk("FIXTURES.json"): "[]\n"}, "freeze")
        commit(r, {pk("impl_v1.py"): "x\n", pk("CORE.md"): "core\n"}, "impl")
        rc, line = run(r, "--present-at-freeze", "FIXTURES.json", freeze="FREEZE_V3.md", impl=("*",))
        self.assertEqual(rc, 0, line)
        self.assertIn("FREEZE_ORDER_OK:", line)
        self.assertIn("strict_order:2", line)

    # --- squash publication: withhold ONLY the ordering assertion -------------

    def test_squash_published_is_not_rederivable_with_head_checks(self):
        r = self.repo()
        commit(r, {"README.md": "root\n"}, "unrelated root commit")
        sq = commit(r, {pk("FREEZE_V1.md"): "freeze\n", pk("impl_v1.py"): "x\n",
                        pk("RESULT_V1.json"): "{}\n"},
                    "research(#833): package landed by squash (#1234)")
        rc, line = run(r)
        self.assertEqual(rc, 0, line)
        self.assertTrue(line.startswith("FREEZE_ORDER_NOT_REDERIVABLE:" + sq), line)
        for tok in ("freeze_present_at_head", "squash_shape:" + sq[:8],
                    "parent_lacks_freeze_and_impl", "pkg_absent_from_parents",
                    "shared_with_freeze:2"):
            self.assertIn(tok, line)

    def test_squash_published_but_freeze_missing_at_head(self):
        r = self.repo()
        commit(r, {"README.md": "root\n"}, "unrelated root commit")
        commit(r, {pk("FREEZE_V1.md"): "freeze\n", pk("impl_v1.py"): "x\n",
                   pk("RESULT_V1.json"): "{}\n"}, "research(#833): landed (#77)")
        delete(r, pk("FREEZE_V1.md"), "drop the freeze")
        rc, line = run(r)
        self.assertEqual(rc, 1, line)
        self.assertIn("FREEZE_FILE_ABSENT_AT_HEAD", line)

    def test_planted_publishing_commit_without_freeze(self):
        # PR #1053 freeze rule 3, first hostile: a "(#N)" commit that publishes
        # implementation with no freeze at all.
        r = self.repo()
        commit(r, {"README.md": "root\n"}, "unrelated root commit")
        commit(r, {pk("impl_v1.py"): "x\n", pk("RESULT_V1.json"): "{}\n"},
               "research(#833): implementation only (#78)")
        rc, line = run(r)
        self.assertEqual(rc, 1, line)
        self.assertIn("FREEZE_FILE_ABSENT_AT_HEAD", line)

    def test_planted_parent_already_contains_implementation(self):
        # PR #1053 freeze rule 3, second hostile: the parent of the publishing
        # commit already holds implementation bytes.
        r = self.repo()
        commit(r, {pk("impl_v1.py"): "x\n"}, "implementation slipped in early")
        commit(r, {pk("FREEZE_V1.md"): "freeze\n", pk("RESULT_V1.json"): "{}\n"},
               "research(#833): freeze plus receipt (#79)")
        rc, line = run(r)
        self.assertEqual(rc, 1, line)
        self.assertIn("FREEZE_ORDER_VIOLATION", line)

    def test_shared_commit_without_squash_subject_is_post_hoc(self):
        r = self.repo()
        commit(r, {"README.md": "root\n"}, "unrelated root commit")
        commit(r, {pk("FREEZE_V1.md"): "freeze\n", pk("impl_v1.py"): "x\n",
                   pk("RESULT_V1.json"): "{}\n"}, "freeze and implementation together")
        rc, line = run(r)
        self.assertEqual(rc, 1, line)
        self.assertIn("FREEZE_AND_IMPL_SHARE_NON_SQUASH_COMMIT", line)

    def test_shared_merge_commit_is_not_a_squash(self):
        r = self.repo()
        commit(r, {"README.md": "root\n"}, "root")
        base = git(r, "rev-parse", "HEAD")
        main = git(r, "rev-parse", "--abbrev-ref", "HEAD")
        git(r, "checkout", "-q", "-b", "side", base)
        commit(r, {"side.txt": "s\n"}, "side work")
        git(r, "checkout", "-q", main)
        commit(r, {"main.txt": "m\n"}, "main work")
        git(r, "merge", "-q", "--no-commit", "--no-ff", "side")
        commit(r, {pk("FREEZE_V1.md"): "freeze\n", pk("impl_v1.py"): "x\n",
                   pk("RESULT_V1.json"): "{}\n"}, "merge with package smuggled in (#80)")
        rc, line = run(r)
        self.assertEqual(rc, 1, line)
        self.assertIn("FREEZE_AND_IMPL_SHARE_NON_SQUASH_COMMIT", line)
        self.assertIn("parents=2", line)

    def test_later_squash_on_published_package_is_disclosed(self):
        r = self.repo()
        commit(r, {pk("FREEZE_V1.md"): "freeze\n"}, "freeze v1")
        commit(r, {pk("impl_v1.py"): "x\n"}, "impl v1")
        sq = commit(r, {pk("FREEZE_V2.md"): "freeze 2\n", pk("impl_v2.py"): "y\n"},
                    "research(#833): revival (#81)")
        rc, line = run(r, freeze="FREEZE_V2.md", impl=("impl_v2.py",))
        self.assertEqual(rc, 0, line)
        self.assertTrue(line.startswith("FREEZE_ORDER_NOT_REDERIVABLE:" + sq), line)
        self.assertIn("later_squash_pkg_files_in_parent:2", line)
        self.assertNotIn("pkg_absent_from_parents", line)

    # --- pinned bytes and the source freeze commit ----------------------------

    def test_pinned_blob_mismatch_is_a_violation(self):
        r = self.repo()
        commit(r, {pk("FREEZE_V1.md"): "freeze\n"}, "freeze")
        commit(r, {pk("impl_v1.py"): "x\n", pk("RESULT_V1.json"): "{}\n"}, "impl")
        rc, line = run(r, "--freeze-blob", "0" * 40)
        self.assertEqual(rc, 1, line)
        self.assertIn("FREEZE_BYTES_DIFFER_FROM_PINNED_BLOB", line)
        real = git(r, "rev-parse", "HEAD:" + pk("FREEZE_V1.md"))
        rc, line = run(r, "--freeze-blob", real)
        self.assertEqual(rc, 0, line)
        self.assertIn("freeze_blob_matches_pin", line)

    def test_freeze_edited_after_pinned_commit_is_a_violation(self):
        r = self.repo()
        fz = commit(r, {pk("FREEZE_V1.md"): "freeze\n"}, "freeze")
        commit(r, {pk("impl_v1.py"): "x\n", pk("RESULT_V1.json"): "{}\n"}, "impl")
        commit(r, {pk("FREEZE_V1.md"): "freeze, quietly widened\n"}, "edit the freeze")
        rc, line = run(r, "--freeze-commit", fz)
        self.assertEqual(rc, 1, line)
        self.assertIn("FREEZE_BYTES_DIFFER_FROM_PINNED_COMMIT", line)

    def test_source_freeze_commit_tree_holding_impl_is_a_violation(self):
        r = self.repo()
        commit(r, {"README.md": "root\n"}, "root")
        base = git(r, "rev-parse", "HEAD")
        main = git(r, "rev-parse", "--abbrev-ref", "HEAD")
        git(r, "checkout", "-q", "-b", "source", base)
        src = commit(r, {pk("FREEZE_V1.md"): "freeze\n", pk("impl_v1.py"): "x\n"},
                     "freeze (with implementation smuggled in)")
        commit(r, {pk("RESULT_V1.json"): "{}\n"}, "receipt")
        git(r, "checkout", "-q", main)
        commit(r, {pk("FREEZE_V1.md"): "freeze\n", pk("impl_v1.py"): "x\n",
                   pk("RESULT_V1.json"): "{}\n"}, "research(#833): squash of source (#82)")
        rc, line = run(r, "--freeze-commit", src)
        self.assertEqual(rc, 1, line)
        self.assertIn("IMPLEMENTATION_REACHABLE_FROM_FREEZE:impl_v1.py", line)

    def test_source_freeze_commit_clean_and_unreachable_states(self):
        r = self.repo()
        commit(r, {"README.md": "root\n"}, "root")
        base = git(r, "rev-parse", "HEAD")
        main = git(r, "rev-parse", "--abbrev-ref", "HEAD")
        git(r, "checkout", "-q", "-b", "source", base)
        src = commit(r, {pk("FREEZE_V1.md"): "freeze\n"}, "freeze")
        commit(r, {pk("impl_v1.py"): "x\n", pk("RESULT_V1.json"): "{}\n"}, "impl")
        git(r, "checkout", "-q", main)
        sq = commit(r, {pk("FREEZE_V1.md"): "freeze\n", pk("impl_v1.py"): "x\n",
                        pk("RESULT_V1.json"): "{}\n"}, "research(#833): squash of source (#83)")
        rc, line = run(r, "--freeze-commit", src)
        self.assertEqual(rc, 0, line)
        self.assertTrue(line.startswith("FREEZE_ORDER_NOT_REDERIVABLE:" + sq), line)
        self.assertIn("freeze_tree_clean:" + src[:8], line)
        self.assertIn("freeze_blob_matches_pinned_commit", line)
        self.assertIn("pinned_commit_not_on_head_history", line)
        # the same pin, read from a FREEZE_COMMIT.txt inside the package
        with open(os.path.join(r, pk("FREEZE_COMMIT.txt")), "w") as fh:
            fh.write(src + "  freeze commit\n")
        git(r, "add", "-A")
        git(r, "commit", "-q", "-m", "pin file")
        rc, line = run(r, "--freeze-commit-file", "FREEZE_COMMIT.txt")
        self.assertEqual(rc, 0, line)
        self.assertIn("freeze_tree_clean:" + src[:8], line)
        # an unreachable pin is a DISTINCT recorded state, not a pass and not a crash
        rc, line = run(r, "--freeze-commit", "0123456789abcdef0123456789abcdef01234567")
        self.assertEqual(rc, 0, line)
        self.assertIn("FREEZE_ORDER_NOT_REDERIVABLE:", line)
        self.assertIn("freeze_tree:UNREACHABLE:0123456789abcdef0123456789abcdef01234567", line)
        self.assertNotIn("freeze_tree_clean", line)

    # --- could-not-check is its own exit code ---------------------------------

    def test_not_a_git_repo_is_could_not_check(self):
        d = tempfile.mkdtemp(prefix="ssfc-plain-")
        self._dirs.append(d)
        os.makedirs(os.path.join(d, PKG))
        with open(os.path.join(d, pk("FREEZE_V1.md")), "w") as fh:
            fh.write("freeze\n")
        rc, line = run(d)
        self.assertEqual(rc, 2, line)
        self.assertIn("FREEZE_ORDER_COULD_NOT_CHECK:NOT_A_GIT_REPO", line)

    def test_shallow_clone_is_could_not_check(self):
        r = self.repo()
        commit(r, {pk("FREEZE_V1.md"): "freeze\n"}, "freeze")
        commit(r, {pk("impl_v1.py"): "x\n", pk("RESULT_V1.json"): "{}\n"}, "impl")
        d = tempfile.mkdtemp(prefix="ssfc-shallow-")
        self._dirs.append(d)
        shutil.rmtree(d)
        subprocess.check_call([GIT, "clone", "-q", "--depth", "1", "file://" + r, d])
        rc, line = run(d)
        self.assertEqual(rc, 2, line)
        self.assertIn("SHALLOW_CLONE_HAS_NO_HISTORY", line)

    def test_impl_pattern_matching_nothing_is_a_violation(self):
        r = self.repo()
        commit(r, {pk("FREEZE_V1.md"): "freeze\n"}, "freeze")
        commit(r, {pk("impl_v1.py"): "x\n"}, "impl")
        rc, line = run(r, impl=("impl_v1.py", "REAL_RUNS*"))
        self.assertEqual(rc, 1, line)
        self.assertIn("IMPL_PATTERN_MATCHES_NOTHING_AT_HEAD:REAL_RUNS*", line)


if __name__ == "__main__":
    unittest.main()
