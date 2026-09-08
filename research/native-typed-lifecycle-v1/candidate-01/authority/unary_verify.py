"""Independent direct AST/model certificate checking; never imports the solver."""
from unary_contract import COUNTERS, InputRefused, RESULT_SCHEMA, fields, task_digest, validate_task


def _expression(expr, assignment):
    if expr[0] == "pred":
        return assignment[expr[1]]
    if expr[0] == "not":
        return not _expression(expr[1], assignment)
    left, right = _expression(expr[1], assignment), _expression(expr[2], assignment)
    return left and right if expr[0] == "and" else left or right


def _holds(statement, world):
    pairs = [(_expression(statement["left"], a), _expression(statement["right"], a)) for a in world]
    kind = statement["kind"]
    if kind == "every":
        return all(not a or b for a, b in pairs)
    if kind == "no":
        return all(not (a and b) for a, b in pairs)
    if kind == "some":
        return any(a and b for a, b in pairs)
    return any(a and not b for a, b in pairs)


def _region_condition(statement, assignment):
    left = _expression(statement["left"], assignment)
    right = _expression(statement["right"], assignment)
    return left and (not right if statement["kind"] in ("every", "not_every") else right)


def _universal(statement, desired):
    return (statement["kind"] in ("every", "no")) == desired


def _certificate(names, requirements, cert):
    if type(cert) is not dict or type(cert.get("kind")) is not str:
        return False
    count = 1 << len(names)
    def assignment(region):
        return {name: bool(region & (1 << i)) for i, name in enumerate(names)}
    if cert["kind"] == "model":
        fields(cert, ("kind", "world"))
        world = cert["world"]
        if (type(world) is not list or not 1 <= len(world) <= count
                or any(type(x) is not int or not 0 <= x < count for x in world)
                or world != sorted(set(world))):
            return False
        actual = [assignment(x) for x in world]
        return all(_holds(stmt, actual) == desired for stmt, desired in requirements)
    if cert["kind"] != "unsat":
        return False
    fields(cert, ("kind", "obligation", "cover"))
    obligation, cover = cert["obligation"], cert["cover"]
    if (type(cover) is not list or len(cover) > len(requirements)
            or any(type(x) is not int or not 0 <= x < len(requirements) for x in cover)
            or cover != sorted(set(cover))):
        return False
    if any(not _universal(*requirements[i]) for i in cover):
        return False
    if type(obligation) is str and obligation == "domain":
        relevant = lambda a: True
    elif type(obligation) is int and 0 <= obligation < len(requirements):
        stmt, desired = requirements[obligation]
        if _universal(stmt, desired):
            return False
        relevant = lambda a: _region_condition(stmt, a)
    else:
        return False
    for region in range(count):
        a = assignment(region)
        if relevant(a) and not any(_region_condition(requirements[i][0], a) for i in cover):
            return False
    return True


def verify_result(value, result):
    """Boolean acceptance of exact semantic certificates, not authenticity of counters."""
    try:
        task = validate_task(value)
        fields(result, ("schema", "task_sha256", "status", "premises", "query_true",
                        "query_false", "counters"))
        if any(type(result[key]) is not str for key in ("schema", "task_sha256", "status")):
            return False
        if result["schema"] != RESULT_SCHEMA or result["task_sha256"] != task_digest(task):
            return False
        fields(result["counters"], COUNTERS)
        if any(type(x) is not int or x < 0 for x in result["counters"].values()):
            return False
        names = task["predicates"]
        base = [(stmt, True) for stmt in task["premises"]]
        if not _certificate(names, base, result["premises"]):
            return False
        if result["premises"]["kind"] == "unsat":
            return (result["status"] == "INCONSISTENT" and result["query_true"] is None
                    and result["query_false"] is None)
        yes, no = result["query_true"], result["query_false"]
        if (not _certificate(names, base + [(task["query"], True)], yes)
                or not _certificate(names, base + [(task["query"], False)], no)):
            return False
        pattern = (yes["kind"], no["kind"])
        expected = {("model", "unsat"): "ENTAILED", ("unsat", "model"): "CONTRADICTED",
                    ("model", "model"): "UNKNOWN"}.get(pattern)
        return expected is not None and result["status"] == expected
    except (InputRefused, KeyError, TypeError, ValueError, RecursionError):
        return False
