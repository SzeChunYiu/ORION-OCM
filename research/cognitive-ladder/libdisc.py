"""E5: library discovery at the right level of abstraction, and the demand for it.

This module is experiment ``E5`` of the cognitive-ladder programme.  It exists to
separate two negatives that the programme has already produced and that are
easily confused with one another.

**Negative 1 -- discovery (`NO_METHOD_ACQUIRED`).**
``research/math-language-learning-v1/ASSAY-ACQUISITION-DIAGNOSIS.md``: a method
learner mined 21 candidates from four episodes; an independent checker accepted
three as essential and sound; all three were singletons; the registered
repeated-support gate emptied the pool.  The stated cause is abstraction at the
wrong level -- "their flat queried fragments differ, but their intermediate
dependency step recurs".

**Negative 2 -- opportunity (`NO_DEVELOPMENT_BENEFIT`).**
``research/math-language-learning-v1/CLAUSE-REVIVAL-RESULT.md``: PR #147's clause
donor implemented step-level abstraction and it *worked* -- the pool went from 0
to 1.  The acquired method then fired zero times: sixteen development trials all
``NO_MATCH``, 4,425 matching-work units.  Only four rows were eligible and every
one of those targets was a Boolean tautology.  "Thus there is no essential
composite target opportunity among these 16 tasks."

Those are different failures.  A programme that reports one number cannot tell
them apart, and ``ROOT_CAUSE_ANALYSIS_V1.md`` records them as two distinct roots
(``PROBE_ABSTRACTION_LEVEL_IS_AUTHORED_NOT_ADAPTED`` for N6,
``STRUCTURE_ACQUIRED_IS_NOT_SUBSEQUENTLY_DEMANDED`` for N7).  This experiment
runs the *same* discovered object against two fresh-task sets that differ only
in whether the opportunity exists.  Without the tautological control a positive
result means nothing.

The domain
----------

Propositional signed clauses over at most eight predicates, so 256 assignments
and everything is decidable by enumeration.

    every(A, B)  is  (not A or B)
    no(A, B)     is  (not A or not B)

A *task* is ``(premises, query)`` and the answer is whether the premises entail
the query.  :func:`entails` is the exact independent checker: it enumerates all
256 assignments, takes only clauses, and never consults a learned object, a
store or a method.  That is CL-D1(c), and ``test_libdisc.py`` asserts it by
source inspection.

An *episode* is a solved task plus its proof, a sequence of resolution steps
``(clause_i, clause_j, pivot) -> resolvent``.  A *step schema* is such a step
with predicates replaced by variables under signed-clause normalisation and
premise sorting.  A *composite* schema collapses two resolution steps into one
macro application, and only a composite can reduce search: a one-step macro
produces exactly what plain resolution produces at exactly the same depth, so
this module never applies one and says so in the receipt.

What lives here and what does not
---------------------------------

``libdisc.py`` is the world and the meters: clauses, the independent checker,
resolution, the schema representation, the search that may or may not hold a
library, exact minimal-derivation-length computation, and the generator with its
four certifications.  It contains no learning.  It does not import
``libdisc_discovery``; the dependency runs the other way, which is what makes
the independence test cheap to state.

Discipline
----------

* The repeated-support threshold is 2 and is never lowered.  The diagnosis
  forbids it explicitly: ">=2 requirement is this learner's registered
  discovery/admission criterion ... Keep >=2 unchanged in the first revival to
  isolate representation."
* Semantic-equivalence *weakening* to accept redundant matches is not
  implemented.  ``CLAUSE-REVIVAL-RESULT.md`` considered exactly that and refused
  it: "Counting them as learned benefit would be misleading."  Redundant-but-
  sound matches are counted in their own column and never in the benefit column.
* No wall-clock enters any result.  Work is counted in exact units.
* Stdlib only, Python 3.11+, frozen dataclasses for records.

Limitations, stated before any number
-------------------------------------

* Eight predicates and 256 assignments.  ``PROTOTYPE_SCALE_TOO_SMALL_FOR_CLAIM``
  remains the appropriate terminal for any attempt to read a field claim here.
* The two fresh-task sets are *authored to differ in exactly one property*, which
  is the design, and it means the contrast identifies the demand term and
  nothing else.  It does not establish that natural task ecologies contain
  essential composite opportunities at any rate at all.
* Resolution with subsumption is complete for non-tautological clause
  entailment, which is why minimal derivation length is well defined here; it is
  not a general-purpose prover and nothing about proof search in a richer logic
  follows.

Parents: resolution (Robinson); anti-unification / least general generalisation
(Plotkin, Reynolds); macro-operator learning (Fikes-Hart-Nilsson STRIPS MACROPS,
Korf); explanation-based generalisation (Mitchell-Keller-Kedar-Cabelli, DeJong);
minimum description length (Rissanen); library learning (DreamCoder, Stitch).
No novelty is claimed for any of them.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Iterable, Sequence

__all__ = [
    "N_PREDS",
    "N_ASSIGNMENTS",
    "Clause",
    "Lit",
    "clause",
    "is_tautology",
    "subsumes",
    "satisfies",
    "entails",
    "pivots",
    "resolve",
    "SearchWork",
    "Pattern",
    "Schema",
    "Step",
    "Episode",
    "Task",
    "SolveResult",
    "solve",
    "min_derivation_length",
    "match_schema",
    "instantiate",
    "canonical_form",
    "flat_fragment",
    "GROUND_STEP_SPACE",
    "SINGLE_SCHEMA_SPACE",
    "COMPOSITE_SCHEMA_SPACE",
    "digest_of",
    "TRAINING_EPISODES",
    "ESSENTIAL_COMPOSITE_TASKS",
    "TAUTOLOGICAL_CONTROL_TASKS",
    "Certification",
    "certify_draw",
    "LIBDISC_PLAN",
    "COMMITMENT",
]

#: Eight predicates, so 256 assignments and every semantic question is decided by
#: enumeration rather than by a solver whose completeness would then need its own
#: argument.
N_PREDS = 8
N_ASSIGNMENTS = 1 << N_PREDS

#: Widest clause the world ever contains.  Three, because a weakened query -- the
#: shape that made two of the diagnosis's flat fragments differ -- needs it.
MAX_CLAUSE_WIDTH = 3

#: Deepest derivation any arm may search.  Identical for every arm, including the
#: parents; a budget that differed between arms would make the comparison
#: inadmissible under CL protocol section 7.
MAX_SEARCH_DEPTH = 4

#: Registered repeated-support threshold.  NOT a tunable.  See module docstring.
REPEATED_SUPPORT_THRESHOLD = 2

Lit = tuple[int, bool]
Clause = tuple[Lit, ...]


# --------------------------------------------------------------------------
# clauses
# --------------------------------------------------------------------------


def clause(*lits: Lit) -> Clause:
    """Signed-clause normalisation: sorted, deduplicated, canonical."""
    out = sorted(set(lits))
    for p, s in out:
        if not 0 <= p < N_PREDS:
            raise ValueError(f"predicate {p} out of range")
    if len(out) > MAX_CLAUSE_WIDTH:
        raise ValueError(f"clause wider than {MAX_CLAUSE_WIDTH}: {out}")
    return tuple(out)


def every(a: int, b: int) -> Clause:
    """``every(A, B)`` is the clause ``(not A or B)``."""
    return clause((a, False), (b, True))


def no(a: int, b: int) -> Clause:
    """``no(A, B)`` is the clause ``(not A or not B)``."""
    return clause((a, False), (b, False))


def is_tautology(c: Clause) -> bool:
    """A clause containing a predicate at both polarities is true everywhere."""
    return any((p, not s) in c for p, s in c)


def subsumes(c: Clause, d: Clause) -> bool:
    """``c`` subsumes ``d`` iff every literal of ``c`` occurs in ``d``.

    A subsuming clause entails the subsumed one, which is why the search may
    stop as soon as it derives one.
    """
    return set(c) <= set(d)


def satisfies(c: Clause, assignment: int) -> bool:
    """Is clause ``c`` true under the bitmask ``assignment``?"""
    for p, s in c:
        if bool(assignment >> p & 1) == s:
            return True
    return False


def entails(premises: Sequence[Clause], query: Clause) -> bool:
    """Exact independent checker (CL-D1(c)).

    Enumerates all ``2 ** N_PREDS`` assignments and returns True iff every model
    of ``premises`` is a model of ``query``.

    This function takes clauses and nothing else.  It reads no store, no
    library, no method, no schema and no learned state, it has no default
    arguments carrying such state, and it calls nothing that does.  That
    property is asserted by source inspection in ``test_libdisc.py`` and is the
    reason a certificate emitted here is admissible evidence about an object the
    machine proposed.
    """
    for assignment in range(N_ASSIGNMENTS):
        ok = True
        for c in premises:
            if not satisfies(c, assignment):
                ok = False
                break
        if ok and not satisfies(query, assignment):
            return False
    return True


def pivots(c1: Clause, c2: Clause) -> tuple[int, ...]:
    """Predicates on which ``c1`` and ``c2`` carry opposite polarity."""
    out = []
    for p, s in c1:
        if (p, not s) in c2:
            out.append(p)
    return tuple(sorted(set(out)))


def resolve(c1: Clause, c2: Clause, pivot: int) -> Clause | None:
    """The resolvent of ``c1`` and ``c2`` on ``pivot``; ``None`` if tautological.

    Tautological resolvents are dropped rather than stored: they entail nothing
    a non-tautological query needs, and keeping them inflates the clause set that
    every arm's work is counted over.
    """
    lits = (set(c1) | set(c2)) - {(pivot, True), (pivot, False)}
    if any((p, not s) in lits for p, s in lits):
        return None
    out = tuple(sorted(lits))
    if len(out) > MAX_CLAUSE_WIDTH:
        return None
    return out


# --------------------------------------------------------------------------
# work
# --------------------------------------------------------------------------


@dataclass
class SearchWork:
    """Exact work counter.  No wall-clock coordinate exists here on purpose.

    ``macro_match_attempts`` is charged whether or not the macro fires.  The
    clause-revival negative reported 4,425 matching-work units against zero
    uses; an experiment that charged matching only on success could not have
    reproduced that number and would have hidden the cost of holding a library
    that no task demands.
    """

    resolution_attempts: int = 0
    macro_match_attempts: int = 0
    subsumption_checks: int = 0
    checker_assignments: int = 0
    clauses_derived: int = 0

    def add(self, other: "SearchWork") -> None:
        self.resolution_attempts += other.resolution_attempts
        self.macro_match_attempts += other.macro_match_attempts
        self.subsumption_checks += other.subsumption_checks
        self.checker_assignments += other.checker_assignments
        self.clauses_derived += other.clauses_derived

    @property
    def total(self) -> int:
        """Single scalar used for budgets and for the benefit column."""
        return (
            self.resolution_attempts
            + self.macro_match_attempts
            + self.subsumption_checks
        )

    def as_dict(self) -> dict:
        return {
            "resolution_attempts": self.resolution_attempts,
            "macro_match_attempts": self.macro_match_attempts,
            "subsumption_checks": self.subsumption_checks,
            "checker_assignments": self.checker_assignments,
            "clauses_derived": self.clauses_derived,
            "total": self.total,
        }


# --------------------------------------------------------------------------
# schemas: the representation, not the learning
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Pattern:
    """A clause with predicate variables in place of predicates."""

    lits: tuple[tuple[str, bool], ...]

    def __post_init__(self) -> None:
        if tuple(sorted(set(self.lits))) != self.lits:
            raise ValueError("pattern literals must be sorted and distinct")

    @property
    def variables(self) -> tuple[str, ...]:
        return tuple(sorted({v for v, _ in self.lits}))

    def as_list(self) -> list:
        return [[v, s] for v, s in self.lits]


def _pattern(*lits: tuple[str, bool]) -> Pattern:
    return Pattern(tuple(sorted(set(lits))))


@dataclass(frozen=True)
class Schema:
    """A lifted derivation: premise patterns, pivots, conclusion pattern.

    ``step_count`` is how many resolution steps the schema collapses.  A schema
    with ``step_count == 1`` is never applied during search (plain resolution
    already produces its conclusion at the same depth for the same cost); it is
    still discovered, still admitted or rejected on its merits, and reported in
    its own column.
    """

    premises: tuple[Pattern, ...]
    conclusion: Pattern
    pivot_vars: tuple[str, ...]
    step_count: int
    origin: str  # "single" | "composed"

    @property
    def variables(self) -> tuple[str, ...]:
        seen: set[str] = set()
        for p in self.premises:
            seen |= set(p.variables)
        seen |= set(self.conclusion.variables)
        return tuple(sorted(seen))

    @property
    def arity(self) -> int:
        return len(self.variables)

    @property
    def body(self) -> dict:
        return {
            "premises": [p.as_list() for p in self.premises],
            "conclusion": self.conclusion.as_list(),
            "pivot_vars": list(self.pivot_vars),
            "step_count": self.step_count,
            "origin": self.origin,
        }

    @property
    def schema_id(self) -> str:
        return digest_of(self.body)

    def as_dict(self) -> dict:
        d = dict(self.body)
        d["schema_id"] = self.schema_id
        d["arity"] = self.arity
        return d


@dataclass(frozen=True)
class Step:
    """One ground resolution step of a proof."""

    left: Clause
    right: Clause
    pivot: int
    conclusion: Clause

    def as_dict(self) -> dict:
        return {
            "left": [list(l) for l in self.left],
            "right": [list(l) for l in self.right],
            "pivot": self.pivot,
            "conclusion": [list(l) for l in self.conclusion],
        }


@dataclass(frozen=True)
class Task:
    """A premise set, a query, and a registered role."""

    task_id: str
    premises: tuple[Clause, ...]
    query: Clause
    role: str

    def as_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "premises": [[list(l) for l in c] for c in self.premises],
            "query": [list(l) for l in self.query],
            "role": self.role,
        }


@dataclass(frozen=True)
class Episode:
    """A solved task plus its proof.  CL-R1 in miniature."""

    episode_id: str
    premises: tuple[Clause, ...]
    query: Clause
    proof: tuple[Step, ...]

    def as_dict(self) -> dict:
        return {
            "episode_id": self.episode_id,
            "premises": [[list(l) for l in c] for c in self.premises],
            "query": [list(l) for l in self.query],
            "proof": [s.as_dict() for s in self.proof],
        }


def digest_of(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


# --------------------------------------------------------------------------
# matching and instantiation
# --------------------------------------------------------------------------


def _match_pattern(
    pattern: Pattern, target: Clause, binding: dict[str, int]
) -> list[dict[str, int]]:
    """Every extension of ``binding`` under which ``pattern`` becomes ``target``.

    Variables bind injectively: two distinct variables never denote the same
    predicate.  That is what keeps ``(not X or Y), (not Y or Z) -> (not X or Z)``
    from silently covering the degenerate case ``X == Z``, whose conclusion is a
    tautology and therefore not a derivation of anything.
    """
    if len(pattern.lits) != len(target):
        return []
    out: list[dict[str, int]] = []
    for perm in itertools.permutations(target):
        b = dict(binding)
        ok = True
        for (v, s), (p, s2) in zip(pattern.lits, perm):
            if s != s2:
                ok = False
                break
            if v in b:
                if b[v] != p:
                    ok = False
                    break
            else:
                if p in b.values():
                    ok = False
                    break
                b[v] = p
        if ok and b not in out:
            out.append(b)
    return out


def match_schema(
    schema: Schema, clauses: Sequence[Clause], work: SearchWork | None = None,
    relevance_index: bool = False,
) -> list[tuple[tuple[Clause, ...], dict[str, int]]]:
    """Every way ``schema``'s premises match distinct clauses from ``clauses``.

    Match attempts are charged to ``work`` whether or not they succeed; the
    clause-revival negative is 4,425 matching-work units against zero uses, and
    an experiment that charged only successful matches could not reproduce it.

    ``relevance_index`` is the duplicate relevance cache: a precomputed shape
    filter that lets a holder skip clauses that cannot match without paying a
    trial for them.  It changes cost and never changes the match set, which is
    exactly what makes ``symbolic_compact_parent`` -- the same learner without
    the cache -- the sharpest comparison in this lane.
    """
    results: list[tuple[tuple[Clause, ...], dict[str, int]]] = []
    n = len(schema.premises)

    def rec(k: int, binding: dict[str, int], chosen: list[Clause]) -> None:
        if k == n:
            results.append((tuple(chosen), dict(binding)))
            return
        pat = schema.premises[k]
        shape = sorted(s for _, s in pat.lits)
        for c in clauses:
            if c in chosen:
                continue
            if relevance_index and (
                len(c) != len(pat.lits) or sorted(s for _, s in c) != shape):
                continue  # the index rules this clause out without a trial
            if work is not None:
                work.macro_match_attempts += 1
            if len(c) != len(pat.lits):
                continue
            for b in _match_pattern(pat, c, binding):
                rec(k + 1, b, chosen + [c])

    rec(0, {}, [])
    return results


def instantiate(pattern: Pattern, binding: dict[str, int]) -> Clause | None:
    """Ground ``pattern`` under ``binding``; ``None`` if unbound or tautological."""
    lits: list[Lit] = []
    for v, s in pattern.lits:
        if v not in binding:
            return None
        lits.append((binding[v], s))
    out = tuple(sorted(set(lits)))
    if any((p, not s) in out for p, s in out):
        return None
    return out


# --------------------------------------------------------------------------
# canonical (alpha-renamed) forms
# --------------------------------------------------------------------------


def canonical_form(clauses: Sequence[Clause]) -> tuple:
    """Alpha-renamed, premise-sorted canonical form of a clause multiset."""
    preds = sorted({p for c in clauses for p, _ in c})
    best: tuple | None = None
    for perm in itertools.permutations(range(len(preds))):
        m = {p: perm[i] for i, p in enumerate(preds)}
        cand = tuple(
            sorted(tuple(sorted((m[p], s) for p, s in c)) for c in clauses)
        )
        if best is None or cand < best:
            best = cand
    return best if best is not None else ()


def flat_fragment(premises: Sequence[Clause], query: Clause) -> tuple:
    """The flat surface fragment of the diagnosis: premise pair plus query.

    "each attempted fragment is the original two statements plus original
    query/negation, alpha-renamed and premise-sorted" -- ASSAY-ACQUISITION-
    DIAGNOSIS.md, causal level 2.  This is deliberately the *wrong* level of
    abstraction; reproducing its emptiness is one of this experiment's jobs.
    """
    preds = sorted({p for c in list(premises) + [query] for p, _ in c})
    best: tuple | None = None
    for perm in itertools.permutations(range(len(preds))):
        m = {p: perm[i] for i, p in enumerate(preds)}
        prem = tuple(sorted(tuple(sorted((m[p], s) for p, s in c)) for c in premises))
        q = tuple(sorted((m[p], s) for p, s in query))
        cand = (prem, q)
        if best is None or cand < best:
            best = cand
    return best if best is not None else ((), ())


# --------------------------------------------------------------------------
# search: the meter every arm is read on
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class SolveResult:
    """Outcome of one search, with the execution-trace witness CL-R3 demands."""

    solved: bool
    depth: int
    trace: tuple[tuple, ...]
    macro_fired: bool
    macro_ids: tuple[str, ...]
    work: SearchWork
    answer_checked: bool

    def as_dict(self) -> dict:
        return {
            "solved": self.solved,
            "depth": self.depth,
            "trace": [list(t) for t in self.trace],
            "macro_fired": self.macro_fired,
            "macro_ids": list(self.macro_ids),
            "answer_checked": self.answer_checked,
            "work": self.work.as_dict(),
        }


def _extract_trace(target: Clause, origin: dict) -> tuple[tuple, ...]:
    """Walk the derivation back from ``target`` to the premises."""
    seen: set[Clause] = set()
    order: list[tuple] = []

    def rec(c: Clause) -> None:
        if c in seen or c not in origin:
            return
        seen.add(c)
        rec_from = origin[c]
        if rec_from[0] == "resolve":
            rec(rec_from[1])
            rec(rec_from[2])
            order.append(("resolve", rec_from[1], rec_from[2], rec_from[3], c))
        else:
            for parent in rec_from[2]:
                rec(parent)
            order.append(("macro", rec_from[1], rec_from[2], c))

    rec(target)
    return tuple(order)


def solve(
    premises: Sequence[Clause],
    query: Clause,
    library: Sequence[Schema] = (),
    max_depth: int = MAX_SEARCH_DEPTH,
    check_answer: bool = True,
    relevance_index: bool = False,
) -> SolveResult:
    """Breadth-first resolution search, optionally holding a macro library.

    A macro whose ``step_count`` is 1 is never applied: plain resolution already
    produces its conclusion in the same round at lower cost, so applying it would
    manufacture matching work and nothing else.  Only composites can move a
    clause to an earlier round, which is the only mechanism by which a library
    can reduce search here.

    Resolution origins take priority over macro origins for an identical
    resolvent, so a macro is credited in the execution trace only when plain
    resolution did not already produce that clause at that depth.  Conservative
    in the direction that matters.
    """
    work = SearchWork()
    macros = tuple(s for s in library if s.step_count >= 2)

    if check_answer:
        work.checker_assignments += N_ASSIGNMENTS
        truth = entails(premises, query)
    else:
        truth = True

    if is_tautology(query):
        return SolveResult(True, 0, (), False, (), work, check_answer)

    current: set[Clause] = set(premises)
    origin: dict[Clause, tuple] = {}
    for c in sorted(current):
        work.subsumption_checks += 1
        if subsumes(c, query):
            return SolveResult(True, 0, (), False, (), work, check_answer)

    for depth in range(1, max_depth + 1):
        ordered = sorted(current)
        new: dict[Clause, tuple] = {}
        for i in range(len(ordered)):
            for j in range(i + 1, len(ordered)):
                # examining a pair costs one unit whether or not it resolves;
                # a prover has to look at it either way, and not charging for
                # the look would understate the baseline's cost in exactly the
                # rounds where the clause set has grown.
                work.resolution_attempts += 1
                for pivot in pivots(ordered[i], ordered[j]):
                    work.resolution_attempts += 1
                    r = resolve(ordered[i], ordered[j], pivot)
                    if r is None or r in current or r in new:
                        continue
                    new[r] = ("resolve", ordered[i], ordered[j], pivot)
        for m in macros:
            for chosen, binding in match_schema(
                    m, ordered, work, relevance_index):
                r = instantiate(m.conclusion, binding)
                if r is None or r in current or r in new:
                    continue
                new[r] = ("macro", m.schema_id, chosen)
        if not new:
            break
        work.clauses_derived += len(new)
        for r, o in new.items():
            origin.setdefault(r, o)
        current |= set(new)
        for r in sorted(new):
            work.subsumption_checks += 1
            if subsumes(r, query):
                trace = _extract_trace(r, origin)
                fired = tuple(t[1] for t in trace if t[0] == "macro")
                return SolveResult(
                    True, depth, trace, bool(fired), fired, work, check_answer
                )

    return SolveResult(False, max_depth, (), False, (), work, check_answer and truth)


def min_derivation_length(
    premises: Sequence[Clause],
    query: Clause,
    library: Sequence[Schema] = (),
    max_depth: int = MAX_SEARCH_DEPTH,
) -> int | None:
    """Fewest derivation steps to a clause subsuming ``query``.

    A macro application counts as one step, a resolution counts as one step.
    ``0`` means the query is a tautology or a premise already subsumes it.
    ``None`` means no derivation within ``max_depth``.

    This is the certification instrument for generator properties 3 and 4: an
    ESSENTIAL-COMPOSITE task is one where removing the library strictly
    *increases* this number, and a BYPASSABLE task is one where it does not move.
    """
    if is_tautology(query):
        return 0
    if any(subsumes(c, query) for c in premises):
        return 0
    macros = tuple(s for s in library if s.step_count >= 2)
    current: set[Clause] = set(premises)
    for depth in range(1, max_depth + 1):
        ordered = sorted(current)
        new: set[Clause] = set()
        for i in range(len(ordered)):
            for j in range(i + 1, len(ordered)):
                for pivot in pivots(ordered[i], ordered[j]):
                    r = resolve(ordered[i], ordered[j], pivot)
                    if r is not None and r not in current:
                        new.add(r)
        for m in macros:
            for _chosen, binding in match_schema(m, ordered, None):
                r = instantiate(m.conclusion, binding)
                if r is not None and r not in current:
                    new.add(r)
        if not new:
            return None
        if any(subsumes(r, query) for r in new):
            return depth
        current |= new
    return None


# --------------------------------------------------------------------------
# exact code sizes: the denominators of CL-D1(a)
# --------------------------------------------------------------------------


def _all_clauses(n_preds: int, max_width: int) -> tuple[Clause, ...]:
    """Every non-tautological clause of width ``1..max_width`` over ``n_preds``."""
    lits = [(p, s) for p in range(n_preds) for s in (False, True)]
    out: list[Clause] = []
    for w in range(1, max_width + 1):
        for combo in itertools.combinations(lits, w):
            if any((p, not s) in combo for p, s in combo):
                continue
            out.append(tuple(sorted(combo)))
    return tuple(out)


def _resolve_raw(c1: Clause, c2: Clause, pivot: int, max_width: int) -> Clause | None:
    lits = (set(c1) | set(c2)) - {(pivot, True), (pivot, False)}
    if any((p, not s) in lits for p, s in lits):
        return None
    out = tuple(sorted(lits))
    return out if 0 < len(out) <= max_width else None


@lru_cache(maxsize=None)
def _step_space(n_preds: int, max_width: int) -> int:
    """Number of well-formed single resolution steps over ``n_preds`` symbols."""
    clauses = _all_clauses(n_preds, max_width)
    total = 0
    for c1 in clauses:
        for c2 in clauses:
            for p in range(n_preds):
                if (p, True) in c1 and (p, False) in c2:
                    if _resolve_raw(c1, c2, p, max_width) is not None:
                        total += 1
    return total


@lru_cache(maxsize=None)
def _composite_space(n_preds: int, max_width: int) -> int:
    """Number of well-formed two-step composites over ``n_preds`` symbols."""
    clauses = _all_clauses(n_preds, max_width)
    total = 0
    for c1 in clauses:
        for c2 in clauses:
            for p in range(n_preds):
                if not ((p, True) in c1 and (p, False) in c2):
                    continue
                mid = _resolve_raw(c1, c2, p, max_width)
                if mid is None:
                    continue
                for c3 in clauses:
                    for q in range(n_preds):
                        if (q, True) in mid and (q, False) in c3:
                            if _resolve_raw(mid, c3, q, max_width) is not None:
                                total += 1
    return total


#: ``bits`` to write down one ground resolution step verbatim, i.e. the cost of
#: the verbatim-listing alternative that CL-T2 must exclude.
GROUND_STEP_SPACE = _step_space(N_PREDS, 2)

#: ``|Lambda|`` for the two registered schema classes.  A schema is coded as one
#: class bit plus a uniform index within its class; the code is fixed with the
#: language and does not depend on which schema turned out to be useful.
SINGLE_SCHEMA_SPACE = _step_space(3, 2)
COMPOSITE_SCHEMA_SPACE = _composite_space(4, 2)


def binding_space(arity: int) -> int:
    """Injective bindings of ``arity`` variables into ``N_PREDS`` predicates."""
    total = 1
    for i in range(arity):
        total *= N_PREDS - i
    return total


def schema_code_bits(schema: Schema) -> float:
    """``bits(M)``: one class bit plus a uniform index inside the class.

    A composite that collapses ``s`` steps is coded as ``s - 1`` composite
    indices, so a longer macro costs strictly more to write down.  The code is
    fixed with the language and does not depend on which schema turned out to be
    useful, which is the property CL-D1(a) needs.
    """
    if schema.step_count >= 2:
        return 1.0 + (schema.step_count - 1) * math.log2(COMPOSITE_SCHEMA_SPACE)
    return 1.0 + math.log2(SINGLE_SCHEMA_SPACE)


def support_data_bits(schema: Schema, n_supports: int) -> float:
    """``bits(D)``: the cost of listing the supporting ground steps verbatim."""
    return n_supports * schema.step_count * math.log2(GROUND_STEP_SPACE)


def support_residual_bits(schema: Schema, n_supports: int) -> float:
    """``bits(D | M)``: given the schema, each support is just its binding."""
    return n_supports * math.log2(binding_space(schema.arity))


# --------------------------------------------------------------------------
# the registered draw
# --------------------------------------------------------------------------


def _step(left: Clause, right: Clause, pivot: int) -> Step:
    concl = resolve(left, right, pivot)
    if concl is None:
        raise ValueError(f"step {left} x {right} on {pivot} is tautological")
    return Step(left, right, pivot, concl)


def _episode(name: str, premises: Sequence[Clause], query: Clause,
             spec: Sequence[tuple[Clause, Clause, int]]) -> Episode:
    """Build and *validate* an episode: real premises, real proof, real answer."""
    prem = tuple(premises)
    available = set(prem)
    steps: list[Step] = []
    for left, right, pivot in spec:
        if left not in available or right not in available:
            raise ValueError(f"{name}: step uses an underived clause")
        s = _step(left, right, pivot)
        steps.append(s)
        available.add(s.conclusion)
    if not steps or not subsumes(steps[-1].conclusion, query):
        raise ValueError(f"{name}: proof does not reach the query")
    if not entails(prem, query):
        raise ValueError(f"{name}: premises do not entail the query")
    if is_tautology(query):
        raise ValueError(f"{name}: training queries must not be tautologies")
    return Episode(name, prem, query, tuple(steps))


C = clause
L = lambda p: (p, True)   # noqa: E731 - positive literal
M = lambda p: (p, False)  # noqa: E731 - negative literal


#: Ten training episodes.  Each proof step is a real resolution, each query is
#: really entailed, and the four generator properties over this draw are
#: certified by :func:`certify_draw` rather than assumed.
#:
#: The chain step ``(not X or Y), (not Y or Z) -> (not X or Z)`` recurs seven
#: times across five episodes; the merge step ``(X or Y), (not Y or Z) ->
#: (X or Z)`` recurs five times across four episodes; the two-chain composite
#: occurs in exactly two episodes.  Every flat surface fragment the diagnosis's
#: miner would accept occurs exactly once, which is what makes the flat pool
#: empty and the step-level pool non-empty on identical evidence.
TRAINING_EPISODES: tuple[Episode, ...] = (
    _episode("E0", [C(M(0), L(1)), C(M(1), L(2)), C(M(2), M(3))], C(M(0), M(3)),
             [(C(M(0), L(1)), C(M(1), L(2)), 1),
              (C(M(0), L(2)), C(M(2), M(3)), 2)]),
    _episode("E1", [C(M(0), L(1)), C(M(1), L(2)), C(M(2), L(3))], C(M(0), L(3)),
             [(C(M(0), L(1)), C(M(1), L(2)), 1),
              (C(M(0), L(2)), C(M(2), L(3)), 2)]),
    _episode("E2", [C(M(1), L(2)), C(M(2), L(3)), C(M(3), L(0)), C(M(5), L(6))],
             C(M(1), L(0)),
             [(C(M(1), L(2)), C(M(2), L(3)), 2),
              (C(M(1), L(3)), C(M(3), L(0)), 3)]),
    _episode("E3", [C(M(0), L(1)), C(M(1), L(2)), C(M(4), L(5)), C(L(6), L(7))],
             C(M(0), L(2)),
             [(C(M(0), L(1)), C(M(1), L(2)), 1)]),
    _episode("E4", [C(M(0), L(1)), C(M(1), L(2)), C(L(5), L(7))],
             C(M(0), L(2), L(7)),
             [(C(M(0), L(1)), C(M(1), L(2)), 1)]),
    _episode("E5", [C(M(0), M(1)), C(L(1), L(2)), C(L(3), L(4))], C(M(0), L(2)),
             [(C(M(0), M(1)), C(L(1), L(2)), 1)]),
    _episode("E6", [C(L(0), L(1)), C(M(1), L(2)), C(M(5), L(6))], C(L(0), L(2)),
             [(C(L(0), L(1)), C(M(1), L(2)), 1)]),
    _episode("E7", [C(L(0), L(1)), C(M(1), L(2)), C(M(2), L(3))], C(L(0), L(3)),
             [(C(L(0), L(1)), C(M(1), L(2)), 1),
              (C(L(0), L(2)), C(M(2), L(3)), 2)]),
    _episode("E8", [C(L(0), L(1)), C(M(1), L(2)), C(M(2), M(4))], C(L(0), M(4)),
             [(C(L(0), L(1)), C(M(1), L(2)), 1),
              (C(L(0), L(2)), C(M(2), M(4)), 2)]),
    _episode("E9", [C(L(2), L(3)), C(M(3), L(4)), C(M(6), L(7))],
             C(L(2), L(4), L(7)),
             [(C(L(2), L(3)), C(M(3), L(4)), 3)]),
)


def _task(name: str, premises: Sequence[Clause], query: Clause, role: str) -> Task:
    prem = tuple(premises)
    if not entails(prem, query):
        raise ValueError(f"{name}: premises do not entail the query")
    return Task(name, prem, query, role)


#: Fresh tasks on which an essential composite opportunity EXISTS: the target is
#: not a tautology and removing the composite schema strictly increases the
#: minimal derivation depth.  Certified, not assumed.
ESSENTIAL_COMPOSITE_TASKS: tuple[Task, ...] = (
    _task("C1", [C(M(0), L(1)), C(M(1), L(2)), C(M(2), L(3)), C(L(6), L(7))],
          C(M(0), L(3)), "essential_composite"),
    _task("C2", [C(M(4), L(5)), C(M(5), L(6)), C(M(6), L(7)), C(L(0), L(1)),
                 C(M(1), L(2))], C(M(4), L(7)), "essential_composite"),
    _task("C3", [C(M(0), L(2)), C(M(2), L(4)), C(M(4), L(6)), C(M(1), L(3)),
                 C(M(5), L(7))], C(M(0), L(6)), "essential_composite"),
    _task("C4", [C(M(1), L(2)), C(M(2), L(3)), C(M(3), L(5)), C(L(0), L(7)),
                 C(M(7), L(4))], C(M(1), L(5)), "essential_composite"),
    _task("C5", [C(M(3), L(4)), C(M(4), L(5)), C(M(5), L(6)), C(M(0), M(1))],
          C(M(3), L(6), L(7)), "essential_composite"),
    _task("C6", [C(M(0), L(1)), C(M(1), L(2)), C(M(2), L(3)), C(M(1), L(7)),
                 C(L(5), L(6))], C(M(0), L(3)), "essential_composite"),
)

#: Fresh tasks the SAME schema matches and on which there is NO opportunity:
#: the target is a Boolean tautology, or the derivation admits a bypass at equal
#: depth.  This is the control that ``CLAUSE-REVIVAL-RESULT.md`` reports as the
#: whole of its development set -- "every target is a Boolean tautology ... there
#: is no essential composite target opportunity" -- and without it a positive
#: result on the set above would mean nothing.
TAUTOLOGICAL_CONTROL_TASKS: tuple[Task, ...] = (
    _task("T1", [C(M(0), L(1)), C(M(1), L(2)), C(M(2), L(3)), C(M(6), L(7))],
          C(L(3), M(3)), "tautological_target"),
    _task("T2", [C(M(4), L(5)), C(M(5), L(6)), C(M(6), L(7))],
          C(L(0), M(0)), "tautological_target"),
    _task("T7", [C(M(1), L(2)), C(M(2), L(3)), C(M(3), L(4)), C(L(0), L(5))],
          C(L(5), M(5)), "tautological_target"),
    _task("T3", [C(M(0), L(1)), C(M(1), L(2)), C(M(2), L(3)), C(M(0), L(3))],
          C(M(0), L(3)), "bypassable_target"),
    _task("T4", [C(M(0), L(1)), C(M(1), L(2)), C(M(2), L(3)), C(M(0), L(2))],
          C(M(0), L(3)), "bypassable_target"),
    _task("T5", [C(M(0), L(1)), C(M(1), L(2)), C(M(2), L(3)), C(M(1), L(3))],
          C(M(0), L(3)), "bypassable_target"),
    _task("T6", [C(M(0), L(1)), C(M(1), L(2)), C(M(2), L(3)), C(M(3), L(4))],
          C(M(0), L(4)), "bypassable_target"),
)

#: Registered controls that are neither of the two headline sets.
CONTROL_TASKS: tuple[Task, ...] = (
    # a singleton step schema (chain-neg, seen once in E0) is refused by the
    # >=2 gate; the task that would have needed it therefore gets nothing.
    _task("S1", [C(M(0), L(1)), C(M(1), L(2)), C(M(2), M(5)), C(L(6), L(7))],
          C(M(0), M(5)), "singleton_no_generalisation"),
    # the merge step recurs five times and is admitted, and its two-step
    # composite has only ONE training support, so the gate refuses it.  This
    # task would have benefited.  The cost of not lowering the threshold is
    # reported here rather than avoided by lowering it.
    _task("FC1", [C(L(0), L(1)), C(M(1), L(2)), C(M(2), L(3)), C(M(6), L(7))],
          C(L(0), L(3)), "false_common_pattern_no_help"),
    # surface-similar to the chain, different pivot polarity: same predicates,
    # a schema a sign-blind miner would merge with the chain and a checker
    # refutes.
    _task("SS1", [C(M(0), M(1)), C(L(1), L(2)), C(M(2), L(3)), C(L(6), L(7))],
          C(M(0), L(3)), "surface_similar_different_polarity"),
)


# --------------------------------------------------------------------------
# leakage discipline: what a learner is allowed to see
# --------------------------------------------------------------------------
#
# Adopted from the frozen protected protocol on branch
# ``codex/ocm-evolvability-independent-20260908``
# (``research/evolvability-independent/PROTECTED_PROTOCOL_V3.md``, card E150-A),
# whose leakage rule is tighter than this lane's default: the learner-visible
# fields of an episode are exactly the input and the correct actions.  Episode
# identity, the registered role/regime of a task, the generator's construction
# and every certification computed about the draw are EVALUATOR-ONLY.
#
# The point is not tidiness.  ``role`` says whether a task is an essential
# composite or a tautological control; a learner that could read it could select
# where to fire and the whole opportunity-versus-discovery contrast would be
# circular.  ``test_libdisc.py`` asserts the field sets and asserts by source
# inspection that no arm touches an evaluator-only attribute.

#: Exactly the fields a learner may read from a training episode.
LEARNER_VISIBLE_EPISODE_FIELDS = ("premises", "query", "proof")

#: Exactly the fields a learner may read from a fresh task.
LEARNER_VISIBLE_TASK_FIELDS = ("premises", "query")

#: Fields that exist on the evaluator-side records and must never reach an arm.
EVALUATOR_ONLY_FIELDS = ("episode_id", "task_id", "role")


@dataclass(frozen=True)
class LearnerView:
    """The input and the correct actions.  Nothing else."""

    premises: tuple[Clause, ...]
    query: Clause
    proof: tuple[Step, ...]


@dataclass(frozen=True)
class TaskView:
    """A fresh task as an arm sees it: premises and query, no identity, no role."""

    premises: tuple[Clause, ...]
    query: Clause


def learner_view(episode: Episode) -> LearnerView:
    return LearnerView(episode.premises, episode.query, episode.proof)


def task_view(task: Task) -> TaskView:
    return TaskView(task.premises, task.query)


def learner_views(episodes: Sequence[Episode] = TRAINING_EPISODES) -> tuple[LearnerView, ...]:
    return tuple(learner_view(e) for e in episodes)


# --------------------------------------------------------------------------
# canonical lifting: normalisation, not learning
# --------------------------------------------------------------------------


def _rename_pattern(pattern: Pattern, mapping: dict) -> Pattern:
    return Pattern(tuple(sorted((mapping[v], s) for v, s in pattern.lits)))


def canonical_schema(schema: Schema) -> Schema:
    """The lexicographically least variable naming of ``schema``.

    Two schemas that differ only by a renaming of predicate variables have the
    same canonical form, so structural identity is decidable by equality here.
    Behavioural identity is a stronger question and is decided separately, by
    exhaustive instantiation, in ``libdisc_discovery.semantic_key``.
    """
    variables = schema.variables
    names = tuple(f"v{i}" for i in range(len(variables)))
    best: Schema | None = None
    best_key: tuple | None = None
    for perm in itertools.permutations(names):
        mapping = {v: perm[i] for i, v in enumerate(variables)}
        prem = tuple(sorted(
            (_rename_pattern(p, mapping) for p in schema.premises),
            key=lambda p: p.lits,
        ))
        concl = _rename_pattern(schema.conclusion, mapping)
        # Pivot variables are a derived annotation, not part of the schema's
        # behaviour, so they are canonicalised as a sorted tuple: two schemas
        # that act identically get the same ``schema_id`` however the prover
        # happened to order the two steps that produced them.
        pivots_ = tuple(sorted(mapping[v] for v in schema.pivot_vars))
        cand = Schema(prem, concl, pivots_, schema.step_count, schema.origin)
        key = (tuple(p.lits for p in prem), concl.lits, pivots_)
        if best_key is None or key < best_key:
            best, best_key = cand, key
    assert best is not None
    return best


def _pattern_from_clause(c: Clause) -> Pattern:
    return Pattern(tuple(sorted((f"p{p}", s) for p, s in c)))


def lift_step(step: Step) -> Schema:
    """Signed-clause normalisation plus predicate-variable lifting of one step.

    This is deterministic normalisation, not induction: every predicate becomes
    its own variable and the result is put in canonical form.  It lives here
    rather than in ``libdisc_discovery`` so that the generator can certify
    recurrence without importing the learner.
    """
    return canonical_schema(Schema(
        premises=(_pattern_from_clause(step.left), _pattern_from_clause(step.right)),
        conclusion=_pattern_from_clause(step.conclusion),
        pivot_vars=(f"p{step.pivot}",),
        step_count=1,
        origin="single",
    ))


def lift_two_step(first: Step, second: Step) -> Schema | None:
    """Lift two consecutive steps where the second consumes the first's result."""
    if second.left == first.conclusion:
        third = second.right
    elif second.right == first.conclusion:
        third = second.left
    else:
        return None
    return canonical_schema(Schema(
        premises=(
            _pattern_from_clause(first.left),
            _pattern_from_clause(first.right),
            _pattern_from_clause(third),
        ),
        conclusion=_pattern_from_clause(second.conclusion),
        pivot_vars=(f"p{first.pivot}", f"p{second.pivot}"),
        step_count=2,
        origin="composed",
    ))


