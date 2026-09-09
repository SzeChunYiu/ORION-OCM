"""Batch descriptor computation over (encoded batch, tape outputs) — GS GPU lane.

Descriptor arithmetic is NEVER reimplemented: structural descriptors are
computed at encode time by evaluation.descriptors.structural_descriptors
(the real zoo function); behavioral / developmental / transfer-profile
descriptors are computed here by calling the real zoo functions with the
tape's per-organism evaluation dicts and a minimal genome-length shim.
Vectorizable parts (the B/D registry projections) are plain column math
over already-exact per-row values.
"""
from __future__ import annotations

from typing import Any, Dict, List, Sequence

from evaluation.descriptors import (DESCRIPTOR_REGISTRY,
                                    behavioral_descriptors,
                                    developmental_descriptors,
                                    transfer_profile)
from evaluation.objectives import dev_score, objective_vector


class _GenomeShim:
    """Minimal org.genome stand-in: only len(genome.U) is consumed."""

    def __init__(self, n_units: int) -> None:
        self.U = [None] * n_units


class _OrgShim:
    def __init__(self, n_units: int) -> None:
        self.genome = _GenomeShim(n_units)


def descriptors_for_batch(batch: Dict[str, Any],
                          tape_out: List[Dict[str, Any]],
                          archive: str = "S_structural_2d"
                          ) -> List[Dict[str, float]]:
    """Descriptor dict per organism for any registered archive.

    Equivalent to evaluation.descriptors.descriptors_for per organism, minus
    the recompilation (structure came from encode time, behaviour from the
    batched tape).
    """
    n_units = batch["columns"]["n_units"]
    out: List[Dict[str, float]] = []
    for i, rec in enumerate(tape_out):
        ev = rec["evaluation"]
        meta = batch["meta"][i]
        if archive.startswith("S"):
            d = dict(meta["_structural"])
        elif archive.startswith("B"):
            d = behavioral_descriptors(_OrgShim(int(n_units[i])), ev)
        else:
            d = developmental_descriptors(_OrgShim(int(n_units[i])), ev)
        out.append(d)
    return out


def descriptor_matrix(batch: Dict[str, Any],
                      tape_out: List[Dict[str, Any]],
                      archive: str = "S_structural_2d"
                      ) -> List[List[float]]:
    """Row vectors in the registry's dim order (surrogate input X)."""
    dims = _dims_for(archive)
    rows = descriptors_for_batch(batch, tape_out, archive)
    return [[float(r[k]) for k in dims] for r in rows]


def _dims_for(archive: str) -> Sequence[str]:
    return DESCRIPTOR_REGISTRY[archive]["dims"]


def objective_vectors(tape_out: List[Dict[str, Any]]) -> List[List[float]]:
    """Frozen objective vectors + dev_score per organism (real zoo funcs)."""
    return [objective_vector(rec["evaluation"]) for rec in tape_out]


def dev_scores(tape_out: List[Dict[str, Any]]) -> List[float]:
    return [dev_score(rec["evaluation"]) for rec in tape_out]


def transfer_profiles(tape_out: List[Dict[str, Any]]) -> List[List[float]]:
    return [transfer_profile(rec["evaluation"]) for rec in tape_out]
