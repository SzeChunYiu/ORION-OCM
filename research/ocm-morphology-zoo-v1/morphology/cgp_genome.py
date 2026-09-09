"""E1 CGP encoding (MZ-D5): feed-forward integer-node re-encoding of the
E0 direct census space.

Encoding fit contract (demonstrated by hpc/mzd5_encoding_fit.py before any
scored use):

  1. SURJECTIVE onto CENSUS_BOUND_V1: every one of the 56,160 legal direct
     genomes has a canonical CGP genotype (identity wiring); the canonical
     encodings are trivially decodable.
  2. LEGAL BY CONSTRUCTION: node payloads live in a uniform index space
     [0, 129); slot-wise modulo folding guarantees decoded values stay
     inside each field's alphabet, so decode never leaves the census bound.
  3. SAME COMPILER PATH: decode() returns an OCMMorphologyGenomeV1 that is
     validated by the ordinary fail-closed compile_genome invariants — no
     encoding bypass exists.
  4. NEUTRAL REDUNDANCY: connection genes permute payloads between slots;
     many genotypes decode to the same organism (the classic CGP neutral
     network).  This changes the single-mutation neighborhood relative to
     the direct encoding, which is the property the D5 comparison studies.

Genotype: 7 nodes (one per categorical field of the direct space).  Node i
carries a payload gene p_i in Z_130 and a feed-forward wire gene w_i with
w_i in [0, i] (node i may route through any earlier node; w_0 = 0 fixed).
Decode applies the routing swaps in node order, then folds each payload
modulo its field alphabet.
"""
from __future__ import annotations

import random
from itertools import combinations
from typing import Dict, List, Sequence, Tuple

from morphology.direct_genome import CENSUS_BOUND_V1, _make
from morphology.schema import OCMMorphologyGenomeV1

UNIFORM_ALPHABET = 130  # lcm-cover of the largest field alphabet (subset code)

# slot order: F_arch, unit-subset code, T_family, Pi_arch, L, R, K
_SLOTS: Tuple[str, ...] = ("F_arch", "extras", "T_family", "Pi_arch",
                           "L", "R", "K")


def _subset_table(bound: Dict[str, Tuple[str, ...]]) -> List[Tuple[Tuple[str, ...], int]]:
    """Ordered (subset, code) table: code = rank of the subset among all
    subsets of size n, n ascending, lexicographic within size."""
    pool = sorted(bound["extra_units"])
    out = []
    code = 0
    for n in range(0, int(bound["max_extra_units"]) + 1):
        for sub in combinations(pool, n):
            out.append((sub, code))
            code += 1
    return out


_TABLE = _subset_table(CENSUS_BOUND_V1)
_TABLE_BY_CODE = {c: s for s, c in _TABLE}
_CODE_BY_SUBSET = {s: c for s, c in _TABLE}
_ALPHABETS: List[int] = [
    len(CENSUS_BOUND_V1["F_arch"]), len(_TABLE),
    len(CENSUS_BOUND_V1["T_family"]), len(CENSUS_BOUND_V1["Pi_arch"]),
    len(CENSUS_BOUND_V1["L"]), len(CENSUS_BOUND_V1["R"]),
    len(CENSUS_BOUND_V1["K"]),
]


class CGPGenomeV1:
    """Integer-node genotype; payload + feed-forward wire per node."""

    __slots__ = ("payload", "wires")

    def __init__(self, payload: Sequence[int], wires: Sequence[int]):
        if len(payload) != len(_SLOTS) or len(wires) != len(_SLOTS):
            raise ValueError("cgp genotype must have %d nodes" % len(_SLOTS))
        self.payload = [int(p) % UNIFORM_ALPHABET for p in payload]
        self.wires = []
        for i, w in enumerate(wires):
            self.wires.append(int(w) % (i + 1))  # w_i in [0, i], deterministic

    # -- bijective-with-canonical-form codec --------------------------------
    def decode_index_vector(self) -> List[int]:
        """Apply routing swaps in node order, then fold modulo alphabets."""
        v = list(self.payload)
        for i in range(1, len(v)):
            j = self.wires[i]
            if j != i:
                v[i], v[j] = v[j], v[i]
        return [vi % a for vi, a in zip(v, _ALPHABETS)]

    def decode(self) -> OCMMorphologyGenomeV1:
        idx = self.decode_index_vector()
        F = CENSUS_BOUND_V1["F_arch"][idx[0]]
        extras = _TABLE_BY_CODE[idx[1]]
        T = CENSUS_BOUND_V1["T_family"][idx[2]]
        Pi = CENSUS_BOUND_V1["Pi_arch"][idx[3]]
        L = CENSUS_BOUND_V1["L"][idx[4]]
        R = CENSUS_BOUND_V1["R"][idx[5]]
        K = CENSUS_BOUND_V1["K"][idx[6]]
        return _make(F, extras, T, Pi, L, R, K)

    @classmethod
    def encode(cls, g: OCMMorphologyGenomeV1) -> "CGPGenomeV1":
        """Canonical genotype of a direct genome: identity wiring."""
        bound = CENSUS_BOUND_V1
        idx: List[int] = []
        idx.append(bound["F_arch"].index(g.F_arch))
        extras = tuple(sorted(u.unit_type for u in g.U if u.unit_type != "fact_relation"))
        idx.append(_CODE_BY_SUBSET[extras])
        idx.append(bound["T_family"].index(g.T_family))
        idx.append(bound["Pi_arch"].index(g.Pi_arch))
        idx.append(bound["L"].index(g.L))
        idx.append(bound["R"].index(g.R))
        idx.append(bound["K"].index(g.K))
        return cls(idx, list(range(len(_SLOTS))))  # identity wires

    # -- variation ----------------------------------------------------------
    def clone(self) -> "CGPGenomeV1":
        return CGPGenomeV1(self.payload, self.wires)

    def mutate(self, rng: random.Random) -> "CGPGenomeV1":
        """Uniform single-gene mutation: payload or wire, then legality is
        guaranteed by construction (mod folding)."""
        child = self.clone()
        if rng.random() < 0.5:
            i = rng.randrange(len(_SLOTS))
            child.payload[i] = rng.randrange(UNIFORM_ALPHABET)
        else:
            i = rng.randrange(1, len(_SLOTS))
            child.wires[i] = rng.randrange(i + 1)
        return child

    def to_json_obj(self) -> Dict[str, object]:
        return {"encoding": "E1_cgp", "payload": list(self.payload),
                "wires": list(self.wires)}


def random_cgp_genome(rng: random.Random) -> CGPGenomeV1:
    """Uniform genotype sample (NOT uniform over organisms: neutral
    redundancy biases the induced distribution — measured, not assumed)."""
    return CGPGenomeV1([rng.randrange(UNIFORM_ALPHABET) for _ in _SLOTS],
                       [rng.randrange(i + 1) for i in range(len(_SLOTS))])
