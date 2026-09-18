"""Route A - ROW-FIRST construction of the Section H per-family requirement matrix.

Entry point: SECTION_H_MIRROR_V1.md (the verbatim issue text, frozen in the freeze commit).
The 43 open rows are enumerated from the issue text in body order.  Each row is bound into
the evidence packages by the frozen TEXT binding rule, and each cell is assigned from
ADJUDICATION_RULES_V1.json, which was frozen before any executor existed.

Route A does not import Route B.  Python 3.8 compatible, stdlib only, no floating point.
"""
from __future__ import print_function

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.dirname(HERE)

FOUR_FAMILY = os.path.join(RESEARCH, "gmi-833-h-neutral-four-family-v1")
CENSUS = os.path.join(RESEARCH, "gmi-833-h-obstruction-census-v1")

ROW_PATTERN = re.compile(r"^- \[ \] (.+)$")
CHECKED_PATTERN = re.compile(r"^- \[x\] (.+)$")


class RouteAError(Exception):
    pass


def normalize_row(text):
    """Frozen binding rule: casefold, strip whitespace, drop ONE trailing period."""
    value = text.strip()
    if value.endswith("."):
        value = value[:-1]
    return value.casefold().strip()


def read_rows():
    path = os.path.join(HERE, "SECTION_H_MIRROR_V1.md")
    with open(path, "r") as handle:
        lines = handle.read().splitlines()
    open_rows = []
    closed_rows = []
    for line in lines:
        match = ROW_PATTERN.match(line)
        if match:
            open_rows.append(match.group(1))
            continue
        match = CHECKED_PATTERN.match(line)
        if match:
            closed_rows.append(match.group(1))
    if len(open_rows) != 43:
        raise RouteAError("expected 43 open Section H rows, found %d" % len(open_rows))
    if len(closed_rows) != 2:
        raise RouteAError("expected 2 already-closed Section H rows, found %d" % len(closed_rows))
    return open_rows, closed_rows


def read_json(path):
    with open(path, "r") as handle:
        return json.load(handle)


def load_rules():
    return read_json(os.path.join(HERE, "ADJUDICATION_RULES_V1.json"))


def build_rule_index(rules):
    """(sigma, requirement) -> rule, plus the dispositional R04 rule at SIGMA_CENSUS."""
    flat = {}
    dispositional = {}
    for rule in rules["rules"]:
        sigma = rule["sigma"]
        if "status_by_census_disposition" in rule:
            for requirement in rule["requirements"]:
                dispositional[(sigma, requirement)] = rule["status_by_census_disposition"]
            continue
        for requirement in rule["requirements"]:
            key = (sigma, requirement)
            if key in flat:
                raise RouteAError("duplicate rule for %s" % (key,))
            flat[key] = rule
    return flat, dispositional


def four_family_rows():
    """Bind the ten-gate ledger rows by TEXT. Returns normalized row -> gate mapping."""
    ledger = read_json(os.path.join(FOUR_FAMILY, "FAMILY_GATE_LEDGER_V1.json"))
    bound = {}
    for entry in ledger["families"]:
        bound[normalize_row(entry["row"])] = entry
    if len(bound) != len(ledger["families"]):
        raise RouteAError("four-family ledger rows collide under the binding rule")
    return bound, ledger["gate_order"]


def census_rows():
    """Bind the census rows by TEXT. Returns normalized row -> census record."""
    result = read_json(os.path.join(CENSUS, "RESULT_V1.json"))
    bound = {}
    for entry in result["family_census"]:
        bound[normalize_row(entry["row"])] = entry
    if len(bound) != len(result["family_census"]):
        raise RouteAError("census rows collide under the binding rule")
    return bound


def _cell(row, requirement, sigma, status, rule, extra=None):
    cell = {
        "row": row,
        "requirement": requirement,
        "sigma": sigma,
        "status": status,
        "route": "A",
    }
    for field in ("citation", "supporting", "scope_gap", "build", "reason_not_adjudicated"):
        if rule and field in rule:
            cell[field] = rule[field]
    if extra:
        cell.update(extra)
    return cell


