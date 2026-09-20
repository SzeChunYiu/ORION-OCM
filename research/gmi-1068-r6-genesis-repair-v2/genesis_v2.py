"""Operational witnesses, not a general intelligence or halting oracle."""
from dataclasses import dataclass, field
from fractions import Fraction

# Instructions occupy three integer cells: opcode, argument, argument.
HALT, STORE, COPY, ADD, JNZ, OUT = range(6)


@dataclass
class RAM:
    memory: dict
    pc: int = 0
    steps: int = 0
    halted: bool = False
    fault: str | None = None
    output: list = field(default_factory=list)
    trace: list = field(default_factory=list)
    frozen_code: dict | None = None

    @classmethod
    def load(cls, words, frozen_code=False):
        memory = dict(enumerate(words))
        return cls(memory, frozen_code=memory.copy() if frozen_code else None)

    @property
    def stopped(self):
        return self.halted or self.fault is not None

    def step(self):
        if self.stopped:
            return
        old_pc = self.pc
        code = self.memory if self.frozen_code is None else self.frozen_code
        op, a, b = (code.get(self.pc + i, 0) for i in range(3))
        self.steps += 1
        write = None
        if self.pc < 0 or self.pc % 3:
            self.fault = "INVALID_PC"
        elif op not in range(6):
            self.fault = "INVALID_OPCODE"
        elif op != HALT and a < 0:
            self.fault = "INVALID_ADDRESS"
        elif op == HALT:
            self.halted = True
        elif op == STORE:
            write = (a, self.memory.get(a, 0), b)
            self.memory[a] = b
            self.pc += 3
        elif op == COPY:
            if b < 0:
                self.fault = "INVALID_ADDRESS"
            else:
                value = self.memory.get(b, 0)
                write = (a, self.memory.get(a, 0), value)
                self.memory[a] = value
                self.pc += 3
        elif op == ADD:
            value = self.memory.get(a, 0) + b
            write = (a, self.memory.get(a, 0), value)
            self.memory[a] = value
            self.pc += 3
        elif op == JNZ:
            self.pc = b if self.memory.get(a, 0) else self.pc + 3
        else:
            self.output.append(self.memory.get(a, 0))
            self.pc += 3
        self.trace.append({"pc": old_pc, "instruction": [op, a, b],
                           "write": list(write) if write else None})


def execute(words, budget, frozen_code=False):
    machine = RAM.load(words, frozen_code)
    for _ in range(budget):
        if machine.stopped:
            break
        machine.step()
    state = "FAULT" if machine.fault else "HALTED" if machine.halted else "BUDGET_EXHAUSTED"
    return machine, state


def halts_after(steps):
    if steps < 1:
        raise ValueError("steps must be positive")
    # Data cell lies after the program, so ADD does not alter these instructions.
    data = 3 * steps + 3
    return [ADD, data, 1] * (steps - 1) + [HALT, 0, 0]


def divergent():
    # The exact invariant pc=0, memory[3]=1 proves divergence for this witness.
    return [JNZ, 3, 0, 1]


def dovetail(factory, stages, mode="fair"):
    machines, finishes, slots = {}, {}, []
    for stage in range(stages):
        machines[stage] = RAM.load(factory(stage))
        indices = range(stage + 1)
        if mode == "serial":
            indices = [next((k for k in range(stage + 1) if not machines[k].stopped), stage)]
        elif mode == "latest":
            indices = [stage]
        for index in indices:
            machine = machines[index]
            slots.append([stage, index])
            if not machine.stopped:
                machine.step()
                if machine.halted:
                    finishes[index] = stage
    return machines, finishes, slots


def reflection_chain(depth, value):
    """A store edits the next store's immediate, for any finite depth >= 1."""
    if depth < 1:
        raise ValueError("depth must be positive")
    words = []
    for level in range(depth):
        words += [STORE, 3 * (level + 1) + 2, value if level == 0 else -level]
    data = 3 * (depth + 3)
    words += [STORE, data, -depth, OUT, data, 0, HALT, 0, 0]
    return words


def abstraction(D, L, c, n):
    D, L, c = map(Fraction, (D, L, c))
    if min(D, L, c) < 0 or not isinstance(n, int) or n < 0:
        raise ValueError("nonnegative costs and integer repetition count required")
    saving = n * (L - c) - D
    outcome = "WIN" if saving > 0 else "TIE" if saving == 0 else "LOSE"
    threshold = D / (L - c) if L > c else None
    first = threshold.numerator // threshold.denominator + 1 if threshold is not None else None
    return {"saving": saving, "outcome": outcome, "first_positive_n": first}


def delay(bits):
    state, outputs = 0, []
    for bit in bits:
        outputs.append(state)
        state = bit
    return tuple(outputs)
