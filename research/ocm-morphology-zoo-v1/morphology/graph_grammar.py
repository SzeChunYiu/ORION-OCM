"""Gated: graph_grammar — MZ-D5 tranche stub (see PROTOCOL_V1.md).

Graph-grammar encoding (E2, MZ-D5): typed production rules over field/unit vocabularies compiling to the same contract.
Not yet implemented; raises NotAuthorized rather than silently degrading to
the direct genome.  Implement only when the #221 ordering reaches MZ-D5.
"""
from __future__ import annotations


class NotAuthorized(NotImplementedError):
    pass


def run(*args, **kwargs):
    raise NotAuthorized("graph_grammar: MZ-D5 tranche not opened")
