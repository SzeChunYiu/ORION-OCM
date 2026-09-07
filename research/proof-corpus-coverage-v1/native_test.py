"""Authored native adapter controls; no corpus selection or proof search."""
import json
import os
import shutil
import sys
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent
BINARY = ROOT / ".lake/build/bin/ocm_coverage"
FIXTURE = ROOT / "newfixtures/NamespaceFixture.lean"

def request(line, name):
    text = FIXTURE.read_text(encoding="utf-8").splitlines()[line - 1]
    start = text.index("theorem")
    sel = text.index(name)
    position = lambda col: {"line": line, "column": col}
    return {"schema": "ocm.coverage.capture.v1", "operation": "capture",
            "module": ["NamespaceFixture"], "source_path": str(FIXTURE),
            "range": {"start": position(start), "end": position(len(text))},
            "selection_range": {"start": position(sel), "end": position(sel + len(name))}}

def invoke(data, extra_env=None):
    with tempfile.TemporaryDirectory() as tmp:
        inp = Path(tmp) / "request.json"
        inp.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
        env = dict(os.environ, LEAN_SYSROOT="/home/billy/orion-director-work/20260906/f0-development-runtime-v4/lean-4.33.1-linux", LEAN_PATH=str(ROOT / ".lake/build/lib/lean"))
        env.update(extra_env or {})
        argv = [str(BINARY), str(inp), str(Path(tmp) / "out")]
        proc = None
        error = None
        try:
            proc = subprocess.run(argv, env=env, capture_output=True, timeout=30, check=False)
        except BaseException as exc:
            error = exc
        finally:
            stdout = proc.stdout if proc is not None else getattr(error, "output", None)
            stderr = proc.stderr if proc is not None else getattr(error, "stderr", None)
            record_root = os.environ.get("OCM_NATIVE_TEST_RECORD_DIR")
            if record_root:
                dest = Path(record_root) / ("capture-" + str(len(list(Path(record_root).glob("capture-*"))) + 1))
                shutil.copytree(tmp, dest)
                (dest / "process.stdout").write_bytes(stdout or b"")
                (dest / "process.stderr").write_bytes(stderr or b"")
                outcome = "COMPLETED" if proc is not None else (
                    "TIMEOUT" if isinstance(error, subprocess.TimeoutExpired) else "PROCESS_EXCEPTION")
                (dest / "process.json").write_text(json.dumps({
                    "argv": argv, "returncode": proc.returncode if proc is not None else None,
                    "outcome": outcome, "exception": None if error is None else type(error).__name__,
                    "reason": "" if error is None else str(error), "cleanup": "NOT_OBSERVED",
                    "stdout_available": stdout is not None, "stderr_available": stderr is not None}) + "\n")
        if error is not None:
            raise error
        if proc.returncode != 0:
            raise AssertionError((proc.returncode, proc.stdout, proc.stderr))
        return json.loads(proc.stdout), {p.name: p.read_bytes() for p in (Path(tmp) / "out").glob("*")}

