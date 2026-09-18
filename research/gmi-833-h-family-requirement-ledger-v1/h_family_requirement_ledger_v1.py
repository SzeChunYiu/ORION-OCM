"""gmi-833-h-family-requirement-ledger-v1 - HRL-1..HRL-4 executor.

Builds the Section H per-family requirement matrix twice, from two materially independent
entry points, reconciles the two cell by cell, and emits:

  LEDGER_V1.json  - the matrix (HRL-1), the family-to-evidence map (HRL-2)
  RESULT_V1.json  - the receipt (HRL-3 residual distribution, HRL-4 verdict counts,
                    reconciliation, hostiles, null, extractor validation)

Closes no #833 checkbox.  Emits no reconciliation artifact.
Run: python3 -I -B h_family_requirement_ledger_v1.py

Python 3.8 compatible, stdlib only, integers only (no floating point anywhere).
"""
from __future__ import print_function

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import family_evidence_map_v1 as kmap          # noqa: E402
import route_a_rowfirst_v1 as route_a          # noqa: E402
import route_b_artifactfirst_v1 as route_b     # noqa: E402

RESEARCH = os.path.dirname(HERE)
CENSUS = os.path.join(RESEARCH, "gmi-833-h-obstruction-census-v1")

SOURCE_MAIN = "364f29f1b39557a863ce891529927cec8dadfd6f"
CLAIM_CEILING = (
    "PER_ROW_PER_REQUIREMENT_REQUIREMENT_STATUS_LEDGER_FOR_THE_43_OPEN_SECTION_H_NAMED_"
    "FAMILY_ROWS__NO_ROW_CLOSED__NO_CELL_EARNS_A_FAMILY"
)
FORBIDDEN_PROMOTIONS = [
    "NAMED_FAMILY_ROW_CLOSED",
    "ANY_SECTION_H_CHECKBOX_CLOSED",
    "NAMED_FAMILY_RECOVERED",
    "FINITE_EVIDENCE_IMPLIES_REAL_SCALE",
    "INDEPENDENT_TEAM_REPLICATION",
    "REAL_SCALE_VALIDATION",
    "K_FAMILY_IS_A_NAMED_ROW",
    "CROSS_SCOPE_GATE_COMPOSITION",
    "SECTION_H_UNIFORMLY_IMPOSSIBLE",
]

STATUS_ENUM = (
    "MET",
    "MET_AT_NARROWER_SCOPE",
    "MISSING_BUILDABLE",
    "MISSING_STRUCTURAL",
    "NOT_APPLICABLE",
    "SCREENED_NOT_ADJUDICATED",
)
MET_STATUSES = ("MET", "MET_AT_NARROWER_SCOPE")
REQUIREMENTS = ("R01", "R02", "R03", "R04", "R05", "R06", "R07", "R08", "R09", "R10", "R11")


class LedgerError(Exception):
    pass


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        digest.update(handle.read())
    return digest.hexdigest()


def cell_key(cell):
    return (cell["row"], cell["requirement"], cell["sigma"])


# --------------------------------------------------------------------------- build

def build_matrix():
    registry = kmap.load_k_registry()
    census_registry = route_b.read_json(os.path.join(CENSUS, "FROZEN_FAMILY_REGISTRY_V1.json"))
    row_index = dict((f["id"], f["row"]) for f in census_registry["families"])
    row_id_by_text = dict((route_a.normalize_row(f["row"]), f["id"]) for f in census_registry["families"])

    absence = kmap.verify_k_binding_absence([f["row"] for f in census_registry["families"]])
    if not absence["absence_established"]:
        raise LedgerError("a primary K-family/named-row binding was found; the freeze premise is false")

    kmapping = kmap.build_map(registry, row_index)
    k_edges_by_row_id = {}
    for edge in kmapping["edges"]:
        k_edges_by_row_id.setdefault(edge["h_id"], []).append(edge["k_family"])

    a = route_a.build(k_edges_by_row_id=k_edges_by_row_id, row_id_by_text=row_id_by_text)
    b = route_b.build(k_edges_by_row_id=k_edges_by_row_id)
    return a, b, kmapping, absence, row_index, row_id_by_text


