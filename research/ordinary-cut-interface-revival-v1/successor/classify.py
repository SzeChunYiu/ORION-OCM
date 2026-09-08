"""Exclusive subtype of a frozen UNKNOWN_INTERFACE root from its P1 contract."""


def floating_types(contract):
    return [h["statement"][0] for h in contract.get("floating") or []]


def classify(contract):
    """First-match exclusive buckets requested for the 54 refusals."""
    n_float = len(contract.get("floating") or [])
    n_ess = len(contract.get("essential") or [])
    n_dv = len(contract.get("dv") or [])
    types = floating_types(contract)
    if n_dv > 0:
        return "extra_DV"
    if n_ess > 0:
        return "extra_$e"
    if any(kind != "class" for kind in types):
        return "non_class_floats"
    if n_float < 3:
        return "missing_3_params"
    return "other"


def subtype_counts(rows):
    counts = {"extra_DV": 0, "extra_$e": 0, "non_class_floats": 0, "missing_3_params": 0, "other": 0}
    for row in rows:
        counts[row["subtype"]] += 1
    return counts
