#!/usr/bin/env python3
"""Route A harness for gmi-833-ab-terminology-harness-v1 (issue #833, section AB).

For each in-scope AB row, verify that the registered terminology audit covers
every comparison term the row's own text names. Coverage is computed against
the frozen parent crosswalk first (parent_coverage) and then against
parent + this package's extension table (total_coverage), so parent ownership
stays visible and this package's residual is exactly the difference.

stdlib only; every reported quantity is an int.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))
PARENT = os.path.join(REPO, "research", "gmi-833-tranche-ab-ac-lit")
CROSSWALK = os.path.join(PARENT, "GMI_TERMINOLOGY_CROSSWALK_V2.md")
BANNED = os.path.join(PARENT, "BANNED_PAPER_TERMS_V1.md")
REQS = os.path.join(HERE, "AB_ROW_REQUIREMENTS_V1.json")
EXTENSION = os.path.join(HERE, "AB_CROSSWALK_EXTENSION_V1.md")

COLUMNS = ["idx", "legacy", "proposed", "field", "canonical", "match",
           "citations", "definition", "migration"]


def norm(s):
    s = s.lower()
    s = s.replace("—", "-").replace("–", "-").replace("→", "->")
    s = re.sub(r"[*`_]", "", s)
    s = s.replace("-", " ")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def parse_crosswalk(path):
    """Parse every 9-column table row whose first cell is an integer index."""
    rows = []
    for line in open(path).read().split("\n"):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 9:
            continue
        if not cells[0].isdigit():
            continue
        rows.append(dict(zip(COLUMNS, cells)))
    return rows


def parse_extension(path):
    if not os.path.exists(path):
        return []
    return parse_crosswalk(path)


def row_blob(r):
    """The audit of a term is carried by the registered row's SUBSTANTIVE cells:
    proposed paper term, academic field, canonical parents, operational
    definition and migration rule. The `legacy` cell is deliberately EXCLUDED:
    a row must not discharge a comparison requirement merely by repeating the
    legacy name it is supposed to be compared against."""
    return norm(" | ".join([r["proposed"], r["field"], r["canonical"],
                            r["definition"], r["migration"]]))


def find_rows(rows, term):
    """`term` may be one crosswalk legacy name or a list of them: a single AB
    row sometimes audits a term whose registered treatment is split over
    several crosswalk rows (e.g. `proof` -> rows 11, 17 and 46)."""
    names = term if isinstance(term, list) else [term]
    wanted = set(norm(t) for t in names)
    return [r for r in rows if norm(r["legacy"]) in wanted]


def covered(blob, req):
    if isinstance(req, dict):
        return any(norm(a) in blob for a in req["any_of"])
    return norm(req) in blob


def req_label(req):
    return " | ".join(req["any_of"]) if isinstance(req, dict) else req


VALID_MATCH = ("exact", "partial", "non", "exact-retain")


def check_row(spec, parent_rows, ext_rows, artifacts):
    kind = spec["evidence_kind"]
    reqs = spec["required_terms"]
    res = {"row_id": spec["row_id"], "evidence_kind": kind,
           "crosswalk_term": spec["crosswalk_term"],
           "required": len(reqs)}
    if kind == "CROSSWALK_COLUMNS":
        header = artifacts["crosswalk_header"]
        miss = [r for r in reqs if not covered(norm(header), r)]
        res["parent_covered"] = len(reqs) - len(miss)
        res["total_covered"] = res["parent_covered"]
        res["missing"] = [req_label(m) for m in miss]
        res["rows_in_crosswalk"] = artifacts["crosswalk_rows"]
        res["verdict"] = "EARNED" if not miss and artifacts["crosswalk_rows"] >= 1 else "OPEN"
        return res
    if kind == "ARTIFACT":
        blob = norm(artifacts["banned_blob"] if spec["crosswalk_term"] == "banned list"
                    else artifacts["gate_blob"])
        miss = [r for r in reqs if not covered(blob, r)]
        res["parent_covered"] = len(reqs) - len(miss)
        res["total_covered"] = res["parent_covered"]
        res["missing"] = [req_label(m) for m in miss]
        res["verdict"] = "EARNED" if not miss else "OPEN"
        if spec["row_id"] == "AB36":
            res["banned_terms"] = artifacts["banned_terms"]
            res["banned_with_replacement"] = artifacts["banned_with_replacement"]
            res["verdict"] = "EARNED" if (not miss and artifacts["banned_terms"] >= 1 and
                                          artifacts["banned_terms"] ==
                                          artifacts["banned_with_replacement"]) else "OPEN"
        if spec["row_id"] == "AB37":
            res["repo_wide_blocking_gate"] = artifacts["ratchet_present"]
            res["verdict"] = "EARNED" if (not miss and artifacts["ratchet_present"]) else "OPEN"
        return res
    # CROSSWALK_ROW and CROSSWALK_ROW+PARENT_PACKAGE
    pr = find_rows(parent_rows, spec["crosswalk_term"])
    er = find_rows(ext_rows, spec["crosswalk_term"])
    res["parent_rows_found"] = len(pr)
    res["extension_rows_found"] = len(er)
    pblob = " || ".join(row_blob(r) for r in pr)
    tblob = " || ".join([pblob] + [row_blob(r) for r in er])
    pmiss = [r for r in reqs if not covered(pblob, r)]
    tmiss = [r for r in reqs if not covered(tblob, r)]
    res["parent_covered"] = len(reqs) - len(pmiss)
    res["total_covered"] = len(reqs) - len(tmiss)
    res["supplied_by_this_package"] = [req_label(m) for m in pmiss if m not in tmiss]
    res["missing"] = [req_label(m) for m in tmiss]
    verdicts = [norm(r["match"]) for r in pr + er]
    res["match_verdicts"] = verdicts
    res["citations_nonempty"] = all(r["citations"].strip() for r in pr + er)
    res["migration_rule_nonempty"] = all(r["migration"].strip() for r in pr + er)
    ok = (len(pr) + len(er) >= 1 and not tmiss and
          all(v.startswith(VALID_MATCH) for v in verdicts) and
          res["citations_nonempty"] and res["migration_rule_nonempty"])
    if kind.endswith("PARENT_PACKAGE"):
        need = artifacts["parent_packages"].get(spec["row_id"])
        res["parent_package"] = need
        ok = ok and bool(need and need.get("present"))
    res["verdict"] = "EARNED" if ok else "OPEN"
    return res


def crosswalk_header(path):
    for line in open(path).read().split("\n"):
        if line.startswith("|") and "legacy GMI term" in line:
            return line
    return ""


def banned_stats(path):
    terms = 0
    withrep = 0
    for line in open(path).read().split("\n"):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 4 or cells[0].startswith("---") or cells[0] == "banned term":
            continue
        terms += 1
        if cells[2]:
            withrep += 1
    return terms, withrep


def grammar_bias_evidence(result_path):
    """AB13 asks for an explicit acknowledgement that the DSL/grammar itself
    induces strong bias. A document that merely contains the words `grammar`
    and `bias` must FAIL this predicate. What is required is a measured result:
    a claim ceiling naming grammar bias, `UNBIASED_G0` on the forbidden list,
    and a same-semantics hostile in which two grammars induce provably
    DIFFERENT exact rational reachability masses."""
    out = {"path": os.path.relpath(result_path, REPO), "present": False}
    if not os.path.exists(result_path):
        out["reason"] = "no receipt"
        return out
    try:
        d = json.load(open(result_path))
    except ValueError:
        out["reason"] = "receipt is not JSON"
        return out
    ceiling = str(d.get("claim_ceiling", ""))
    out["claim_ceiling"] = ceiling
    out["ceiling_names_grammar_bias"] = "GRAMMAR_BIAS" in ceiling.upper()
    out["forbids_unbiased"] = "UNBIASED_G0" in d.get("forbidden_promotions", [])
    hostile = d.get("nonisometric_same_semantics_hostile") or {}
    ga = hostile.get("GA_bias") or {}
    profiles = []
    for name in sorted(ga):
        q = ga[name].get("Q")
        if isinstance(q, dict):
            profiles.append(tuple(sorted(q.items())))
    out["grammars_compared"] = len(profiles)
    out["distinct_bias_profiles"] = len(set(profiles))
    out["bias_is_measured_not_asserted"] = (len(profiles) >= 2 and
                                            len(set(profiles)) >= 2)
    out["present"] = (out["ceiling_names_grammar_bias"] and out["forbids_unbiased"] and
                      out["bias_is_measured_not_asserted"])
    return out


COG_CRITERION = "operationally distinguishable iff"
COG_NON_CORRESPONDENCE = "do not establish anatomical modules"


def cognitive_criteria_evidence(theorems_path):
    """AB28 asks that cognitive terms satisfy OPERATIONAL criteria before any
    correspondence to human/animal constructs is claimed. A document that says
    the phrase `operational criteria` must FAIL: what is required is an
    executable criterion (an iff over a frozen probe interface), at least two
    named results, and an explicit refusal of the anatomical correspondence."""
    out = {"path": os.path.relpath(theorems_path, REPO), "present": False}
    if not os.path.exists(theorems_path):
        out["reason"] = "no theorems note"
        return out
    t = norm(open(theorems_path).read())
    out["operational_criterion"] = COG_CRITERION in t
    out["non_correspondence_scope"] = COG_NON_CORRESPONDENCE in t
    names = sorted(set(re.findall(r"\b(?:theorem|proposition) ([a-z]+ ?\d)", t)))
    out["named_results"] = names
    out["present"] = (out["operational_criterion"] and out["non_correspondence_scope"]
                      and len(names) >= 2)
    return out


def parent_package_evidence():
    return {
        "AB13": grammar_bias_evidence(os.path.join(
            REPO, "research", "gmi-833-g0-grammar-bias-v1", "RESULT_V1.json")),
        "AB28": cognitive_criteria_evidence(os.path.join(
            REPO, "research", "gmi-833-cognitive-reaudit-v1",
            "COGNITIVE_REAUDIT_THEOREMS_V1.md")),
    }


def run():
    spec = json.load(open(REQS))
    parent_rows = parse_crosswalk(CROSSWALK)
    ext_rows = parse_extension(EXTENSION)
    bt, bwr = banned_stats(BANNED)
    ratchet = os.path.join(HERE, "terminology_ratchet_v1.py")
    wf = os.path.join(REPO, ".github", "workflows",
                      "gmi-833-ab-terminology-harness-v1.yml")
    artifacts = {
        "crosswalk_header": crosswalk_header(CROSSWALK),
        "crosswalk_rows": len(parent_rows),
        "extension_rows": len(ext_rows),
        "banned_blob": open(BANNED).read(),
        "gate_blob": open(os.path.join(PARENT, "GMI_TERMINOLOGY_CI_GATE_V1.py")).read(),
        "banned_terms": bt,
        "banned_with_replacement": bwr,
        "ratchet_present": os.path.exists(ratchet) and os.path.exists(wf),
        "parent_packages": parent_package_evidence(),
    }
    rows = [check_row(s, parent_rows, ext_rows, artifacts) for s in spec["rows"]]
    earned = [r for r in rows if r["verdict"] == "EARNED"]
    return {
        "schema": "GMI_AB_HARNESS_RESULT_V1",
        "route": "A",
        "crosswalk_rows": len(parent_rows),
        "extension_rows": len(ext_rows),
        "banned_terms": bt,
        "banned_with_replacement": bwr,
        "rows_checked": len(rows),
        "rows_earned": len(earned),
        "rows_open": len(rows) - len(earned),
        "required_terms_total": sum(r["required"] for r in rows),
        "parent_covered_total": sum(r["parent_covered"] for r in rows),
        "total_covered_total": sum(r["total_covered"] for r in rows),
        "rows": rows,
    }


def main(argv):
    print(json.dumps(run(), indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
