"""Read-only evaluation prerequisites; no protected run or adoption authority."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction


class CannotCheck(ValueError):
    pass


def identity(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def token(value):
    if type(value) is not str or not value:
        raise CannotCheck("nonempty identity required")
    return value


def sha(value):
    if type(value) is not str or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise CannotCheck("SHA-256 identity required")
    return value


def indexed(rows):
    if type(rows) is not list or not rows:
        raise CannotCheck("nonempty explicit case inventory required")
    result = {}
    for row in rows:
        if type(row) is not dict:
            raise CannotCheck("case must be an object")
        try:
            key = tuple(token(row[k]) for k in ("lifetime", "family", "case"))
        except KeyError as exc:
            raise CannotCheck("missing case identity") from exc
        if key in result:
            raise CannotCheck("duplicate case identity")
        result[key] = row
    return result


def match_cases(left, right):
    """Compare declared inputs, rubric, order, information and resource ceilings.

    Identical declarations do not authenticate actual exposure or prove that the
    chosen parent is strongest. Outcome payloads are deliberately not inspected.
    """
    a, b = indexed(left), indexed(right)
    if set(a) != set(b):
        raise CannotCheck("unmatched case inventories; observations cannot be padded or dropped")
    fields = ("task_sha256", "rubric_sha256", "information_sha256", "channel_sha256")
    for key in a:
        try:
            for field in fields:
                if sha(a[key][field]) != sha(b[key][field]):
                    raise CannotCheck("case binding differs: " + field)
            for row in (a[key], b[key]):
                if type(row["order"]) is not int or row["order"] < 0:
                    raise CannotCheck("explicit nonnegative order required")
                budget = row["budget"]
                if type(budget) is not dict or not budget:
                    raise CannotCheck("named resource ceilings required")
                for name, amount in budget.items():
                    token(name)
                    if type(amount) is not int or amount < 0:
                        raise CannotCheck("resource ceiling must be a nonnegative integer")
            if a[key]["budget"] != b[key]["budget"] or a[key]["order"] != b[key]["order"]:
                raise CannotCheck("unmatched order or resource ceilings")
        except KeyError as exc:
            raise CannotCheck("missing case binding") from exc
    for rows in (a, b):
        order_keys = [(key[0], row["order"]) for key, row in rows.items()]
        if len(order_keys) != len(set(order_keys)):
            raise CannotCheck("duplicate order within lifetime")
    return tuple(sorted(a))


def paired_descriptives(left, right, left_results, right_results):
    keys = match_cases(left, right)
    results = [indexed(left_results), indexed(right_results)]
    if any(set(rs) != set(keys) for rs in results):
        raise CannotCheck("missing or extra outcome; cannot impute a score")
    groups = {}
    plans = [indexed(left), indexed(right)]
    for key in keys:
        scores = []
        for plan, result in zip(plans, results):
            record = result[key]
            if record.get("case_binding") != identity(plan[key]):
                raise CannotCheck("outcome does not bind the exact declared case")
            if record.get("status") != "OBSERVED" or type(record.get("success")) is not bool:
                raise CannotCheck("undecided or nonboolean outcome cannot become a score")
            scores.append(int(record["success"]))
        groups.setdefault(key[:2], []).append(scores)
    rows = []
    for (lifetime, family), scores in sorted(groups.items()):
        n = len(scores)
        a, b = (Fraction(sum(x[i] for x in scores), n) for i in (0, 1))
        rows.append({"lifetime": lifetime, "family": family, "paired_cases": n,
                     "ocm": str(a), "parent": str(b), "difference": str(a-b)})
    return {"status": "COMPLETE_PAIRED_DESCRIPTIVES", "rows": rows,
            "unit": "lifetime", "independence": "NOT_ESTABLISHED_BY_CASE_IDENTITIES",
            "scientific_terminal": "CANNOT_CHECK_PROTECTED_EVALUATION_AND_PARENT_EVIDENCE"}


def profile(value):
    if type(value) is not list or any(type(w) is not list for w in value):
        raise CannotCheck("explicit finite support family required")
    return tuple(frozenset(token(e) for e in w) for w in value)


def expected_liveness(lower, upper, revoked):
    """Existing finite warrant-interval semantics; roots are evaluator-supplied.

    Supports must already include the registered dependency and nogood checks.
    This function neither discovers hidden supports nor authenticates evidence.
    """
    lo, up = profile(lower), profile(upper)
    if type(revoked) is not list:
        raise CannotCheck("explicit revocation identities required")
    dead = frozenset(token(e) for e in revoked)
    if not all(any(v <= w for v in up) for w in lo):
        raise CannotCheck("lower support does not imply upper support")
    if any(not w & dead for w in lo):
        return "LIVE"
    if any(not w & dead for w in up):
        return "UNKNOWN"
    return "DEAD"


def grade_lifecycle(lower, upper, revoked, observed):
    """Grade the registered query without assuming a fresh or exclusive lesson.

    Existing live alternative support must survive. If lower support disappears
    while upper closure is incomplete, UNKNOWN is the expected state. Answer
    wording/semantic correspondence remains a separate protected rubric.
    """
    if observed not in ("LIVE", "UNKNOWN", "DEAD"):
        raise CannotCheck("missing/invalid observed lifecycle state")
    expected = expected_liveness(lower, upper, revoked)
    return {"expected": expected, "observed": observed, "success": observed == expected}


def check_self_change_binding(record):
    """Consistency preflight for exact targets and prior/candidate identities.

    This is not an assurance or adoption decision; receipt issuer legitimacy,
    hidden test custody and strongest-parent adequacy remain external checks.
    """
    try:
        target = token(record["target"])
        if token(record["assurance_target"]) != target:
            raise CannotCheck("assurance target differs from proposal target")
        incumbent = sha(record["components"][target])
        if sha(record["predecessor"]) != incumbent or sha(record["incumbent"]) != incumbent:
            raise CannotCheck("wrong exact predecessor/incumbent binding")
        if sha(record["candidate"]) != sha(record["assurance_subject"]):
            raise CannotCheck("assurance belongs to a different candidate")
        for k in ("source_sha256", "scenario_sha256", "preservation_sha256",
                  "proposal_sha256", "parent_sha256", "adoption_receipt_sha256"):
            sha(record[k])
        if token(record["candidate_channel"]) != token(record["parent_channel"]):
            raise CannotCheck("parent lacks the same candidate channel")
    except (KeyError, TypeError) as exc:
        raise CannotCheck("missing self-change binding") from exc
    return {"status": "BINDINGS_CONSISTENT", "adoption_authorized": False,
            "assurance_validity": "EXTERNAL_VERIFICATION_REQUIRED"}
