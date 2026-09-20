"""Independent operational audit of the existing V9 context collision."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
V9 = "research/gmi-1068-r0-foundation-repair-v9/"
BINDINGS = {
    V9 + "RecoverabilityV9.lean": "164768fbda9a973001312c04e8ad07626de64b3fa0ec44fbd45391d7a0a704bd",
    V9 + "RESULT_V9.json": "bff9b4a3d539890a1ca7faf8b464d4148a8c46d92ef482caa7a7b09d9458b35b",
    V9 + "semantic_v9.py": "7e2f80870e0d8049b283d4adafcf582e75393d26d6b24112787cd233e0c3e979",
    V9 + "THEORY_V9.md": "af995866959e8228f020e6d2ca50d89934379c5944540a00c645897d3aa18452",
    "research/gmi-1068-grand-unified-v2-r0/ATOMIC_CHECKLIST_V1.json":
        "4cc262d491fbcdccf2b4c8656e80dcdb06e1795344500e46ac980ca09a679574",
    "research/gmi-1068-r1-minimal-process-core-v1/FREEZE_V1.md":
        "5f755106e6e5e2fcda6257d71e6eda6f2d895adf817834b2f2464685a491558a",
    "research/gmi-1068-r2-context-irreducibility-v1/FREEZE_V1.md":
        "cd3754eb383e2796c3fe06dc7e9fbb7cf17d9d0bca35bea983e43fbc6b6ae320",
}
ARROWS = ("i0", "i1", "a", "b")
ENDS = {"i0": (0, 0), "i1": (1, 1), "a": (0, 1), "b": (0, 1)}
OBJECTIVES = ({"i0": 0, "i1": 0, "a": 1, "b": 0},
              {"i0": 0, "i1": 0, "a": 0, "b": 1})


def need(condition, message):
    if not condition:
        raise ValueError(message)


def compose(first, second):
    need(first in ENDS and second in ENDS, "unknown arrow")
    need(ENDS[first][1] == ENDS[second][0], "illegal boundary")
    return second if first in ("i0", "i1") else first


def process_record():
    """Complete finite category data, not merely a selector name."""
    table = tuple((a, b, compose(a, b) if ENDS[a][1] == ENDS[b][0] else None)
                  for a in ARROWS for b in ARROWS)
    return ((0, 1), tuple((a, *ENDS[a]) for a in ARROWS),
            ((0, "i0"), (1, "i1")), table, ARROWS)


def histories(maximum):
    need(type(maximum) is int and maximum >= 0, "invalid history depth")
    layer = tuple((s, (), s) for s in (0, 1))
    result = list(layer)
    for _ in range(maximum):
        layer = tuple((s, path + (a,), ENDS[a][1]) for s, path, end in layer
                      for a in ARROWS if ENDS[a][0] == end)
        result.extend(layer)
    return tuple((s, path) for s, path, _ in result)


def evaluate(objective, start, path):
    need(type(start) is int and start in (0, 1), "invalid start")
    need(type(path) is tuple, "invalid history")
    need(type(objective) is dict and set(objective) == set(ARROWS)
         and all(type(v) is int and v in (0, 1) for v in objective.values()),
         "invalid common-domain evaluator")
    current, nonidentity = start, None
    for a in path:
        need(type(a) is str and a in ENDS, "unknown arrow")
        need(ENDS[a][0] == current, "ill-typed history")
        current = ENDS[a][1]
        if a in ("a", "b"):
            nonidentity = a
    return objective[nonidentity if nonidentity else "i" + str(start)]


def same_typed_data(first, second):
    if type(first) is not type(second):
        return False
    if type(first) is tuple:
        return len(first) == len(second) and all(same_typed_data(a, b)
                                               for a, b in zip(first, second))
    return first == second


def verify_collision(first, second, objective_a, objective_b):
    need(same_typed_data(first, second) and same_typed_data(first, process_record()),
         "different or invalid process laws")
    need(type(objective_a) is dict and type(objective_b) is dict, "invalid evaluator maps")
    need(tuple(objective_a) == tuple(objective_b) == ARROWS, "different evaluator domains")
    ranks = tuple(tuple(evaluate(o, 0, (a,)) for a in ("a", "b"))
                  for o in (objective_a, objective_b))
    need(ranks == ((1, 0), (0, 1)), "no registered strict ranking reversal")
    return ranks


def audit(repo_root=None):
    root = ROOT if repo_root is None else Path(repo_root)
    for name, expected in BINDINGS.items():
        need(hashlib.sha256((root / name).read_bytes()).hexdigest() == expected,
             "source custody mismatch: " + name)
    rows = json.loads((root / "research/gmi-1068-grand-unified-v2-r0/ATOMIC_CHECKLIST_V1.json").read_text())["rows"]
    titles = {r["id"]: r["title"] for r in rows}
    need(titles["GMI2-R2-002"] == "prove context not derived from process law",
         "original context requirement changed")
    first_process, second_process = process_record(), process_record()
    ranks = verify_collision(first_process, second_process, *OBJECTIVES)
    coverage = dict(typed_histories=0, evaluator_disagreements=0,
                    identity_only_histories=0, padded_ranking_reversals=0,
                    full_process_comparisons=1, path_admission_comparisons=0)
    first_domain, second_domain = histories(12), histories(12)
    need(first_domain == second_domain, "different actual history domains")
    for start, path in first_domain:
        admitted = tuple(all(a in process[-1] for a in path)
                         for process in (first_process, second_process))
        need(admitted == (True, True), "different path admission")
        coverage["path_admission_comparisons"] += 1
        values = tuple(evaluate(o, start, path) for o in OBJECTIVES)
        coverage["typed_histories"] += 1
        coverage["evaluator_disagreements"] += values[0] != values[1]
        identity_only = all(a in ("i0", "i1") for a in path)
        coverage["identity_only_histories"] += identity_only
        need(identity_only == (values == (0, 0)), "history normalization mismatch")
    for before in range(6):
        for after in range(6):
            paths = tuple(("i0",) * before + (a,) + ("i1",) * after for a in ("a", "b"))
            values = tuple(tuple(evaluate(o, 0, p) for p in paths) for o in OBJECTIVES)
            need(values == ranks, "padding changes opposite rankings")
            coverage["padded_ranking_reversals"] += 1
    return {"atom_id": "GMI2-R2-002", "bindings": dict(BINDINGS),
            "coverage": coverage, "ranking_witness": [list(row) for row in ranks],
            "scope": "NO_UNIFORM_DECODER_OVER_CLASSES_CONTAINING_BOTH_EXPANSIONS"}