def reconcile(a, b):
    index_a = dict((cell_key(c), c) for c in a["cells"])
    index_b = dict((cell_key(c), c) for c in b["cells"])
    if len(index_a) != len(a["cells"]):
        raise LedgerError("route A emitted duplicate cells")
    if len(index_b) != len(b["cells"]):
        raise LedgerError("route B emitted duplicate cells")
    only_a = sorted(set(index_a) - set(index_b))
    only_b = sorted(set(index_b) - set(index_a))
    shared = sorted(set(index_a) & set(index_b))
    disagreements = []
    for key in shared:
        if index_a[key]["status"] != index_b[key]["status"]:
            disagreements.append({"cell": list(key),
                                  "route_a": index_a[key]["status"],
                                  "route_b": index_b[key]["status"],
                                  "route_a_basis": index_a[key].get("citation", ""),
                                  "route_b_basis": index_b[key].get("witness", "")})
    return {
        "cells_route_a": len(index_a),
        "cells_route_b": len(index_b),
        "cells_shared": len(shared),
        "cells_only_route_a": [list(k) for k in only_a],
        "cells_only_route_b": [list(k) for k in only_b],
        "disagreements": disagreements,
        "agreement_count": len(shared) - len(disagreements),
        "agreement_is_total": not disagreements and not only_a and not only_b,
    }


def merge(a, b, recon):
    """The ledger keeps route A's cell record, having proved both routes agree on status."""
    if not recon["agreement_is_total"]:
        raise LedgerError("routes disagree; a merged ledger may not be emitted before resolution")
    index_b = dict((cell_key(c), c) for c in b["cells"])
    merged = []
    for cell in a["cells"]:
        record = dict(cell)
        record["route"] = "A+B"
        record["route_b_witness"] = index_b[cell_key(cell)].get("witness", "")
        merged.append(record)
    return merged


# --------------------------------------------------------------------- HRL-3 / HRL-4

def per_sigma_counts(cells, rows):
    counts = {}
    for row in rows:
        counts[row] = {}
    for cell in cells:
        counts[cell["row"]].setdefault(cell["sigma"], {})[cell["requirement"]] = cell["status"]
    return counts


def residual(cells, rows):
    counts = per_sigma_counts(cells, rows)
    per_row = {}
    for row in rows:
        best_sigma = None
        best_met = -1
        by_sigma = {}
        for sigma, mapping in counts[row].items():
            met = sum(1 for r in REQUIREMENTS if mapping.get(r) in MET_STATUSES)
            by_sigma[sigma] = {
                "met": met,
                "requirements_covered": len(mapping),
                "missing": sorted(r for r in REQUIREMENTS if mapping.get(r) not in MET_STATUSES
                                  and mapping.get(r) is not None),
                "not_covered": sorted(r for r in REQUIREMENTS if r not in mapping),
            }
            # only a sigma that covers all eleven coordinates can carry a row verdict
            if len(mapping) == len(REQUIREMENTS) and met > best_met:
                best_met = met
                best_sigma = sigma
        per_row[row] = {"by_sigma": by_sigma, "best_sigma": best_sigma,
                        "best_met_of_11": best_met if best_sigma else 0}
    return per_row


def verdicts(cells, rows, per_row):
    counts = per_sigma_counts(cells, rows)
    out = {}
    for row in rows:
        sigma = per_row[row]["best_sigma"]
        if sigma is None:
            out[row] = {"verdict": "CLOSABLE_AFTER_BUILDABLE_WORK",
                        "reason": "no single scope covers all eleven coordinates",
                        "sigma": None, "residual": list(REQUIREMENTS)}
            continue
        mapping = counts[row][sigma]
        residual_reqs = [r for r in REQUIREMENTS if mapping[r] not in MET_STATUSES]
        statuses = set(mapping[r] for r in residual_reqs)
        if not residual_reqs:
            verdict = "CLOSABLE_NOW"
        elif "MISSING_STRUCTURAL" in statuses:
            verdict = "BLOCKED_STRUCTURAL"
        elif statuses <= set(["MISSING_BUILDABLE", "NOT_APPLICABLE"]):
            verdict = "CLOSABLE_AFTER_BUILDABLE_WORK"
        else:
            verdict = "CLOSABLE_AFTER_BUILDABLE_WORK"
        out[row] = {"verdict": verdict, "sigma": sigma,
                    "residual": residual_reqs,
                    "residual_statuses": dict((r, mapping[r]) for r in residual_reqs)}
    return out


# ------------------------------------------------------------------------- checker

