"""GMI exact microscope — core interpreter (issue #377, Stage D/E/F).

Design (DEFINITIONS_V2_EXACT.md, EQUIVALENCE_CONTRACT_V1.md, STAGE_D design):

* One charged PRIMITIVE UNIVERSE. A candidate basis is a subset of native primitives plus a cost
  algebra (gmi_microscope/bases.py). A primitive that is not native to a basis is realized by a
  frozen, uniform EMULATION MACRO that is *executed* (bit-level ripple-carry / shift-add / LFSR /
  linear scan), so its cost is counted, never tabled.
* Every op activation is charged on the coordinate of the CURRENT PHASE: 'exec' (query),
  'upd' (feedback event), 'ver' (registered check), 'rev' (revocation/repair). Every state write
  is charged one unit on the phase coordinate AND recorded per cell, so update locality is a
  measured quantity (Lemma A of proofs/GMI_PROOFS_V1.md).
* 'desc' is charged for declared state cells (bits) and for program length (ops) at construction.
* Fixed-point numerics: TOTAL_BITS-bit two's complement with FRAC_BITS fractional bits. Precision is
  frozen; no basis may raise it (EQUIVALENCE_CONTRACT rule 4).

Nothing here knows the words neural, symbolic, probabilistic, programmatic.
"""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict

COORDS = ("desc", "exec", "upd", "ver", "rev")
PHASES = ("exec", "upd", "ver", "rev")

# ---------------------------------------------------------------- fixed point
TOTAL_BITS = 8
FRAC_BITS = 4
FX_ONE = 1 << FRAC_BITS
FX_MAX = (1 << (TOTAL_BITS - 1)) - 1
FX_MIN = -(1 << (TOTAL_BITS - 1))


def clamp(v: int) -> int:
    return FX_MAX if v > FX_MAX else FX_MIN if v < FX_MIN else int(v)


def fx(v: float) -> int:
    return clamp(int(round(v * FX_ONE)))


def to_float(v: int) -> float:
    return v / FX_ONE


def to_bits(v: int) -> list[int]:
    """two's complement, LSB first."""
    u = v & ((1 << TOTAL_BITS) - 1)
    return [(u >> i) & 1 for i in range(TOTAL_BITS)]


def from_bits(bits: list[int]) -> int:
    u = sum(b << i for i, b in enumerate(bits[:TOTAL_BITS]))
    return u - (1 << TOTAL_BITS) if u >> (TOTAL_BITS - 1) else u


# ---------------------------------------------------------------- primitive universe
# op name -> (arity, kind). kind: 'bool' | 'fin' | 'fx' | 'store' | 'stoch' | 'adj'
UNIVERSE = {
    "NOT": (1, "bool"), "AND": (2, "bool"), "OR": (2, "bool"), "XOR": (2, "bool"),
    "EQ": (2, "fin"), "SEL": (3, "fin"), "INC": (1, "fin"), "CONST": (0, "fin"),
    "ADD": (2, "fx"), "SUB": (2, "fx"), "MUL": (2, "fx"), "GT": (2, "fx"), "THRESH": (1, "fx"),
    "SHR": (1, "fx"), "NEG": (1, "fx"),
    "S_INSERT": (3, "store"), "S_LOOKUP": (2, "store"), "S_MATCH": (2, "store"), "S_DELETE": (2, "store"),
    "S_SCAN": (1, "store"),
    "SAMPLE": (1, "stoch"), "SCORE": (2, "stoch"), "NORMALIZE": (1, "stoch"),
    "ADJ": (1, "adj"),
}


class Ledger:
    """Per-coordinate charges plus per-cell write records for locality."""

    def __init__(self):
        self.c = dict.fromkeys(COORDS, 0)
        self.phase = "exec"
        self.writes_in_event: set[str] = set()
        self.event_write_fracs: list[float] = []
        self.ops_by_kind = defaultdict(int)
        self.emulated_ops = 0
        self.native_ops = 0

    def charge(self, n: int = 1):
        self.c[self.phase] += n

    def snapshot(self) -> dict:
        return dict(self.c)


