"""Candidate bases B0..B3 and parent columns U, P3 as primitive subsets + cost algebras.

Frozen before any matrix entry was computed. A non-native op is executed by the frozen emulation
macro in core.Machine._emulate, whose native ops are charged under THIS basis's cost table. No
basis may contain NEURON/BACKPROP/PRODUCTION_RULE/BAYES_UPDATE/PROGRAM_INTERPRETER/ATTENTION.

Coordinates: desc bits per declared cell type; desc per program op; write cost per state write
(charged on the current phase); op costs per activation (charged on the current phase).
"""
from __future__ import annotations

from .core import TOTAL_BITS, UNIVERSE

BOOL_OPS = {"NOT", "AND", "OR", "XOR"}
FIN_OPS = {"EQ", "SEL", "INC", "CONST"}
FX_OPS = {"ADD", "SUB", "MUL", "GT", "THRESH", "SHR", "NEG"}
STORE_OPS = {"S_INSERT", "S_LOOKUP", "S_MATCH", "S_DELETE", "S_SCAN"}
STOCH_OPS = {"SAMPLE", "SCORE", "NORMALIZE"}
ADJ_OPS = {"ADJ"}


class Basis:
    def __init__(self, name, native, cost, desc_bits_by_type, desc_per_op, write_cost, desc_store_header, desc_store_entry, note):
        self.name = name
        self.native = set(native)
        self.cost = {op: cost.get(op, 1) for op in self.native}
        self._desc = desc_bits_by_type
        self.desc_per_op = desc_per_op
        self.write_cost = write_cost
        self.desc_store_header = desc_store_header
        self.desc_store_entry = desc_store_entry
        self.note = note
        for op in self.native:
            assert op in UNIVERSE, op

    def desc_bits(self, typ):
        return self._desc[typ]

    def spec(self):
        return {"name": self.name, "native": sorted(self.native), "cost": dict(sorted(self.cost.items())),
                "desc_bits_by_type": self._desc, "desc_per_op": self.desc_per_op, "write_cost": self.write_cost,
                "desc_store_header": self.desc_store_header, "desc_store_entry": self.desc_store_entry, "note": self.note}


_DESC_FULL = {"bool": 1, "fin": 2, "fx": TOTAL_BITS}
_STORE_ENTRY = 2 + TOTAL_BITS  # key (fin) + value (fx) bits when materialized as cells

B0 = Basis(
    "B0_LOCAL_ADAPTIVE_TRANSDUCERS",
    BOOL_OPS | FIN_OPS | FX_OPS,
    {op: 1 for op in BOOL_OPS | FIN_OPS} | {"ADD": 1, "SUB": 1, "MUL": 2, "GT": 1, "THRESH": 1, "SHR": 1, "NEG": 1},
    _DESC_FULL, 1, 1, 2, _STORE_ENTRY,
    "typed local cells with local arithmetic/Boolean transitions; stores are emulated as cells + linear scan; "
    "gradients need an explicit adjoint pass built from arithmetic ops; sampling emulated by an LFSR",
)

B1 = Basis(
    "B1_COMPOSITIONAL_LEARNER",
    BOOL_OPS | FIN_OPS | FX_OPS | ADJ_OPS,
    {op: 1 for op in BOOL_OPS | FIN_OPS} | {"ADD": 1, "SUB": 1, "MUL": 2, "GT": 1, "THRESH": 1, "SHR": 1, "NEG": 1, "ADJ": 1},
    _DESC_FULL, 1, 1, 2, _STORE_ENTRY,
    "parameterized maps with a native request/adjoint combinator (one unit per recorded op = cheap-gradient constant made explicit); "
    "stores emulated; sampling emulated",
)

