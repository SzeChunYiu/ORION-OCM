import unittest
from helpers import api, wrapper


class PublicFormatControls(unittest.TestCase):
    def test_identifier_segments_do_not_become_command_tokens(self):
        for name in ("hU₂open", "hαopen", "hαopen'", "open'", "open′", "h₂open₃",
                     "Example.open'", "Example.open′", "h\u0301open"):
            with self.subTest(name=name):
                row = api("corpus_syntax").extract_wrapper(wrapper(signature=f"({name} : True) : True"), "A")
                self.assertIn(name, row["declaration_source"])

    def test_escaped_identifier_is_masked_without_losing_raw_source(self):
        for name in ("«open»", "«def name»", "«/- not a comment -/»"):
            row = api("corpus_syntax").extract_wrapper(wrapper(signature=f"({name} : True) : True"), "A")
            self.assertIn(name, row["declaration_source"])

    def test_unclosed_escaped_identifier_refuses(self):
        with self.assertRaisesRegex(api("corpus_contract").CorpusError, "LEXICAL_LAYOUT"):
            api("corpus_syntax").extract_wrapper(wrapper(signature="(«open : True) : True"), "A")

    def test_type_comparison_warning_is_preserved_but_not_executed(self):
        tail = "#p2m_type_eq_warn P2M.Dup.example Example.example\n"
        row = api("corpus_syntax").extract_wrapper(wrapper(tail=tail), "A")
        self.assertEqual(row["trailing_source"].strip(), tail.strip())
        self.assertEqual(row["trailing_directives"], ["UNEVALUATED_P2M_TYPE_EQ_WARN"])
        self.assertEqual(row["semantic_correspondence"], "NOT_ELABORATED")

    def test_masked_literals_remain_tokens_after_solution_reference(self):
        for suffix in (' «extra»', ' "extra"', '\n"extra"\n', ' /- fine -/ "extra"'):
            with self.subTest(suffix=suffix), self.assertRaisesRegex(
                    api("corpus_contract").CorpusError, "BRIDGE_TAIL"):
                api("corpus_syntax").extract_wrapper(wrapper(
                    body="by p2m_exact_reverting @_root_.P2MW.S_A.solution" + suffix), "A")

    def test_masked_literal_cannot_turn_into_import_or_warning_identifier(self):
        with self.assertRaisesRegex(api("corpus_contract").CorpusError, "IMPORT_LAYOUT"):
            api("corpus_lex").active_imports('import "Mathlib"\n')
        with self.assertRaisesRegex(api("corpus_contract").CorpusError, "BRIDGE_TAIL"):
            api("corpus_syntax").extract_wrapper(wrapper(tail='#p2m_type_eq_warn "A" B\n'), "A")

    def test_empty_or_comment_only_import_refuses(self):
        for text in ("import   \n", "import /- comment -/\n"):
            with self.subTest(text=text), self.assertRaisesRegex(
                    api("corpus_contract").CorpusError, "IMPORT_LAYOUT"):
                api("corpus_lex").active_imports(text)

    def test_invalid_or_embedded_warning_is_not_a_bridge(self):
        for tail in ("#p2m_type_eq_warn A\n", "#p2m_type_eq_warn A B extra\n",
                     "#p2m_type_eq_warn A B\nexact True.intro\n"):
            with self.subTest(tail=tail), self.assertRaisesRegex(api("corpus_contract").CorpusError, "BRIDGE_TAIL"):
                api("corpus_syntax").extract_wrapper(wrapper(tail=tail), "A")
        with self.assertRaisesRegex(api("corpus_contract").CorpusError, "BRIDGE_TAIL"):
            api("corpus_syntax").extract_wrapper(
                wrapper(body="by p2m_exact_reverting @_root_.P2MW.S_A.solution #p2m_type_eq_warn A B"), "A")


if __name__ == "__main__":
    unittest.main()
