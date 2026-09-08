"""Authored finite-list parity controls only; no study or recorded task inputs."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time
import unittest

TARGET = Path(sys.argv.pop(1)).resolve()
RECEIPT = Path(sys.argv.pop(1)).resolve()
START = time.perf_counter()
BEFORE = hashlib.sha256(TARGET.read_bytes()).hexdigest()
SPEC = importlib.util.spec_from_file_location("isolated_row_parity", TARGET)
E = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = E
SPEC.loader.exec_module(E)
FUNCS = (E.g2_rows_equal, E.g3_rows_equal)


def row(name="authored-a"):
    return {"task": name, "enumeration_attempts": 7,
            "unique_candidates_checked": 5, "program": ["inc"],
            "token_word": ["MACRO_A"], "macros_used": ["MACRO_A"],
            "macro_used": True, "verified": True}


class TestAffectedParity(unittest.TestCase):
    def test_nonempty_equal_rows_accept_without_mutation(self):
        left = [row(), row("authored-b")]
        right = copy.deepcopy(left)
        for r in right:
            for k in ("program", "token_word", "macros_used"):
                r[k] = tuple(r[k])
        before = copy.deepcopy((left, right))
        for fn in FUNCS:
            with self.subTest(helper=fn.__name__):
                self.assertTrue(fn(left, right))
        self.assertEqual((left, right), before)

    def test_strict_prefix_rejected_in_both_directions(self):
        one, two = [row()], [row(), row("authored-b")]
        for fn in FUNCS:
            for a, b in ((one, two), (two, one)):
                with self.subTest(helper=fn.__name__, lengths=(len(a), len(b))):
                    self.assertFalse(fn(a, b))

    def test_one_empty_rejected_in_both_directions(self):
        for fn in FUNCS:
            for a, b in (([], [row()]), ([row()], [])):
                with self.subTest(helper=fn.__name__, lengths=(len(a), len(b))):
                    self.assertFalse(fn(a, b))

    def test_two_empty_lists_do_not_establish_parity(self):
        for fn in FUNCS:
            with self.subTest(helper=fn.__name__):
                self.assertFalse(fn([], []))

    def test_each_original_comparison_field_remains_authoritative(self):
        for fn in FUNCS:
            for key in ("task", "enumeration_attempts", "unique_candidates_checked",
                        "program", "token_word"):
                right = row()
                right[key] = ["different"] if isinstance(right[key], list) else "different"
                with self.subTest(helper=fn.__name__, field=key):
                    self.assertFalse(fn([row()], [right]))

    def test_g3_macro_labels_and_order_remain_authoritative(self):
        left = row(); left["macros_used"] = ["MACRO_A", "MACRO_B"]
        for value in (["MACRO_A"], ["MACRO_B", "MACRO_A"]):
            right = copy.deepcopy(left); right["macros_used"] = value
            with self.subTest(macros=value):
                self.assertFalse(E.g3_rows_equal([left], [right]))
                self.assertTrue(E.g2_rows_equal([left], [right]))

    def test_guard_does_not_newly_certify_uncompared_flags(self):
        right = row(); right["verified"] = False; right["macro_used"] = False
        for fn in FUNCS:
            with self.subTest(helper=fn.__name__):
                self.assertTrue(fn([row()], [right]))


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestAffectedParity)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    after = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    modules = {n: str(Path(m.__file__).resolve()) for n, m in sys.modules.items()
               if getattr(m, "__file__", None)}
    forbidden = [n for n in modules if n == "ocm" or n.startswith("ocm.")
                 or n.startswith(("g2_macro", "g3_independent"))]
    receipt = {"schema": "g2.cost-parity.authored-controls.v1", "pid": os.getpid(),
        "ppid": os.getppid(), "cwd": os.getcwd(), "python": sys.executable,
        "python_version": sys.version, "test_file": str(Path(__file__).resolve()),
        "helper_file": str(Path(E.__file__).resolve()), "helper_sha256_before": BEFORE,
        "helper_sha256_after": after, "helper_unchanged": BEFORE == after,
        "test_methods": result.testsRun, "failure_count": len(result.failures),
        "error_count": len(result.errors), "failures": [str(x) for x, _ in result.failures],
        "success": result.wasSuccessful(), "file_backed_modules": modules,
        "forbidden_study_module_imports": forbidden,
        "measured_control_window_s": time.perf_counter() - START,
        "scope": "Authored scalar/list rows only. No index, training, partition, search, native or retained-result execution."}
    with RECEIPT.open("x") as handle:
        json.dump(receipt, handle, indent=2, sort_keys=True); handle.write("\n")
    raise SystemExit(0 if result.wasSuccessful() and BEFORE == after and not forbidden else 1)
