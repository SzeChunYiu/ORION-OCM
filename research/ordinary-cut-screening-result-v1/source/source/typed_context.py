"""Explicit homogeneous native context; structural validity is not native authority."""
IDS = ("V0", "V1", "V2")


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def rename(tokens, mapping):
    return [mapping.get(token, token) for token in tokens]


def parameters(kind):
    require(kind in ("class", "wff"), "parameter type")
    return [{"id": key, "type": kind} for key in IDS]


def validate(context):
    require(type(context) is dict and set(context) == {"schema", "parameters", "dv"},
            "context shape")
    require(context["schema"] == "native.typed-context.v1" and context["dv"] == [],
            "context schema/DV")
    rows = context["parameters"]
    require(type(rows) is list and len(rows) == 3, "three parameters")
    for i, row in enumerate(rows):
        require(type(row) is dict and set(row) == {"id", "type", "variable", "floating_label"},
                "parameter descriptor")
        require(row["id"] == IDS[i] and row["type"] in ("class", "wff"), "parameter identity/type")
        for key in ("variable", "floating_label"):
            value = row[key]
            require(type(value) is str and value and
                    all(c.isalnum() or c in "-_." for c in value), "parameter token/label")
    require(len({r["type"] for r in rows}) == 1, "homogeneous parameters")
    require(len({r["variable"] for r in rows}) == 3 and
            len({r["floating_label"] for r in rows}) == 3, "distinct parameter bindings")
    return rows


def from_source(source, order=None):
    require(source["dv"] == [] and source["active_dv"] == [], "source/active DV")
    floating = source["floating"]
    require(type(floating) is list and len(floating) == 3, "three mandatory floats")
    by_variable = {}
    for h in floating:
        require(set(h) == {"label", "statement"} and type(h["statement"]) is list and
                len(h["statement"]) == 2, "floating declaration")
        kind, var = h["statement"]
        require(kind in ("class", "wff") and var not in by_variable, "floating type/identity")
        by_variable[var] = (kind, h["label"])
    chosen = list(by_variable) if order is None else list(order)
    require(len(chosen) == 3 and set(chosen) == set(by_variable), "complete parameter order")
    context = {"schema": "native.typed-context.v1", "dv": [], "parameters": [
        {"id": key, "type": by_variable[var][0], "variable": var,
         "floating_label": by_variable[var][1]} for key, var in zip(IDS, chosen)]}
    validate(context)
    return context


def bijection(context, mapping):
    rows = validate(context)
    variables = {r["variable"] for r in rows}
    require(type(mapping) is dict and set(mapping) == variables and
            all(type(v) is str for v in mapping.values()) and set(mapping.values()) == variables,
            "atomic bijection")
    return mapping
