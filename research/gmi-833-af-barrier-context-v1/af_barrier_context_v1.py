from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_CORE_PATH = Path(__file__).with_name("af_core_v1.py")
_SPEC = importlib.util.spec_from_file_location("gmi_af_core_v1", _CORE_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("cannot load af_core_v1.py")
_CORE = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _CORE
_SPEC.loader.exec_module(_CORE)
for _name, _value in vars(_CORE).items():
    if not _name.startswith("_"):
        globals()[_name] = _value

def run() -> dict:
    prov_compute = {"REPAIR_SECOND_ENTRY": ("ENDOGENOUS_COMPUTE",)}
    f1_a = gamma_profiles("C0", {"C0": (("REPAIR_SECOND_ENTRY", "ID"),)}, prov_compute)
    f1_b = gamma_profiles("C0", {}, prov_compute)
    require(score_string("C0") == "1/2", "F1 frozen start score drift")
    require("1" in profile_capability_set(f1_a), "F1 repair system must reach perfect capability")
    require(profile_capability_set(f1_b) == ["1/2"], "F1 frozen system must remain at one half")

    all_edges = tuple((f"RESET_THEN_SET_{p}", p) for p in sorted(POLICIES))
    action_prov = {action: ("ENDOGENOUS_COMPUTE",) for action, _ in all_edges}
    f2_id = gamma_profiles("ID", {"ID": all_edges}, action_prov)
    f2_not = gamma_profiles("NOT", {"NOT": all_edges}, action_prov)
    terminal_id = sorted(p["machine"] for p in f2_id)
    terminal_not = sorted(p["machine"] for p in f2_not)
    require(terminal_id == terminal_not == sorted(POLICIES), "F2 terminal envelopes must match")
    require(score_string("ID") != score_string("NOT"), "F2 current capabilities must differ")

    possibility = sorted(POLICIES)
    frozen_reach = sorted(p["machine"] for p in f1_b)
    require("NOT" in possibility and "NOT" not in frozen_reach, "possibility/reachability hostile failed")

    f3_before_accuracy = "1/2"
    f3_after_accuracy = "1"
    f3_initial_target_information_bits = 1
    f3_final_target_information_bits = 1
    f3_terminal = classify_information_case(
        target_correlated_import=False,
        initial_target_information=True,
        random_novelty=False,
        capability_gain=True,
        consumed_provenance=("INITIAL_OR_INHERITED_ORGANIZATION", "ENDOGENOUS_COMPUTE"),
    )
    require(f3_terminal == "COMPUTATIONAL_UNFOLDING_WITHOUT_EXTERNAL_DATA", "F3 terminal mismatch")

    independent_joint = {(theta, rnd): 0.25 for theta in (0, 1) for rnd in (0, 1)}
    random_marginal = {0: 0.5, 1: 0.5}
    f4_mi = mutual_information_bits(independent_joint)
    f4_entropy = entropy_bits(random_marginal)
    f4_accuracy = sum(p for (theta, rnd), p in independent_joint.items() if theta == rnd)
    require(f4_mi == 0.0 and f4_entropy == 1.0 and f4_accuracy == 0.5, "F4 independence fixture drift")
    f4_terminal = classify_information_case(
        target_correlated_import=False,
        initial_target_information=False,
        random_novelty=True,
        capability_gain=False,
        consumed_provenance=("STOCHASTIC_VARIATION",),
    )

    oracle_joint = {(theta, theta): 0.5 for theta in (0, 1)}
    f5_mi = mutual_information_bits(oracle_joint)
    f5_terminal = classify_information_case(
        target_correlated_import=True,
        initial_target_information=False,
        random_novelty=False,
        capability_gain=True,
        consumed_provenance=("ORACLE_ADVICE_OR_TOOL",),
    )
    require(f5_mi == 1.0 and f5_terminal == "IMPORTED_ORACLE_OR_ADVICE_POWER", "F5 oracle fixture drift")

    f5b_terminal = classify_information_case(
        target_correlated_import=True,
        initial_target_information=True,
        random_novelty=False,
        capability_gain=True,
        consumed_provenance=("INITIAL_OR_INHERITED_ORGANIZATION",),
    )
    require(f5b_terminal == "IMPORTED_INFORMATION_OR_ADVICE", "F5b nonuniform-advice classification drift")

    base = {"A": {"benefit": 10, "cost": 2}}
    optional = {**base, "B": {"benefit": 11, "cost": 4}}
    base_best = max(v["benefit"] - v["cost"] for v in base.values())
    optional_best = max(v["benefit"] - v["cost"] for v in optional.values())
    mandatory_overhead = 12
    mandatory_best = max(v["benefit"] - v["cost"] - mandatory_overhead for v in optional.values())
    require(base_best == 8 and optional_best == 8, "F6 optional monotonicity fixture drift")
    require(mandatory_best == -4 and mandatory_best < base_best, "F6 mandatory-overhead reversal must fire")

    transitions = make_transition_records()
    for tr in transitions:
        validate_barrier_transition(tr)

    hostile = dict(transitions[1])
    hostile.update(
        terminal="BROKE_TURING",
        claims_literal_contradiction=True,
        contradiction_verified=True,
        transition_classes=["LITERAL_CONTRADICTION"],
    )
    hostile_rejected = False
    try:
        validate_barrier_transition(hostile)
    except ValueError:
        hostile_rejected = True
    require(hostile_rejected, "BROKE_* premise-change hostile was not rejected")

    result = {
        "status": "GREEN",
        "af0": {
            "parent_pin_count": len(EXPECTED_PARENT_PINS),
            "parent_ownership_rule": "IMPORT_NOT_RENAME_OR_SUPERSEDE",
            "barrier_break_rule": "BROKE_* only with all premises and contracts retained plus verified contradiction",
        },
        "af1": {
            "gamma_object": "Gamma_{M0,Delta}^S(Pi,R,H,Q,V)",
            "profile_fields": ["capability", "resources", "provenance", "machine", "history"],
            "provenance_tags": list(PROVENANCE_TAGS),
            "f1_same_current_score": "1/2",
            "f1_system_a_capability_set": profile_capability_set(f1_a),
            "f1_system_b_capability_set": profile_capability_set(f1_b),
            "f2_initial_scores": {"ID": score_string("ID"), "NOT": score_string("NOT")},
            "f2_common_postdevelopment_machine_set": terminal_id,
            "possibility_set": possibility,
            "frozen_reachable_set": frozen_reach,
            "possibility_not_reachability_witness": "NOT",
        },
        "af2": {
            "gamma_null_warning": "NO_EXTERNAL_DATA != NOTHING",
            "null_condition_hierarchy": [
                {
                    "id": row["id"],
                    "forbidden_channels": list(row["forbidden_channels"]),
                    "reading": row["reading"],
                }
                for row in NULL_CONDITION_HIERARCHY
            ],
            "af_t01": {
                "finite_joint_mutual_information_bits": f4_mi,
                "reading": "Theta independent of (M0,W); deterministic post-processing does not create target mutual information",
                "ownership": "PARENT_SPECIALIZATION_DATA_PROCESSING_AND_INDEPENDENCE",
            },
            "compute_unfolding": {
                "accuracy_before": f3_before_accuracy,
                "accuracy_after": f3_after_accuracy,
                "target_information_bits_before": f3_initial_target_information_bits,
                "target_information_bits_after": f3_final_target_information_bits,
                "terminal": f3_terminal,
            },
            "random_novelty": {
                "output_entropy_bits": f4_entropy,
                "target_mutual_information_bits": f4_mi,
                "expected_target_accuracy": "1/2",
                "terminal": f4_terminal,
            },
            "oracle_advice": {
                "target_mutual_information_bits": f5_mi,
                "target_accuracy": "1",
                "terminal": f5_terminal,
                "required_provenance": "ORACLE_ADVICE_OR_TOOL",
            },
            "nonuniform_initial_advice": {
                "example": "target-correlated arbitrary-real/advice content supplied in initial organization",
                "terminal": f5b_terminal,
                "required_provenance": "INITIAL_OR_INHERITED_ORGANIZATION",
                "reading": "information content / precision is imported and must be charged by the downstream physical/resource contract",
            },
            "terminals": [
                "NO_TARGET_INFORMATION_ACQUIRED",
                "COMPUTATIONAL_UNFOLDING_WITHOUT_EXTERNAL_DATA",
                "RANDOM_NOVELTY_WITHOUT_TARGET_ALIGNMENT",
                "IMPORTED_ORACLE_OR_ADVICE_POWER",
                "IMPORTED_INFORMATION_OR_ADVICE",
                "UNEXERCISED_CAPABILITY",
            ],
        },
        "af3": {
            "context": "chi=(S,Pi,Q,R,H,eps,delta,V)",
            "statuses": list(BARRIER_STATUSES),
            "af_t02_optional_extension": {"base_best_net": base_best, "optional_extension_best_net": optional_best},
            "mandatory_overhead_hostile": {"overhead": mandatory_overhead, "best_net": mandatory_best, "reversal": True},
            "transition_records": transitions,
            "broke_changed_premise_hostile_rejected": hostile_rejected,
            "solved_forever_allowed": False,
        },
        "forbidden_promotions": list(FORBIDDEN_TERMINALS),
        "claim_ceiling": "GMI_AF0_AF3_DEVELOPMENTAL_RESPONSE_PROVENANCE_AND_BARRIER_CONTEXT_FORMALIZED_AT_REGISTERED_FINITE_SCOPE",
    }
    return result


def write_result(path: Path) -> dict:
    result = run()
    path.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE / "RESULT_V1.json")
    parser.add_argument("--parent-ledger", type=Path, default=HERE / "GMI_BARRIER_PARENT_LEDGER_V1.json")
    parser.add_argument("--skip-parent-ledger", action="store_true")
    args = parser.parse_args()
    if not args.skip_parent_ledger:
        validate_parent_ledger(args.parent_ledger)
    result = write_result(args.output)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
