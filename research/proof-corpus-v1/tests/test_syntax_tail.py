import unittest
from helpers import api, wrapper


class TailControls(unittest.TestCase):
    def test_whitespace_or_comment_after_bridge_before_namespace_close_is_allowed(self):
        for suffix in ("   \n", " /- explanation -/\n", " -- explanation\n"):
            with self.subTest(suffix=suffix):
                body = "by p2m_exact_reverting @_root_.P2MW.S_A.solution" + suffix
                text = wrapper(context="namespace N\n", body=body, tail="end N\n")
                row = api("corpus_syntax").extract_wrapper(text, "A")
                self.assertIn("end N", row["trailing_source"])

    def test_same_line_end_is_not_misread_as_namespace_close(self):
        text = wrapper(body="by p2m_exact_reverting @_root_.P2MW.S_A.solution end N")
        with self.assertRaisesRegex(api("corpus_contract").CorpusError, "BRIDGE_TAIL"):
            api("corpus_syntax").extract_wrapper(text, "A")


if __name__ == "__main__":
    unittest.main()
