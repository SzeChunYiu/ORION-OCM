"""Independent static witness: never call the parent's validator or a candidate."""
import dis
import inspect


def expectation(fn):
    code = fn.__code__
    rows = list(dis.get_instructions(code, adaptive=False))
    jumps = set(dis.hasjabs) | set(dis.hasjrel)
    if (code.co_exceptiontable or code.co_flags & (inspect.CO_GENERATOR | inspect.CO_COROUTINE)
            or any(row.opcode in jumps or row.opname.startswith("YIELD") for row in rows)):
        raise ValueError("oracle only covers straight-line, non-suspending candidate bodies")
    body = [row for row in rows if row.opname not in ("CACHE", "RESUME")]
    if not body or not body[-1].opname.startswith("RETURN"):
        raise ValueError("missing final return")
    if any(row.opname.startswith("RETURN") for row in body[:-1]):
        raise ValueError("early return outside oracle scope")
    return {"offsets": [row.offset for row in body],
            "instructions": [{"offset": row.offset, "opname": row.opname} for row in body]}


def inspect_calls(calls, expected, inputs):
    errors = []
    if type(calls) is not list:
        return {"complete_frames": 0, "events": 0, "errors": ["calls must be a list"]}
    if len(calls) != len(inputs):
        errors.append("wrong frame count")
    complete, total = 0, 0
    for index, row in enumerate(calls):
        if type(row) is not dict:
            errors.append(f"frame {index}: malformed")
            continue
        offsets = row.get("opcode_offsets")
        exact_offsets = (type(offsets) is list and all(type(x) is int for x in offsets)
                         and offsets == expected["offsets"])
        if type(offsets) is list:
            total += len(offsets)
        correct = (index < len(inputs) and type(row.get("output")) is int
                   and row["output"] == sum(inputs[index]) % 2)
        returned = row.get("returned") is True
        if exact_offsets and correct and returned:
            complete += 1
        else:
            causes = [name for name, ok in (("offset sequence", exact_offsets),
                      ("parity output", correct), ("return", returned)) if not ok]
            errors.append(f"frame {index}: " + ", ".join(causes))
    return {"complete_frames": complete, "events": total, "errors": errors}
