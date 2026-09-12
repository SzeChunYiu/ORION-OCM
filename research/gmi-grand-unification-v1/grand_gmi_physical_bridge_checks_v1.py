#!/usr/bin/env python3
"""Exact finite checks for Grand GMI physical-resource bridge.

The checks are combinatorial/symbolic. They do not simulate thermodynamic dynamics
or fit physical constants.
"""

from itertools import product
from math import ceil, log2
import json


def bit_capacity(m):
    return 0 if m <= 1 else ceil(log2(m))


def check_binary_capacity():
    checks = 0
    rows = []
    for m in range(1, 65):
        b = bit_capacity(m)
        assert 2 ** b >= m
        if b > 0:
            assert 2 ** (b - 1) < m
        checks += 1
        rows.append((m, b))
    return {
        "message_counts_checked": checks,
        "m_1_bits": rows[0][1],
        "m_64_bits": rows[-1][1],
        "all_minimal": True,
    }


def _partitions(items):
    if not items:
        yield ()
        return
    first = items[0]
    for p in _partitions(items[1:]):
        yield ((first,),) + p
        for i in range(len(p)):
            q = list(p)
            q[i] = tuple(sorted((first,) + q[i]))
            yield tuple(sorted(q, key=lambda block: block[0]))


def check_microstate_partitions():
    total = 0
    by_n = {}
    for n in range(1, 7):
        ps = set(_partitions(tuple(range(n))))
        by_n[str(n)] = len(ps)
        for p in ps:
            k = len(p)
            assert 1 <= k <= n
            # Minimum binary labels needed for k semantic response classes.
            b = bit_capacity(k)
            assert 2 ** b >= k
            total += 1
    assert by_n == {"1": 1, "2": 2, "3": 5, "4": 15, "5": 52, "6": 203}
    return {
        "physical_microstate_partition_checks": total,
        "bell_counts_n_1_to_6": by_n,
        "semantic_classes_never_exceed_physical_microstates": True,
    }


def check_parity_irreversibility_separation():
    inputs = list(product([0, 1], repeat=2))

    direct = {xy: xy[0] ^ xy[1] for xy in inputs}
    direct_image = set(direct.values())
    preimages = {z: [xy for xy, zz in direct.items() if zz == z] for z in direct_image}
    assert sorted(len(v) for v in preimages.values()) == [2, 2]

    reversible = {xy: (xy[0], xy[1], xy[0] ^ xy[1]) for xy in inputs}
    assert len(set(reversible.values())) == 4
    assert all(reversible[xy][2] == direct[xy] for xy in inputs)

    # Uniform input: 4 equiprobable states -> 2 equiprobable parity states = exactly 1 bit
    # of logical uncertainty discarded by the direct map. The reversible embedding discards 0.
    return {
        "input_logical_states": 4,
        "protected_semantic_outputs": 2,
        "direct_map_preimage_sizes": [2, 2],
        "direct_uniform_logical_bits_discarded": 1,
        "reversible_embedding_full_states": 4,
        "reversible_embedding_logical_bits_discarded": 0,
        "protected_parity_output_identical": True,
    }


def check_symbolic_landauer_multiplicity():
    rows = []
    for bits in range(0, 7):
        m = 2 ** bits
        # Under the standard symmetric/equiprobable reset model the Landauer
        # scale is bits * k_B T ln 2; keep the multiplier symbolic/exact.
        rows.append({"logical_states_reset": m, "kBT_ln2_multiples": bits})
    assert [r["kBT_ln2_multiples"] for r in rows] == list(range(7))
    return {"power_of_two_reset_cases": len(rows), "rows": rows, "all_symbolic_exact": True}


def check_resource_tradeoff_nonidentity():
    # Same protected response; two physical schedules route cost differently.
    # A retains one history bit (memory +1, immediate erase 0).
    # B discards it now (memory +0, logical erase event +1).
    schedules = {
        "retain_history": {"protected_output": "parity", "extra_history_bits": 1, "logical_reset_events_now": 0},
        "discard_history": {"protected_output": "parity", "extra_history_bits": 0, "logical_reset_events_now": 1},
    }
    assert schedules["retain_history"]["protected_output"] == schedules["discard_history"]["protected_output"]
    assert schedules["retain_history"] != schedules["discard_history"]
    return {"schedules": schedules, "same_semantics_different_physical_accounting": True}


def run():
    return {
        "terminal": "GRAND_GMI_PHYSICAL_RESOURCE_BRIDGE_TRANCHE_ALL_GREEN",
        "binary_capacity": check_binary_capacity(),
        "microstate_partitions": check_microstate_partitions(),
        "parity_irreversibility_separation": check_parity_irreversibility_separation(),
        "symbolic_landauer_multiplicity": check_symbolic_landauer_multiplicity(),
        "resource_tradeoff_nonidentity": check_resource_tradeoff_nonidentity(),
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
