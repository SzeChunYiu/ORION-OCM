from __future__ import annotations

from fractions import Fraction as F
from itertools import product
import json

FREEZE_COMMIT = "a050f592b3a2b9eb20b12bdfc7670d42bb22ae39"
CLAIM = "USEFUL_DESCENDANT_EVOLVABILITY_PREDICTION_VALIDATED_AT_REGISTERED_FINITE_SCOPE"
ZERO_TERMINAL = "UNREACHABLE_ZERO_USEFUL_MASS"
CURRENT_OBJECT = (0, 0, 0, 0, 0, 0)
SPACE = tuple(product((0, 1), repeat=6))
KERNELS = {
    "RESET": (F(1,2),) * 6,
    "CONTINUED": (F(3,4), F(3,4), F(1,2), F(1,2), F(1,2), F(1,2)),
    "SHUFFLED_HISTORY": (F(1,2), F(1,2), F(1,2), F(1,2), F(3,4), F(3,4)),
}
CONJUNCTIONS = {
    "H0": {0: 1},
    "H1": {1: 1},
    "U_AND": {0: 1, 1: 1},
    "U_ANTI": {0: 0, 1: 0},
    "U_45": {4: 1, 5: 1},
}
EXPECTED = {
    "U_AND": {"RESET": F(1,4), "CONTINUED": F(9,16), "SHUFFLED_HISTORY": F(1,4)},
    "U_ANTI": {"RESET": F(1,4), "CONTINUED": F(1,16), "SHUFFLED_HISTORY": F(1,4)},
    "U_45": {"RESET": F(1,4), "CONTINUED": F(1,4), "SHUFFLED_HISTORY": F(9,16)},
}


def frac(v: F) -> str:
    return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"


def point_mass(z, ps):
    if len(z) != 6 or len(ps) != 6:
        raise ValueError("registered vectors must have length six")
    mass = F(1)
    for bit, p in zip(z, ps):
        if bit not in (0, 1) or not (F(0) <= p <= F(1)):
            raise ValueError("invalid Bernoulli kernel")
        mass *= p if bit else 1 - p
    return mass


def distribution(ps):
    dist = tuple((z, point_mass(z, ps)) for z in SPACE)
    if sum((m for _, m in dist), F(0)) != 1:
        raise RuntimeError("kernel does not normalize")
    return dist


def satisfies(z, conjunction):
    return all(z[i] == bit for i, bit in conjunction.items())


def useful_mass_enum(ps, conjunction):
    return sum((m for z, m in distribution(ps) if satisfies(z, conjunction)), F(0))


def useful_mass_closed(ps, conjunction):
    mass = F(1)
    for i, bit in conjunction.items():
        p = ps[i]
        mass *= p if bit else 1 - p
    return mass


def first_hit_burden(p):
    if p == 0:
        return ZERO_TERMINAL
    if p < 0 or p > 1:
        raise ValueError("success probability must lie in [0,1]")
    return F(1, 1) / p


def truth_table(conjunction):
    return tuple(satisfies(z, conjunction) for z in SPACE)


def symbolic_entropy_signature(ps):
    # Shannon entropy H(Q)=sum_i h(p_i). Exact equality here is established
    # by identical sorted Bernoulli parameter multisets, avoiding float logs.
    return tuple(sorted((p.numerator, p.denominator) for p in ps))


def sorted_mass_signature(ps):
    return tuple(sorted(m for _, m in distribution(ps)))


