"""Scoped exact-recall and witness-vs-class checks, not a general GMI solver."""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from typing import Iterable


def exact_recall_requirement(records: int, bits_per_record: int = 1) -> dict:
    """Fixed decoder, no external data, every dataset and every index, zero error."""
    if type(records) is not int or records < 0:
        raise ValueError("records must be a nonnegative integer")
    if type(bits_per_record) is not int or bits_per_record < 1:
        raise ValueError("positive integer bits_per_record required")
    return {
        "minimum_dataset_dependent_bits": records * bits_per_record,
        "bound_kind": "EXACT_ALL_DATASETS_ALL_INDICES_FIXED_DECODER",
        "charged_information": "all dataset-dependent state, code, external storage and precision",
        "not_implied": "a fixed number of unbounded-precision words is a fixed bit budget",
    }


def parity_compression_collision(records: int = 3) -> dict:
    """Exhibit a failing one-bit encoder; theorem covers all encoders by counting."""
    if type(records) is not int or not 2 <= records <= 16:
        raise ValueError("microscope requires 2 through 16 binary records")
    seen = {}
    for data in product((0, 1), repeat=records):
        encoded = sum(data) % 2
        if encoded in seen:
            other = seen[encoded]
            index = next(i for i in range(records) if other[i] != data[i])
            return {"dataset_a": other, "dataset_b": data, "same_encoded_bit": encoded,
                    "separating_query_index": index,
                    "required_answers": [other[index], data[index]]}
        seen[encoded] = data
    raise AssertionError("counting promised a collision")


@dataclass(frozen=True)
class ExactBitMemory:
    """Constructive finite recall control with explicitly charged byte payload.

    Python object/allocator overhead, record-count metadata and program description
    are NOT included in payload_bits; this is not a whole-process or energy meter.
    The mathematical model treats N as part of the fixed public task contract.
    """
    records: int
    payload: bytes

    def __post_init__(self):
        if type(self.records) is not int or self.records < 0:
            raise ValueError("records must be nonnegative integer")
        if type(self.payload) is not bytes or len(self.payload) != (self.records + 7) // 8:
            raise ValueError("payload capacity disagrees with declared record count")
        if self.records % 8 and self.payload[-1] >> (self.records % 8):
            raise ValueError("noncanonical nonzero padding")

    @classmethod
    def from_records(cls, values: Iterable[int]) -> "ExactBitMemory":
        data = tuple(values)
        if any(type(x) is not int or x not in (0, 1) for x in data):
            raise ValueError("records must be integer bits, not arbitrary values")
        packed = bytearray((len(data) + 7) // 8)
        for i, bit in enumerate(data):
            packed[i // 8] |= bit << (i % 8)
        return cls(len(data), bytes(packed))

    def recall(self, index: int) -> int:
        if type(index) is not int or not 0 <= index < self.records:
            raise IndexError("query outside declared record set")
        return (self.payload[index // 8] >> (index % 8)) & 1

    @property
    def payload_bits(self) -> int:
        return 8 * len(self.payload)


def witness_comparison(witness_cost: Fraction, rival_cost: Fraction,
                       target_class_lower_bound: Fraction | None = None) -> dict:
    """Class exclusion is CONDITIONAL on an externally justified valid bound.

    Exact rational arithmetic avoids rounding a cost tie into a strict separation.
    This function checks arithmetic, NOT semantic admissibility or proof validity.
    """
    vals = [witness_cost, rival_cost]
    if target_class_lower_bound is not None:
        vals.append(target_class_lower_bound)
    if any(type(v) not in (int, Fraction) or v < 0 for v in vals):
        raise ValueError("nonnegative exact rational costs required")
    if target_class_lower_bound is not None and target_class_lower_bound > witness_cost:
        raise ValueError("lower bound contradicts supplied admissible target witness")
    witness_dominated = rival_cost < witness_cost
    class_excluded = (target_class_lower_bound is not None and
                      rival_cost < target_class_lower_bound)
    status = ("TARGET_CLASS_EXCLUDED_GIVEN_VALID_BOUND" if class_excluded else
              "WITNESS_DOMINATED_ONLY" if witness_dominated else
              "NO_STRICT_DOMINANCE_ESTABLISHED")
    return {"status": status, "witness_dominated": witness_dominated,
            "target_class_exclusion_conditional": class_excluded,
            "semantic_admissibility_checked": False,
            "lower_bound_validity_checked": False}


def summary() -> dict:
    memory = ExactBitMemory.from_records((0, 1, 1, 0, 1, 0, 1, 1, 0))
    return {
        "kind": "SAME_AUTHOR_DEVELOPMENT_LOGIC_AND_EXECUTION_CONTROLS",
        "recall_requirement": exact_recall_requirement(128),
        "collision": parity_compression_collision(),
        "constructive_recall": {"records": memory.records, "payload_bits": memory.payload_bits,
                                "outputs": [memory.recall(i) for i in range(memory.records)]},
        "dominated_witness_not_class": {"target_witness_cost": 10, "rival_cost": 5,
                                       "other_target_cost": 1,
                                       "assessment": witness_comparison(10, 5)},
        "valid_bound_separation": witness_comparison(10, 5, 6),
    }
