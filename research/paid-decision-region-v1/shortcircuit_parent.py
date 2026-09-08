"""R0D exact parent: charge the comparisons the unanimity predicate executes.

DEV-6 intentionally repriced naive unanimity by ``len(survivors)``.  That is a
valid conservative full-scan tariff, but the predicate implementation itself is
short-circuiting: once a disagreeing survivor is encountered, the decision is
already UNDECIDED and the rest of the version space need not be inspected.

This file preserves donor fidelity the same way X1 did: retrieve the exact
``dev6_arms._run`` source with ``inspect``, require one exact source fragment,
replace only that fragment, compile in DEV-6's module namespace, and leave every
other state transition/counter untouched.

No learned predictor, cache, vote book or maintenance state is introduced.
"""
from __future__ import annotations

import hashlib
import inspect

import dev6_arms as D


DONOR_BLOB_SHA = "7952b99500cd664ada6ff9c191b56e2a064336d5"

OLD = '''        if mode == "unanimity_naive":
            charge(max(1, len(survivors)))
            if not survivors:
                return None
            first = survivors[0].excludes(index)
            return first if all(p.excludes(index) == first for p in survivors[1:]) else None
'''

NEW = '''        if mode == "unanimity_naive":
            if not survivors:
                charge(1)
                return None
            first = survivors[0].excludes(index)
            examined = 1
            for pred in survivors[1:]:
                examined += 1
                if pred.excludes(index) != first:
                    charge(examined)
                    return None
            charge(examined)
            return first
'''


def donor_source() -> str:
    return inspect.getsource(D._run)


def transformed_source() -> str:
    source = donor_source()
    if source.count(OLD) != 1:
        raise RuntimeError(
            "DEV-6 donor source drifted: expected exactly one full-scan unanimity fragment"
        )
    return source.replace(OLD, NEW, 1)


def source_fidelity() -> dict:
    source = donor_source()
    transformed = transformed_source()
    return {
        "donor_function": "research/developmental-spine/dev6_arms.py::_run",
        "donor_blob_sha": DONOR_BLOB_SHA,
        "original_source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "transformed_source_sha256": hashlib.sha256(transformed.encode()).hexdigest(),
        "old_fragment_occurrences": source.count(OLD),
        "new_fragment_occurrences": transformed.count(NEW),
        "substitution_only": transformed == source.replace(OLD, NEW, 1),
    }


def _compile_shortcircuit_run():
    namespace = dict(D.__dict__)
    exec(compile(transformed_source(), "<r0d-shortcircuit-dev6-_run>", "exec"), namespace)
    return namespace["_run"]


_SHORT_RUN = _compile_shortcircuit_run()


def run_shortcircuit(world, d0, d1, budget):
    """Run DEV-6's naive-unanimity arm with exact short-circuit comparison cost."""
    return _SHORT_RUN(world, d0, d1, budget, "unanimity_naive")


def phase_semantics(phase) -> dict:
    """Everything except lookup work, the one resource coordinate changed here."""
    return {
        key: value
        for key, value in vars(phase).items()
        if key != "lookup_work"
    }
