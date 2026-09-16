from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from fractions import Fraction
from itertools import permutations, product
from pathlib import Path
from typing import Dict, FrozenSet, Iterable, Mapping, Sequence, Tuple
import importlib.util
import json
import math
import sys

SOURCE_MAIN = "367e14e9296cf79924ce56d89fad34b3769acb5d"
FREEZE_COMMIT = "f5195a8ae04cce0d96d0e005f5cd39c38a4717ef"
PARENT_MANIFEST_BLOB = "cfe890b276cef0bdb2424877de878b9173547cf2"
PARENT_RECEIPT_BLOB = "5d2948b9c04c84a46f6625e043753a489895478f"
CLAIM_CEILING = "GMI_FINITE_GRAMMAR_BIAS_AND_REMINT_BOUNDARY_AT_REGISTERED_G0_SCOPE"
FORBIDDEN_PROMOTIONS = (
    "UNBIASED_G0",
    "UNIVERSAL_ALGORITHMIC_PRIOR",
    "KOLMOGOROV_NEUTRALITY",
    "GRAMMAR_REPRESENTATION_INVARIANT_UNIVERSALLY",
    "SEARCH_REACHABILITY_INVARIANT_UNIVERSALLY",
    "MORPHOLOGY_SELECTION_INVARIANT_UNDER_ARBITRARY_GRAMMAR",
    "ALL_GRAMMARS_EQUIVALENT",
    "COMPLETE_GMI",
)
PROTECTED_INPUTS = ((), (0,), (1,))
STEP_BUDGET = 6


