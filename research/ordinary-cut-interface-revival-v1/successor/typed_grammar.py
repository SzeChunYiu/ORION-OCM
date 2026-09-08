"""Successor class grammar: P1 syntax contracts on a 2- or 3-class packet."""
import sys
from pathlib import Path

import typed_context as TC

SYNTAX = Path(__file__).resolve().parents[2] / "ordinary-cut-syntax-revival-v1" / "successor"
if str(SYNTAX) not in sys.path:
    sys.path.append(str(SYNTAX))
import p1_syntax as S  # noqa: E402


def checker(parameters, contracts):
    TC.require(type(parameters) is list and len(parameters) in TC.ALLOWED_ARITIES,
               "typed grammar parameters")
    TC.require([r.get("id") for r in parameters] == list(TC.ids_for(len(parameters))) and
               {r.get("type") for r in parameters} == {"class"}, "typed grammar identities")
    TC.require(type(contracts) is list and contracts, "syntax contracts")
    types = {row["id"]: row["type"] for row in parameters}
    axioms = S.syntax_contracts(contracts)

    def syntax(wanted, tokens):
        TC.require(type(tokens) is list and 0 < len(tokens) <= 512 and
                   all(type(t) is str for t in tokens), "typed ground vector")
        S.proof(wanted, tokens, types, axioms)
        return True

    return syntax
