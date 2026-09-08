"""Research-only certified pure checker calculus for R0A; no runtime integration.

The language contains only bounded read-only predicates over detached candidate
data.  There are no user callbacks or runtime capabilities.  Admission recomputes
a complete certificate, enforces predicate/checker syntax sorts, and evaluation
returns only a registered solve Status.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

from ocm.runtime import solve as SV


SCHEMA = "ocm.r0a.pure-checker.certificate.v1"
LANGUAGE = "ocm.r0a.pure-checker.dsl.v1"
MAX_NODES = 128
MAX_DEPTH = 16
MAX_PATH = 16
MAX_LITERAL_BYTES = 4096
KINDS = {"dict", "list", "tuple", "str", "int", "float", "bool", "none"}
STATUSES = {status.value: status for status in (SV.Status.PASS, SV.Status.FAIL, SV.Status.CANNOT_CHECK)}
PREDICATE_OPS = {"TRUE", "FALSE", "HAS", "TYPE", "EQ", "NOT", "AND", "OR"}
CHECKER_OPS = {"STATUS", "IF"}


class CertificateRejected(ValueError):
    pass


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def _literal_ok(value: Any, active: set[int] | None = None) -> bool:
    """Closed detached literal grammar; no arbitrary objects or mapping subclasses."""
    if value is None or type(value) in (str, int, bool):
        return True
    if type(value) is float:
        return value == value and value not in (float("inf"), float("-inf"))
    if type(value) not in (list, tuple, dict):
        return False
    active = set() if active is None else active
    identity = id(value)
    if identity in active:
        return False
    active.add(identity)
    try:
        if type(value) is dict:
            return all(type(key) is str and _literal_ok(item, active) for key, item in value.items())
        return all(_literal_ok(item, active) for item in value)
    finally:
        active.remove(identity)


def _literal_equal(left: Any, right: Any) -> bool:
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return left.keys() == right.keys() and all(_literal_equal(value, right[key]) for key, value in left.items())
    if type(left) in (list, tuple):
        return len(left) == len(right) and all(_literal_equal(a, b) for a, b in zip(left, right, strict=True))
    if type(left) is float:
        return left.hex() == right.hex()
    return left == right


def _kind(value: Any) -> str | None:
    return {
        dict: "dict", list: "list", tuple: "tuple", str: "str", int: "int",
        float: "float", bool: "bool", type(None): "none",
    }.get(type(value))


def _resolve(candidate: Any, path: Sequence[Any], work: dict[str, int]):
    current = candidate
    for component in path:
        work["path_steps"] += 1
        if type(component) is str and type(current) is dict and component in current:
            current = current[component]
        elif type(component) is int and not isinstance(component, bool) and type(current) in (list, tuple) and 0 <= component < len(current):
            current = current[component]
        else:
            return False, None
    return True, current


def _validate_path(path):
    if type(path) is not list or len(path) > MAX_PATH:
        raise CertificateRejected("invalid or oversized path")
    for component in path:
        if type(component) is str:
            continue
        if type(component) is int and not isinstance(component, bool) and component >= 0:
            continue
        raise CertificateRejected("path components must be string keys or nonnegative integer indices")


def _validate(node, depth, stats, expected_sort):
    if depth > MAX_DEPTH or type(node) is not dict or type(node.get("op")) is not str:
        raise CertificateRejected("malformed or too-deep AST")
    if expected_sort not in ("predicate", "checker"):
        raise AssertionError("invalid validator sort")
    stats["node_count"] += 1
    stats["max_depth"] = max(stats["max_depth"], depth)
    if stats["node_count"] > MAX_NODES:
        raise CertificateRejected("too many AST nodes")
    op = node["op"]
    if expected_sort == "predicate" and op not in PREDICATE_OPS:
        raise CertificateRejected("checker expression used where predicate required")
    if expected_sort == "checker" and op not in CHECKER_OPS:
        raise CertificateRejected("predicate expression used where checker required")

    if op in ("TRUE", "FALSE"):
        if set(node) != {"op"}:
            raise CertificateRejected("unexpected fields")
        return
    if op == "STATUS":
        if set(node) != {"op", "status"} or node["status"] not in STATUSES:
            raise CertificateRejected("invalid status")
        return
    if op in ("HAS", "TYPE", "EQ"):
        expected = {"op", "path"} | ({"kind"} if op == "TYPE" else {"literal"} if op == "EQ" else set())
        if set(node) != expected:
            raise CertificateRejected("unexpected predicate fields")
        _validate_path(node["path"])
        stats["max_path_length"] = max(stats["max_path_length"], len(node["path"]))
        if op == "TYPE" and node["kind"] not in KINDS:
            raise CertificateRejected("invalid type kind")
        if op == "EQ":
            if not _literal_ok(node["literal"]):
                raise CertificateRejected("literal outside detached grammar")
            stats["literal_bytes"] += len(_canonical(node["literal"]))
            if stats["literal_bytes"] > MAX_LITERAL_BYTES:
                raise CertificateRejected("literal budget exceeded")
        return
    if op == "NOT":
        if set(node) != {"op", "arg"}:
            raise CertificateRejected("unexpected NOT fields")
        _validate(node["arg"], depth + 1, stats, "predicate")
        return
    if op in ("AND", "OR"):
        if set(node) != {"op", "left", "right"}:
            raise CertificateRejected("unexpected binary fields")
        _validate(node["left"], depth + 1, stats, "predicate")
        _validate(node["right"], depth + 1, stats, "predicate")
        return
    if op == "IF":
        if set(node) != {"op", "predicate", "then", "else"}:
            raise CertificateRejected("unexpected IF fields")
        _validate(node["predicate"], depth + 1, stats, "predicate")
        _validate(node["then"], depth + 1, stats, "checker")
        _validate(node["else"], depth + 1, stats, "checker")
        return
    raise CertificateRejected("unknown AST opcode")


def issue_certificate(ast: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a bounded pure checker AST and return a recomputable certificate."""
    try:
        detached = json.loads(_canonical(ast))
    except (TypeError, ValueError, UnicodeError) as exc:
        raise CertificateRejected("AST must be canonical JSON data") from exc
    stats = {"node_count": 0, "max_depth": 0, "max_path_length": 0, "literal_bytes": 0}
    _validate(detached, 1, stats, "checker")
    digest = hashlib.sha256(_canonical(detached)).hexdigest()
    return {
        "schema": SCHEMA,
        "language_version": LANGUAGE,
        "ast": detached,
        "ast_sha256": digest,
        **stats,
        "claimed_effects": [],
    }


