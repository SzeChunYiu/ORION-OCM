"""Route B - ARTIFACT-FIRST construction of the same matrix, materially independently.

Route B never reads SECTION_H_MIRROR_V1.md and never reads ADJUDICATION_RULES_V1.json.
It enumerates assertions out of the evidence packages themselves:

  * rows come from FROZEN_FAMILY_REGISTRY_V1.json by machine id H01..H43 and ORDINAL
    position (not by text matching);
  * SIGMA_4F rows come from FAMILY_GATE_LEDGER_V1.json by ORDINAL position, cross-checked
    against RESULT_V1.json::family_gate_ledger.family_rows by ORDINAL;
  * cell statuses are derived from each artifact's OWN status strings, and where an
    artifact has no status string, from a presence/absence detection Route B performs
    itself on that artifact's bytes.

Route B does not import Route A.  Python 3.8 compatible, stdlib only, no floating point.
"""
from __future__ import print_function

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.dirname(HERE)
FOUR_FAMILY = os.path.join(RESEARCH, "gmi-833-h-neutral-four-family-v1")
CENSUS = os.path.join(RESEARCH, "gmi-833-h-obstruction-census-v1")


class RouteBError(Exception):
    pass


# Route B's own translation of the corpus status vocabulary. Written independently of
# ADJUDICATION_RULES_V1.json.
GATE_STATUS_TO_CELL = {
    "SUPPORTED_AT_REGISTERED_EXACT_SCOPE": "MET_AT_NARROWER_SCOPE",
    "SUPPORTED_SOURCE_SEPARATED_EXACT_SCOPE": "MET_AT_NARROWER_SCOPE",
    "OPEN": "MISSING_BUILDABLE",
}

# Route B's own gate-name -> requirement translation. The ten-gate ledger collapses the
# grammar and the macro requirement into one name; Route B splits it and takes each half
# from a different field of the package's own RESULT_V1.json.
GATE_TO_REQUIREMENT = {
    "property_prediction_from_ecology": "R01",
    "neutral_recovery": "R04",
    "negative_twin": "R05",
    "lower_bound_where_possible": "R06",
    "resource_crossover": "R07",
    "heldout_frozen_prediction": "R08",
    "remint": "R09",
    "independent_search": "R10",
    "real_scale_test": "R11",
}
SPLIT_GATE = "p3_p4_lower_grammar_without_named_macros"

CENSUS_DISPOSITION_TO_R04 = {
    "RECOVERED_CONTROL": "MET_AT_NARROWER_SCOPE",
    "EXPRESSIVITY_OBSTRUCTION": "MISSING_BUILDABLE",
    "RESOURCE_OBSTRUCTION": "MISSING_BUILDABLE",
    "IDENTIFIABILITY_OBSTRUCTION": "MISSING_BUILDABLE",
}


def read_json(path):
    with open(path, "r") as handle:
        return json.load(handle)


def read_text(path):
    with open(path, "r") as handle:
        return handle.read()


