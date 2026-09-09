"""Read-only, allowlisted development intake; source prose never reaches the self-model.

`extract` is an external curation operation. Only `load_cases` and `ingest_case`
belong to the proposer-facing interface. The audit manifest is external and must
not be supplied to a blinded proposer. This is an interface separation, not an OS
security boundary. No result-generating assay is imported or executed here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).resolve().parent / "sources"
MAIN_COMMIT = "3430919fd7614589e4fcfb9756dfaffb6ef1b3b4"
LADDER_COMMIT = "4f40e9f534eb4a16f254d9607291115b6b6ec44f"
TABLE_METRICS = (
    "N", "methods", "k_max", "k_mean", "k_over_N", "query_work_mean",
    "query_work_max", "lifetime_index_build_work", "lifetime_index_maintenance_work",
    "lifetime_index_work", "persistent_bytes", "store_bytes", "index_bytes",
    "false_matches", "missed_matches", "decision_error_rate", "feature_size",
    "re_indexes", "features_evaluated", "language_exhausted",
)
DEPEND_METRICS = (
    "N", "methods", "blocks", "graph_precision", "graph_recall", "graph_exact",
    "true_edges", "believed_edges", "missed_edges", "spurious_edges",
    "graph_disclosure_work", "build_work", "revocation_work", "total_work",
    "index_bytes", "persistent_bytes", "stale_survivors", "collateral_invalidations",
    "exact_revocations", "revocations",
)
STEP_METRICS = (
    "N", "expected_cone", "observed_cone", "precision", "recall",
    "stale_survivors", "collateral_invalidations", "exact", "revision_work", "k",
)
DIAG_METRICS = (
    "episodes", "correct", "accuracy", "probe_cost", "probes_bought",
    "cost_per_diagnosis", "correct_cannot_identify", "missed_cannot_identify",
    "false_cannot_identify", "over_generalisations", "reused_facts",
    "false_exclusions", "missed_reopenings", "wasted_work_avoided",
    "repeated_wasted_work", "downstream_queries",
)
ESC_METRICS = (
    "n", "exact_match", "accuracy", "false_escalation", "missed_escalation",
    "overreach", "underreach", "witnessed",
)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def numeric(row, keys):
    """Strict positive allowlist: no terminal, target, diagnosis or free-text values."""
    out = {}
    for key in keys:
        if key in row:
            if row[key] is None:
                out[key] = None
                continue
            if type(row[key]) not in (int, float, bool):
                raise ValueError("non-numeric allowlisted field: " + key)
            out[key] = row[key]
    return out


def source(commit, path):
    raw = subprocess.check_output(["git", "show", commit + ":" + path], cwd=ROOT)
    blob = subprocess.check_output(
        ["git", "rev-parse", commit + ":" + path], cwd=ROOT, text=True
    ).strip()
    return raw, {"commit": commit, "blob": blob, "path": path,
                 "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def extract():
    """Reproduce the six exposed-development summaries from pinned Git objects."""
    cases, audit = [], []
    identities = {}

    def opaque(kind, original):
        identity = kind + "-" + hashlib.sha256(original.encode()).hexdigest()[:12]
        identities[identity] = original
        return identity

    def add(label, binding, observations, extraction, missing, partial=False):
        case_id = "case-" + hashlib.sha256((binding["sha256"] + label).encode()).hexdigest()[:16]
        payload = {"case_id": case_id, "ecology": "DEVELOPMENT",
                   "observations": observations,
                   "trace_completeness": "PARTIAL_REVISION_STEPS" if partial else "SUMMARY_ONLY",
                   "raw_trace_status": "CANNOT_CHECK_RAW_TRACE_MISSING"}
        payload["observation_sha256"] = digest(observations)
        cases.append(payload)
        audit.append({"external_failure_key": label, "case_id": case_id,
                      "source": binding, "extraction": extraction,
                      "missing": missing, "observation_sha256": payload["observation_sha256"]})

    raw, binding = source(MAIN_COMMIT, "research/math-language-learning-v1/ASSAY-ACQUISITION-DIAGNOSIS.md")
    rows = []
    for line in raw.decode().splitlines():
        if re.fullmatch(r"\|\s*[0-3]\s*\|(?:\s*\d+\s*\|){7}", line):
            values = [int(x.strip()) for x in line.split("|")[1:-1]]
            rows.append(dict(zip(("episode", "eligible_checked_branches", "tried_subcovers",
                                  "valid_essential", "nonessential", "counterexample",
                                  "singleton_groups_excluded", "final_pool"), values)))
    if len(rows) != 4:
        raise ValueError("F1 table format changed")
    add("F1", binding, {"rows": rows}, "Only four numeric rows of the acquisition funnel table",
        ["Original A task/certificate/acquisition/process records absent from this Git tree",
         "External FACTS.json sha256 37c41f6e13a44a628617651550a47f56f04341e661a8d682f8f0b5d02d891f19 not read"])

    raw, binding = source(LADDER_COMMIT, "research/cognitive-ladder/results/SUBSPACE_E1_V1.json")
    data = json.loads(raw)
    rows = []
    for row in data["table"]:
        item = {"component_id": opaque("arm", row["arm_id"]),
                "scale_id": opaque("scale", row["scale"]), **numeric(row, TABLE_METRICS)}
        for key in ("answered", "decisions_correct", "in_store_correct", "absent_correct"):
            if key in row:
                match = re.fullmatch(r"(\d+)/(\d+)", row[key])
                if not match:
                    raise ValueError("invalid count fraction")
                item[key] = list(map(int, match.groups()))
        item["bucket_metrics"] = numeric(row["feature_adequacy"] or {},
            ("feature_size", "n_methods", "n_buckets", "max_bucket", "collision_rate", "mean_bucket", "adequate", "max_bucket_size_threshold"))
        rows.append(item)
    for label in ("F2", "F3"):
        add(label, binding, {"rows": rows},
            "table: allowlisted numeric resources/quality/bucket metrics; arm/scale names replaced by opaque IDs",
            ["Individual method/query traces and re-index search events not retained in receipt"])

    raw, binding = source(LADDER_COMMIT, "research/cognitive-ladder/results/DEPEND_E3_V1.json")
    data = json.loads(raw)
    rows = [{"component_id": opaque("arm", r["arm"]), "scale_id": opaque("scale", r["scale"]),
             **numeric(r, DEPEND_METRICS)} for r in data["table"]]
    steps = [{"component_id": opaque("arm", r["arm"]), "scale_id": opaque("scale", r["scale"]),
              "event_id": "event-" + str(i), **numeric(r, STEP_METRICS)}
             for i, r in enumerate(data["step_table"])]
    add("F4", binding, {"rows": rows, "events": steps},
        "table and step_table: numeric metrics; no discovery prose, semantic step names, support IDs or causal role labels",
        ["Full acquisition evidence and individual dependency intervention calls absent"], partial=True)

    raw, binding = source(LADDER_COMMIT, "research/cognitive-ladder/results/DIAGNOSIS_E2_V1.json")
    data = json.loads(raw)
    totals = [{"component_id": opaque("arm", arm), **numeric(v, DIAG_METRICS)}
              for arm, v in data["totals"].items()]
    rows = []
    for arm, worlds in data["per_world"].items():
        for world, v in worlds.items():
            curve = v["cost_curve"]
            if any(type(x) not in (int, float) for x in curve):
                raise ValueError("non-numeric cost curve")
            rows.append({"component_id": opaque("arm", arm), "stream_id": opaque("stream", world),
                         **numeric(v, DIAG_METRICS), "cost_curve": curve})
    add("F5", binding, {"rows": rows, "totals": totals},
        "totals/per_world numeric metrics and cost curves; target/verdict/confusion/cause labels excluded",
        ["Per-probe observations/choices absent", "Augmented cached parent has no measured row in this pinned receipt; reported cached-parent tie cannot be independently checked here"])

    raw, binding = source(LADDER_COMMIT, "research/cognitive-ladder/results/ESCALATION_INDEPENDENT_E4_V1.json")
    data = json.loads(raw)
    label_comparison = numeric(data["generator_intent_audit"],
        ("n", "intent_equals_oracle", "intent_agreement_rate", "intent_overstates_required_level", "intent_understates_required_level"))
    rows = [{"component_id": opaque("arm", arm), **numeric(v, ESC_METRICS)}
            for arm, v in data["independent_worlds"]["arms"].items()]
    add("F6", binding, {"rows": rows, "annotation_comparison": label_comparison},
        "independent_worlds.arms aggregate metrics and five numeric annotation comparison fields; oracle levels/repairs/examples excluded",
        ["Full 2000 instance traces and counterfactual repair evaluations absent"])

    SOURCES.mkdir(exist_ok=True)
    blind = {"schema": "ocm.self-evolution.blind-development.v1", "cases": cases}
    manifest = {"schema": "ocm.self-evolution.external-source-audit.v1",
        "proposer_access": False, "entries": audit, "opaque_identity_mapping": identities,
        "source_exposure": "External curators read source summaries including diagnosis prose. The machine-facing payload is allowlisted numeric observations only. Blinding is against direct label transmission, not against human prior knowledge in authored algorithms.",
        "protected_execution": False, "assays_executed": 0,
        "blind_payload_sha256": digest(blind)}
    for name, value in (("blind_development.json", blind), ("EXTERNAL_AUDIT_MANIFEST.json", manifest)):
        (SOURCES / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    return manifest


def load_cases(path=None):
    """Load only observations; never open provenance/diagnosis mapping."""
    payload = json.loads(Path(path or SOURCES / "blind_development.json").read_text())
    if payload.get("schema") != "ocm.self-evolution.blind-development.v1":
        raise ValueError("wrong intake schema")
    cases = payload["cases"]
    for case in cases:
        if case["ecology"] != "DEVELOPMENT" or digest(case["observations"]) != case["observation_sha256"]:
            raise ValueError("intake integrity/ecology failure")
    return cases


def ingest_case(self_model, case):
    """Create real M11 evidence and FailureRecord without a supplied attribution.

    A missing fine trace does not become available merely through ingestion. The
    observation evidence is a historical-summary receipt, not a causal witness.
    """
    from ocm.selfmodel.model import FailureRecord, Layer
    if case["ecology"] != "DEVELOPMENT" or digest(case["observations"]) != case["observation_sha256"]:
        raise ValueError("intake integrity/ecology failure")
    trace = self_model.record("development-observation:" + case["case_id"],
        {"case_id": case["case_id"], "observation_sha256": case["observation_sha256"],
         "observations": case["observations"], "trace_completeness": case["trace_completeness"]})
    failure = FailureRecord(
        failure_id=case["case_id"], task_id=case["case_id"], environment="DEVELOPMENT",
        observed=json.dumps(case["observations"], sort_keys=True),
        expected="Assess the registered quality/resource contract from observations; no responsibility label supplied",
        trace_ids=(trace,), candidate_layers=tuple(Layer), ablations=(),
        resource_state={"observation_sha256": case["observation_sha256"],
                        "raw_trace_status": case["raw_trace_status"]},
        uncertainty="UNKNOWN", severity="UNASSESSED", frequency=1, scope="self-evolution-development")
    self_model.ingest_failure(failure)
    return failure


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--extract", action="store_true", help="external read-only Git source curation")
    args = parser.parse_args()
    if args.extract:
        result = extract()
        print(json.dumps({"cases": len(result["entries"]), "assays_executed": 0,
                          "blind_payload_sha256": result["blind_payload_sha256"]}, sort_keys=True))
    else:
        print(json.dumps({"cases": len(load_cases()), "assays_executed": 0}, sort_keys=True))
