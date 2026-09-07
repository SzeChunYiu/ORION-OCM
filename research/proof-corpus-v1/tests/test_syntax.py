import hashlib
import unittest
from helpers import api, wrapper


class SyntaxControls(unittest.TestCase):
    def extract(self, text, key="A"):
        return api("corpus_syntax").extract_wrapper(text, key)

    def refuses(self, text, code, key="A"):
        try:
            self.extract(text, key)
        except api("corpus_contract").CorpusError as exc:
            self.assertEqual(exc.code, code)
        else:
            self.fail("invalid wrapper was accepted")

    def test_standard_wrapper_preserves_exact_bytes_and_binding(self):
        text = wrapper()
        row = self.extract(text)
        self.assertEqual(row["theorem_name"], "A")
        self.assertEqual(row["expected_solution"], "P2M.Sol.S_A")
        self.assertEqual(row["wrapper_sha256"], hashlib.sha256(text.encode()).hexdigest())
        self.assertEqual(row["context_source"] + row["declaration_source"] +
                         row["bridge_source"] + row["trailing_source"], text)
        self.assertTrue(row["lexical_only"])

    def test_extra_definition_import_is_preserved(self):
        row = self.extract(wrapper(extra="import Definitions.Compat\n"))
        self.assertIn("Definitions.Compat", row["imports"])
        self.assertIn("Definitions.Compat", row["context_source"])

    def test_universe_and_namespace_context_are_preserved(self):
        text = wrapper(context="universe u\nnamespace N\n", tail="end N\n")
        row = self.extract(text)
        self.assertIn("universe u", row["context_source"])
        self.assertIn("namespace N", row["context_source"])
        self.assertIn("end N", row["trailing_source"])

    def test_no_forced_autoimplicit_preamble(self):
        row = self.extract(wrapper(context=""))
        self.assertTrue(row["declaration_source"].startswith("theorem A"))

    def test_helper_before_target_is_context_not_target(self):
        row = self.extract(wrapper(context="lemma helper : True := by trivial\n"))
        self.assertIn("lemma helper", row["context_source"])
        self.assertNotIn("helper", row["declaration_source"])

    def test_let_type_does_not_terminate_at_assignment(self):
        row = self.extract(wrapper(signature=": let p := True; p"))
        self.assertIn("let p := True", row["declaration_source"])

    def test_leti_type_does_not_terminate_at_assignment(self):
        row = self.extract(wrapper(signature=": letI : Inhabited Nat := ⟨0⟩; True"))
        self.assertIn("letI", row["declaration_source"])

    def test_default_binder_and_by_type_are_preserved(self):
        for signature in ("(n : Nat := 1) : n = n",
                          "(h : True := by trivial) : True"):
            with self.subTest(signature=signature):
                self.assertIn(signature, self.extract(wrapper(signature=signature))["declaration_source"])

    def test_comment_and_string_bridges_do_not_count(self):
        context = ('/- outer /- := by p2m_exact_reverting -/ end -/\n'
                   'def note := "import P2M.Sol.S_FAKE\\n:= by p2m_exact_reverting"\n')
        row = self.extract(wrapper(context=context))
        self.assertNotIn("P2M.Sol.S_FAKE", row["imports"])

    def test_comments_inside_real_bridge_and_escaped_string(self):
        context = 'def note := "a \\" := by p2m_exact_reverting"\n'
        text = wrapper(context=context,
                       body="by /- nested /- x -/ -/ p2m_exact_reverting @_root_.P2MW.S_A.solution")
        self.assertEqual(self.extract(text)["theorem_name"], "A")

    def test_unterminated_comment_and_string_refuse(self):
        for suffix in ('/- unfinished', '"unfinished'):
            with self.subTest(suffix=suffix):
                self.refuses(wrapper() + suffix, "LEXICAL_LAYOUT")

    def test_missing_and_multiple_bridges_refuse(self):
        self.refuses(wrapper(body="by assumption"), "BRIDGE_COUNT")
        self.refuses(wrapper() + wrapper("B"), "BRIDGE_COUNT")

    def test_exact_bridge_target_is_required(self):
        self.refuses(wrapper(body="by p2m_exact_reverting @_root_.P2MW.S_B.solution"),
                     "BRIDGE_TARGET")
        self.refuses(wrapper(body="by p2m_exact_reverting @_root_.P2MW.S_A.solutionExtra"),
                     "BRIDGE_TARGET")

    def test_expected_solution_import_is_required(self):
        self.refuses(wrapper().replace("import P2M.Sol.S_A\n", ""),
                     "PAIR_IMPORT")

    def test_additional_proof_arguments_and_tactics_refuse(self):
        for body in ("by p2m_exact_reverting @_root_.P2MW.S_A.solution 1",
                     "by p2m_exact_reverting @_root_.P2MW.S_A.solution\n  exact True.intro"):
            with self.subTest(body=body):
                self.refuses(wrapper(body=body), "BRIDGE_TAIL")

    def test_wrapper_identity_cannot_inject_module_path(self):
        self.refuses(wrapper(), "MODULE_IDENTITY", "../A")

    def test_import_scanner_masks_nested_comments_strings_and_keeps_order(self):
        text = ('/- import Bad /- import Worse -/ -/\nimport Mathlib Definitions.X\n'
                'def s := "import Nope"\n')
        self.assertEqual(api("corpus_lex").active_imports(text),
                         ("Mathlib", "Definitions.X"))


if __name__ == "__main__":
    unittest.main()
