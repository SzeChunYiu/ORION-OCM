"""Versioned data-only unary Boolean semantics; supplied engineering scope."""
import hashlib
import json
import re

SCHEMA = "ocm.unary-task.v1"
RESULT_SCHEMA = "ocm.unary-result.v1"
MAX_PREDICATES, MAX_PREMISES, MAX_NODES, MAX_DEPTH = 4, 32, 512, 16
MAX_TEXT_BYTES = 16384
KINDS = ("every", "no", "some", "not_every")
RESERVED = frozenset(("every", "no", "some", "not", "and", "or", "is", "query"))
COUNTERS = ("expression_nodes", "predicate_region_tests", "cache_hits", "cache_misses", "mask_operations",
            "constraints_checked", "satisfiability_checks", "witness_selections")
NAME = re.compile(r"[A-Za-z][A-Za-z0-9_]{0,31}\Z")


class InputRefused(ValueError):
    """Malformed or outside the registered input fragment; no logical verdict."""


def fields(value, expected):
    if (type(value) is not dict or any(type(k) is not str for k in value)
            or set(value) != set(expected)):
        raise InputRefused("INVALID_FIELDS")


def predicate_name(value):
    if type(value) is not str or NAME.fullmatch(value) is None or value in RESERVED:
        raise InputRefused("INVALID_PREDICATE_NAME")
    return value


def predicate_registry(value):
    if type(value) is not list or not 1 <= len(value) <= MAX_PREDICATES:
        raise InputRefused("PREDICATE_BOUND")
    names = [predicate_name(x) for x in value]
    if names != sorted(set(names)):
        raise InputRefused("PREDICATES_MUST_BE_SORTED_UNIQUE")
    return names


def validate_task(value):
    """Return a fully detached, strictly validated task; names are never normalized."""
    fields(value, ("schema", "predicates", "premises", "query"))
    if value["schema"] != SCHEMA or type(value["schema"]) is not str:
        raise InputRefused("UNKNOWN_SCHEMA")
    names = predicate_registry(value["predicates"])
    if type(value["premises"]) is not list or len(value["premises"]) > MAX_PREMISES:
        raise InputRefused("PREMISE_BOUND")
    used, nodes = set(), 0

    def expression(node, depth=0):
        nonlocal nodes
        nodes += 1
        if nodes > MAX_NODES or depth > MAX_DEPTH:
            raise InputRefused("EXPRESSION_BOUND")
        if type(node) is not list or not node or type(node[0]) is not str:
            raise InputRefused("INVALID_EXPRESSION")
        tag = node[0]
        if tag == "pred" and len(node) == 2:
            name = predicate_name(node[1])
            if name not in names:
                raise InputRefused("UNREGISTERED_PREDICATE")
            used.add(name)
            return [tag, name]
        if (tag == "not" and len(node) == 2) or (tag in ("and", "or") and len(node) == 3):
            return [tag, *(expression(x, depth + 1) for x in node[1:])]
        raise InputRefused("INVALID_EXPRESSION")

    def statement(item):
        fields(item, ("kind", "left", "right"))
        if type(item["kind"]) is not str or item["kind"] not in KINDS:
            raise InputRefused("UNKNOWN_QUANTIFIER")
        return {"kind": item["kind"], "left": expression(item["left"]),
                "right": expression(item["right"])}

    premises = [statement(x) for x in value["premises"]]
    query = statement(value["query"])
    if used != set(names):
        raise InputRefused("UNUSED_PREDICATE_REGISTRY_ENTRY")
    return {"schema": SCHEMA, "predicates": names, "premises": premises, "query": query}


def task_digest(value):
    task = validate_task(value)
    raw = json.dumps(task, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(raw).hexdigest()


def negate(statement):
    """Classical negation of one registered quantified statement."""
    kind = dict(every="not_every", not_every="every", some="no", no="some")
    return {"kind": kind[statement["kind"]], "left": statement["left"],
            "right": statement["right"]}
