from __future__ import annotations

import json
from fractions import Fraction as F
from typing import Mapping


def frac(x: F) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def build_certificate() -> Mapping[str, object]:
    atoms = tuple(range(200))
    source_failure = set(range(0, 10))
    relation1_failure = set(range(10, 12))
    relation2_failure = {12}

    failures_union = source_failure | relation1_failure | relation2_failure
    joint_good = set(atoms) - failures_union

    p_source_good = F(len(atoms) - len(source_failure), len(atoms))
    p_r1_good = F(len(atoms) - len(relation1_failure), len(atoms))
    p_r2_good = F(len(atoms) - len(relation2_failure), len(atoms))
    independent_product = p_source_good * p_r1_good * p_r2_good
    actual_joint_good = F(len(joint_good), len(atoms))
    union_bound_failure = (
        F(len(source_failure), len(atoms))
        + F(len(relation1_failure), len(atoms))
        + F(len(relation2_failure), len(atoms))
    )

    return {
        "schema": "DevelopmentalUncertaintyDependenceCertificateV1",
        "issue": 748,
        "atoms": len(atoms),
        "source_failure_probability": frac(F(1, 20)),
        "relation1_failure_probability": frac(F(1, 100)),
        "relation2_failure_probability": frac(F(1, 200)),
        "failure_sets_pairwise_disjoint": (
            not (source_failure & relation1_failure)
            and not (source_failure & relation2_failure)
            and not (relation1_failure & relation2_failure)
        ),
        "union_failure_probability": frac(F(len(failures_union), len(atoms))),
        "sum_registered_failure_budgets": frac(union_bound_failure),
        "actual_joint_good_probability": frac(actual_joint_good),
        "union_bound_good_lower_bound": frac(F(1) - union_bound_failure),
        "product_if_independent": frac(independent_product),
        "success_events_are_independent": actual_joint_good == independent_product,
        "bound_is_tight": actual_joint_good == F(1) - union_bound_failure,
        "independence_used": False,
    }


if __name__ == "__main__":
    print(json.dumps(build_certificate(), indent=2, sort_keys=True))
