"""Finite persistent images and fresh-state service; no native VM imports."""
from dataclasses import dataclass, replace

TOKENS = ("L0", "L1", "L2", "XOR", "EMIT", "EMIT0", "EMIT1", "NOP")

@dataclass(frozen=True)
class Image:
    data: tuple
    programs: tuple

def validate(image):
    if not isinstance(image, Image) or len(image.data) > 3:
        raise ValueError("invalid data")
    if any(type(x) is not int or x not in (0, 1) for x in image.data):
        raise ValueError("data must be bits")
    if len(image.programs) != 3:
        raise ValueError("three query programs required")
    for program in image.programs:
        if not 1 <= len(program) <= 7 or any(t not in TOKENS for t in program):
            raise ValueError("invalid code")
    return 2 + 9 + 3 * sum(map(len, image.programs)) + len(image.data)

def encode(image):
    validate(image)
    fields = [format(len(image.data), "02b")]
    fields += [format(len(p), "03b") for p in image.programs]
    fields += [format(TOKENS.index(t), "03b") for p in image.programs for t in p]
    fields += [str(x) for x in image.data]
    return "".join(fields)

def decode(bits):
    if not isinstance(bits, str) or any(c not in "01" for c in bits) or len(bits) < 11:
        raise ValueError("invalid image encoding")
    n = int(bits[:2], 2)
    lengths = [int(bits[i:i+3], 2) for i in (2, 5, 8)]
    if not all(lengths) or len(bits) != 11 + 3 * sum(lengths) + n:
        raise ValueError("invalid complete image length")
    pc, programs = 11, []
    for length in lengths:
        programs.append(tuple(TOKENS[int(bits[i:i+3], 2)]
                              for i in range(pc, pc + 3*length, 3)))
        pc += 3 * length
    image = Image(tuple(map(int, bits[pc:])), tuple(programs))
    validate(image)
    return image

def construct(history, compact=False):
    x, y = history
    data = (x, y) if compact else (x, y, x ^ y)
    programs = (("L0", "EMIT"), ("L1", "EMIT"),
                ("L0", "L1", "XOR", "EMIT") if compact else ("L2", "EMIT"))
    image = Image(data, programs)
    validate(image)
    return image

def service(image, query, stack_capacity=2):
    validate(image)
    if type(query) is not int or query not in range(3):
        raise ValueError("unknown query")
    if type(stack_capacity) is not int or stack_capacity < 0:
        raise ValueError("invalid workspace")
    stack, trace, peak = [], [], 0
    program = image.programs[query]
    for pc, token in enumerate(program):
        before = tuple(stack)
        if token.startswith("L"):
            index = int(token[1:])
            if index >= len(image.data):
                raise ValueError("missing data")
            stack.append(image.data[index])
        elif token == "XOR":
            if len(stack) < 2:
                raise ValueError("stack underflow")
            b, a = stack.pop(), stack.pop()
            stack.append(a ^ b)
        elif token in ("EMIT", "EMIT0", "EMIT1"):
            if token == "EMIT":
                if not stack:
                    raise ValueError("stack underflow")
                answer = stack.pop()
            else:
                answer = int(token[-1])
            if pc != len(program)-1:
                raise ValueError("nonterminal emit")
            trace.append((pc, token, before, tuple(stack), answer))
            return dict(answer=answer, trace=trace, instructions=len(trace),
                        workspace_bits=2+len(program).bit_length()+peak+1)
        if len(stack) > stack_capacity:
            raise ValueError("operand capacity exceeded")
        peak = max(peak, len(stack))
        trace.append((pc, token, before, tuple(stack), None))
    raise ValueError("no output")

def setup(image, compact):
    size = validate(image)
    # Installation checks every serialized bit and every admitted token.
    validation = size + sum(map(len, image.programs))
    return dict(history_reads=2, raw_xor=0 if compact else 1, image_writes=size,
                validation_checks=validation, persistent_bits=size,
                core_operations=2+(0 if compact else 1)+size,
                total_operations=2+(0 if compact else 1)+size+validation)

def zero_slot(image, index):
    validate(image)
    if index not in range(len(image.data)):
        raise ValueError("missing slot")
    data = list(image.data)
    data[index] = 0
    return replace(image, data=tuple(data))

def replace_query(image, query, program):
    programs = list(image.programs)
    programs[query] = tuple(program)
    result = replace(image, programs=tuple(programs))
    validate(result)
    return result

def intervention(before, after):
    a, b = encode(before), encode(after)
    return dict(image=decode(b), read_bits=len(a), write_bits=len(b),
                snapshot_bits=len(a), snapshot_read_write_operations=2*len(a))

def restore(snapshot):
    return decode(snapshot)
