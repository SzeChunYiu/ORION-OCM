"""Exact measured size of the constant payload each realization needs.

TT-6 showed that charging a constant cell at any positive rate makes the
threshold rendering strictly dominate the `2**n` table. Its second component was
a declared **count** of integer cells, which the theorem was explicit about not
being bytes and not being memory. This module replaces the premise with three
exact measurements on a validated object-size contract:

- `marshalled_constant_bytes` -- the serialized size CPython itself writes for
  these constants, `len(marshal.dumps(payload))`. Deterministic and exact.
- `tuple_structure_bytes` -- the in-memory size of the tuple objects the payload
  needs, `sum(sys.getsizeof(node))` over every tuple node.
- `tuple_nodes` and `tuple_slots` -- the structural counts that explain it.

The integers are **not** counted as incremental memory, and that is a
measurement rather than a convenience: every value in these payloads is 0 or 1,
CPython caches small integers, and `verify_small_integer_interning` checks that
the table's leaves are the very same objects as independently built integers. So
a lookup table's incremental in-memory cost is its pointer arrays, not its
values. Reporting `sys.getsizeof` of each leaf would double-count shared
objects and inflate the table's cost, which would flatter the conclusion.

None of these is resident set size. They are exact sizes of the constant payload
in two well-defined senses, on a size contract this module validates and refuses
to guess about.
"""

import marshal
import sys
from types import CodeType

# CPython 3.12 on a 64-bit build. Validated rather than assumed: a different
# build changes every number here, so the contract is checked and the caller
# raises instead of restating different measurements under the same claim.
EMPTY_TUPLE_BYTES = 40
TUPLE_SLOT_BYTES = 8
SMALL_INT_BYTES = 28


class FootprintError(ValueError):
    """The measured size contract does not hold on this interpreter."""


def require(condition, message):
    if not condition:
        raise FootprintError(message)


def size_contract():
    """Validate the object-size contract these measurements are stated against."""
    empty = sys.getsizeof(())
    per_slot = sys.getsizeof((1, 2)) - sys.getsizeof((1,))
    small_int = sys.getsizeof(0)
    require(empty == EMPTY_TUPLE_BYTES,
            "empty tuple is %d bytes, contract says %d" % (empty, EMPTY_TUPLE_BYTES))
    require(per_slot == TUPLE_SLOT_BYTES,
            "tuple slot is %d bytes, contract says %d" % (per_slot, TUPLE_SLOT_BYTES))
    require(small_int == SMALL_INT_BYTES,
            "small int is %d bytes, contract says %d" % (small_int, SMALL_INT_BYTES))
    return {"empty_tuple_bytes": empty, "tuple_slot_bytes": per_slot,
            "small_integer_bytes": small_int,
            "interpreter_maxsize_bits": sys.maxsize.bit_length()}


def integer_leaves(value):
    if type(value) is tuple:
        return [leaf for item in value for leaf in integer_leaves(item)]
    return [value] if type(value) in (int, bool) else []


def tuple_nodes(value):
    if type(value) is not tuple:
        return []
    nodes = [value]
    for item in value:
        nodes.extend(tuple_nodes(item))
    return nodes


def constant_payload(program):
    """Every constant the realization needs: code constants and data bindings."""
    payload = []
    for function in program.functions.values():
        for constant in function.code.co_consts:
            if type(constant) is CodeType:
                continue
            payload.append(constant)
    payload.extend(program.data.values())
    return payload


def verify_small_integer_interning(program):
    """Are the payload's integers shared objects rather than new allocations?

    Returns True only when every integer leaf is identical (`is`) to a value
    built independently, so counting them as incremental memory would be
    double-counting.
    """
    leaves = [leaf for value in constant_payload(program) for leaf in integer_leaves(value)]
    for leaf in leaves:
        independent = int(str(int(leaf)))
        if independent is not leaf:
            return False
    return True


def measure(program):
    """Exact measured footprint of one realization's constant payload."""
    payload = constant_payload(program)
    leaves = [leaf for value in payload for leaf in integer_leaves(value)]
    nodes = [node for value in payload for node in tuple_nodes(value)]
    return {
        "integer_cells": len(leaves),
        "marshalled_constant_bytes": len(marshal.dumps(tuple(payload))),
        "tuple_nodes": len(nodes),
        "tuple_slots": sum(len(node) for node in nodes),
        "tuple_structure_bytes": sum(sys.getsizeof(node) for node in nodes),
        "integers_are_shared_objects": verify_small_integer_interning(program),
    }


def footprints(register):
    """{candidate name: measured footprint} for a `frontier_registers` register."""
    return {name: measure(program) for name, (program, _family, _note)
            in sorted(register.items())}
