"""Prospective G3.2 scoped failure-memory study.

Research-only. Failed continuations are keyed by remaining-state signature, method,
budget, and environment — never by task id. Ordinary JSON persistence receives the
identical memory and matching algorithm as OCM admit/restart/revoke.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from fractions import Fraction
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import time

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "src"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(REPO / "research" / "g2-cognitive-objects-v1"))

G2_PATH = REPO / "research" / "g2-macro-operator-v1" / "experiment.py"
G2_BLOB = "4c8cb45c182f12a5e09db873fb7625dc37dbf599"
SPEC = importlib.util.spec_from_file_location("g2_macro_parent", G2_PATH)
G2 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(G2)

from g2_cognitive_objects.types import (  # noqa: E402
    UNKNOWN,
    AcquisitionLineage,
    CheckStatus,
    CorrectnessEvidence,
    CurrentAuthorizationState,
    FailureAttemptV1,
    FailureKind,
    InformationVector,
    Liveness,
    OriginCategory,
    ResourceVector,
    ScopeState,
    UsefulnessEvidence,
    Verdict,
    emit,
)

from ocm.kso.ids import content_hash  # noqa: E402
from ocm.kso.space import Atom, Hyperedge  # noqa: E402
from ocm.kso.types import Scope  # noqa: E402
from ocm.kso.warrant import Liveness as KSOLiveness, WarrantProfile  # noqa: E402
from ocm.runtime.ocm_runtime import OCMRuntime  # noqa: E402
from ocm.store.evidence import Channel  # noqa: E402

METHOD_BLOB = "50323a33418b8ef8bb6500ddeba4b9d1f795e9e3"
TRAIN_SALT = "orion-ocm-g3-failure-train-v1"
TEST_SALT = "orion-ocm-g3-failure-test-v1"
TRAIN_N = 24
TEST_N = 16
TRAIN_MIN_LENGTH = 5
TEST_MIN_LENGTH = 6
METHODS = G2.M.PRIMITIVES
ENV_V1 = "polynomial-backward-residual.v1"
SCOPE = Scope.of("polynomial-failure-memory.v1")
IDENTITY = (Fraction(0), Fraction(1))
SCHEMA = "g3.failure-memory.result.v1"

# Prior outcome-exposed length-6 identities. Length 5 was not used by G2/G3
# macro/composition salts; documented rather than reconstructed as empty.
PRIOR_LENGTH6 = (
    ("orion-ocm-g2-length6-test-v1", 64),
    ("orion-ocm-g2-utility-validation-v1", 32),
    (G2.TRAIN_SALT, G2.TRAIN_N),
    ("orion-ocm-g3-a-training-v1", 48),
    ("orion-ocm-g3-b-training-v1", 48),
)
G3_PRIOR_LENGTH6_PREFIX = PRIOR_LENGTH6[:3]


def git_blob_sha1(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def ranked_stratum(population, length: int, salt: str, n: int, exclude=()):
    excluded = set(exclude)
    pool = [
        task for _fp, (minimum, task) in population.items()
        if minimum == length and task.fingerprint not in excluded
    ]
    chosen = tuple(sorted(
        pool,
        key=lambda task: (G2.stable_rank(salt, task.fingerprint), task.fingerprint),
    )[:n])
    if len(chosen) != n:
        raise RuntimeError(f"stratum {length}/{salt} too small: {len(chosen)} < {n}")
    return chosen


def prior_exposure(population, length: int, specs):
    out = set()
    for salt, n in specs:
        # G3 A/B training already excluded earlier length-6 salts. Reconstruct that
        # nested exclusion so we do not drop the wrong 48 identities.
        if salt == "orion-ocm-g3-a-training-v1":
            exposed = set()
            for prior_salt, prior_n in G3_PRIOR_LENGTH6_PREFIX:
                exposed.update(
                    task.fingerprint for task in ranked_stratum(population, length, prior_salt, prior_n)
                )
            out.update(task.fingerprint for task in ranked_stratum(population, length, salt, n, exposed))
        elif salt == "orion-ocm-g3-b-training-v1":
            exposed = set()
            for prior_salt, prior_n in G3_PRIOR_LENGTH6_PREFIX:
                exposed.update(
                    task.fingerprint for task in ranked_stratum(population, length, prior_salt, prior_n)
                )
            a_ids = {
                task.fingerprint
                for task in ranked_stratum(
                    population, length, "orion-ocm-g3-a-training-v1", 48, exposed
                )
            }
            out.update(task.fingerprint for task in ranked_stratum(population, length, salt, n, exposed | a_ids))
        else:
            out.update(task.fingerprint for task in ranked_stratum(population, length, salt, n))
    return out


def frozen_partition():
    population = G2.minimal_length_population(6)
    training = ranked_stratum(population, TRAIN_MIN_LENGTH, TRAIN_SALT, TRAIN_N)
    exposed6 = prior_exposure(population, TEST_MIN_LENGTH, PRIOR_LENGTH6)
    test = ranked_stratum(population, TEST_MIN_LENGTH, TEST_SALT, TEST_N, exposed6)
    ids = [task.fingerprint for task in training + test]
    if len(ids) != len(set(ids)):
        raise RuntimeError("train/test overlap")
    if exposed6 & {task.fingerprint for task in test}:
        raise RuntimeError("test overlaps previously exposed length-6 identities")
    return {
        "population": population,
        "training": training,
        "test": test,
        "exposed6": exposed6,
        "length5_prior_exposure": "none: G2 macro and G3 composition salts used lengths 6/7/8 only",
    }


def canonicalize(coeffs):
    coeffs = tuple(Fraction(c) for c in coeffs)
    while len(coeffs) > 1 and coeffs[-1] == 0:
        coeffs = coeffs[:-1]
    return coeffs


def remaining_signature(coeffs) -> str:
    """Remaining-state key: canonical residual coefficients. Never a task id."""
    return ",".join(str(c) for c in canonicalize(coeffs))


def parse_signature(sig: str):
    parts = sig.split(",") if sig else []
    return canonicalize(Fraction(p) for p in parts)


def integer_sqrt(n: int):
    if n < 0:
        return None
    r = int(n ** 0.5)
    while r * r < n:
        r += 1
    while r * r > n:
        r -= 1
    return r if r * r == n else None


def rational_sqrt(value: Fraction):
    a = integer_sqrt(value.numerator)
    b = integer_sqrt(value.denominator)
    if a is None or b is None:
        return None
    return Fraction(a, b)


def polynomial_sqrt(coeffs):
    coeffs = canonicalize(coeffs)
    deg = len(coeffs) - 1
    if deg % 2:
        return None
    d = deg // 2
    pad = list(coeffs) + [Fraction(0)] * max(0, 2 * d + 1 - len(coeffs))
    lead = rational_sqrt(pad[2 * d])
    if lead is None:
        return None
    if lead == 0 and d > 0:
        return None
    q = [Fraction(0)] * (d + 1)
    q[d] = lead
    two_lead = 2 * lead
    for k in range(d - 1, -1, -1):
        n = d + k
        acc = Fraction(0)
        for i in range(k + 1, d + 1):
            j = n - i
            if 0 <= j <= d and i != k:
                acc += q[i] * q[j]
        if two_lead == 0:
            return None
        q[k] = (pad[n] - acc) / two_lead
    squared = [Fraction(0)] * (2 * d + 1)
    for i, a in enumerate(q):
        for j, b in enumerate(q):
            squared[i + j] += a * b
    if canonicalize(squared) != canonicalize(coeffs):
        return None
    return canonicalize(q)


def invert_method(method: str, coeffs):
    coeffs = canonicalize(coeffs)
    if method == "inc":
        c = list(coeffs)
        c[0] -= 1
        return canonicalize(c)
    if method == "dec":
        c = list(coeffs)
        c[0] += 1
        return canonicalize(c)
    if method == "double":
        return canonicalize(tuple(c / 2 for c in coeffs))
    if method == "square":
        return polynomial_sqrt(coeffs)
    raise ValueError(f"unknown method {method}")


def coefficient_l1(a, b) -> Fraction:
    a, b = canonicalize(a), canonicalize(b)
    n = max(len(a), len(b))
    ap = a + (Fraction(0),) * (n - len(a))
    bp = b + (Fraction(0),) * (n - len(b))
    return sum(abs(x - y) for x, y in zip(ap, bp))


def budget_id(max_length: int) -> str:
    return f"max_length={max_length}"


@dataclass
class Meter:
    enumerations: int = 0
    lookups: int = 0
    skipped: int = 0
    records_written: int = 0
    extra_retries: int = 0
    impossibility_cuts: int = 0


@dataclass
class SearchOutcome:
    solved: bool
    program: tuple[str, ...] | None
    complete: bool
    kind: str
    enumerations: int
    lookups: int
    skipped: int


@dataclass
class FailureMemory:
    """Scoped remaining-state memory. Skip keys never include a task id."""

    policy: str = "scoped"
    env: str = ENV_V1
    method_failures: dict = field(default_factory=dict)
    impossibilities: dict = field(default_factory=dict)
    root_failures_by_task: dict = field(default_factory=dict)
    failed_task_coefficients: list = field(default_factory=list)
    task_blacklist: set = field(default_factory=set)
    records: list = field(default_factory=list)

    def skip_key(self, method: str, remaining_sig: str, budget: str, env: str):
        return (method, remaining_sig, budget, env)

    def compact(self, method_id, remaining_sig, budget, env, failure_kind, outcome, complete, feedback):
        return {
            "method_id": method_id,
            "remaining_sig": remaining_sig,
            "budget": budget,
            "environment_version": env,
            "failure_kind": failure_kind,
            "outcome": outcome,
            "complete": complete,
            "feedback": feedback,
        }

    def remember(self, record: dict, *, task_fingerprint: str | None, root: bool):
        kind = record["failure_kind"]
        key = self.skip_key(
            record["method_id"], record["remaining_sig"], record["budget"], record["environment_version"]
        )
        if kind == "TASK_IMPOSSIBILITY":
            self.impossibilities[(record["remaining_sig"], record["budget"], record["environment_version"])] = record
        else:
            self.method_failures[key] = record
        self.records.append(record)
        if root and task_fingerprint is not None:
            self.root_failures_by_task.setdefault(task_fingerprint, []).append(record)
            if kind == "TASK_IMPOSSIBILITY":
                self.task_blacklist.add(task_fingerprint)
                self.failed_task_coefficients.append(
                    (task_fingerprint, parse_signature(record["remaining_sig"]))
                )

    def lookup_method(self, method: str, remaining_sig: str, budget: str, env: str, meter: Meter) -> dict | None:
        meter.lookups += 1
        if self.policy == "none":
            return None
        if self.policy == "overclaim":
            # Any prior method failure at this remaining state, ignoring method/budget.
            for record in self.method_failures.values():
                if record["remaining_sig"] == remaining_sig and record["environment_version"] == env:
                    meter.skipped += 1
                    return record
            if (remaining_sig, budget, env) in self.impossibilities:
                meter.skipped += 1
                return self.impossibilities[(remaining_sig, budget, env)]
            for (sig, _b, e), record in self.impossibilities.items():
                if sig == remaining_sig and e == env:
                    meter.skipped += 1
                    return record
            return None
        if self.policy == "cegar":
            degree = remaining_sig.count(",")
            for key, record in self.method_failures.items():
                rec_method, rec_sig, rec_budget, rec_env = key
                if rec_method == method and rec_budget == budget and rec_env == env and rec_sig.count(",") == degree:
                    meter.skipped += 1
                    return record
            if (remaining_sig, budget, env) in self.impossibilities:
                meter.skipped += 1
                return self.impossibilities[(remaining_sig, budget, env)]
            return None
        if self.policy == "cbr":
            return None
        if self.policy == "blacklist":
            return None
        hit = self.method_failures.get(self.skip_key(method, remaining_sig, budget, env))
        if hit is not None:
            meter.skipped += 1
            return hit
        return None

    def lookup_impossibility(self, remaining_sig: str, budget: str, env: str, meter: Meter) -> dict | None:
        meter.lookups += 1
        if self.policy in {"none", "cbr", "blacklist"}:
            return None
        if self.policy == "overclaim":
            for (sig, _b, e), record in self.impossibilities.items():
                if sig == remaining_sig and e == env:
                    meter.skipped += 1
                    meter.impossibility_cuts += 1
                    return record
            for record in self.method_failures.values():
                if record["remaining_sig"] == remaining_sig and record["environment_version"] == env:
                    meter.skipped += 1
                    meter.impossibility_cuts += 1
                    return record
            return None
        hit = self.impossibilities.get((remaining_sig, budget, env))
        if hit is not None:
            meter.skipped += 1
            meter.impossibility_cuts += 1
            return hit
        return None

    def cbr_methods_to_skip(self, remaining_coeffs, meter: Meter) -> set[str]:
        meter.lookups += 1
        if self.policy != "cbr" or not self.failed_task_coefficients:
            return set()
        nearest = min(
            self.failed_task_coefficients,
            key=lambda item: (coefficient_l1(remaining_coeffs, item[1]), item[0]),
        )
        methods = {
            record["method_id"]
            for record in self.root_failures_by_task.get(nearest[0], ())
            if record["failure_kind"] == "METHOD_FAILURE"
        }
        return methods

    def blacklist_blocks(self, task_fingerprint: str, meter: Meter) -> bool:
        meter.lookups += 1
        return self.policy == "blacklist" and task_fingerprint in self.task_blacklist

    def storage_bytes(self) -> int:
        payload = json.dumps(self.export_records(), sort_keys=True, separators=(",", ":")).encode()
        return len(payload)

    def export_records(self) -> list:
        # Persist skip material only. Task ids are intentionally absent.
        out = []
        seen = set()
        for record in self.records:
            key = (
                record["method_id"], record["remaining_sig"], record["budget"],
                record["environment_version"], record["failure_kind"],
            )
            if key in seen:
                continue
            seen.add(key)
            out.append({k: record[k] for k in (
                "method_id", "remaining_sig", "budget", "environment_version",
                "failure_kind", "outcome", "complete", "feedback",
            )})
        return out

    def keys_contain_task_id(self, task_ids) -> bool:
        forbidden = set(task_ids)
        for method, remaining_sig, budget, env in self.method_failures:
            if method in forbidden or remaining_sig in forbidden or budget in forbidden or env in forbidden:
                return True
            if remaining_sig in forbidden:
                return True
        for remaining_sig, budget, env in self.impossibilities:
            if remaining_sig in forbidden or budget in forbidden or env in forbidden:
                return True
        return False

    @classmethod
    def from_records(cls, records, *, policy="scoped", env=ENV_V1):
        memory = cls(policy=policy, env=env)
        for record in records:
            memory.remember(record, task_fingerprint=None, root=False)
        return memory


def clone_memory(memory: FailureMemory, *, policy: str | None = None) -> FailureMemory:
    out = FailureMemory(policy=policy or memory.policy, env=memory.env)
    out.method_failures = dict(memory.method_failures)
    out.impossibilities = dict(memory.impossibilities)
    out.root_failures_by_task = {k: list(v) for k, v in memory.root_failures_by_task.items()}
    out.failed_task_coefficients = list(memory.failed_task_coefficients)
    out.task_blacklist = set(memory.task_blacklist)
    out.records = list(memory.records)
    return out


def solve_remaining(
    remaining,
    max_length: int,
    memory: FailureMemory,
    env: str,
    meter: Meter,
    *,
    record: bool,
    methods: tuple[str, ...] = METHODS,
    task_fingerprint: str | None = None,
    root: bool = False,
    memo: dict | None = None,
    reopen_from: FailureMemory | None = None,
):
    remaining = canonicalize(remaining)
    if memo is None:
        memo = {}
    if remaining == IDENTITY:
        return SearchOutcome(True, (), True, "SOLVED", meter.enumerations, meter.lookups, meter.skipped)
    sig = remaining_signature(remaining)
    budget = budget_id(max_length)
    memo_key = (sig, max_length, env, memory.policy)
    if memo_key in memo:
        return memo[memo_key]

    if task_fingerprint is not None and root and memory.blacklist_blocks(task_fingerprint, meter):
        outcome = SearchOutcome(False, None, False, "BLACKLISTED", meter.enumerations, meter.lookups, meter.skipped)
        memo[memo_key] = outcome
        return outcome

    if max_length <= 0:
        kind = "TASK_IMPOSSIBILITY"
        if record:
            rec = memory.compact(UNKNOWN, sig, budget, env, kind, "GRAMMAR_EMPTY", True, "non-identity residual at length 0")
            memory.remember(rec, task_fingerprint=task_fingerprint, root=root)
            meter.records_written += 1
        outcome = SearchOutcome(False, None, True, kind, meter.enumerations, meter.lookups, meter.skipped)
        memo[memo_key] = outcome
        return outcome

    if memory.lookup_impossibility(sig, budget, env, meter) is not None:
        outcome = SearchOutcome(False, None, True, "TASK_IMPOSSIBILITY", meter.enumerations, meter.lookups, meter.skipped)
        memo[memo_key] = outcome
        return outcome

    # CBR is a task-level parent: nearest failed TASK by coefficient L1, not a remaining-state key.
    cbr_skip = memory.cbr_methods_to_skip(remaining, meter) if memory.policy == "cbr" and root else set()
    method_complete_fails = []
    incomplete = False
    for method in methods:
        if reopen_from is not None:
            old_hits = [
                rec for rec in reopen_from.method_failures.values()
                if rec["method_id"] == method and rec["remaining_sig"] == sig and rec["environment_version"] == env
            ]
            if old_hits:
                meter.extra_retries += 1
        skip_rec = memory.lookup_method(method, sig, budget, env, meter)
        if skip_rec is not None:
            method_complete_fails.append(bool(skip_rec.get("complete")))
            continue
        if method in cbr_skip:
            meter.skipped += 1
            method_complete_fails.append(True)
            continue
        meter.enumerations += 1
        inverted = invert_method(method, remaining)
        if inverted is None:
            if record:
                rec = memory.compact(
                    method, sig, budget, env, "METHOD_FAILURE", "INVERT_IMPOSSIBLE", True,
                    "method cannot produce this remaining polynomial",
                )
                memory.remember(rec, task_fingerprint=task_fingerprint, root=root)
                meter.records_written += 1
            method_complete_fails.append(True)
            continue
        sub = solve_remaining(
            inverted, max_length - 1, memory, env, meter,
            record=record, methods=methods, task_fingerprint=task_fingerprint, root=False,
            memo=memo, reopen_from=reopen_from,
        )
        if sub.solved:
            program = sub.program + (method,)
            if G2.M.normal_form(program) != remaining:
                raise RuntimeError("backward reconstruction failed exact verification")
            outcome = SearchOutcome(True, program, True, "SOLVED", meter.enumerations, meter.lookups, meter.skipped)
            memo[memo_key] = outcome
            return outcome
        if record:
            rec = memory.compact(
                method, sig, budget, env, "METHOD_FAILURE",
                "CONTINUATION_FAILED", bool(sub.complete),
                "method inverted but residual unsolved under this bound",
            )
            memory.remember(rec, task_fingerprint=task_fingerprint, root=root)
            meter.records_written += 1
        method_complete_fails.append(bool(sub.complete))
        if not sub.complete:
            incomplete = True

    all_complete = bool(method_complete_fails) and all(method_complete_fails) and not incomplete
    kind = "TASK_IMPOSSIBILITY" if all_complete else "UNKNOWN"
    if record and all_complete:
        rec = memory.compact(
            UNKNOWN, sig, budget, env, "TASK_IMPOSSIBILITY", "ALL_METHODS_EXHAUSTED", True,
            "full grammar enumerated under the remaining-length bound",
        )
        memory.remember(rec, task_fingerprint=task_fingerprint, root=root)
        meter.records_written += 1
    elif record and not all_complete:
        rec = memory.compact(
            UNKNOWN, sig, budget, env, "UNKNOWN", "PARTIAL_EXHAUSTION", False,
            "not every method received a completeness certificate",
        )
        memory.remember(rec, task_fingerprint=task_fingerprint, root=root)
        meter.records_written += 1
    outcome = SearchOutcome(False, None, all_complete, kind, meter.enumerations, meter.lookups, meter.skipped)
    memo[memo_key] = outcome
    return outcome


def solve_task(task, max_length: int, memory: FailureMemory, env: str, *, record: bool, reopen_from=None):
    meter = Meter()
    start_e, start_l, start_s = meter.enumerations, meter.lookups, meter.skipped
    outcome = solve_remaining(
        task.coefficients, max_length, memory, env, meter,
        record=record, task_fingerprint=task.fingerprint, root=True, reopen_from=reopen_from,
    )
    if outcome.solved:
        if G2.M.normal_form(tuple(outcome.program)) != task.coefficients:
            raise RuntimeError(f"solution failed verification {task.fingerprint}")
    return {
        "task": task.fingerprint,
        "solved": outcome.solved,
        "program": list(outcome.program) if outcome.program is not None else None,
        "complete": outcome.complete,
        "kind": outcome.kind,
        "enumerations": meter.enumerations - start_e,
        "lookups": meter.lookups - start_l,
        "skipped": meter.skipped - start_s,
        "extra_retries": meter.extra_retries,
        "impossibility_cuts": meter.impossibility_cuts,
        "records_written": meter.records_written,
        "remaining_sig": remaining_signature(task.coefficients),
    }


def evaluate_tasks(tasks, max_length: int, memory: FailureMemory, env: str, *, record: bool, reopen_from=None):
    rows = [solve_task(task, max_length, memory, env, record=record, reopen_from=reopen_from) for task in tasks]
    return {
        "rows": rows,
        "solved": sum(1 for row in rows if row["solved"]),
        "enumerations": sum(row["enumerations"] for row in rows),
        "lookups": sum(row["lookups"] for row in rows),
        "skipped": sum(row["skipped"] for row in rows),
        "extra_retries": sum(row["extra_retries"] for row in rows),
        "impossibility_cuts": sum(row["impossibility_cuts"] for row in rows),
        "records_written": sum(row["records_written"] for row in rows),
    }


def rows_equal(a_rows, b_rows) -> bool:
    return all(
        a["task"] == b["task"]
        and a["solved"] == b["solved"]
        and tuple(a["program"] or ()) == tuple(b["program"] or ())
        and a["enumerations"] == b["enumerations"]
        and a["kind"] == b["kind"]
        for a, b in zip(a_rows, b_rows)
    )


def make_failure_attempt(record: dict, *, task_id: str = UNKNOWN) -> FailureAttemptV1:
    remaining_sig = record["remaining_sig"]
    scope = ScopeState(contexts=(f"remaining:{remaining_sig}",), epoch_start=0.0, epoch_end=None)
    kind = FailureKind(record["failure_kind"])
    notes = [
        "scope key is remaining-state signature, not task id",
        f"complete={record['complete']}",
    ]
    return FailureAttemptV1(
        attempt_id="g3.fail:" + content_hash(record),
        method_id=record["method_id"],
        task_id=task_id,
        scope=scope,
        budget=record["budget"],
        environment_version=record["environment_version"],
        outcome=record["outcome"],
        feedback=record["feedback"],
        failure_kind=kind,
        resources=ResourceVector(work_units=1, notes=("one remaining-state continuation",)),
        acquisition_lineage=AcquisitionLineage(
            origin_category=OriginCategory.LEARNED_APPLICABILITY,
            episode_ids=("g3.failure-memory.train.v1",),
            status=CheckStatus.MEASURED,
            discovery_evidence_id="g3.failure-memory.discovery.v1",
            information=InformationVector(grounded_observations=1),
        ),
        correctness=CorrectnessEvidence(
            checker_id=G2.M.CHECKER,
            verdict=Verdict.FAIL,
            status=CheckStatus.MEASURED,
            independent_of_usefulness=True,
        ),
        usefulness=UsefulnessEvidence(
            independent_of_correctness=True,
            status=CheckStatus.UNKNOWN,
        ),
        authorization=CurrentAuthorizationState(
            admitted=True,
            proof_liveness=Liveness.LIVE,
            applicability_liveness=Liveness.LIVE,
            serving_liveness=Liveness.LIVE,
            warrant_ids=("g3.failure-memory.support.v1",),
            scope=scope,
            status=CheckStatus.MEASURED,
        ),
        notes=tuple(notes),
    )


def sample_attempts(memory: FailureMemory, limit: int = 6) -> list:
    samples = []
    wanted = ["METHOD_FAILURE", "TASK_IMPOSSIBILITY", "UNKNOWN"]
    for kind in wanted:
        for record in memory.records:
            if record["failure_kind"] == kind:
                obj = make_failure_attempt(record)
                raw = emit(obj)
                samples.append(json.loads(raw.decode()))
                break
    for record in memory.records:
        if len(samples) >= limit:
            break
        obj = make_failure_attempt(record)
        plain = json.loads(emit(obj).decode())
        if plain not in samples:
            samples.append(plain)
    return samples


def ordinary_persist(path: Path, records):
    payload = {"records": records, "fingerprint": content_hash({"records": records})}
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


def ordinary_load(path: Path):
    payload = json.loads(path.read_text())
    records = payload["records"]
    if content_hash({"records": records}) != payload["fingerprint"]:
        raise RuntimeError("ordinary failure-memory identity mismatch")
    return records


def admit_memory(root: Path, records, training_receipt, utility_receipt, revoke=False):
    runtime = OCMRuntime(root)
    _tr, training_evidence = runtime.admit_evidence(
        training_receipt, Channel.PROOF, "g3-failure-training.v1", scope=SCOPE,
    )
    _ur, utility_evidence = runtime.admit_evidence(
        utility_receipt, Channel.OBSERVATION, "g3-failure-utility.v1", scope=SCOPE,
    )
    warrant = WarrantProfile.of({training_evidence, utility_evidence})
    source_payload = {
        "kind": "g3.failure.support.v1",
        "training": content_hash(training_receipt),
        "utility": content_hash(utility_receipt),
    }
    source_id = "g3-failure-support:" + content_hash(source_payload)
    runtime.admit_object(
        Atom(
            source_id, "proof", warrant, scope=SCOPE, quarantined=True,
            content_ref=content_hash(source_payload), meta=tuple(source_payload.items()),
        ),
        (),
        "OBSERVATION",
    )
    payload = {
        "kind": "failure.memory.v1",
        "records": records,
        "fingerprint": content_hash({"records": records}),
    }
    atom_id = "failure-memory:" + content_hash({"kind": payload["kind"], "fingerprint": payload["fingerprint"]})
    edge = Hyperedge("support:" + atom_id, (source_id,), (atom_id,), "SUPPORT", warrant=warrant)
    runtime.admit_object(
        Atom(
            atom_id, "procedure", warrant, scope=SCOPE,
            content_ref=content_hash(payload), meta=tuple(payload.items()),
        ),
        (edge,),
        "OBSERVATION",
    )
    if revoke:
        runtime.revoke((training_evidence,))
    runtime.persist()

    replay = OCMRuntime(root)
    atom = replay.state.ks.atom_map().get(atom_id)
    if revoke:
        if atom is not None and atom.liveness(replay.state.revoked) is KSOLiveness.LIVE:
            raise RuntimeError("revoked failure memory remained live")
        return None, atom_id, training_evidence, utility_evidence
    if atom is None or atom.liveness(replay.state.revoked) is not KSOLiveness.LIVE:
        raise RuntimeError("failure memory did not survive restart")
    stored = dict(atom.meta)
    if atom.content_ref != content_hash(stored):
        raise RuntimeError("failure-memory content identity mismatch")
    loaded = stored["records"]
    if isinstance(loaded, tuple):
        loaded = list(loaded)
    loaded = [dict(row) for row in loaded]
    if content_hash({"records": loaded}) != stored["fingerprint"]:
        # Meta round-trip may freeze lists to tuples; compare against the admitted payload.
        if content_hash({"records": stored["records"]}) != stored["fingerprint"]:
            raise RuntimeError("failure-memory fingerprint mismatch")
    return loaded, atom_id, training_evidence, utility_evidence


def outside_scope_witness(memory: FailureMemory, train_eval, test_eval, test_tasks, env: str):
    """A method with a retained METHOD_FAILURE that still succeeds on another remaining state."""
    failed_methods = {}
    for record in memory.records:
        if record["failure_kind"] == "METHOD_FAILURE":
            failed_methods.setdefault(record["method_id"], set()).add(record["remaining_sig"])
    successes = []
    for row in list(train_eval["rows"]) + list(test_eval["rows"]):
        if not row["solved"] or not row["program"]:
            continue
        program = tuple(row["program"])
        remaining = G2.M.normal_form(program)
        for index, method in enumerate(reversed(program)):
            sig = remaining_signature(remaining)
            failed_at = failed_methods.get(method, set())
            if failed_at and sig not in failed_at:
                successes.append({
                    "method_id": method,
                    "success_remaining_sig": sig,
                    "failed_remaining_example": sorted(failed_at)[0],
                    "task": row["task"],
                    "index_from_end": index,
                })
                break
            inverted = invert_method(method, remaining)
            if inverted is None:
                break
            remaining = inverted
        if len(successes) >= 3:
            break
    return successes


def one_method_failure_is_not_impossibility():
    """Protocol fact: a single method miss is METHOD_FAILURE, not TASK_IMPOSSIBILITY."""
    remaining = canonicalize((Fraction(1), Fraction(1)))  # x+1, not a polynomial square
    memory = FailureMemory(policy="none")
    meter = Meter()
    env = ENV_V1
    sig = remaining_signature(remaining)
    budget = budget_id(2)
    inverted = invert_method("square", remaining)
    if inverted is not None:
        raise RuntimeError("expected square invert to fail on x+1")
    rec = memory.compact(
        "square", sig, budget, env, "METHOD_FAILURE", "INVERT_IMPOSSIBLE", True, "square miss",
    )
    memory.remember(rec, task_fingerprint=None, root=False)
    kinds = {record["failure_kind"] for record in memory.records}
    return "METHOD_FAILURE" in kinds and "TASK_IMPOSSIBILITY" not in kinds


def diagnose_parent_table(none_eval, scoped_eval, tms_eval, cbr_eval, cegar_eval, overclaim_eval, blacklist_eval):
    return {
        "none_enumerations": none_eval["enumerations"],
        "scoped_enumerations": scoped_eval["enumerations"],
        "tms_enumerations": tms_eval["enumerations"],
        "cbr_enumerations": cbr_eval["enumerations"],
        "cegar_enumerations": cegar_eval["enumerations"],
        "overclaim_enumerations": overclaim_eval["enumerations"],
        "blacklist_enumerations": blacklist_eval["enumerations"],
        "none_solved": none_eval["solved"],
        "scoped_solved": scoped_eval["solved"],
        "tms_solved": tms_eval["solved"],
        "cbr_solved": cbr_eval["solved"],
        "cegar_solved": cegar_eval["solved"],
        "overclaim_solved": overclaim_eval["solved"],
        "blacklist_solved": blacklist_eval["solved"],
        "tms_ties_scoped": rows_equal(tms_eval["rows"], scoped_eval["rows"]),
        "cbr_ties_scoped": rows_equal(cbr_eval["rows"], scoped_eval["rows"]),
        "cegar_ties_scoped": rows_equal(cegar_eval["rows"], scoped_eval["rows"]),
        "overclaim_ties_scoped": rows_equal(overclaim_eval["rows"], scoped_eval["rows"]),
        "blacklist_ties_none": rows_equal(blacklist_eval["rows"], none_eval["rows"]),
    }


def choose_terminal(
    *,
    ordinary_equals_ocm: bool,
    revoked_equals_none: bool,
    restart_ok: bool,
    harmful: bool,
    reopen_ok: bool,
    blacklist_reopen_fails: bool,
    overclaim_harms: bool,
    useful_skips: bool,
    outside_scope: bool,
    tms_ties: bool,
    none_matches_scoped: bool,
    keys_are_remaining_state: bool,
    single_method_not_impossibility: bool,
):
    if not keys_are_remaining_state:
        return "CANNOT_CHECK_SCOPE_KEY_IS_TASK_ID", False
    if not single_method_not_impossibility:
        return "CANNOT_CHECK_FAILURE_KIND_COLLAPSE", False
    if not ordinary_equals_ocm:
        return "CANNOT_CHECK_COMPONENT_TRANSPLANT_PARITY", False
    if not restart_ok:
        return "CANNOT_CHECK_RESTART_RECONSTRUCTION", False
    if not revoked_equals_none:
        return "CANNOT_CHECK_REVOCATION_ABLATION", False
    if harmful:
        return "HARMFUL_TRANSFER_LIMIT", False
    if none_matches_scoped or not useful_skips:
        return "FAILURE_MEMORY_NOT_USEFUL", False
    if not reopen_ok or not blacklist_reopen_fails:
        return "FAILURE_MEMORY_NOT_USEFUL", False
    if not overclaim_harms:
        return "CANNOT_CHECK_OVERCLAIM_CONTRAST", False
    if not outside_scope:
        return "FAILURE_MEMORY_NOT_USEFUL", False
    if tms_ties and none_matches_scoped:
        return "PARENT_SUFFICIENT", False
    return "FAILURE_MEMORY_USEFUL_AT_SCOPE", True


def run():
    source_path = SRC / "ocm" / "learning" / "methods.py"
    observed_blob = git_blob_sha1(source_path)
    if observed_blob != METHOD_BLOB:
        raise RuntimeError(f"method source drift: {observed_blob}")
    if git_blob_sha1(G2_PATH) != G2_BLOB:
        raise RuntimeError("G2 macro parent source drift")
    if not one_method_failure_is_not_impossibility():
        raise RuntimeError("method failure collapsed into task impossibility")

    start = time.perf_counter()
    parts = frozen_partition()
    training_tasks = parts["training"]
    test_tasks = parts["test"]

    train_memory = FailureMemory(policy="scoped", env=ENV_V1)
    train_eval = evaluate_tasks(training_tasks, TRAIN_MIN_LENGTH, train_memory, ENV_V1, record=True)
    if train_eval["solved"] != TRAIN_N:
        raise RuntimeError("training identities were not reconstructed at declared bound")
    exported = train_memory.export_records()
    if any("task" in record or "task_id" in record or "fingerprint" in record for record in exported):
        raise RuntimeError("persisted skip records must not carry task identity")
    task_ids = [task.fingerprint for task in training_tasks + test_tasks]
    keys_are_remaining_state = not train_memory.keys_contain_task_id(task_ids)

    none_memory = FailureMemory(policy="none", env=ENV_V1)
    none_eval = evaluate_tasks(test_tasks, TEST_MIN_LENGTH, none_memory, ENV_V1, record=False)

    scoped_serve = clone_memory(train_memory, policy="scoped")
    scoped_eval = evaluate_tasks(test_tasks, TEST_MIN_LENGTH, scoped_serve, ENV_V1, record=False)

    tms_serve = clone_memory(train_memory, policy="scoped")
    tms_eval = evaluate_tasks(test_tasks, TEST_MIN_LENGTH, tms_serve, ENV_V1, record=False)

    cegar_serve = clone_memory(train_memory, policy="cegar")
    cegar_eval = evaluate_tasks(test_tasks, TEST_MIN_LENGTH, cegar_serve, ENV_V1, record=False)

    overclaim_serve = clone_memory(train_memory, policy="overclaim")
    overclaim_eval = evaluate_tasks(test_tasks, TEST_MIN_LENGTH, overclaim_serve, ENV_V1, record=False)

    # Regime change: length-4 bound cannot realize min-length-5 training identities.
    tight_memory = FailureMemory(policy="scoped", env=ENV_V1)
    tight_eval = evaluate_tasks(training_tasks, TRAIN_MIN_LENGTH - 1, tight_memory, ENV_V1, record=True)

    cbr_serve = clone_memory(train_memory, policy="cbr")
    cbr_serve.failed_task_coefficients = list(tight_memory.failed_task_coefficients)
    cbr_serve.root_failures_by_task = {k: list(v) for k, v in tight_memory.root_failures_by_task.items()}
    cbr_eval = evaluate_tasks(test_tasks, TEST_MIN_LENGTH, cbr_serve, ENV_V1, record=False)

    blacklist_serve = clone_memory(tight_memory, policy="blacklist")
    blacklist_eval = evaluate_tasks(test_tasks, TEST_MIN_LENGTH, blacklist_serve, ENV_V1, record=False)
    reopen_scoped = clone_memory(tight_memory, policy="scoped")
    reopen_eval = evaluate_tasks(
        training_tasks, TRAIN_MIN_LENGTH, reopen_scoped, ENV_V1, record=False, reopen_from=tight_memory,
    )
    reopen_none = evaluate_tasks(
        training_tasks, TRAIN_MIN_LENGTH, FailureMemory(policy="none", env=ENV_V1), ENV_V1, record=False,
    )
    reopen_blacklist = evaluate_tasks(
        training_tasks, TRAIN_MIN_LENGTH, clone_memory(tight_memory, policy="blacklist"), ENV_V1, record=False,
    )
    reopen_ok = reopen_eval["solved"] == TRAIN_N and reopen_eval["solved"] > tight_eval["solved"]
    blacklist_reopen_fails = reopen_blacklist["solved"] < TRAIN_N

    training_receipt = {
        "schema": "g3.failure.training.v1",
        "source_blob": METHOD_BLOB,
        "training_ids": [task.fingerprint for task in training_tasks],
        "record_count": len(exported),
        "record_fingerprint": content_hash({"records": exported}),
    }
    utility_receipt = {
        "schema": "g3.failure.utility.v1",
        "test_ids": [task.fingerprint for task in test_tasks],
        "scoped_enumerations": scoped_eval["enumerations"],
        "none_enumerations": none_eval["enumerations"],
        "skipped": scoped_eval["skipped"],
    }

    with tempfile.TemporaryDirectory(prefix="ocm-g3-failmem-") as temp_dir:
        root = Path(temp_dir)
        ordinary_path = root / "ordinary-failure-memory.json"
        ordinary_persist(ordinary_path, exported)
        ordinary_records = ordinary_load(ordinary_path)
        ocm_records, atom_id, training_evidence, utility_evidence = admit_memory(
            root / "ocm-live", exported, training_receipt, utility_receipt, revoke=False,
        )
        revoked_records, _revoked_atom, _rte, _rue = admit_memory(
            root / "ocm-revoked", exported, training_receipt, utility_receipt, revoke=True,
        )

    ordinary_eval = evaluate_tasks(
        test_tasks, TEST_MIN_LENGTH, FailureMemory.from_records(ordinary_records, policy="scoped"), ENV_V1, record=False,
    )
    ocm_eval = evaluate_tasks(
        test_tasks, TEST_MIN_LENGTH, FailureMemory.from_records(ocm_records, policy="scoped"), ENV_V1, record=False,
    )
    revoked_eval = evaluate_tasks(
        test_tasks, TEST_MIN_LENGTH,
        FailureMemory(policy="none") if revoked_records is None else FailureMemory.from_records(revoked_records),
        ENV_V1, record=False,
    )
    ordinary_equals_ocm = rows_equal(ordinary_eval["rows"], ocm_eval["rows"]) and rows_equal(
        scoped_eval["rows"], ocm_eval["rows"]
    )
    revoked_equals_none = rows_equal(revoked_eval["rows"], none_eval["rows"])
    restart_ok = ocm_records is not None and content_hash({"records": ocm_records}) == content_hash({"records": exported})

    outside = outside_scope_witness(train_memory, train_eval, scoped_eval, test_tasks, ENV_V1)
    harmful = any(
        (not scoped_row["solved"] and none_row["solved"])
        for scoped_row, none_row in zip(scoped_eval["rows"], none_eval["rows"])
    )
    overclaim_harms = overclaim_eval["solved"] < none_eval["solved"] or any(
        (not over_row["solved"] and none_row["solved"])
        for over_row, none_row in zip(overclaim_eval["rows"], none_eval["rows"])
    )
    useful_skips = scoped_eval["skipped"] > 0 and scoped_eval["enumerations"] < none_eval["enumerations"]
    none_matches_scoped = rows_equal(none_eval["rows"], scoped_eval["rows"]) and scoped_eval["enumerations"] == none_eval["enumerations"]
    parents = diagnose_parent_table(
        none_eval, scoped_eval, tms_eval, cbr_eval, cegar_eval, overclaim_eval, blacklist_eval,
    )
    terminal, useful = choose_terminal(
        ordinary_equals_ocm=ordinary_equals_ocm,
        revoked_equals_none=revoked_equals_none,
        restart_ok=restart_ok,
        harmful=harmful,
        reopen_ok=reopen_ok,
        blacklist_reopen_fails=blacklist_reopen_fails,
        overclaim_harms=overclaim_harms,
        useful_skips=useful_skips,
        outside_scope=bool(outside),
        tms_ties=parents["tms_ties_scoped"],
        none_matches_scoped=none_matches_scoped,
        keys_are_remaining_state=keys_are_remaining_state,
        single_method_not_impossibility=True,
    )

    root_cause = None
    if terminal != "FAILURE_MEMORY_USEFUL_AT_SCOPE":
        root_cause = {
            "terminal": terminal,
            "useful_skips": useful_skips,
            "outside_scope": bool(outside),
            "reopen_ok": reopen_ok,
            "blacklist_reopen_fails": blacklist_reopen_fails,
            "overclaim_harms": overclaim_harms,
            "harmful": harmful,
            "none_enumerations": none_eval["enumerations"],
            "scoped_enumerations": scoped_eval["enumerations"],
            "note": (
                "v1 remaining-state keys are residual coefficient polynomials after backward inversion, "
                "budget-scoped by remaining length. A negative does not license salt edits."
            ),
        }

    kind_counts = {}
    for record in exported:
        kind_counts[record["failure_kind"]] = kind_counts.get(record["failure_kind"], 0) + 1

    return {
        "schema": SCHEMA,
        "terminal": terminal,
        "failure_memory_useful_at_scope": useful,
        "method_blob": METHOD_BLOB,
        "partition": {
            "training_n": TRAIN_N,
            "test_n": TEST_N,
            "training_min_length": TRAIN_MIN_LENGTH,
            "test_min_length": TEST_MIN_LENGTH,
            "training_salt": TRAIN_SALT,
            "test_salt": TEST_SALT,
            "training_ids": [task.fingerprint for task in training_tasks],
            "test_ids": [task.fingerprint for task in test_tasks],
            "prior_exposed_length6_n": len(parts["exposed6"]),
            "length5_prior_exposure": parts["length5_prior_exposure"],
            "population_counts": {
                str(length): sum(1 for minimum, _task in parts["population"].values() if minimum == length)
                for length in (5, 6)
            },
        },
        "training": {
            "solved": train_eval["solved"],
            "enumerations": train_eval["enumerations"],
            "records": len(exported),
            "storage_bytes": train_memory.storage_bytes(),
            "failure_kind_counts": kind_counts,
            "rows": train_eval["rows"],
        },
        "test": {
            "none": none_eval,
            "scoped": scoped_eval,
            "tms_nogood": tms_eval,
            "cbr": cbr_eval,
            "cegar": cegar_eval,
            "overclaim": overclaim_eval,
            "blacklist": blacklist_eval,
            "ordinary": ordinary_eval,
            "ocm": ocm_eval,
            "revoked": revoked_eval,
            "ordinary_equals_ocm": ordinary_equals_ocm,
            "revoked_equals_none": revoked_equals_none,
            "enumeration_saving_vs_none": none_eval["enumerations"] - scoped_eval["enumerations"],
        },
        "parents": parents,
        "reopen": {
            "tight_max_length": TRAIN_MIN_LENGTH - 1,
            "tight_solved": tight_eval["solved"],
            "scoped_reopen_solved": reopen_eval["solved"],
            "none_reopen_solved": reopen_none["solved"],
            "blacklist_reopen_solved": reopen_blacklist["solved"],
            "scoped_extra_retries": reopen_eval["extra_retries"],
            "blacklist_fails_reopen": blacklist_reopen_fails,
            "scoped_reopens": reopen_ok,
        },
        "distinctions": {
            "keys_are_remaining_state": keys_are_remaining_state,
            "exported_records_omit_task_id": True,
            "single_method_failure_is_not_task_impossibility": True,
            "outside_scope_successes": outside,
            "overclaim_harms": overclaim_harms,
            "harmful_scoped_transfer": harmful,
        },
        "failure_attempts_v1": sample_attempts(train_memory),
        "accounting": {
            "stored_records": len(exported),
            "storage_bytes": train_memory.storage_bytes(),
            "index_lookups_test_scoped": scoped_eval["lookups"],
            "skipped_enumerations_test_scoped": scoped_eval["skipped"],
            "extra_retries_after_reopen": reopen_eval["extra_retries"],
            "study_wall_seconds": time.perf_counter() - start,
            "note": "Coordinates are research search work, not a whole-architecture net-benefit claim.",
        },
        "ocm": {
            "atom_id": atom_id,
            "training_evidence": training_evidence,
            "utility_evidence": utility_evidence,
            "restart_before_test": True,
            "support_withdrawal_ablation": True,
        },
        "root_cause_if_negative": root_cause,
        "claim_boundary": (
            "Bounded remaining-state failure memory in one exact polynomial residual-search ecology. "
            "The identical ordinary JSON parent receives the same records and skip rule; TMS/nogood with "
            "the same (method, remaining_state, budget) key is expected to tie. No OCM architecture residual, "
            "cross-domain, or whole-resource benefit claim. Logical ATMS nogoods are not used to promote a "
            "budget miss to task impossibility."
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
        "enumeration_saving_vs_none": result["test"]["enumeration_saving_vs_none"],
        "stored_records": result["accounting"]["stored_records"],
        "ordinary_equals_ocm": result["test"]["ordinary_equals_ocm"],
        "blacklist_fails_reopen": result["reopen"]["blacklist_fails_reopen"],
        "overclaim_harms": result["distinctions"]["overclaim_harms"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
