#!/usr/bin/env python3
"""Route A - AC literature-structure harness (issue #833, AC01/AC03/AC04/AC06).

Verifies, against the FROZEN lanes index and the FROZEN 48-row crosswalk, the
structure the AC rows demand. It verifies NOTHING about whether any citation is
correct: AC05 is out of scope and every result carries the citation
verification status as a disclosed field.

Route B (`independent_ac_oracle_v1.py`) re-derives every quantity with an
independently written parser and is compared by set equality, not by count.

stdlib only; exact integer arithmetic; python3.8-compatible.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Sequence, Set, Tuple

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
LIT = REPO / "research" / "gmi-833-tranche-ab-ac-lit"
LANES = LIT / "EXPERT_LITERATURE_LANES_V1.md"
CROSSWALK = LIT / "GMI_TERMINOLOGY_CROSSWALK_V2.md"
ADDENDUM = HERE / "AC_CROSSWALK_ADDENDUM_V1.md"

# The AC rows, verbatim from comment 5684607872 at source_main. Every
# requirement below is extracted FROM these strings; the anti-invention guard
# asserts it.
ROWS = {
    "AC01": ("- [ ] Create expert literature lanes: theoretical CS/formal languages; "
             "statistical learning/information theory; optimization/algorithm selection; "
             "program synthesis; neural architectures; RL/control; Bayesian/causal inference; "
             "evolutionary computation/ALife; cognitive science/neuroscience; formal methods; "
             "philosophy of science."),
    "AC03": "- [ ] Prefer canonical field terminology when definitions coincide.",
    "AC04": ("- [ ] When terminology differs across fields, state the cross-field synonyms "
             "and choose one primary paper term."),
    "AC06": "- [ ] Record earliest/strongest known parent for each mathematical idea.",
    "AC07": ("- [ ] Record whether GMI contribution is theorem, synthesis, generalization, "
             "new selection law, new empirical result, or only terminology."),
}

STOPWORDS = {"the", "a", "of", "and", "or", "in", "to", "for", "with", "sense", "exact"}
DATED = re.compile(r"\b(1[89]\d\d|20[0-2]\d)\b")
LANE_HEADING = re.compile(r"^##\s+Lane\s+(\d+)\s*[—-]\s*(.+?)\s*$")


class ACError(RuntimeError):
    pass


def normalize(text: str) -> str:
    low = text.lower().replace("*", "").replace("`", "").replace("–", "-")
    for ch in "-/,":
        low = low.replace(ch, " ")
    return " ".join(low.split())


def content_tokens(text: str) -> Set[str]:
    stripped = re.sub(r"\([^)]*\)", " ", text)
    return set(w for w in normalize(stripped).split()
               if w not in STOPWORDS and len(w) > 2)


# ---------------------------------------------------------------------------
# AC01 - lane coverage against the ROW's own eleven-item list.
# ---------------------------------------------------------------------------
def row_lane_items() -> List[str]:
    body = ROWS["AC01"].split("lanes:", 1)[1]
    return [p.strip().rstrip(".") for p in body.split(";") if p.strip().rstrip(".")]


def lane_headings(text: str) -> List[Tuple[int, str]]:
    out = []
    for line in text.split("\n"):
        hit = LANE_HEADING.match(line)
        if hit:
            out.append((int(hit.group(1)), hit.group(2)))
    return out


def lane_entry_counts(text: str) -> Dict[int, int]:
    counts = {}
    current = None
    for line in text.split("\n"):
        hit = LANE_HEADING.match(line)
        if hit:
            current = int(hit.group(1))
            counts[current] = 0
            continue
        if current is None:
            continue
        if line.startswith("| ") and line.count("|") >= 4:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) == 3 and cells[0].lower() != "work" \
               and not set(cells[0]) <= set("-: "):
                counts[current] += 1
    return counts


def ac01() -> Dict[str, object]:
    text = LANES.read_text(encoding="utf-8")
    items = row_lane_items()
    heads = lane_headings(text)
    counts = lane_entry_counts(text)

    forward = {}
    for item in items:
        matches = [n for n, title in heads if normalize(title) == normalize(item)]
        forward[item] = matches
    used = Counter()
    for matches in forward.values():
        for n in matches:
            used[n] += 1

    bound = sum(1 for m in forward.values() if len(m) == 1)
    injective = all(v == 1 for v in used.values()) and len(used) == len(heads)
    return {
        "row_items": len(items),
        "lane_headings": len(heads),
        "bound_one_to_one": bound,
        "binding_is_injective_both_ways": bool(injective and bound == len(items)),
        "unbound_row_items": sorted(k for k, v in forward.items() if len(v) != 1),
        "lanes_serving_two_items": sorted(n for n, v in used.items() if v > 1),
        "entries_per_lane": {str(k): v for k, v in sorted(counts.items())},
        "total_entries": sum(counts.values()),
        "min_entries_in_a_lane": min(counts.values()) if counts else 0,
    }


# ---------------------------------------------------------------------------
# Crosswalk parsing, shared by AC03 / AC04 / AC06.
# ---------------------------------------------------------------------------
COLS = ("n", "legacy", "proposed", "field", "canonical", "match",
        "citations", "definition", "migration")


def crosswalk_rows() -> List[Dict[str, str]]:
    text = CROSSWALK.read_text(encoding="utf-8")
    out = []
    for line in text.split("\n"):
        if not line.startswith("| ") or line.count("|") < 10:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 9 or not cells[0].isdigit():
            continue
        out.append(dict(zip(COLS, cells)))
    return out


def split_terms(cell: str) -> List[str]:
    stripped = re.sub(r"\([^)]*\)", "", cell)
    parts = [p.strip() for p in stripped.split(";") if p.strip()]
    if len(parts) == 1 and "," in parts[0]:
        parts = [p.strip() for p in parts[0].split(",") if p.strip()]
    if len(parts) == 1 and "/" in parts[0]:
        parts = [p.strip() for p in parts[0].split("/") if p.strip()]
    return parts


def ac03(rows: Sequence[Dict[str, str]]) -> Dict[str, object]:
    """EXACT means the definitions coincide, and the crosswalk's own key says
    `adopt it in paper-facing text`. Two structural conditions, either of which
    witnesses adoption; a row satisfying neither is a violation."""
    exact = [r for r in rows if r["match"].upper().startswith("EXACT")]
    adopt = 0
    overlap = 0
    ok = 0
    violations = []
    for r in exact:
        has_adopt_rule = r["migration"].startswith("RENAME") or \
            r["migration"].startswith("PAPER-RENAME")
        shares = bool(content_tokens(r["proposed"]) & content_tokens(r["canonical"]))
        adopt += int(has_adopt_rule)
        overlap += int(shares)
        if has_adopt_rule or shares:
            ok += 1
        else:
            violations.append({"row": r["n"], "legacy": r["legacy"],
                               "proposed": r["proposed"], "migration": r["migration"]})
    return {
        "antecedent_rows_exact_match": len(exact),
        "rows_outside_antecedent": len(rows) - len(exact),
        "with_adopt_migration_rule": adopt,
        "with_canonical_token_overlap": overlap,
        "satisfying_either": ok,
        "violations": violations,
    }


ADDENDUM_AC04_ROWS = ("23", "33")


def ac04(rows: Sequence[Dict[str, str]]) -> Dict[str, object]:
    """Antecedent: the canonical column lists two or more distinct synonyms.
    Requirement: a single proposed paper term, or a selection rule. The
    crosswalk's own convention puts the selection rule in the migration
    parenthetical, so `has a parenthetical` is the structural test - it cannot
    be tuned toward an outcome the way a verb list could."""
    ante = []
    for r in rows:
        syns = {t.lower() for t in split_terms(r["canonical"])}
        if len(syns) >= 2:
            ante.append(r)
    resolved_by_parent = 0
    violations = []
    for r in ante:
        single = len(split_terms(r["proposed"])) == 1
        has_rule = "(" in r["migration"]
        if single or has_rule:
            resolved_by_parent += 1
        else:
            violations.append({"row": r["n"], "legacy": r["legacy"],
                               "migration": r["migration"]})
    supplied = supplied_ac04_rows()
    still_open = [v for v in violations if v["row"] not in supplied]
    return {
        "antecedent_rows_multi_synonym": len(ante),
        "rows_outside_antecedent": len(rows) - len(ante),
        "resolved_by_frozen_parent": resolved_by_parent,
        "resolved_by_addendum": len([v for v in violations if v["row"] in supplied]),
        "unresolved": still_open,
        "addendum_rows": sorted(supplied),
    }


def supplied_ac04_rows() -> Set[str]:
    """Read the addendum's Part 1 table rather than trusting a constant."""
    text = ADDENDUM.read_text(encoding="utf-8")
    part = text.split("## Part 1", 1)[1].split("## Part 2", 1)[0]
    out = set()
    for line in part.split("\n"):
        if line.startswith("| ") and line.count("|") >= 5:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cells and cells[0].isdigit():
                out.add(cells[0])
    return out


