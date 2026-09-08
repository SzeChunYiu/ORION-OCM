"""Project existing native-learning / method-serving receipts onto G2.1 types.

This module does not invent causal reuse. Gaps are explicit UNKNOWN / CANNOT_CHECK.
Cited paths are repository-relative.
"""
from __future__ import annotations

from typing import Any

from .types import (
    UNKNOWN,
    AcquisitionLineage,
    CheckStatus,
    CorrectnessEvidence,
    CurrentAuthorizationState,
    FailureAttemptV1,
    FailureKind,
    G24Lifecycle,
    Liveness,
    MethodRecordV1,
    OriginCategory,
    PrimitiveAlias,
    RepresentationChangeV1,
    ResourceVector,
    ReuseEventV1,
    ScopeState,
    ScopeTransferV1,
    UsefulnessEvidence,
    Verdict,
    unknown_authorization,
    unknown_lineage,
    unknown_usefulness,
)

SOURCES = {
    "me_resource": "research/machine-epistemics-lifetime-v1/ME_LIFETIME_RECEIPT_SCHEMA_V1.json#/$defs/resource",
    "me_reuse_def": "research/machine-epistemics-lifetime-v1/ME_LIFETIME_RECEIPT_SCHEMA_V1.json x-orion-definitions.reuse_event",
    "unary_store": "research/math-language-learning-v1/unary_method_store.py",
    "unary_journal": "research/math-language-learning-v1/unary_method_journal.py",
    "unary_envelope": "research/math-language-learning-v1/unary_method_store.py ocm.unary-method.data.v1",
    "unary_packet": "research/math-language-learning-v1/unary_method_execution.py ocm.unary-method.packet.v1",
    "native_store": "research/native-method-serving-v1/native_store.py",
    "native_journal": "research/native-method-serving-v1/native_journal.py",
    "native_engine": "research/native-method-serving-v1/native_engine.py",
    "native_packet": "research/native-method-serving-v1/native_packet.py native.packet.v1",
    "native_inputs": "research/native-method-serving-v1/native_inputs.py METHODS.json",
    "liveness": "src/ocm/kso/warrant.py Liveness",
    "authority": "src/ocm/kso/types.py Authority/Scope",
    "teaching_packet": "research/ordinary-cut-source-evidence-v1/consumer-v3/teaching_packet.py",
    "clia_core": "research/ocm-prototype/results/clia-reuse-study-result-20260906/CORE.md",
    "clia_readout": "research/ocm-prototype/results/clia-reuse-study-result-20260906/READOUT.json",
    "clia_protocol": "research/ocm-prototype/results/clia-reuse-study-qualification-20260906/protocol/protocol.json",
    "stitch": "research/ocm-prototype/results/stitch-public-induction-20260906/CORE.md",
    "typed_lifecycle": "research/native-typed-lifecycle-v1/CORE.md",
    "unary_release": "research/math-language-learning-v1/release-review-records/REVIEW.json",
}

GAPS = {
    "unary_utility_is_not_usefulness": "unary envelope utility evidence is authored-selected.v1 policy, not later-task causal benefit",
    "native_applicability_is_not_usefulness": "native applicability evidence is authored-import.v1 policy, not later-task causal benefit",
    "native_methods_are_imported": "native-method-serving methods are externally acquired open methods, not episode-induced abstractions",
    "use_receipt_has_no_restart": "ocm.unary-method.use.v1 / ocm.native-method.use.v1 do not record process restart or fresh-task disjointness",
    "use_receipt_has_no_ablation": "use receipts do not record method-removal ablation",
    "teaching_packet_is_training_data": "ordinary training-trace packets are prefix/release authority, not CognitiveEpisodeV1 method objects",
    "scope_transfer_unrepresented": "no existing receipt records typed correspondence + reminted target vocabulary as ScopeTransferV1",
    "g24_not_complete": "no existing receipt satisfies the full G2.4 lifecycle as CAUSAL_METHOD_REUSE_SUPPORTED",
}


