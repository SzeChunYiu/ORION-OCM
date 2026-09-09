"""One-step ordinary matching of held-out theorems against a parent."""
import sys
from pathlib import Path

from load_inputs import CONSUMER

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(CONSUMER), str(CONSUMER / "donor")]

import p1_syntax as S
import typed_alias as A
import typed_context as TC


def syntax_for(floating, parent):
    types = {h["statement"][1]: h["statement"][0] for h in floating}
    types.update({key: "class" for key in TC.IDS})
    axioms = S.syntax_contracts(parent)

    def syntax(wanted, tokens):
        S.proof(wanted, tokens, types, axioms)
        return True

    return syntax


def screen(query, premises, floating, parent, work):
    syntax = syntax_for(floating, parent)
    try:
        A.ground_guard(query, premises, syntax)
    except (ValueError, KeyError, TypeError, IndexError, RecursionError) as exc:
        return {"status": "UNKNOWN", "reason": str(exc), "aliases": [], "lemma_labels": [],
                "n_aliases": 0, "coverage_complete": False, "unknown_rows": 0}
    answers = []
    unknown = 0
    for row in parent:
        if row.get("statement", [None])[0] != "|-":
            continue
        try:
            if any(h["statement"][0] not in ("wff", "class", "setvar") for h in row["floating"]):
                continue
            for witness in A.applications(row, query, premises, work, syntax):
                answers.append({
                    "kind": "one_logical_assertion",
                    "label": witness["label"],
                    "premise_indices": witness["premise_indices"],
                    "substitution": witness["substitution"],
                })
        except (ValueError, KeyError, TypeError, IndexError, RecursionError):
            unknown += 1
    if answers:
        status = "ALIAS_FOUND_PROOF_READY"
    elif unknown:
        status = "UNKNOWN"
    else:
        status = "SCREENED_NEGATIVE_IN_DOMAIN"
    return {
        "status": status,
        "aliases": answers,
        "n_aliases": len(answers),
        "unknown_rows": unknown,
        "coverage_complete": unknown == 0,
        "lemma_labels": [a["label"] for a in answers if str(a["label"]).startswith("ocm-cut-")],
    }


def screen_family(theorems, parent, work):
    rows = []
    consumed = []
    for theorem in theorems:
        result = screen(
            theorem["statement"],
            [h["statement"] for h in theorem["essential"]],
            theorem["floating"],
            parent,
            work,
        )
        record = {
            "ordinal": theorem["ordinal"],
            "label": theorem["label"],
            "status": result["status"],
            "n_aliases": result["n_aliases"],
            "lemma_labels": result["lemma_labels"],
            "alias_labels": [a["label"] for a in result["aliases"]],
            "coverage_complete": result["coverage_complete"],
            "unknown_rows": result.get("unknown_rows", 0),
        }
        if result.get("reason"):
            record["reason"] = result["reason"]
        rows.append(record)
        consumed.extend(result["lemma_labels"])
    return {
        "theorems": rows,
        "lemma_consumed": bool(consumed),
        "consumed_labels": sorted(set(consumed)),
        "status_counts": _counts(rows),
    }


def _counts(rows):
    out = {}
    for row in rows:
        out[row["status"]] = out.get(row["status"], 0) + 1
    return out