def schema_is_sound(schema: Schema, sample_bindings: int | None = None) -> bool:
    """Does the independent checker certify every ground instance of ``schema``?

    Propositional semantics is invariant under renaming of predicate symbols, so
    a schema certified under one injective binding is certified under all of
    them; ``sample_bindings=None`` checks every injective binding anyway, which
    is affordable at this scale and turns that argument into a measurement.
    """
    variables = schema.variables
    k = len(variables)
    combos = itertools.permutations(range(N_PREDS), k)
    checked = 0
    for combo in combos:
        binding = {v: combo[i] for i, v in enumerate(variables)}
        prem = [instantiate(p, binding) for p in schema.premises]
        concl = instantiate(schema.conclusion, binding)
        if concl is None or any(p is None for p in prem):
            continue
        if not entails([p for p in prem if p is not None], concl):
            return False
        checked += 1
        if sample_bindings is not None and checked >= sample_bindings:
            break
    return checked > 0


def extrapolation_probes(schema: Schema, above: int) -> list[dict[str, int]]:
    """Registered scope sample drawn strictly beyond the training support.

    CL-D1(b) asks for certificates on ``scope(M) \\ support(D)`` at magnitudes
    strictly greater than ``max(support(D))``.  The magnitude analogue here is
    the predicate index: probes use only predicates with index ``> above``, none
    of which appear in any training step this schema was induced from.
    """
    pool = [p for p in range(N_PREDS) if p > above]
    k = len(schema.variables)
    if len(pool) < k:
        return []
    return [
        {v: combo[i] for i, v in enumerate(schema.variables)}
        for combo in itertools.permutations(pool, k)
    ]


