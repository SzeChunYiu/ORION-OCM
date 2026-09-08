"""Compile declared typed syntax contracts to a CFG; no theorem search."""
import json
from typed_context import IDS, require

TYPES = ("wff", "class", "setvar")
FIELDS = {"label", "kind", "statement", "floating", "essential", "dv"}


def compile_grammar(contracts, parameters):
    require(type(parameters) is list and len(parameters) == 3, "three parameters")
    require([p.get("id") for p in parameters] == list(IDS), "parameter identities")
    require(len({p.get("type") for p in parameters}) == 1 and
            parameters[0]["type"] in {"class", "wff"}, "homogeneous parameters")
    rows = json.loads(json.dumps(contracts, allow_nan=False))
    catalogue = {}
    rules, unsupported = [], []
    for row in rows:
        require(type(row) is dict and set(row) == FIELDS, "ordinary contract schema")
        label = row["label"]
        require(type(label) is str and label and label not in catalogue, "ordinary labels")
        require(row["kind"] in {"$a", "$p"} and type(row["statement"]) is list and
                row["statement"] and all(type(t) is str for t in row["statement"]), "statement")
        catalogue[label] = row
        kind = row["statement"][0]
        if kind == "|-":
            continue
        try:
            require(kind in TYPES, "undeclared syntax typecode")
            require(not row["essential"] and not row["dv"], "syntax essential/DV context")
            floats = row["floating"]
            require(type(floats) is list and all(set(h) == {"label", "statement"} and
                    type(h["statement"]) is list and len(h["statement"]) == 2 and
                    h["statement"][0] in TYPES for h in floats), "syntax floating frame")
            variables = [h["statement"][1] for h in floats]
            require(len(set(variables)) == len(variables), "duplicate syntax variables")
            pattern = row["statement"][1:]
            require(pattern and all(pattern.count(v) == 1 for v in variables),
                    "nonlinear or missing syntax variable")
            require(not (set(pattern) - set(variables)) & set(IDS), "canonical constant collision")
            occurrence = [t for t in pattern if t in variables]
            rules.append({"label": label, "kind": kind, "pattern": pattern,
                          "variables": dict(zip(variables, [h["statement"][0] for h in floats])),
                          "emit_order": [occurrence.index(v) for v in variables]})
        except (ValueError, TypeError, KeyError) as error:
            unsupported.append({"label": label, "reason": str(error)})
    require(not set(catalogue) & {"cut-f0", "cut-f1", "cut-f2"}, "private floating label collision")
    productive = {parameters[0]["type"]}
    while True:
        added = {r["kind"] for r in rules if set(r["variables"].values()) <= productive}
        if added <= productive:
            break
        productive |= added
    usable = [r for r in rules if set(r["variables"].values()) <= productive]
    constants = set(IDS)
    for r in usable:
        constants.update(t for t in r["pattern"] if t not in r["variables"])
    tokens = {t: "z" + str(i).zfill(8) for i, t in enumerate(sorted(constants))}
    grammar, alternatives, emitted = [], {k: [] for k in productive}, {}
    for i, p in enumerate(parameters):
        name = "f" + str(i)
        alternatives[p["type"]].append(name)
        grammar.append(name + ": " + json.dumps(tokens[p["id"]]))
        emitted[name] = {"float": "cut-f" + str(i)}
    for i, r in enumerate(usable):
        name = "r" + str(i)
        alternatives[r["kind"]].append(name)
        symbols = ["n_" + r["variables"][t] if t in r["variables"]
                   else json.dumps(tokens[t]) for t in r["pattern"]]
        grammar.append(name + ": " + " ".join(symbols))
        emitted[name] = {"label": r["label"], "emit_order": r["emit_order"]}
    for kind in sorted(productive):
        grammar.append("n_" + kind + ": " + " | ".join(alternatives[kind]))
    grammar.append('%ignore " "')
    return {"text": "\n".join(grammar), "tokens": tokens, "rules": emitted,
            "productive": sorted(productive), "catalogue": catalogue,
            "parameters": json.loads(json.dumps(parameters)), "unsupported": unsupported,
            "syntax_contracts": len(rules), "compiled_syntax_contracts": len(usable)}
