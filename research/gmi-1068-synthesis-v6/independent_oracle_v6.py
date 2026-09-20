"""Independent cost-layer, operational and certificate oracles (no core imports)."""
from itertools import product


ASSIGNMENTS = tuple(product((0, 1), repeat=2))


def source(ast, x, y):
    if ast == "x":
        return x
    if ast == "y":
        return y
    if not isinstance(ast, tuple) or len(ast) != 3 or ast[0] != "nand":
        raise ValueError("invalid oracle AST")
    return int(not (source(ast[1], x, y) and source(ast[2], x, y)))


def measured_cost(ast, load_cost=1, nand_cost=1):
    if ast in ("x", "y"):
        return load_cost
    if not isinstance(ast, tuple) or len(ast) != 3 or ast[0] != "nand":
        raise ValueError("invalid oracle AST")
    return nand_cost + measured_cost(ast[1], load_cost, nand_cost) + measured_cost(
        ast[2], load_cost, nand_cost)


def pack(values):
    return sum(value * (2 ** index) for index, value in enumerate(values))


def cost_layers(max_cost, terminals=("x", "y"), allow_nand=True,
                load_cost=1, nand_cost=1):
    """Increasing-cost discovery; substitution of cheaper equal semantics is safe.

    Unlike relaxation, a semantic value is retained only at its first cost.
    Full four-case truth tuples are the internal states, not bitwise operations.
    """
    layers = {cost: {} for cost in range(1, max_cost + 1)}
    seen = {}
    for cost in layers:
        candidates = {}
        if cost == load_cost:
            for terminal in terminals:
                semantic = tuple(source(terminal, x, y) for x, y in ASSIGNMENTS)
                candidates[semantic] = terminal
        if allow_nand:
            for left_cost in range(1, cost):
                right_cost = cost - nand_cost - left_cost
                if right_cost not in layers:
                    continue
                for left, left_ast in layers[left_cost].items():
                    for right, right_ast in layers[right_cost].items():
                        table = tuple(int(not (a and b)) for a, b in zip(left, right))
                        candidates.setdefault(table, ("nand", left_ast, right_ast))
        for semantic, ast in candidates.items():
            if semantic not in seen:
                seen[semantic] = {"ast": ast, "cost": cost}
                layers[cost][semantic] = ast
    return {pack(semantic): record for semantic, record in seen.items()}


def stack_execute(code, x, y, stack=()):
    """Independent recursive transition interpreter with an explicit stack tuple."""
    def bit(value):
        if type(value) is not int or value not in (0, 1):
            raise ValueError("not an exact bit")
    bit(x)
    bit(y)
    state = tuple(stack)
    for value in state:
        bit(value)
    for opcode in code:
        if opcode == "PUSH_X":
            state += (x,)
        elif opcode == "PUSH_Y":
            state += (y,)
        elif opcode == "NAND":
            if len(state) < 2:
                raise ValueError("underflow")
            a, b = state[-2:]
            state = state[:-2] + ((0 if a == b == 1 else 1),)
        else:
            raise ValueError("unknown instruction")
    return state


def certificate_is_valid(records):
    """Direct independent witness and all-pairs lower-bound verification."""
    if not isinstance(records, dict) or set(records) != set(range(16)):
        return False
    if any(type(semantic) is not int for semantic in records):
        return False
    try:
        for semantic, record in records.items():
            if type(record["cost"]) is not int or record["cost"] < 1:
                return False
            ast = record["ast"]
            if measured_cost(ast) != record["cost"]:
                return False
            if pack(source(ast, x, y) for x, y in ASSIGNMENTS) != semantic:
                return False
        for terminal in ("x", "y"):
            semantic = pack(source(terminal, x, y) for x, y in ASSIGNMENTS)
            if records[semantic]["cost"] > 1:
                return False
        for left, right in product(records, repeat=2):
            result = pack(int(not ((left // 2 ** i % 2) and (right // 2 ** i % 2)))
                          for i in range(4))
            if records[result]["cost"] > 1 + records[left]["cost"] + records[right]["cost"]:
                return False
    except (KeyError, TypeError, ValueError, IndexError):
        return False
    return True
