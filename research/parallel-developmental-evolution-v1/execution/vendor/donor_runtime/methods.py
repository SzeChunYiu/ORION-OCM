"""Registered method languages, description-length admissibility and bits accounting.

Implements CL-D1 (admissibility), CL-D2 (structural placebo) and CL-D3
(bits of prior versus bits acquired) of
``docs/spec/COGNITIVE_LADDER_PROTOCOL_V1.md``.

Two languages are registered.

``GrundyRuleLanguage`` (per-heap rule, ``L1``)
    A hypothesis is ``(preperiod q, period p, values v)`` denoting

    ``G(n) = v[n]`` for ``n < q`` and ``G(n) = v[q + (n-q) mod p]`` otherwise.

    Every finite subtraction game has an eventually periodic Grundy sequence, so
    the true rule lies in this language for a large enough ``(q, p)`` bound.  The
    language also contains an enormous number of hypotheses that agree with any
    small sample and diverge later; those are the mandated decoys, and the
    structural placebo of CL-D2 is drawn from exactly that set.

``CombinerLanguage`` (multi-heap combiner, ``L2``)
    A hypothesis is one of nine registered functions from a tuple of per-heap
    Grundy values to a verdict.  ``XOR`` is the Sprague--Grundy answer.  Three of
    the other eight **agree with XOR on every position whose Grundy values are all
    0 or 1**, so a training draw confined to such positions cannot separate them.  Held-out
    worlds with Grundy values of 2 or more do separate them.  This is the
    "two representations fit training, disagree on held-out worlds" requirement
    of CL-3, built into the language rather than asserted about it.

The point of the whole module is that ``|L|``, ``|L_evidence|``, ``bits(M)`` and
``bits(D)`` are all *computed exactly*, never estimated.  Version-space counting
is analytic: for a fixed ``(q, p)`` each observation constrains exactly one
table slot, so the count factorises over slots and no enumeration is needed.

Parents: minimum description length (Rissanen); version-space learning (Mitchell);
Sprague--Grundy theory.  No novelty claimed for any of them.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

from games import SubtractionGame, Work

__all__ = [
    "GrundyRule",
    "GrundyRuleLanguage",
    "Combiner",
    "CombinerLanguage",
    "BitsAccounting",
    "Admissibility",
    "COMBINERS",
]

# --------------------------------------------------------------------------
# L1: periodic Grundy rules
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class GrundyRule:
    """A single hypothesis in ``GrundyRuleLanguage``."""

    preperiod: int
    period: int
    values: tuple[int, ...]

    def __post_init__(self) -> None:
        if self.period < 1:
            raise ValueError("period must be positive")
        if len(self.values) != self.preperiod + self.period:
            raise ValueError("values must have length preperiod + period")

    def slot(self, n: int) -> int:
        if n < self.preperiod:
            return n
        return self.preperiod + (n - self.preperiod) % self.period

    def grundy(self, n: int, work: Work | None = None) -> int:
        if work is not None:
            work.predicate_evaluations += 1
        return self.values[self.slot(n)]

    def is_p_position(self, n: int, work: Work | None = None) -> bool:
        return self.grundy(n, work=work) == 0

    @property
    def table_size(self) -> int:
        return len(self.values)


@dataclass(frozen=True)
class GrundyRuleLanguage:
    """The registered per-heap method language ``L1``.

    ``max_preperiod``, ``max_period`` and ``max_value`` are frozen before any
    protected outcome and are part of the pre-registration commitment.  They are
    reported in every method record, because a language chosen after seeing the
    answer is the first attack a reviewer will make (CL-D3, attack A1).
    """

    max_preperiod: int
    max_period: int
    max_value: int  # values range over 0 .. max_value - 1

    @property
    def language_id(self) -> str:
        return f"L1(q<={self.max_preperiod},p<={self.max_period},v<{self.max_value})"

    # ---- size -----------------------------------------------------------

    def size(self) -> int:
        """Exact ``|L1|``."""
        total = 0
        for q in range(self.max_preperiod + 1):
            for p in range(1, self.max_period + 1):
                total += self.max_value ** (q + p)
        return total

    def prior_bits(self) -> float:
        return math.log2(self.size())

    def code_bits(self, rule: GrundyRule) -> float:
        """``bits(M)``: a two-part code, shape then table.

        The shape is coded uniformly over the registered ``(q, p)`` grid and the
        table uniformly over ``max_value``.  A shorter code could be built for a
        favoured family; using the uniform one keeps the code independent of the
        answer, which is the property the compression test needs.
        """
        shapes = (self.max_preperiod + 1) * self.max_period
        return math.log2(shapes) + rule.table_size * math.log2(self.max_value)

    # ---- version space --------------------------------------------------

    def _slot_constraints(
        self, q: int, p: int, evidence: Sequence[tuple[int, int]]
    ) -> dict[int, int] | None:
        """Map slot -> forced value for shape ``(q, p)``; ``None`` on contradiction."""
        forced: dict[int, int] = {}
        for n, g in evidence:
            slot = n if n < q else q + (n - q) % p
            if slot in forced and forced[slot] != g:
                return None
            forced[slot] = g
        return forced

    def consistent_count(self, evidence: Sequence[tuple[int, int]]) -> int:
        """Exact ``|L1_evidence|`` given ``(position, grundy)`` observations.

        Analytic, not enumerative: for a fixed shape each observation pins one
        table slot, so the surviving count is ``max_value ** (free slots)``.
        """
        total = 0
        for q in range(self.max_preperiod + 1):
            for p in range(1, self.max_period + 1):
                forced = self._slot_constraints(q, p, evidence)
                if forced is None:
                    continue
                if any(v >= self.max_value or v < 0 for v in forced.values()):
                    continue
                free = (q + p) - len(forced)
                total += self.max_value ** free
        return total

    def consistent_count_binary(self, evidence: Sequence[tuple[int, bool]]) -> int:
        """Exact ``|L1_evidence|`` when only ``is_P`` (``G == 0``) was observed.

        A weaker channel: each observation pins a slot to zero or to any of the
        ``max_value - 1`` non-zero values.  Reported separately so the protocol
        can charge the machine for the channel it actually used.
        """
        total = 0
        for q in range(self.max_preperiod + 1):
            for p in range(1, self.max_period + 1):
                forced: dict[int, bool] = {}
                bad = False
                for n, is_p in evidence:
                    slot = n if n < q else q + (n - q) % p
                    if slot in forced and forced[slot] != is_p:
                        bad = True
                        break
                    forced[slot] = is_p
                if bad:
                    continue
                count = 1
                for is_p in forced.values():
                    count *= 1 if is_p else (self.max_value - 1)
                total += count * self.max_value ** ((q + p) - len(forced))
        return total

    # ---- induction ------------------------------------------------------

    def induce(
        self, evidence: Sequence[tuple[int, int]], work: Work | None = None
    ) -> GrundyRule | None:
        """Shortest-code hypothesis consistent with ``evidence``.

        Ties are broken by smallest ``(period, preperiod)`` and then lexically on
        the table, so induction is deterministic and its result does not depend
        on dictionary order.  Unconstrained slots are filled with ``0``; a slot
        the evidence never touched is not knowledge, and the extrapolation test
        of CL-D1(b) is what catches a rule that guessed one wrong.
        """
        work = work if work is not None else Work()
        best: GrundyRule | None = None
        best_bits = math.inf
        for p in range(1, self.max_period + 1):
            for q in range(self.max_preperiod + 1):
                work.expansions += 1
                forced = self._slot_constraints(q, p, evidence)
                if forced is None:
                    continue
                if any(v >= self.max_value or v < 0 for v in forced.values()):
                    continue
                values = tuple(forced.get(i, 0) for i in range(q + p))
                rule = GrundyRule(q, p, values)
                bits = self.code_bits(rule)
                if bits < best_bits:
                    best, best_bits = rule, bits
        return best

    def decoys(
        self,
        evidence: Sequence[tuple[int, int]],
        truth: Callable[[int], int],
        probe_upto: int,
        limit: int = 64,
    ) -> list[GrundyRule]:
        """Hypotheses consistent with ``evidence`` but wrong somewhere in
        ``(max evidence position, probe_upto]``.

        These are the mandated decoys of CL-D3 and the source pool for the
        CL-D2 structural placebo.  A decoy is precisely the memorisation
        hypothesis made concrete: it reproduces every training label and fails to
        generalise.  If the pool is empty the family is too easy and the rung
        must report ``PROTOTYPE_SCALE_TOO_SMALL_FOR_CLAIM``.
        """
        seen = max((n for n, _ in evidence), default=0)
        out: list[GrundyRule] = []
        for p in range(1, self.max_period + 1):
            for q in range(self.max_preperiod + 1):
                forced = self._slot_constraints(q, p, evidence)
                if forced is None:
                    continue
                if any(v >= self.max_value or v < 0 for v in forced.values()):
                    continue
                for fill in range(self.max_value):
                    values = tuple(forced.get(i, fill) for i in range(q + p))
                    rule = GrundyRule(q, p, values)
                    if any(rule.grundy(n) != truth(n) for n in range(seen + 1, probe_upto + 1)):
                        out.append(rule)
                        if len(out) >= limit:
                            return out
        return out


# --------------------------------------------------------------------------
# L2: multi-heap combiners
# --------------------------------------------------------------------------


def _xor(vs: Sequence[int]) -> int:
    acc = 0
    for v in vs:
        acc ^= v
    return acc


COMBINERS: dict[str, Callable[[Sequence[int]], int]] = {
    # the Sprague--Grundy answer
    "XOR": _xor,
    # decoys that agree with XOR whenever every value is 0 or 1
    "SUM_MOD_2": lambda vs: sum(vs) % 2,
    "COUNT_NONZERO_MOD_2": lambda vs: sum(1 for v in vs if v) % 2,
    "XOR_OF_PARITY": lambda vs: _xor([v % 2 for v in vs]),
    "MAX_MOD_2": lambda vs: (max(vs) if vs else 0) % 2,
    # decoys that agree with XOR on a single heap only
    "SUM": lambda vs: sum(vs),
    "SUM_MOD_3": lambda vs: sum(vs) % 3,
    "MAX": lambda vs: max(vs) if vs else 0,
    "MIN": lambda vs: min(vs) if vs else 0,
}

#: combiners that are provably indistinguishable from ``XOR`` when every
#: per-heap Grundy value lies in ``{0, 1}``.  Named here so a draw confined to
#: such values is recognised as non-discriminating *before* it is run.
#: This membership is verified exhaustively by the lane's tests rather than
#: asserted; ``MAX_MOD_2`` is deliberately NOT a member, because it already
#: disagrees with XOR at (1, 1), and listing it would have overstated the
#: language's decoy strength.
XOR_LOOKALIKES_ON_BINARY_VALUES = (
    "SUM_MOD_2",
    "COUNT_NONZERO_MOD_2",
    "XOR_OF_PARITY",
)


@dataclass(frozen=True)
class Combiner:
    name: str

    def verdict_is_p(self, values: Sequence[int], work: Work | None = None) -> bool:
        if work is not None:
            work.predicate_evaluations += 1
        return COMBINERS[self.name](values) == 0


@dataclass(frozen=True)
class CombinerLanguage:
    """The registered multi-heap method language ``L2``."""

    names: tuple[str, ...] = tuple(COMBINERS)

    @property
    def language_id(self) -> str:
        return "L2(" + ",".join(self.names) + ")"

    def size(self) -> int:
        return len(self.names)

    def prior_bits(self) -> float:
        return math.log2(self.size())

    def code_bits(self, combiner: Combiner) -> float:
        return math.log2(self.size())

    def consistent(
        self, evidence: Sequence[tuple[tuple[int, ...], bool]]
    ) -> list[Combiner]:
        """Every combiner reproducing all ``(grundy values, is_P)`` observations."""
        out = []
        for name in self.names:
            fn = COMBINERS[name]
            if all((fn(vs) == 0) == is_p for vs, is_p in evidence):
                out.append(Combiner(name))
        return out

    def consistent_count(
        self, evidence: Sequence[tuple[tuple[int, ...], bool]]
    ) -> int:
        return len(self.consistent(evidence))


# --------------------------------------------------------------------------
# CL-D3 bits accounting and CL-D1 admissibility
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class BitsAccounting:
    """CL-D3.  Reported with every method claim, without exception."""

    language_id: str
    language_size: int
    consistent_size: int
    prior_bits: float
    acquired_bits: float
    residual_bits: float

    @classmethod
    def build(cls, language_id: str, size: int, consistent: int) -> "BitsAccounting":
        if consistent < 1:
            raise ValueError("no hypothesis survives the evidence; the language is wrong")
        prior = math.log2(size)
        residual = math.log2(consistent)
        return cls(
            language_id=language_id,
            language_size=size,
            consistent_size=consistent,
            prior_bits=prior,
            acquired_bits=prior - residual,
            residual_bits=residual,
        )

    def as_dict(self) -> dict:
        return {
            "language_id": self.language_id,
            "language_size": self.language_size,
            "consistent_size": self.consistent_size,
            "prior_bits": round(self.prior_bits, 4),
            "acquired_bits": round(self.acquired_bits, 4),
            "residual_bits": round(self.residual_bits, 4),
        }


@dataclass(frozen=True)
class Admissibility:
    """CL-D1.  A method that is not ADMISSIBLE may be stored but never counted."""

    compression_ok: bool
    bits_method: float
    bits_data: float
    bits_residual: float
    extrapolation_ok: bool
    extrapolation_probes: int
    extrapolation_failures: int
    independence_ok: bool
    verdict: str

    @classmethod
    def build(
        cls,
        *,
        bits_method: float,
        bits_data: float,
        bits_residual: float,
        extrapolation_probes: int,
        extrapolation_failures: int,
        independence_ok: bool,
    ) -> "Admissibility":
        compression_ok = (bits_method + bits_residual) < bits_data
        extrapolation_ok = extrapolation_probes > 0 and extrapolation_failures == 0
        if not compression_ok:
            verdict = "INADMISSIBLE_NO_COMPRESSION"
        elif not extrapolation_ok:
            verdict = "INADMISSIBLE_NO_EXTRAPOLATION"
        elif not independence_ok:
            verdict = "INADMISSIBLE_CHECKER_NOT_INDEPENDENT"
        else:
            verdict = "ADMISSIBLE"
        return cls(
            compression_ok=compression_ok,
            bits_method=bits_method,
            bits_data=bits_data,
            bits_residual=bits_residual,
            extrapolation_ok=extrapolation_ok,
            extrapolation_probes=extrapolation_probes,
            extrapolation_failures=extrapolation_failures,
            independence_ok=independence_ok,
            verdict=verdict,
        )

    @property
    def admissible(self) -> bool:
        return self.verdict == "ADMISSIBLE"

    def as_dict(self) -> dict:
        return {
            "verdict": self.verdict,
            "compression_ok": self.compression_ok,
            "bits_method": round(self.bits_method, 4),
            "bits_data": round(self.bits_data, 4),
            "bits_residual": round(self.bits_residual, 4),
            "extrapolation_ok": self.extrapolation_ok,
            "extrapolation_probes": self.extrapolation_probes,
            "extrapolation_failures": self.extrapolation_failures,
            "independence_ok": self.independence_ok,
        }


def data_bits(evidence: Sequence[tuple[int, int]], max_value: int) -> float:
    """``bits(D)``: the cost of simply listing the observed labels.

    Positions are not charged, because the arm being compared against -- a
    verbatim cache -- is also given the positions.  Charging positions would
    inflate ``bits(D)`` and make compression easier to pass, which is the wrong
    direction for a test whose job is to exclude caches.
    """
    return len(evidence) * math.log2(max_value)
