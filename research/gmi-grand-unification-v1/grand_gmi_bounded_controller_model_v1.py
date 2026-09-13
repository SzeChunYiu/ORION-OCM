"""Exact finite Moore controllers; binary payloads and product execution."""
from dataclasses import dataclass
from itertools import product


@dataclass(frozen=True)
class Model:
    transitions: tuple
    goals: tuple
    initial: tuple
    actions: int = 1
    observations: int = 1


def width(n):
    return (n - 1).bit_length()


def natural(value):
    return type(value) is int and value >= 0


def validate(model):
    n = len(model.transitions)
    a, o = model.actions, model.observations
    if not n or not natural(a) or not a or not natural(o) or not o:
        raise ValueError("nonempty state/action/observation alphabets required")
    u = len(model.transitions[0])
    if len(model.goals) != n or any(not natural(g) or g >= 1 << a for g in model.goals):
        raise ValueError("one valid terminal-action mask per state required")
    if not model.initial or any(not natural(s) or s >= n for s in model.initial):
        raise ValueError("nonempty valid initial-state register required")
    if tuple(sorted(set(model.initial))) != model.initial:
        raise ValueError("initial states must be distinct and sorted")
    for row in model.transitions:
        if len(row) != u:
            raise ValueError("rectangular transition table required")
        for edge in row:
            if edge is not None and (not isinstance(edge, tuple) or len(edge) != 2
                    or not natural(edge[0]) or edge[0] >= n
                    or not natural(edge[1]) or edge[1] >= o):
                raise ValueError("invalid physical successor/observation")
    return n, u, a, o


def validate_controller(model, controller):
    _, u, a, o = validate(model)
    j = len(controller)
    if not j:
        raise ValueError("at least one controller node required")
    for opcode, successors in controller:
        if not natural(opcode) or opcode >= a + u:
            raise ValueError("invalid opcode")
        if opcode < a:
            if successors != ():
                raise ValueError("terminal successors must be empty")
        elif len(successors) != o or any(not natural(q) or q >= j for q in successors):
            raise ValueError("one valid successor per observation required")


def bits(value, size):
    return format(value, f"0{size}b") if size else ""


def reader(payload):
    if any(b not in "01" for b in payload):
        raise ValueError("binary payload required")
    position = 0
    def read(size):
        nonlocal position
        value = int(payload[position:position+size] or "0", 2)
        position += size
        return value
    return read


def encode_model(model):
    n, u, a, o = validate(model)
    cells = [0 if edge is None else 1 + o*edge[0] + edge[1]
             for row in model.transitions for edge in row]
    return ("".join(bits(v, width(n*o+1)) for v in cells)
            + "".join(bits(g, a) for g in model.goals)
            + bits(sum(1 << s for s in model.initial), n))


def decode_model(payload, n, u, a, o):
    if any(not natural(v) for v in (n, u, a, o)) or not n or not a or not o:
        raise ValueError("invalid dimensions")
    if len(payload) != n*u*width(n*o+1) + n*a + n:
        raise ValueError("wrong model payload length")
    read = reader(payload)
    def edge():
        value = read(width(n*o+1))
        return None if value == 0 else divmod(value-1, o)
    transitions = tuple(tuple(edge() for _ in range(u)) for _ in range(n))
    goals = tuple(read(a) for _ in range(n))
    initial_mask = read(n)
    model = Model(transitions, goals, tuple(s for s in range(n) if initial_mask >> s & 1), a, o)
    validate(model)
    return model


def encode_controller(model, controller):
    validate_controller(model, controller)
    _, u, a, o = validate(model)
    b, k = width(len(controller)), width(a+u)
    return "".join(bits(op, k) + "".join(bits(q, b) for q in (nxt or (0,)*o))
                   for op, nxt in controller)


def decode_controller(payload, model, j):
    _, u, a, o = validate(model)
    if not natural(j) or not j:
        raise ValueError("positive controller size required")
    b, k = width(j), width(a+u)
    if len(payload) != j*(k+o*b):
        raise ValueError("wrong controller payload length")
    read, rows = reader(payload), []
    for _ in range(j):
        op, nxt = read(k), tuple(read(b) for _ in range(o))
        if op < a and any(nxt):
            raise ValueError("noncanonical terminal padding")
        rows.append((op, () if op < a else nxt))
    controller = tuple(rows)
    validate_controller(model, controller)
    return controller


def controllers(model, j):
    _, u, a, o = validate(model)
    if not natural(j) or not j:
        raise ValueError("positive controller size required")
    rows = [(action, ()) for action in range(a)]
    rows += [(a+control, nxt) for control in range(u)
             for nxt in product(range(j), repeat=o)]
    yield from product(rows, repeat=j)


def evaluate(model, controller):
    validate_controller(model, controller)
    runs, inspections, lookups = [], 0, 0
    for initial in model.initial:
        state, node, steps, seen = initial, 0, 0, set()
        while True:
            if (state, node) in seen:
                verdict = "LOOP"
                break
            seen.add((state, node))
            inspections += 1
            opcode, nxt = controller[node]
            if opcode < model.actions:
                verdict = "SUCCESS" if model.goals[state] >> opcode & 1 else "WRONG_TERMINAL"
                break
            lookups += 1
            edge = model.transitions[state][opcode-model.actions]
            if edge is None:
                verdict = "ILLEGAL"
                break
            state, observation = edge
            node = nxt[observation]
            steps += 1
        runs.append((verdict, steps))
    success = all(verdict == "SUCCESS" for verdict, _ in runs)
    profile = None
    if success:
        t = max(steps for _, steps in runs)
        profile = (width(len(controller)), len(encode_controller(model, controller)),
                   len(encode_model(model)), t, 2*t+1)
    return {"success": success, "runs": tuple(runs), "profile": profile,
            "product_pair_inspections": inspections, "physical_transition_lookups": lookups}


def search(model, bound, ceilings=None):
    if not natural(bound) or not bound:
        raise ValueError("finite positive node bound required")
    if ceilings is not None and (len(ceilings) != 5 or any(not natural(v) for v in ceilings)):
        raise ValueError("five finite nonnegative integer ceilings required")
    result = {"candidates": 0, "initial_runs": 0, "product_pair_inspections": 0,
              "physical_transition_lookups": 0, "winners": []}
    for j in range(1, bound+1):
        for controller in controllers(model, j):
            report = evaluate(model, controller)
            result["candidates"] += 1
            result["initial_runs"] += len(model.initial)
            for key in ("product_pair_inspections", "physical_transition_lookups"):
                result[key] += report[key]
            if report["success"] and (ceilings is None or all(x <= y for x, y in zip(report["profile"], ceilings))):
                result["winners"].append((controller, report["profile"]))
    return result
