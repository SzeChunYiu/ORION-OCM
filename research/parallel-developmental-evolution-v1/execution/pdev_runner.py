"""PDEV morphology runner: the frozen external meter over the pinned donor runtime.

Executes any grammar-legal morphology configuration (``pdev_grammar``) through
the vendored byte-identical donor code and returns the measured raw resource
vector.  NOTHING in here reads an outcome-dependent parameter: the meter was
written and frozen before any candidate evaluation ran (see PROTOCOL.json).

Honesty rules baked into the meter:

* ``Query.in_store`` and ``Query.truth`` are the SCORER's fields.  No code path
  in this module reads them.  The only family-identity consumer is the
  composite family-key unit, whose use of the public ``Query.family_id`` field
  is the donor ceiling mechanism absorbed as an explicit transferrable form
  (#214 first-refusal precedent) -- flagged in every receipt it produces.
* Every arm answers through ``arm.query`` so exactly one checker call per arm
  per query is charged; the composite pays up to two.
* Staged growth (``s_growth`` > 1) performs real intermediate ``grow`` events,
  each charged in the event that caused it.
* Bucket-bound overrides patch the module attribute for the duration of one
  candidate evaluation and restore it after (fail-closed on exception).
* Store reads/writes are metered by the donor's instrumented store; the meter
  additionally records lifetime store-read and store-write counts per task for
  the unmetered-scan and hidden-preprocessing hostiles.

Python 3.8+ stdlib only.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
VENDOR = HERE / "vendor" / "donor_runtime"
if str(VENDOR) not in sys.path:
    sys.path.insert(0, str(VENDOR))

import subspace as S  # noqa: E402
import subspace_arms as SA  # noqa: E402
import depend as D  # noqa: E402
import depend_arms as DA  # noqa: E402
from games import SubtractionGame  # noqa: E402

SCHEMA = "pdev217.runner.v1"

#: Headline resource vector (frozen; same keys as the #149 protocol).
RESOURCE_KEYS: Tuple[str, ...] = ("work", "persistent_bytes")
#: Detail vector retained per task for raw-vector accounting and hostiles.
DETAIL_KEYS: Tuple[str, ...] = (
    "query_work", "checker_expansions", "checker_calls", "index_work",
    "revision_work", "k_max", "N", "false_matches", "missed_matches",
    "stale_survivors", "collateral_invalidations", "store_reads",
    "store_writes", "index_build_work", "index_maintenance_work", "re_indexes",
    "features_evaluated", "growth_events", "escalations",
    "uses_family_identity", "n_queries", "n_correct",
)

#: Per-record numeric rows kept in receipts so hostiles can independently
#: recompute the charged vector (cost-moving) and audit instrumented reads.
RECORD_ROW_FIELDS: Tuple[str, ...] = (
    "operation", "k", "object_reads", "index_probes", "checker_calls",
    "checker_expansions", "query_work", "charged_total_work",
    "triggered_index_work", "index_build_work", "index_maintenance_work",
)


def _record_rows(records: Sequence[Any]) -> List[Dict[str, Any]]:
    rows = []
    for r in records:
        row: Dict[str, Any] = {}
        for name in RECORD_ROW_FIELDS:
            value = getattr(r, name, None)
            if value is None:
                row[name] = None
            elif isinstance(value, (int, float, str, bool)):
                row[name] = value
            else:
                row[name] = str(value)
        rows.append(row)
    return rows

_DEFAULT_BUCKET = SA.MAX_BUCKET_SIZE


# ---------------------------------------------------------------------------
# morphology unit construction
# ---------------------------------------------------------------------------

def resolve_feature(spec: str) -> "S.Feature":
    if spec == "prefix9":
        return S.Feature(S.SIGNATURE_PREFIX)
    if spec.startswith("fl"):
        idx = int(spec[2:])
        features = S.feature_language().features()
        if idx >= len(features):
            raise ValueError("feature index outside registered language")
        return features[idx]
    raise ValueError("unknown feature spec")


class MorphologyFeatureArm(SA.FeatureArm):
    """FeatureArm body driven by the morphology grammar (one class, flags set
    per candidate; the query path remains literally the donor's code)."""

    def __init__(self, catalogue: S.SubspaceCatalogue, config: Mapping[str, Any]):
        self._morph_config = dict(config)
        self.chooses_feature = bool(config.get("s_choose"))
        self.re_indexes = bool(config.get("s_reindex"))
        self.hand_feature = resolve_feature(str(config.get("s_feature", "prefix9")))
        super().__init__(catalogue)

    def as_receipt(self) -> Dict[str, Any]:
        return {"unit": "feature", "config": self._morph_config,
                "current_feature": (repr(self.current_feature.positions)
                                    if self.current_feature is not None else None),
                "language_exhausted": bool(self.language_exhausted)}


def build_s_arm(config: Mapping[str, Any], catalogue: S.SubspaceCatalogue
                ) -> Tuple[SA.SubspaceArm, Dict[str, Any]]:
    unit = config.get("s_unit", "feature")
    if unit == "feature":
        arm = MorphologyFeatureArm(catalogue, config)
        return arm, arm.as_receipt()
    factory = {"family_key": SA.OracleKeyParent,
               "vector": SA.NearestNeighbourParent,
               "scan": SA.ExactScanParent}[str(unit)]
    arm = factory(catalogue)
    return arm, {"unit": str(unit),
                 "uses_query_family_identity": unit == "family_key",
                 "donor_role": SA.ARM_ROLES.get(arm.arm_id, "ARM"),
                 "arm_id": arm.arm_id}


def build_d_arm(config: Mapping[str, Any]):
    mapping = {"learned": "learned_dependency_arm", "lazy": "lazy_learner_arm",
               "recompute": "full_recomputation_parent",
               "cooc": "co_occurrence_parent", "all_evidence": "all_evidence_parent"}
    arm_id = mapping[str(config.get("d_unit", "lazy"))]
    return arm_id, DA.ARMS[arm_id]


# ---------------------------------------------------------------------------
# staged growth
# ---------------------------------------------------------------------------

def _growth_ladder(scale: int, events: int) -> List[int]:
    """``s_growth`` = number of acquisition events dividing 1 -> scale.

    1 = the parent's single install+grow event; 2/5 = more, smaller growth
    events (more insertion maintenance and re-index triggers, charged each).
    """
    if scale <= 1:
        return []
    events = max(1, int(events))
    out: List[int] = []
    for k in range(1, events + 1):
        step = int(round(k * scale / events))
        if step >= 1 and (not out or step > out[-1]) and step < scale:
            out.append(step)
    out.append(scale)
    return out


# ---------------------------------------------------------------------------
# domain execution
# ---------------------------------------------------------------------------

def _record_counters(records: Sequence[Any], writes_declared: int) -> Tuple[int, int]:
    """Lifetime store-read lower bound from the donor's instrumented records.

    ``object_reads`` is summed over every record of the task (construction,
    growth, answers): that is every instrumented read the morphology made.
    Writes are declared accounting: each persistent object is inserted exactly
    once by ``populate_store``/``grow_store`` (the s domain never deletes), and
    each d-domain revocation is one structural mutation.
    """
    reads = sum(int(getattr(r, "object_reads", 0) or 0) for r in records)
    return reads, int(writes_declared)


def _run_s(config: Mapping[str, Any], item: Mapping[str, Any]) -> Dict[str, Any]:
    start = time.perf_counter_ns()
    scale, instance = int(item["scale"]), int(item["instance"])
    chunk = int(config.get("s_growth", 1))
    arm, unit_receipt = build_s_arm(config, S.build_catalogue(1))
    construction = [arm.install_record]
    growth_events = 0
    for step in _growth_ladder(scale, chunk):
        construction.append(arm.grow(S.build_catalogue(step)))
        growth_events += 1

    composite = config.get("s_composite", "none") == "in_store_first_refusal"
    family_arm = family_receipt = None
    if composite:
        family_arm = SA.OracleKeyParent(S.build_catalogue(1))
        family_construction = [family_arm.install_record]
        for step in _growth_ladder(scale, chunk):
            family_construction.append(family_arm.grow(S.build_catalogue(step)))
        construction.extend(family_construction)
        growth_events *= 2
        family_receipt = {
            "unit": "family_key",
            "mechanism": "donor ceiling absorbed as transferrable form (#214 "
                         "first-refusal precedent)",
            "uses_query_family_identity": True,
            "first_refusal": "family-key unit probed first; NO_METHOD_APPLIES "
                             "falls through to the configured s_unit",
            "routing_uses_scorer_in_store": False,
        }

    base_queries = S.query_stream()
    selected = [base_queries[i] for i in range(0, len(base_queries), 5)]
    position = 2003 + 2 * instance
    outcomes = []
    escalations = 0
    first_records: List[Any] = []
    fallthrough_records: List[Any] = []
    for q in selected:
        truth = SubtractionGame(q.moves).grundy_upto(position)[position] == 0
        query = S.Query(item["semantic_id"] + ":" + q.family_id, q.family_id,
                        q.moves, q.observations, position, q.in_store, truth)
        if composite:
            assert family_arm is not None
            first = family_arm.query(query)
            # The first-refusal probe is charged whether or not it answers:
            # its record (probe, read, checker call) enters the ledger here.
            first_records.append(first.record)
            if first.record.outcome != "NO_METHOD_APPLIES":
                outcomes.append(first)
            else:
                outcome = arm.query(query)
                outcomes.append(outcome)
                fallthrough_records.append(outcome.record)
                escalations += 1
        else:
            outcomes.append(arm.query(query))

    records = (construction + first_records + fallthrough_records
               + ([o.record for o in outcomes] if not composite else []))
    if any(r.k is None or r.k_status.value != "MEASURED" for r in records):
        raise ValueError("CANNOT_CHECK: incomplete relevance resource measurement")
    reads, writes = _record_counters(records, arm.n_objects)
    if family_arm is not None:
        fr, fw = _record_counters(
            family_construction + first_records, family_arm.n_objects)
        reads += fr
        writes += fw
    work = sum(r.charged_total_work + r.checker_expansions for r in records)
    persistent = arm.store_bytes + arm.index_bytes
    if family_arm is not None:
        persistent += family_arm.store_bytes + family_arm.index_bytes
    return {
        "domain": "s", "scale": scale, "instance": instance,
        "correct": all(o.decision_correct for o in outcomes),
        "violations": sum(o.false_match for o in outcomes),
        "missed_matches": sum(o.missed_match for o in outcomes),
        "work": work, "persistent_bytes": persistent,
        "query_work": sum(o.record.query_work for o in outcomes),
        "checker_expansions": sum(r.checker_expansions for r in records),
        "index_work": sum(r.triggered_index_work for r in records),
        "revision_work": 0,
        "k": max(o.record.k for o in outcomes), "N": arm.n_objects,
        "stale_survivors": 0, "collateral_invalidations": 0,
        "store_reads": reads, "store_writes": writes,
        "index_build_work": arm.lifetime_index_build_work,
        "index_maintenance_work": arm.lifetime_index_maintenance_work,
        "re_indexes": getattr(arm, "re_index_count", 0),
        "features_evaluated": getattr(arm, "features_evaluated", 0),
        "growth_events": growth_events, "escalations": escalations,
        "uses_family_identity": composite,
        "n_queries": len(outcomes),
        "n_correct": sum(o.decision_correct for o in outcomes),
        "checker_calls": sum(int(r.checker_calls or 0) for r in records),
        "record_rows": _record_rows(records),
        "unit_receipts": [unit_receipt] + ([family_receipt] if family_receipt else []),
        "elapsed_ns": time.perf_counter_ns() - start,
    }


def _run_d(config: Mapping[str, Any], item: Mapping[str, Any]) -> Dict[str, Any]:
    start = time.perf_counter_ns()
    scale, instance = int(item["scale"]), int(item["instance"])
    catalogue = D.build_catalogue(scale)
    schedule = list(D.revocation_schedule(catalogue))
    if instance not in (0, 1):
        raise ValueError("only two explicitly registered revision schedules")
    if instance == 1:
        schedule = list(reversed(schedule[:3])) + schedule[3:]

    def run_lifecycle(arm_id: str) -> Dict[str, Any]:
        arm = DA.ARMS[arm_id](D.build_catalogue(scale))
        revisions = [arm.revoke(step) for step in schedule]
        if any(r.k is None or r.revision_work is None or r.k_status.value != "MEASURED"
               for r in revisions):
            raise ValueError("CANNOT_CHECK: incomplete revision resource measurement")
        reads, writes = _record_counters(
            revisions, arm.n_objects + len(schedule))
        # Serialized ledger rows: the donor's d-domain records carry their
        # charged work as ``revision_work`` (revisions) / ``build_work``
        # (construction), not ``charged_total_work``; write the FULLY charged
        # total into each row so the cost-moving hostile can recompute the
        # headline exactly from the serialized ledger (no unmeasured residue).
        rows = _record_rows([arm.build_record] + list(revisions))
        rows[0]["charged_total_work"] = arm.build_work
        for row, rec in zip(rows[1:], revisions):
            row["charged_total_work"] = rec.revision_work
        return {
            "arm_id": arm_id,
            "stale": sum(len(r.stale_survivor_ids) for r in revisions),
            "collateral": sum(len(r.collateral_invalidated_ids) for r in revisions),
            "work": arm.build_work + sum(r.revision_work for r in revisions),
            "revision_work": sum(r.revision_work for r in revisions),
            "build_work": arm.build_work,
            "persistent_bytes": arm.store.store_bytes + arm.index_bytes,
            "k": max(r.k for r in revisions), "N": arm.n_objects,
            "reads": reads, "writes": writes,
            "record_rows": rows,
        }

    primary_id, _ = build_d_arm(config)
    composite = config.get("d_composite", "none") == "escalate_on_stale"
    primary = run_lifecycle(primary_id)
    escalated = None
    escalations = 0
    if composite:
        escalate_id = "learned_dependency_arm" if primary_id != "learned_dependency_arm" \
            else "all_evidence_parent"
        escalated = run_lifecycle(escalate_id)
        escalations = 1 if (primary["stale"] > 0 or primary["collateral"] > 0) else 0
        if escalations:
            primary, escalated = escalated, primary  # outcome source = escalated arm
    source = primary
    total_work = source["work"] + (escalated["work"] if escalated else 0)
    persistent = max(source["persistent_bytes"],
                     escalated["persistent_bytes"] if escalated else 0)
    reads = source["reads"] + (escalated["reads"] if escalated else 0)
    writes = source["writes"] + (escalated["writes"] if escalated else 0)
    return {
        "domain": "d", "scale": scale, "instance": instance,
        "correct": source["stale"] == source["collateral"] == 0,
        "violations": source["stale"],
        "missed_matches": 0,
        "work": total_work, "persistent_bytes": persistent,
        "query_work": 0,
        "checker_expansions": 0,
        "index_work": source["build_work"],
        "revision_work": source["revision_work"],
        "k": source["k"], "N": source["N"],
        "stale_survivors": source["stale"],
        "collateral_invalidations": source["collateral"],
        "store_reads": reads, "store_writes": writes,
        "index_build_work": source["build_work"],
        "index_maintenance_work": 0,
        "re_indexes": 0, "features_evaluated": 0,
        "growth_events": 0, "escalations": escalations,
        "uses_family_identity": False,
        "n_queries": len(schedule),
        "n_correct": int(source["stale"] == source["collateral"] == 0),
        "checker_calls": 0,
        "record_rows": list(source["record_rows"])
        + (list(escalated["record_rows"]) if escalated else []),
        "unit_receipts": [{"unit": source["arm_id"],
                           "donor_role": DA.ARM_ROLES.get(source["arm_id"], "ARM")}]
                         + ([{"unit": escalated["arm_id"], "escalated": True}]
                            if escalated else []),
        "elapsed_ns": time.perf_counter_ns() - start,
    }


def run_task(config: Mapping[str, Any], item: Mapping[str, Any]) -> Dict[str, Any]:
    if item["ecology"] != "development":
        raise PermissionError("this adapter cannot execute protected tasks")
    if item["domain"] == "s":
        return _run_s(config, item)
    if item["domain"] == "d":
        return _run_d(config, item)
    raise ValueError("unregistered domain")


def runner(config: Mapping[str, Any], tasks: Sequence[Mapping[str, Any]]
           ) -> Dict[str, Any]:
    """The frozen meter entry point (EvolutionCell Runner interface).

    Bucket-bound override is applied for the whole call and always restored.
    """
    global _DEFAULT_BUCKET
    bucket = int(config.get("s_bucket", 4))
    if bucket != _DEFAULT_BUCKET:
        SA.MAX_BUCKET_SIZE = bucket
        S.MAX_BUCKET_SIZE = bucket
    try:
        rows = [run_task(config, item) for item in tasks]
    finally:
        SA.MAX_BUCKET_SIZE = _DEFAULT_BUCKET
        S.MAX_BUCKET_SIZE = _DEFAULT_BUCKET
    return {"n": len(rows),
            "success": sum(1 for r in rows if r["correct"]),
            "preservation_violations": sum(r["violations"] for r in rows),
            "resources": {"work": sum(r["work"] for r in rows),
                          "persistent_bytes": max(
                              (r["persistent_bytes"] for r in rows), default=0)},
            "details": rows}


def aggregate_details(rows: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    """Raw-vector aggregation across tasks (sums; bytes peaked)."""
    out: Dict[str, Any] = {}
    for key in DETAIL_KEYS:
        if key in ("uses_family_identity",):
            out[key] = any(bool(r.get(key)) for r in rows)
        else:
            out[key] = int(sum(int(r.get(key, 0) or 0) for r in rows))
    return out