def _wall(seconds: Any) -> ResourceVector:
    try:
        value = float(seconds)
    except (TypeError, ValueError):
        return ResourceVector(notes=("UNKNOWN wall seconds",))
    if value < 0:
        raise ValueError("negative wall")
    return ResourceVector(wall_seconds=value, notes=("partial: only wall_seconds mapped from source receipt",))


def _scope(*contexts: str) -> ScopeState:
    return ScopeState(contexts=tuple(contexts) if contexts else None)


def map_unary_envelope(envelope: dict[str, Any], *, method_id: str, eligible: bool | None = None,
                       correctness_liveness: str = UNKNOWN, selection_liveness: str = UNKNOWN) -> MethodRecordV1:
    """ADAPT unary method envelope. usefulness remains UNKNOWN."""
    proof = envelope.get("proof", UNKNOWN)
    sources = envelope.get("sources_sha256", UNKNOWN)
    discovery = envelope.get("discovery", UNKNOWN)
    cert = envelope.get("schema_certificate") or {}
    accepted = cert.get("accepted")
    if accepted is True:
        verdict, status = Verdict.PASS, CheckStatus.MEASURED
        reason = None
    elif accepted is False:
        verdict, status = Verdict.FAIL, CheckStatus.MEASURED
        reason = None
    else:
        verdict, status = Verdict.UNKNOWN, CheckStatus.UNKNOWN
        reason = None
    proof_lv = Liveness(correctness_liveness) if correctness_liveness in ("LIVE", "DEAD", "UNKNOWN") else Liveness.UNKNOWN
    apply_lv = Liveness(selection_liveness) if selection_liveness in ("LIVE", "DEAD", "UNKNOWN") else Liveness.UNKNOWN
    serving = Liveness.LIVE if eligible is True else (Liveness.DEAD if eligible is False else Liveness.UNKNOWN)
    if serving is Liveness.LIVE and (proof_lv is not Liveness.LIVE or apply_lv is not Liveness.LIVE):
        serving = Liveness.UNKNOWN
    return MethodRecordV1(
        method_id=method_id,
        payload_sha256=UNKNOWN,
        method_schema_id=UNKNOWN,
        source_schema=envelope.get("schema", "ocm.unary-method.data.v1"),
        acquisition_lineage=AcquisitionLineage(
            origin_category=OriginCategory.TAUGHT_IMPORTED,
            discovery_evidence_id=str(discovery),
            source_sha256=str(sources),
            status=CheckStatus.MEASURED if discovery != UNKNOWN else CheckStatus.UNKNOWN,
        ),
        correctness=CorrectnessEvidence(
            checker_id="unary_rule_check.check_rule",
            proof_evidence_id=str(proof),
            certificate_sha256=UNKNOWN,
            verdict=verdict,
            independent_of_usefulness=True,
            status=status,
            cannot_check_reason=reason,
        ),
        usefulness=unknown_usefulness(
            status=CheckStatus.CANNOT_CHECK,
            reason=GAPS["unary_utility_is_not_usefulness"],
        ),
        authorization=CurrentAuthorizationState(
            admitted=True if envelope.get("proof") else None,
            proof_liveness=proof_lv,
            applicability_liveness=apply_lv,
            serving_liveness=serving if serving is not Liveness.LIVE else (
                Liveness.LIVE if proof_lv is Liveness.LIVE and apply_lv is Liveness.LIVE else Liveness.UNKNOWN
            ),
            warrant_ids=tuple(x for x in (str(proof),) if x != UNKNOWN),
            scope=_scope("unary-method-runtime.v1"),
            status=CheckStatus.MEASURED if eligible is not None else CheckStatus.UNKNOWN,
        ),
        notes=(f"mapped from {SOURCES['unary_envelope']}", GAPS["unary_utility_is_not_usefulness"]),
    )


