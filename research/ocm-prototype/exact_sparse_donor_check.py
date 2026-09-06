"""Independent exact residual against the unchanged original Fraction kernel mechanics.

The original dense kernel is built ONLY here, as required checker work. This is
not a sparse end-to-end implementation. No custom elimination or tolerance.
"""
from fractions import Fraction
from ocm.kso import navigation as N
from ocm.kso.warrant import CannotCheck


def verify(ks, seed, alpha, values, *, revoked=(), relevance=None,
           mode=N.NavigationMode.WARRANTED):
    if tuple(values) != ks.ids or any(type(v) is not Fraction for v in values.values()):
        raise CannotCheck("EXACT_DONOR_OUTPUT_CONTRACT")
    matrix = N.navigation_matrix(ks, revoked=revoked, relevance=relevance, mode=mode)
    gated = N.gated_seed(ks, seed, revoked, mode)
    original_step = N.restart_step(matrix.rows, gated, list(values.values()), alpha)
    if list(values.values()) != original_step:
        raise CannotCheck("EXACT_DONOR_ORIGINAL_RESIDUAL_NONZERO")
    return {"independent_residual": "EXACT_ZERO",
            "checker": "original Fraction navigation_matrix + restart_step",
            "checker_dense_cells": len(ks.ids)**2,
            "full_output_entries": len(values)}
