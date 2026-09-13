"""Complete small retained-code search, using generic one-bit observations."""

from fractions import Fraction as F
from functools import lru_cache
from itertools import product


def partitions(size, symbols):
    """Restricted growth strings: all set partitions, once each."""
    if min(size, symbols) < 1:
        raise ValueError("nonempty finite domain and symbol set required")

    def visit(prefix, maximum):
        if len(prefix) == size:
            yield tuple(prefix)
            return
        for value in range(min(symbols - 1, maximum + 1) + 1):
            yield from visit(prefix + [value], max(maximum, value))

    yield from visit([0], 0)


class ReadCompiler:
    """Exact uniform-fiber Bellman compiler with executed tree witnesses."""

    def __init__(self, n):
        self.database = tuple(product((0, 1), repeat=n))
        self.n = n
        self.states = 0
        self.actions = 0

    def solve(self, labels, fiber=None):
        if fiber is None:
            fiber = tuple(range(len(self.database)))
        labels = tuple(labels)

        @lru_cache(None)
        def rec(ids):
            self.states += 1
            values = {labels[i] for i in ids}
            if len(values) == 1:
                return F(0), ("return", labels[ids[0]])
            best = None
            for bit in range(self.n):
                self.actions += 1
                zero = tuple(i for i in ids if self.database[i][bit] == 0)
                one = tuple(i for i in ids if self.database[i][bit] == 1)
                if not zero or not one:
                    continue
                c0, t0 = rec(zero)
                c1, t1 = rec(one)
                cost = 1 + (len(zero) * c0 + len(one) * c1) / len(ids)
                if best is None or cost < best[0]:
                    best = cost, ("read", bit, t0, t1)
            if best is None:
                raise ValueError("distinct database labels cannot be separated")
            return best

        return rec(tuple(fiber))

    def trace(self, program, database_id):
        reads = 0
        while program[0] == "read":
            reads += 1
            program = program[2 + self.database[database_id][program[1]]]
        return program[1], reads


def profile(code, compiler, probabilities):
    symbols = max(code) + 1
    memory = (symbols - 1).bit_length()
    acquisition, program = compiler.solve(code)
    observed = sum(compiler.trace(program, i)[1] for i in range(len(code)))
    if F(observed, len(code)) != acquisition:
        raise ValueError("acquisition trace disagrees with synthesis")
    if any(compiler.trace(program, i)[0] != code[i] for i in range(len(code))):
        raise ValueError("acquisition program outputs wrong retained code")
    retrieval = F(0)
    for symbol in range(symbols):
        fiber = tuple(i for i, s in enumerate(code) if s == symbol)
        for bit, probability in enumerate(probabilities):
            labels = tuple(x[bit] for x in compiler.database)
            cost, program = compiler.solve(labels, fiber)
            outcomes = [compiler.trace(program, i) for i in fiber]
            if any(value != labels[i] for i, (value, _) in zip(fiber, outcomes)):
                raise ValueError("retrieval program returns wrong bit")
            if F(sum(reads for _, reads in outcomes), len(fiber)) != cost:
                raise ValueError("retrieval trace disagrees with synthesis")
            retrieval += probability * F(len(fiber), len(code)) * cost
    return memory, acquisition, retrieval


def search(n, memory_max, probabilities, cA, cM, cR, horizon):
    probabilities = tuple(F(p) for p in probabilities)
    if len(probabilities) != n or any(p < 0 for p in probabilities) or sum(probabilities) != 1:
        raise ValueError("query distribution required")
    if any(v < 0 for v in (cA, cM, cR, horizon)) or not 0 <= memory_max <= n:
        raise ValueError("nonnegative charges and legal memory required")
    compiler = ReadCompiler(n)
    best, sizes, codes, count = None, set(), [], 0
    for code in partitions(2 ** n, 2 ** memory_max):
        count += 1
        memory, acquisition, retrieval = profile(code, compiler, probabilities)
        objective = cA * acquisition + cM * memory + horizon * cR * retrieval
        if best is None or objective < best:
            best, sizes, codes = objective, {memory}, [code]
        elif objective == best:
            sizes.add(memory)
            codes.append(code)
    return {"minimum": best, "memory_sizes": sorted(sizes), "optimal_codes": codes,
            "encoders": count, "bellman_states": compiler.states,
            "queried_actions": compiler.actions}