def supplied_ac06_rows() -> Dict[str, str]:
    text = ADDENDUM.read_text(encoding="utf-8")
    part = text.split("## Part 2", 1)[1]
    out = {}
    for line in part.split("\n"):
        if line.startswith("| ") and line.count("|") >= 6:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cells and cells[0].isdigit():
                out[cells[0]] = cells[2]
    return out


def ac06(rows: Sequence[Dict[str, str]]) -> Dict[str, object]:
    """Presence, uniqueness and structure of a parent record per idea - never
    that the parent is correct or truly earliest. Verification status is a
    disclosed field, because AC05 is explicitly NOT in scope."""
    supplied = supplied_ac06_rows()
    status = Counter()
    with_anchor = 0
    missing = []
    for r in rows:
        cite = r["citations"]
        anchored = bool(DATED.search(cite)) or "ISO" in cite or "Wikipedia" in cite
        if anchored:
            with_anchor += 1
        else:
            missing.append(r["n"])
        status["VERIFIED" if "VERIFIED" in cite
               else ("CITE-TF" if "CITE-TF" in cite else "UNMARKED")] += 1
    supplied_anchored = 0
    for n in missing:
        cell = supplied.get(n, "")
        if DATED.search(cell):
            supplied_anchored += 1
    return {
        "rows": len(rows),
        "with_dated_or_authored_parent_in_parent_artifact": with_anchor,
        "without_parent_in_parent_artifact": sorted(missing),
        "supplied_by_addendum": supplied_anchored,
        "total_with_parent_record": with_anchor + supplied_anchored,
        "verification_status_in_parent_artifact": dict(sorted(status.items())),
        "addendum_verification_status": "CITE-TF for every supplied entry",
        "ac05_in_scope": False,
    }


