"""No corpus data: selectors are derived from authored retained-segment fixtures."""
import copy
import hashlib
from pathlib import Path
import sys
import unittest
from native_ranges import prepare_selector

sha = lambda raw: hashlib.sha256(raw).hexdigest()

def fixture(context="namespace A\n", declaration=" theorem name (α : Type) : True ",
            bridge=":= by p2m_exact_reverting P2MW.S_test.solution", trailing="\nend A\n"):
    parts = dict(context=context, declaration=declaration, bridge=bridge, trailing=trailing)
    text = "".join(parts.values())
    record = {k + "_source": v for k, v in parts.items()}
    record.update({k + "_sha256": sha(v.encode()) for k, v in parts.items()})
    record.update(wrapper_sha256=sha(text.encode()), wrapper_bytes=len(text.encode()),
                  theorem_id="Theorems.Thm_test", theorem_name="name", lexical_only=True,
                  semantic_correspondence="NOT_ELABORATED")
    return text.encode(), record

class SelectorTests(unittest.TestCase):
    def test_exact_source_positions_from_retained_segments(self):
        raw, record = fixture()
        result = prepare_selector(raw, record, "/inputs/source.lean")
        self.assertEqual(result["request"]["range"]["start"], {"line": 2, "column": 1})
        self.assertEqual(result["request"]["selection_range"],
                         {"start": {"line": 2, "column": 9}, "end": {"line": 2, "column": 13}})
        self.assertEqual(result["request"]["module"], ["Theorems", "Thm_test"])
        self.assertEqual(result["provenance"]["wrapper_sha256"], sha(raw))

    def test_unicode_is_codepoints_not_utf8_bytes(self):
        raw, record = fixture(declaration=" theorem name (α : Type) : True ")
        result = prepare_selector(raw, record, "/inputs/source.lean")
        end = result["request"]["range"]["end"]
        self.assertEqual(end["column"], len(record["declaration_source"] + record["bridge_source"]))
        self.assertLess(end["column"], len((record["declaration_source"] + record["bridge_source"]).encode()))

    def test_changed_source_refuses(self):
        raw, record = fixture()
        with self.assertRaisesRegex(ValueError, "WRAPPER_SOURCE_BINDING"):
            prepare_selector(raw.replace(b"True", b"False"), record, "/inputs/source.lean")

    def test_changed_segment_refuses_even_if_its_own_hash_is_repaired(self):
        raw, record = fixture(); record["context_source"] += " "
        record["context_sha256"] = sha(record["context_source"].encode())
        with self.assertRaisesRegex(ValueError, "SEGMENT_RECONSTRUCTION"):
            prepare_selector(raw, record, "/inputs/source.lean")

    def test_changed_registered_name_refuses(self):
        raw, record = fixture(); record["theorem_name"] = "another"
        with self.assertRaisesRegex(ValueError, "REGISTERED_HEADER_NAME"):
            prepare_selector(raw, record, "/inputs/source.lean")

    def test_modifier_prefix_stays_part_of_core_range(self):
        raw, record = fixture(declaration=" private theorem name : True ")
        result = prepare_selector(raw, record, "/inputs/source.lean")
        self.assertEqual(result["request"]["range"]["start"]["column"], 1)
        self.assertEqual(result["request"]["selection_range"]["start"]["column"], 17)

    def test_header_injected_command_is_not_a_declaration_selector(self):
        raw, record = fixture(declaration=" def name : True ")
        with self.assertRaisesRegex(ValueError, "REGISTERED_HEADER_LAYOUT"):
            prepare_selector(raw, record, "/inputs/source.lean")


    def test_parent_trailing_apostrophe_is_explicitly_corrected(self):
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "proof-corpus-v1"))
        from corpus_syntax import extract_wrapper
        text = ("import P2M.Sol.S_test\nnamespace N\n"
                "theorem foo' : True := by p2m_exact_reverting P2MW.S_test.solution\nend N\n")
        record = extract_wrapper(text, "test")
        self.assertEqual(record["theorem_name"], "foo")
        result = prepare_selector(text.encode(), record, "/inputs/source.lean")
        self.assertEqual(result["request"]["selection_range"]["end"]["column"], 12)
        self.assertEqual(result["provenance"]["source_header_name"], "foo'")
        self.assertEqual(result["provenance"]["legacy_name_status"], "CORRECTED_LEGACY_NAME_BOUNDARY")

    def test_qualified_apostrophe_name_uses_the_complete_token(self):
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "proof-corpus-v1"))
        from corpus_syntax import extract_wrapper
        text = ("import P2M.Sol.S_test\n"
                "theorem N.foo' : True := by p2m_exact_reverting P2MW.S_test.solution\n")
        record = extract_wrapper(text, "test")
        result = prepare_selector(text.encode(), record, "/inputs/source.lean")
        self.assertEqual(result["request"]["selection_range"]["end"]["column"], 14)
        self.assertEqual(result["provenance"]["source_header_name"], "N.foo'")

if __name__ == "__main__": unittest.main()
