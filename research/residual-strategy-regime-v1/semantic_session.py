"""Exact, reusable bounded polynomial search; conventional semantic BFS donor.

This is a new research engine, not a change to ``methods.solve``. Its query
budget counts newly evaluated semantic transitions, NOT that solver's slots.
State merging is valid because equal rational polynomials remain equal under
every primitive. Breadth-first discovery retains a shortest primitive word.
It does not promise minimum arithmetic cost or infer an unreachable target from
a timeout. No task universe or target generator is supplied to this engine.

Snapshots are untrusted hints: restore replays every recorded transition and
compares the complete canonical state. Replay costs are included in totals.
External authority/warrant checks belong to a governed admission wrapper.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

from ocm.learning import methods as M


VERSION = "ocm.semantic-bfs-lifetime.v1"
COUNTERS = (
    "transitions", "arithmetic_additions", "arithmetic_multiplications",
    "index_probes", "index_key_coefficients", "index_writes", "answer_checks",
    "answer_program_length", "checkpoint_bytes_written", "checkpoint_bytes_read",
    "restore_transitions", "checkpoints", "restores", "resets",
)


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("ascii")


def _source_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _normal_form_cost(program):
    """Exact Fraction +/* count of M.normal_form, including zero coefficients."""
    width, additions, multiplications = 2, 0, 0
    for op in program:
        if op in ("inc", "dec"):
            additions += 1
        elif op == "double":
            multiplications += width
        else:
            additions += width * width
            multiplications += width * width
            width = 2 * width - 1
    return additions, multiplications


class SemanticSearchSession:
    """Lazily extend one exact BFS and reuse it across distinct specifications."""

    def __init__(self, max_length=4):
        if type(max_length) is not int or not 0 <= max_length <= 8:
            raise ValueError("invalid maximum primitive length")
        self.max_length = max_length
        self.scope = {
            "version": VERSION, "grammar": list(M.PRIMITIVES),
            "checker": M.CHECKER, "max_length": max_length,
            "engine_source_sha256": _source_hash(__file__),
            "checker_source_sha256": _source_hash(M.__file__),
            "schedule": "semantic-bfs-primitive-order.v1",
            "budget_unit": "new-semantic-transition",
        }
        self.engine_identity = hashlib.sha256(_canonical(self.scope)).hexdigest()
        self.work = dict.fromkeys(COUNTERS, 0)
        self._initialize_state()

    def _initialize_state(self):
        identity = (Fraction(0), Fraction(1))
        self.nodes = [(identity, ())]
        self._index = {identity: 0}
        self._node_cursor = self._op_cursor = self._state_transitions = 0
        self.work["index_writes"] += 1
        self._normalize_cursor()

    def reset(self):
        """Discard reusable derived state; acquisition costs stay in the ledger."""
        self.work["resets"] += 1
        self._initialize_state()

    def _normalize_cursor(self):
        while (self._node_cursor < len(self.nodes) and
               len(self.nodes[self._node_cursor][1]) >= self.max_length):
            self._node_cursor += 1
            self._op_cursor = 0

    @property
    def exhausted(self):
        return self._node_cursor >= len(self.nodes)

    def _lookup(self, coefficients):
        self.work["index_probes"] += 1
        self.work["index_key_coefficients"] += len(coefficients)
        return self._index.get(coefficients)

    def _expand_one(self):
        if self.exhausted:
            return False
        coefficients, program = self.nodes[self._node_cursor]
        op = M.PRIMITIVES[self._op_cursor]
        new = list(coefficients)
        if op in ("inc", "dec"):
            new[0] += 1 if op == "inc" else -1
            self.work["arithmetic_additions"] += 1
        elif op == "double":
            new = [2 * c for c in coefficients]
            self.work["arithmetic_multiplications"] += len(coefficients)
        else:
            new = [Fraction(0)] * (2 * len(coefficients) - 1)
            for i, a in enumerate(coefficients):
                for j, b in enumerate(coefficients):
                    new[i + j] += a * b
            self.work["arithmetic_additions"] += len(coefficients) ** 2
            self.work["arithmetic_multiplications"] += len(coefficients) ** 2
        new = tuple(new)
        self.work["transitions"] += 1
        self._state_transitions += 1
        if self._lookup(new) is None:
            self._index[new] = len(self.nodes)
            self.nodes.append((new, program + (op,)))
            self.work["index_writes"] += 1
        self._op_cursor += 1
        if self._op_cursor == len(M.PRIMITIVES):
            self._node_cursor += 1
            self._op_cursor = 0
        self._normalize_cursor()
        return True

    def query(self, task, expansion_budget):
        """Return exact checked success, bounded timeout, or completed-grammar miss."""
        if not isinstance(task, M.PolynomialTask):
            raise ValueError("query requires a registered PolynomialTask")
        if type(expansion_budget) is not int or not 0 <= expansion_budget <= 200_000:
            raise ValueError("invalid new-transition budget")
        before = dict(self.work)
        found = self._lookup(task.coefficients)
        while found is None and self.work["transitions"] - before["transitions"] < expansion_budget:
            if not self._expand_one():
                break
            found = self._lookup(task.coefficients)
        program = None
        verified = False
        if found is not None:
            program = self.nodes[found][1]
            # SearchResult is used only as the established verifier's input.
            # Its internal slots value is never presented as incumbent search cost.
            certificate = M.SearchResult(
                task.fingerprint, self.engine_identity, "VERIFIED_POLYNOMIAL_IDENTITY",
                program, 0, 0, (), self.max_length,
            )
            additions, multiplications = _normal_form_cost(program)
            self.work["arithmetic_additions"] += additions
            self.work["arithmetic_multiplications"] += multiplications
            self.work["answer_checks"] += 1
            self.work["answer_program_length"] += len(program)
            verified = M.verify_solution(task, certificate)
            if not verified:
                raise ValueError("semantic index returned an invalid answer certificate")
            status = "VERIFIED_POLYNOMIAL_IDENTITY"
        else:
            status = "EXHAUSTED_DECLARED_GRAMMAR" if self.exhausted else "BUDGET_EXHAUSTED"
        return {
            "status": status, "program": list(program) if program is not None else None,
            "verified": verified, "task_fingerprint": task.fingerprint,
            "engine_identity": self.engine_identity,
            "budget_unit": "new-semantic-transition", "expansion_budget": expansion_budget,
            "max_length": self.max_length,
            "query_work": {k: self.work[k] - before[k] for k in COUNTERS},
            "lifetime_work": dict(self.work), "indexed_states": len(self.nodes),
            "claim": "exact identity; shortest primitive representative within declared grammar",
        }

    def _state(self):
        return {
            "schema": VERSION, "scope": self.scope,
            "transitions": self._state_transitions,
            "cursor": {"node": self._node_cursor, "op": self._op_cursor},
            "nodes": [{"coefficients": [str(c) for c in coefficients],
                       "program": list(program)} for coefficients, program in self.nodes],
        }

    def checkpoint(self):
        payload = _canonical(self._state())
        self.work["checkpoint_bytes_written"] += len(payload)
        self.work["checkpoints"] += 1
        return payload

    @classmethod
    def restore(cls, payload):
        if type(payload) is not bytes or len(payload) > 64 * 1024 * 1024:
            raise ValueError("snapshot must be bounded canonical bytes")
        try:
            state = json.loads(payload)
            result = cls(state["scope"]["max_length"])
            count = state["transitions"]
        except (ValueError, KeyError, TypeError, UnicodeError) as exc:
            raise ValueError("invalid snapshot structure") from exc
        if (state.get("schema") != VERSION or state.get("scope") != result.scope or
                type(count) is not int or not 0 <= count <= 200_000):
            raise ValueError("snapshot scope or transition count mismatch")
        result.work["checkpoint_bytes_read"] += len(payload)
        result.work["restores"] += 1
        for _ in range(count):
            if not result._expand_one():
                raise ValueError("snapshot claims transitions after grammar exhaustion")
        result.work["restore_transitions"] += count
        if _canonical(result._state()) != payload:
            raise ValueError("snapshot state failed independent deterministic replay")
        return result