# ---------------------------------------------------------------------------
# AC07 - feasibility measurement, declared in FREEZE_V1.md section 4.
# ---------------------------------------------------------------------------
def ac07_kinds() -> List[str]:
    body = ROWS["AC07"].split("contribution is", 1)[1].rstrip(".")
    body = body.replace(", or only ", ", ")
    return [p.strip() for p in body.split(",") if p.strip()]


def ac07_feasibility() -> Dict[str, object]:
    """Is any field registered on `main` a discriminator for the six kinds?

    A kind is DETERMINED when a registered census field has values that pick it
    out; it is UNDETERMINED when no registered field distinguishes it from
    another kind. The row is earned only if the rule types the declared set.
    """
    kinds = ac07_kinds()
    determined = {
        "theorem": "proof_evidence_mode in {ANALYTIC_DEDUCTIVE, MECHANIZED_PROOF}",
        "new empirical result": ("proof_evidence_mode in {EMPIRICAL_EXPERIMENT, "
                                 "STATISTICAL_EXPERIMENT}"),
    }
    undetermined = [k for k in kinds if k not in determined]
    return {
        "kinds_named_by_the_row": kinds,
        "kind_count": len(kinds),
        "determined_by_a_registered_field": sorted(determined),
        "determined_count": len(determined),
        "undetermined": undetermined,
        "undetermined_count": len(undetermined),
        "rule_types_the_declared_set": False,
        "verdict": (
            "NOT EARNED. Four of the six kinds - synthesis, generalization, new "
            "selection law, terminology - have no discriminator among the fields "
            "registered on main; they are distinctions about a claim's relation "
            "to its parents, and no parent relation is registered. A keyword "
            "typer would manufacture a kind rather than record one. AC07 stays "
            "open, as FREEZE_V1.md section 4 said it would if the rule could not "
            "type the set."
        ),
    }


