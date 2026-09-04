"""KSO M4 — governed Jump calibration from an exact expressive ceiling.

Current representational family: affine Boolean functions over two bits,
f(a,b)=c0 xor c1*a xor c2*b. Target AND is outside the family. Exhausting all eight
incumbents is an exact EXPRESSIVE_CEILING witness. Two repairs are proposed:
J3 adds the feature a*b (representation transition); J5 adds AND as a primitive operator.
Both solve the target, but J3 is the minimum sufficient Jump and therefore wins.

This is a finite calibration of the existing ORION Jump contract, not novelty.
"""
from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def _load(name, path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


m3 = _load("kso_m3_learning_v1", HERE / "kso_m3_learning_v1.py")
jump = _load("orion_v2_jump_for_kso", ROOT / "src" / "orion_v2" / "jump.py")
DOMAIN = m3.DOMAIN
TARGET = m3.TARGET_AND


def affine_table(c0: int, c1: int, c2: int) -> tuple[int, ...]:
    return tuple((c0 ^ (c1 & a) ^ (c2 & b)) for a, b in DOMAIN)


AFFINE: tuple[tuple[int, ...], ...] = tuple(affine_table(*c) for c in itertools.product((0, 1), repeat=3))
assert len(set(AFFINE)) == 8


@dataclass(frozen=True)
class CeilingWitness:
    family_size: int
    exact_matches: int
    target: tuple[int, ...]
    counterexample_by_candidate: tuple[tuple[int, int], ...]


def witness_affine_ceiling(target: Sequence[int] = TARGET) -> CeilingWitness:
    t = tuple(target)
    witnesses = []
    matches = 0
    for cand in AFFINE:
        diffs = [i for i, (x, y) in enumerate(zip(cand, t, strict=True)) if x != y]
        if not diffs:
            matches += 1
            witnesses.append((-1, -1))
        else:
            witnesses.append(DOMAIN[diffs[0]])
    return CeilingWitness(8, matches, t, tuple(witnesses))


def expanded_linear_table(c0: int, c1: int, c2: int, c3: int) -> tuple[int, ...]:
    return tuple(c0 ^ (c1 & a) ^ (c2 & b) ^ (c3 & (a & b)) for a, b in DOMAIN)


def find_expanded_coeffs(target: Sequence[int]) -> tuple[int, int, int, int] | None:
    t = tuple(target)
    for c in itertools.product((0, 1), repeat=4):
        if expanded_linear_table(*c) == t:
            return c
    return None


def preservation_old_to_expanded() -> bool:
    return all(
        expanded_linear_table(c0, c1, c2, 0) == affine_table(c0, c1, c2)
        for c0 in (0, 1)
        for c1 in (0, 1)
        for c2 in (0, 1)
    )


def make_trigger():
    cw = witness_affine_ceiling()
    if cw.exact_matches != 0:
        raise RuntimeError("ceiling witness did not fire")
    return jump.JumpTrigger(
        trigger_id="kso-m4-affine-ceiling",
        kind=jump.TriggerKind.EXPRESSIVE_CEILING,
        incumbent_level=jump.JumpLevel.LOCAL_REPAIR_COMPOSITION,
        witness_ids=("affine-family-enumerated-8", "and-has-no-affine-representative"),
        lower_level_dispositions=("J0_PARAMETERS_EXHAUSTED", "J1_AFFINE_COMPOSITION_CLOSED"),
        route_censored=False,
        protected_outcome_seen=False,
    )


def proposals():
    trigger = make_trigger()
    j3 = jump.JumpProposal(
        proposal_id="kso-j3-add-conjunction-feature",
        trigger=trigger,
        level=jump.JumpLevel.REPRESENTATION_REGIME_TRANSITION,
        transformation_family="phi(a,b)=(1,a,b) -> phi'(a,b)=(1,a,b,a*b)",
        parent_ids=("polynomial-feature-lift", "algebraic-normal-form"),
        correspondence_ids=("old-feature-projection", "old-affine-coefficients-embed-with-c3=0"),
        preservation_obligation_ids=("all-8-affine-functions-unchanged",),
        predicted_contract_ids=("AND-becomes-linear-with-c3=1",),
        falsifier_ids=("any-old-affine-output-changes", "AND-not-exact-on-4-inputs"),
    )
    j5 = jump.JumpProposal(
        proposal_id="kso-j5-add-and-operator",
        trigger=trigger,
        level=jump.JumpLevel.METHOD_TOOL_INSTRUMENT_INVENTION,
        transformation_family="add primitive AND operator",
        parent_ids=("boolean-circuit-basis",),
        correspondence_ids=("old-operator-library-inclusion",),
        preservation_obligation_ids=("old-operators-byte-identical",),
        predicted_contract_ids=("AND-available-as-primitive",),
        falsifier_ids=("AND-truth-table-mismatch",),
    )
    return j3, j5


def check_j3():
    coeff = find_expanded_coeffs(TARGET)
    assert coeff == (0, 0, 0, 1)
    assert expanded_linear_table(*coeff) == TARGET
    assert preservation_old_to_expanded()
    projected = {
        expanded_linear_table(c0, c1, c2, 0)
        for c0 in (0, 1)
        for c1 in (0, 1)
        for c2 in (0, 1)
    }
    assert projected == set(AFFINE)
    return {
        "coefficients": coeff,
        "target_exact": 4,
        "old_functions_preserved": 8,
        "rollback_recovers_old_family": 8,
    }


def check_bad_jump_rejected() -> bool:
    bad = set()
    for c in itertools.product((0, 1), repeat=4):
        table = tuple(c[0] ^ (c[1] & a) ^ (c[2] & b) ^ (c[3] & (a ^ b)) for a, b in DOMAIN)
        bad.add(table)
    return TARGET not in bad


def run_m4() -> dict[str, object]:
    cw = witness_affine_ceiling()
    assert cw.exact_matches == 0 and len(cw.counterexample_by_candidate) == 8
    trig = make_trigger()
    assert trig.is_admissible
    j3, j5 = proposals()
    assert j3.is_formally_complete and j5.is_formally_complete
    a3 = jump.assess_jump(j3, lower_level_sufficient=False, donor_product_ties=False)
    a5 = jump.assess_jump(j5, lower_level_sufficient=False, donor_product_ties=False)
    assert a3 is jump.JumpAssessment.CANDIDATE_FOR_PROTECTED_EVALUATION
    assert a5 is jump.JumpAssessment.CANDIDATE_FOR_PROTECTED_EVALUATION
    minimum = jump.minimum_level((j5, j3))
    assert minimum.proposal_id == j3.proposal_id
    exact = check_j3()
    assert check_bad_jump_rejected()
    weak = jump.JumpTrigger(
        "weak",
        jump.TriggerKind.POOR_SCORE,
        jump.JumpLevel.LOCAL_REPAIR_COMPOSITION,
        ("score-low",),
        ("retry-done",),
    )
    assert not weak.is_admissible
    assert (
        jump.assess_jump(j3, lower_level_sufficient=True, donor_product_ties=False)
        is jump.JumpAssessment.NO_JUMP_NEEDED_LOWER_LEVEL_SUFFICIENT
    )
    return {
        "terminal": "M4_FINITE_GOVERNED_JUMP_GREEN",
        "ceiling": {
            "family": "affine Boolean functions",
            "family_size": cw.family_size,
            "exact_matches": cw.exact_matches,
            "counterexample_witnesses": len(cw.counterexample_by_candidate),
        },
        "trigger": {"kind": trig.kind.value, "admissible": trig.is_admissible},
        "proposals": {
            "J3": j3.proposal_id,
            "J5": j5.proposal_id,
            "minimum_sufficient": minimum.proposal_id,
        },
        "j3_exact": exact,
        "hostiles": {
            "bad_feature_rejected": True,
            "poor_score_not_a_trigger": True,
            "lower_level_sufficient_refuses_jump": True,
        },
        "authority": {
            "v1_84_opaque_world_benchmark": False,
            "novelty": False,
            "M5": False,
            "M6": False,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out")
    a = p.parse_args(argv)
    try:
        r = run_m4()
        if a.out:
            Path(a.out).write_text(json.dumps(r, indent=2, sort_keys=True) + "\n")
        print(json.dumps(r, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"terminal": "FAIL", "reason": f"{type(exc).__name__}: {exc}"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