def map_native_plan(plan: dict[str, Any], *, payload_sha256: str | None = None) -> MethodRecordV1:
    """ADAPT native imported method plan. usefulness remains UNKNOWN."""
    mid = str(plan.get("id") or plan.get("method_id") or UNKNOWN)
    proof = plan.get("proof", UNKNOWN)
    applies = plan.get("applicability", UNKNOWN)
    sources = plan.get("sources_sha256", UNKNOWN)
    qualification = plan.get("qualification") or {}
    cert = qualification.get("claims_sha256", UNKNOWN)
    return MethodRecordV1(
        method_id=mid,
        payload_sha256=str(payload_sha256 or plan.get("payload_sha256") or UNKNOWN),
        method_schema_id=UNKNOWN,
        source_schema="native.method-plan.v1",
        acquisition_lineage=AcquisitionLineage(
            origin_category=OriginCategory.TAUGHT_IMPORTED,
            source_sha256=str(sources),
            prior_information_ids=("authored-import.v1",),
            status=CheckStatus.MEASURED,
        ),
        correctness=CorrectnessEvidence(
            checker_id="native.replay.v1",
            proof_evidence_id=str(proof),
            certificate_sha256=str(cert),
            verdict=Verdict.PASS if cert != UNKNOWN else Verdict.UNKNOWN,
            status=CheckStatus.MEASURED if cert != UNKNOWN else CheckStatus.UNKNOWN,
        ),
        usefulness=unknown_usefulness(
            status=CheckStatus.CANNOT_CHECK,
            reason=GAPS["native_applicability_is_not_usefulness"],
        ),
        authorization=CurrentAuthorizationState(
            admitted=True,
            proof_liveness=Liveness.UNKNOWN,
            applicability_liveness=Liveness.UNKNOWN,
            serving_liveness=Liveness.UNKNOWN,
            warrant_ids=tuple(x for x in (str(proof), str(applies)) if x != UNKNOWN),
            scope=_scope("native-method-runtime.v1"),
            status=CheckStatus.UNKNOWN,
            cannot_check_reason=None,
        ),
        notes=(
            f"mapped from {SOURCES['native_store']}",
            GAPS["native_methods_are_imported"],
            GAPS["native_applicability_is_not_usefulness"],
        ),
    )