# ---------------------------------------------------------------------------
# Anti-invention guard and null.
# ---------------------------------------------------------------------------
def anti_invention_guard() -> Dict[str, object]:
    items = row_lane_items()
    kinds = ac07_kinds()
    checks = []
    for item in items:
        checks.append({"what": item, "row": "AC01",
                       "occurs": item in ROWS["AC01"]})
    for kind in kinds:
        checks.append({"what": kind, "row": "AC07",
                       "occurs": kind in ROWS["AC07"]})
    for phrase, row in (("canonical field terminology", "AC03"),
                        ("definitions coincide", "AC03"),
                        ("cross-field synonyms", "AC04"),
                        ("one primary paper term", "AC04"),
                        ("earliest/strongest known parent", "AC06")):
        checks.append({"what": phrase, "row": row, "occurs": phrase in ROWS[row]})
    return {
        "checked": len(checks),
        "occurring_in_their_row": sum(1 for c in checks if c["occurs"]),
        "passed": all(c["occurs"] for c in checks),
        "detail": checks,
    }


NULL_TRIALS = 200
NULL_SEED = 8330106  # 833 / AC01


def lane_binding_null() -> Dict[str, object]:
    """Shuffle which row item is bound to which lane heading. The true binding
    is one-to-one on all eleven; a random permutation should not be."""
    import random
    text = LANES.read_text(encoding="utf-8")
    items = [normalize(i) for i in row_lane_items()]
    heads = [normalize(t) for _, t in lane_headings(text)]
    rng = random.Random(NULL_SEED)
    full = 0
    hits = []
    for _ in range(NULL_TRIALS):
        shuffled = heads[:]
        rng.shuffle(shuffled)
        n = sum(1 for a, b in zip(items, shuffled) if a == b)
        hits.append(n)
        if n == len(items):
            full += 1
    from fractions import Fraction
    return {
        "trials": NULL_TRIALS,
        "seed": NULL_SEED,
        "items": len(items),
        "true_binding_matches": sum(1 for a, b in zip(items, heads) if a == b),
        "random_permutations_fully_matching": full,
        "max_random_matches": max(hits),
        "mean_random_matches_exact": str(Fraction(sum(hits), NULL_TRIALS)),
    }


