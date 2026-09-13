"""Refusal and accounting controls for the delegation-invariant cost coordinate.

The registered checker prints a receipt on the registered path. Every refusal
path is proved here instead, so the capsule never sees stderr or a nonzero exit.
"""
from functools import partial
from pathlib import Path
import json
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent
MODULE = HERE / "grand_gmi_delegation_invariant_cost_checks_v1.py"
RECEIPT = HERE / "GRAND_GMI_DELEGATION_INVARIANT_COST_RECEIPT_V1.json"
DIC = {"__name__": "delegation_invariant_cost_under_test", "__file__": str(MODULE)}
exec(compile(MODULE.read_bytes(), str(MODULE), "exec"), DIC)

WRAPPER = "def f(x):\n    return delegate(x)\n"


def written_net(x):
    a, b, c = x
    s = a + b + c
    h0 = int(s >= 1)
    h1 = int(s >= 2)
    h2 = int(s >= 3)
    return int(h0 - h1 + h2 >= 1)


class RefusalTests(unittest.TestCase):
    """The instrument must refuse rather than guess when it cannot account."""

    def test_unbound_callee_name_is_refused(self):
        with self.assertRaises(DIC["CoordinateRefusal"]):
            DIC["account"]("def f(x):\n    return nowhere(x)\n")

    def test_unaccounted_opcode_is_refused(self):
        # An f-string emits formatting opcodes this instrument does not model.
        with self.assertRaises(DIC["CoordinateRefusal"]):
            DIC["account"]('def f(x):\n    return f"{x}"\n')

    def test_attribute_call_is_refused(self):
        with self.assertRaises(DIC["CoordinateRefusal"]):
            DIC["account"]("def f(x):\n    return x.count(1)\n")

    def test_control_flow_is_refused(self):
        with self.assertRaises(DIC["CoordinateRefusal"]):
            DIC["account"]("def f(x):\n    return [v for v in x]\n")

    def test_recursive_callee_is_refused(self):
        def loop(x):
            return loop(x)

        with self.assertRaises(DIC["CoordinateRefusal"]):
            DIC["account"](WRAPPER, {"delegate": loop})

    def test_nesting_beyond_the_registered_limit_is_refused(self):
        def base(x):
            return 0

        current = base
        for _ in range(10):
            previous = current

            def current(x, _inner=previous):
                return _inner(x)

        with self.assertRaises(DIC["CoordinateRefusal"]):
            DIC["account"](WRAPPER, {"delegate": current})

    def test_source_without_f_is_refused(self):
        with self.assertRaises(DIC["CoordinateRefusal"]):
            DIC["account"]("def g(x):\n    return 0\n")


class AccountingTests(unittest.TestCase):
    """A Python-coded callee is charged; an opaque one is declared unaccounted."""

    def test_python_coded_callee_is_charged_by_recursion(self):
        row = DIC["vector"](WRAPPER, {"delegate": written_net})
        parent = DIC["vector"](DIC["REGISTERED"]["WRITTEN_SHARED_SUM_NET"])
        self.assertGreater(row["opcodes"], parent["opcodes"])
        self.assertEqual(row["unaccounted_calls"], parent["unaccounted_calls"])
        self.assertEqual(DIC["relation"](row, parent), "IS_DOMINATED_BY")

    def test_opaque_callee_is_counted_as_unaccounted(self):
        row = DIC["vector"](WRAPPER, {"delegate": partial(written_net)})
        self.assertEqual(row["unaccounted_calls"], 8)
        self.assertEqual(row["opcodes"], 32)

    def test_export_into_a_builtin_never_dominates(self):
        parent = DIC["vector"](DIC["REGISTERED"]["WRITTEN_SHARED_SUM_NET"])
        export = DIC["vector"](DIC["REGISTERED"]["NET_DELEGATING_THE_SUM"])
        self.assertGreater(export["unaccounted_calls"], parent["unaccounted_calls"])
        self.assertEqual(DIC["relation"](export, parent), "INCOMPARABLE")

    def test_product_order_is_strict_and_antisymmetric(self):
        left = {"opcodes": 88, "unaccounted_calls": 0}
        same = {"opcodes": 88, "unaccounted_calls": 0}
        worse = {"opcodes": 312, "unaccounted_calls": 32}
        self.assertFalse(DIC["dominates"](left, same))
        self.assertFalse(DIC["dominates"](same, left))
        self.assertTrue(DIC["dominates"](left, worse))
        self.assertFalse(DIC["dominates"](worse, left))
        self.assertEqual(DIC["relation"](left, same), "EQUAL")

    def test_registered_realizations_all_compute_parity(self):
        for name, source in DIC["REGISTERED"].items():
            with self.subTest(name=name):
                self.assertTrue(DIC["vector"](source)["exact_parity_on_all_eight_inputs"])


class CapsuleContractTests(unittest.TestCase):
    """What the replay capsule requires of a registered checker."""

    def test_checker_runs_clean_and_matches_the_frozen_receipt(self):
        result = subprocess.run([sys.executable, "-I", "-B", str(MODULE)],
                                cwd=HERE, capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr[-800:])
        self.assertEqual(result.stderr, "")
        observed = json.loads(result.stdout)
        self.assertEqual(observed["terminal"],
                         "GRAND_GMI_DELEGATION_INVARIANT_COST_GREEN_AT_FINITE_SCOPE")
        if RECEIPT.exists():
            frozen = json.loads(RECEIPT.read_text(encoding="utf-8"))
            self.assertEqual(observed, frozen)

    def test_checker_uses_no_bare_assert(self):
        # The suite also runs under -O, which strips assert statements.
        source = MODULE.read_text(encoding="utf-8")
        for line in source.splitlines():
            self.assertFalse(line.strip().startswith("assert "), line)

    def test_receipt_declares_what_it_does_not_establish(self):
        result = subprocess.run([sys.executable, "-I", "-B", str(MODULE)],
                                cwd=HERE, capture_output=True, text=True, timeout=60)
        observed = json.loads(result.stdout)
        self.assertFalse(observed["explicitly_not_established"][
            "universal_delegated_family_exclusion"])
        self.assertFalse(observed["coordinate"]["timing_used"])
        self.assertFalse(observed["coordinate"]["tracing_used"])
        self.assertFalse(observed["rejected_alternative_scalar_charge"][
            "registered_as_the_coordinate"])


if __name__ == "__main__":
    unittest.main()
