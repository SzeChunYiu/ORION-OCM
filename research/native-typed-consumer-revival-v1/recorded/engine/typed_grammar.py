"""Alias-domain syntax uses the existing class and Boolean parsers."""
import typed_boolean as boolean
from vendor import legacy_class_terms as legacy
from typed_context import IDS, require


def checker(parameters):
    require(type(parameters) is list and len(parameters)==3, "typed grammar parameters")
    require([r.get("id") for r in parameters]==list(IDS) and
            len({r.get("type") for r in parameters})==1, "typed grammar identities")
    kind=parameters[0]["type"]
    require(kind in ("wff","class"), "typed grammar type")
    types={key:kind for key in IDS}
    def syntax(wanted,tokens):
        require(type(tokens) is list and 0<len(tokens)<=512 and
                all(type(t) is str for t in tokens), "typed ground vector")
        if kind=="class":
            require(not any(t in legacy.ATOMS for t in tokens), "undeclared legacy atom")
            legacy.syntax(wanted,[dict(zip(IDS,legacy.ATOMS)).get(t,t) for t in tokens])
        else:
            require(wanted=="wff", "no ground inhabitant of requested type")
            # Original turnstile envelope: no extra expression level or tokens.
            boolean.parse_expression(["|-"]+tokens,types)
        return True
    return syntax