def census_presence_profile():
    """Route B's own presence detection over the census package bytes.

    Returns requirement -> (status, detector, witness). Detection is positive-only: a
    requirement is met at narrower scope when Route B finds the artifact structure that
    would carry it, and MISSING_BUILDABLE when the structure is absent everywhere in the
    package.
    """
    result = read_json(os.path.join(CENSUS, "RESULT_V1.json"))
    registry = read_json(os.path.join(CENSUS, "FROZEN_FAMILY_REGISTRY_V1.json"))
    theorems = read_text(os.path.join(CENSUS, "OBSTRUCTION_THEOREMS_V1.md"))
    oracle = read_json(os.path.join(CENSUS, "ORACLE_RESULT_V1.json"))
    source = read_text(os.path.join(CENSUS, "obstruction_census_v1.py"))

    profile = {}

    has_prediction = all(
        "predicted_disposition" in spec for spec in registry["target_contracts"].values()
    ) and "predicted_counts" in registry and 'registry["predicted_counts"]' in source
    profile["R01"] = ("MET_AT_NARROWER_SCOPE" if has_prediction else "MISSING_BUILDABLE",
                      "registry predicted_disposition for every target contract and an executor equality assertion")
    # R08 is NOT inherited from R01: Route B asks whether the census package asserts a
    # held-out gate at all. It never uses the word, and the frozen prediction's domain is
    # exactly the evaluated contract set, so nothing is held out from it.
    census_blob = (json.dumps(result) + json.dumps(registry) + theorems + source).lower()
    asserts_heldout = ("heldout" in census_blob) or ("held-out" in census_blob) or ("held out" in census_blob)
    profile["R08"] = ("MET_AT_NARROWER_SCOPE" if asserts_heldout else "MISSING_BUILDABLE",
                      "the census package asserts no held-out prediction gate; the frozen "
                      "prediction's domain is exactly the evaluated contract set")

    has_grammar = "leaves" in result["scope"] and "operators" in result["scope"]
    profile["R02"] = ("MET_AT_NARROWER_SCOPE" if has_grammar else "MISSING_BUILDABLE",
                      "RESULT_V1.json::scope.leaves + scope.operators - one grammar for all rows")

    has_macro_statement = "Family names never occur in the grammar or search" in theorems
    profile["R03"] = ("MET_AT_NARROWER_SCOPE" if has_macro_statement else "MISSING_BUILDABLE",
                      "OBSTRUCTION_THEOREMS_V1.md statement that family names never occur in grammar or search")

    has_twin = ("negative" in theorems.lower()) or ("twin" in theorems.lower()) \
        or ("negative" in json.dumps(result).lower()) or ("twin" in json.dumps(result).lower())
    profile["R05"] = ("MET_AT_NARROWER_SCOPE" if has_twin else "MISSING_BUILDABLE",
                      "no matched negative twin structure anywhere in the census package")

    has_bound = "lower_bound_enumeration_limit" in result["scope"] and "semantic_quotient" in result
    profile["R06"] = ("MET_AT_NARROWER_SCOPE" if has_bound else "MISSING_BUILDABLE",
                      "RESULT_V1.json::scope.lower_bound_enumeration_limit + semantic_quotient layer sizes")

    blob = json.dumps(result).lower() + theorems.lower() + source.lower()
    has_crossover = ("crossover" in blob) or ("price" in blob) or ("resource_regime" in blob)
    profile["R07"] = ("MET_AT_NARROWER_SCOPE" if has_crossover else "MISSING_BUILDABLE",
                      "single node-count cost model; no price regimes in the census package")

    has_remint = "REMINT" in result.get("theorems", {}) or "H-REMINT" in theorems
    profile["R09"] = ("MET_AT_NARROWER_SCOPE" if has_remint else "MISSING_BUILDABLE",
                      "OBSTRUCTION_THEOREMS_V1.md H-REMINT + executor remint guard")

    oracle_ok = "no primary import" in oracle.get("implementation", "") and \
        set(oracle.get("target_results", {})) == set(registry["target_contracts"])
    profile["R10"] = ("MET_AT_NARROWER_SCOPE" if oracle_ok else "MISSING_BUILDABLE",
                      "ORACLE_RESULT_V1.json source-separated oracle covering every target contract")

    eligible = result.get("family_gate_audit", {}).get("eligible_named_family_rows")
    profile["R11"] = ("MISSING_BUILDABLE" if eligible == 0 else "SCREENED_NOT_ADJUDICATED",
                      "RESULT_V1.json::family_gate_audit.eligible_named_family_rows = %r" % (eligible,))
    return profile


def four_family_profile():
    """Route B derives SIGMA_4F cells from the ledger's own per-gate status strings."""
    ledger = read_json(os.path.join(FOUR_FAMILY, "FAMILY_GATE_LEDGER_V1.json"))
    result = read_json(os.path.join(FOUR_FAMILY, "RESULT_V1.json"))
    by_ordinal = {}
    declared = result["family_gate_ledger"]["family_rows"]
    if len(declared) != len(ledger["families"]):
        raise RouteBError("ledger/result family-row counts disagree")
    for index, entry in enumerate(ledger["families"]):
        if entry["row"] != declared[index]:
            raise RouteBError("ordinal %d row text disagrees between ledger and result" % index)
        cells = {}
        for gate_name, gate in entry["gates"].items():
            status = GATE_STATUS_TO_CELL.get(gate["status"])
            if status is None:
                raise RouteBError("unknown gate status " + gate["status"])
            if gate_name == SPLIT_GATE:
                # split, each half taking its own witness out of RESULT_V1.json
                grammar_ok = "definition" in result["grammar"] and "digest" in result["grammar"]
                macro_ok = result["semantic_no_smuggling_audit"].get("token_scan_clean") is True and \
                    result["semantic_no_smuggling_audit"].get("semantic_verdict") == "NO_TARGET_DEPENDENT_GENERATION_DETECTED"
                cells["R02"] = (status if grammar_ok else "MISSING_BUILDABLE",
                                "RESULT_V1.json::grammar.definition + grammar.digest")
                cells["R03"] = (status if macro_ok else "MISSING_BUILDABLE",
                                "RESULT_V1.json::semantic_no_smuggling_audit.token_scan_clean + semantic_verdict")
                continue
            requirement = GATE_TO_REQUIREMENT.get(gate_name)
            if requirement is None:
                raise RouteBError("unknown gate name " + gate_name)
            cells[requirement] = (status, "FAMILY_GATE_LEDGER_V1.json::families[%d].gates.%s = %s"
                                  % (index, gate_name, gate["status"]))
            # Each SIGMA_4F gate is witnessed by its own named field, so R01 and R08 do not
            # share a citation string even though they share the FROZEN evidence key
            # (soundness observation HRL-5.1).
        by_ordinal[index] = {"row": entry["row"], "cells": cells,
                             "complete": entry.get("complete"),
                             "checkbox": entry.get("issue_833_checkbox")}
    return by_ordinal


