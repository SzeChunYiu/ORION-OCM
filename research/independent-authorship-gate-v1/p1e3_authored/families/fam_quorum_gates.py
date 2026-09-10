"""Quorum Gates: a gate fires only once k of its n input seats are lit.

Fixed seed 1102. Six instances; quorum size, seat count, which seats start
lit, seat costs, and gate chaining vary. Every k-subset of seats gets its own
rule, so partial quorums fail and the cheapest completion is a real choice.
"""

from itertools import combinations
from families._common import make_instance

FAMILY_NAME = "Quorum Gates"
FAMILY_BLURB = ("Committee gates that open only when a quorum of their seats is "
                "lit; seats cost different amounts and gates feed gates, so the "
                "question is which cheapest seat bundle completes a quorum.")
SEED = 1102

# (gate spec list, base seats, weights, goals)
# gate spec: (name, k, seats)
SPECS = [
    ([("gate_a", 2, ["s1", "s2", "s3"])], ["s1"],
     {"s2": 4, "s3": 7}, ["gate_a"]),
    ([("gate_a", 3, ["s1", "s2", "s3", "s4", "s5"])], ["s1", "s2"],
     {"s3": 5, "s4": 5, "s5": 6}, ["gate_a"]),
    ([("gate_a", 2, ["s1", "s2", "s3"]),
      ("gate_b", 2, ["s3", "s4", "gate_a"])], ["s1", "s4"],
     {"s2": 3, "s3": 9}, ["gate_b"]),
    ([("gate_a", 3, ["s1", "s2", "s3", "s4"]),
      ("gate_b", 2, ["gate_a", "s5", "s6"])], ["s1", "s2"],
     {"s3": 2, "s4": 8, "s5": 4, "s6": 6}, ["gate_b"]),
    ([("gate_a", 2, ["s1", "s2", "s3"]),
      ("gate_b", 2, ["s4", "s5", "s6"]),
      ("gate_c", 2, ["gate_a", "gate_b", "s7"])], ["s1", "s4"],
     {"s2": 5, "s3": 5, "s5": 3, "s6": 7, "s7": 12}, ["gate_c"]),
    ([("gate_a", 3, ["s1", "s2", "s3", "s4", "s5"]),
      ("gate_b", 3, ["gate_a", "s4", "s5", "s6"])], ["s2", "s3"],
     {"s1": 6, "s4": 2, "s5": 9, "s6": 3}, ["gate_b"]),
]


def emit(seed: int) -> list:
    assert seed == SEED, "family seed is pinned"
    out = []
    for idx, (gates, base, base_weights, goals) in enumerate(SPECS, 1):
        weights = dict(base_weights)
        elements = set(base) | set(weights) | set(goals)
        implications = []
        for name, k, seats in gates:
            elements.update(seats)
            elements.add(name)
            for combo in combinations(seats, k):
                implications.append({"if": list(combo), "then": [name]})
            weights.setdefault(name, 99)
        core = {
            "elements": sorted(elements),
            "implications": implications,
            "base": base,
            "excluded": [],
            "weights": weights,
            "goals": goals,
        }
        out.append(make_instance(FAMILY_NAME, "quorum_gates_%02d" % idx, core, {
            "gates": [{"gate": n, "quorum": k, "seats": s} for n, k, s in gates],
            "pre_lit_seats": base,
            "tier": idx,
            "intent_note": "cheapest seat bundle completing the top quorum",
        }))
    return out
