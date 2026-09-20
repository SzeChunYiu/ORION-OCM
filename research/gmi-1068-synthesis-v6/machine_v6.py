"""A separate finite stack language and compiler for the disclosed NAND ASTs."""


def _bit(value):
    if type(value) is not int or value not in (0, 1):
        raise ValueError("input and stack cells must be integer bits")
    return value


def compile_ast(ast):
    """Postorder compiler. For every initial S, execution returns S + (value,)."""
    pending, code = [(ast, False)], []
    while pending:
        node, ready = pending.pop()
        if type(node) is str and node in ("x", "y"):
            code.append("PUSH_X" if node == "x" else "PUSH_Y")
        elif (type(node) is tuple and len(node) == 3
              and type(node[0]) is str and node[0] == "nand"):
            if ready:
                code.append("NAND")
            else:
                pending.extend(((node, True), (node[2], False), (node[1], False)))
        else:
            raise ValueError("invalid source AST")
    return tuple(code)


def execute(code, x, y, stack=()):
    """Execute a complete finite instruction sequence, stack bottom to top.

    This is an arbitrary-program interface: empty code is valid and preserves
    the initial stack. Use run_program when exactly one result is required.
    Inputs are copied, so malformed code never partially mutates caller state.
    """
    x, y = _bit(x), _bit(y)
    if type(code) not in (tuple, list) or type(stack) not in (tuple, list):
        raise ValueError("code and stack must be finite sequences")
    if any(type(op) is not str or op not in ("PUSH_X", "PUSH_Y", "NAND")
           for op in code):
        raise ValueError("invalid opcode")
    cells = [_bit(cell) for cell in stack]
    for op in code:
        if op == "PUSH_X":
            cells.append(x)
        elif op == "PUSH_Y":
            cells.append(y)
        else:
            if len(cells) < 2:
                raise ValueError("stack underflow")
            right, left = cells.pop(), cells.pop()
            cells.append(0 if left == 1 and right == 1 else 1)
    return tuple(cells)


def run_program(code, x, y):
    result = execute(code, x, y)
    if len(result) != 1:
        raise ValueError("standalone expression program needs exactly one result")
    return result[0]