def build(k_edges_by_row_id=None, k_requirements=("R02", "R03", "R04", "R10")):
    registry = read_json(os.path.join(CENSUS, "FROZEN_FAMILY_REGISTRY_V1.json"))
    census_result = read_json(os.path.join(CENSUS, "RESULT_V1.json"))
    census_by_id = dict((entry["id"], entry) for entry in census_result["family_census"])
    profile = census_presence_profile()
    ff = four_family_profile()

    # Route B's binding: registry ordinal i <-> census family_census ordinal i, by id.
    ff_row_to_ordinal = {}
    for ordinal, record in ff.items():
        ff_row_to_ordinal[record["row"]] = ordinal

    cells = []
    bindings = []
    for ordinal, family in enumerate(registry["families"]):
        h_id = family["id"]
        census = census_by_id.get(h_id)
        if census is None:
            raise RouteBError("registry id %s absent from the census result" % h_id)
        if census["row"] != family["row"]:
            raise RouteBError("registry/result row text disagrees at %s" % h_id)
        row = family["row"]

        # SIGMA_4F attaches when the ledger row, lowercased with its period dropped by the
        # ledger's own authors, is the registry row with the same treatment.
        ff_ordinal = None
        for ledger_row, cand in ff_row_to_ordinal.items():
            if ledger_row.strip().lower() == row.strip().lower().rstrip("."):
                ff_ordinal = cand
                break
        bindings.append({"h_id": h_id, "ordinal": ordinal, "row": row,
                         "sigma_4f_ordinal": ff_ordinal,
                         "census_disposition": census["disposition"],
                         "census_contract": census["contract"]})

        # R04 is the one census requirement that is not package-level: it is per-row
        # dispositional, so it is enumerated explicitly rather than from the presence
        # profile. Round 1 of the two-route reconciliation found exactly this omission
        # (ROUTE_RECONCILIATION_ROUND1_V1.json).
        census_requirements = sorted(set(profile) | set(["R04"]))
        for requirement in census_requirements:
            if requirement == "R04":
                status = CENSUS_DISPOSITION_TO_R04[census["disposition"]]
                witness = "family_census[%s].disposition = %s" % (h_id, census["disposition"])
            else:
                status, witness = profile[requirement]
            cells.append({"row": row, "requirement": requirement, "sigma": "SIGMA_CENSUS",
                          "status": status, "route": "B", "witness": witness,
                          "census_disposition": census["disposition"],
                          "census_contract": census["contract"]})

        if ff_ordinal is not None:
            for requirement, pair in sorted(ff[ff_ordinal]["cells"].items()):
                cells.append({"row": row, "requirement": requirement, "sigma": "SIGMA_4F",
                              "status": pair[0], "route": "B", "witness": pair[1]})

        if k_edges_by_row_id and k_edges_by_row_id.get(h_id):
            for requirement in k_requirements:
                cells.append({"row": row, "requirement": requirement, "sigma": "SIGMA_K",
                              "status": "SCREENED_NOT_ADJUDICATED", "route": "B",
                              "witness": "candidate K families %s are agent-constructed; no primary binding exists"
                                         % (",".join(k_edges_by_row_id[h_id]),),
                              "candidate_k_families": k_edges_by_row_id[h_id]})

    return {"route": "B", "entry_point": "FROZEN_FAMILY_REGISTRY_V1.json + FAMILY_GATE_LEDGER_V1.json",
            "bindings": bindings, "cells": cells}
