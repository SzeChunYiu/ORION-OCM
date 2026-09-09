"""Gated: metaevolution — not yet authorized in this tranche (see PROTOCOL_V1.md gates).

Raises NotAuthorized with the gate condition; never silently returns a
weaker algorithm.  Implement only when the #221 ordering reaches it.
"""
from __future__ import annotations


class NotAuthorized(NotImplementedError):
    pass


def run(*args, **kwargs):
    gate = {
        "cma_me": "MZ-D4: requires demonstrated cost/encoding fit (continuous params within family)",
        "cma_mae": "MZ-D4: compare against CMA-ME where flat/weak objectives cause exploration problems",
        "surrogate_qd": "MZ-D4/P10: only after true evaluation cost is measured expensive enough (T0 measured 0.14ms/eval — gate NOT met)",
        "island_qd": "MZ-D8/P13: after fixed-ecology QD is calibrated (MZ-D3)",
        "pbt_inner": "MZ-D7+/P14: inner-loop parent only, after lifetime evaluation exists beyond T0",
        "poet": "MZ-D10/P16: only after Z1-Z3 establish a stable baseline",
        "metaevolution": "MZ-D11/P17: only after P00-P16",
    }["metaevolution"]
    raise NotAuthorized("NOT_AUTHORIZED_YET: %s" % gate)
