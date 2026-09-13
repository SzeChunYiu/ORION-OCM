"""Finite complete search over elimination orders, with charged search work."""

from itertools import permutations

from factor_compile import eliminate


def search_orders(sizes, factors, algebra):
    best_key = None
    best = None
    ties = []
    profiles = []
    totals = dict(candidates=0, order_coordinates=0, score_comparisons=0,
                  scalar_work=0, scope_tests=0, generated_entries=0,
                  scope_coordinate_visits=0, index_coordinates=0,
                  assignment_coordinate_writes=0, input_value_checks=0,
                  input_scope_checks=0,
                  generated_bits=0, arithmetic_result_bits=0,
                  peak_candidate_table_entries=0, peak_candidate_table_bits=0)
    reference = None
    have_reference = False
    for order in permutations(range(len(sizes))):
        result = eliminate(sizes, factors, algebra, order)
        profile = result["profile"]
        if have_reference and result["value"] != reference:
            raise AssertionError("orders disagree on protected scalar value")
        reference, have_reference = result["value"], True
        key = (profile["work"], profile["peak_table_entries"])
        totals["candidates"] += 1
        totals["order_coordinates"] += len(order)
        totals["score_comparisons"] += int(best_key is not None)
        totals["scalar_work"] += profile["work"]
        for field in ("scope_tests", "generated_entries", "generated_bits",
                      "arithmetic_result_bits", "scope_coordinate_visits",
                      "index_coordinates", "assignment_coordinate_writes",
                      "input_value_checks", "input_scope_checks"):
            totals[field] += profile[field]
        for field in ("entries", "bits"):
            name = "peak_candidate_table_" + field
            totals[name] = max(totals[name], profile["peak_table_" + field])
        profiles.append(dict(order=list(order), work=profile["work"],
                             peak_table_entries=profile["peak_table_entries"],
                             width=profile["width"]))
        if best_key is None or key < best_key:
            best_key, best, ties = key, result, [order]
        elif key == best_key:
            ties.append(order)
    # Permutations arrive lexicographically: the first optimum is canonical.
    totals["certificate_order_coordinates"] = len(sizes) * len(profiles)
    totals["certificate_profile_scalars"] = 3 * len(profiles)
    totals["tie_order_coordinates"] = len(sizes) * len(ties)
    return dict(best=best, ties=ties, candidates=profiles, search=totals)