B2 = Basis(
    "B2_REWRITABLE_TYPED_PROGRAM_GRAPH",
    BOOL_OPS | FIN_OPS | STORE_OPS,
    {op: 1 for op in BOOL_OPS | FIN_OPS} | {"S_INSERT": 1, "S_LOOKUP": 1, "S_MATCH": 1, "S_DELETE": 1, "S_SCAN": 1},
    {"bool": 1, "fin": 2, "fx": TOTAL_BITS}, 1, 1, 2, 2 + TOTAL_BITS,
    "typed rewrite/store primitives are native (indexed store: lookup/match/delete charged 1 per activation, "
    "the Rete-class assumption); fixed-point arithmetic is NOT native and is emulated at gate level (ripple-carry, shift-add); "
    "adjoint explicit over emulated arithmetic; sampling emulated",
)

B3 = Basis(
    "B3_STOCHASTIC_GENERATIVE_KERNEL",
    BOOL_OPS | FIN_OPS | FX_OPS | STOCH_OPS,
    {op: 1 for op in BOOL_OPS | FIN_OPS} | {"ADD": 1, "SUB": 1, "MUL": 2, "GT": 1, "THRESH": 1, "SHR": 1, "NEG": 1, "SAMPLE": 1, "SCORE": 2, "NORMALIZE": 2},
    _DESC_FULL, 1, 1, 2, _STORE_ENTRY,
    "native sample/score/normalize with arithmetic; stores emulated; adjoint explicit",
)

U = Basis(
    "U_UNIFORM_UNIVERSAL",
    set(UNIVERSE),
    {op: 1 for op in UNIVERSE},
    _DESC_FULL, 1, 1, 2, _STORE_ENTRY,
    "reference universal basis: every op native at uniform cost 1 — the upper band. Its desc is charged separately "
    "as the FLAT TRANSITION TABLE of the reference (computed analytically in references.py: |states|x|inputs| entries), "
    "which is what the uniform-cost interpreter must store to be a table machine",
)

P3 = Basis(
    "P3_COMPRESSED_PROGRAM_PARENT",
    set(UNIVERSE),
    {op: 1 for op in UNIVERSE},
    _DESC_FULL, 1, 1, 2, _STORE_ENTRY,
    "fair program parent (Codex Stage C-v2): the same programs with every op native at uniform cost 1 and desc = program length; "
    "the lower band",
)

import copy as _copy


def _indexed_variant(b, suffix="i"):
    v = _copy.deepcopy(b)
    v.name = b.name.replace("_", suffix + "_", 1)
    v.indexed_emulation = True
    v.note = b.note + " | DECLARED AMENDMENT R2: emulated store carries a charged binary index (1+ceil(log2(n+1)) compares per access; index maintenance on insert)"
    return v


B0i, B1i, B3i = _indexed_variant(B0), _indexed_variant(B1), _indexed_variant(B3)
INDEXED_VARIANTS = {b.name: b for b in (B0i, B1i, B3i)}

CANDIDATES = {b.name: b for b in (B0, B1, B2, B3)}
PARENTS = {b.name: b for b in (U, P3)}
ALL = {**CANDIDATES, **PARENTS}

# RV-377-035: a DECLARED hardware-priced parent column (tensor accelerator reading of P-N4/P-N5 in
# NEURAL_MORPHOLOGY_PARENT_ANALYSIS_V1): arithmetic and the adjoint are native at unit cost (MUL = 1, not 2), store
# operations are native but memory-bound (8 per activation), stochastic ops emulated. Not a member of ALL: no existing
# receipt is re-priced; used only by the CLIs that name it.
HW = Basis(
    "HW_TENSOR_PRICED",
    BOOL_OPS | FIN_OPS | FX_OPS | ADJ_OPS | STORE_OPS,
    {op: 1 for op in BOOL_OPS | FIN_OPS | FX_OPS | ADJ_OPS} | {op: 8 for op in STORE_OPS},
    _DESC_FULL, 1, 1, 2, _STORE_ENTRY,
    "declared hardware price vector: dense arithmetic and adjoints at unit cost, memory-bound store activations at 8x",
)
ALL_HW = {**ALL, HW.name: HW}