def build(k_edges_by_row_id=None, row_id_by_text=None):
    rules = load_rules()
    flat, dispositional = build_rule_index(rules)
    open_rows, closed_rows = read_rows()
    ff_bound, gate_order = four_family_rows()
    cn_bound = census_rows()
    requirements = sorted(rules["requirements"])

    cells = []
    bindings = []
    for row in open_rows:
        key = normalize_row(row)
        ff = ff_bound.get(key)
        cn = cn_bound.get(key)
        if cn is None:
            # Binding failure: never a guess.
            for requirement in requirements:
                cells.append(_cell(row, requirement, "SIGMA_CENSUS", "SCREENED_NOT_ADJUDICATED", None,
                                   {"reason_not_adjudicated": "row did not bind into the census registry"}))
            bindings.append({"row": row, "sigma_4f": ff is not None, "sigma_census": False, "h_id": None})
            continue
        bindings.append({"row": row, "sigma_4f": ff is not None, "sigma_census": True, "h_id": cn["id"],
                         "census_disposition": cn["disposition"], "census_contract": cn["contract"]})

        for requirement in requirements:
            # SIGMA_CENSUS
            if (("SIGMA_CENSUS", requirement) in dispositional):
                table = dispositional[("SIGMA_CENSUS", requirement)]
                branch = table.get(cn["disposition"])
                if branch is None:
                    cells.append(_cell(row, requirement, "SIGMA_CENSUS", "SCREENED_NOT_ADJUDICATED", None,
                                       {"reason_not_adjudicated": "census disposition %s has no frozen branch" % cn["disposition"]}))
                else:
                    cells.append(_cell(row, requirement, "SIGMA_CENSUS", branch["status"], branch,
                                       {"census_disposition": cn["disposition"], "census_contract": cn["contract"]}))
            else:
                rule = flat.get(("SIGMA_CENSUS", requirement))
                if rule is None:
                    cells.append(_cell(row, requirement, "SIGMA_CENSUS", "SCREENED_NOT_ADJUDICATED", None,
                                       {"reason_not_adjudicated": "no frozen rule"}))
                else:
                    cells.append(_cell(row, requirement, "SIGMA_CENSUS", rule["status"], rule,
                                       {"census_disposition": cn["disposition"], "census_contract": cn["contract"]}))

            # SIGMA_4F, only for rows that bind into the ten-gate ledger
            if ff is not None:
                rule = flat.get(("SIGMA_4F", requirement))
                if rule is None:
                    cells.append(_cell(row, requirement, "SIGMA_4F", "SCREENED_NOT_ADJUDICATED", None,
                                       {"reason_not_adjudicated": "no frozen rule"}))
                else:
                    cells.append(_cell(row, requirement, "SIGMA_4F", rule["status"], rule))

        # SIGMA_K, only for rows carrying an agent-constructed candidate K edge
        if k_edges_by_row_id and row_id_by_text:
            h_id = row_id_by_text.get(key)
            if h_id and k_edges_by_row_id.get(h_id):
                rule = flat.get(("SIGMA_K", "R04"))
                for requirement in rules_k_requirements(rules):
                    cells.append(_cell(row, requirement, "SIGMA_K", "SCREENED_NOT_ADJUDICATED", rule,
                                       {"candidate_k_families": k_edges_by_row_id[h_id]}))

    return {
        "route": "A",
        "entry_point": "SECTION_H_MIRROR_V1.md",
        "open_rows": open_rows,
        "closed_rows_out_of_scope": closed_rows,
        "bindings": bindings,
        "cells": cells,
    }


def rules_k_requirements(rules):
    for rule in rules["rules"]:
        if rule["sigma"] == "SIGMA_K":
            return list(rule["requirements"])
    raise RouteAError("no SIGMA_K rule frozen")
