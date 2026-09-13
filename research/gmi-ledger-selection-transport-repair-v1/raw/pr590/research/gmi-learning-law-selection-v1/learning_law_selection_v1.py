"""Exact finite model: which learning law a registered contract selects.

O0 supplies the local decision rule and states that "different premises select
different mechanisms", then stops.  O1/O2/O3 each show a premise *forces* a law.
This module supplies the converse map that is missing: contract -> law.

Nothing here is fitted.  Operation prices are supplied by the contract, so the
selection is conditional on a registered resource contract, never on a constant
chosen by the author.
"""
from fractions import Fraction
from itertools import combinations, product

CAPABILITIES = (
    "DIFFERENTIABLE_OBJECTIVE",
    "EUCLIDEAN_GEOMETRY",
    "SIMPLEX_GEOMETRY",
    "LIKELIHOOD_MODEL",
    "FINITE_HYPOTHESES",
    "DISCRETE_PROGRAM_SPACE",
    "ORDINAL_COMPARISON",
)

OPERATIONS = ("GRADIENT_EVAL", "PROJECTION", "NORMALIZATION",
              "LIKELIHOOD_EVAL", "ENUMERATION", "COMPARISON")

# Each law: the premises O0 names, and the operations it charges.
LAWS = {
    "GRADIENT_STEP": {
        "requires": frozenset({"DIFFERENTIABLE_OBJECTIVE", "EUCLIDEAN_GEOMETRY"}),
        "uses": ("GRADIENT_EVAL", "PROJECTION"),
        "clause": "O1",
    },
    "MIRROR_DESCENT": {
        "requires": frozenset({"DIFFERENTIABLE_OBJECTIVE", "SIMPLEX_GEOMETRY"}),
        "uses": ("GRADIENT_EVAL", "NORMALIZATION"),
        "clause": "O2",
    },
    "BAYES_UPDATE": {
        "requires": frozenset({"LIKELIHOOD_MODEL", "FINITE_HYPOTHESES", "SIMPLEX_GEOMETRY"}),
        "uses": ("LIKELIHOOD_EVAL", "NORMALIZATION"),
        "clause": "O3",
    },
    "EXACT_SEARCH": {
        "requires": frozenset({"DISCRETE_PROGRAM_SPACE"}),
        "uses": ("ENUMERATION",),
        "clause": "core-exact",
    },
    "ORDINAL_HILL_CLIMB": {
        "requires": frozenset({"DISCRETE_PROGRAM_SPACE", "ORDINAL_COMPARISON"}),
        "uses": ("COMPARISON",),
        "clause": "core-ordinal",
    },
}

TERMINALS = ("SELECTED", "UNDETERMINED_TIE", "INFEASIBLE_AT_CONTRACT")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def admissible(capabilities):
    """Laws whose premises the contract supplies.  Pure subset test."""
    caps = frozenset(capabilities)
    require(caps <= frozenset(CAPABILITIES), "unregistered capability")
    return tuple(sorted(n for n, s in LAWS.items() if s["requires"] <= caps))


def cost(law, prices):
    """Charged cost of one law under supplied prices.  Missing price = refusal."""
    require(law in LAWS, "unregistered law: %s" % law)
    total = Fraction(0)
    for op in LAWS[law]["uses"]:
        require(op in prices, "unpriced operation %s for %s" % (op, law))
        p = prices[op]
        require(isinstance(p, Fraction), "price must be exact Fraction")
        require(p >= 0, "negative price")
        total += p
    return total


def select(capabilities, prices):
    """Total map: contract -> terminal.  Single-valued except on declared ties."""
    adm = admissible(capabilities)
    if not adm:
        return {"terminal": "INFEASIBLE_AT_CONTRACT", "law": None,
                "admissible": (), "costs": {}}
    costs = {law: cost(law, prices) for law in adm}
    best = min(costs.values())
    winners = sorted(l for l in adm if costs[l] == best)
    if len(winners) > 1:
        return {"terminal": "UNDETERMINED_TIE", "law": None,
                "admissible": adm, "costs": costs, "tied": tuple(winners)}
    return {"terminal": "SELECTED", "law": winners[0],
            "admissible": adm, "costs": costs}


def all_contracts():
    """The complete finite capability lattice: 2**7 = 128 contracts."""
    for r in range(len(CAPABILITIES) + 1):
        for combo in combinations(CAPABILITIES, r):
            yield frozenset(combo)


def uniform_prices(value=Fraction(1)):
    return {op: value for op in OPERATIONS}


def observational_projection(capabilities, hidden):
    """What an observer sees when `hidden` capabilities are not recorded."""
    return frozenset(capabilities) - frozenset(hidden)