def check(rows, cells, kmapping):
    """Acceptance predicate. Returns list of violations; empty list means ACCEPTED."""
    violations = []
    if len(rows) != 43:
        violations.append("ROW_COUNT_NOT_43")
    if len(set(rows)) != len(rows):
        violations.append("DUPLICATE_ROW")

    mirror_rows, _ = route_a.read_rows()
    if list(rows) != list(mirror_rows):
        violations.append("ROW_TEXT_DRIFT")

    by_row_sigma = {}
    for cell in cells:
        if cell["status"] not in STATUS_ENUM:
            violations.append("STATUS_OUT_OF_ENUM:" + str(cell["status"]))
        if cell["status"] == "MET":
            violations.append("UNQUALIFIED_MET:%s/%s/%s" % (cell["row"], cell["requirement"], cell["sigma"]))
        if cell["status"] == "NOT_APPLICABLE":
            if cell["requirement"] != "R06" or not cell.get("citation"):
                violations.append("NOT_APPLICABLE_WITHOUT_PROOF:%s/%s" % (cell["row"], cell["requirement"]))
        if cell["requirement"] == "R11":
            if cell["status"] == "MISSING_STRUCTURAL":
                violations.append("FGS3_OVERREAD:%s/%s" % (cell["row"], cell["sigma"]))
            if cell["status"] in MET_STATUSES:
                violations.append("REAL_SCALE_CLAIMED:%s/%s" % (cell["row"], cell["sigma"]))
        if cell["sigma"] == "SIGMA_K" and cell["status"] != "SCREENED_NOT_ADJUDICATED":
            violations.append("K_PROMOTION:%s/%s" % (cell["row"], cell["requirement"]))
        key = (cell["row"], cell["sigma"])
        by_row_sigma.setdefault(key, {})[cell["requirement"]] = cell["status"]

    for (row, sigma), mapping in by_row_sigma.items():
        met = [r for r in REQUIREMENTS if mapping.get(r) in MET_STATUSES]
        if len(met) == len(REQUIREMENTS):
            violations.append("CLOSABLE_NOW_CLAIMED:%s/%s" % (row, sigma))

    # scope-gluing: a row is glued if its met set is complete only when sigmas are pooled
    for row in rows:
        pooled = set()
        per_sigma_met = []
        for (r, sigma), mapping in by_row_sigma.items():
            if r != row:
                continue
            met = set(x for x in REQUIREMENTS if mapping.get(x) in MET_STATUSES)
            per_sigma_met.append(met)
            pooled |= met
        if len(pooled) == len(REQUIREMENTS) and not any(len(m) == len(REQUIREMENTS) for m in per_sigma_met):
            violations.append("SCOPE_GLUE:" + row)

    # two requirements at the same (row, sigma) may not both be non-MISSING on one and the
    # same citation string: that is double counting one witness (HOSTILE_SHARED_CITATION_DOUBLE_COUNT)
    by_citation = {}
    for cell in cells:
        citation = cell.get("citation")
        if not citation or cell["status"].startswith("MISSING") or cell["status"] == "SCREENED_NOT_ADJUDICATED":
            continue
        key = (cell["row"], cell["sigma"], citation)
        by_citation.setdefault(key, set()).add(cell["requirement"])
    for key, requirements in by_citation.items():
        if len(requirements) > 1:
            violations.append("SHARED_CITATION_DOUBLE_COUNT:%s/%s/%s"
                              % (key[0], key[1], ",".join(sorted(requirements))))

    for edge in kmapping["edges"]:
        if edge["provenance"] != "AGENT_CONSTRUCTED_UNADJUDICATED":
            violations.append("K_EDGE_PROVENANCE:" + edge["k_family"] + "->" + edge["h_id"])
    return violations


# ------------------------------------------------------------------------ hostiles

def _clone(cells):
    return [dict(c) for c in cells]