#: The single-step chain schema the training proofs make recur.
CHAIN_SCHEMA = lift_step(_step(C(M(0), L(1)), C(M(1), L(2)), 1))

#: The single-step merge schema: recurs, is admissible, and is never demanded.
MERGE_SCHEMA = lift_step(_step(C(L(0), L(1)), C(M(1), L(2)), 1))

#: The two-step composite the discovery arm has to build for itself.  Declared
#: here as the *reference* the generator certifies its draw against; the arms
#: never read it, and ``test_libdisc.py`` asserts that what discovery finds is
#: behaviourally identical to it rather than assuming so.
CHAIN2_SCHEMA = lift_two_step(
    _step(C(M(0), L(1)), C(M(1), L(2)), 1),
    _step(C(M(0), L(2)), C(M(2), L(3)), 2),
)
assert CHAIN2_SCHEMA is not None


# --------------------------------------------------------------------------
# the four certifications
# --------------------------------------------------------------------------


def checked_flat_fragments(episode: Episode) -> list[tuple]:
    """Flat fragments of one episode that the diagnosis's miner would accept.

    A candidate is a PROPER two-premise subcover whose pair the independent
    checker certifies as entailing the query (sound) and as essential (neither
    premise alone suffices).  These are the "three structurally different
    essential fragments" of the diagnosis, at the level of abstraction that made
    them singletons.
    """
    out: list[tuple] = []
    prem = episode.premises
    if len(prem) <= 2:
        return out  # a two-premise task cannot donate a PROPER subcover
    for pair in itertools.combinations(prem, 2):
        if not entails(pair, episode.query):
            continue
        if any(entails([single], episode.query) for single in pair):
            continue
        out.append(flat_fragment(pair, episode.query))
    return out


