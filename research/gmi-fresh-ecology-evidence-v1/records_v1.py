"""Exact arithmetic over the retained printed summaries; no evaluator calls."""
import json
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCORES = "STAGE_FRESH_ECOLOGY_CAPABILITY_V1.json"
ECOLOGIES = tuple("E_fresh" + str(i) for i in range(1, 6))
ROWS = ("compiled_search", "constant_emitter", "exemplar_table",
        "gradient_net_h2", "gradient_net_h4", "hamming_knn_k3",
        "particles_p4", "program_search", "soft_retrieval")
INTERVENTIONS = ("standard", "no_revoke", "double_revoke", "half_events",
                 "shuffled_events", "extra_unseen_feedback")


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def load_scores(path=None):
    return json.loads((path or HERE / "raw/tip" / SCORES).read_text(),
                      parse_float=F)


def fraction(value):
    require(type(value) in (int, F), "exact finite number required")
    return F(value)


def analyze(data):
    require(set(data) == {"ecologies", "interventions", "results", "schema", "seed"},
            "unexpected aggregate fields")
    require(data["schema"] == "FreshEcologyCapabilityTestV1", "schema")
    require(type(data["seed"]) is int and data["seed"] == 753793017, "seed")
    require(tuple(data["interventions"]) == INTERVENTIONS, "six intervention labels")
    require(set(data["ecologies"]) == set(ECOLOGIES), "ecology register")
    require(set(data["results"]) == set(ECOLOGIES), "result register")
    accepted = {r: [] for r in ROWS}
    thresholds = {r: [] for r in ROWS}
    search_margins, memory_margins, records = {}, {}, []
    for e in ECOLOGIES:
        coeffs = data["ecologies"][e]
        require(len(coeffs) == 4, "coefficient arity")
        for v in coeffs:
            require(-F(1, 2) <= fraction(v) <= F(1, 2)
                    and (16 * fraction(v)).denominator == 1, "coefficient grid")
        block = data["results"][e]
        require(set(block) == {"best_constant", "rows"}, "result block")
        require(0 <= fraction(block["best_constant"]) <= 1, "constant score")
        require(set(block["rows"]) == set(ROWS), "row register")
        for r in ROWS:
            row = block["rows"][r]
            require(set(row) == {"admissible", "margin_fx", "min_over_six"}, "row fields")
            score, margin = fraction(row["min_over_six"]), fraction(row["margin_fx"])
            require(0 <= score <= 1, "score range")
            require(type(row["admissible"]) is bool, "boolean flag")
            gate = score >= F(85, 100) and margin >= 1
            require(row["admissible"] == gate, "reported flag disagrees with printed predicate")
            if gate:
                accepted[r].append(e)
            if score >= F(85, 100):
                thresholds[r].append(e)
            records.append({"ecology": e, "row": r, "score": str(score),
                            "margin": str(margin), "reported_admissible": gate})
        require(block["rows"]["compiled_search"] == block["rows"]["program_search"],
                "search summaries differ")
        search_margins[e] = str(block["rows"]["program_search"]["margin_fx"])
        memory_margins[e] = str(block["rows"]["hamming_knn_k3"]["margin_fx"])
    band = {r: sum(F(887, 1000) <= data["results"][e]["rows"][r]["min_over_six"] <= 1
                   for e in ECOLOGIES) for r in ("program_search", "compiled_search")}
    predictions = {
        "P1": all(len(accepted[r]) >= 4 for r in band),
        "P2": not any(accepted[r] for r in ("gradient_net_h2", "gradient_net_h4")),
        "P3": all(v >= 4 for v in band.values()),
        "P4": 1 <= len(accepted["hamming_knn_k3"]) <= 4,
    }
    return {"scope": "PRINTED_AGGREGATE_CONSISTENCY_ONLY", "reported_score_rows": len(records),
            "ecology_count": 5, "intervention_labels": 6, "accepted_ecologies": accepted,
            "threshold_ecologies": thresholds, "search_margins": search_margins,
            "memory_margins": memory_margins, "predictions": predictions,
            "full_printed_row_audit": records}


def table_rows(text):
    return [[c.strip() for c in line.strip().strip("|").split("|")]
            for line in text.splitlines() if line.startswith("|")]


def prose_comparison(data, capability, sampling):
    report = analyze(data)
    margins = {}
    for row in table_rows(capability):
        name = row[0].strip("`")
        if name in ECOLOGIES and len(row) == 5:
            require(name not in margins, "duplicate prose ecology")
            margins[name] = F(row[-1].replace("+", ""))
    require(set(margins) == set(ECOLOGIES), "complete source margin table")
    mismatches = [{"ecology": e, "prose": str(margins[e]),
                   "json": report["search_margins"][e]} for e in ECOLOGIES
                  if margins[e] != F(report["search_margins"][e])]
    median = None
    baselines = {}
    for row in table_rows(sampling):
        if row[0] == "median":
            median = F(row[1])
        if row[0].startswith("`E_"):
            baselines[row[0].strip("`")] = F(row[1])
    require(median is not None and len(baselines) == 6, "sampling table")
    return {"search_margin_discrepancies": mismatches,
            "displayed_registry_median": str(median),
            "displayed_registry_comparison": {
                "below": sum(x < median for x in baselines.values()),
                "equal": sum(x == median for x in baselines.values()),
                "above": sum(x > median for x in baselines.values())},
            "sampling_raw_3000_draws": "NOT_IN_THE_FIVE_PATH_DELTA",
            "native_execution_identity": "NOT_BOUND_BY_THE_AGGREGATE"}
