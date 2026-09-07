"""Conventional cached exact region-bitset parent; no learned methods."""
from unary_contract import (COUNTERS, InputRefused, RESULT_SCHEMA, negate,
                            predicate_registry, task_digest, validate_task)


class RegionSolver:
    """Cache expression masks for one fixed vocabulary; no cached premise truth."""
    def __init__(self, predicates):
        self.predicates = predicate_registry(predicates)
        self.regions = 1 << len(self.predicates)
        self.full = (1 << self.regions) - 1
        self.cache = {}
        self.counters = {}

    def _mask(self, expr):
        self.counters["expression_nodes"] += 1
        key = self._key(expr)
        if key in self.cache:
            self.counters["cache_hits"] += 1
            return self.cache[key]
        self.counters["cache_misses"] += 1
        if expr[0] == "pred":
            bit = self.predicates.index(expr[1])
            self.counters["predicate_region_tests"] += self.regions
            mask = sum(1 << region for region in range(self.regions) if region & (1 << bit))
        elif expr[0] == "not":
            mask = self.full ^ self._mask(expr[1])
            self.counters["mask_operations"] += 1
        else:
            a, b = self._mask(expr[1]), self._mask(expr[2])
            mask = a & b if expr[0] == "and" else a | b
            self.counters["mask_operations"] += 1
        self.cache[key] = mask
        return mask

    @staticmethod
    def _key(expr):
        return tuple(expr) if expr[0] == "pred" else (expr[0], *(RegionSolver._key(x) for x in expr[1:]))

    def _constraint(self, statement):
        a, b = self._mask(statement["left"]), self._mask(statement["right"])
        if statement["kind"] in ("every", "not_every"):
            b = self.full ^ b
            self.counters["mask_operations"] += 1
        self.counters["mask_operations"] += 1
        return statement["kind"] in ("every", "no"), a & b

    def _sat(self, constraints):
        self.counters["satisfiability_checks"] += 1
        allowed, universals, existentials = self.full, [], []
        for index, (universal, mask) in enumerate(constraints):
            self.counters["constraints_checked"] += 1
            if universal:
                universals.append(index)
                allowed &= self.full ^ mask
                self.counters["mask_operations"] += 2
            else:
                existentials.append((index, mask))
        if not allowed:
            return {"kind": "unsat", "obligation": "domain", "cover": universals}
        world = set()
        for index, mask in existentials:
            available = allowed & mask
            self.counters["mask_operations"] += 1
            if not available:
                return {"kind": "unsat", "obligation": index, "cover": universals}
            world.add((available & -available).bit_length() - 1)
            self.counters["witness_selections"] += 1
        if not world:
            world.add((allowed & -allowed).bit_length() - 1)
            self.counters["witness_selections"] += 1
        return {"kind": "model", "world": sorted(world)}

    def solve(self, value):
        self.counters = dict.fromkeys(COUNTERS, 0)
        try:
            task = validate_task(value)
            if task["predicates"] != self.predicates:
                raise InputRefused("CACHE_VOCABULARY_MISMATCH")
        except InputRefused as exc:
            return {"schema": RESULT_SCHEMA, "status": "INPUT_REFUSED", "reason": str(exc)}
        constraints = [self._constraint(s) for s in task["premises"]]
        base = self._sat(constraints)
        yes = no = None
        if base["kind"] == "unsat":
            status = "INCONSISTENT"
        else:
            yes = self._sat(constraints + [self._constraint(task["query"])])
            no = self._sat(constraints + [self._constraint(negate(task["query"]))])
            if yes["kind"] == "unsat":
                status = "CONTRADICTED"
            elif no["kind"] == "unsat":
                status = "ENTAILED"
            else:
                status = "UNKNOWN"
        return {"schema": RESULT_SCHEMA, "task_sha256": task_digest(task), "status": status,
                "premises": base, "query_true": yes, "query_false": no,
                "counters": dict(self.counters)}


def solve(value):
    try:
        task = validate_task(value)
    except InputRefused as exc:
        return {"schema": RESULT_SCHEMA, "status": "INPUT_REFUSED", "reason": str(exc)}
    return RegionSolver(task["predicates"]).solve(task)
