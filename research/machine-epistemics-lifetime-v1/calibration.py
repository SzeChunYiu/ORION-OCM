"""Exact synthetic calibration for ORION-OCM issue #50 (D3/D6).

These finite worlds validate meters/falsifiers. They are DEVELOPMENT_CALIBRATION_ONLY
and cannot establish real-world OCM superiority.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Iterable

from ocm.evaluation.lifetime_metrics import (
    AcquisitionMeasure, CheckStatus, ComparatorManifest, InformationVector,
    ResourceVector, RevisionMeasure, StateMeasure, TouchMeasure,
)

SEED = "ME-LIFETIME-CALIBRATION-V1-20260905"
SCALES = (100, 300, 1000, 3000)
RELEVANT_K = 5


def acquisition_calibration() -> dict:
    tasks = [
        ("T1", ("inspect", "localize", "repair-a", "verify-a")),
        ("T2", ("inspect", "localize", "repair-b", "verify-b")),
        ("T3", ("inspect", "localize", "repair-c", "verify-c")),
        ("T4", ("inspect", "localize", "repair-d", "verify-d")),
    ]

    def arm(persistent: bool) -> list[dict]:
        library: set[str] = set()
        out = []
        for task_id, needed in tasks:
            missing = [m for m in needed if m not in library]
            reused = [m for m in needed if m in library]
            measure = AcquisitionMeasure(
                task_id, "all-required-methods-available", True,
                InformationVector(examples=len(missing)),
                ResourceVector(work_units=len(missing), notes=("one toy work unit per newly acquired method",)),
                tuple(f"method:{m}" for m in missing),
                tuple(f"method:{m}" for m in reused),
                tuple(f"exec:{task_id}:{m}" for m in reused),
            )
            out.append({
                "task_id": task_id,
                "prior_library_size": len(library),
                "acquisition_examples": measure.information.examples,
                "acquisition_work_units": measure.resources.work_units,
                "reused": reused,
            })
            if persistent:
                library.update(needed)
        return out

    ocm, skill_parent, reset = arm(True), arm(True), arm(False)
    return {
        "figure": "A/E", "ocm": ocm, "skill_library_parent": skill_parent, "reset_parent": reset,
        "signature_present": [x["acquisition_work_units"] for x in ocm] == [4, 2, 2, 2],
        "isolated_terminal": "PARENT_SUFFICIENT",
        "reason": "an equally informed persistent skill-library parent has the same amortized acquisition curve",
    }


def sparse_scaling_calibration() -> dict:
    rows = []
    for n in SCALES:
        state = StateMeasure({"persistent_objects": n}, object_grammar="SyntheticIdentity.v1")
        relevant = tuple(f"obj:{i}" for i in range(RELEVANT_K))
        sparse = TouchMeasure(relevant, {"persistent_objects": relevant})
        global_scan = TouchMeasure(tuple(f"obj:{i}" for i in range(n)), global_scan_items=n)
        index_steps = math.ceil(math.log2(n))
        indexed = TouchMeasure(relevant, {"persistent_objects": relevant}, index_entries_touched=index_steps)
        rows.append({
            "N": n,
            "oracle_sparse_k": sparse.k, "oracle_sparse_k_over_N": sparse.k_over_n(state), "oracle_sparse_work_units": sparse.k,
            "indexed_parent_k": indexed.k, "indexed_parent_index_entries": index_steps, "indexed_parent_work_units": indexed.k + index_steps,
            "global_scan_k": global_scan.k, "global_scan_k_over_N": global_scan.k_over_n(state), "global_scan_work_units": n,
        })
    return {
        "figure": "B", "rows": rows,
        "meter_checks": {"k_is_actual_identity_touch_not_return_top_k": True, "index_probe_work_reported_separately": True, "global_scan_cannot_hide_behind_sparse_result": True},
        "isolated_terminal": "PARENT_SUFFICIENT",
        "reason": "an indexed retrieval parent also avoids full-state query scans; maintenance/storage must be counted",
    }


class SupportWorld:
    def __init__(self, n_unrelated: int = 1000):
        self.labels = {
            "method:a": (frozenset({"support:s0"}),),
            "method:b": (frozenset({"support:s0"}),),
            "composition:c": (frozenset({"support:s0"}),),
            "alternate:d": (frozenset({"support:s0"}), frozenset({"support:s_alt"})),
        }
        for i in range(n_unrelated):
            self.labels[f"unrelated:{i}"] = (frozenset({f"support:u{i}"}),)

    @staticmethod
    def live(labels, revoked: frozenset[str]) -> bool:
        return any(label.isdisjoint(revoked) for label in labels)

    def changed_by(self, revoked: Iterable[str]) -> tuple[str, ...]:
        rv = frozenset(revoked)
        return tuple(sorted(obj for obj, labels in self.labels.items() if self.live(labels, frozenset()) != self.live(labels, rv)))


def revision_calibration() -> dict:
    world = SupportWorld()
    expected = world.changed_by(("support:s0",))
    assert expected == ("composition:c", "method:a", "method:b")
    all_ids = tuple(sorted(world.labels))
    unrelated = tuple(x for x in all_ids if x.startswith("unrelated:"))
    state = StateMeasure({"competence_objects": len(all_ids)}, object_grammar="SyntheticSupportLabel.v1")
    exact = RevisionMeasure(
        "revoke:s0:exact", ("support:s0",), expected, expected, tuple(sorted((*expected, "alternate:d"))), unrelated, (), (), (), expected, expected,
        ResourceVector(work_units=4, notes=("three invalidations plus one alternate-support check",)),
    )
    under = RevisionMeasure("revoke:s0:under", ("support:s0",), expected, expected[:-1], expected[:-1], unrelated, (), (expected[-1],), ())
    over_obs = tuple(sorted((*expected, "unrelated:0")))
    over = RevisionMeasure("revoke:s0:over", ("support:s0",), expected, over_obs, over_obs, unrelated, ("unrelated:0",), (), ("unrelated:0",))
    return {
        "figure": "C/F", "N": state.logical_n, "expected_changed": list(expected), "alternate_support_survives": "alternate:d" not in expected,
        "exact": {"changed_fraction": exact.affected_fraction(state), "touch_fraction": len(exact.touched_ids) / state.logical_n, "precision": exact.dependency_precision, "recall": exact.dependency_recall, "unrelated_retention": exact.unrelated_retention, "exact_revocation": exact.exact_revocation, "exact_restoration": exact.exact_restoration},
        "under_revoke_hostile": {"caught": not under.exact_revocation, "precision": under.dependency_precision, "recall": under.dependency_recall, "stale_survivors": list(under.stale_survivor_ids)},
        "over_revoke_hostile": {"caught": not over.exact_revocation, "precision": over.dependency_precision, "recall": over.dependency_recall, "collateral": list(over.collateral_invalidated_ids)},
        "isolated_terminal": "PARENT_SUFFICIENT",
        "reason": "exact truth/reason-maintenance parents can implement the same finite locality/revocation behavior",
    }


def cannot_check_calibration() -> dict:
    touch = TouchMeasure((), status=CheckStatus.CANNOT_CHECK, cannot_check_reason="backend may perform an uninstrumented global scan", global_scan_items=3000)
    return {"case": "uninstrumented backend", "status": touch.status.value, "reason": touch.cannot_check_reason, "global_scan_items_observed_outside_k": touch.global_scan_items, "required_behavior": "do not report k/N as measured"}


def comparator_calibration() -> dict:
    common = dict(same_information=True, same_tools=True, same_verifiers=True, full_resource_accounting=True)
    simple = ComparatorManifest("current-simple-matched-parent", True, False, False, False, False, False, **common)
    composite = ComparatorManifest("registered-composite-parent", True, True, True, True, True, True, **common)
    reqs = {
        "H1_amortized_acquisition": ("persistent_memory", "post_deployment_adaptation", "reusable_skill_library"),
        "H2_sparse_relevant_computation": ("persistent_memory", "retrieval_index"),
        "H3_H4_local_exact_revision": ("persistent_memory", "dependency_truth_maintenance", "exact_revocation"),
        "H5_lifetime_economics": ("persistent_memory", "retrieval_index", "post_deployment_adaptation", "reusable_skill_library"),
    }
    out = {}
    for h, needs in reqs.items():
        ss, sm = simple.match_for(needs); cs, cm = composite.match_for(needs)
        out[h] = {"current_simple": {"status": ss.value, "missing": list(sm)}, "composite": {"status": cs.value, "missing": list(cm)}}
    return out


def run() -> dict:
    return {
        "receipt": "ME_SYNTHETIC_CALIBRATION_V1", "seed": SEED,
        "study_role": "DEVELOPMENT_CALIBRATION_ONLY", "protected_claim_authority": False,
        "expert_disposition": {
            "machine_epistemics_theorist": "Each isolated signature has strong parent mechanisms; test the joint governed lifecycle.",
            "systems_researcher": "Counters distinguish actual state touches, index work and global scans; current kernels require instrumentation before H2 is measurable.",
            "learning_researcher": "Amortized acquisition is measurable but matched skill-library/adaptation parents are mandatory.",
            "skeptical_reviewer": "Synthetic wins cannot support the thesis; fresh protected N3/N5-era lifetimes and strongest composite parents remain required."
        },
        "figure_A_E_acquisition": acquisition_calibration(),
        "figure_B_sparse_scaling": sparse_scaling_calibration(),
        "figure_C_F_revision": revision_calibration(),
        "figure_D_lifetime_economics": {"status": "CANNOT_CHECK_REAL_LIFETIME_ECONOMICS_FROM_SYNTHETIC_WORK_UNITS", "reason": "no valid cross-architecture conversion from toy work units to compute/storage/verification/IO economics has been frozen"},
        "cannot_check_hostile": cannot_check_calibration(), "comparator_contract": comparator_calibration(),
        "pilot_terminal": "PARTIAL_SIGNATURE_ONLY_SYNTHETIC_METERS_CALIBRATED",
        "confirmatory_terminal": "CANNOT_CHECK_N3_N5_LOCKED_AND_FRESH_MATCHED_LIFETIMES_NOT_RUN",
    }


def main() -> None:
    p = argparse.ArgumentParser(); p.add_argument("--out", type=Path, default=Path(__file__).with_name("ME_SYNTHETIC_CALIBRATION_V1.json")); args = p.parse_args()
    result = run(); args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"receipt": result["receipt"], "pilot_terminal": result["pilot_terminal"], "confirmatory_terminal": result["confirmatory_terminal"]}, sort_keys=True))


if __name__ == "__main__":
    main()
