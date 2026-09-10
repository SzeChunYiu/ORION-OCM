"""M1 frozen semantic partition emitter (entry gate (d) of the M1 freeze).

Enumerates polynomial targets of the registered grammar (src/ocm/learning/methods.py,
primitives inc/dec/double/square) and partitions them BY SEMANTIC PROPERTY of the
polynomial normal form: degree band x monomial-support band x coefficient-structure
class. The predicate is structural on the normal form only -- never on instance ids,
program spellings or seeds. Seeds rank members WITHIN a partition; they never move a
member across partitions (freeze: semantic_partitions.rule).

Streams (train / validation / test / protected) are disjoint by construction and the
emitter asserts ZERO shared normal forms. The protected fresh-obligation evaluation
set is sha256-bound before any arm runs (freeze: semantic_partitions.protected_set).
"""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from itertools import product
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from ocm.learning import methods as M  # noqa: E402  (bound AS-IS)

SCHEMA = "OCM_M1_PARTITIONS"
VERSION = "V1"
FROZEN_SEED = "orion-ocm-m1-semantic-partition-v1"
STREAMS = ("train", "validation", "test", "protected")

DEGREE_BANDS = ((0, 1, "DEG_0_1"), (2, 3, "DEG_2_3"), (4, 7, "DEG_4_7"), (8, 10**9, "DEG_8_PLUS"))
SUPPORT_BANDS = ((1, 2, "SUP_LE2"), (3, 4, "SUP_3_4"), (5, 10**9, "SUP_GE5"))
COEFFICIENT_CLASSES = ("COEFF_RATIONAL", "COEFF_INT_SMALL", "COEFF_INT_LARGE")
INT_SMALL_MAGNITUDE = 16


def coefficient_class(coefficients) -> str:
    """Structural predicate on the normal form: rational > integer magnitude."""
    values = [Fraction(c) for c in coefficients]
    if any(c.denominator != 1 for c in values):
        return "COEFF_RATIONAL"
    return "COEFF_INT_SMALL" if all(abs(c) <= INT_SMALL_MAGNITUDE for c in values) else "COEFF_INT_LARGE"


def semantic_class(coefficients) -> dict:
    """The frozen semantic predicate: degree band, support band, coefficient class."""
    values = [Fraction(c) for c in coefficients]
    degree = max((i for i, c in enumerate(values) if c != 0), default=0)
    support = sum(1 for c in values if c != 0)
    degree_band = next(name for lo, hi, name in DEGREE_BANDS if lo <= degree <= hi)
    support_band = next(name for lo, hi, name in SUPPORT_BANDS if lo <= support <= hi)
    return {"degree": degree, "degree_band": degree_band,
            "support": support, "support_band": support_band,
            "coefficient_class": coefficient_class(values)}


def minimal_length_population(max_length: int) -> dict:
    """Every exact polynomial identity reachable by programs up to max_length,
    with its minimum primitive program length. Task identity is the normal form."""
    best: dict[str, tuple] = {}
    for length in range(max_length + 1):
        for program in product(M.PRIMITIVES, repeat=length):
            coefficients = M.normal_form(program)
            task = M.PolynomialTask(f"minlen-{length}", coefficients)
            best.setdefault(task.fingerprint, (length, coefficients))
    return best


def stable_rank(salt: str, fingerprint: str) -> str:
    return hashlib.sha256((salt + "\0" + fingerprint).encode()).hexdigest()


def emit(max_length: int, seed: str, per_stream: int) -> dict:
    population = minimal_length_population(max_length)
    buckets: dict[tuple, list] = {}
    for fingerprint, (min_length, coefficients) in population.items():
        cls = semantic_class(coefficients)
        key = (cls["degree_band"], cls["support_band"], cls["coefficient_class"])
        buckets.setdefault(key, []).append((fingerprint, min_length, coefficients, cls))
    streams = {name: [] for name in STREAMS}
    contribution = {}
    for key in sorted(buckets):
        members = sorted(buckets[key], key=lambda m: (stable_rank(seed + ":" + key[0] + key[1] + key[2], m[0]), m[0]))
        take = min(per_stream, len(members) // len(STREAMS))
        contribution["/".join(key)] = take
        if take == 0:
            continue
        for index, stream in enumerate(STREAMS):
            for fingerprint, min_length, coefficients, cls in members[index * take:(index + 1) * take]:
                streams[stream].append({
                    "task_id": f"{stream}:{key[0]}:{key[1]}:{key[2]}:{len(streams[stream])}",
                    "coefficients": [str(c) for c in coefficients],
                    "normal_form_digest": fingerprint,
                    "min_primitive_length": min_length,
                    "semantic_class": cls,
                })
    digests = {name: {row["normal_form_digest"] for row in rows} for name, rows in streams.items()}
    shared = set.intersection(*[digests[name] for name in STREAMS]) if all(digests.values()) else set()
    if not all(digests.values()):
        raise SystemExit(f"PARTITION_EMISSION_FAILED: empty stream (max_length={max_length}, per_stream={per_stream})")
    if shared:
        raise SystemExit(f"PARTITION_EMISSION_FAILED: {len(shared)} shared normal forms across streams")
    protected_sha = hashlib.sha256("\n".join(sorted(digests["protected"])).encode()).hexdigest()
    return {
        "schema": SCHEMA, "version": VERSION, "frozen_seed": seed,
        "grammar": {"primitives": list(M.PRIMITIVES), "max_program_length": max_length,
                    "checker": M.CHECKER, "source": "src/ocm/learning/methods.py (bound AS-IS)"},
        "class_definitions": {
            "degree_bands": [{"lo": lo, "hi": hi, "name": n} for lo, hi, n in DEGREE_BANDS],
            "support_bands": [{"lo": lo, "hi": hi, "name": n} for lo, hi, n in SUPPORT_BANDS],
            "coefficient_classes": COEFFICIENT_CLASSES,
            "predicate": "structural on the polynomial normal form (degree/support/coefficient structure); "
                         "never on instance ids, program spellings or seeds",
        },
        "selection_rule": "within-partition stable_rank(seed+partition, digest) ordering, then "
                          "contiguous slices per stream; seeds rank WITHIN a partition and never move "
                          "the partition boundary",
        "per_class_train_contribution": contribution,
        "streams": streams,
        "disjointness_assertion": {"checked": True, "shared_normal_forms": 0},
        "protected_set_sha256": protected_sha,
        "difficulty_axis": "held FIXED across checkpoints (freeze semantic_partitions.difficulty_axis)",
        "generated_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "governing_freeze": "M1_NATIVE_ACQUISITION_PROTOCOL_FREEZE_V1.json",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--max-length", type=int, default=8)
    parser.add_argument("--seed", default=FROZEN_SEED)
    parser.add_argument("--per-stream", type=int, default=8,
                        help="members drawn per stream per semantic partition (capped by partition size)")
    parser.add_argument("--toy", action="store_true", help="tiny selftest parameters (never for scored emission)")
    args = parser.parse_args()
    if args.toy:
        args.max_length, args.per_stream = 4, 2
    document = emit(args.max_length, args.seed, args.per_stream)
    args.out.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    counts = {name: len(document["streams"][name]) for name in STREAMS}
    print(json.dumps({"written": str(args.out), "streams": counts,
                      "partitions_contributing": sum(1 for v in document["per_class_train_contribution"].values() if v),
                      "protected_set_sha256": document["protected_set_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
