"""Finite prefix interpreters and an actual reserved-code wrapper parser."""
from dataclasses import dataclass
from fractions import Fraction


def program(value):
    if type(value) is not tuple or any(type(bit) is not bool for bit in value):
        raise ValueError("a tuple of strict Boolean programme bits is required")
    return value


@dataclass(frozen=True)
class Book:
    outputs: int
    entries: tuple

    def __post_init__(self):
        if type(self.outputs) is not int or self.outputs < 0 or type(self.entries) is not tuple:
            raise ValueError("nonnegative output count and canonical entries required")
        trie = {}
        for row in self.entries:
            if type(row) is not tuple or len(row) != 2:
                raise ValueError("programme/output pair required")
            code, output = row
            program(code)
            if type(output) is not int or not 0 <= output < self.outputs:
                raise ValueError("output outside the declared alphabet")
            node = trie
            for bit in code:
                if "output" in node:
                    raise ValueError("domain contains a strict prefix")
                node = node.setdefault(bit, {})
            if node:
                raise ValueError("duplicate programme or prefix conflict")
            node["output"] = output
        object.__setattr__(self, "entries", tuple(sorted(self.entries)))


@dataclass(frozen=True)
class Wrapped:
    base: Book
    target: int
    padding: int

    def __post_init__(self):
        if type(self.base) is not Book:
            raise ValueError("finite base interpreter required")
        if type(self.target) is not int or not 0 <= self.target < self.base.outputs:
            raise ValueError("target outside output alphabet")
        if type(self.padding) is not int or self.padding < 1:
            raise ValueError("positive integer padding required")

    @property
    def outputs(self):
        return self.base.outputs


def decode(machine, code):
    program(code)
    if type(machine) is Book:
        return next((value for key, value in machine.entries if key == code), None)
    if type(machine) is not Wrapped:
        raise ValueError("Book or Wrapped interpreter required")
    if code == (False,):
        return machine.target
    if len(code) < machine.padding or not all(code[:machine.padding]):
        return None
    return decode(machine.base, code[machine.padding:])


def compiled(machine):
    if type(machine) is not Wrapped:
        raise ValueError("Wrapped interpreter required")
    prefix = (True,) * machine.padding
    entries = (((False,), machine.target),) + tuple(
        (prefix + code, output) for code, output in machine.base.entries)
    return Book(machine.outputs, entries)


def shortest(machine):
    if type(machine) is Wrapped:
        machine = compiled(machine)
    if type(machine) is not Book:
        raise ValueError("Book or Wrapped interpreter required")
    result = {}
    for code, output in machine.entries:
        if output not in result or len(code) < result[output]:
            result[output] = len(code)
    return result


def weights(machine):
    return {output: Fraction(1, 2 ** length) for output, length in shortest(machine).items()}


def profile(values, size):
    if type(values) is not tuple or len(values) != size:
        raise ValueError("one value per declared output required")
    if any(type(v) is not Fraction or not 0 <= v <= 1 for v in values):
        raise ValueError("exact Fraction values in the unit interval required")
    return values


def score(machine, values):
    if type(machine) not in (Book, Wrapped):
        raise ValueError("Book or Wrapped interpreter required")
    profile(values, machine.outputs)
    return sum((weight * values[output] for output, weight in weights(machine).items()),
               Fraction(0))