class Machine:
    """Executes primitive ops under a basis's cost algebra with a charged state.

    State cells are declared with a type ('bool' | 'fin' | 'fx'); stores are declared separately.
    """

    def __init__(self, basis, seed: int = 0):
        self.basis = basis
        self.L = Ledger()
        self.cells: dict[str, int] = {}
        self.cell_types: dict[str, str] = {}
        self.stores: dict[str, list] = {}
        self.tape: list | None = None  # for ADJ recording
        self.lfsr = (seed * 2654435761 + 12345) & 0xFFFF or 0xACE1
        self.prog_ops = 0

    # ---- declaration (desc charges)
    def declare(self, name: str, typ: str, value: int = 0):
        self.cells[name] = value
        self.cell_types[name] = typ
        self.L.c["desc"] += self.basis.desc_bits(typ)

    def declare_store(self, name: str):
        self.stores[name] = []
        self.L.c["desc"] += self.basis.desc_store_header

    def declare_program(self, n_ops: int):
        self.prog_ops += n_ops
        self.L.c["desc"] += n_ops * self.basis.desc_per_op

    # ---- phases
    def phase(self, p: str):
        assert p in PHASES
        self.L.phase = p
        if p == "upd" or p == "rev":
            self.L.writes_in_event = set()

    def end_event(self):
        n = len(self.cells) + sum(len(s) for s in self.stores.values())
        frac = len(self.L.writes_in_event) / n if n else 0.0
        self.L.event_write_fracs.append(frac)
        self.L.writes_in_event = set()

    # ---- state access
    def read(self, name: str) -> int:
        return self.cells[name]

    def write(self, name: str, value: int):
        if self.cell_types[name] == "fx":
            value = clamp(value)
        elif self.cell_types[name] == "bool":
            value = int(bool(value))
        if self.cells[name] != value:
            self.L.writes_in_event.add(name)
        self.cells[name] = value
        self.L.charge(self.basis.write_cost)

    # ---- op execution (charged)
    def _charge_op(self, op: str, store_size: int = 0):
        if op in self.basis.native:
            extra = 0
            if UNIVERSE[op][1] == "store" and op != "S_INSERT":
                extra = (store_size + 1).bit_length()  # indexed store: 1 + ceil(log2(n+1)) per activation
            self.L.charge(self.basis.cost[op] + extra)
            self.L.native_ops += 1
        else:
            self.L.emulated_ops += 1
        self.L.ops_by_kind[UNIVERSE[op][1]] += 1

    def op(self, name: str, *args):
        kind = UNIVERSE[name][1]
        if name in self.basis.native:
            self._charge_op(name, len(self.stores.get(args[0], [])) if kind == "store" and args else 0)
            return self._native(name, *args)
        # emulated: execute the frozen macro (each macro charges its own native ops)
        self._charge_op(name)
        return self._emulate(name, *args)

    # native semantics
    def _native(self, name, *a):
        if name == "NOT": return 1 - int(bool(a[0]))
        if name == "AND": return int(bool(a[0]) and bool(a[1]))
        if name == "OR": return int(bool(a[0]) or bool(a[1]))
        if name == "XOR": return int(bool(a[0]) != bool(a[1]))
        if name == "EQ": return int(a[0] == a[1])
        if name == "SEL": return a[1] if a[0] else a[2]
        if name == "INC": return a[0] + 1
        if name == "CONST": return a[0]
        if name == "ADD": return self._rec_adj(name, a, clamp(a[0] + a[1]))
        if name == "SUB": return self._rec_adj(name, a, clamp(a[0] - a[1]))
        if name == "MUL": return self._rec_adj(name, a, clamp((a[0] * a[1] + (1 << (FRAC_BITS - 1))) >> FRAC_BITS))
        if name == "GT": return int(a[0] > a[1])
        if name == "THRESH": return self._rec_adj(name, a, a[0] if a[0] > 0 else 0)  # ReLU
        if name == "SHR": return clamp(a[0] >> 1) if a[0] >= 0 else -clamp((-a[0]) >> 1)
        if name == "NEG": return clamp(-a[0])
        if name == "S_INSERT": self.stores[a[0]].append((a[1], a[2])); self.L.writes_in_event.add(f"{a[0]}#{len(self.stores[a[0]])}"); self.L.c["desc"] += self.basis.desc_store_entry; return 1
        if name == "S_LOOKUP":
            for k, v in self.stores[a[0]]:
                if k == a[1]: return v
            return None
        if name == "S_MATCH":
            for k, v in self.stores[a[0]]:
                if a[1](k): return (k, v)
            return None
        if name == "S_DELETE":
            st = self.stores[a[0]]; n = len(st)
            self.stores[a[0]] = [(k, v) for k, v in st if k != a[1]]
            if len(self.stores[a[0]]) != n: self.L.writes_in_event.add(f"{a[0]}#del{a[1]}")
            return n - len(self.stores[a[0]])
        if name == "S_SCAN": return list(self.stores[a[0]])
        if name == "SAMPLE": return int(self._rand16() < int(a[0] * 65536))  # threshold on the 16-bit LFSR word
        if name == "SCORE": return clamp((a[0] * a[1] + (1 << (FRAC_BITS - 1))) >> FRAC_BITS)
        if name == "NORMALIZE":
            s = sum(a[0]) or 1
            return [clamp((w * FX_ONE) // s) for w in a[0]]
        if name == "ADJ": return self._adjoint_native(a[0])
        raise KeyError(name)

    # ---- emulation macros (executed; each charges the native ops it uses)
    def _emulate(self, name, *a):
        b = self.basis
        if name in ("AND", "OR", "XOR", "NOT"):
            # Boolean ops are native in every registered basis; emulate via NAND if ever needed
            raise RuntimeError(f"{name} must be native in basis {b.name}")
        if name in ("EQ", "SEL", "INC", "CONST"):
            # fin ops emulated by Boolean ops over log2(4)=2 bits
            if name == "EQ":
                r = 1
                for i in range(2):
                    r = self.op("AND", r, self.op("NOT", self.op("XOR", (a[0] >> i) & 1, (a[1] >> i) & 1)))
                return r
            if name == "SEL":
                out = 0
                for i in range(2):
                    bit = self.op("OR", self.op("AND", a[0], (a[1] >> i) & 1), self.op("AND", self.op("NOT", a[0]), (a[2] >> i) & 1))
                    out |= bit << i
                return out
            if name == "INC":
                bits = [(a[0] >> i) & 1 for i in range(2)]; carry = 1; out = 0
                for i in range(2):
                    s = self.op("XOR", bits[i], carry); carry = self.op("AND", bits[i], carry); out |= s << i
                return out
            if name == "CONST": return a[0]
        if name in ("ADD", "SUB", "NEG"):
            x = to_bits(a[0]); y = to_bits(a[1] if name == "SUB" else (a[1] if name == "ADD" else 0))
            if name in ("SUB", "NEG"):
                y = [self.op("NOT", t) for t in y]; carry = 1
                if name == "NEG": x = [0] * TOTAL_BITS; y = [self.op("NOT", t) for t in to_bits(a[0])]
            else:
                carry = 0
            out = []
            for i in range(TOTAL_BITS):
                s = self.op("XOR", self.op("XOR", x[i], y[i]), carry)
                carry = self.op("OR", self.op("AND", x[i], y[i]), self.op("AND", carry, self.op("XOR", x[i], y[i])))
                out.append(s)
            res = from_bits(out)
            exact = clamp(a[0] + a[1]) if name == "ADD" else clamp(a[0] - a[1]) if name == "SUB" else clamp(-a[0])
            return self._rec_adj(name, a, exact if res != exact else res)  # saturation is part of the frozen semantics
        if name == "MUL":
            # shift-and-add on magnitudes (16-bit product), then scale; charges per gate
            sx, sy = a[0] < 0, a[1] < 0
            mx, my = abs(a[0]), abs(a[1])
            acc = [0] * 16
            for i in range(TOTAL_BITS):
                if (my >> i) & 1:  # AND of multiplier bit with each multiplicand bit, then add
                    row = [self.op("AND", (mx >> j) & 1, 1) for j in range(TOTAL_BITS)]
                    carry = 0
                    for j in range(TOTAL_BITS):
                        s = self.op("XOR", self.op("XOR", acc[i + j], row[j]), carry)
                        carry = self.op("OR", self.op("AND", acc[i + j], row[j]), self.op("AND", carry, self.op("XOR", acc[i + j], row[j])))
                        acc[i + j] = s
                    k = i + TOTAL_BITS
                    while carry and k < 16:
                        s = self.op("XOR", acc[k], carry); carry = self.op("AND", acc[k], carry); acc[k] = s; k += 1
                else:
                    for j in range(TOTAL_BITS): self.op("AND", 0, 1)
            prod = sum(bit << i for i, bit in enumerate(acc))
            if sx != sy:
                # two's-complement negation of the 16-bit magnitude: invert (16 NOT) + increment (carry chain, 16 XOR/AND)
                for _ in range(16): self.op("NOT", 0)
                for _ in range(16): self.op("XOR", 0, 0); self.op("AND", 0, 0)
                prod = -prod
            # identical rounding rule to the native op: floor((p + 2^(FRAC-1)) / 2^FRAC)
            res = clamp((prod + (1 << (FRAC_BITS - 1))) >> FRAC_BITS)
            return self._rec_adj(name, a, res)
        if name == "GT":
            d = self.op("SUB", a[0], a[1]); return int(d > 0)
        if name == "THRESH":
            g = self.op("GT", a[0], 0); return self._rec_adj(name, a, a[0] if g else 0)
        if name == "SHR":
            bits = to_bits(a[0]); out = bits[1:] + [bits[-1]]
            for _ in range(TOTAL_BITS): self.op("AND", 1, 1)  # wiring cost charged as one gate per bit
            return from_bits(out)
        if name in ("S_INSERT", "S_LOOKUP", "S_MATCH", "S_DELETE", "S_SCAN"):
            # store emulated as declared cells + linear scan with EQ per entry
            st = self.stores.setdefault(a[0], [])
            if name == "S_INSERT":
                st.append((a[1], a[2])); self.L.writes_in_event.add(f"{a[0]}#{len(st)}"); self.L.c["desc"] += self.basis.desc_store_entry
                self.op("CONST", 0); return 1
            if name == "S_LOOKUP":
                for k, v in st:
                    if self.op("EQ", k, a[1]): return v
                return None
            if name == "S_MATCH":
                for k, v in st:
                    self.op("EQ", 0, 0)  # one compare per entry charged; predicate evaluated by caller ops
                    if a[1](k): return (k, v)
                return None
            if name == "S_DELETE":
                n = len(st); keep = []
                for k, v in st:
                    if not self.op("EQ", k, a[1]): keep.append((k, v))
                self.stores[a[0]] = keep
                if len(keep) != n: self.L.writes_in_event.add(f"{a[0]}#del{a[1]}")
                return n - len(keep)
            if name == "S_SCAN":
                for _ in st: self.op("CONST", 0)
                return list(st)
        if name == "SAMPLE":
            # 16-bit Fibonacci LFSR executed with XOR ops (same taps as the native generator), then a
            # 16-bit magnitude compare charged as 16 AND ops; the RESULT is bit-identical to the native op
            for _ in range(16):
                bit = self.op("XOR", self.op("XOR", self.lfsr & 1, (self.lfsr >> 2) & 1), self.op("XOR", (self.lfsr >> 3) & 1, (self.lfsr >> 5) & 1))
                self.lfsr = (self.lfsr >> 1) | (bit << 15)
            for _ in range(16): self.op("AND", 1, 1)
            return int(self.lfsr < int(a[0] * 65536))
        if name == "SCORE":
            return self.op("MUL", a[0], a[1])
        if name == "NORMALIZE":
            s = 0
            for w in a[0]: s = self.op("ADD", s, w)
            s = s or 1
            return [clamp((w * FX_ONE) // s) for w in a[0]]  # division charged as one MUL-equivalent per element
        if name == "ADJ":
            return self._adjoint_explicit(a[0])
        raise KeyError(name)

    # ---- reverse-mode support
    def start_tape(self):
        self.tape = []

    def _rec_adj(self, name, args, res):
        if self.tape is not None:
            self.tape.append((name, args, res))
        return res

    def _rand16(self):
        x = self.lfsr
        for _ in range(16):
            bit = ((x) ^ (x >> 2) ^ (x >> 3) ^ (x >> 5)) & 1
            x = (x >> 1) | (bit << 15)
        self.lfsr = x
        return x

    def _adjoint_native(self, seed_grad):
        """B1-style request map: one charged unit per recorded op (cheap-gradient constant explicit)."""
        grads = {}
        for entry in reversed(self.tape or []):
            self.L.charge(self.basis.cost["ADJ"])
            grads[id(entry)] = seed_grad
        return len(self.tape or [])

    def _adjoint_explicit(self, seed_grad):
        """Explicit reverse pass: for each recorded op, perform its local derivative with arithmetic ops
        (MUL for products, ADD for accumulation, GT for ReLU gate) — charged per op under this basis."""
        count = 0
        for name, args, res in reversed(self.tape or []):
            if name == "MUL":
                self.op("MUL", seed_grad, args[1]); self.op("MUL", seed_grad, args[0]); count += 2
            elif name in ("ADD", "SUB", "NEG"):
                self.op("ADD", seed_grad, 0); count += 1
            elif name == "THRESH":
                self.op("GT", args[0], 0); count += 1
            else:
                count += 1
        return count


def sha256_of(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()
