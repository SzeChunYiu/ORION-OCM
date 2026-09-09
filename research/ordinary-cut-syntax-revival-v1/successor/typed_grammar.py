"""Successor alias-domain syntax: P1 syntax contracts on the declared packet type."""
import p1_syntax as S
from typed_context import IDS, require


def checker(parameters, contracts):
    require(type(parameters) is list and len(parameters) == 3, "typed grammar parameters")
    require([r.get("id") for r in parameters] == list(IDS) and
            len({r.get("type") for r in parameters}) == 1, "typed grammar identities")
    kind = parameters[0]["type"]
    require(kind in ("wff", "class"), "typed grammar type")
    require(type(contracts) is list and contracts, "syntax contracts")
    types = {row["id"]: row["type"] for row in parameters}
    axioms = S.syntax_contracts(contracts)

    def syntax(wanted, tokens):
        require(type(tokens) is list and 0 < len(tokens) <= 512 and
                all(type(t) is str for t in tokens), "typed ground vector")
        S.proof(wanted, tokens, types, axioms)
        return True

    return syntax
