#!/usr/bin/env python3
"""Hostile/selftest for exact_basis_census.py; stdlib only."""
from exact_basis_census import closure, run_census


def main() -> None:
    r = run_census()
    got = {tuple(x["basis"]) for x in r["minimal_complete_bases"]}
    expected = {("NAND",), ("NOR",), ("NOT", "AND"), ("NOT", "OR")}
    assert r["subset_count"] == 63
    assert r["complete_subset_count"] == 54
    assert got == expected, (got, expected)

    # Negative controls: these familiar but incomplete bases must not silently pass.
    assert len(closure(("AND",))) == 3
    assert len(closure(("OR",))) == 3
    assert len(closure(("XOR",))) == 4
    assert len(closure(("NOT", "XOR"))) == 8

    # Positive controls.
    assert len(closure(("NAND",))) == 16
    assert len(closure(("NOR",))) == 16

    print("EXACT_BASIS_CENSUS_SELFTEST_GREEN")


if __name__ == "__main__":
    main()