def hostiles(rows, cells, kmapping):
    results = []

    h = _clone(cells)
    for cell in h:
        if cell["row"] == rows[0] and cell["sigma"] == "SIGMA_CENSUS":
            cell["status"] = "MET_AT_NARROWER_SCOPE"
    results.append(("HOSTILE_CLOSABLE_NOW", check(rows, h, kmapping)))

    # glue SIGMA_4F's R11 into a fabricated met, leaving no single sigma complete
    h = _clone(cells)
    target = rows[0]
    for cell in h:
        if cell["row"] != target:
            continue
        if cell["sigma"] == "SIGMA_CENSUS" and cell["requirement"] != "R11":
            cell["status"] = "MET_AT_NARROWER_SCOPE"
        if cell["sigma"] == "SIGMA_4F" and cell["requirement"] == "R11":
            cell["status"] = "MET_AT_NARROWER_SCOPE"
    results.append(("HOSTILE_SCOPE_GLUE", check(rows, h, kmapping)))

    h = _clone(cells)
    for cell in h:
        if cell["sigma"] == "SIGMA_K":
            cell["status"] = "MET_AT_NARROWER_SCOPE"
            break
    results.append(("HOSTILE_K_PROMOTION", check(rows, h, kmapping)))

    drifted = list(rows)
    drifted[7] = drifted[7].replace("Decision", "Decisions")
    results.append(("HOSTILE_ROW_DRIFT", check(drifted, cells, kmapping)))

    h = _clone(cells)
    h[0] = dict(h[0])
    h[0]["status"] = "MET"
    results.append(("HOSTILE_UNQUALIFIED_MET", check(rows, h, kmapping)))

    h = _clone(cells)
    for cell in h:
        if cell["requirement"] == "R11":
            cell["status"] = "MISSING_STRUCTURAL"
    results.append(("HOSTILE_FGS3_OVERREAD", check(rows, h, kmapping)))

    results.append(("HOSTILE_ROW_DROP", check(list(rows)[:42], cells, kmapping)))

    h = _clone(cells)
    for cell in h:
        if cell["requirement"] == "R06" and cell["sigma"] == "SIGMA_CENSUS":
            cell["status"] = "NOT_APPLICABLE"
            cell.pop("citation", None)
            break
    results.append(("HOSTILE_NA_WITHOUT_PROOF", check(rows, h, kmapping)))

    # two requirements at one (row, sigma) counted met on one and the same citation
    h = _clone(cells)
    target_row = rows[0]
    donor = None
    for cell in h:
        if cell["row"] == target_row and cell["sigma"] == "SIGMA_CENSUS" \
                and cell["requirement"] == "R01" and cell.get("citation"):
            donor = cell["citation"]
            break
    for cell in h:
        if cell["row"] == target_row and cell["sigma"] == "SIGMA_CENSUS" and cell["requirement"] == "R08":
            cell["status"] = "MET_AT_NARROWER_SCOPE"
            cell["citation"] = donor
            cell["scope_gap"] = "fabricated"
            break
    results.append(("HOSTILE_SHARED_CITATION_DOUBLE_COUNT", check(rows, h, kmapping)))

    detected = dict((name, len(v) > 0) for name, v in results)
    return {
        "hostiles": [{"name": name, "detected": len(v) > 0, "violations": v[:4]} for name, v in results],
        "all_detected": all(detected.values()),
        "count": len(results),
    }


def null_controls(rows, cells, kmapping, trials=200, seed=20260918):
    """Exact-integer LCG randomized control ledgers. No float, no `random`."""
    state = seed
    modulus = 2147483647
    multiplier = 48271
    passed = 0
    for _ in range(trials):
        variant = _clone(cells)
        for cell in variant:
            state = (multiplier * state) % modulus
            cell["status"] = STATUS_ENUM[state % len(STATUS_ENUM)]
        if not check(rows, variant, kmapping):
            passed += 1
    return {"trials": trials, "seed": seed, "controls_accepted": passed,
            "true_ledger_accepted": not check(rows, cells, kmapping)}


# ---------------------------------------------------------------------- validation

HAND_READ = {
    "H01": {"row": "Finite-state/automata intelligence.",
            "sigma_4f_present": True, "census_disposition": "IDENTIFIABILITY_OBSTRUCTION",
            "census_contract": "UNEXCITED_CONTEXT"},
    "H02": {"row": "Linear regression / linear classifiers.",
            "sigma_4f_present": True, "census_disposition": "RECOVERED_CONTROL",
            "census_contract": "PAIR_PARITY"},
    "H20": {"row": "Feed-forward neural networks.",
            "sigma_4f_present": False, "census_disposition": "RECOVERED_CONTROL",
            "census_contract": "PAIR_PARITY"},
    "H25": {"row": "Attention mechanisms.",
            "sigma_4f_present": False, "census_disposition": "IDENTIFIABILITY_OBSTRUCTION",
            "census_contract": "UNEXCITED_CONTEXT"},
}