def step_schema_supports(
    episodes: Sequence[Episode] = TRAINING_EPISODES,
) -> dict[str, dict]:
    """Distinct-episode support counts for every lifted single step in the draw."""
    table: dict[str, dict] = {}
    for ep in episodes:
        for st in ep.proof:
            sch = lift_step(st)
            row = table.setdefault(sch.schema_id, {
                "schema": sch, "episodes": set(), "instances": 0})
            row["episodes"].add(ep.episode_id)
            row["instances"] += 1
    return table


def composite_supports(
    episodes: Sequence[Episode] = TRAINING_EPISODES,
) -> dict[str, dict]:
    """Distinct-episode support counts for every lifted two-step composite."""
    table: dict[str, dict] = {}
    for ep in episodes:
        for a, b in zip(ep.proof, ep.proof[1:]):
            sch = lift_two_step(a, b)
            if sch is None:
                continue
            row = table.setdefault(sch.schema_id, {
                "schema": sch, "episodes": set(), "instances": 0})
            row["episodes"].add(ep.episode_id)
            row["instances"] += 1
    return table


@dataclass(frozen=True)
class Certification:
    """What the generator proves about its own draw before anything is run."""

    flat_fragments_distinct: bool
    flat_fragment_count: int
    flat_fragment_max_multiplicity: int
    step_schema_recurs: bool
    recurring_schema_id: str
    recurring_schema_episodes: int
    recurring_schema_instances: int
    composite_schema_episodes: int
    essential_composite_exists: bool
    essential_rows: tuple[dict, ...]
    tautological_control_exists: bool
    control_rows: tuple[dict, ...]
    tautology_count: int
    bypass_count: int
    fresh_disjoint_from_training: bool
    all_certified: bool
    failures: tuple[str, ...]

    def as_dict(self) -> dict:
        return {
            "flat_fragments_distinct": self.flat_fragments_distinct,
            "flat_fragment_count": self.flat_fragment_count,
            "flat_fragment_max_multiplicity": self.flat_fragment_max_multiplicity,
            "step_schema_recurs": self.step_schema_recurs,
            "recurring_schema_id": self.recurring_schema_id,
            "recurring_schema_episodes": self.recurring_schema_episodes,
            "recurring_schema_instances": self.recurring_schema_instances,
            "composite_schema_episodes": self.composite_schema_episodes,
            "essential_composite_exists": self.essential_composite_exists,
            "essential_rows": list(self.essential_rows),
            "tautological_control_exists": self.tautological_control_exists,
            "control_rows": list(self.control_rows),
            "tautology_count": self.tautology_count,
            "bypass_count": self.bypass_count,
            "fresh_disjoint_from_training": self.fresh_disjoint_from_training,
            "all_certified": self.all_certified,
            "failures": list(self.failures),
        }