class NativeCaptureTests(unittest.TestCase):
    def test_namespace_and_ordered_universe_are_captured(self):
        result, files = invoke(request(4, "same_name"))
        self.assertEqual(result["terminal"], "REFERENCE_CAPTURED", result)
        assoc = json.loads(files["association.json"])
        self.assertEqual(assoc["resolved_name"], "RefAlpha.same_name")
        self.assertEqual(assoc["level_params"], ["u"])
        self.assertEqual(set(files), {"goal.ndjson", "reference.ndjson", "source.ndjson", "association.json", "result.json"})

    def test_renamed_namespace_does_not_choose_by_leaf_name(self):
        result, files = invoke(request(8, "renamed"))
        self.assertEqual(result["terminal"], "REFERENCE_CAPTURED", result)
        self.assertEqual(json.loads(files["association.json"])["resolved_name"], "RenamedScope.renamed")

    def test_unicode_uses_codepoint_columns(self):
        result, files = invoke(request(14, "lemma₂"))
        self.assertEqual(result["terminal"], "REFERENCE_CAPTURED", result)
        self.assertEqual(json.loads(files["association.json"])["resolved_name"], "UnicodeScope.lemma₂")

    def test_wrong_range_refuses_without_a_fallback(self):
        data = request(4, "same_name")
        data["selection_range"]["start"]["column"] += 1
        result, _ = invoke(data)
        self.assertEqual(result["terminal"], "CANNOT_CHECK")
        self.assertIn("NO_EXACT_ASSOCIATION", result["reason"])
        self.assertEqual(result["stage"], "association")


    def test_attribute_modifier_prefix_is_accepted(self):
        result, files = invoke(request(19, "decorated"))
        self.assertEqual(result["terminal"], "REFERENCE_CAPTURED", result)
        self.assertEqual(json.loads(files["association.json"])["range"]["start"]["column"], 0)

    def test_private_imported_ranges_are_available(self):
        data = request(22, "hidden")
        data["range"]["start"]["column"] = 0
        result, files = invoke(data)
        self.assertEqual(result["terminal"], "REFERENCE_CAPTURED", result)
        self.assertIn("PrivateScope.hidden", json.loads(files["association.json"])["resolved_name"])

    def test_duplicate_metadata_does_not_choose_the_first(self):
        result, _ = invoke(request(25, "first"))
        self.assertEqual(result["terminal"], "CANNOT_CHECK", result)
        self.assertIn("AMBIGUOUS_ASSOCIATION", result["reason"])

    def test_import_does_not_run_source_initializers(self):
        with tempfile.TemporaryDirectory() as tmp:
            sentinel = Path(tmp) / "initializer"
            result, files = invoke(request(4, "same_name"),
                                   {"OCM_COVERAGE_INITIALIZER_SENTINEL": str(sentinel)})
            self.assertEqual(result["terminal"], "REFERENCE_CAPTURED", result)
            self.assertFalse(sentinel.exists())
            self.assertFalse(json.loads(files["association.json"])["load_extensions"])


    def test_unique_swapped_metadata_fails_source_header_consistency(self):
        line = next(i for i, s in enumerate(FIXTURE.read_text().splitlines(), 1)
                    if s.startswith("theorem original_target "))
        result, _ = invoke(request(line, "original_target"))
        self.assertEqual(result["terminal"], "CANNOT_CHECK", result)
        self.assertIn("SOURCE_HEADER_NAME_MISMATCH", result["reason"])


    def test_registered_segments_to_actual_exposed_reference_capture(self):
        sys.path.insert(0, str(ROOT.parent / "proof-corpus-v1"))
        from corpus_syntax import extract_wrapper
        from native_ranges import prepare_selector
        source = ROOT / "newfixtures/Theorems/Thm_authored.lean"
        record = extract_wrapper(source.read_text(), "authored")
        prepared = prepare_selector(source.read_bytes(), record, str(source))
        result, files = invoke(prepared["request"])
        self.assertEqual(result["terminal"], "REFERENCE_CAPTURED", result)
        assoc = json.loads(files["association.json"])
        self.assertEqual(assoc["resolved_name"], "RenamedPublicScope.passage")
        self.assertIn("P2MW.S_authored.solution", assoc["reference_dependencies"])


    def test_corrected_qualified_apostrophe_reaches_the_actual_declaration(self):
        sys.path.insert(0, str(ROOT.parent / "proof-corpus-v1"))
        from corpus_syntax import extract_wrapper
        from native_ranges import prepare_selector
        source = ROOT / "newfixtures/Theorems/Thm_apostrophe.lean"
        record = extract_wrapper(source.read_text(), "apostrophe")
        prepared = prepare_selector(source.read_bytes(), record, str(source))
        self.assertEqual(prepared["provenance"]["legacy_name_status"], "CORRECTED_LEGACY_NAME_BOUNDARY")
        result, files = invoke(prepared["request"])
        self.assertEqual(result["terminal"], "REFERENCE_CAPTURED", result)
        self.assertEqual(json.loads(files["association.json"])["resolved_name"], "AliasedScope.proof'")


    def test_two_universes_preserve_their_order(self):
        line = next(i for i, s in enumerate(FIXTURE.read_text().splitlines(), 1)
                    if s.startswith("theorem universes "))
        result, files = invoke(request(line, "universes"))
        self.assertEqual(result["terminal"], "REFERENCE_CAPTURED", result)
        self.assertEqual(json.loads(files["association.json"])["level_params"], ["u", "v"])

    def test_unregistered_axiom_is_reported_without_authorizing_it(self):
        line = next(i for i, s in enumerate(FIXTURE.read_text().splitlines(), 1)
                    if s.startswith("theorem dependent "))
        result, files = invoke(request(line, "dependent"))
        self.assertEqual(result["terminal"], "REFERENCE_CAPTURED", result)
        assoc = json.loads(files["association.json"])
        self.assertEqual(assoc["axioms"], ["UnregisteredSupport.premise"])
        self.assertEqual(assoc["kernel_check"], "NOT_RUN")

if __name__ == "__main__":
    unittest.main()
