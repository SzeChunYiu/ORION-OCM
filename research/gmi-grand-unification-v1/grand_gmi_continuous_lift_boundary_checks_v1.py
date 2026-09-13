"""CL V2: order, attainment, effective enclosure and declaration-scope controls."""
from fractions import Fraction as F
from itertools import product
import json

FIELDS = ("attainment_witness", "measurable_response_kernels", "effective_description",
          "admitted_operations", "measured_resource_contract")


class ContractError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def rational(value, positive=False):
    if type(value) not in (int, F) or value < 0 or (positive and value == 0):
        raise ContractError("finite exact nonnegative rational required; positive when specified")
    return F(value)


def tail_cost(n):
    if type(n) is not int or n < 1:
        raise ContractError("positive integer tail index required")
    return 1+F(1, n)


def epsilon_witness(epsilon):
    epsilon = rational(epsilon, positive=True)
    n = max(1, (epsilon.denominator+epsilon.numerator-1)//epsilon.numerator)
    return n, tail_cost(n)


def finite_enclosure(values, lower, upper, witness, tolerance):
    values = tuple(rational(v) for v in values)
    lower, upper, tolerance = map(rational, (lower, upper, tolerance))
    if not values or type(witness) is not int or not 0 <= witness < len(values):
        raise ContractError("nonempty complete finite table and valid witness index required")
    return lower <= min(values) <= values[witness] <= upper and upper-lower <= tolerance


def grid_enclosure(n):
    """For the proved 1-Lipschitz objective abs(x-1/3) on [0,1]."""
    if type(n) is not int or n < 1:
        raise ContractError("positive integer grid denominator required")
    values = tuple(abs(F(j, n)-F(1, 3)) for j in range(n+1))
    index = min(range(n+1), key=lambda j: values[j])
    upper = values[index]
    lower = max(F(0), upper-F(1, 2*n))
    return lower, upper, F(index, n)


def accounting_certificate(relaxed_values, allocation, accounted, real):
    relaxed = tuple(rational(v) for v in relaxed_values)
    accounted, real = rational(accounted), rational(real)
    if not relaxed or type(allocation) is not int or not 0 <= allocation < len(relaxed):
        return False
    return relaxed[allocation] == accounted and min(relaxed) <= accounted <= real


def declaration_status(declaration):
    if type(declaration) is not dict or set(declaration) != set(FIELDS):
        raise ContractError("complete registered declaration schema required")
    if any(type(value) is not bool for value in declaration.values()):
        raise ContractError("declaration fields must be Boolean")
    return {field: "DECLARED_UNVERIFIED" if declaration[field] else "NOT_DECLARED" for field in FIELDS}


def bounded_halt(program, steps):
    """Execute finite countdown/loop controls; not a general halting oracle."""
    kind, counter = program
    if kind not in ("countdown", "loop") or type(counter) is not int or counter < 0:
        raise ContractError("unknown finite control program")
    if type(steps) is not int or steps < 0:
        raise ContractError("nonnegative step count required")
    for _ in range(steps):
        if kind == "countdown" and counter > 0:
            counter -= 1
    return kind == "countdown" and counter == 0


def finite_row_selector(rows):
    rows = tuple(tuple(row) for row in rows)
    if not rows or not rows[0] or any(len(row) != len(rows[0]) for row in rows):
        raise ContractError("nonempty rectangular response table required")
    return tuple(next(j for j, other in enumerate(rows) if other == row) for row in rows)


def run():
    epsilons = tuple(F(a, b) for a in range(1, 9) for b in range(1, 33))
    for epsilon in epsilons:
        n, value = epsilon_witness(epsilon)
        require(1 < value <= 1+epsilon, "constructive epsilon-optimum failed")
        require(n == 1 or tail_cost(n-1) > 1+epsilon, "witness index is not minimal")
    require(tail_cost(2) < 2, "nonattaining family lost its finite-margin competitor witness")
    require(all(tail_cost(n) > 1 for n in range(1, 257)), "tail reached unattained infimum")
    for x in (F(j, 8) for j in range(-64, 65)):
        require(x*x >= 0 and (x*x == 0) == (x == 0), "noncompact attained minimum control failed")
    require(not finite_enclosure((2, 3), 1, 2, 0, 0), "attainment alone licensed relaxation tightness")
    require(finite_enclosure((2, 3), 2, 2, 0, 0), "matching finite certificates rejected")
    transport = [accounting_certificate((F(5, 6),), 0, F(5, 6), F(4, 3)),
                 accounting_certificate((F(4, 3),), 0, F(4, 3), F(5, 6)),
                 accounting_certificate((F(4, 3),), 0, F(5, 6), 1)]
    require(transport == [True, False, False], "accounting direction or membership reversed")
    for n in range(1, 65):
        lower, upper, point = grid_enclosure(n)
        require(lower <= 0 <= upper and upper-lower <= F(1, 2*n)
                and abs(point-F(1, 3)) == upper, "grid certificate failed")
    for depth in range(1, 33):
        a = [bounded_halt(("loop", 0), t) for t in range(depth+1)]
        b = [bounded_halt(("countdown", depth+1), t) for t in range(depth+1)]
        require(a == b and bounded_halt(("countdown", depth+1), depth+1), "late-halting prefix control failed")
    declarations = 0
    for bits in product((False, True), repeat=len(FIELDS)):
        statuses = declaration_status(dict(zip(FIELDS, bits)))
        require(set(statuses.values()) <= {"DECLARED_UNVERIFIED", "NOT_DECLARED"}, "declaration promoted itself")
        declarations += 1
    selectors = 0
    for values in product((0, 1), repeat=6):
        rows = (values[:2], values[2:4], values[4:])
        chosen = finite_row_selector(rows)
        require(all(rows[chosen[i]] == rows[i] and chosen[chosen[i]] == chosen[i] for i in range(3)), "selector not a representative")
        require(all((chosen[i] == chosen[j]) == (rows[i] == rows[j]) for i in range(3) for j in range(3)), "selector merges distinct rows")
        selectors += 1
    return {"schema": "continuous-lift-boundary-v2", "all_checks_green": True,
            "terminal": "GRAND_GMI_CONTINUOUS_LIFT_SCOPE_REPAIR_GREEN_AT_FINITE_SCOPE",
            "epsilon_witness_cases": len(epsilons), "noncompact_attained_minimum": {"point": "0", "value": "0"},
            "nonattaining_finite_margin_witness": {"A_cost": "3/2", "B_lower": "2"},
            "attainment_without_matching_lower_upper_does_not_certify_tightness": True,
            "accounting_undercharge_overcharge_nonmembership": transport,
            "verified_lipschitz_grid_enclosures": 64, "late_halting_prefix_controls": 32,
            "declaration_schemas_never_license_results": declarations, "finite_selector_tables": selectors,
            "infinite_computability_and_nonselector_claims": "analytic proofs, not finite empirical tests",
            "historical_receipt_preserved": "GRAND_GMI_CONTINUOUS_LIFT_BOUNDARY_RECEIPT_V1.json",
            "physical_continuum_measured": False}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
