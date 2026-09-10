#!/usr/bin/env python3
"""EB-F0 tests — run as python3 tests/test_ebf0.py (no pytest required)."""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)

import lib  # noqa: E402
import micro_earth as me  # noqa: E402
import parents  # noqa: E402
import theorems  # noqa: E402


def test_price_identity():
    pr = parents.price_identity([1, 2, 3], [0.0, 1.0, 4.0], [0.0, 2.0, 3.0])
    assert pr["ok"], pr


def test_multilevel_decomp():
    ml = parents.multilevel_price([0, 0, 1, 1], [1.0, 3.0, 2.0, 8.0], [1, 2, 1, 4])
    assert ml["ok_decomp"], ml


def test_n_bounds():
    try:
        me.MicroEarth(1)
        raise AssertionError("n=1 must fail")
    except ValueError:
        pass
    me.MicroEarth(2)
    me.MicroEarth(8)
    try:
        me.MicroEarth(9)
        raise AssertionError("n=9 must fail")
    except ValueError:
        pass


def test_clean_no_leak():
    e = me.MicroEarth(2, leak=False)
    assert not e.assay_interferes()


def test_no_lstar():
    cg = lib.load_json(os.path.join(ROOT, "COARSE_GRAINING_INDIVIDUALITY_V1.json"))
    assert cg["frozen_winner_L_star"] is False
    assert cg["outcome_neutral"] is True


def test_theorems_no_fail():
    rows = theorems.run_all()
    fails = [r for r in rows if r.get("status") == "FAIL"]
    assert not fails, fails


def main() -> int:
    tests = [
        test_price_identity, test_multilevel_decomp, test_n_bounds,
        test_clean_no_leak, test_no_lstar, test_theorems_no_fail,
    ]
    for fn in tests:
        fn()
        print("ok", fn.__name__)
    print("ALL_OK", len(tests))
    return 0


if __name__ == "__main__":
    sys.exit(main())