def verify_certificate(certificate: Mapping[str, Any]) -> dict[str, Any]:
    if type(certificate) is not dict or certificate.get("schema") != SCHEMA or certificate.get("language_version") != LANGUAGE:
        raise CertificateRejected("unexpected certificate schema/language")
    regenerated = issue_certificate(certificate.get("ast"))
    if certificate != regenerated:
        raise CertificateRejected("certificate metadata/hash mismatch")
    return regenerated


def _predicate(node, candidate, work):
    work["ast_nodes"] += 1
    op = node["op"]
    if op == "TRUE":
        return True
    if op == "FALSE":
        return False
    if op in ("HAS", "TYPE", "EQ"):
        found, value = _resolve(candidate, node["path"], work)
        if op == "HAS":
            return found
        if not found:
            return False
        if op == "TYPE":
            return _kind(value) == node["kind"]
        return _literal_equal(value, node["literal"])
    if op == "NOT":
        return not _predicate(node["arg"], candidate, work)
    if op == "AND":
        return _predicate(node["left"], candidate, work) and _predicate(node["right"], candidate, work)
    if op == "OR":
        return _predicate(node["left"], candidate, work) or _predicate(node["right"], candidate, work)
    raise AssertionError("validated checker branch reached predicate evaluator")


def _checker(node, candidate, work):
    work["ast_nodes"] += 1
    if node["op"] == "STATUS":
        return STATUSES[node["status"]]
    if node["op"] == "IF":
        branch = node["then"] if _predicate(node["predicate"], candidate, work) else node["else"]
        return _checker(branch, candidate, work)
    raise AssertionError("validated predicate reached checker evaluator")


def evaluate(certificate: Mapping[str, Any], candidate: Any) -> tuple[SV.Status, dict[str, int]]:
    """Evaluate with no callback/runtime capability; returns exact work counters."""
    cert = verify_certificate(certificate)
    if not _literal_ok(candidate):
        raise CertificateRejected("candidate outside detached data grammar")
    work = {"ast_nodes": 0, "path_steps": 0}
    status = _checker(cert["ast"], candidate, work)
    return status, work


def break_even_horizon(build, maintenance, saving_per_use, overhead_per_use):
    """Smallest integer H satisfying H*s > B+M+H*u, or None if impossible."""
    values = tuple(float(x) for x in (build, maintenance, saving_per_use, overhead_per_use))
    if any(not (x >= 0.0) for x in values):
        raise ValueError("costs must be finite and nonnegative")
    build, maintenance, saving, overhead = values
    if saving <= overhead:
        return None
    fixed = build + maintenance
    return int(fixed // (saving - overhead)) + 1
