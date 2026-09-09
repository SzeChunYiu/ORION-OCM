"""Gated: typed_program_genome — MZ-D5 tranche stub (see PROTOCOL_V1.md).

Typed-program encoding (E3, MZ-D5): linear typed rewrite programs compiling to the same contract.
Not yet implemented; raises NotAuthorized rather than silently degrading to
the direct genome.  Implement only when the #221 ordering reaches MZ-D5.
"""
from __future__ import annotations


class NotAuthorized(NotImplementedError):
    pass


def run(*args, **kwargs):
    raise NotAuthorized("typed_program_genome: MZ-D5 tranche not opened")
