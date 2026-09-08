"""Admit ground terms by matching P1 syntax contracts. Not a new language."""
SYNTAX_TYPES = ("wff", "class", "setvar")


def syntax_contracts(contracts):
    rows = []
    for row in contracts:
        if row.get("kind") not in ("$a", "$p"):
            continue
        if row.get("essential") or row.get("dv"):
            continue
        statement = row.get("statement")
        if type(statement) is not list or not statement or statement[0] not in SYNTAX_TYPES:
            continue
        if any(type(h.get("statement")) is not list or len(h["statement"]) != 2
               or h["statement"][0] not in SYNTAX_TYPES for h in row.get("floating") or []):
            continue
        rows.append(row)
    return rows


def proof(wanted, tokens, types, axioms):
    """Postfix syntax proof: parameter names then P1 syntax labels."""
    if wanted not in SYNTAX_TYPES:
        raise ValueError("ground type has no syntax proof")
    if type(tokens) is not list or not 0 < len(tokens) <= 512 or any(type(t) is not str for t in tokens):
        raise ValueError("typed ground vector")
    cache = {}

    def parses(kind, index, depth):
        key = (kind, index)
        if key in cache:
            hit = cache[key]
            return [] if hit is None else hit
        if depth > 24:
            cache[key] = []
            return []
        cache[key] = None
        found = []
        if index < len(tokens) and types.get(tokens[index]) == kind:
            found.append((index + 1, [tokens[index]]))
        for row in axioms:
            if row["statement"][0] != kind:
                continue
            floats = {h["statement"][1]: h["statement"][0] for h in row["floating"]}
            pattern = row["statement"][1:]

            def match(pi, ti, acc):
                if pi == len(pattern):
                    return [(ti, acc + [row["label"]])]
                atom = pattern[pi]
                if atom in floats:
                    answers = []
                    for end, sub in parses(floats[atom], ti, depth + 1):
                        answers.extend(match(pi + 1, end, acc + sub))
                    return answers
                if ti < len(tokens) and tokens[ti] == atom:
                    return match(pi + 1, ti + 1, acc)
                return []

            found.extend(match(0, index, []))
        unique = []
        seen = set()
        for end, items in found:
            if end in seen:
                continue
            seen.add(end)
            unique.append((end, items))
        cache[key] = unique
        return unique

    complete = [items for end, items in parses(wanted, 0, 0) if end == len(tokens)]
    if not complete:
        raise ValueError(kind_error(wanted, tokens))
    return complete[0]


def kind_error(wanted, tokens):
    if wanted != "wff":
        return wanted + " type"
    if tokens and tokens[0] == "(":
        return "wff operator"
    return "wff type"
