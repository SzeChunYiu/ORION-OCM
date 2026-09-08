"""Incremental re-indexing: the cheapest unrun fix in the programme.

Experiment E1 returned ``INDEX_MAINTENANCE_DOMINATES`` and its own receipt named
the reason and disclaimed the generality in the same breath:

    The discovering arm rescans the whole feature language from the smallest
    arity on every re-index, charged one unit per stored method per candidate
    with no early exit.  An incremental search that resumed from the current
    arity, or abandoned a candidate at the first overflowing bucket, would cost
    materially less.  Such a search is NOT run here, so the terminal is about
    what this procedure costs, not about what is achievable.

This module runs it.  Two changes, both of which must leave the *chosen feature*
untouched, so that only cost moves and capability cannot.

**Monotone resumption.**  Buckets only grow as methods are inserted, never
shrink.  So a candidate feature whose maximum bucket already exceeded the
threshold at some earlier point still exceeds it now, and can never become
adequate again.  Every candidate rejected in an earlier search may therefore be
skipped permanently, and the search resumes where the last one stopped rather
than restarting from arity one.  This is sound because the store here only
grows; a store that also *deletes* would invalidate the argument and the
implementation refuses to resume in that case rather than silently being wrong.

**Early exit.**  The exhaustive search counts every method into buckets before
looking at the maximum.  A candidate is doomed the moment any one bucket passes
the threshold, so the scan stops there.  This changes cost from ``methods`` per
candidate to ``methods examined before the first overflow``.

The equivalence gate is the point of the module: at every step the incremental
search must select **the same feature** the exhaustive search would have
selected.  If it ever does not, the optimisation is unsound and the experiment
is void, and a test asserts it on every scale of the sweep.
"""

from __future__ import annotations

from dataclasses import dataclass

from scaling import TouchLedger
from subspace import MAX_BUCKET_SIZE, Feature, feature_language, feature_pool
from subspace_arms import DiscoveringArm, FeatureIndex

__all__ = ["IncrementalFeatureIndex", "IncrementalDiscoveringArm", "search_cost_exhaustive",
           "search_cost_incremental"]


class IncrementalFeatureIndex(FeatureIndex):
    """``FeatureIndex`` with a resumable, early-exiting feature search.

    Selection is identical to the parent class by construction: both scan the
    registered language in the same order and take the first adequate candidate.
    Only the work charged differs.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        #: number of leading candidates permanently excluded by monotonicity
        self._resume_at = 0
        self._resume_valid = True
        self.candidates_skipped = 0
        self.early_exits = 0

    def note_deletion(self) -> None:
        """Deletions break the monotonicity argument, so stop resuming.

        Nothing in this lane deletes, but a store that did would make a rejected
        feature adequate again, and a silently wrong optimisation is worse than
        a slow one.
        """
        self._resume_valid = False
        self._resume_at = 0

    def search_for_feature(
        self, ledger: TouchLedger, *, charge: str
    ) -> tuple[Feature | None, int]:
        language = feature_language()
        ids = list(self._pool_vectors)
        candidates = list(language.features())
        start = self._resume_at if self._resume_valid else 0
        self.candidates_skipped += start

        tried = 0
        cost = 0
        chosen: Feature | None = None
        rejected_upto = start
        for position in range(start, len(candidates)):
            candidate = candidates[position]
            tried += 1
            buckets: dict[tuple[int, ...], int] = {}
            overflowed = False
            examined = 0
            for method_id in ids:
                examined += 1
                key = self._image_under(method_id, candidate)
                buckets[key] = buckets.get(key, 0) + 1
                if buckets[key] > MAX_BUCKET_SIZE:
                    overflowed = True
                    self.early_exits += 1
                    break
            cost += max(examined, 1)
            if not overflowed:
                chosen = candidate
                self._resume_at = position if self._resume_valid else 0
                break
            rejected_upto = position + 1
        else:
            self._resume_at = rejected_upto if self._resume_valid else 0

        self.features_evaluated += tried
        if charge == "build":
            self.build_work += cost
            ledger.index_build_work += cost
        else:
            self.maintenance_work += cost
            ledger.index_maintenance_work += cost
        return chosen, tried


class IncrementalDiscoveringArm(DiscoveringArm):
    """The E1 discovering arm with the incremental index, and nothing else changed.

    ``_install`` is duplicated from ``FeatureArm`` rather than patched, because
    the original file is a committed result and must not be edited to make a
    later experiment work. The only difference is the index class.
    """

    role = "MACHINE"
    arm_id = "incremental_discovering_arm"

    def _install(self, ledger: TouchLedger) -> None:
        chooses = self.chooses_feature or self.re_indexes
        pool = feature_pool() if chooses else None
        initial = feature_language().features()[0] if chooses else self.hand_feature
        self.index = IncrementalFeatureIndex(self.store, initial, ledger, cache_pool=pool)
        self._exhausted = False
        if self.chooses_feature:
            chosen, _ = self.index.search_for_feature(ledger, charge="build")
            if chosen is None:
                self._exhausted = True
            else:
                self.index.rebuild_on(chosen, ledger)
                self.index.re_index_count = 0


def search_cost_exhaustive(pool_vectors, candidates) -> int:
    """Cost model of the original search: every candidate charges every method."""
    return len(candidates) * max(len(pool_vectors), 1)


def search_cost_incremental(examined_per_candidate) -> int:
    """Cost model of the incremental search: methods examined before overflow."""
    return sum(max(e, 1) for e in examined_per_candidate)


@dataclass(frozen=True)
class EquivalenceCheck:
    """Result of comparing the two searches at one point in the sweep."""

    scale_id: str
    exhaustive_feature: str | None
    incremental_feature: str | None
    same_feature: bool
    exhaustive_cost: int
    incremental_cost: int
    saving_ratio: float
    candidates_skipped: int
    early_exits: int


# --------------------------------------------------------------------------
# registering the arm without editing the committed experiment
# --------------------------------------------------------------------------

#: ``subspace_arms.run_lifetime`` resolves an arm by id through its ``ARMS``
#: map.  Registering here ADDS an entry; it replaces nothing, so every existing
#: arm behaves exactly as it did and the committed E1 receipt stays reproducible.
INCREMENTAL_ARM_ID = "incremental_discovering_arm"


def register() -> None:
    import subspace_arms as SA

    if INCREMENTAL_ARM_ID in SA.ARMS:
        return
    if set(SA.ARMS) != {
        "discovering_arm", "fixed_feature_arm", "oracle_key_parent",
        "exact_scan_parent", "signature_hash_parent", "nearest_neighbour_parent",
    }:
        raise RuntimeError(
            "the E1 arm registry changed; refusing to register against an unexpected "
            "baseline rather than silently comparing against something else"
        )
    SA.ARMS[INCREMENTAL_ARM_ID] = IncrementalDiscoveringArm
    SA.ARM_ROLES[INCREMENTAL_ARM_ID] = IncrementalDiscoveringArm.role
