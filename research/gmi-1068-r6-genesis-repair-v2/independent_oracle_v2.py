"""Independent dense-memory interpreter and cost calculation; no candidate imports."""
from fractions import Fraction


def run(code, budget):
    tape, pointer, answer, records = list(code), 0, [], []
    for count in range(1, budget + 1):
        if pointer < 0 or pointer % 3:
            return "FAULT", answer, count, records
        while len(tape) <= pointer + 2:
            tape.append(0)
        instruction, x, y = tape[pointer:pointer + 3]
        if instruction not in (0, 1, 2, 3, 4, 5) or (instruction != 0 and x < 0):
            return "FAULT", answer, count, records
        old_pointer = pointer
        edit = None
        if instruction == 0:
            records.append({"pc": pointer, "instruction": [instruction, x, y], "write": None})
            return "HALTED", answer, count, records
        while len(tape) <= x:
            tape.append(0)
        pointer += 3
        if instruction in (1, 2, 3):
            old_value = tape[x]
            if instruction == 1:
                tape[x] = y
            elif instruction == 2:
                if y < 0:
                    return "FAULT", answer, count, records
                while len(tape) <= y:
                    tape.append(0)
                tape[x] = tape[y]
            else:
                tape[x] += y
            edit = [x, old_value, tape[x]]
        elif instruction == 4 and tape[x] != 0:
            pointer = y
        elif instruction == 5:
            answer += [tape[x]]
        records.append({"pc": old_pointer, "instruction": [instruction, x, y], "write": edit})
    return "BUDGET_EXHAUSTED", answer, budget, records


def schedule(factory, stages):
    # Replay each prefix independently instead of sharing resumable RAM objects.
    finishes = {}
    for diagonal in range(stages):
        for index in range(diagonal + 1):
            state, _, _, _ = run(factory(index), diagonal - index + 1)
            if state == "HALTED" and index not in finishes:
                finishes[index] = diagonal
    return finishes


def cost_outcome(D, L, c, n):
    inline = sum((Fraction(L) for _ in range(n)), Fraction(0))
    library = Fraction(D) + sum((Fraction(c) for _ in range(n)), Fraction(0))
    return "WIN" if inline > library else "TIE" if inline == library else "LOSE"
