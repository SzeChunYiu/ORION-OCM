"""Cheap exact G6 study: unlabeled diagnosis on bound in-repo incidents.

Does not invent root-cause labels. Does not execute donor probes, AutoML, ATMS
comparators, or self-evolution generations. Missing raw traces remain UNKNOWN.
"""
from __future__ import annotations

import hashlib
import json
import re
import statistics
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
HEAD = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
LADDER_COMMIT = "4f40e9f534eb4a16f254d9607291115b6b6ec44f"
F1_COMMIT = "3430919fd7614589e4fcfb9756dfaffb6ef1b3b4"
SE_COMMIT = "d793f3f8403fc2e2b74a9aeef16ccdb0aa5b88c0"
FACTS_SHA256 = "37c41f6e13a44a628617651550a47f56f04341e661a8d682f8f0b5d02d891f19"

sys.path.insert(0, str(ROOT / "src"))
from ocm.selfmodel import diagnose as DG
from ocm.selfmodel import model as SM
from ocm.selfmodel import replay as RP
from ocm.kso.revocation import impact_cone


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_show(commit: str, path: str) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{commit}:{path}"], cwd=ROOT, stderr=subprocess.DEVNULL,
    )


def git_blob(commit: str, path: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"{commit}:{path}"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL,
    ).strip()


def bind(commit: str, path: str) -> dict:
    raw = git_show(commit, path)
    return {
        "commit": commit,
        "path": path,
        "blob": git_blob(commit, path),
        "sha256": sha256_bytes(raw),
        "bytes": len(raw),
        "present_in_head_tree": _present_in_head(path, raw),
    }


def _present_in_head(path: str, raw: bytes) -> bool:
    try:
        head = git_show(HEAD, path)
    except subprocess.CalledProcessError:
        return False
    return head == raw


def unlabeled_failure(failure_id: str, task_id: str, environment: str, observed: str) -> SM.FailureRecord:
    return SM.FailureRecord(
        failure_id=failure_id,
        task_id=task_id,
        environment=environment,
        observed=observed,
        expected="no responsibility label supplied",
        trace_ids=(),
        candidate_layers=tuple(SM.Layer),
        ablations=(),
        resource_state={"raw_trace_status": "CANNOT_CHECK_RAW_TRACE_MISSING"},
        uncertainty="UNKNOWN",
        severity="UNASSESSED",
        frequency=1,
        scope="g6-evolvability-v1",
    )


def diagnosis_record(d: DG.Diagnosis) -> dict:
    return {
        "weights": dict(d.weights),
        "unknown": list(d.unknown),
        "minimum_sufficient": d.minimum_sufficient,
        "architecture_alarm": d.architecture_alarm,
        "evidence": list(d.evidence),
        "all_candidate_layers_unknown": (
            d.minimum_sufficient is None
            and not d.weights
            and set(d.unknown) == {layer.value for layer in SM.Layer}
        ),
    }


def extract_f1_rows(raw: bytes) -> list[dict]:
    rows = []
    for line in raw.decode().splitlines():
        if re.fullmatch(r"\|\s*[0-3]\s*\|(?:\s*\d+\s*\|){7}", line):
            values = [int(x.strip()) for x in line.split("|")[1:-1]]
            rows.append(dict(zip(
                ("episode", "eligible_checked_branches", "tried_subcovers",
                 "valid_essential", "nonessential", "counterexample",
                 "singleton_groups_excluded", "final_pool"),
                values,
            )))
    if len(rows) != 4:
        raise ValueError("F1 table format changed")
    return rows


def facts_json_present() -> bool:
    for path in ROOT.rglob("FACTS.json"):
        if ".git" in path.parts:
            continue
        if sha256_bytes(path.read_bytes()) == FACTS_SHA256:
            return True
    return False


def kappa_proxy_from_depend_steps(data: dict) -> dict:
    """Locality ratio expected_cone/N from numeric F4 step fields only.

    This is not κ of machine self-change. Arm/step/revoked identity strings are
    not used as root-cause labels and are not returned.
    """
    ratios = []
    missing = 0
    for row in data["step_table"]:
        n = row.get("N")
        cone = row.get("expected_cone")
        if type(n) not in (int, float) or type(cone) not in (int, float) or n <= 0:
            missing += 1
            continue
        ratios.append(cone / n)
    if not ratios:
        return {"status": "CANNOT_CHECK_NO_NUMERIC_CONE"}
    return {
        "status": "PROXY_ONLY_DEPENDENCY_REVISION_RECEIPT",
        "n_steps": len(ratios),
        "dropped_nonnumeric": missing,
        "kappa_hat_expected_cone_over_N": {
            "min": min(ratios),
            "max": max(ratios),
            "mean": statistics.fmean(ratios),
            "median": statistics.median(ratios),
        },
        "not_self_change_kappa": True,
        "estimator": "expected_cone / N",
        "code_parent": "ocm.kso.revocation.impact_cone / |V_t|",
    }


