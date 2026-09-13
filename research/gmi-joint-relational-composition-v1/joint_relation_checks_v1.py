#!/usr/bin/env python3
"""Source-bound finite JRC checks; exact deterministic mathematics only."""
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path
import json

from joint_relation_model_v1 import Relation, fixed_bits, incidence_bound, joint_relation, minimum_cover
from joint_relation_oracle_v1 import (direct_protocol_optimum, joint_selector_optimum,
                                      selector_optimum, verify_pair_protocol)
from joint_relation_witnesses_v1 import c5, check, triangle

HERE = Path(__file__).resolve().parent
SOURCES = ("JOINT_RELATIONAL_COMPOSITION_THEOREM_V1.md", "PARENTS_AND_COSTS_V1.md",
           "joint_relation_model_v1.py", "joint_relation_oracle_v1.py",
           "joint_relation_witnesses_v1.py", "joint_relation_checks_v1.py",
           "SOURCE_PARENTS_V1.json")


def all_relations(inputs, actions):
    rows = tuple(tuple(i for i in range(actions) if mask & (1 << i))
                 for mask in range(1, 1 << actions))
    return tuple(Relation(selection, actions) for selection in product(rows, repeat=inputs))


def local_census():
    stats = dict(relations=0, adequate_selectors=0, protocol_tables_examined=0,
                 uncovered_states=0, candidate_branches=0)
    for relation in all_relations(3, 3):
        cover, work = minimum_cover(relation)
        selector = selector_optimum(relation.rows)
        tables = direct_protocol_optimum(relation.rows, relation.actions)
        check(cover["used_symbols"] == selector["width"] == tables["width"], "local full-class equivalence")
        stats["relations"] += 1
        stats["adequate_selectors"] += selector["selectors"]
        stats["protocol_tables_examined"] += tables["tables"]
        for key in work:
            stats[key] += work[key]
    return stats


def joint_census():
    stats = dict(relation_pairs=0, adequate_joint_selectors=0, executed_pairs=0,
                 uncovered_states=0, candidate_branches=0)
    for n1, n2 in product((1, 2, 3), repeat=2):
        lefts, rights = all_relations(n1, 2), all_relations(n2, 2)
        widths = {r: selector_optimum(r.rows)["width"] for r in lefts+rights}
        for left, right in product(lefts, rights):
            relation = joint_relation(left, right)
            actual, work = minimum_cover(relation)
            independent = joint_selector_optimum(left.rows, right.rows)
            size = actual["used_symbols"]
            check(size == independent["width"], "shared cover differs from all actual selectors")
            check(max(widths[left], widths[right]) <= size <= widths[left]*widths[right], "composition bounds")
            bounds = incidence_bound(left, right, widths[left], widths[right])
            check(max(bounds["row"], bounds["column"], bounds["area"]) <= size, "incidence bounds")
            decoder = tuple(divmod(a, right.actions) for a in actual["decoder"])
            checks = verify_pair_protocol(left.rows, right.rows, actual["encoder"], decoder)
            stats["relation_pairs"] += 1
            stats["adequate_joint_selectors"] += independent["selectors"]
            stats["executed_pairs"] += len(checks)
            for key in work:
                stats[key] += work[key]
    return stats


def exact_function_census():
    functions = tuple(product(range(3), repeat=3))
    count = 0
    for f, g in product(functions, repeat=2):
        relation = joint_relation(Relation(tuple((a,) for a in f), 3),
                                  Relation(tuple((b,) for b in g), 3))
        actual, _ = minimum_cover(relation)
        required = len({(a, b) for a in f for b in g})
        check(actual["used_symbols"] == required == len(set(f))*len(set(g)), "function multiplicativity")
        count += 1
    check(fixed_bits(3*5) == 4 < fixed_bits(3)+fixed_bits(5), "packing is not separately rounded addition")
    return dict(function_pairs=count, packed_fifteen_symbols=4, separate_three_five_fields=5)


def run():
    result = dict(schema="joint-relational-composition-v1", local=local_census(),
                  joint=joint_census(), exact_functions=exact_function_census(),
                  triangle=triangle(), c5=c5(),
                  source_sha256={name: sha256((HERE/name).read_bytes()).hexdigest() for name in SOURCES},
                  claim_ceiling="Exact supplied finite classical message alphabet; no physical or lifetime Pareto claim.",
                  terminal="JOINT_RELATIONAL_COMPOSITION_FINITE_GREEN")
    return json.loads(json.dumps(result))


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
