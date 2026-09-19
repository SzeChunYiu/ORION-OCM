#!/usr/bin/env python3
import json
import pathlib
import sys
from fractions import Fraction

ROOT = pathlib.Path(__file__).resolve().parent

# R2 permits partial context evaluators. Two histories deliberately share one
# contextual value so the checker distinguishes image semantics from history count.
VALUES = {
    "h0": (0, 0),
    "h1": (1, 2),
    "h2": (2, 5),
    "h3": (2, 3),
    "h4": (2, 3),
    "hU": None,
}
FULL = frozenset(VALUES)
BUDGET = frozenset({"h0", "h1"})
TARGET_PERFORMANCE = 2


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def attainable(histories):
    """Contextual image of finite histories on the evaluator's defined domain."""
    return frozenset(VALUES[h] for h in histories if VALUES[h] is not None)


def weakly_dominates(a, b):
    # Context orientation for this fixture: higher performance and lower cost.
    pa, ca = a
    pb, cb = b
    return pa >= pb and ca <= cb


def strictly_dominates(a, b):
    return weakly_dominates(a, b) and not weakly_dominates(b, a)


def frontier(values):
    return tuple(
        sorted(v for v in values if not any(strictly_dominates(u, v) for u in values))
    )


def capable(values, threshold):
    return any(performance >= threshold for performance, _ in values)


def resource_projection(values):
    # The second coordinate is explicitly declared as cost/resource in this fixture.
    return tuple(sorted({cost for _, cost in values}))


def performance_projection(values):
    # A deliberately different projection used only as a hostile witness.
    return tuple(sorted({performance for performance, _ in values}))


def scalar_winner(values, lam):
    scored = {v: lam * v[0] - v[1] for v in values}
    best = max(scored.values())
    return tuple(sorted(v for v, score in scored.items() if score == best))


def one_step_relief_witnesses(histories, universe, threshold):
    """One-step enabling witnesses, not unique/minimal/causal barriers."""
    out = []
    for h in sorted(universe - histories):
        if capable(attainable(histories | {h}), threshold):
            out.append(h)
    return tuple(out)


def run_hostiles(full_a, budget_a, full_frontier):
    caught = []

    # H1: treating an undefined evaluation as an attainable value is invalid.
    bad_with_undefined = frozenset(VALUES[h] for h in FULL)
    caught.append(None in bad_with_undefined and None not in full_a)

    # H2: image semantics are not history semantics; h3/h4 collapse to one value.
    evaluated_histories = tuple(sorted(h for h in FULL if VALUES[h] is not None))
    caught.append(len(evaluated_histories) != len(full_a))

    # H3: performance-only maxima are not the Pareto frontier in this context.
    max_p = max(p for p, _ in full_a)
    performance_only = tuple(sorted(v for v in full_a if v[0] == max_p))
    caught.append(performance_only != full_frontier)

    # H4: universal rather than existential capability changes the verdict.
    bad_all_capable = all(p >= TARGET_PERFORMANCE for p, _ in full_a)
    caught.append(bad_all_capable != capable(full_a, TARGET_PERFORMANCE))

    # H5: assuming the selected optimum is invariant across lambda is refuted.
    caught.append(
        scalar_winner(full_a, Fraction(1, 1))
        != scalar_winner(full_a, Fraction(3, 1))
    )

    # H6: arbitrary missing histories are not enabling witnesses; hU changes nothing.
    caught.append(
        "hU" not in one_step_relief_witnesses(BUDGET, FULL, TARGET_PERFORMANCE)
    )

    # H7: budget monotonicity requires actual set inclusion, not a numeric label.
    nonnested = frozenset({"h1", "h3"})
    caught.append(not (BUDGET <= nonnested))

    # H8: a context-family switch has a tie point; endpoint changes alone do not
    # establish a stronger physical/statistical phase-transition claim.
    caught.append(len(scalar_winner(full_a, Fraction(3, 2))) == 2)

    # H9: a resource response is not recoverable from an unlabelled coordinate
    # tuple. Declaring performance instead of cost produces a different response.
    caught.append(resource_projection(full_a) != performance_projection(full_a))

    require(all(caught), f"hostile failure vector={caught}")
    return len(caught)


def main():
    require(BUDGET <= FULL, "budget history set must be nested in full set")

    full_a = attainable(FULL)
    budget_a = attainable(BUDGET)
    require(budget_a <= full_a, "attainability image monotonicity failed")
    require(len(FULL) == 6, "history fixture drift")
    require(
        sum(VALUES[h] is not None for h in FULL) == 5,
        "defined-domain fixture drift",
    )
    require(len(full_a) == 4, "image must deduplicate equal contextual values")
    require(len(budget_a) == 2, "budget image drift")

    ff = frontier(full_a)
    fb = frontier(budget_a)
    require(ff == ((0, 0), (1, 2), (2, 3)), f"full frontier drift: {ff}")
    require(fb == ((0, 0), (1, 2)), f"budget frontier drift: {fb}")

    require(
        not capable(budget_a, 2) and capable(full_a, 2),
        "capability projection drift",
    )
    require(not capable(full_a, 3), "impossibility target drift")

    full_resources = resource_projection(full_a)
    budget_resources = resource_projection(budget_a)
    require(full_resources == (0, 2, 3, 5), f"full resource response drift: {full_resources}")
    require(budget_resources == (0, 2), f"budget resource response drift: {budget_resources}")

    low = scalar_winner(full_a, Fraction(1, 1))
    tie = scalar_winner(full_a, Fraction(3, 2))
    high = scalar_winner(full_a, Fraction(3, 1))
    require(low == ((0, 0),), f"low-lambda winner drift: {low}")
    require(tie == ((0, 0), (2, 3)), f"switch-point tie drift: {tie}")
    require(high == ((2, 3),), f"high-lambda winner drift: {high}")

    relief = one_step_relief_witnesses(BUDGET, FULL, TARGET_PERFORMANCE)
    require(
        relief == ("h2", "h3", "h4"),
        f"one-step relief witness drift: {relief}",
    )

    hostiles = run_hostiles(full_a, budget_a, ff)

    r = json.loads((ROOT / "RESULT_V1.json").read_text())
    expected = {
        "histories": len(FULL),
        "defined_histories": 5,
        "full_attainable_values": len(full_a),
        "budget_attainable_values": len(budget_a),
        "full_frontier_count": len(ff),
        "budget_frontier_count": len(fb),
        "full_resource_levels": len(full_resources),
        "budget_resource_levels": len(budget_resources),
        "barrier_relief_witnesses": len(relief),
        "hostiles_caught": hostiles,
    }
    for key, value in expected.items():
        require(
            r.get(key) == value,
            f"RESULT drift for {key}: {r.get(key)!r} != {value!r}",
        )
    require(
        r.get("selection_switch_lambda") == "3/2",
        "selection switch threshold drift",
    )
    require(
        r.get("history_scope") == "FINITE_ADMISSIBLE_HISTORIES",
        "finite-history scope must be explicit",
    )

    payload = {
        "status": "GREEN",
        "full_frontier": [list(v) for v in ff],
        "budget_frontier": [list(v) for v in fb],
        "full_resources": list(full_resources),
        "budget_resources": list(budget_resources),
        "phase_low": [list(v) for v in low],
        "phase_tie": [list(v) for v in tie],
        "phase_high": [list(v) for v in high],
        "relief_witnesses": list(relief),
        "hostiles_caught": hostiles,
    }
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("R3_RED:" + repr(exc), file=sys.stderr)
        sys.exit(1)