def map_use_receipt(body: dict[str, Any], *, native: bool) -> ReuseEventV1 | FailureAttemptV1:
    """ADAPT unary/native use journals. Restart, ablation, and usefulness stay UNKNOWN."""
    schema = body.get("schema", UNKNOWN)
    qid = str(body.get("qid") or UNKNOWN)
    receipt = body.get("receipt") or {}
    terminal = receipt.get("terminal")
    packet = receipt.get("packet") or {}
    if native:
        method_ids = tuple(packet.get("selected_proof_method_ids") or ())
        source = "ocm.native-method.use.v1"
        context = "native-method-runtime.v1"
    else:
        use = (packet.get("use") or {})
        mid = use.get("method_id")
        method_ids = (str(mid),) if mid else ()
        source = "ocm.unary-method.use.v1"
        context = "unary-method-runtime.v1"
    wall = receipt.get("solve_wall_s")
    resources = _wall(wall) if wall is not None else ResourceVector(notes=("UNKNOWN resources",))
    if terminal != "CHECKED" or not method_ids:
        return FailureAttemptV1(
            attempt_id=str(body.get("intent_sha256") or qid),
            method_id=method_ids[0] if method_ids else UNKNOWN,
            task_id=qid,
            scope=_scope(context),
            budget=UNKNOWN,
            environment_version=str(body.get("sources_sha256") or UNKNOWN),
            outcome=str(terminal or "USE_REFUSED"),
            feedback=str(receipt.get("backend_failure") or ""),
            failure_kind=FailureKind.AUTHORITY_REFUSAL if terminal == "CANNOT_CHECK" else FailureKind.UNKNOWN,
            resources=resources,
            acquisition_lineage=unknown_lineage(),
            correctness=CorrectnessEvidence(status=CheckStatus.UNKNOWN),
            usefulness=unknown_usefulness(status=CheckStatus.CANNOT_CHECK, reason=GAPS["use_receipt_has_no_ablation"]),
            authorization=CurrentAuthorizationState(
                serving_liveness=Liveness.DEAD if terminal == "CANNOT_CHECK" else Liveness.UNKNOWN,
                scope=_scope(context),
                status=CheckStatus.UNKNOWN,
            ),
            notes=(f"mapped from {SOURCES['native_journal' if native else 'unary_journal']}", GAPS["use_receipt_has_no_restart"]),
        )
    witness = str((receipt.get("check") or {}).get("packet_sha256") or packet.get("normal_proof_sha256") or UNKNOWN)
    return ReuseEventV1(
        event_id=str(body.get("intent_sha256") or qid),
        method_ids=method_ids,
        task_id=qid,
        source_schema=source,
        invocation_witness_id=witness,
        resources=resources,
        correctness=CorrectnessEvidence(
            checker_id="native.replay.v1" if native else "unary_method_check.check_packet",
            verdict=Verdict.PASS if (receipt.get("check") or {}).get("status") == "PASS" else Verdict.UNKNOWN,
            status=CheckStatus.MEASURED if (receipt.get("check") or {}).get("status") == "PASS" else CheckStatus.UNKNOWN,
        ),
        usefulness=unknown_usefulness(status=CheckStatus.CANNOT_CHECK, reason=GAPS["use_receipt_has_no_ablation"]),
        authorization=unknown_authorization(),
        g24=G24Lifecycle(
            actually_invoked=True,
            execution_trace_identifies_object=True,
            admitted_before_fresh_task=None,
            process_restarted=None,
            fresh_task_disjoint_from_acquisition=None,
            material_effect=CheckStatus.UNKNOWN,
            removal_ablation=CheckStatus.UNKNOWN,
            complete=False,
            status=CheckStatus.CANNOT_CHECK,
            cannot_check_reason=GAPS["use_receipt_has_no_restart"],
        ),
        notes=(f"mapped from {schema}", GAPS["use_receipt_has_no_restart"], GAPS["use_receipt_has_no_ablation"]),
    )


def map_clia_result_summary() -> dict[str, Any]:
    """Cite the closest existing reuse control. Does not satisfy G2.4 completeness."""
    return {
        "source": SOURCES["clia_core"],
        "readout": SOURCES["clia_readout"],
        "protocol": SOURCES["clia_protocol"],
        "adopt": "ADAPT",
        "mapped_type": "ReuseEventV1",
        "lifecycle": {
            "admitted_before_fresh_task": True,
            "process_restarted": True,
            "fresh_task_disjoint_from_acquisition": True,
            "actually_invoked": True,
            "execution_trace_identifies_object": True,
            "material_effect": "CANNOT_CHECK",
            "removal_ablation": "MEASURED",
            "answer_cache_excluded": "UNKNOWN",
            "retrieval_only_excluded": "PARENT_SUFFICIENT_FUNCTION_ONLY",
            "complete": False,
        },
        "scientific_terminal": "EXECUTABLE_REUSE_DEVELOPMENT_SUPPORTED / PARENT_SUFFICIENT_FUNCTION_ONLY",
        "cost_terminal": "CANNOT_CHECK_COST",
        "gaps": [
            GAPS["g24_not_complete"],
            "material cost coordinate is CANNOT_CHECK_COST",
            "result is matched native-library function reuse, not episode-induced method residual",
            "CORE.md: no OCM residual over the matched native library; not protected acceptance",
        ],
        "g24_checkbox": "UNCHECKED",
    }


