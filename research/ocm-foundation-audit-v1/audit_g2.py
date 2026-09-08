"""Independent mathematical audit of the frozen G2 utility-tournament v1 receipt.

No OCM imports, training, protocol tuning, persistence, or admission are performed.
Exact search-slot ranks are reconstructed from the registered total grammar. This
is NOT a verifier of OS-process restart, authority, storage durability, or clocks.
See FOUNDATION.md for the refinement argument and explicit trust boundary.
"""
from __future__ import annotations

import argparse
from collections import Counter
from functools import lru_cache
import hashlib
from itertools import product
import json
from pathlib import Path
import sys
import time
from typing import Any

OPS = ("inc", "dec", "double", "square")
CHECKER = "rational-polynomial-coefficients.v1"
METHOD_BLOB = "50323a33418b8ef8bb6500ddeba4b9d1f795e9e3"
SCHEMA = "g2.utility-tournament.result.v1"
SLOT_CAP = 200_000
PARTS = (("training", 5, 48), ("validation", 6, 32), ("test", 7, 64))


class AuditError(ValueError):
    """A missing, malformed, or contradictory certificate fails closed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def expect(actual: Any, expected: Any, label: str) -> None:
    # Unlike Python ==, canonical JSON distinguishes True from 1.
    require(canonical(actual) == canonical(expected), f"mismatch: {label}")


def integer(value: Any, label: str, lower: int = 0, upper: int | None = None) -> int:
    require(type(value) is int, f"non-integer: {label}")
    require(value >= lower and (upper is None or value <= upper), f"out of range: {label}")
    return value


def program(value: Any, maximum: int = 7) -> tuple[str, ...]:
    require(type(value) in (list, tuple), "program must be a sequence")
    require(len(value) <= maximum, "program exceeds declared grammar")
    require(all(type(op) is str and op in OPS for op in value), "unknown instruction")
    return tuple(value)


@lru_cache(maxsize=100_000)
def step(coefficients: tuple[int, ...], op: str) -> tuple[int, ...]:
    require(op in OPS, "unknown instruction")
    p = list(coefficients)
    if op == "inc":
        p[0] += 1
    elif op == "dec":
        p[0] -= 1
    elif op == "double":
        p = [2 * a for a in p]
    else:
        # Symmetric convolution; a different implementation from production's
        # ordered-pair Fraction convolution. Integers suffice for this grammar.
        q = [0] * (2 * len(p) - 1)
        for i, a in enumerate(p):
            q[2 * i] += a * a
            for j in range(i + 1, len(p)):
                q[i + j] += 2 * a * p[j]
        p = q
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return tuple(p)


@lru_cache(maxsize=30_000)
def coefficients(word: tuple[str, ...]) -> tuple[int, ...]:
    if not word:
        return (0, 1)
    return step(coefficients(word[:-1]), word[-1])


@lru_cache(maxsize=30_000)
def task_id(word: tuple[str, ...]) -> str:
    return digest({"domain": CHECKER, "coefficients": [str(c) for c in coefficients(word)]})


def method_id(fragments: tuple[tuple[str, ...], ...], training_ids: list[str]) -> str:
    return digest({"grammar": OPS, "fragments": fragments,
                   "training_tasks": sorted(training_ids), "schedule": "alternate-baseline.v1"})


@lru_cache(maxsize=1)
def frozen_partition() -> dict[str, Any]:
    """Exact quotient-state BFS, not a search through performance outcomes."""
    best = {(0, 1): 0}
    frontier = {(0, 1)}
    for length in range(1, 8):
        new = set()
        for p in frontier:
            for op in OPS:
                q = step(p, op)
                if q not in best:
                    best[q] = length
                    new.add(q)
        frontier = new
    answer: dict[str, Any] = {"population_counts": {}}
    for name, length, n in PARTS:
        salt = f"orion-ocm-g2-utility-{name}-v1"
        ids = [digest({"domain": CHECKER, "coefficients": [str(c) for c in p]})
               for p, minimum in best.items() if minimum == length]
        ids.sort(key=lambda fp: (hashlib.sha256((salt + "\0" + fp).encode()).hexdigest(), fp))
        require(len(ids) >= n, "registered population is too small")
        answer.update({f"{name}_n": n, f"{name}_min_length": length,
                       f"{name}_salt": salt, f"{name}_ids": ids[:n]})
        answer["population_counts"][str(length)] = len(ids)
    return answer


def primitive_words(maximum: int):
    for length in range(maximum + 1):
        yield from product(OPS, repeat=length)


def guided_words(fragments: tuple[tuple[str, ...], ...], maximum: int):
    tokens = fragments + tuple((op,) for op in OPS)
    for length in range(1, maximum + 1):
        for word in product(tokens, repeat=length):
            yield tuple(op for token in word for op in token)


def first_hits(ids: list[str], maximum: int, fragments=(), budget: int = SLOT_CAP) -> dict:
    """First exact solutions and charged ranks of the registered schedule.

    Target-specific counterexamples cannot remove a true polynomial identity;
    hence one shared stream can independently verify all target slot ranks.
    This equivalence does not extend to CPU time or candidate-check counts.
    """
    integer(maximum, "maximum length", 0, 7)
    integer(budget, "budget", 0, SLOT_CAP)
    require(len(ids) == len(set(ids)), "duplicate task demand")
    fragments = tuple(program(f, maximum=7) for f in fragments)
    require(len(fragments) <= 16 and all(len(f) >= 2 for f in fragments), "invalid library")
    require(len(set(fragments)) == len(fragments), "duplicate fragments")
    pending, found, seen = set(ids), {}, set()
    if not pending:
        return found
    primitive = iter(primitive_words(maximum))
    guided = iter(guided_words(fragments, maximum)) if fragments else None
    for slot in range(1, budget + 1):
        is_guided = guided is not None and slot % 2 == 1
        stream = guided if is_guided else primitive
        try:
            word = next(stream)
        except StopIteration:
            if not is_guided:
                break
            guided = None
            continue
        if len(word) > maximum or word in seen:
            continue
        seen.add(word)
        fp = task_id(word)
        if fp in pending:
            found[fp] = {"task": fp, "slots": slot, "program": list(word),
                         "origin": "guided" if is_guided else "primitive"}
            pending.remove(fp)
            if not pending:
                break
    require(not pending, "CANNOT_CHECK_UNSOLVED_REGISTERED_TASK")
    return found


def check_rows(rows: Any, ids: list[str], maximum: int, fragments=(), training=False) -> int:
    require(type(rows) is list and len(rows) == len(ids) and bool(ids), "incomplete row coverage")
    require(len(set(ids)) == len(ids), "duplicate expected task")
    expect([r["task"] for r in rows], ids, "ordered task coverage")
    expected = first_hits(ids, maximum, fragments)
    total = 0
    for row in rows:
        integer(row["slots"], "slots", 1, SLOT_CAP)
        program(row["program"], maximum)
        for key in ("task", "slots", "program") + (() if training else ("origin",)):
            expect(row[key], expected[row["task"]][key], f"exact rank {key}")
        total += row["slots"]
    return total


def paired_equal(a: Any, b: Any, ids: list[str]) -> bool:
    """Nonempty, complete, unique, ordered pairing; never zip-prefix equality."""
    if not ids or len(ids) != len(set(ids)):
        return False
    if type(a) is not list or type(b) is not list or len(a) != len(ids) or len(b) != len(ids):
        return False
    try:
        for rows in (a, b):
            if [r["task"] for r in rows] != ids:
                return False
            for r in rows:
                integer(r["slots"], "slots", 1, SLOT_CAP)
                program(r["program"])
        return all(canonical([x[k] for k in ("task", "slots", "program")]) ==
                   canonical([y[k] for k in ("task", "slots", "program")])
                   for x, y in zip(a, b))
    except (AuditError, KeyError, TypeError, ValueError):
        return False


def comparison(base: list[dict], other: list[dict]) -> dict[str, int]:
    require(len(base) == len(other) and bool(base), "incomplete comparison")
    expect([r["task"] for r in base], [r["task"] for r in other], "comparison alignment")
    require(len({r["task"] for r in base}) == len(base), "duplicate comparison task")
    result = {"strict_improvement_tasks": 0, "harmful_tasks": 0, "guided_wins": 0}
    for a, b in zip(base, other):
        integer(a["slots"], "baseline slots", 1, SLOT_CAP)
        integer(b["slots"], "candidate slots", 1, SLOT_CAP)
        require(b["origin"] in ("primitive", "guided"), "invalid origin")
        if b["slots"] < a["slots"]:
            result["strict_improvement_tasks"] += 1
            result["guided_wins"] += int(b["origin"] == "guided")
        elif b["slots"] > a["slots"]:
            result["harmful_tasks"] += 1
    return result


def candidate_pool(rows: list[dict]) -> tuple[list[tuple[str, ...]], Counter]:
    require(len(rows) == len({r["task"] for r in rows}), "duplicate training identity")
    support: Counter = Counter()
    for row in rows:
        word = program(row["program"], 5)
        require(task_id(word) == row["task"], "training mathematical identity mismatch")
        fragments = {word[i:j] for i in range(len(word))
                     for j in range(i + 2, min(len(word), i + 4) + 1)
                     if j - i < len(word)}
        support.update(fragments)
    ordered = sorted((f for f, n in support.items() if n >= 2),
                     key=lambda f: (-support[f], -len(f), f))[:16]
    return ordered, support


def audit_result(d: dict) -> dict:
    """Verify deterministic claims; deliberately emit no programme-closure flag."""
    require(type(d) is dict, "receipt must be an object")
    expect(d["schema"], SCHEMA, "schema")
    expect(d["method_blob"], METHOD_BLOB, "registered method blob")
    partition = frozen_partition()
    expect(d["partition"], partition, "frozen population/partition")
    train_ids, val_ids, test_ids = (partition[f"{n}_ids"] for n in ("training", "validation", "test"))
    training = d["training"]
    training_slots = check_rows(training["rows"], train_ids, 5, training=True)
    expect(training["total_slots"], training_slots, "training total")
    candidates, support = candidate_pool(training["rows"])
    tour = d["tournament"]
    expect(tour["candidate_order"], candidates, "complete candidate pool and order")
    baseline = tour["baseline_rows"]
    baseline_slots = check_rows(baseline, val_ids, 6)
    expect(tour["baseline_aggregate_slots"], baseline_slots, "baseline validation total")
    evaluations = tour["evaluations"]
    require(type(evaluations) is list and len(evaluations) == len(candidates), "missing candidate evaluations")
    candidate_slots = 0
    for fragment, row in zip(candidates, evaluations):
        expect(row["fragment"], fragment, "candidate identity")
        expect(row["method"], method_id((fragment,), train_ids), "candidate method identity")
        expect(row["support"], support[fragment], "distinct-task support")
        total = check_rows(row["rows"], val_ids, 6, (fragment,))
        candidate_slots += total
        for key, value in {"aggregate_slots": total, "baseline_aggregate_slots": baseline_slots,
                           "saving": baseline_slots - total, **comparison(baseline, row["rows"])}.items():
            expect(row[key], value, key)
        for a, b in zip(baseline, row["rows"]):
            expect(b["delta_slots"], a["slots"] - b["slots"], "candidate task delta")
    chosen = min(enumerate(evaluations), key=lambda p: (p[1]["aggregate_slots"], p[0]))[1] if evaluations else None
    expect(tour["selected"], chosen, "frozen utility argmin/tie break")
    accepted = chosen is not None and chosen["aggregate_slots"] < baseline_slots
    expect(tour["accepted"], accepted, "utility acceptance")
    tour_terminal = ("NO_REPEATED_FRAGMENT_CANDIDATES" if not candidates else
                     "UTILITY_TOURNAMENT_SELECTED_METHOD" if accepted else
                     "UTILITY_TOURNAMENT_SELECTS_NO_METHOD")
    expect(tour["terminal"], tour_terminal, "tournament terminal")
    fragments = (tuple(chosen["fragment"]),) if accepted else ()
    expect(d["selected_method"], {"fragments": fragments,
           "fingerprint": method_id(fragments, train_ids) if accepted else None}, "selected executable")
    test, totals = d["test"], {}
    for name, library in (("primitive", ()), ("ordinary", fragments), ("ocm", fragments), ("revoked", ())):
        totals[name] = check_rows(test[f"{name}_rows"], test_ids, 7, library)
        expect(test[f"{name}_total_slots"], totals[name], f"{name} test total")
    parity = paired_equal(test["ordinary_rows"], test["ocm_rows"], test_ids)
    ablation = paired_equal(test["revoked_rows"], test["primitive_rows"], test_ids)
    expect(test["ordinary_equals_ocm"], parity, "component parity")
    expect(test["revoked_equals_primitive"], ablation, "ablation parity")
    cmp = comparison(test["primitive_rows"], test["ocm_rows"])
    expect(test["comparison"], cmp, "test comparison")
    causal = accepted and parity and ablation and cmp["guided_wins"] > 0 and totals["ocm"] < totals["primitive"]
    terminal = (tour_terminal if not accepted else
                "CANNOT_CHECK_COMPONENT_TRANSPLANT_PARITY" if not parity else
                "CANNOT_CHECK_REVOCATION_ABLATION" if not ablation else
                "NO_CAUSAL_METHOD_CONSUMPTION" if cmp["guided_wins"] <= 0 else
                "NO_AMORTIZED_SEARCH_ON_LENGTH7_TEST" if totals["ocm"] >= totals["primitive"] else
                "CAUSAL_UTILITY_SELECTED_METHOD_REUSE_SUPPORTED_AT_LENGTH7")
    expect(d["terminal"], terminal, "experiment terminal")
    expect(d["causal_method_reuse_supported"], causal, "bounded causal flag")
    total = training_slots + baseline_slots + candidate_slots + totals["ocm"]
    accounting = {"training_slots": training_slots, "baseline_validation_slots": baseline_slots,
                  "all_candidate_validation_slots": candidate_slots,
                  "full_selection_validation_slots": baseline_slots + candidate_slots,
                  "learned_path_through_test_slots": total, "primitive_test_slots": totals["primitive"]}
    for key, value in accounting.items():
        expect(d["accounting"][key], value, f"lifetime accounting: {key}")
    lifetime = ("LIFETIME_SEARCH_SLOTS_PAYBACK_AT_64_LENGTH7_TESTS" if accepted and total < totals["primitive"]
                else "NO_LIFETIME_SEARCH_SLOTS_PAYBACK_AT_64_LENGTH7_TESTS")
    expect(d["lifetime_terminal"], lifetime, "lifetime terminal")
    ocm = d["ocm"]
    for key in ("restart_before_test", "support_withdrawal_ablation"):
        expect(ocm[key], accepted, f"declared adapter flag: {key}")
    if accepted:
        payload = {"kind": "generator.utility-tournament.v1", "fragments": fragments,
                   "training_tasks": sorted(train_ids), "fingerprint": method_id(fragments, train_ids)}
        for key in ("atom_id", "revoked_atom_id"):
            expect(ocm[key], "generator-tournament:" + digest(payload), f"method atom identity: {key}")
        for key in ("training_evidence", "utility_evidence"):
            require(type(ocm[key]) is str and bool(ocm[key]), f"missing {key}")
        require(ocm["training_evidence"] != ocm["utility_evidence"], "collapsed evidence identities")
    else:
        for key in ("atom_id", "revoked_atom_id", "training_evidence", "utility_evidence"):
            expect(ocm[key], None, f"undeployed metadata: {key}")
    return {"schema": "ocm.g2.mathematical-audit.v1", "audit_terminal": "EXACT_G2_RECEIPT_RECONCILED",
            "experiment_terminal": terminal, "lifetime_terminal": lifetime,
            "candidate_count": len(candidates), "guided_wins": cmp["guided_wins"],
            "test_slots": totals, "accounting": accounting,
            "programme_closure": False,
            "not_verified": ["OS-process restart and absence of hidden inherited state",
                             "runtime admission, scope, authority and revocation execution",
                             "historical execution custody and independent authorship",
                             "wall/CPU/storage/energy and complete lifecycle cost",
                             "population generalization, cross-domain transfer and G3-G8"]}


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, f"duplicate JSON key: {key}")
        out[key] = value
    return out


def reject_constant(value):
    raise AuditError(f"non-finite JSON constant: {value}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    started, cpu = time.perf_counter(), time.process_time()
    try:
        with args.receipt.open("rb") as handle:
            raw = handle.read(64 * 1024 * 1024 + 1)
        require(len(raw) <= 64 * 1024 * 1024, "receipt exceeds 64 MiB")
        value = json.loads(raw, object_pairs_hook=unique_object, parse_constant=reject_constant)
        result = audit_result(value)
        result.update({"input_sha256": hashlib.sha256(raw).hexdigest(),
                       "auditor_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                       "audit_wall_seconds": time.perf_counter() - started,
                       "audit_cpu_seconds": time.process_time() - cpu})
        text = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.out is not None:
            with args.out.open("x", encoding="utf-8") as handle:
                handle.write(text)
        print(text, end="")
        return 0
    except (AuditError, KeyError, TypeError, ValueError, OSError, RecursionError, OverflowError) as exc:
        print(json.dumps({"audit_terminal": "CANNOT_CHECK_G2_RECEIPT", "reason": str(exc),
                          "programme_closure": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
