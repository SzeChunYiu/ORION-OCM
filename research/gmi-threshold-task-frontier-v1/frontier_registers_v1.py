"""Registered realizations of the majority-n task, measured in DCR's typed register.

Every candidate is a source string admitted by `typed_program_v1.parse_function`
and executed by `typed_machine_v1.execute`, so its Python-opcode count and its
native obligations are produced by the same instrument that produced the
registered parity-3 facts (11 for the written XOR chain, 39 with four native
obligations for the shared-sum threshold net, 6 with one for `sum(x) & 1`).

A second component is recorded alongside the opcode count: `constant_cells`, the
number of integer cells the realization needs in its constants and its registered
data bindings. It is a count, not a physical memory measurement; the theorem
document states exactly what it is and is not.
"""

import itertools
import sys
from pathlib import Path
from types import CodeType

HERE = Path(__file__).resolve().parent
DCR = HERE.parent / "gmi-delegation-cost-repair-v1"
for _path in (str(DCR), str(HERE)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from typed_machine_v1 import execute                      # noqa: E402
from typed_program_v1 import Program, require             # noqa: E402

SCOPE = (3, 4, 5, 6, 7, 8)


def points(n):
    return tuple(itertools.product((0, 1), repeat=n))


def majority(bits):
    return int(2 * sum(bits) >= len(bits))


def parity(bits):
    return sum(bits) & 1


def names(n):
    return ["v%d" % i for i in range(n)]


def _unpack(n):
    return "    %s = x\n" % ", ".join(names(n))


def _nested_table(n, task):
    def build(prefix):
        if len(prefix) == n:
            return task(prefix)
        return tuple(build(prefix + (bit,)) for bit in (0, 1))
    return build(())


def _dnf_terms(n):
    """All minimal true sets of majority-n: every ceil(n/2)-subset."""
    k = (n + 1) // 2
    return [combo for combo in itertools.combinations(range(n), k)]


def register(n):
    """{candidate name: (Program, declared family, declared structural note)}."""
    require(n in SCOPE, "declared scope is n in %s" % (SCOPE,))
    vs = names(n)
    total = " + ".join(vs)
    k = (n + 1) // 2
    out = {}

    def add(name, source, family, note, data=None):
        out[name] = (Program({"f": source}, data=data or {}), family, note)

    add("NESTED_CONSTANT_TABLE",
        "def f(x):\n" + _unpack(n) + "    return TABLE"
        + "".join("[%s]" % v for v in vs) + "\n",
        "NON_NEURAL_TABLE", "task-independent constant table of 2**n cells",
        data={"TABLE": _nested_table(n, majority)})

    index = " | ".join(("(%s << %d)" % (v, n - 1 - i)) if i < n - 1 else v
                       for i, v in enumerate(vs))
    add("FLAT_INDEX_TABLE",
        "def f(x):\n" + _unpack(n) + "    i = " + index + "\n    return TABLE[i]\n",
        "NON_NEURAL_TABLE", "the rendering the parity-n registration costed as 5n+2",
        data={"TABLE": tuple(majority(bits) for bits in points(n))})

    add("THRESHOLD_COMPARISON_BOOL",
        "def f(x):\n" + _unpack(n) + "    return (" + total + ") >= %d\n" % k,
        "THRESHOLD", "one linear form, one threshold; Boolean-valued")

    add("THRESHOLD_COMPARISON_INT",
        "def f(x):\n" + _unpack(n) + "    return 0 + ((" + total + ") >= %d)\n" % k,
        "THRESHOLD", "same form, coerced to int without a native call")

    add("THRESHOLD_SHIFT_INT",
        "def f(x):\n" + _unpack(n) + "    return (" + total + ") >> 1\n",
        "THRESHOLD", "linear form then a fixed shift; exact only where checked")

    if n >= 3:
        head = " + ".join(vs[:-1])
        add("NONAFFINE_SHIFT_BOOL",
            "def f(x):\n" + _unpack(n) + "    return ((" + head + ") << %s) > 1\n" % vs[-1],
            "NON_THRESHOLD_ARITHMETIC",
            "minimal-cost non-affine rendering found by the enumeration")

    add("HIDDEN_UNIT_NET_BOOL",
        "def f(x):\n" + _unpack(n) + "    s = " + total
        + "\n    h0 = s >= %d\n    return h0 >= 1\n" % k,
        "THRESHOLD_NET", "registered shape B with one hidden unit, native-free")

    add("HIDDEN_UNIT_NET_INT",
        "def f(x):\n" + _unpack(n) + "    s = " + total
        + "\n    h0 = int(s >= %d)\n    return int(h0 >= 1)\n" % k,
        "THRESHOLD_NET", "registered shape B with one hidden unit and int() units")

    add("DELEGATING_SUM_COMPARISON",
        "def f(x):\n    return sum(x) >= %d\n" % k,
        "DELEGATING", "native sum; its work is a separate obligation")

    terms = ["(" + " & ".join(vs[i] for i in combo) + ")" for combo in _dnf_terms(n)]
    add("MONOTONE_DNF_CHAIN",
        "def f(x):\n" + _unpack(n) + "    return " + " | ".join(terms) + "\n",
        "NON_NEURAL_GATES", "disjunction of every minimal true set")

    return out


def constant_cells(program):
    """Integer cells in the code object's constants plus the data bindings."""
    def leaves(value):
        if type(value) is tuple:
            return sum(leaves(item) for item in value)
        return 1 if type(value) in (int, bool) else 0

    cells = 0
    for function in program.functions.values():
        for const in function.code.co_consts:
            if type(const) is CodeType:
                continue
            cells += leaves(const)
    for value in program.data.values():
        cells += leaves(value)
    return cells


def measure(n, task=majority):
    """Exact per-call cost of every registered candidate over the whole domain."""
    rows = {}
    for name, (program, family, note) in sorted(register(n).items()):
        opcodes, natives, kinds, correct = set(), set(), set(), True
        for bits in points(n):
            result = execute(program, "f", bits)
            want = task(bits)
            if result.value != want:
                correct = False
            opcodes.add(result.python_opcodes)
            natives.add(sum(not e.startswith("py:") for e in result.events))
            kinds.add(type(result.value).__name__)
        require(len(opcodes) == 1 and len(natives) == 1,
                "straight-line cost must not vary over the domain: " + name)
        rows[name] = {
            "family": family,
            "note": note,
            "python_opcodes_per_call": opcodes.pop(),
            "native_obligations_per_call": natives.pop(),
            "constant_cells": constant_cells(program),
            "return_type": sorted(kinds),
            "exact_on_whole_domain": correct,
            "value_equals_obligation": correct,
            "source": program.functions["f"].source,
        }
    return rows
