"""Finite explicit machine; no closures, RNG, external cache or implicit library."""
from copy import deepcopy

PRIMITIVES = ("double", "inc")
KINDS = {"task_read", "candidate", "dispatch", "arithmetic", "lookup",
         "compare", "copy_body", "admission", "store", "copy_state", "gate",
         "holding"}


class Ledger:
    def __init__(self):
        self.events = []

    def add(self, kind, quantity=1, **detail):
        if kind not in KINDS or type(quantity) is not int or quantity < 0:
            raise ValueError("invalid declared cost")
        self.events.append({"kind": kind, "quantity": quantity, **detail})

    def record(self):
        return {"cost": sum(e["quantity"] for e in self.events),
                "events": deepcopy(self.events)}


def empty():
    return {"library": [], "active": []}


def validate(state):
    if set(state) != {"library", "active"}:
        raise ValueError("complete state schema")
    names = []
    for name, body in state["library"]:
        if not isinstance(name, str) or name in PRIMITIVES or name in names:
            raise ValueError("ambiguous instruction")
        if not body or any(op not in PRIMITIVES for op in body):
            raise ValueError("only flattened primitive bodies are legal")
        names.append(name)
    if len(set(state["active"])) != len(state["active"]):
        raise ValueError("duplicate active entry")
    if any(x not in names for x in state["active"]):
        raise ValueError("dangling active entry")


def clone(state, ledger):
    validate(state)
    quantity = 1 + len(state["active"]) + sum(1 + len(b) for _, b in state["library"])
    ledger.add("copy_state", quantity)
    return deepcopy(state)


def gate(state, name, enabled, ledger):
    validate(state)
    if type(enabled) is not bool or name not in dict(state["library"]):
        raise ValueError("illegal gate")
    ledger.add("gate", name=name, enabled=enabled)
    active = set(state["active"])
    active.add(name) if enabled else active.discard(name)
    state["active"] = [n for n, _ in state["library"] if n in active]


def names(state):
    validate(state)
    return tuple(n for n, _ in reversed(state["library"]) if n in state["active"]) + PRIMITIVES


def evaluate(ops, state, x, ledger):
    validate(state)
    if type(x) is not int:
        raise ValueError("integer input required")
    for op in ops:
        ledger.add("dispatch", op=op, input=x)
        if op in PRIMITIVES:
            old = x
            x = 2 * x if op == "double" else x + 1
            ledger.add("arithmetic", op=op, input=old, output=x)
        else:
            if op not in state["active"]:
                raise ValueError("inactive or unknown instruction")
            body = dict(state["library"])[op]
            ledger.add("lookup", name=op, body=list(body))
            x = evaluate(body, state, x, ledger)
    return x


def flatten(ops, state, ledger):
    out = []
    for op in ops:
        if op in PRIMITIVES:
            out.append(op)
            ledger.add("copy_body", op=op)
        elif op in state["active"]:
            for primitive in dict(state["library"])[op]:
                out.append(primitive)
                ledger.add("copy_body", op=primitive, via=op)
        else:
            raise ValueError("invalid dependency")
    return tuple(out)


def hold(state, ledger):
    validate(state)
    ledger.add("holding", sum(len(b) for _, b in state["library"]))
