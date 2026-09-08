"""Conventional target-directed inverse synthesis in the fixed polynomial grammar.

Each query starts a fresh backwards BFS. No future targets, answer table or OCM
state is used. Integer-coefficient, positive-leading predecessors suffice because
every forward-reachable polynomial has these properties. Exact square roots are
reconstructed from highest coefficient down and checked by full convolution.

Counters are an explicit arithmetic operation model, not elapsed-time substitutes:
subtractions count as additions; divisions and integer square roots remain separate.
The ordinary answer verifier always runs, including for the identity program.
"""
from __future__ import annotations

from collections import deque
from math import isqrt

from ocm.learning import methods as M


KEYS = ("arithmetic_additions", "arithmetic_multiplications",
        "arithmetic_divisions", "integer_sqrt_calls", "coefficient_visits",
        "index_probes", "index_key_coefficients", "index_writes",
        "transitions", "answer_checks", "answer_program_length", "queries",
        "states_created", "peak_query_states")


class InverseSession:
    """Independent per-query synthesis; lifetime counters survive between calls."""

    def __init__(self, max_length=4):
        M.SearchBudget(slots=0, max_length=max_length)
        self.max_length = max_length
        self.work = dict.fromkeys(KEYS, 0)

    def _count(self, key, amount=1):
        self.work[key] += amount

    def _square_root(self, coefficients):
        degree = len(coefficients) - 1
        if degree % 2:
            return None
        half = degree // 2
        self._count("integer_sqrt_calls")
        leading = isqrt(coefficients[-1])
        self._count("arithmetic_multiplications")
        if leading * leading != coefficients[-1]:
            return None
        root = [0] * (half + 1)
        root[-1] = leading
        self._count("arithmetic_multiplications")
        denominator = 2 * leading
        for k in range(half - 1, -1, -1):
            known = 0
            for i in range(k + 1, half + 1):
                j = half + k - i
                if k < j <= half:
                    self._count("coefficient_visits", 2)
                    self._count("arithmetic_multiplications")
                    self._count("arithmetic_additions")
                    known += root[i] * root[j]
            self._count("coefficient_visits")
            self._count("arithmetic_additions")
            self._count("arithmetic_divisions")
            value, remainder = divmod(coefficients[half + k] - known, denominator)
            if remainder:
                return None
            root[k] = value
        check = [0] * len(coefficients)
        for i, left in enumerate(root):
            for j, right in enumerate(root):
                self._count("coefficient_visits", 2)
                self._count("arithmetic_multiplications")
                self._count("arithmetic_additions")
                check[i + j] += left * right
        self._count("coefficient_visits", len(coefficients))
        return tuple(root) if tuple(check) == coefficients else None

    def _predecessor(self, coefficients, op):
        if op in ("inc", "dec"):
            self._count("coefficient_visits", len(coefficients))
            self._count("arithmetic_additions")
            return (coefficients[0] + (-1 if op == "inc" else 1), *coefficients[1:])
        if op == "double":
            predecessor = []
            for value in coefficients:
                self._count("coefficient_visits")
                self._count("arithmetic_divisions")
                quotient, remainder = divmod(value, 2)
                if remainder:
                    return None
                predecessor.append(quotient)
            return tuple(predecessor)
        return self._square_root(coefficients)

    def _verify(self, task, program):
        # Count exactly the coefficient arithmetic performed by M.normal_form
        # inside M.verify_solution; this accounting performs no second synthesis.
        length = 2
        for op in program:
            if op in ("inc", "dec"):
                self._count("arithmetic_additions")
            elif op == "double":
                self._count("arithmetic_multiplications", length)
            else:
                self._count("arithmetic_additions", length * length)
                self._count("arithmetic_multiplications", length * length)
                length = 2 * length - 1
        self._count("answer_checks")
        self._count("answer_program_length", len(program))
        result = M.SearchResult(task.fingerprint, "inverse-bfs.v1",
                                "VERIFIED_POLYNOMIAL_IDENTITY", program,
                                0, 0, (), self.max_length)
        if not M.verify_solution(task, result):
            raise AssertionError("inverse witness failed independent forward check")

    def query(self, task, transition_budget=200_000):
        if type(transition_budget) is not int or transition_budget < 0:
            raise ValueError("transition budget must be a nonnegative integer")
        if not isinstance(task, M.PolynomialTask):
            raise TypeError("expected PolynomialTask")
        before = dict(self.work)
        self._count("queries")
        query_peak = 0

        def finish(status, program=None):
            if program is not None:
                self._verify(task, program)
            query_work = {key: self.work[key] - before[key] for key in KEYS}
            query_work["peak_query_states"] = query_peak
            return {"status": status, "program": list(program) if program is not None else None,
                    "verified": program is not None,
                    "query_work": query_work, "lifetime_work": dict(self.work),
                    "engine_identity": "inverse-bfs.v1"}

        coefficients = task.coefficients
        self._count("coefficient_visits", len(coefficients))
        if (len(coefficients) < 2 or coefficients[-1] <= 0 or
                any(value.denominator != 1 for value in coefficients)):
            return finish("EXHAUSTED_DECLARED_GRAMMAR")
        start = tuple(int(value) for value in coefficients)
        queue = deque([(start, ())])
        seen = {start}
        self._count("index_writes")
        self._count("index_key_coefficients", len(start))
        self._count("states_created")
        query_peak = 1
        self.work["peak_query_states"] = max(self.work["peak_query_states"], 1)
        identity = (0, 1)
        while queue:
            current, backwards = queue.popleft()
            self._count("index_probes")
            if current == identity:
                return finish("VERIFIED_POLYNOMIAL_IDENTITY", tuple(reversed(backwards)))
            if len(backwards) == self.max_length:
                continue
            for op in M.PRIMITIVES:
                if self.work["transitions"] - before["transitions"] >= transition_budget:
                    return finish("BUDGET_EXHAUSTED")
                self._count("transitions")
                predecessor = self._predecessor(current, op)
                if predecessor is None:
                    continue
                self._count("index_probes")
                self._count("index_key_coefficients", len(predecessor))
                if predecessor not in seen:
                    seen.add(predecessor)
                    self._count("index_writes")
                    self._count("index_key_coefficients", len(predecessor))
                    self._count("states_created")
                    query_peak = max(query_peak, len(seen))
                    self.work["peak_query_states"] = max(self.work["peak_query_states"], len(seen))
                    path = (*backwards, op)
                    # Return a discovered goal immediately, without spending
                    # irrelevant sibling expansions past the query budget.
                    if predecessor == identity:
                        return finish("VERIFIED_POLYNOMIAL_IDENTITY", tuple(reversed(path)))
                    queue.append((predecessor, path))
        return finish("EXHAUSTED_DECLARED_GRAMMAR")

    solve = query


InverseSearchSession = InverseSession