def validate_extractor(cells, row_index):
    checks = []
    by_row = {}
    for cell in cells:
        by_row.setdefault(cell["row"], []).append(cell)
    for h_id, expected in sorted(HAND_READ.items()):
        row = row_index[h_id]
        if row != expected["row"]:
            checks.append({"h_id": h_id, "ok": False, "why": "registry row text differs from the hand-read text"})
            continue
        present = set(c["sigma"] for c in by_row[row])
        got_4f = "SIGMA_4F" in present
        dispositions = set(c.get("census_disposition") for c in by_row[row] if c["sigma"] == "SIGMA_CENSUS")
        contracts = set(c.get("census_contract") for c in by_row[row] if c["sigma"] == "SIGMA_CENSUS")
        ok = (got_4f == expected["sigma_4f_present"]
              and dispositions == set([expected["census_disposition"]])
              and contracts == set([expected["census_contract"]]))
        checks.append({"h_id": h_id, "row": row, "ok": ok,
                       "sigma_4f_present": got_4f,
                       "expected_sigma_4f_present": expected["sigma_4f_present"],
                       "census_disposition": sorted(x for x in dispositions if x),
                       "census_contract": sorted(x for x in contracts if x),
                       "case": "PLANTED_POSITIVE" if expected["sigma_4f_present"] else "NO_ALARM"})
    return {"cases": checks, "all_ok": all(c["ok"] for c in checks),
            "planted_positive_recall": sum(1 for c in checks if c["case"] == "PLANTED_POSITIVE" and c["ok"]),
            "planted_positive_total": sum(1 for c in checks if c["case"] == "PLANTED_POSITIVE"),
            "no_alarm_cases_clean": sum(1 for c in checks if c["case"] == "NO_ALARM" and c["ok"]),
            "no_alarm_total": sum(1 for c in checks if c["case"] == "NO_ALARM")}


# ------------------------------------------------------------------------- reports

def distribution(per_row, rows):
    hist = dict((str(n), 0) for n in range(0, 12))
    for row in rows:
        hist[str(per_row[row]["best_met_of_11"])] += 1
    return hist


def residual_dominance(cells, rows, per_row):
    counts = per_sigma_counts(cells, rows)
    missing = dict((r, 0) for r in REQUIREMENTS)
    for row in rows:
        sigma = per_row[row]["best_sigma"]
        if sigma is None:
            for r in REQUIREMENTS:
                missing[r] += 1
            continue
        mapping = counts[row][sigma]
        for r in REQUIREMENTS:
            if mapping[r] not in MET_STATUSES:
                missing[r] += 1
    return missing


def canonical_status(cells, rows, per_row):
    """Exactly one status per (row, requirement): 473 entries, taken at the row's best
    single covering scope. Scope is carried on every entry - FGS-2 forbids composing
    across scopes, so the canonical view is a projection, never a merge."""
    counts = per_sigma_counts(cells, rows)
    index = dict(((c["row"], c["requirement"], c["sigma"]), c) for c in cells)
    canonical = {}
    total = 0
    for row in rows:
        sigma = per_row[row]["best_sigma"]
        entry = {}
        for requirement in REQUIREMENTS:
            if sigma is None:
                entry[requirement] = {"status": "SCREENED_NOT_ADJUDICATED", "sigma": None,
                                      "why": "no single scope covers all eleven coordinates"}
            else:
                cell = index[(row, requirement, sigma)]
                record = {"status": cell["status"], "sigma": sigma}
                for field in ("citation", "scope_gap", "build"):
                    if field in cell:
                        record[field] = cell[field]
                entry[requirement] = record
            total += 1
        canonical[row] = entry
    if total != len(rows) * len(REQUIREMENTS):
        raise LedgerError("canonical map is not total")
    return canonical


def status_totals(cells):
    totals = dict((s, 0) for s in STATUS_ENUM)
    by_sigma = {}
    for cell in cells:
        totals[cell["status"]] += 1
        by_sigma.setdefault(cell["sigma"], dict((s, 0) for s in STATUS_ENUM))[cell["status"]] += 1
    return totals, by_sigma


