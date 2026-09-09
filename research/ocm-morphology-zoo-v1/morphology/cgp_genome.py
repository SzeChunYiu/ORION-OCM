"""Gated: cgp_genome — MZ-D5 tranche stub (see PROTOCOL_V1.md).

Cartesian genetic programming encoding (E1, MZ-D5): nodes/wires/levels genome compiling to the same CognitiveUnitContractV1 organism.
Not yet implemented; raises NotAuthorized rather than silently degrading to
the direct genome.  Implement only when the #221 ordering reaches MZ-D5.
"""
from __future__ import annotations


class NotAuthorized(NotImplementedError):
    pass


def run(*args, **kwargs):
    raise NotAuthorized("cgp_genome: MZ-D5 tranche not opened")