def certify_draw(
    episodes: Sequence[Episode] = TRAINING_EPISODES,
    essential: Sequence[Task] = ESSENTIAL_COMPOSITE_TASKS,
    control: Sequence[Task] = TAUTOLOGICAL_CONTROL_TASKS,
    reference: Schema = CHAIN2_SCHEMA,
) -> Certification:
    """Certify the four properties the design needs, by computation.

    1. every flat surface fragment the flat miner would accept occurs at most
       once, so the flat miner finds no repeated support;
    2. a lifted step schema recurs across at least
       ``REPEATED_SUPPORT_THRESHOLD`` distinct training episodes, and so does
       the two-step composite;
    3. ESSENTIAL-COMPOSITE fresh tasks exist: non-tautological targets on which
       removing the composite schema STRICTLY INCREASES the minimal derivation
       depth;
    4. TAUTOLOGICAL / BYPASSABLE fresh tasks exist: targets the same schema
       matches, which are tautologies or admit a bypass at equal depth.

    Nothing here is hoped for.  If a property fails, ``all_certified`` is False
    and ``failures`` names it; the registered response is to report that as the
    finding, never to relax the property.
    """
    failures: list[str] = []

    # (1) flat surface fragments
    frags: list[tuple] = []
    for ep in episodes:
        frags.extend(checked_flat_fragments(ep))
    counts: dict[tuple, int] = {}
    for f in frags:
        counts[f] = counts.get(f, 0) + 1
    max_mult = max(counts.values()) if counts else 0
    flat_distinct = max_mult <= 1
    if not flat_distinct:
        failures.append("flat surface fragments are not pairwise distinct")
    if not frags:
        failures.append("no flat fragment is even accepted; the ablation is vacuous")

    # (2) recurrence at the step level
    steps = step_schema_supports(episodes)
    best_id, best = "", {"episodes": set(), "instances": 0}
    for sid, row in steps.items():
        if len(row["episodes"]) > len(best["episodes"]):
            best_id, best = sid, row
    recurs = len(best["episodes"]) >= REPEATED_SUPPORT_THRESHOLD
    if not recurs:
        failures.append("no step schema recurs across the required episode count")
    comps = composite_supports(episodes)
    comp_eps = max((len(r["episodes"]) for r in comps.values()), default=0)
    if comp_eps < REPEATED_SUPPORT_THRESHOLD:
        failures.append("no two-step composite recurs across the required episodes")

    # (3) essential composite opportunity
    essential_rows: list[dict] = []
    for t in essential:
        without = min_derivation_length(t.premises, t.query, ())
        with_ = min_derivation_length(t.premises, t.query, (reference,))
        matched = bool(match_schema(reference, sorted(t.premises)))
        ok = (
            not is_tautology(t.query)
            and matched
            and without is not None
            and with_ is not None
            and without > with_
        )
        essential_rows.append({
            "task_id": t.task_id, "role": t.role, "matched": matched,
            "tautology": is_tautology(t.query),
            "min_depth_without": without, "min_depth_with": with_,
            "strictly_shorter": ok,
        })
        if not ok:
            failures.append(f"{t.task_id} declared essential-composite but is not")
    essential_exists = bool(essential_rows) and all(
        r["strictly_shorter"] for r in essential_rows)

    # (4) tautological / bypassable control
    control_rows: list[dict] = []
    tauto = 0
    bypass = 0
    for t in control:
        without = min_derivation_length(t.premises, t.query, ())
        with_ = min_derivation_length(t.premises, t.query, (reference,))
        matched = bool(match_schema(reference, sorted(t.premises)))
        taut = is_tautology(t.query)
        equal = without == with_
        ok = matched and (taut or equal)
        if taut:
            tauto += 1
        elif equal:
            bypass += 1
        control_rows.append({
            "task_id": t.task_id, "role": t.role, "matched": matched,
            "tautology": taut, "min_depth_without": without,
            "min_depth_with": with_, "no_opportunity": ok,
        })
        if not ok:
            failures.append(f"{t.task_id} declared a control but has an opportunity")
    control_exists = (
        bool(control_rows)
        and all(r["no_opportunity"] for r in control_rows)
        and tauto > 0
        and bypass > 0
    )
    if tauto == 0:
        failures.append("no tautological target in the control set")
    if bypass == 0:
        failures.append("no equal-cost bypass in the control set")

    # freshness
    training_forms = {flat_fragment(ep.premises, ep.query) for ep in episodes}
    fresh_ok = all(
        flat_fragment(t.premises, t.query) not in training_forms
        for t in tuple(essential) + tuple(control))
    if not fresh_ok:
        failures.append("a fresh task duplicates a training episode")

    return Certification(
        flat_fragments_distinct=flat_distinct,
        flat_fragment_count=len(frags),
        flat_fragment_max_multiplicity=max_mult,
        step_schema_recurs=recurs,
        recurring_schema_id=best_id,
        recurring_schema_episodes=len(best["episodes"]),
        recurring_schema_instances=best["instances"],
        composite_schema_episodes=comp_eps,
        essential_composite_exists=essential_exists,
        essential_rows=tuple(essential_rows),
        tautological_control_exists=control_exists,
        control_rows=tuple(control_rows),
        tautology_count=tauto,
        bypass_count=bypass,
        fresh_disjoint_from_training=fresh_ok,
        all_certified=not failures,
        failures=tuple(failures),
    )


