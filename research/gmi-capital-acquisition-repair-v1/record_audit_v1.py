"""Small exact retained-record audit; never reruns the original K2 census."""
import hashlib
import json
from fractions import Fraction
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw/source/research"
DOC_HASH = "38493781de864856409a607ff75afea80a3f51ad89d5c8b947a66d77a6f84787"


def load(rel):
    data = (RAW / rel).read_bytes()
    return json.loads(data)


def module(rel, injected=None):
    source = (RAW / rel).read_text()
    # Only the original local selector import is replaced by a verified object;
    # no source file or global import cache is changed.
    env = {"__name__": "archived_source", "__file__": str(RAW / rel)}
    if injected is not None:
        source = source.replace("import learning_law_selection_v1 as M", "")
        env["M"] = injected
    exec(compile(source, str(RAW / rel), "exec"), env)
    return types.SimpleNamespace(**env)


def deferred(text):
    if hashlib.sha256(text.encode()).hexdigest() != DOC_HASH:
        raise ValueError("unregistered document: cannot check")
    m = module("gmi-learning-law-selection-v1/learning_law_selection_v1.py")
    old = module("gmi-learning-law-selection-v1/execute_deferred_v1.py", m)
    rows = old.parse_predictions(text)
    if len(rows) != 3 or {r["tag"] for r in rows} != {"D-P1", "D-P2", "D-P3"}:
        raise ValueError("missing or duplicate registered predictions")
    old.execute.__globals__["frozen_text"] = lambda: text
    result = old.execute()
    if result["total"] != 3:
        raise ValueError("incomplete execution")
    return result


def run():
    text = (RAW / "gmi-learning-law-selection-v1/DEFERRED_PREDICTIONS_V1.md").read_text()
    current = deferred(text)
    expected = load("gmi-learning-law-selection-v1/DEFERRED_EXECUTION_RECEIPT_V1.json")
    if current != expected:
        raise ValueError("full original three-table payload mismatch")
    receipt = load("gmi-k2-acquisition-experiment-v1/K2_ACQUISITION_RECEIPT_V1.json")
    cohorts = [receipt["exploratory"], receipt["confirmatory_heldout"]]
    for cohort in cohorts:
        for row in cohort["results"].values():
            if row["reuse_targets"] + row["noreuse_targets"] != cohort["targets"]:
                raise ValueError("cohort denominator mismatch")
            if not (0 <= row["k2_on_reuse"] <= row["reuse_targets"]):
                raise ValueError("invalid reuse count")
            if not (0 <= row["k2_on_noreuse"] + row["h_worse_on_noreuse"] <= row["noreuse_targets"]):
                raise ValueError("invalid nonreuse partition")
    total = sum(r["noreuse_targets"] for c in cohorts for r in c["results"].values())
    if total != receipt["necessity"]["total_noreuse_targets"]:
        raise ValueError("pooled denominator mismatch")
    rates = [Fraction(r["k2_on_reuse"], r["reuse_targets"])
             for r in cohorts[1]["results"].values() if r["reuse_targets"]]
    ties = [r["noreuse_targets"] - r["k2_on_noreuse"] - r["h_worse_on_noreuse"]
            for r in cohorts[0]["results"].values()]
    return {"deferred_complete_payload": current,
            "k2_original_complete_aggregate": receipt,
            "corrected_minimum_sufficiency": str(min(rates)),
            "exploratory_no_shortening_ties": ties,
            "scope": "retained aggregate/source audit, not original census replay"}