def load_cycle(n: int) -> dict:
    return json.loads(git_show(SE_COMMIT, f"research/self-evolution-v1/results/run-v1/cycle-{n}.json"))


def main() -> dict:
    binds = {
        "f1": bind(F1_COMMIT, "research/math-language-learning-v1/ASSAY-ACQUISITION-DIAGNOSIS.md"),
        "f2_f3_shared": bind(LADDER_COMMIT, "research/cognitive-ladder/results/SUBSPACE_E1_V1.json"),
        "f4": bind(LADDER_COMMIT, "research/cognitive-ladder/results/DEPEND_E3_V1.json"),
        "f5": bind(LADDER_COMMIT, "research/cognitive-ladder/results/DIAGNOSIS_E2_V1.json"),
        "f6": bind(LADDER_COMMIT, "research/cognitive-ladder/results/ESCALATION_INDEPENDENT_E4_V1.json"),
        "m11_eval": bind(HEAD, "research/ocm-m11/M11_SELF_EVAL_V1.json"),
        "diagnose_py": bind(HEAD, "src/ocm/selfmodel/diagnose.py"),
        "revocation_py": bind(HEAD, "src/ocm/kso/revocation.py"),
        "replay_py": bind(HEAD, "src/ocm/selfmodel/replay.py"),
        "cycle0": bind(SE_COMMIT, "research/self-evolution-v1/results/run-v1/cycle-0.json"),
        "cycle1": bind(SE_COMMIT, "research/self-evolution-v1/results/run-v1/cycle-1.json"),
        "cycle2": bind(SE_COMMIT, "research/self-evolution-v1/results/run-v1/cycle-2.json"),
    }

    incidents = []
    f1_rows = extract_f1_rows(git_show(F1_COMMIT, binds["f1"]["path"]))
    incidents.append({
        "incident": "F1",
        "challenge_from_issue_149": "No reusable methods",
        "source": binds["f1"],
        "trace_completeness": "SUMMARY_ONLY",
        "independent_of": [],
        "raw_trace_status": "CANNOT_CHECK_RAW_TRACE_MISSING",
        "missing": [
            "Original A task/certificate/acquisition/process records absent from this Git tree",
            f"FACTS.json sha256 {FACTS_SHA256} not present in this worktree",
        ],
        "facts_json_present": facts_json_present(),
        "numeric_rows": f1_rows,
        "diagnosis": diagnosis_record(DG.diagnose(unlabeled_failure(
            "F1", "F1", "math-language-learning", "numeric acquisition funnel only",
        ))),
    })
    for label in ("F2", "F3"):
        incidents.append({
            "incident": label,
            "challenge_from_issue_149": (
                "Fixed keys become dense" if label == "F2"
                else "Index maintenance fails to amortize"
            ),
            "source": binds["f2_f3_shared"],
            "trace_completeness": "SUMMARY_ONLY",
            "independent_of": [],
            "shares_receipt_with": "F3" if label == "F2" else "F2",
            "raw_trace_status": "CANNOT_CHECK_RAW_TRACE_MISSING",
            "missing": ["Individual method/query traces and re-index search events not retained in receipt"],
            "diagnosis": diagnosis_record(DG.diagnose(unlabeled_failure(
                label, label, "cognitive-ladder-subspace", "shared subspace receipt numerics",
            ))),
        })
    f4 = json.loads(git_show(LADDER_COMMIT, binds["f4"]["path"]))
    incidents.append({
        "incident": "F4",
        "challenge_from_issue_149": "Redundant supports missed",
        "source": binds["f4"],
        "trace_completeness": "PARTIAL_REVISION_STEPS",
        "independent_of": [],
        "raw_trace_status": "CANNOT_CHECK_FULL_INTERVENTION_CALLS_ABSENT",
        "missing": ["Full acquisition evidence and individual dependency intervention calls absent"],
        "step_table_n": len(f4.get("step_table", [])),
        "table_n": len(f4.get("table", [])),
        "diagnosis": diagnosis_record(DG.diagnose(unlabeled_failure(
            "F4", "F4", "cognitive-ladder-depend", "numeric revision-step receipt",
        ))),
        "kappa_proxy": kappa_proxy_from_depend_steps(f4),
    })
    incidents.append({
        "incident": "F5",
        "challenge_from_issue_149": "Apparent diagnosis residual disappears",
        "source": binds["f5"],
        "trace_completeness": "SUMMARY_ONLY",
        "independent_of": [],
        "raw_trace_status": "CANNOT_CHECK_PER_PROBE_ABSENT",
        "missing": [
            "Per-probe observations/choices absent",
            "Augmented cached parent has no measured row in this pinned receipt",
        ],
        "diagnosis": diagnosis_record(DG.diagnose(unlabeled_failure(
            "F5", "F5", "cognitive-ladder-diagnosis", "aggregate diagnosis receipt",
        ))),
    })
    incidents.append({
        "incident": "F6",
        "challenge_from_issue_149": "Authored labels disagree with independent checking",
        "source": binds["f6"],
        "trace_completeness": "SUMMARY_ONLY",
        "independent_of": [],
        "raw_trace_status": "CANNOT_CHECK_INSTANCE_TRACES_ABSENT",
        "missing": ["Full 2000 instance traces and counterfactual repair evaluations absent"],
        "diagnosis": diagnosis_record(DG.diagnose(unlabeled_failure(
            "F6", "F6", "cognitive-ladder-escalation", "aggregate escalation receipt",
        ))),
    })

    historical = []
    for row in RP.ROWS:
        fr = unlabeled_failure(row.row, row.row, "historical-ledger", "recorded replay; no ablation channel")
        historical.append({
            "row": row.row,
            "module": row.module,
            "unlabeled_diagnosis": diagnosis_record(DG.diagnose(fr)),
            "recorded_attribution_not_used": row.attributed_layer,
        })
    replay = RP.replay_all()

    planted = []
    eval_v1 = json.loads((ROOT / "research/ocm-m11/M11_SELF_EVAL_V1.json").read_text())
    for sc in eval_v1["scenarios"]:
        planted.append({
            "scenario": sc["scenario"],
            "true_layer_supplied": sc["true_layer"],
            "usable_for_unlabeled_self_identifiability": False,
            "reason": "M11 controlled benchmark supplies ablation-channel labels; issue #149 forbids using it as blind localization evidence",
        })

    cycles = []
    for i in range(3):
        d = load_cycle(i)
        lib = d.get("registered_candidate_library") or []
        cycles.append({
            "cycle": d["cycle"],
            "generation_before": d["generation_before"],
            "generation_after": d["generation_after"],
            "terminal": d["terminal"],
            "initial_diagnosis": d.get("initial_diagnosis"),
            "post_probe_diagnosis": d.get("diagnosis"),
            "n_probes": len(d.get("probes") or []),
            "n_candidates": len(lib) if isinstance(lib, list) else None,
            "change_classes": sorted({c.get("change_class") for c in lib}) if isinstance(lib, list) else None,
            "origins": sorted({c.get("origin") for c in lib}) if isinstance(lib, list) else None,
            "origin_claim": d.get("origin_claim"),
        })

    third = (
        cycles[0]["generation_before"] == 0
        and cycles[0]["generation_after"] == 1
        and cycles[1]["generation_before"] == 1
        and cycles[1]["generation_after"] == 2
        and cycles[2]["generation_before"] == 2
        and cycles[2]["generation_after"] == 2
        and cycles[2]["terminal"] == "SELF_DIAGNOSIS_NOT_IDENTIFIABLE"
    )

    unlabeled_ok = all(inc["diagnosis"]["all_candidate_layers_unknown"] for inc in incidents)
    historical_ok = all(h["unlabeled_diagnosis"]["all_candidate_layers_unknown"] for h in historical)
    if not unlabeled_ok or not historical_ok:
        raise SystemExit("unlabeled diagnosis did not preserve UNKNOWN")
    if not third:
        raise SystemExit("pinned generation trajectory mismatch")
    if incidents[1]["source"]["sha256"] != incidents[2]["source"]["sha256"]:
        raise SystemExit("F2/F3 must share one receipt")
    if incidents[0]["facts_json_present"]:
        raise SystemExit("unexpected FACTS.json")
    if impact_cone.__name__ != "impact_cone":
        raise SystemExit("impact_cone missing")

    chi = {
        "status": "CANNOT_CHECK_NO_CALIBRATED_REPAIR_POSTERIOR",
        "theory": "chi(e) = 2^H(R|e) requires a calibrated posterior over successful repairs",
        "fallback_complete_candidate_count": {
            "n": cycles[0]["n_candidates"],
            "change_classes": cycles[0]["change_classes"],
            "origins": cycles[0]["origins"],
            "probes_evaluated_per_cycle": cycles[0]["n_probes"],
            "same_catalogue_all_cycles": all(c["n_candidates"] == cycles[0]["n_candidates"] for c in cycles),
        },
        "not_chi": True,
        "source_review_qualification": "entropy of a wrong concentrated heuristic is not search cost; see research/evolvability-source-review-v1/DECISION.md",
    }
    omega = {
        "status": "CANNOT_CHECK_NO_PER_PROBE_TRANSCRIPT",
        "theory": "Omega(eps) = H(Z)/B_id(eps) needs allowed probes, conditional I(Z;Yi|history,action), and a latent cause for scoring only",
        "missing": [
            "F5 per-probe observations/choices",
            "F1 original acquisition traces",
            "F6 instance-level counterfactual repairs",
            "registered probe policy without supplied Z labels in the proposer channel",
        ],
        "fano_example_not_remeasured": "PR150 synthetic m=30, eps=0.05 remains theory/synthetic; not an OCM incident measurement",
    }

    result = {
        "schema": "ocm.g6-evolvability-v1.result",
        "head": HEAD,
        "terminal": "CANNOT_CHECK_MISSING_RAW_TRACES_AND_NO_THIRD_EARNED_SELF_CHANGE",
        "developmental_evolvability_supported": False,
        "third_nontrivial_earned_self_change": False,
        "generation_trajectory": "g0 -> g1 -> g2 -> g2",
        "unlabeled_diagnosis_preserved_unknown": unlabeled_ok and historical_ok,
        "shared_f2_f3_receipt": True,
        "binds": binds,
        "incidents": incidents,
        "historical_unlabeled": {
            "n": len(historical),
            "all_unknown": historical_ok,
            "rows": historical,
        },
        "historical_governance_replay": replay["summary"],
        "planted_m11_s0_s7": planted,
        "self_evolution_cycles": cycles,
        "triad": {
            "kappa": {
                "operational_definition": "kappa_H(z) = |impact_cone(ks, {z})| / |V_t| from ocm.kso.revocation.impact_cone",
                "self_change_measurement": "CANNOT_CHECK_NO_SELF_MODEL_COMPONENT_GRAPH_FOR_REAL_INCIDENTS",
                "receipt_proxy": incidents[3]["kappa_proxy"],
            },
            "omega": omega,
            "chi": chi,
        },
        "intervention_effect_learning": {
            "status": "CANNOT_CHECK_NO_DISJOINT_UNLABELED_INTERVENTION_TRANSCRIPTS",
            "missing_ingredient": (
                "source-bound per-incident probe/intervention transcripts with unlabeled "
                "effects, disjoint from F2/F3's shared receipt, including recovered F1/F5/F6 traces"
            ),
        },
        "matched_parents_executed": {
            "system_identification": "NOT_RUN",
            "structured_surrogate": "NOT_RUN",
            "atms_change_impact": "NOT_RUN",
            "automl_bo": "NOT_RUN",
            "evolutionary_search": "NOT_RUN",
            "program_repair": "NOT_RUN",
            "learned_selector": "NOT_RUN",
            "human_designed_repair": "NOT_RUN",
            "finite_catalogue_identity_parent": "RECORDED_ON_SE_COMMIT_NOT_RERUN",
        },
        "claim_ceiling": "E2/L0 inventory and unlabeled-diagnosis check; no evolvability residual",
    }
    out = HERE / "RESULT.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    (HERE / "SOURCE-BINDS.json").write_text(json.dumps({"head": HEAD, "binds": binds}, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "terminal": result["terminal"],
        "unlabeled_unknown": result["unlabeled_diagnosis_preserved_unknown"],
        "third_change": result["third_nontrivial_earned_self_change"],
        "trajectory": result["generation_trajectory"],
        "result": str(out),
    }, sort_keys=True))
    return result


if __name__ == "__main__":
    main()
