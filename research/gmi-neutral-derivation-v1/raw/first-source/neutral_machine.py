"""Bounded Boolean machine: exact executable semantics and charged traces."""
from fractions import Fraction
from itertools import product


def inputs(arity):
    if not 1 <= arity <= 16:
        raise ValueError("The registered index field has four bits")
    return tuple(product((0, 1), repeat=arity))


def encode(program):
    kind = program[0]
    if kind == "c" and program[1] in (0, 1) and len(program) == 2:
        return f"{program[1]:03b}0000"
    if kind == "r" and len(program) == 2 and 0 <= program[1] < 16:
        return f"010{program[1]:04b}"
    if kind == "b" and len(program) == 4 and 0 <= program[1] < 16:
        return f"011{program[1]:04b}" + encode(program[2]) + encode(program[3])
    if kind == "i" and len(program) == 4:
        return "1000000" + "".join(encode(p) for p in program[1:])
    raise ValueError("Invalid primitive or parameter")


def execute(program, bits):
    """An eager binary opcode reads both operands; IF executes one arm."""
    kind = program[0]
    if kind == "c":
        return program[1], (("c", program[1]),)
    if kind == "r":
        value = bits[program[1]]
        return value, (("r", program[1], value),)
    if kind == "b":
        left, lt = execute(program[2], bits)
        right, rt = execute(program[3], bits)
        value = (program[1] >> (2 * left + right)) & 1
        return value, lt + rt + (("b", program[1], left, right, value),)
    if kind == "i":
        condition, ct = execute(program[1], bits)
        value, vt = execute(program[2 if condition else 3], bits)
        return value, ct + (("i", condition),) + vt
    raise ValueError("Unknown primitive")


def trace_row(output, events):
    reads = binary = branches = mask = 0
    for event in events:
        if event[0] == "r":
            reads += 1
            mask |= 1 << event[1]
        elif event[0] == "b":
            binary += 1
        elif event[0] == "i":
            branches += 1
    return output, reads, binary, branches, mask


def signature(program, arity):
    encode(program)
    return tuple(trace_row(*execute(program, bits)) for bits in inputs(arity))


def verify_trace(program, bits, claimed_output, claimed_events):
    encode(program)
    actual = execute(program, bits)
    if actual != (claimed_output, tuple(claimed_events)):
        raise ValueError("Trace disagrees with actual primitive execution")


def verify_signature(program, arity, claimed):
    if signature(program, arity) != claimed:
        raise ValueError("Semantic or charged-trace certificate mismatch")


def weights(arity, p):
    p = Fraction(p)
    if not 0 < p < 1:
        raise ValueError("Registered workloads have full support")
    return tuple(p ** sum(x) * (1 - p) ** (arity - sum(x)) for x in inputs(arity))


def objective(sig, node_count, probabilities, prices):
    read, binary, branch, storage = map(Fraction, prices)
    if min(read, binary, branch, storage) < 0:
        raise ValueError("Resource prices must be nonnegative")
    return 7 * node_count * storage + sum(
        (w * (row[1] * read + row[2] * binary + row[3] * branch)
         for row, w in zip(sig, probabilities)), Fraction(0)
    )


def observable_property(sig):
    has_branch = any(row[3] for row in sig)
    has_binary = any(row[2] for row in sig)
    if not has_branch:
        return "EAGER"
    return "MIXED" if has_binary else "CONDITIONAL"