def main():
    a, b, kmapping, absence, row_index, row_id_by_text = build_matrix()
    rows = a["open_rows"]
    recon = reconcile(a, b)
    cells = merge(a, b, recon)

    per_row = residual(cells, rows)
    row_verdicts = verdicts(cells, rows, per_row)
    violations = check(rows, cells, kmapping)
    hostile_report = hostiles(rows, cells, kmapping)
    null_report = null_controls(rows, cells, kmapping)
    validation = validate_extractor(cells, row_index)
    totals, by_sigma = status_totals(cells)

    verdict_counts = {}
    for row in rows:
        verdict_counts[row_verdicts[row]["verdict"]] = verdict_counts.get(row_verdicts[row]["verdict"], 0) + 1

    hist = distribution(per_row, rows)
    dominance = residual_dominance(cells, rows, per_row)

    # pooled, scope-blind distribution - reported ONLY under its FGS-2 label
    pooled_hist = dict((str(n), 0) for n in range(0, 12))
    counts = per_sigma_counts(cells, rows)
    pooled_rows = {}
    for row in rows:
        pooled = set()
        for sigma, mapping in counts[row].items():
            if sigma == "SIGMA_K":
                continue
            pooled |= set(r for r in REQUIREMENTS if mapping.get(r) in MET_STATUSES)
        pooled_hist[str(len(pooled))] += 1
        pooled_rows[row] = sorted(pooled)

    census_registry = route_b.read_json(os.path.join(CENSUS, "FROZEN_FAMILY_REGISTRY_V1.json"))
    contract_by_row = dict((f["row"], f["contract"]) for f in census_registry["families"])
    distinct_contracts = sorted(set(contract_by_row.values()))

    predictions = {
        "P1_closable_now_is_zero": (verdict_counts.get("CLOSABLE_NOW", 0) == 0,
                                    verdict_counts.get("CLOSABLE_NOW", 0)),
        "P2_missing_structural_is_zero": (totals["MISSING_STRUCTURAL"] == 0, totals["MISSING_STRUCTURAL"]),
        "P3_unqualified_met_is_zero": (totals["MET"] == 0, totals["MET"]),
        "P4_R11_missing_at_all_43": (dominance["R11"] == 43, dominance["R11"]),
        "P5_R10_not_in_residual": (dominance["R10"] == 0, dominance["R10"]),
    }

    ledger = {
        "schema": "GMI833HFamilyRequirementLedgerV1",
        "source_main": SOURCE_MAIN,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN_PROMOTIONS,
        "closes_no_checkbox": True,
        "emits_no_reconciliation_artifact": True,
        "requirements": {
            "R01": "property prediction from specification/ecology",
            "R02": "P3/P4 grammar",
            "R03": "no family macros",
            "R04": "neutral recovery",
            "R05": "negative twin",
            "R06": "lower bound where possible",
            "R07": "resource crossover",
            "R08": "held-out frozen prediction",
            "R09": "remint",
            "R10": "independent search",
            "R11": "real-scale test",
        },
        "hrl1_matrix": cells,
        "hrl1_canonical_status": canonical_status(cells, rows, per_row),
        "hrl1_canonical_status_note": (
            "Exactly one status per (row, requirement) - 43 x 11 = 473 entries - projected "
            "onto the row's best single covering scope. Every entry names its scope: FGS-2 "
            "forbids composing certificates across scopes, so this is a projection of "
            "hrl1_matrix, never a merge of it."
        ),
        "hrl2_family_to_evidence_map": {
            "named_row_to_census_contract": contract_by_row,
            "distinct_census_contracts": distinct_contracts,
            "distinct_census_contract_count": len(distinct_contracts),
            "named_rows": len(contract_by_row),
            "k_family_to_named_row_candidates": kmapping,
            "k_binding_absence_verification": {
                "absence_established": absence["absence_established"],
                "way1_verbatim_row_text_hits": absence["way1_verbatim_row_text_hits"],
                "way2_section_h_mention_hits": absence["way2_section_h_mention_hits"],
                "control_pattern_fired": absence["control_pattern_hits"] > 0,
                "note": ("file and hit COUNTS are deliberately not committed here: they depend "
                         "on nine sibling packages another lane may add files to, and this "
                         "package's CI compares the committed receipt against a fresh run. "
                         "The counts are printed by the executor and asserted by the test."),
            },
            "provenance_note": (
                "The named-row-to-census-contract map is EVIDENCE-BACKED: it is read verbatim "
                "from research/gmi-833-h-obstruction-census-v1/FROZEN_FAMILY_REGISTRY_V1.json. "
                "The K-family-to-named-row map is AGENT_CONSTRUCTED_UNADJUDICATED: no primary "
                "artifact in the corpus asserts any such edge."
            ),
        },
        "hrl3_per_row_scope_counts": per_row,
        "hrl4_row_verdicts": row_verdicts,
    }

    result = {
        "schema": "GMI833HFamilyRequirementLedgerResultV1",
        "source_main": SOURCE_MAIN,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN_PROMOTIONS,
        "closes_no_checkbox": True,
        "emits_no_reconciliation_artifact": True,
        "rows": len(rows),
        "requirements": len(REQUIREMENTS),
        "row_requirement_pairs": len(rows) * len(REQUIREMENTS),
        "cells_total": len(cells),
        "cell_status_totals": totals,
        "cell_status_totals_by_sigma": by_sigma,
        "hrl3_best_single_scope_met_distribution": hist,
        "hrl3_residual_dominance_missing_rows_per_requirement": dominance,
        "hrl3_pooled_distribution_NON_GLUABLE_UNDER_FGS2": pooled_hist,
        "hrl4_verdict_counts": verdict_counts,
        "hrl4_closable_now_rows": [r for r in rows if row_verdicts[r]["verdict"] == "CLOSABLE_NOW"],
        "hrl4_blocked_structural_rows": [r for r in rows if row_verdicts[r]["verdict"] == "BLOCKED_STRUCTURAL"],
        "hrl2_distinct_census_contracts": len(distinct_contracts),
        "hrl2_k_edges": len(kmapping["edges"]),
        "hrl2_rows_with_candidate_k": len(kmapping["rows_with_candidate_k"]),
        "hrl2_rows_without_any_k": kmapping["rows_without_any_k"],
        "hrl2_rows_with_multiple_k": kmapping["rows_with_multiple_k"],
        "reconciliation_two_routes": recon,
        "checker_violations_on_true_ledger": violations,
        "true_ledger_accepted": not violations,
        "hostiles": hostile_report,
        "null": null_report,
        "extractor_validation": validation,
        "k_binding_absence_established": absence["absence_established"],
        "adjudication_corrections_applied": [c["id"] for c in
                                             route_b.read_json(os.path.join(HERE, "ADJUDICATION_CORRECTION_V1.json"))["corrections"]],
        "frozen_predictions": dict((k, {"held": v[0], "observed": v[1]}) for k, v in predictions.items()),
        "all_frozen_predictions_held": all(v[0] for v in predictions.values()),
        "structural_constraints": route_a.load_rules()["structural_constraints_recorded_not_as_cells"],
    }

    with open(os.path.join(HERE, "LEDGER_V1.json"), "w") as handle:
        json.dump(ledger, handle, indent=1, sort_keys=True)
        handle.write("\n")
    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as handle:
        json.dump(result, handle, indent=1, sort_keys=True)
        handle.write("\n")

    print("rows=%d cells=%d" % (len(rows), len(cells)))
    print("routes agree totally: %s (shared=%d, disagreements=%d)"
          % (recon["agreement_is_total"], recon["cells_shared"], len(recon["disagreements"])))
    print("HRL-3 best-single-scope met distribution:", json.dumps(hist, sort_keys=True))
    print("HRL-3 residual dominance:", json.dumps(dominance, sort_keys=True))
    print("HRL-4 verdicts:", json.dumps(verdict_counts, sort_keys=True))
    print("status totals:", json.dumps(totals, sort_keys=True))
    print("hostiles all detected:", hostile_report["all_detected"])
    print("null: %d/%d controls accepted; true ledger accepted: %s"
          % (null_report["controls_accepted"], null_report["trials"], null_report["true_ledger_accepted"]))
    print("extractor validation ok:", validation["all_ok"])
    print("K-binding absence: established=%s files_scanned=%d control_hits=%d"
          % (absence["absence_established"], absence["files_scanned"], absence["control_pattern_hits"]))
    print("frozen predictions held:", result["all_frozen_predictions_held"],
          json.dumps(dict((k, v[1]) for k, v in predictions.items()), sort_keys=True))
    if violations:
        raise LedgerError("true ledger rejected: " + ", ".join(violations[:5]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
