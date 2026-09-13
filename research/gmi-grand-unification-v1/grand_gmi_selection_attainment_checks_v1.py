"""Exact finite diagnostics for MSC-1--3; infinite claims require the prose proof."""
from fractions import Fraction
from itertools import product
import json


class SelectionInputError(ValueError):
    """Malformed finite register or incomplete covering certificate."""


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def validate_profiles(rows, dimension):
    if type(dimension) is not int or dimension < 1 or type(rows) is not dict:
        raise SelectionInputError("declare a positive dimension and a register")
    for name, profile in rows.items():
        if type(name) is not str or not name:
            raise SelectionInputError("nonempty realization identities required")
        if type(profile) is not tuple or len(profile) != dimension:
            raise SelectionInputError("profile violates registered dimension")
        if any(type(x) not in (int, Fraction) for x in profile):
            raise SelectionInputError("exact non-Boolean real coordinates required")


def weakly_better(a, b):
    return all(x <= y for x, y in zip(a, b))


def frontier(rows, dimension):
    validate_profiles(rows, dimension)
    return {name for name, p in rows.items()
            if not any(q != p and weakly_better(q, p) for q in rows.values())}


def selected_property(values):
    values = tuple(values)
    if any(type(value) is not bool for value in values):
        raise SelectionInputError("explicit Boolean property evidence required")
    if not values:
        return "NO_SELECTED_REALIZATION"
    return "DERIVED" if all(values) else "NOT_DERIVED"


def covering_fibers(rows, witness_ids, dimension):
    validate_profiles(rows, dimension)
    witness_ids = tuple(witness_ids)
    if not witness_ids or len(set(witness_ids)) != len(witness_ids):
        raise SelectionInputError("nonempty distinct constructive register required")
    if any(name not in rows for name in witness_ids):
        raise SelectionInputError("construction is not in the feasible register")
    constructions = {name: rows[name] for name in witness_ids}
    if any(not any(weakly_better(c, a) for c in constructions.values())
           for a in rows.values()):
        raise SelectionInputError("construction register does not cover candidates")
    minimal_profiles = {constructions[name] for name in frontier(constructions, dimension)}
    return {name for name, p in rows.items() if p in minimal_profiles}


def scan_reference(rows):
    """Independent sorted scan: any strict dominator has strictly smaller sum."""
    keep = {}
    for name, p in sorted(rows.items(), key=lambda row: (sum(row[1]), row[0])):
        if any(q != p and all(y >= x for x, y in zip(q, p)) for q in keep.values()):
            continue
        keep[name] = p
    return set(keep)


def check_covering_registers():
    points = tuple(product(range(2), range(3)))
    registrations = accepted = rejected = 0
    for labels in product(range(3), repeat=len(points)):
        if 2 not in labels:
            continue
        rows = {str(i): points[i] for i, tag in enumerate(labels) if tag}
        constructions = tuple(str(i) for i, tag in enumerate(labels) if tag == 2)
        expected = scan_reference(rows)
        require(frontier(rows, 2) == expected, "frontier/reference mismatch")
        # On a finite set cofinality is equivalent to containing all minimal profiles.
        covered = {rows[i] for i in expected} <= {rows[i] for i in constructions}
        registrations += 1
        try:
            got = covering_fibers(rows, constructions, 2)
        except SelectionInputError:
            require(not covered, "valid coverage rejected")
            rejected += 1
        else:
            require(covered and got == expected and bool(got), "false closure")
            accepted += 1
    require(accepted > 0 and rejected > 0, "vacuous coverage enumeration")
    return {"registers": registrations, "certified": accepted, "rejected": rejected,
            "independent_scan_agrees": True}


def check_fiber_and_nonvacuity():
    rows = {"neural": (1, 1), "program": (1, 1), "wasteful": (2, 2)}
    selected = covering_fibers(rows, ("neural",), 2)
    require(selected == {"neural", "program"}, "equal-profile fiber lost")
    neural = {name: name == "neural" for name in rows}
    require(selected_property(neural[name] for name in selected) == "NOT_DERIVED",
            "representative property leaked to its whole fiber")
    require(selected_property(()) == "NO_SELECTED_REALIZATION", "vacuous claim")
    require(selected_property((True,)) == "DERIVED", "positive selection rejected")
    return {"selected_fiber": sorted(selected), "neurality_derived": False,
            "empty_selection_status": selected_property(())}


def gap_certificate(lower, upper, rival_lowers):
    rival_lowers = tuple(rival_lowers)
    values = (lower, upper, *rival_lowers)
    if any(type(x) not in (int, Fraction) for x in values) or lower > upper:
        raise SelectionInputError("finite exact well-formed bounds required")
    return {"rivals_excluded": all(upper < x for x in rival_lowers),
            "regret_bound": str(upper - lower)}


def check_approximate_revival():
    # Every finite truncation has an optimum that the next legal term beats.
    for n in range(1, 65):
        finite = {str(i): (Fraction(1, i),) for i in range(1, n + 1)}
        require(frontier(finite, 1) == {str(n)}, "finite attained minimum missing")
        require(Fraction(1, n + 1) < finite[str(n)][0], "descent diagnostic failed")
    eta = Fraction(1, 16)
    witness = Fraction(1, 16)
    certificate = gap_certificate(0, witness, (2,))
    require(certificate == {"rivals_excluded": True, "regret_bound": "1/16"},
            "approximate witness certificate failed")
    require(witness <= eta and witness > 0, "approximate/exact boundary failed")
    require(not gap_certificate(0, 2, (2,))["rivals_excluded"], "tie excluded")
    return {"finite_sequence_extensions": 64, "registered_eta": str(eta),
            "witness_cost": str(witness), "exact_optimum_claimed": False,
            **certificate}


def run():
    return {
        "terminal": "GRAND_GMI_SELECTION_ATTAINMENT_FINITE_CERTIFICATE_GREEN",
        "covering_registers": check_covering_registers(),
        "fiber_and_nonvacuity": check_fiber_and_nonvacuity(),
        "approximate_revival": check_approximate_revival(),
        "infinite_nonattainment_authority": "MSC-1 and MSC-3 written proofs",
        "claim_ceiling": "registered finite diagnostics; no physical family verdict",
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
