"""Order-preserving macro enumeration with prefix pruning and shared semantics.

This is an engineering successor of #192's physical index builder. Historical
valid-word enumeration counts are preserved, not retrospectively discounted.
A pool may be shared by candidate builders only under one fixed normal_form
callable and primitive grammar. Its initialization/retained memory are not free.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterator

PRIMITIVES = ("inc", "dec", "double", "square")
MACRO = "MACRO"


@dataclass
class SemanticPool:
    normal_form: Callable[[tuple[str, ...]], tuple]
    values: dict[tuple[str, ...], tuple] = field(default_factory=dict, init=False)
    requests: int = field(default=0, init=False)
    misses: int = field(default=0, init=False)
    hits: int = field(default=0, init=False)

    def evaluate(self, program: tuple[str, ...]) -> tuple:
        self.requests += 1
        if program not in self.values:
            # Exceptions do not become cache entries; the exact verifier remains
            # the supplied original function, not an approximate point signature.
            value = self.normal_form(program)
            self.values[program] = value
            self.misses += 1
        else:
            self.hits += 1
        return self.values[program]


def words(macro: tuple[str, ...] | None, bound: int, metrics: dict) -> Iterator[tuple[tuple, tuple, bool]]:
    if type(bound) is not int or bound < 0:
        raise ValueError("nonnegative primitive-length bound required")
    if macro is not None and (type(macro) is not tuple or not macro or any(t not in PRIMITIVES for t in macro)):
        raise ValueError("nonempty primitive macro required")
    tokens = ((MACRO,) + PRIMITIVES) if macro is not None else PRIMITIVES
    expansions = {p: (p,) for p in PRIMITIVES}
    if macro is not None:
        expansions[MACRO] = macro
    def visit(remaining, token_word, expanded, used):
        metrics["prefix_visits"] = metrics.get("prefix_visits", 0) + 1
        if not remaining:
            metrics["valid_words"] = metrics.get("valid_words", 0) + 1
            yield token_word, expanded, used
            return
        for token in tokens:
            extension = expansions[token]
            # Every remaining token expands to at least one primitive. No valid
            # complete word occurs beneath a prefix violating this lower bound.
            if len(expanded) + len(extension) + remaining - 1 > bound:
                metrics["pruned_prefixes"] = metrics.get("pruned_prefixes", 0) + 1
                continue
            yield from visit(remaining - 1, token_word + (token,), expanded + extension, used or token == MACRO)
    for depth in range(bound + 1):
        yield from visit(depth, (), (), False)


def build_search_index(macro, max_primitive_length: int, pool: SemanticPool, metrics: dict | None = None):
    macro = tuple(macro) if macro is not None else None
    metrics = {} if metrics is None else metrics
    seen_programs = set()
    first_by_coefficients = {}
    attempts = checks = 0
    for token_word, expanded, used in words(macro, max_primitive_length, metrics):
        attempts += 1
        if expanded in seen_programs:
            continue
        seen_programs.add(expanded)
        checks += 1
        coefficients = pool.evaluate(expanded)
        first_by_coefficients.setdefault(coefficients, {
            "enumeration_attempts": attempts, "unique_candidates_checked": checks,
            "token_word": token_word, "program": expanded, "macro_used": used,
        })
    return {"macro": macro, "max_primitive_length": max_primitive_length,
            "total_enumeration_attempts": attempts, "total_unique_candidates_checked": checks,
            "first_by_coefficients": first_by_coefficients}