# --------------------------------------------------------------------------
# pre-registration (CL-D4)
# --------------------------------------------------------------------------

LIBDISC_PLAN = {
    "study_id": "CL-LIBDISC-E5-V1",
    "question": (
        "Two negatives have been reported in this programme and they are "
        "different failures: NO_METHOD_ACQUIRED, where discovery happened at "
        "the wrong level of abstraction, and NO_DEVELOPMENT_BENEFIT, where "
        "discovery succeeded and no task demanded what was discovered. Run the "
        "SAME discovered schema against a fresh-task set that has an essential "
        "composite opportunity and one that does not, and report which term is "
        "doing the work."
    ),
    "domain": {
        "logic": "propositional signed clauses",
        "predicates": N_PREDS,
        "assignments": N_ASSIGNMENTS,
        "max_clause_width": MAX_CLAUSE_WIDTH,
        "every(A,B)": "(not A or B)",
        "no(A,B)": "(not A or not B)",
        "checker": "exhaustive assignment enumeration, CL-D1(c)",
    },
    "repeated_support_threshold": REPEATED_SUPPORT_THRESHOLD,
    "threshold_is_frozen": (
        "The >=2 gate is the registered discovery criterion of the diagnosed "
        "learner and is not lowered here under any circumstances. "
        "ASSAY-ACQUISITION-DIAGNOSIS.md: 'Keep >=2 unchanged in the first "
        "revival to isolate representation.'"
    ),
    "semantic_weakening": (
        "NOT IMPLEMENTED. CLAUSE-REVIVAL-RESULT.md considered accepting "
        "redundant sound substitutions and refused: 'Counting them as learned "
        "benefit would be misleading.' Redundant-but-sound matches are counted "
        "in their own column."
    ),
    "max_search_depth": MAX_SEARCH_DEPTH,
    "arms": [
        "libdisc_discovery_arm", "flat_mining_ablation",
        "anti_unification_parent", "stitch_parent", "dreamcoder_parent",
        "symbolic_compact_parent", "symbolic_incremental_memory_parent",
        "no_library_baseline", "reset_arm",
    ],
    "fresh_task_sets": ["essential_composite", "tautological_control"],
    "controls": [
        "false_common_pattern", "surface_similar_different_polarity",
        "singleton_no_generalisation", "harmful_abstraction", "scope_revision",
    ],
    "leakage": {
        "learner_visible_episode_fields": list(LEARNER_VISIBLE_EPISODE_FIELDS),
        "learner_visible_task_fields": list(LEARNER_VISIBLE_TASK_FIELDS),
        "evaluator_only_fields": list(EVALUATOR_ONLY_FIELDS),
        "adopted_from": (
            "codex/ocm-evolvability-independent-20260908:"
            "research/evolvability-independent/PROTECTED_PROTOCOL_V3.md card E150-A"
        ),
    },
    "custody": "CL-T1: acquiring process serializes and EXITS; a different PID reads it",
    "endpoints": {
        "primary": "fresh-task search work on each set, reported separately",
        "secondary": [
            "schemas discovered and admitted per arm",
            "flat ablation pool size",
            "harmful-transfer rate S5",
            "redundant-but-sound matches, separate column",
        ],
    },
}

