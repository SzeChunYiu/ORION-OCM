"""Structural syntax-proof replay, adapted from the existing screen."""
from typed_context import IDS, require
from contract_grammar import TYPES


def substitute(tokens, mapping):
    return [x for token in tokens for x in mapping.get(token, [token])]


def replay(proof, wanted, tokens, compiled):
    require(type(proof) is list and 0 < len(proof) <= 4096, "syntax proof label bound")
    declared = compiled["parameters"][0]["type"]
    leaves = {"cut-f" + str(i): [declared, var] for i, var in enumerate(IDS)}
    stack = []
    for label in proof:
        if label in leaves:
            stack.append(leaves[label])
            continue
        row = compiled["catalogue"][label]
        require(row["kind"] in {"$a", "$p"} and row["statement"][0] in TYPES and
                not row["essential"] and not row["dv"], "syntax contract scope")
        floats = row["floating"]
        n = len(floats)
        require(len(stack) >= n, "syntax stack")
        supplied = stack[-n:] if n else []
        if n:
            del stack[-n:]
        require(all(x[0] == h["statement"][0] for x, h in zip(supplied, floats)), "syntax type")
        mapping = {h["statement"][1]: x[1:] for x, h in zip(supplied, floats)}
        stack.append(substitute(row["statement"], mapping))
    require(stack == [[wanted] + tokens], "syntax conclusion")
    return True
