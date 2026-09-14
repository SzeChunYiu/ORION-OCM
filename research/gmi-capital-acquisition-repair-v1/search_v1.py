"""Verified acquisition, with all unsuccessful candidates and descendant work paid."""
from itertools import product
from machine_v1 import PRIMITIVES, evaluate, flatten, names, validate


def candidates(alphabet, bound):
    for size in range(1, bound + 1):
        yield from product(alphabet, repeat=size)


def solve(state, examples, bound, ledger, generator=candidates):
    validate(state)
    if type(bound) is not int or bound < 1 or not examples:
        raise ValueError("finite nonempty task register required")
    if any(type(x) is not int or type(y) is not int for x, y in examples):
        raise ValueError("integer task coordinates")
    ledger.add("task_read", 2 * len(examples))
    rows = []
    for body in generator(names(state), bound):
        start = len(ledger.events)
        ledger.add("candidate", 1 + len(body), body=list(body))
        outputs = [evaluate(body, state, x, ledger) for x, _ in examples]
        ledger.add("compare", len(examples), outputs=outputs)
        good = outputs == [y for _, y in examples]
        rows.append({"body": list(body), "outputs": outputs, "pass": good,
                     "events_begin": start, "events_end": len(ledger.events)})
        if good:
            return {"status": "SOLVED", "body": list(body), "rank": len(rows),
                    "candidates": rows}
    return {"status": "EXHAUSTED", "body": None, "rank": None, "candidates": rows}


def verify_primitive(body, examples, ledger):
    if not body or any(op not in PRIMITIVES for op in body):
        raise ValueError("not an independently executable primitive body")
    ledger.add("task_read", 2 * len(examples), purpose="independent_verification")
    # Independent evaluator uses only the two declared primitive operations.
    result = []
    for x, _ in examples:
        y = x
        for op in body:
            ledger.add("dispatch", op=op, purpose="independent_verification")
            y = y + 1 if op == "inc" else y * 2
            ledger.add("arithmetic", op=op, purpose="independent_verification", output=y)
        result.append(y)
    ledger.add("compare", len(examples), outputs=result, purpose="independent_verification")
    if result != [y for _, y in examples]:
        raise ValueError("verification failed")
    return result


def acquire(state, label, examples, bound, ledger, generator=candidates):
    if label in dict(state["library"]) or label in PRIMITIVES:
        raise ValueError("new entry required")
    ledger.add("task_read", 2 * len(examples), purpose="newness")
    initial = [[op, [op]] for op in PRIMITIVES] + state["library"]
    for old_name, old_body in initial:
        outputs = [evaluate(old_body, state, x, ledger) for x, _ in examples]
        ledger.add("compare", len(examples), purpose="newness", name=old_name)
        ledger.add("admission", purpose="newness", name=old_name)
        if outputs == [y for _, y in examples]:
            raise ValueError("target already in the initial response register")
    result = solve(state, examples, bound, ledger, generator)
    if result["status"] != "SOLVED":
        return result
    body = flatten(result["body"], state, ledger)
    verify_primitive(body, examples, ledger)
    ledger.add("admission", 1 + len(body), name=label)
    state["library"].append([label, list(body)])
    state["active"].append(label)
    ledger.add("store", 2, name=label, body=list(body))
    result["stored"] = {"name": label, "body": list(body)}
    return result
