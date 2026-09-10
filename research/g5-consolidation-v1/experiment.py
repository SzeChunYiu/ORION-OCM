"""Prospective G5.4 cognitive consolidation study.

Research-only. G2/G3 polynomial macros are reused as *schemas*, not as confirmatory
task outcomes. Training items are explicit program traces drawn from a fresh salt
and a disjoint length stratum (4–5), so length-6/7/8 G2/G3 identities cannot leak
in as held-out confirmation.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, field
import hashlib
from itertools import product
import json
import os
from pathlib import Path
import sys
import tempfile
import time
from typing import Any, Iterable

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "src"
sys.path.insert(0, str(SRC))

from ocm.kso.ids import canonical_json, content_hash
from ocm.kso.space import Atom, Hyperedge
from ocm.kso.types import Scope
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.learning import methods as M
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.evidence import Channel

METHOD_BLOB = "50323a33418b8ef8bb6500ddeba4b9d1f795e9e3"
TRAIN_SALT = "orion-ocm-g5-consolidation-train-v1"
HELDOUT_SALT = "orion-ocm-g5-consolidation-heldout-v1"
TRAIN_N = 40
HELDOUT_N = 12
UNIQUE_COUNTS = {"SDS": 9, "SII": 8, "SDD": 8, "EXC": 9}
DUPLICATE_COUNTS = {"SDS": 2, "SII": 2, "SDD": 2}
HELDOUT_COUNTS = {"SDS": 4, "SII": 4, "SDD": 4}
PROGRAM_LENGTHS = (4, 5)
MAX_PRIMITIVE_LENGTH = 5
FRAGMENT_MIN_LENGTH = 2
FRAGMENT_MAX_LENGTH = 3
LIBRARY_CAP = 8
LIBRARY_MIN_SUPPORT = 2
SCOPE = Scope.of("polynomial-cognitive-consolidation.v1")
SCHEMAS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("SDS", ("square", "dec", "square")),
    ("SII", ("square", "inc", "inc")),
    ("SDD", ("square", "dec", "dec")),
)
SCHEMA_PATTERNS = {name: pattern for name, pattern in SCHEMAS}
SCHEMA_ORDER = tuple(name for name, _pattern in SCHEMAS)


def git_blob_sha1(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def stable_rank(salt: str, fingerprint: str) -> str:
    return hashlib.sha256((salt + "\0" + fingerprint).encode()).hexdigest()


def program_task(program: tuple[str, ...], task_id: str = "trace") -> M.PolynomialTask:
    return M.PolynomialTask(task_id, M.normal_form(program))


def program_fingerprint(program: tuple[str, ...]) -> str:
    return program_task(program).fingerprint


def payload_bytes(value: Any) -> int:
    return len(canonical_json(value).encode("utf-8"))


def coefficients_as_strings(coefficients) -> list[str]:
    return [str(c) for c in coefficients]


@dataclass(frozen=True)
class Trace:
    episode_id: str
    program: tuple[str, ...]
    schema_id: str | None
    occurrence: int | None
    residual_identity: str

    @property
    def coefficients(self):
        return M.normal_form(self.program)

    @property
    def fingerprint(self) -> str:
        return program_fingerprint(self.program)

    def as_dict(self) -> dict[str, Any]:
        return {
            "episode_id": self.episode_id,
            "program": list(self.program),
            "schema_id": self.schema_id,
            "occurrence": self.occurrence,
            "residual_identity": self.residual_identity,
            "fingerprint": self.fingerprint,
            "coefficients": coefficients_as_strings(self.coefficients),
        }


def find_schema(program: tuple[str, ...]) -> tuple[str | None, int | None]:
    for name, pattern in SCHEMAS:
        n = len(pattern)
        for index in range(len(program) - n + 1):
            if program[index:index + n] == pattern:
                return name, index
    return None, None


def residual_identity(episode_id: str, program: tuple[str, ...]) -> str:
    return content_hash({"episode_id": episode_id, "program": program})


def future_split_key(trace: Trace) -> tuple[str, str, str]:
    """Hypothetical later operator: splits currently co-schematic traces by ends + episode."""
    return (trace.program[0], trace.program[-1], trace.episode_id)


def make_trace(episode_id: str, program: tuple[str, ...]) -> Trace:
    schema_id, occurrence = find_schema(program)
    return Trace(
        episode_id=episode_id,
        program=tuple(program),
        schema_id=schema_id,
        occurrence=occurrence,
        residual_identity=residual_identity(episode_id, tuple(program)),
    )


def all_programs() -> tuple[tuple[str, ...], ...]:
    return tuple(
        program
        for length in PROGRAM_LENGTHS
        for program in product(M.PRIMITIVES, repeat=length)
    )


def ranked_programs(pool: Iterable[tuple[str, ...]], salt: str) -> tuple[tuple[str, ...], ...]:
    return tuple(sorted(
        pool,
        key=lambda program: (stable_rank(salt, program_fingerprint(program)), program),
    ))


def classified_pools() -> dict[str, tuple[tuple[str, ...], ...]]:
    buckets: dict[str, list[tuple[str, ...]]] = {name: [] for name in SCHEMA_ORDER}
    buckets["EXC"] = []
    for program in all_programs():
        schema_id, _occ = find_schema(program)
        buckets[schema_id or "EXC"].append(program)
    return {name: ranked_programs(programs, TRAIN_SALT) for name, programs in buckets.items()}


def frozen_partition():
    pools = classified_pools()
    unique: list[tuple[str, ...]] = []
    used = set()
    for name, count in UNIQUE_COUNTS.items():
        chosen = []
        for program in pools[name]:
            if program in used:
                continue
            chosen.append(program)
            used.add(program)
            if len(chosen) == count:
                break
        if len(chosen) != count:
            raise RuntimeError(f"unique pool {name} too small: {len(chosen)} < {count}")
        unique.extend(chosen)

    duplicates: list[tuple[str, ...]] = []
    cursor = 0
    for name, count in DUPLICATE_COUNTS.items():
        source = [program for program in unique[cursor:cursor + UNIQUE_COUNTS[name]]]
        cursor += UNIQUE_COUNTS[name]
        if len(source) < count:
            raise RuntimeError(f"duplicate source {name} too small")
        duplicates.extend(source[:count])

    if len(unique) + len(duplicates) != TRAIN_N:
        raise RuntimeError("frozen training count drifted")

    traces = tuple(
        make_trace(f"ep-{index:02d}", program)
        for index, program in enumerate(tuple(unique) + tuple(duplicates))
    )
    training_fingerprints = {trace.fingerprint for trace in traces}
    training_programs = {trace.program for trace in traces}

    heldout_programs: list[tuple[str, ...]] = []
    heldout_pools = {
        name: ranked_programs(pools[name], HELDOUT_SALT) for name in SCHEMA_ORDER
    }
    for name, count in HELDOUT_COUNTS.items():
        chosen = []
        for program in heldout_pools[name]:
            if program in training_programs:
                continue
            if program_fingerprint(program) in training_fingerprints:
                continue
            chosen.append(program)
            if len(chosen) == count:
                break
        if len(chosen) != count:
            raise RuntimeError(f"held-out pool {name} too small: {len(chosen)} < {count}")
        heldout_programs.extend(chosen)
    if len(heldout_programs) != HELDOUT_N:
        raise RuntimeError("frozen held-out count drifted")
    heldout = tuple(
        make_trace(f"ho-{index:02d}", program)
        for index, program in enumerate(heldout_programs)
    )
    ids = [trace.episode_id for trace in traces + heldout]
    if len(ids) != len(set(ids)):
        raise RuntimeError("episode id collision")
    fps = [trace.fingerprint for trace in traces] + [trace.fingerprint for trace in heldout]
    if set(fps[:TRAIN_N]) & set(fps[TRAIN_N:]):
        raise RuntimeError("train/held-out fingerprint overlap")
    return traces, heldout


def schema_context(program: tuple[str, ...], schema_id: str, occurrence: int) -> dict[str, Any]:
    pattern = SCHEMA_PATTERNS[schema_id]
    prefix = program[:occurrence]
    suffix = program[occurrence + len(pattern):]
    return {
        "schema_id": schema_id,
        "occurrence": occurrence,
        "prefix": list(prefix),
        "suffix": list(suffix),
        "token_word": list(prefix) + [schema_id] + list(suffix),
    }


def expand_schema_context(context: dict[str, Any]) -> tuple[str, ...]:
    pattern = SCHEMA_PATTERNS[context["schema_id"]]
    return tuple(context["prefix"]) + pattern + tuple(context["suffix"])


def expand_tokens(token_word, macros: dict[str, tuple[str, ...]]):
    expanded = []
    used = []
    for token in token_word:
        if token in macros:
            expanded.extend(macros[token])
            if token not in used:
                used.append(token)
        else:
            if token not in M.PRIMITIVES:
                raise ValueError(f"unknown token {token}")
            expanded.append(token)
    return tuple(expanded), tuple(used)


def token_order(macros: dict[str, tuple[str, ...]]) -> tuple[str, ...]:
    schema_tokens = tuple(name for name in SCHEMA_ORDER if name in macros)
    other = tuple(sorted(name for name in macros if name not in SCHEMA_ORDER))
    return schema_tokens + other + M.PRIMITIVES


def build_search_index(macros: dict[str, tuple[str, ...]], max_primitive_length: int = MAX_PRIMITIVE_LENGTH):
    macros = {name: tuple(pattern) for name, pattern in macros.items()}
    tokens = token_order(macros)
    seen = set()
    first_by_coefficients = {}
    attempts = 0
    checks = 0
    for depth in range(max_primitive_length + 1):
        for token_word in product(tokens, repeat=depth):
            program, used = expand_tokens(token_word, macros)
            if len(program) > max_primitive_length:
                continue
            attempts += 1
            if program in seen:
                continue
            seen.add(program)
            checks += 1
            coefficients = M.normal_form(program)
            first_by_coefficients.setdefault(coefficients, {
                "enumeration_attempts": attempts,
                "unique_candidates_checked": checks,
                "token_word": token_word,
                "program": program,
                "macros_used": used,
            })
    return {
        "macros": macros,
        "total_enumeration_attempts": attempts,
        "total_unique_candidates_checked": checks,
        "first_by_coefficients": first_by_coefficients,
    }


def solve_task(task: M.PolynomialTask, index) -> dict[str, Any]:
    hit = index["first_by_coefficients"].get(task.coefficients)
    if hit is None:
        raise RuntimeError(f"grammar failed to solve {task.fingerprint}")
    if M.normal_form(tuple(hit["program"])) != task.coefficients:
        raise RuntimeError("exact verification failed")
    return {
        "task": task.fingerprint,
        "enumeration_attempts": hit["enumeration_attempts"],
        "unique_candidates_checked": hit["unique_candidates_checked"],
        "token_word": list(hit["token_word"]),
        "program": list(hit["program"]),
        "macros_used": list(hit["macros_used"]),
        "verified": True,
    }


def evaluate_tasks(tasks, macros: dict[str, tuple[str, ...]]):
    index = build_search_index(macros)
    rows = [solve_task(task, index) for task in tasks]
    return rows, sum(row["enumeration_attempts"] for row in rows), sum(
        row["unique_candidates_checked"] for row in rows
    )


def proper_fragments(program: tuple[str, ...]):
    out = set()
    for start in range(len(program)):
        stop = min(len(program), start + FRAGMENT_MAX_LENGTH)
        for end in range(start + FRAGMENT_MIN_LENGTH, stop + 1):
            fragment = tuple(program[start:end])
            if len(fragment) < len(program):
                out.add(fragment)
    return out


def mine_library(traces: tuple[Trace, ...]):
    support = Counter()
    for trace in traces:
        for fragment in proper_fragments(trace.program):
            support[fragment] += 1
    candidates = tuple(sorted(
        (fragment for fragment, count in support.items() if count >= LIBRARY_MIN_SUPPORT),
        key=lambda fragment: (-support[fragment], -len(fragment), fragment),
    )[:LIBRARY_CAP])
    return candidates, {fragment: support[fragment] for fragment in candidates}


def greedy_tokenize(program: tuple[str, ...], fragments: tuple[tuple[str, ...], ...]):
    ordered = tuple(sorted(fragments, key=lambda fragment: (-len(fragment), fragment)))
    tokens = []
    index = 0
    while index < len(program):
        matched = False
        for fragment in ordered:
            if program[index:index + len(fragment)] == fragment:
                tokens.append(fragment)
                index += len(fragment)
                matched = True
                break
        if not matched:
            tokens.append((program[index],))
            index += 1
    return tuple(tokens)


def expand_library_tokens(tokens) -> tuple[str, ...]:
    program = []
    for token in tokens:
        program.extend(token)
    return tuple(program)


@dataclass
class ParentStore:
    name: str
    live: dict[str, Any]
    archive: dict[str, Any]
    consolidation_ops: int
    consolidation_cpu_seconds: float
    live_bytes: int = 0
    archive_bytes: int = 0

    def __post_init__(self):
        self.live_bytes = payload_bytes(self.live)
        self.archive_bytes = payload_bytes(self.archive)

    @property
    def total_bytes(self) -> int:
        return self.live_bytes + self.archive_bytes


def reconstruct_from_keep_all(store: ParentStore, episode_id: str) -> tuple[str, ...] | None:
    for row in store.live["traces"]:
        if row["episode_id"] == episode_id:
            return tuple(row["program"])
    return None


def reconstruct_from_dedup(store: ParentStore, episode_id: str) -> tuple[str, ...] | None:
    for row in store.live["traces"]:
        if row["episode_id"] == episode_id:
            return tuple(row["program"])
    return None


def reconstruct_from_trie(node: dict[str, Any], prefix: tuple[str, ...], episode_id: str):
    if episode_id in node.get("episodes", ()):
        return prefix
    for op, child in node.get("children", {}).items():
        hit = reconstruct_from_trie(child, prefix + (op,), episode_id)
        if hit is not None:
            return hit
    return None


def reconstruct_from_library(store: ParentStore, episode_id: str) -> tuple[str, ...] | None:
    for row in store.live["traces"]:
        if row["episode_id"] == episode_id:
            return expand_library_tokens(tuple(tuple(token) for token in row["tokens"]))
    return None


def reconstruct_from_schema(store: ParentStore, episode_id: str) -> tuple[str, ...] | None:
    for row in store.live.get("residuals", ()):
        if row["episode_id"] == episode_id:
            return expand_schema_context(row["context"])
    for row in store.live.get("exceptions", ()):
        if row["episode_id"] == episode_id:
            return tuple(row["program"])
    return None


def reconstruct(store: ParentStore, episode_id: str) -> tuple[str, ...] | None:
    if store.name == "keep_all":
        return reconstruct_from_keep_all(store, episode_id)
    if store.name == "fingerprint_dedup":
        return reconstruct_from_dedup(store, episode_id)
    if store.name == "structural_sharing":
        return reconstruct_from_trie(store.live["trie"], (), episode_id)
    if store.name == "library_learn":
        return reconstruct_from_library(store, episode_id)
    if store.name == "schema_residual":
        return reconstruct_from_schema(store, episode_id)
    raise KeyError(store.name)


def stored_residual_identity(store: ParentStore, trace: Trace) -> str | None:
    if store.name == "keep_all":
        for row in store.live["traces"]:
            if row["episode_id"] == trace.episode_id:
                return row["residual_identity"]
        return None
    if store.name == "fingerprint_dedup":
        for row in store.live["traces"]:
            if row["episode_id"] == trace.episode_id:
                return row["fingerprint"]
        return None
    if store.name == "structural_sharing":
        program = reconstruct(store, trace.episode_id)
        if program is None:
            return None
        return residual_identity(trace.episode_id, program)
    if store.name == "library_learn":
        for row in store.live["traces"]:
            if row["episode_id"] == trace.episode_id:
                return row["residual_identity"]
        return None
    if store.name == "schema_residual":
        for row in (*store.live["residuals"], *store.live["exceptions"]):
            if row["episode_id"] == trace.episode_id:
                return row["residual_identity"]
        return None
    raise KeyError(store.name)


def recovered_split_key(store: ParentStore, trace: Trace):
    program = reconstruct(store, trace.episode_id)
    stored_episode = None
    if store.name == "keep_all":
        stored_episode = next(
            (row["episode_id"] for row in store.live["traces"] if row["episode_id"] == trace.episode_id),
            None,
        )
    elif store.name == "fingerprint_dedup":
        stored_episode = next(
            (row["episode_id"] for row in store.live["traces"] if row["episode_id"] == trace.episode_id),
            None,
        )
    elif store.name == "structural_sharing":
        stored_episode = trace.episode_id if program is not None else None
    elif store.name == "library_learn":
        stored_episode = next(
            (row["episode_id"] for row in store.live["traces"] if row["episode_id"] == trace.episode_id),
            None,
        )
    elif store.name == "schema_residual":
        stored_episode = next(
            (
                row["episode_id"]
                for row in (*store.live["residuals"], *store.live["exceptions"])
                if row["episode_id"] == trace.episode_id
            ),
            None,
        )
    if program is None or stored_episode is None:
        return None
    return (program[0], program[-1], stored_episode)


def exception_lookup(store: ParentStore, episode_id: str) -> tuple[str, ...] | None:
    if store.name == "schema_residual":
        for row in store.live.get("exceptions", ()):
            if row["episode_id"] == episode_id:
                return tuple(row["program"])
        return None
    return reconstruct(store, episode_id)


def parent_keep_all(traces: tuple[Trace, ...], ops: int, cpu: float) -> ParentStore:
    live = {"kind": "g5.parent.keep-all.v1", "traces": [trace.as_dict() for trace in traces]}
    return ParentStore("keep_all", live, {"kind": "g5.archive.empty.v1", "items": []}, ops, cpu)


def parent_fingerprint_dedup(traces: tuple[Trace, ...], ops: int, cpu: float) -> ParentStore:
    by_fp: dict[str, dict[str, Any]] = {}
    for trace in traces:
        ops += 1
        if trace.fingerprint in by_fp:
            continue
        by_fp[trace.fingerprint] = {
            "fingerprint": trace.fingerprint,
            "program": list(trace.program),
            "episode_id": trace.episode_id,
            "coefficients": coefficients_as_strings(trace.coefficients),
        }
    live = {"kind": "g5.parent.fingerprint-dedup.v1", "traces": list(by_fp.values())}
    return ParentStore("fingerprint_dedup", live, {"kind": "g5.archive.empty.v1", "items": []}, ops, cpu)


def parent_structural_sharing(traces: tuple[Trace, ...], ops: int, cpu: float) -> ParentStore:
    trie: dict[str, Any] = {"children": {}, "episodes": []}
    for trace in traces:
        node = trie
        for op in trace.program:
            ops += 1
            node = node["children"].setdefault(op, {"children": {}, "episodes": []})
        node["episodes"].append(trace.episode_id)
    live = {"kind": "g5.parent.structural-sharing.v1", "trie": trie}
    return ParentStore("structural_sharing", live, {"kind": "g5.archive.empty.v1", "items": []}, ops, cpu)


def parent_library_learn(traces: tuple[Trace, ...], ops: int, cpu: float) -> ParentStore:
    fragments, support = mine_library(traces)
    ops += sum(len(proper_fragments(trace.program)) for trace in traces)
    rows = []
    for trace in traces:
        tokens = greedy_tokenize(trace.program, fragments)
        ops += len(trace.program)
        rows.append({
            "episode_id": trace.episode_id,
            "residual_identity": trace.residual_identity,
            "tokens": [list(token) for token in tokens],
            "fingerprint": trace.fingerprint,
        })
    live = {
        "kind": "g5.parent.library-learn.v1",
        "fragments": [list(fragment) for fragment in fragments],
        "support": {",".join(fragment): support[fragment] for fragment in fragments},
        "traces": rows,
    }
    return ParentStore("library_learn", live, {"kind": "g5.archive.empty.v1", "items": []}, ops, cpu)


def parent_schema_residual(traces: tuple[Trace, ...], ops: int, cpu: float) -> ParentStore:
    residuals = []
    exceptions = []
    archive_items = []
    support: dict[str, list[str]] = {name: [] for name in SCHEMA_ORDER}
    for trace in traces:
        ops += 1
        if trace.schema_id is None:
            exceptions.append({
                "episode_id": trace.episode_id,
                "program": list(trace.program),
                "residual_identity": trace.residual_identity,
                "fingerprint": trace.fingerprint,
                "coefficients": coefficients_as_strings(trace.coefficients),
            })
            continue
        context = schema_context(trace.program, trace.schema_id, trace.occurrence)
        ops += 1
        residuals.append({
            "episode_id": trace.episode_id,
            "schema_id": trace.schema_id,
            "residual_identity": trace.residual_identity,
            "context": context,
            "fingerprint": trace.fingerprint,
        })
        support[trace.schema_id].append(trace.episode_id)
        archive_items.append({
            "episode_id": trace.episode_id,
            "program": list(trace.program),
            "fingerprint": trace.fingerprint,
            "schema_id": trace.schema_id,
            "residual_identity": trace.residual_identity,
        })
    live = {
        "kind": "g5.parent.schema-residual.v1",
        "schemas": [
            {
                "schema_id": name,
                "pattern": list(SCHEMA_PATTERNS[name]),
                "support_episodes": support[name],
            }
            for name in SCHEMA_ORDER
        ],
        "residuals": residuals,
        "exceptions": exceptions,
    }
    archive = {"kind": "g5.archive.schema-covered.v1", "items": archive_items}
    return ParentStore("schema_residual", live, archive, ops, cpu)


def consolidate(traces: tuple[Trace, ...]) -> dict[str, ParentStore]:
    cpu_start = time.process_time()
    ops = 0
    for trace in traces:
        ops += 1
        _ = trace.residual_identity
    stores = {
        "keep_all": parent_keep_all(traces, ops, 0.0),
        "fingerprint_dedup": parent_fingerprint_dedup(traces, ops, 0.0),
        "structural_sharing": parent_structural_sharing(traces, ops, 0.0),
        "library_learn": parent_library_learn(traces, ops, 0.0),
        "schema_residual": parent_schema_residual(traces, ops, 0.0),
    }
    cpu = time.process_time() - cpu_start
    for store in stores.values():
        store.consolidation_cpu_seconds = cpu
    return stores


def live_macros_from_schema_store(store: ParentStore, revoked_schemas=()) -> dict[str, tuple[str, ...]]:
    revoked = set(revoked_schemas)
    macros = {}
    for row in store.live["schemas"]:
        if row["schema_id"] in revoked:
            continue
        if row["support_episodes"]:
            macros[row["schema_id"]] = tuple(row["pattern"])
    return macros


def live_macros_from_library(store: ParentStore) -> dict[str, tuple[str, ...]]:
    macros = {}
    for index, fragment in enumerate(store.live["fragments"]):
        macros[f"FRAG{index}"] = tuple(fragment)
    return macros


def coefficient_lookup(store: ParentStore, fingerprint: str) -> bool:
    if store.name == "keep_all":
        return any(row["fingerprint"] == fingerprint for row in store.live["traces"])
    if store.name == "fingerprint_dedup":
        return any(row["fingerprint"] == fingerprint for row in store.live["traces"])
    if store.name == "structural_sharing":
        def walk(node, program):
            found = []
            if node.get("episodes"):
                found.append(program)
            for op, child in node.get("children", {}).items():
                found.extend(walk(child, program + (op,)))
            return found
        programs = walk(store.live["trie"], ())
        return any(program_fingerprint(program) == fingerprint for program in programs)
    if store.name == "library_learn":
        return any(row["fingerprint"] == fingerprint for row in store.live["traces"])
    if store.name == "schema_residual":
        if any(row["fingerprint"] == fingerprint for row in store.live["residuals"]):
            return True
        return any(row["fingerprint"] == fingerprint for row in store.live["exceptions"])
    raise KeyError(store.name)


def heldout_capability(store: ParentStore, heldout: tuple[Trace, ...], macros: dict[str, tuple[str, ...]] | None = None):
    tasks = [program_task(trace.program, trace.episode_id) for trace in heldout]
    stored_hits = sum(1 for trace in heldout if coefficient_lookup(store, trace.fingerprint))
    if macros:
        rows, attempts, checks = evaluate_tasks(tasks, macros)
        method_uses = [
            row for row in rows
            if row["macros_used"] and row["verified"]
        ]
        primitive_rows, primitive_attempts, _pc = evaluate_tasks(tasks, {})
        strict = 0
        for row, base in zip(rows, primitive_rows):
            if row["macros_used"] and row["enumeration_attempts"] < base["enumeration_attempts"]:
                strict += 1
        return {
            "stored_hits": stored_hits,
            "method_use_count": len(method_uses),
            "strict_method_wins": strict,
            "attempts": attempts,
            "primitive_attempts": primitive_attempts,
            "unique_checks": checks,
            "rows": rows,
            "primitive_rows": primitive_rows,
        }
    return {
        "stored_hits": stored_hits,
        "method_use_count": 0,
        "strict_method_wins": 0,
        "attempts": None,
        "primitive_attempts": None,
        "unique_checks": None,
        "rows": [],
        "primitive_rows": [],
    }


def ordinary_persist(path: Path, payload: dict[str, Any]) -> None:
    temp = path.with_suffix(".tmp")
    with temp.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, sort_keys=True)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def admit_schema_residual(root: Path, traces: tuple[Trace, ...], store: ParentStore, revoke_schema_ids=()):
    runtime = OCMRuntime(root)
    episode_evidence = {}
    for trace in traces:
        _admission, eid = runtime.admit_evidence(
            {
                "schema": "g5.episode.v1",
                "episode_id": trace.episode_id,
                "program": list(trace.program),
                "residual_identity": trace.residual_identity,
            },
            Channel.PROOF,
            "g5-consolidation-episode.v1",
            scope=SCOPE,
        )
        episode_evidence[trace.episode_id] = eid

    schema_atoms = {}
    residual_by_schema = {name: [] for name in SCHEMA_ORDER}
    for row in store.live["residuals"]:
        residual_by_schema[row["schema_id"]].append(row)

    for schema_row in store.live["schemas"]:
        schema_id = schema_row["schema_id"]
        support_ids = [episode_evidence[episode] for episode in schema_row["support_episodes"]]
        if not support_ids:
            continue
        warrants = tuple([eid] for eid in support_ids)
        warrant = WarrantProfile.of(*warrants)
        source_payload = {
            "kind": "g5.schema.support.v1",
            "schema_id": schema_id,
            "episodes": list(schema_row["support_episodes"]),
        }
        source_id = "g5-schema-support:" + content_hash(source_payload)
        runtime.admit_object(
            Atom(
                source_id,
                "proof",
                warrant,
                scope=SCOPE,
                quarantined=True,
                content_ref=content_hash(source_payload),
                meta=tuple(source_payload.items()),
            ),
            (),
            "OBSERVATION",
        )
        payload = {
            "kind": "g5.schema.v1",
            "schema_id": schema_id,
            "pattern": list(SCHEMA_PATTERNS[schema_id]),
            "support_episodes": list(schema_row["support_episodes"]),
            "residuals": residual_by_schema[schema_id],
            "fingerprint": content_hash({"schema_id": schema_id, "pattern": SCHEMA_PATTERNS[schema_id]}),
        }
        atom_id = "g5-schema:" + content_hash(payload)
        edge = Hyperedge("support:" + atom_id, (source_id,), (atom_id,), "SUPPORT", warrant=warrant)
        runtime.admit_object(
            Atom(
                atom_id,
                "procedure",
                warrant,
                scope=SCOPE,
                content_ref=content_hash(payload),
                meta=tuple(payload.items()),
            ),
            (edge,),
            "OBSERVATION",
        )
        schema_atoms[schema_id] = atom_id

    exception_atoms = {}
    for row in store.live["exceptions"]:
        eid = episode_evidence[row["episode_id"]]
        warrant = WarrantProfile.of({eid})
        source_payload = {
            "kind": "g5.exception.support.v1",
            "episode_id": row["episode_id"],
        }
        source_id = "g5-exception-support:" + content_hash(source_payload)
        runtime.admit_object(
            Atom(
                source_id,
                "proof",
                warrant,
                scope=SCOPE,
                quarantined=True,
                content_ref=content_hash(source_payload),
                meta=tuple(source_payload.items()),
            ),
            (),
            "OBSERVATION",
        )
        payload = {
            "kind": "g5.exception.v1",
            "episode_id": row["episode_id"],
            "program": list(row["program"]),
            "residual_identity": row["residual_identity"],
            "fingerprint": row["fingerprint"],
        }
        atom_id = "g5-exception:" + content_hash(payload)
        edge = Hyperedge("support:" + atom_id, (source_id,), (atom_id,), "SUPPORT", warrant=warrant)
        runtime.admit_object(
            Atom(
                atom_id,
                "observation",
                warrant,
                scope=SCOPE,
                content_ref=content_hash(payload),
                meta=tuple(payload.items()),
            ),
            (edge,),
            "OBSERVATION",
        )
        exception_atoms[row["episode_id"]] = atom_id

    revoked = []
    for schema_id in revoke_schema_ids:
        for episode_id in store.live["schemas"][SCHEMA_ORDER.index(schema_id)]["support_episodes"]:
            revoked.append(episode_evidence[episode_id])
    if revoked:
        runtime.revoke(tuple(revoked))
    runtime.persist()

    replay = OCMRuntime(root)
    live_schemas = {}
    live_exceptions = {}
    dead_schemas = []
    for schema_id, atom_id in schema_atoms.items():
        atom = replay.state.ks.atom_map().get(atom_id)
        live = atom is not None and atom.liveness(replay.state.revoked) is Liveness.LIVE
        if live:
            stored = dict(atom.meta)
            live_schemas[schema_id] = tuple(stored["pattern"])
        else:
            dead_schemas.append(schema_id)
            if schema_id not in set(revoke_schema_ids):
                raise RuntimeError(f"unrevoked schema {schema_id} is not live")
            if atom is not None and atom.liveness(replay.state.revoked) is Liveness.LIVE:
                raise RuntimeError(f"revoked schema {schema_id} remained live")
    for episode_id, atom_id in exception_atoms.items():
        atom = replay.state.ks.atom_map().get(atom_id)
        if atom is None or atom.liveness(replay.state.revoked) is not Liveness.LIVE:
            raise RuntimeError(f"exception {episode_id} lost after revocation")
        live_exceptions[episode_id] = tuple(dict(atom.meta)["program"])
    return {
        "live_schemas": live_schemas,
        "dead_schemas": tuple(dead_schemas),
        "live_exceptions": live_exceptions,
        "episode_evidence": episode_evidence,
        "schema_atoms": schema_atoms,
        "exception_atoms": exception_atoms,
    }


def current_behavior_ok(store: ParentStore, traces: tuple[Trace, ...]) -> tuple[bool, int]:
    recovered = 0
    for trace in traces:
        program = reconstruct(store, trace.episode_id)
        if program != trace.program:
            return False, recovered
        if M.normal_form(program) != trace.coefficients:
            return False, recovered
        recovered += 1
    return True, recovered


def future_revision_ok(store: ParentStore, traces: tuple[Trace, ...]) -> dict[str, Any]:
    by_schema: dict[str, list[Trace]] = {name: [] for name in SCHEMA_ORDER}
    for trace in traces:
        if trace.schema_id is not None:
            by_schema[trace.schema_id].append(trace)
    distinguishable = True
    collapsed = []
    missing = []
    schema_id_only = []
    pairs = 0
    for schema_id, group in by_schema.items():
        identities = []
        for trace in group:
            stored = stored_residual_identity(store, trace)
            if stored is None:
                distinguishable = False
                missing.append(trace.episode_id)
                continue
            if stored == schema_id:
                distinguishable = False
                schema_id_only.append(trace.episode_id)
            identities.append(stored)
            recovered = recovered_split_key(store, trace)
            pairs += 1
            if recovered is None or recovered != future_split_key(trace):
                distinguishable = False
                if recovered is None:
                    missing.append(trace.episode_id)
                else:
                    collapsed.append(trace.episode_id)
        if len(identities) != len(set(identities)):
            distinguishable = False
            collapsed.append(schema_id)
    return {
        "ok": distinguishable and not missing and not schema_id_only,
        "collapsed": collapsed,
        "missing": missing,
        "schema_id_only": schema_id_only,
        "checked_traces": pairs,
        "residual_identities_unique_per_schema": not collapsed,
    }


def compare_parents(stores: dict[str, ParentStore], traces: tuple[Trace, ...], heldout: tuple[Trace, ...]):
    table = {}
    schema_macros = live_macros_from_schema_store(stores["schema_residual"])
    library_macros = live_macros_from_library(stores["library_learn"])
    for name, store in stores.items():
        behavior_ok, recovered = current_behavior_ok(store, traces)
        future = future_revision_ok(store, traces)
        exception_ids = [trace.episode_id for trace in traces if trace.schema_id is None]
        exceptions_ok = all(exception_lookup(store, episode_id) is not None for episode_id in exception_ids)
        macros = None
        if name == "schema_residual":
            macros = schema_macros
        elif name == "library_learn":
            macros = library_macros
        capability = heldout_capability(store, heldout, macros)
        table[name] = {
            "live_bytes": store.live_bytes,
            "archive_bytes": store.archive_bytes,
            "total_bytes": store.total_bytes,
            "consolidation_ops": store.consolidation_ops,
            "consolidation_cpu_seconds": store.consolidation_cpu_seconds,
            "current_behavior": behavior_ok,
            "recovered_training_traces": recovered,
            "future_revision": future["ok"],
            "exceptions_addressable": exceptions_ok,
            "heldout_stored_hits": capability["stored_hits"],
            "heldout_method_use_count": capability["method_use_count"],
            "heldout_strict_method_wins": capability["strict_method_wins"],
            "heldout_attempts": capability["attempts"],
            "heldout_primitive_attempts": capability["primitive_attempts"],
        }
        if name == "schema_residual":
            table[name]["heldout_rows"] = capability["rows"]
            table[name]["heldout_primitive_rows"] = capability["primitive_rows"]
            table[name]["future_detail"] = future
        if name == "library_learn":
            table[name]["heldout_rows"] = capability["rows"]
        if name == "structural_sharing":
            table[name]["heldout_rows"] = capability["rows"]
    return table


def decide_terminal(checks: dict[str, Any], comparison: dict[str, Any], revocation: dict[str, Any]) -> tuple[str, bool]:
    for key, reason in (
        ("method_blob_ok", "CANNOT_CHECK_METHOD_SOURCE"),
        ("current_behavior", "CANNOT_CHECK_CURRENT_BEHAVIOR"),
        ("future_revision", "CANNOT_CHECK_FUTURE_REVISION"),
        ("exceptions_addressable", "CANNOT_CHECK_EXCEPTIONS"),
        ("provenance_recoverable", "CANNOT_CHECK_PROVENANCE"),
        ("archive_bytes_charged", "CANNOT_CHECK_ARCHIVE_BYTES"),
        ("consolidation_compute_charged", "CANNOT_CHECK_CONSOLIDATION_COMPUTE"),
    ):
        if not checks[key]:
            return reason, False
    if not revocation["exact"]:
        return "REVOCATION_NOT_PRESERVED", False
    if not checks["heldout_survives"]:
        if comparison["structural_sharing"]["live_bytes"] < comparison["keep_all"]["live_bytes"]:
            return "STRUCTURAL_COMPRESSION_ONLY", False
        return "PARENT_SUFFICIENT", False

    schema = comparison["schema_residual"]
    structural = comparison["structural_sharing"]
    schema_joint = (schema["heldout_method_use_count"], int(revocation["exact"]))
    structural_joint = (structural["heldout_method_use_count"], int(structural["current_behavior"]))
    if schema_joint <= structural_joint:
        return "PARENT_SUFFICIENT", False

    keep_all_bytes = comparison["keep_all"]["total_bytes"]
    schema_total = schema["total_bytes"]
    heldout_saving = 0
    if schema["heldout_attempts"] is not None and schema["heldout_primitive_attempts"]:
        heldout_saving = schema["heldout_primitive_attempts"] - schema["heldout_attempts"]
    if schema_total > keep_all_bytes and heldout_saving <= 0:
        return "CONSOLIDATION_COST_DOMINATES", False
    return "EPISTEMICALLY_SAFE_COMPRESSION_SUPPORTED", True


def run():
    source_path = SRC / "ocm" / "learning" / "methods.py"
    observed_blob = git_blob_sha1(source_path)
    method_blob_ok = observed_blob == METHOD_BLOB
    if not method_blob_ok:
        raise RuntimeError(f"method source drift: {observed_blob}")

    start = time.perf_counter()
    traces, heldout = frozen_partition()
    stores = consolidate(traces)
    comparison = compare_parents(stores, traces, heldout)

    schema_store = stores["schema_residual"]
    archive_ok = schema_store.archive_bytes > 0 and schema_store.archive["items"]
    compute_ok = schema_store.consolidation_cpu_seconds >= 0.0 and schema_store.consolidation_ops > 0
    behavior_ok, _recovered = current_behavior_ok(schema_store, traces)
    future = future_revision_ok(schema_store, traces)
    exception_ids = [trace.episode_id for trace in traces if trace.schema_id is None]
    exceptions_ok = all(
        exception_lookup(schema_store, episode_id) is not None for episode_id in exception_ids
    )
    provenance_ok = True
    for row in schema_store.live["schemas"]:
        if not row["support_episodes"]:
            provenance_ok = False
    recovered_from_archive = {
        item["episode_id"]: tuple(item["program"]) for item in schema_store.archive["items"]
    }
    for trace in traces:
        if trace.schema_id is None:
            continue
        if recovered_from_archive.get(trace.episode_id) != trace.program:
            provenance_ok = False
    heldout_survives = comparison["schema_residual"]["heldout_method_use_count"] > 0

    with tempfile.TemporaryDirectory(prefix="ocm-g5-consol-") as temp_dir:
        root = Path(temp_dir)
        ordinary_path = root / "ordinary-schema.json"
        ordinary_persist(ordinary_path, schema_store.live)
        ordinary_live = json.loads(ordinary_path.read_text())
        live_state = admit_schema_residual(root / "ocm-live", traces, schema_store, revoke_schema_ids=())
        revoked_state = admit_schema_residual(
            root / "ocm-revoked-sds", traces, schema_store, revoke_schema_ids=("SDS",)
        )

    ordinary_macros = {
        row["schema_id"]: tuple(row["pattern"])
        for row in ordinary_live["schemas"]
        if row["support_episodes"]
    }
    ocm_macros = live_state["live_schemas"]
    revoked_macros = revoked_state["live_schemas"]
    heldout_tasks = [program_task(trace.program, trace.episode_id) for trace in heldout]
    ordinary_rows, ordinary_attempts, _oc = evaluate_tasks(heldout_tasks, ordinary_macros)
    ocm_rows, ocm_attempts, _omc = evaluate_tasks(heldout_tasks, ocm_macros)
    revoked_rows, revoked_attempts, _rc = evaluate_tasks(heldout_tasks, revoked_macros)
    primitive_rows, primitive_attempts, _pc = evaluate_tasks(heldout_tasks, {})

    def rows_equal(a_rows, b_rows):
        if len(a_rows) != len(b_rows):
            return False
        return all(
            a["task"] == b["task"]
            and a["enumeration_attempts"] == b["enumeration_attempts"]
            and tuple(a["program"]) == tuple(b["program"])
            and tuple(a["macros_used"]) == tuple(b["macros_used"])
            for a, b in zip(a_rows, b_rows)
        )

    ordinary_equals_ocm = rows_equal(ordinary_rows, ocm_rows)
    sds_heldout = [trace for trace in heldout if trace.schema_id == "SDS"]
    sii_heldout = [trace for trace in heldout if trace.schema_id == "SII"]
    sdd_heldout = [trace for trace in heldout if trace.schema_id == "SDD"]
    revoked_by_task = {row["task"]: row for row in revoked_rows}
    ocm_by_task = {row["task"]: row for row in ocm_rows}
    sds_unused_after_revoke = all(
        "SDS" not in revoked_by_task[program_fingerprint(trace.program)]["macros_used"]
        for trace in sds_heldout
    )
    cached_sds = False
    for trace in sds_heldout:
        before = ocm_by_task[program_fingerprint(trace.program)]
        after = revoked_by_task[program_fingerprint(trace.program)]
        if "SDS" in after["macros_used"]:
            cached_sds = True
        if before["macros_used"] == after["macros_used"] and "SDS" in before["macros_used"]:
            cached_sds = True
    remaining_sii = any(
        "SII" in revoked_by_task[program_fingerprint(trace.program)]["macros_used"]
        for trace in sii_heldout
    )
    remaining_sdd = any(
        "SDD" in revoked_by_task[program_fingerprint(trace.program)]["macros_used"]
        for trace in sdd_heldout
    )
    exceptions_survive_revoke = set(revoked_state["live_exceptions"]) == {
        trace.episode_id for trace in traces if trace.schema_id is None
    }
    remaining_schemas = set(revoked_macros) == {"SII", "SDD"}
    revocation_exact = (
        ordinary_equals_ocm
        and "SDS" in live_state["live_schemas"]
        and "SDS" not in revoked_macros
        and remaining_schemas
        and sds_unused_after_revoke
        and not cached_sds
        and remaining_sii
        and remaining_sdd
        and exceptions_survive_revoke
        and set(live_state["live_exceptions"]) == set(revoked_state["live_exceptions"])
    )

    checks = {
        "method_blob_ok": method_blob_ok,
        "current_behavior": behavior_ok,
        "future_revision": future["ok"],
        "exceptions_addressable": exceptions_ok,
        "provenance_recoverable": provenance_ok,
        "archive_bytes_charged": bool(archive_ok),
        "consolidation_compute_charged": compute_ok,
        "heldout_survives": heldout_survives,
    }
    revocation = {
        "exact": revocation_exact,
        "ordinary_equals_ocm": ordinary_equals_ocm,
        "sds_live_before": "SDS" in live_state["live_schemas"],
        "sds_dead_after": "SDS" not in revoked_macros,
        "remaining_schemas": sorted(revoked_macros),
        "sds_unused_after_revoke": sds_unused_after_revoke,
        "cached_sds_answers": cached_sds,
        "remaining_sii_use": remaining_sii,
        "remaining_sdd_use": remaining_sdd,
        "exceptions_survive": exceptions_survive_revoke,
        "revoked_attempts": revoked_attempts,
        "ocm_attempts": ocm_attempts,
        "ordinary_attempts": ordinary_attempts,
        "primitive_attempts": primitive_attempts,
    }
    terminal, supported = decide_terminal(checks, comparison, revocation)

    schema_counts = Counter(trace.schema_id or "EXC" for trace in traces)
    heldout_counts = Counter(trace.schema_id or "EXC" for trace in heldout)

    return {
        "schema": "g5.consolidation.result.v1",
        "terminal": terminal,
        "epistemically_safe_compression_supported": supported,
        "method_blob": METHOD_BLOB,
        "partition": {
            "train_n": TRAIN_N,
            "heldout_n": HELDOUT_N,
            "program_lengths": list(PROGRAM_LENGTHS),
            "train_salt": TRAIN_SALT,
            "heldout_salt": HELDOUT_SALT,
            "unique_counts": UNIQUE_COUNTS,
            "duplicate_counts": DUPLICATE_COUNTS,
            "heldout_counts": HELDOUT_COUNTS,
            "schemas": {name: list(pattern) for name, pattern in SCHEMAS},
            "training_ids": [trace.episode_id for trace in traces],
            "heldout_ids": [trace.episode_id for trace in heldout],
            "training_schema_counts": dict(schema_counts),
            "heldout_schema_counts": dict(heldout_counts),
            "training_programs": [list(trace.program) for trace in traces],
            "heldout_programs": [list(trace.program) for trace in heldout],
        },
        "checks": checks,
        "future_revision": future,
        "parents": {
            name: {
                "live_bytes": store.live_bytes,
                "archive_bytes": store.archive_bytes,
                "total_bytes": store.total_bytes,
                "consolidation_ops": store.consolidation_ops,
                "consolidation_cpu_seconds": store.consolidation_cpu_seconds,
            }
            for name, store in stores.items()
        },
        "comparison": {
            name: {key: value for key, value in row.items() if key not in {"heldout_rows", "heldout_primitive_rows", "future_detail"}}
            for name, row in comparison.items()
        },
        "heldout": {
            "ordinary_equals_ocm": ordinary_equals_ocm,
            "ocm_attempts": ocm_attempts,
            "ordinary_attempts": ordinary_attempts,
            "revoked_attempts": revoked_attempts,
            "primitive_attempts": primitive_attempts,
            "schema_method_use_count": comparison["schema_residual"]["heldout_method_use_count"],
            "schema_strict_method_wins": comparison["schema_residual"]["heldout_strict_method_wins"],
            "library_method_use_count": comparison["library_learn"]["heldout_method_use_count"],
            "structural_method_use_count": comparison["structural_sharing"]["heldout_method_use_count"],
            "structural_stored_hits": comparison["structural_sharing"]["heldout_stored_hits"],
            "schema_rows": comparison["schema_residual"]["heldout_rows"],
            "revoked_rows": revoked_rows,
            "primitive_rows": primitive_rows,
        },
        "revocation": revocation,
        "accounting": {
            "archive_bytes": schema_store.archive_bytes,
            "live_bytes": schema_store.live_bytes,
            "total_bytes_including_archive": schema_store.total_bytes,
            "keep_all_bytes": stores["keep_all"].total_bytes,
            "structural_sharing_bytes": stores["structural_sharing"].total_bytes,
            "library_learn_bytes": stores["library_learn"].total_bytes,
            "fingerprint_dedup_bytes": stores["fingerprint_dedup"].total_bytes,
            "consolidation_ops": schema_store.consolidation_ops,
            "consolidation_cpu_seconds": schema_store.consolidation_cpu_seconds,
            "study_wall_seconds": time.perf_counter() - start,
            "note": (
                "Archive bytes are added into total_bytes. Consolidation CPU is process-time "
                "over all five parents. Search attempts are research coordinates only."
            ),
        },
        "claim_boundary": (
            "Bounded epistemically safe consolidation of explicit polynomial traces under three "
            "previously useful macros reused as schemas. Fresh salts and length 4–5 traces are "
            "disjoint from G2/G3 confirmatory identities. No architecture uniqueness or "
            "whole-lifetime resource claim."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, sort_keys=True, indent=2)
        handle.write("\n")
    print(json.dumps({
        "terminal": result["terminal"],
        "heldout_schema_method_uses": result["heldout"]["schema_method_use_count"],
        "heldout_structural_method_uses": result["heldout"]["structural_method_use_count"],
        "archive_bytes": result["accounting"]["archive_bytes"],
        "live_bytes": result["accounting"]["live_bytes"],
        "revocation_exact": result["revocation"]["exact"],
        "study_wall_seconds": result["accounting"]["study_wall_seconds"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