def map_stitch_alias() -> RepresentationChangeV1:
    return RepresentationChangeV1(
        change_id="stitch-public-induction-20260906",
        before_representation_id="primitive:minus",
        after_representation_id="fn_0(h0,h1)=h1-h0",
        trigger="stitch public induction on two TRAIN programs",
        primitive_alias=PrimitiveAlias.PRIMITIVE_ALIAS,
        lifecycle_equivalence=CheckStatus.UNKNOWN,
        acquisition_lineage=AcquisitionLineage(
            origin_category=OriginCategory.TAUGHT_IMPORTED,
            donor_ids=("stitch",),
            status=CheckStatus.MEASURED,
        ),
        correctness=CorrectnessEvidence(
            checker_id="z3-whole-program",
            verdict=Verdict.PASS,
            status=CheckStatus.MEASURED,
        ),
        usefulness=unknown_usefulness(
            status=CheckStatus.CANNOT_CHECK,
            reason="stitch CORE.md: useful new operator acquisition remains NOT_ESTABLISHED; no later task",
        ),
        authorization=unknown_authorization(status=CheckStatus.CANNOT_CHECK, reason="no field admission or persistent library commit"),
        notes=(f"mapped from {SOURCES['stitch']}", "PRIMITIVE_ALIAS assessment dedicated packet NOT_RUN"),
    )


def map_scope_transfer_gap() -> ScopeTransferV1:
    return ScopeTransferV1(
        transfer_id="unrepresented",
        method_id=UNKNOWN,
        source_scope=ScopeState(),
        target_scope=ScopeState(),
        correspondence_witness_id=UNKNOWN,
        outcome="UNKNOWN",
        acquisition_lineage=unknown_lineage(status=CheckStatus.CANNOT_CHECK, reason=GAPS["scope_transfer_unrepresented"]),
        correctness=CorrectnessEvidence(status=CheckStatus.UNKNOWN),
        usefulness=unknown_usefulness(status=CheckStatus.CANNOT_CHECK, reason=GAPS["scope_transfer_unrepresented"]),
        authorization=unknown_authorization(),
        notes=(GAPS["scope_transfer_unrepresented"],),
    )


def mapping_table() -> list[dict[str, str]]:
    return [
        {"source": SOURCES["unary_envelope"], "target": "MethodRecordV1", "disposition": "ADAPT", "gap": GAPS["unary_utility_is_not_usefulness"]},
        {"source": SOURCES["native_store"], "target": "MethodRecordV1", "disposition": "ADAPT", "gap": GAPS["native_methods_are_imported"]},
        {"source": SOURCES["unary_journal"], "target": "ReuseEventV1|FailureAttemptV1", "disposition": "ADAPT", "gap": GAPS["use_receipt_has_no_restart"]},
        {"source": SOURCES["native_journal"], "target": "ReuseEventV1|FailureAttemptV1", "disposition": "ADAPT", "gap": GAPS["use_receipt_has_no_ablation"]},
        {"source": SOURCES["me_resource"], "target": "ResourceVector", "disposition": "ADOPT", "gap": ""},
        {"source": SOURCES["liveness"], "target": "CurrentAuthorizationState.liveness", "disposition": "ADAPT", "gap": ""},
        {"source": SOURCES["teaching_packet"], "target": "CognitiveEpisodeV1", "disposition": "REJECT", "gap": GAPS["teaching_packet_is_training_data"]},
        {"source": SOURCES["clia_core"], "target": "ReuseEventV1 / G2.4", "disposition": "ADAPT", "gap": GAPS["g24_not_complete"]},
        {"source": SOURCES["stitch"], "target": "RepresentationChangeV1", "disposition": "ADAPT", "gap": "no later-task usefulness"},
        {"source": SOURCES["typed_lifecycle"], "target": "MethodRecordV1", "disposition": "REJECT", "gap": "CORE.md: no useful acquisition; empty serving-eligible method IDs"},
        {"source": SOURCES["unary_release"], "target": "G2.4", "disposition": "REJECT", "gap": "restart/fresh causal use explicitly not established"},
        {"source": "ScopeTransferV1 sources", "target": "ScopeTransferV1", "disposition": "OPEN", "gap": GAPS["scope_transfer_unrepresented"]},
    ]
