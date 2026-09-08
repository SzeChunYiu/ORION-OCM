"""Existing receipts map onto G2.1 with explicit UNKNOWN gaps."""
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from g2_cognitive_objects.mapping import (
    GAPS,
    SOURCES,
    map_clia_result_summary,
    map_native_plan,
    map_stitch_alias,
    map_unary_envelope,
    map_use_receipt,
    mapping_table,
)
from g2_cognitive_objects.types import CheckStatus, FailureAttemptV1, PrimitiveAlias, ReuseEventV1, emit


def test_unary_envelope_does_not_treat_utility_as_usefulness():
    record = map_unary_envelope(
        {
            "schema": "ocm.unary-method.data.v1",
            "proof": "eid-proof",
            "discovery": "eid-disc",
            "sources_sha256": "abc",
            "schema_certificate": {"accepted": True},
        },
        method_id="unary:method:rule",
        eligible=True,
        correctness_liveness="LIVE",
        selection_liveness="LIVE",
    )
    emit(record)
    assert record.correctness.verdict.value == "PASS"
    assert record.usefulness.status is CheckStatus.CANNOT_CHECK
    assert GAPS["unary_utility_is_not_usefulness"] in record.usefulness.cannot_check_reason
    assert record.authorization.serving_liveness.value == "LIVE"


def test_native_plan_marks_imported_origin():
    record = map_native_plan(
        {
            "id": "native-method-1",
            "payload_sha256": "def",
            "proof": "p",
            "applicability": "a",
            "sources_sha256": "src",
            "qualification": {"claims_sha256": "claims"},
        }
    )
    emit(record)
    assert record.acquisition_lineage.origin_category.value == "TAUGHT_IMPORTED"
    assert record.usefulness.status is CheckStatus.CANNOT_CHECK
    assert record.authorization.serving_liveness.value == "UNKNOWN"


def test_native_checked_use_is_invocation_not_g24():
    event = map_use_receipt(
        {
            "schema": "ocm.native-method.use.v1",
            "qid": "q1",
            "intent_sha256": "int",
            "sources_sha256": "src",
            "receipt": {
                "terminal": "CHECKED",
                "solve_wall_s": 0.2,
                "check": {"status": "PASS", "packet_sha256": "pkt"},
                "packet": {"selected_proof_method_ids": ["mid-a"], "normal_proof_sha256": "np"},
            },
        },
        native=True,
    )
    assert isinstance(event, ReuseEventV1)
    emit(event)
    assert event.g24.actually_invoked is True
    assert event.g24.complete is False
    assert event.g24.process_restarted is None
    assert event.usefulness.status is CheckStatus.CANNOT_CHECK


def test_refused_use_is_failure_attempt():
    event = map_use_receipt(
        {
            "schema": "ocm.unary-method.use.v1",
            "qid": "q2",
            "intent_sha256": "int2",
            "receipt": {"terminal": "CANNOT_CHECK", "backend_failure": "METHOD_NOT_ELIGIBLE", "packet": None},
        },
        native=False,
    )
    assert isinstance(event, FailureAttemptV1)
    emit(event)
    assert event.failure_kind.value == "AUTHORITY_REFUSAL"


def test_stitch_alias_is_not_useful_acquisition():
    change = map_stitch_alias()
    emit(change)
    assert change.primitive_alias is PrimitiveAlias.PRIMITIVE_ALIAS
    assert change.usefulness.status is CheckStatus.CANNOT_CHECK


def test_clia_is_not_g24_complete():
    summary = map_clia_result_summary()
    assert summary["g24_checkbox"] == "UNCHECKED"
    assert summary["lifecycle"]["complete"] is False
    assert summary["lifecycle"]["process_restarted"] is True
    assert summary["lifecycle"]["removal_ablation"] == "MEASURED"
    assert (ROOT / "research/ocm-prototype/results/clia-reuse-study-result-20260906/CORE.md").is_file()
    assert (ROOT / "research/math-language-learning-v1/unary_method_store.py").is_file()
    assert (ROOT / "research/native-method-serving-v1/native_journal.py").is_file()


def test_mapping_table_cites_real_paths():
    rows = mapping_table()
    assert any(row["disposition"] == "ADOPT" and "ME_LIFETIME" in row["source"] for row in rows)
    assert any(row["disposition"] == "OPEN" for row in rows)
    for row in rows:
        if row["source"] in SOURCES.values() and not row["source"].startswith("Scope"):
            # cited files or JSON pointers into files
            path = row["source"].split("#", 1)[0].split(" ", 1)[0]
            if path.endswith(".py") or path.endswith(".md") or path.endswith(".json"):
                assert (ROOT / path).is_file(), path


def test_me_resource_fields_adopted():
    from g2_cognitive_objects.schema import load_schema
    from g2_cognitive_objects.types import ResourceVector

    me = json.loads((ROOT / "research/machine-epistemics-lifetime-v1/ME_LIFETIME_RECEIPT_SCHEMA_V1.json").read_text())
    g2 = load_schema("common.json")["$defs"]["resource_vector"]
    assert set(g2["properties"]) == set(me["$defs"]["resource"]["properties"]) == set(ResourceVector.__dataclass_fields__)
    assert set(g2["required"]) == set(me["$defs"]["resource"]["required"])
