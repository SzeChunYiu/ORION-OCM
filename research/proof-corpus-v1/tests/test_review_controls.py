import zlib
from pathlib import Path
import tempfile
import unittest
from helpers import api, wrapper
from git_fixture import repository, git


class ReviewControls(unittest.TestCase):
    def test_selected_child_tree_identity_is_checked(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            pin = repository(root, {"Theorems/Thm_A.lean": "original\n"})
            with api("corpus_git").Snapshot(root, pin) as snapshot:
                self.assertEqual(list(snapshot.blobs())[0]["body"], b"original\n")
            tree = git(root, "rev-parse", pin + ":Theorems").decode().strip()
            old = git(root, "cat-file", "tree", tree)
            new_blob = git(root, "hash-object", "-w", "--stdin", data=b"changed\n").decode().strip()
            replacement = old[:-20] + bytes.fromhex(new_blob)
            frame = b"tree " + str(len(replacement)).encode() + b"\0" + replacement
            loose = root / ".git/objects" / tree[:2] / tree[2:]
            loose.chmod(0o644)
            loose.write_bytes(zlib.compress(frame))
            with self.assertRaisesRegex(api("corpus_contract").CorpusError, "SOURCE_TREE_IDENTITY"):
                with api("corpus_git").Snapshot(root, pin) as snapshot:
                    list(snapshot.blobs())

    def test_bridge_cannot_attach_to_helper_across_new_declaration(self):
        for declaration in ("def A", "private noncomputable def A", "@[simp] def A"):
            text = ("import P2M.Sol.S_A\n"
                    "theorem helper : True := by trivial\n" + declaration +
                    " : True := by p2m_exact_reverting @_root_.P2MW.S_A.solution\n")
            with self.subTest(declaration=declaration), self.assertRaisesRegex(
                    api("corpus_contract").CorpusError, "DECLARATION_ASSOCIATION"):
                api("corpus_syntax").extract_wrapper(text, "A")

    def test_same_line_command_boundary_cannot_attach_to_helper(self):
        text = ("import P2M.Sol.S_A\n"
                "theorem helper : True := True.intro def A : True := by "
                "p2m_exact_reverting @_root_.P2MW.S_A.solution\n")
        with self.assertRaisesRegex(api("corpus_contract").CorpusError, "DECLARATION_ASSOCIATION"):
            api("corpus_syntax").extract_wrapper(text, "A")

    def test_identifier_suffix_cannot_consume_a_real_following_command(self):
        text = ("import P2M.Sol.S_A\n"
                "theorem helper : True := myprivate def A : True := by "
                "p2m_exact_reverting @_root_.P2MW.S_A.solution\n")
        with self.assertRaisesRegex(api("corpus_contract").CorpusError, "DECLARATION_ASSOCIATION"):
            api("corpus_syntax").extract_wrapper(text, "A")

    def test_qualified_keyword_identifier_does_not_look_like_command(self):
        row = api("corpus_syntax").extract_wrapper(wrapper(signature=": Example.def"), "A")
        self.assertIn("Example.def", row["declaration_source"])

    def test_prior_helper_and_nested_type_assignment_remain_allowed(self):
        text = wrapper(context="def helper : Nat := 1\nlemma useful : True := by trivial\n",
                       signature=": letI : Inhabited Nat := ⟨0⟩; True")
        row = api("corpus_syntax").extract_wrapper(text, "A")
        self.assertEqual(row["theorem_name"], "A")
        self.assertNotIn("lemma useful", row["declaration_source"])


if __name__ == "__main__":
    unittest.main()