def _load_parent():
    parent_path = Path(__file__).resolve().parents[1] / "gmi-833-g0-register-core-v1" / "g0_register_core_v1.py"
    spec = importlib.util.spec_from_file_location("gmi833_g0_parent", parent_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load #868 parent")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PARENT = _load_parent()


def instruction_key(instr: object) -> Tuple[str, ...]:
    if isinstance(instr, PARENT.Halt):
        return ("HALT",)
    if isinstance(instr, PARENT.Read):
        return ("READ", instr.register, instr.next_label)
    if isinstance(instr, PARENT.Inc):
        return ("INC", instr.register, instr.next_label)
    if isinstance(instr, PARENT.Emit):
        return ("EMIT", instr.register, instr.next_label)
    if isinstance(instr, PARENT.DecJz):
        return ("DECJZ", instr.register, instr.nonzero_label, instr.zero_label)
    raise TypeError(f"unsupported instruction {type(instr)!r}")


def instruction_options(labels: Sequence[str]) -> Tuple[object, ...]:
    labels = tuple(labels)
    r = "r"
    out = [PARENT.Halt()]
    out.extend(PARENT.Read(r, nxt) for nxt in labels)
    out.extend(PARENT.Inc(r, nxt) for nxt in labels)
    out.extend(PARENT.Emit(r, nxt) for nxt in labels)
    out.extend(PARENT.DecJz(r, nz, z) for nz in labels for z in labels)
    return tuple(out)


def presentation_id(label_count: int, *instructions: object) -> str:
    payload = [label_count]
    payload.extend([list(instruction_key(i)) for i in instructions])
    return json.dumps(payload, separators=(",", ":"))


def enumerate_presentations() -> Dict[str, object]:
    presentations: Dict[str, object] = {}
    for i0 in instruction_options(("L0",)):
        pid = presentation_id(1, i0)
        presentations[pid] = PARENT.Program(("r",), "L0", {"L0": i0})
    opts2 = instruction_options(("L0", "L1"))
    for i0, i1 in product(opts2, repeat=2):
        pid = presentation_id(2, i0, i1)
        presentations[pid] = PARENT.Program(("r",), "L0", {"L0": i0, "L1": i1})
    if len(presentations) != 126:
        raise RuntimeError("registered presentation count drift")
    return presentations


def semantic_signature(program: object) -> Tuple[Tuple[str, Tuple[int, ...]], ...]:
    rows = []
    for inp in PROTECTED_INPUTS:
        result = PARENT.execute(program, inp, STEP_BUDGET)
        rows.append((result.terminal, tuple(result.output)))
    return tuple(rows)


def semantic_key(signature: Tuple[Tuple[str, Tuple[int, ...]], ...]) -> str:
    return json.dumps([[terminal, list(output)] for terminal, output in signature], separators=(",", ":"))


def _pid_payload(pid: str):
    return json.loads(pid)


def build_adjacency(presentations: Mapping[str, object]) -> Dict[str, FrozenSet[str]]:
    nodes = tuple(sorted(presentations))
    one = [n for n in nodes if _pid_payload(n)[0] == 1]
    two = [n for n in nodes if _pid_payload(n)[0] == 2]
    adj: Dict[str, set[str]] = {n: set() for n in nodes}

    # Fixed-label-count mutation: exactly one instruction differs.
    for group in (one, two):
        for idx, a in enumerate(group):
            pa = _pid_payload(a)
            for b in group[idx + 1 :]:
                pb = _pid_payload(b)
                if sum(x != y for x, y in zip(pa[1:], pb[1:])) == 1:
                    adj[a].add(b)
                    adj[b].add(a)

    # Add/delete L1 while preserving a one-label-well-typed L0 instruction.
    for a in one:
        a0 = _pid_payload(a)[1]
        for b in two:
            if _pid_payload(b)[1] == a0:
                adj[a].add(b)
                adj[b].add(a)

    return {k: frozenset(v) for k, v in adj.items()}


def start_node(presentations: Mapping[str, object]) -> str:
    target = presentation_id(1, PARENT.Halt())
    if target not in presentations:
        raise RuntimeError("HALT start presentation missing")
    return target


def bfs_distances(adjacency: Mapping[str, FrozenSet[str]], starts: Iterable[str]) -> Dict[str, int]:
    starts = tuple(starts)
    if not starts:
        raise ValueError("empty start set")
    dist: Dict[str, int] = {}
    q: deque[str] = deque()
    for s in starts:
        if s not in adjacency:
            raise ValueError("start outside graph")
        if s not in dist:
            dist[s] = 0
            q.append(s)
    while q:
        u = q.popleft()
        for v in sorted(adjacency[u]):
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def wave_distances(adjacency: Mapping[str, FrozenSet[str]], starts: Iterable[str]) -> Dict[str, int]:
    wave = set(starts)
    if not wave:
        raise ValueError("empty start set")
    if any(x not in adjacency for x in wave):
        raise ValueError("start outside graph")
    dist = {x: 0 for x in wave}
    reached = set(wave)
    radius = 0
    while True:
        next_wave = set(reached)
        for u in reached:
            next_wave.update(adjacency[u])
        new = next_wave - reached
        if not new:
            return dist
        radius += 1
        for v in new:
            dist[v] = radius
        reached = next_wave


def _fraction_text(x: Fraction) -> str:
    return f"{x.numerator}/{x.denominator}"


def registered_census() -> Dict[str, object]:
    presentations = enumerate_presentations()
    semantics = {pid: semantic_key(semantic_signature(program)) for pid, program in presentations.items()}
    lengths = {pid: int(_pid_payload(pid)[0]) for pid in presentations}
    adjacency = build_adjacency(presentations)
    start = start_node(presentations)
    bfs = bfs_distances(adjacency, (start,))
    wave = wave_distances(adjacency, (start,))
    if bfs != wave:
        raise RuntimeError("BFS/wave reachability mismatch")

    classes: Dict[str, list[str]] = defaultdict(list)
    for pid, sem in semantics.items():
        classes[sem].append(pid)

    class_rows = []
    for sem in sorted(classes):
        nodes = classes[sem]
        lens = [lengths[p] for p in nodes]
        ds = [bfs[p] for p in nodes]
        n1 = sum(x <= 1 for x in lens)
        n2 = sum(x <= 2 for x in lens)
        class_rows.append(
            {
                "semantic_key": sem,
                "multiplicity": len(nodes),
                "L_G": min(lens),
                "N_B1": n1,
                "N_B2": n2,
                "Q_B1": _fraction_text(Fraction(n1, 5)),
                "Q_B2": _fraction_text(Fraction(n2, 126)),
                "d_G": min(ds),
                "A_k0": sum(d <= 0 for d in ds),
                "A_k1": sum(d <= 1 for d in ds),
                "A_k2": sum(d <= 2 for d in ds),
            }
        )

    undirected_edges = sum(len(v) for v in adjacency.values()) // 2
    return {
        "presentation_count": len(presentations),
        "one_label_presentations": sum(lengths[p] == 1 for p in presentations),
        "two_label_presentations": sum(lengths[p] == 2 for p in presentations),
        "semantic_class_count": len(classes),
        "undirected_edge_count": undirected_edges,
        "presentation_distance_histogram": {str(k): v for k, v in sorted(Counter(bfs.values()).items())},
        "class_multiplicity_histogram": {str(k): v for k, v in sorted(Counter(len(v) for v in classes.values()).items())},
        "class_shortest_length_histogram": {str(k): v for k, v in sorted(Counter(r["L_G"] for r in class_rows).items())},
        "class_distance_histogram": {str(k): v for k, v in sorted(Counter(r["d_G"] for r in class_rows).items())},
        "reachable_class_count_by_radius": {
            str(k): sum(r["d_G"] <= k for r in class_rows) for k in (0, 1, 2)
        },
        "class_rows": class_rows,
        "bfs_wave_mismatches": 0,
        "all_presentations_reachable": len(bfs) == len(presentations),
    }
