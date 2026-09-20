"""Exact synthesis in a disclosed Boolean grammar; no family templates."""
from collections.abc import Mapping


def _bit(value):
    if type(value) is not int or value not in (0, 1):
        raise ValueError("input must be integer bit 0 or 1")
    return value


def _fold(ast, leaf, branch):
    """Iterative structural fold; tuple trees only, no Python evaluation."""
    pending, values = [(ast, False)], []
    while pending:
        node, ready = pending.pop()
        if type(node) is str and node in ("x", "y"):
            values.append(leaf(node))
        elif (type(node) is tuple and len(node) == 3
              and type(node[0]) is str and node[0] == "nand"):
            if ready:
                right, left = values.pop(), values.pop()
                values.append(branch(left, right))
            else:
                pending.extend(((node, True), (node[2], False), (node[1], False)))
        else:
            raise ValueError("invalid AST; expected x, y, or ('nand', left, right)")
    return values[0]


def eval_ast(ast, x, y):
    x, y = _bit(x), _bit(y)
    return _fold(ast, lambda name: x if name == "x" else y,
                 lambda left, right: 1 - left * right)


def ast_cost(ast):
    """Unit node count of the unfolded tree; shared tuple references count twice."""
    return _fold(ast, lambda _: 1, lambda left, right: 1 + left + right)


def truth_table(ast):
    """Bit 2*x+y is the response on (x,y); no sampled inputs."""
    return sum(eval_ast(ast, x, y) << (2 * x + y)
               for x in (0, 1) for y in (0, 1))


def swap_inputs(ast):
    return _fold(ast, lambda name: "y" if name == "x" else "x",
                 lambda left, right: ("nand", left, right))


def synthesize(*, terminal_order=("x", "y"), allow_nand=True, stats=None):
    """Semantic dynamic programming until closure; return cheapest witnesses.

    A supplied terminal subset or disabled NAND defines a different grammar.
    Only the default full grammar is claimed complete by validate_certificate.
    Search costs below count operations of this implementation, not physical
    runtime or complete acquisition, validation, compilation and deployment.
    """
    if type(terminal_order) not in (tuple, list) or not terminal_order:
        raise ValueError("terminal_order must be a nonempty sequence")
    if any(type(t) is not str or t not in ("x", "y") for t in terminal_order):
        raise ValueError("unknown terminal")
    if len(set(terminal_order)) != len(terminal_order):
        raise ValueError("duplicate terminal")
    if type(allow_nand) is not bool or (stats is not None and type(stats) is not dict):
        raise ValueError("allow_nand must be bool and stats must be a dict")
    records = {truth_table(t): {"ast": t, "cost": 1} for t in terminal_order}
    measured = {"rounds": 0, "pair_evaluations": 0, "new_semantics": 0,
                "strict_improvements": 0, "terminal_insertions": len(records),
                "saturated": False}
    while True:
        measured["rounds"] += 1
        changed = False
        # Snapshot records makes each round independent of in-round insertions.
        previous = tuple(records.items())
        if allow_nand:
            for f, left in previous:
                for g, right in previous:
                    measured["pair_evaluations"] += 1
                    semantic = 15 ^ (f & g)
                    cost = 1 + left["cost"] + right["cost"]
                    old = records.get(semantic)
                    if old is None or cost < old["cost"]:
                        records[semantic] = {
                            "ast": ("nand", left["ast"], right["ast"]),
                            "cost": cost,
                        }
                        measured["new_semantics" if old is None
                                 else "strict_improvements"] += 1
                        changed = True
        if not changed:
            measured["saturated"] = True
            break
    if stats is not None:
        stats.clear()
        stats.update(measured)
    return records


def validate_certificate(records):
    """Check an exact-minimum certificate for the complete x,y,NAND grammar.

    Pair inequalities bound every finite AST by structural induction; executable
    witnesses attain the bound. The mathematical theorem is in THEORY_V6.md.
    """
    if not isinstance(records, Mapping):
        raise ValueError("certificate must be a mapping")
    if any(type(k) is not int or not 0 <= k < 16 for k in records):
        raise ValueError("invalid semantic key")
    if set(records) != set(range(16)):
        raise ValueError("incomplete semantic certificate")
    for semantic, row in records.items():
        if type(row) is not dict or set(row) != {"ast", "cost"}:
            raise ValueError("invalid witness schema")
        if type(row["cost"]) is not int or row["cost"] < 1:
            raise ValueError("cost must be a positive integer")
        if ast_cost(row["ast"]) != row["cost"]:
            raise ValueError("witness cost mismatch")
        if truth_table(row["ast"]) != semantic:
            raise ValueError("witness semantics mismatch")
    for terminal in ("x", "y"):
        if records[truth_table(terminal)]["cost"] > 1:
            raise ValueError("terminal lower-bound inequality violated")
    for f, left in records.items():
        for g, right in records.items():
            if records[15 ^ (f & g)]["cost"] > 1 + left["cost"] + right["cost"]:
                raise ValueError("composition lower-bound inequality violated")
    return {"functions": len(records), "witness_cases": 4 * len(records),
            "composition_inequalities": len(records) ** 2}
