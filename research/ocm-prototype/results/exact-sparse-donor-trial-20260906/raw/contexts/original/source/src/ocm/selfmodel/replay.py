"""Historical failure replay (M11 §14): the self-application ledger rows S11–S28 as frozen
FailureRecords, each with the layer the human attribution named and the class of the fix that
was actually shipped.  The replay is RECORDED — it re-reads outcomes, it does not re-execute the
historical code — so it can only check the *governance* over the record:

  narrowness      the shipped fix class never exceeded the minimum class for the attributed layer
  escalation      rows attributed above the local layers (D3/D4) carry a recorded ceiling witness
                  (the obstruction the certificate would need); rows without one are CANNOT_CHECK
  cannot-check    the S14 lesson: a stale receipt is CANNOT_CHECK, never a result

The layer assignment is the ledger's attribution column read through the D0–D8 vocabulary; it is
data, not a claim about the OCM's diagnostic accuracy (no ablation channel exists for history).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from . import diagnose as DG
from . import model as SM
from . import proposal as PR


@dataclass(frozen=True)
class HistoricalRow:
    row: str
    module: str
    attributed_layer: str
    shipped_class: PR.ChangeClass
    ceiling_witness: str | None          # recorded evidence that narrower repair was insufficient
    attribution: str


ROWS: tuple[HistoricalRow, ...] = (
    HistoricalRow("S11", "M3 interpretation", "D2", PR.ChangeClass.C2_OPERATOR, None, "the construction under-specified its slot (requires/forbids), not the morphology"),
    HistoricalRow("S12", "M3 morphology", "D2", PR.ChangeClass.C2_OPERATOR, None, "override predicate keyed on the token instead of the lemma"),
    HistoricalRow("S13", "M3 evaluation", "D3", PR.ChangeClass.C3_REPRESENTATION, "transitive_adj 0/26 under every flat pattern: no token pattern has a place for a modifier", "the construction grammar lacked recursion"),
    HistoricalRow("S14", "M3 evaluation tooling", "D2", PR.ChangeClass.C2_OPERATOR, None, "no freshness binding between run and receipt file (stale receipt read as a result)"),
    HistoricalRow("S15", "M4 correction", "D2", PR.ChangeClass.C2_OPERATOR, None, "supersession target chosen by recency instead of proposition identity"),
    HistoricalRow("S16", "M4 clarification", "D3", PR.ChangeClass.C3_REPRESENTATION, "a cardinality cannot rank a one-candidate question against a menu and is not commensurate with cost", "value defined as a cardinality instead of an expectation"),
    HistoricalRow("S17", "M5 regime E1", "D4", PR.ChangeClass.C3_REPRESENTATION, "held-out lexemes never occur in dev by construction: no aligned example with one unknown exists", "the regime's information design"),
    HistoricalRow("S18", "M6 gate", "D5", PR.ChangeClass.C2_OPERATOR, None, "the gate's layer vocabulary lagged the planner's"),
    HistoricalRow("S19", "M6 question forms", "D2", PR.ChangeClass.C2_OPERATOR, None, "a registered question form under-specified its determiner handling"),
    HistoricalRow("S20", "M2 solve loop", "D2", PR.ChangeClass.C2_OPERATOR, None, "the enabled set computed by fire_stage was discarded"),
    HistoricalRow("S21", "M4 promotion", "D3", PR.ChangeClass.C3_REPRESENTATION, "bridge ids travelling in the payload cannot make an atom depend on them: the evidence record had no derived_from field", "admit_evidence had no way to admit derived evidence"),
    HistoricalRow("S22", "M7 negative-transfer probe", "D1", PR.ChangeClass.C1_ROUTER, None, "the session treated the pending question as blocking"),
    HistoricalRow("S23", "M7 factual suite", "D2", PR.ChangeClass.C2_OPERATOR, None, "contradiction by object difference is wrong for non-functional relations"),
    HistoricalRow("S24", "M7 post-deployment relearn", "D3", PR.ChangeClass.C3_REPRESENTATION, "identical bytes deduplicate onto the revoked id by the KS rule: no operator-level change can distinguish the relearn", "a lesson event lacked a turn stamp"),
    HistoricalRow("S25", "M8 cross-scale navigation", "D2", PR.ChangeClass.C2_OPERATOR, None, "entry points defined by region membership"),
    HistoricalRow("S26", "M8 language stream", "D3", PR.ChangeClass.C3_REPRESENTATION, "closure from a single lexeme cannot fire a multi-tail DEPENDENCE edge under warrant semantics", "retrieval stream modelled with warrant semantics"),
    HistoricalRow("S27", "M9 comparators", "D4", PR.ChangeClass.C3_REPRESENTATION, "the parent skipped the acceptance test every other arm pays: no mechanism change can rebalance the accounting", "information/discipline accounting, not the mechanism"),
    HistoricalRow("S28", "M2.1 / M7 statistics", "D4", PR.ChangeClass.C3_REPRESENTATION, "an equivalence verdict with no scale is not a verdict", "pre-registered rule without an explicit scale"),
)


def replay_all() -> dict[str, Any]:
    rows = []
    for h in ROWS:
        layer = SM.Layer(h.attributed_layer)
        minimum_class = PR.minimum_class_for(h.attributed_layer)
        narrow = PR.CLASS_ORDER.index(h.shipped_class) <= PR.CLASS_ORDER.index(minimum_class)
        local = layer in DG.LOCAL
        escalation = None if local else ("WITNESSED" if h.ceiling_witness else "CANNOT_CHECK")
        rows.append({"row": h.row, "module": h.module, "attributed_layer": h.attributed_layer, "shipped_class": h.shipped_class.value, "minimum_class": minimum_class.value, "narrow": narrow, "local": local, "escalation_witness": escalation, "attribution": h.attribution})
    summary = {"rows": len(rows), "narrow": sum(r["narrow"] for r in rows), "local_layer_rows": sum(r["local"] for r in rows), "escalated_rows": sum(not r["local"] for r in rows), "escalated_with_witness": sum(r["escalation_witness"] == "WITNESSED" for r in rows), "escalated_cannot_check": sum(r["escalation_witness"] == "CANNOT_CHECK" for r in rows), "kind": "RECORDED_REPLAY (outcomes re-read, code not re-executed; layer assignment is the ledger attribution)"}
    return {"summary": summary, "rows": rows}
