"""E5 parents: the strongest faithful alternative explanations, first right of refusal.

Every parent here sees the SAME episodes through the same ``LearnerView`` (input
plus correct actions, nothing else), searches to the same depth, calls the same
independent checker, and is scored on the same two fresh-task sets.  No parent is
weakened to make room for a result.  Protocol section 7: "The strongest plausible
alternative explanation gets first right of refusal on every effect."

    ``anti_unification_parent``
        Syntactic least general generalisation over FLAT traces.  No step
        decomposition: an episode is one object, premises plus query.  This is
        the level the diagnosed learner worked at, made as strong as it can be
        -- a flat generalisation over three or more premises is treated as a
        macro that collapses two or more steps, so if flat traces shared
        structure this parent would find a usable one.

    ``stitch_parent``
        Corpus-level MDL compression over trace subsequences, with positional
        argument abstraction.  Its admission criterion is its own: description
        length of the corpus under the library.  It has NO >=2 support gate and
        no soundness gate, which is faithful to what it is, and it therefore can
        -- and on this draw does -- admit abstractions the >=2 gate refuses.
        If that buys it fresh-task work the discovery arm did not get, that is a
        finding against the gate and it is reported as one.

    ``dreamcoder_parent``
        Library induction with a refit loop: propose abstractions, RE-SOLVE the
        whole corpus with the candidate library, keep the candidate only if the
        corpus description length strictly falls, iterate to a fixpoint.  This
        is a different algorithm from Stitch, not a renaming of it: Stitch counts
        occurrences, DreamCoder re-runs the solver.

    ``symbolic_compact_parent``
        Adopted from the frozen protected protocol on branch
        ``codex/ocm-evolvability-independent-20260908``
        (``research/evolvability-independent/PROTECTED_PROTOCOL_V3.md``, card
        E150-A).  Same observable episodes, same bounded grammar, same exact
        clustering/MDL learner, same contradiction-triggered local refit -- and
        no duplicate relevance cache.  It is the hardest target in this file
        precisely because it shares the mechanism under test: whatever separates
        it from the discovery arm is caching and nothing else.  If it matches,
        the terminal is ``PARENT_SUFFICIENT`` and the honest reading is
        ``REUSE_EFFECT_IS_INFRASTRUCTURAL``.

    ``symbolic_incremental_memory_parent``
        The same, plus the exact episode archive, replayed on a fresh task when
        the task is alpha-equivalent to a stored one.  This is CL protocol
        parent ``P1``, the persistent memo table, and it is mandatory.

    ``no_library_baseline``
        Plain enumerative resolution search.  No library, no persistence.

    ``reset_arm``
        Discovery runs and its state is DISCARDED at the custody boundary, so at
        fresh-task time the arm holds nothing.  This is the arm the causal chain
        is measured against: "less search than the reset arm".

``ROOT_CAUSE_ANALYSIS_V1.md`` records ``PARENT_SHARES_THE_MECHANISM_UNDER_TEST``
as a first-order root of two earlier verdicts, and two of the parents here share
the mechanism deliberately.  That is stated in the receipt rather than hidden:
their sufficiency, if it holds, is informative about caching and infrastructure,
not about whether an independently implemented parent would also suffice.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field
from typing import Sequence

from libdisc import (
    GROUND_STEP_SPACE,
    MAX_SEARCH_DEPTH,
    REPEATED_SUPPORT_THRESHOLD,
    Clause,
    LearnerView,
    Pattern,
    Schema,
    SearchWork,
    SolveResult,
    Step,
    binding_space,
    canonical_schema,
    entails,
    flat_fragment,
    instantiate,
    schema_code_bits,
    schema_is_sound,
    solve,
    support_data_bits,
    support_residual_bits,
)
from libdisc_discovery import (
    AdmissionRecord,
    admit,
    anti_unify,
    discover,
    semantic_key,
)

__all__ = [
    "ParentResult",
    "PARENTS",
    "lift_subsequence",
    "anti_unification_parent",
    "stitch_parent",
    "dreamcoder_parent",
    "symbolic_compact_parent",
    "symbolic_incremental_memory_parent",
    "no_library_baseline",
    "reset_arm",
    "replay_from_archive",
]

GROUND_BITS = math.log2(GROUND_STEP_SPACE)

#: Corpus-description-length charge for an episode the library cannot re-solve.
#: Set to twice the cost of writing the longest observed proof out verbatim, so
#: an abstraction can never be accepted because it made an episode unsolvable.
UNSOLVED_PENALTY = 8 * GROUND_BITS


@dataclass(frozen=True)
class ParentResult:
    """What one parent holds after training, and how it will be run."""

    name: str
    library: tuple[Schema, ...]
    relevance_index: bool
    archive: tuple[LearnerView, ...]
    notes: str
    funnel: dict

    @property
    def applicable(self) -> tuple[Schema, ...]:
        return tuple(s for s in self.library if s.step_count >= 2)

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "library_size": len(self.library),
            "applicable_macros": len(self.applicable),
            "schema_ids": [s.schema_id for s in self.library],
            "relevance_index": self.relevance_index,
            "archive_episodes": len(self.archive),
            "notes": self.notes,
            "funnel": self.funnel,
        }


def _pattern_of(c: Clause) -> Pattern:
    return Pattern(tuple(sorted((f"p{p}", s) for p, s in c)))


def lift_subsequence(steps: Sequence[Step]) -> Schema | None:
    """Abstract a contiguous run of proof steps into one macro.

    The premises are the clauses the run consumes but does not itself produce;
    the conclusion is the last step's conclusion; every predicate becomes a
    variable.  This is the argument abstraction both library-learning parents
    perform, and it is deliberately the SAME proposal space the discovery arm
    reaches by composition, so the arms differ in their admission criteria
    rather than in what they are able to see.
    """
    if not steps:
        return None
    produced: set[Clause] = set()
    externals: list[Clause] = []
    for st in steps:
        for c in (st.left, st.right):
            if c not in produced and c not in externals:
                externals.append(c)
        produced.add(st.conclusion)
    if not 2 <= len(externals) <= 4:
        return None
    concl = steps[-1].conclusion
    try:
        return canonical_schema(Schema(
            tuple(_pattern_of(c) for c in externals),
            _pattern_of(concl),
            tuple(f"p{st.pivot}" for st in steps),
            len(steps),
            "subsequence",
        ))
    except ValueError:
        return None


def _subsequence_candidates(views: Sequence[LearnerView]) -> dict[tuple, dict]:
    """Every contiguous proof subsequence in the corpus, semantically clustered."""
    table: dict[tuple, dict] = {}
    for view in views:
        sup = flat_fragment(view.premises, view.query)
        n = len(view.proof)
        for i in range(n):
            for j in range(i + 1, n + 1):
                sch = lift_subsequence(view.proof[i:j])
                if sch is None:
                    continue
                key = semantic_key(sch)
                row = table.setdefault(key, {
                    "schema": sch, "occurrences": 0, "supports": set(),
                    "instances": []})
                row["occurrences"] += 1
                row["supports"].add(sup)
                prem = tuple(p for p in _externals(view.proof[i:j]))
                row["instances"].append((prem, view.proof[j - 1].conclusion))
    return table


def _externals(steps: Sequence[Step]) -> list[Clause]:
    produced: set[Clause] = set()
    externals: list[Clause] = []
    for st in steps:
        for c in (st.left, st.right):
            if c not in produced and c not in externals:
                externals.append(c)
        produced.add(st.conclusion)
    return externals


# --------------------------------------------------------------------------
# P: flat anti-unification, no step decomposition
# --------------------------------------------------------------------------


def _flat_schema(view: LearnerView) -> Schema | None:
    """One whole episode as a single flat object: premises in, query out."""
    if not 2 <= len(view.premises) <= 4:
        return None
    try:
        return canonical_schema(Schema(
            tuple(_pattern_of(c) for c in view.premises),
            _pattern_of(view.query),
            (),
            max(1, len(view.premises) - 1),
            "flat",
        ))
    except ValueError:
        return None


def anti_unification_parent(
    views: Sequence[LearnerView],
    threshold: int = REPEATED_SUPPORT_THRESHOLD,
) -> ParentResult:
    """Least general generalisation over flat traces, with the same gate."""
    flats = [(v, _flat_schema(v)) for v in views]
    funnel = {
        "episodes": len(views),
        "flat_objects": sum(1 for _, s in flats if s is not None),
        "pairs_generalised": 0,
        "generalisations_unsound": 0,
        "admitted": 0,
    }
    groups: dict[tuple, dict] = {}
    for (va, sa), (vb, sb) in itertools.combinations(flats, 2):
        if sa is None or sb is None:
            continue
        g = anti_unify(sa, sb)
        if g is None:
            continue
        funnel["pairs_generalised"] += 1
        if not schema_is_sound(g):
            funnel["generalisations_unsound"] += 1
            continue
        row = groups.setdefault(semantic_key(g), {
            "schema": g, "supports": set(), "instances": []})
        for v in (va, vb):
            row["supports"].add(flat_fragment(v.premises, v.query))
            row["instances"].append((tuple(v.premises), v.query))
    library: list[Schema] = []
    for row in groups.values():
        rec = admit(row["schema"], row["instances"], len(row["supports"]), threshold)
        if rec.admissible:
            library.append(row["schema"])
            funnel["admitted"] += 1
    return ParentResult(
        "anti_unification_parent", tuple(library), True, (),
        "syntactic lgg over whole episodes; no step decomposition", funnel)


# --------------------------------------------------------------------------
# P: Stitch -- corpus-level MDL over trace subsequences
# --------------------------------------------------------------------------


def stitch_parent(views: Sequence[LearnerView]) -> ParentResult:
    """Keep every abstraction whose corpus description length saving is positive.

    ``saving = k * L * bits(ground step) - k * bits(binding) - bits(schema)``

    where ``k`` is the number of occurrences in the corpus and ``L`` the number
    of steps the abstraction collapses.  There is no support threshold: a
    single occurrence can pay for itself if the abstraction is short enough
    relative to what it replaces, and on this draw several do.
    """
    table = _subsequence_candidates(views)
    funnel = {
        "episodes": len(views), "candidates": len(table), "kept": 0,
        "kept_single_occurrence": 0, "kept_unsound": 0, "savings": {},
    }
    library: list[Schema] = []
    for row in sorted(table.values(), key=lambda r: r["schema"].schema_id):
        sch = row["schema"]
        k = row["occurrences"]
        saving = (
            k * sch.step_count * GROUND_BITS
            - k * math.log2(binding_space(sch.arity))
            - schema_code_bits(sch)
        )
        funnel["savings"][sch.schema_id[:12]] = round(saving, 3)
        if saving <= 0:
            continue
        library.append(sch)
        funnel["kept"] += 1
        if len(row["supports"]) < REPEATED_SUPPORT_THRESHOLD:
            funnel["kept_single_occurrence"] += 1
        if not schema_is_sound(sch):
            funnel["kept_unsound"] += 1
    return ParentResult(
        "stitch_parent", tuple(library), True, (),
        "corpus MDL over contiguous trace subsequences; no support gate, "
        "no soundness gate", funnel)


# --------------------------------------------------------------------------
# P: DreamCoder -- propose, re-solve, keep what shortens the corpus
# --------------------------------------------------------------------------


def _corpus_bits(library: Sequence[Schema], views: Sequence[LearnerView]) -> float:
    """Description length of the corpus under ``library``, by RE-SOLVING it."""
    arity = {s.schema_id: s.arity for s in library}
    total = sum(schema_code_bits(s) for s in library)
    for view in views:
        res = solve(view.premises, view.query, library, MAX_SEARCH_DEPTH,
                    check_answer=False, relevance_index=True)
        if not res.solved:
            total += UNSOLVED_PENALTY
            continue
        for item in res.trace:
            if item[0] == "macro":
                total += math.log2(binding_space(arity.get(item[1], 4)))
            else:
                total += GROUND_BITS
    return total


def dreamcoder_parent(
    views: Sequence[LearnerView], max_rounds: int = 6
) -> ParentResult:
    """Library induction with a refit loop, to a fixpoint."""
    proposals = [row["schema"] for row in _subsequence_candidates(views).values()]
    library: list[Schema] = []
    best = _corpus_bits(library, views)
    funnel = {
        "episodes": len(views), "proposals": len(proposals), "rounds": 0,
        "accepted": 0, "corpus_bits_start": round(best, 3), "trace": [],
    }
    for _round in range(max_rounds):
        funnel["rounds"] += 1
        winner: Schema | None = None
        winner_bits = best
        for cand in proposals:
            if any(cand.schema_id == s.schema_id for s in library):
                continue
            bits = _corpus_bits(library + [cand], views)
            if bits < winner_bits - 1e-9:
                winner, winner_bits = cand, bits
        if winner is None:
            break
        library.append(winner)
        funnel["trace"].append({
            "schema_id": winner.schema_id[:12], "step_count": winner.step_count,
            "corpus_bits": round(winner_bits, 3)})
        funnel["accepted"] += 1
        best = winner_bits
    funnel["corpus_bits_end"] = round(best, 3)
    return ParentResult(
        "dreamcoder_parent", tuple(library), True, (),
        "propose abstractions, re-solve the corpus, keep what shortens it, "
        "iterate to a fixpoint", funnel)


# --------------------------------------------------------------------------
# P: the symbolic parents adopted from the frozen protected protocol
# --------------------------------------------------------------------------


def symbolic_compact_parent(views: Sequence[LearnerView]) -> ParentResult:
    """Same learner, same grammar, same gate, same refit -- no relevance cache.

    This parent shares the mechanism under test on purpose.  It exists to answer
    exactly one question: how much of any separation is knowledge and how much
    is the duplicate index that makes matching cheap?  A tie on schemas with a
    gap only in matching work is ``REUSE_EFFECT_IS_INFRASTRUCTURAL``, and a tie
    on both is ``PARENT_SUFFICIENT``.
    """
    result = discover(views)
    funnel = dict(result.funnel)
    funnel["shares_mechanism_under_test"] = True
    return ParentResult(
        "symbolic_compact_parent", result.library(), False, (),
        "identical clustering/MDL learner and identical >=2 gate; differs from "
        "the discovery arm ONLY by holding no duplicate relevance cache", funnel)


def symbolic_incremental_memory_parent(
    views: Sequence[LearnerView],
) -> ParentResult:
    """The compact parent plus the exact episode archive (CL protocol ``P1``)."""
    result = discover(views)
    funnel = dict(result.funnel)
    funnel["shares_mechanism_under_test"] = True
    funnel["archive_episodes"] = len(views)
    return ParentResult(
        "symbolic_incremental_memory_parent", result.library(), False,
        tuple(views),
        "the compact parent, plus a verbatim archive of every training episode "
        "replayed on any alpha-equivalent fresh task", funnel)


def replay_from_archive(
    archive: Sequence[LearnerView], premises: Sequence[Clause], query: Clause
) -> SolveResult | None:
    """Alpha-equivalence lookup in the episode archive.

    Every archived episode is examined and the look is charged, whether or not
    it hits.  Fresh tasks are disjoint from the training draw by construction,
    so this is expected to miss on every row; reporting the misses and their
    cost is the point of running a memoization parent at all.
    """
    work = SearchWork()
    target = flat_fragment(premises, query)
    for view in archive:
        work.subsumption_checks += 1
        if flat_fragment(view.premises, view.query) == target:
            return SolveResult(True, len(view.proof), (), False, (), work, False)
    return None


# --------------------------------------------------------------------------
# P: no library, and no persistence
# --------------------------------------------------------------------------


def no_library_baseline(views: Sequence[LearnerView]) -> ParentResult:
    return ParentResult(
        "no_library_baseline", (), False, (),
        "plain enumerative resolution search; nothing is learned and nothing "
        "is carried across the custody boundary",
        {"episodes": len(views), "library": 0})


def reset_arm(views: Sequence[LearnerView]) -> ParentResult:
    """Discovery runs; the state is DISCARDED at the custody boundary.

    The acquisition work is real and is charged; what the arm holds afterwards
    is nothing.  This is the arm the causal chain's "less search than the reset
    arm" clause is measured against, and it differs from
    ``no_library_baseline`` only in having paid for the discovery it then threw
    away.
    """
    result = discover(views)
    return ParentResult(
        "reset_arm", (), False, (),
        "discovery ran and its state was discarded at the custody boundary; "
        f"{len(result.pool)} schemas were found and none survived the restart",
        {"episodes": len(views), "discovered_then_discarded": len(result.pool)})


#: Registered parent set, in the order the receipt reports them.
PARENTS = (
    anti_unification_parent,
    stitch_parent,
    dreamcoder_parent,
    symbolic_compact_parent,
    symbolic_incremental_memory_parent,
    no_library_baseline,
    reset_arm,
)