def build_receipt():
    if len(SPACE) != 64 or CURRENT_OBJECT not in SPACE:
        raise RuntimeError("registered state-space invariant failed")

    distributions = {name: distribution(ps) for name, ps in KERNELS.items()}
    normalization = {name: frac(sum((m for _, m in dist), F(0))) for name, dist in distributions.items()}

    history_nonidentity = {}
    for held in ("U_AND", "U_ANTI", "U_45"):
        history_nonidentity[held] = {
            history: truth_table(CONJUNCTIONS[held]) != truth_table(CONJUNCTIONS[history])
            for history in ("H0", "H1")
        }
        if not all(history_nonidentity[held].values()):
            raise RuntimeError("held utility duplicates developmental history")

    tasks = {}
    for held in ("U_AND", "U_ANTI", "U_45"):
        tasks[held] = {}
        for kernel, ps in KERNELS.items():
            enum = useful_mass_enum(ps, CONJUNCTIONS[held])
            closed = useful_mass_closed(ps, CONJUNCTIONS[held])
            if enum != closed or enum != EXPECTED[held][kernel]:
                raise RuntimeError(f"frozen useful-mass prediction failed: {held}/{kernel}")
            burden = first_hit_burden(enum)
            tasks[held][kernel] = {
                "useful_mass_enum": frac(enum),
                "useful_mass_closed_form": frac(closed),
                "expected_iid_proposals_to_first_useful": frac(burden),
            }

    frozen_winners = {
        "U_AND": ["CONTINUED", "RESET", "SHUFFLED_HISTORY"],
        "U_ANTI": ["RESET", "SHUFFLED_HISTORY", "CONTINUED"],
        "U_45": ["SHUFFLED_HISTORY", "RESET", "CONTINUED"],
    }
    # First item must be strict best. Remaining equalities are checked separately.
    if not (
        EXPECTED["U_AND"]["CONTINUED"] > EXPECTED["U_AND"]["RESET"] == EXPECTED["U_AND"]["SHUFFLED_HISTORY"]
        and EXPECTED["U_ANTI"]["CONTINUED"] < EXPECTED["U_ANTI"]["RESET"] == EXPECTED["U_ANTI"]["SHUFFLED_HISTORY"]
        and EXPECTED["U_45"]["SHUFFLED_HISTORY"] > EXPECTED["U_45"]["RESET"] == EXPECTED["U_45"]["CONTINUED"]
    ):
        raise RuntimeError("frozen winner ordering failed")

    continued_sig = symbolic_entropy_signature(KERNELS["CONTINUED"])
    shuffled_sig = symbolic_entropy_signature(KERNELS["SHUFFLED_HISTORY"])
    continued_mass = sorted_mass_signature(KERNELS["CONTINUED"])
    shuffled_mass = sorted_mass_signature(KERNELS["SHUFFLED_HISTORY"])
    remint = {
        "same_coordinate_parameter_multiset": continued_sig == shuffled_sig,
        "same_symbolic_shannon_entropy": continued_sig == shuffled_sig,
        "same_sorted_64_point_mass_multiset": continued_mass == shuffled_mass,
        "continued_parameter_signature": [[n,d] for n,d in continued_sig],
        "shuffled_parameter_signature": [[n,d] for n,d in shuffled_sig],
    }
    if not all(remint[k] for k in ("same_coordinate_parameter_multiset", "same_symbolic_shannon_entropy", "same_sorted_64_point_mass_multiset")):
        raise RuntimeError("semantic-remint concentration control failed")

    q0 = tuple((z, F(1) if z == CURRENT_OBJECT else F(0)) for z in SPACE)
    q0_mass = sum((m for z, m in q0 if satisfies(z, CONJUNCTIONS["U_AND"])), F(0))
    zero_hostile = {
        "useful_mass": frac(q0_mass),
        "first_hit_burden": first_hit_burden(q0_mass),
    }
    if zero_hostile["first_hit_burden"] != ZERO_TERMINAL:
        raise RuntimeError("zero-mass hostile failed")

    return {
        "schema": "UsefulDescendantEvolvabilityReceiptV1",
        "issue": 779,
        "parent_issue": 602,
        "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": CLAIM,
        "registered_common_state": {
            "current_object": list(CURRENT_OBJECT),
            "descendant_space_size": len(SPACE),
            "same_current_object_across_arms": True,
            "same_descendant_space_across_arms": True,
            "same_admissibility_across_arms": True,
            "same_membership_verifier_per_held_task": True,
            "one_proposal_and_one_verification_event_per_draw": True,
        },
        "kernel_parameters": {name: [frac(p) for p in ps] for name, ps in KERNELS.items()},
        "kernel_normalization": normalization,
        "developmental_history": {"H0": "z_0=1", "H1": "z_1=1"},
        "held_history_nonidentity": history_nonidentity,
        "held_tasks": tasks,
        "frozen_ordering_summary": frozen_winners,
        "semantic_remint_control": remint,
        "zero_mass_hostile": zero_hostile,
        "theorems": {
            "EV-1": "finite useful-descendant probability mass",
            "EV-2": "iid first-useful proposal count E[T]=1/Ev for Ev>0",
            "EV-3": "coordinate-remint preserves entropy and point-mass multiset",
        },
        "negative_transfer_observed": True,
        "forbidden_claims": [
            "UNIVERSAL_EVOLVABILITY_LAW",
            "OPEN_ENDED_EVOLUTION_PROVED",
            "REAL_WORLD_EVOLVABILITY_CALIBRATED",
            "CONTINUED_DEVELOPMENT_ALWAYS_BETTER",
            "COMPLETE_GMI",
        ],
    }


def main():
    print(json.dumps(build_receipt(), sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