COMMITMENT_BODY = digest_of(LIBDISC_PLAN)


def schema_from_body(body: dict) -> Schema:
    """Rebuild a schema from its serialized body.

    Used across the custody boundary: the acquiring process writes bodies to
    disk and exits, and the reading process reconstructs the objects from the
    file and from nothing else.
    """
    return Schema(
        premises=tuple(
            Pattern(tuple(sorted((v, bool(s)) for v, s in p)))
            for p in body["premises"]),
        conclusion=Pattern(tuple(sorted((v, bool(s)) for v, s in body["conclusion"]))),
        pivot_vars=tuple(body["pivot_vars"]),
        step_count=int(body["step_count"]),
        origin=str(body["origin"]),
    )


def _negative_task(name: str, premises: Sequence[Clause], query: Clause,
                   role: str) -> Task:
    prem = tuple(premises)
    if entails(prem, query):
        raise ValueError(f"{name}: query IS entailed; this is not a trap")
    return Task(name, prem, query, role)


#: Tasks whose query is NOT entailed, chosen so that a polarity-blind or
#: over-general macro would fire on them.  Any arm that reports these solved has
#: produced a wrong answer, which is endpoint S5 (harmful transfer) in its
#: sharpest form.  The sign-preserving matcher does not fire here; the
#: ``polarity_blind_refutations`` control measures what a sign-blind one would
#: have done.
UNSOUND_TRAP_TASKS: tuple[Task, ...] = (
    _negative_task("X1", [C(M(0), L(1)), C(L(1), L(2)), C(M(2), L(3))],
                   C(M(0), L(3)), "unsound_trap"),
    _negative_task("X2", [C(M(0), L(1)), C(M(1), L(2)), C(M(2), L(3))],
                   C(M(3), L(0)), "unsound_trap"),
    _negative_task("X3", [C(M(0), M(1)), C(M(1), L(2)), C(M(2), L(3)),
                          C(L(6), L(7))], C(M(0), L(3)), "unsound_trap"),
)