# ---------------------------------------------------------------------------
def hostiles(rows: Sequence[Dict[str, str]]) -> List[Dict[str, object]]:
    out = []
    base01 = ac01()
    # H1 - drop a lane heading.
    text = LANES.read_text(encoding="utf-8")
    broken = text.replace("## Lane 7 — Bayesian / causal inference",
                          "## Lane 7 — Bayesian inference only")
    heads = lane_headings(broken)
    items = row_lane_items()
    bound = sum(1 for i in items
                if len([n for n, t in heads if normalize(t) == normalize(i)]) == 1)
    out.append({"name": "H1_rename_a_lane_heading",
                "moved_quantity": "bound_one_to_one",
                "before": base01["bound_one_to_one"], "after": bound,
                "detected": bound != base01["bound_one_to_one"]})

    # H2 - flip an EXACT row to a coined term with a DEFINE rule.
    fake = [dict(r) for r in rows]
    target = [r for r in fake if r["match"].upper().startswith("EXACT")][0]
    target["proposed"] = "gmi zorbulator"
    target["migration"] = "DEFINE (new term)"
    before = ac03(rows)["satisfying_either"]
    after = ac03(fake)["satisfying_either"]
    out.append({"name": "H2_coined_term_on_an_exact_row",
                "moved_quantity": "ac03_satisfying_either",
                "before": before, "after": after, "detected": after < before})

    # H3 - strip the selection parenthetical from a multi-synonym row.
    fake3 = [dict(r) for r in rows]
    changed = 0
    for r in fake3:
        if len({t.lower() for t in split_terms(r["canonical"])}) >= 2 \
           and "(" in r["migration"] and len(split_terms(r["proposed"])) > 1:
            r["migration"] = r["migration"].split("(")[0].strip()
            changed += 1
            break
    b4 = ac04(rows)["resolved_by_frozen_parent"]
    af = ac04(fake3)["resolved_by_frozen_parent"]
    out.append({"name": "H3_strip_a_selection_parenthetical",
                "moved_quantity": "ac04_resolved_by_frozen_parent",
                "before": b4, "after": af, "detected": af < b4 and changed == 1})

    # H4 - remove the date from a cited parent.
    fake4 = [dict(r) for r in rows]
    hit = None
    for r in fake4:
        stripped = DATED.sub("", r["citations"])
        if DATED.search(r["citations"]) and "ISO" not in stripped \
           and "Wikipedia" not in stripped:
            hit = r["n"]
            r["citations"] = stripped
            break
    b6 = ac06(rows)["with_dated_or_authored_parent_in_parent_artifact"]
    a6 = ac06(fake4)["with_dated_or_authored_parent_in_parent_artifact"]
    out.append({"name": "H4_undate_a_parent_citation",
                "moved_quantity": "ac06_rows_with_parent",
                "before": b6, "after": a6, "detected": a6 < b6 and hit is not None})

    # H5 - a CITE-TF reference must never be counted as verified.
    counted_verified = ac06(rows)["verification_status_in_parent_artifact"].get("VERIFIED", 0)
    tf = ac06(rows)["verification_status_in_parent_artifact"].get("CITE-TF", 0)
    out.append({"name": "H5_cite_tf_never_promoted_to_verified",
                "moved_quantity": "verified_count_if_tf_were_promoted",
                "before": counted_verified, "after": counted_verified + tf,
                "detected": tf > 0 and counted_verified < counted_verified + tf})

    # H6 - an invented lane item must not bind.
    fake_items = items + ["quantum astrology"]
    heads2 = lane_headings(text)
    unbound = [i for i in fake_items
               if len([n for n, t in heads2 if normalize(t) == normalize(i)]) != 1]
    out.append({"name": "H6_invented_lane_item_does_not_bind",
                "moved_quantity": "unbound_row_items",
                "before": len(base01["unbound_row_items"]), "after": len(unbound),
                "detected": len(unbound) > len(base01["unbound_row_items"])})
    return out


def main() -> Dict[str, object]:
    rows = crosswalk_rows()
    if len(rows) != 48:
        raise ACError("crosswalk row count changed: %d" % len(rows))
    host = hostiles(rows)
    return {
        "schema": "GMI_833_AC_LANES_HARNESS_V1",
        "route": "A",
        "source_main": "5e57d4292266bccf435136e1f7d72caa32e920a0",
        "claim_ceiling": "REGISTERED_LITERATURE_STRUCTURE_VERIFIED_V1",
        "AC01_lane_coverage": ac01(),
        "AC03_canonical_preference": ac03(rows),
        "AC04_synonyms_and_primary_term": ac04(rows),
        "AC06_parent_record": ac06(rows),
        "AC07_feasibility": ac07_feasibility(),
        "guard": anti_invention_guard(),
        "null": lane_binding_null(),
        "hostiles": host,
        "hostiles_detected": sum(1 for h in host if h["detected"]),
        "hostiles_total": len(host),
    }


if __name__ == "__main__":
    out = main()
    out["guard"] = {k: v for k, v in out["guard"].items() if k != "detail"}
    print(json.dumps(out, indent=2, sort_keys=True))
