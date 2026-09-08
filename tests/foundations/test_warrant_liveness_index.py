"""Finite calibration and adversarial tests for the optional frozen-epoch index."""
from __future__ import annotations

import random
import unittest

from ocm.kso.warrant import CannotCheck, Liveness, WarrantProfile, all_profiles, leq, powerset
from ocm.kso.warrant_liveness_index import WarrantLivenessIndex

EPOCH = "test-field-epoch:0"


def all_intervals(n: int) -> dict[str, WarrantProfile]:
    profiles = all_profiles(n)
    intervals = [WarrantProfile(lo, up) for lo in profiles for up in profiles if leq(lo, up)]
    return {f"interval:{i}": interval for i, interval in enumerate(intervals)}


class WarrantIndexTests(unittest.TestCase):
    def test_every_three_evidence_interval_and_revocation_transition(self):
        intervals = all_intervals(3)
        self.assertEqual(len(intervals), 168)
        revocations = powerset((0, 1, 2))
        checks = 0
        for start in revocations:
            for target in revocations:
                index = WarrantLivenessIndex(intervals, epoch=EPOCH, revoked=start)
                current = start
                before = {k: p.liveness(current) for k, p in intervals.items()}
                delta = index.apply(epoch=EPOCH, revoke=target - current, reinstate=current - target)
                expected = {k: p.liveness(target) for k, p in intervals.items()}
                self.assertEqual(dict(index.snapshot(epoch=EPOCH)), expected)
                self.assertEqual(dict(delta.changes), {
                    k: (before[k], expected[k]) for k in expected if before[k] is not expected[k]
                })
                self.assertEqual(index.revoked_snapshot(epoch=EPOCH), target)
                checks += len(intervals)
        self.assertEqual(checks, 10_752)

    def test_zero_one_and_unknown_remain_distinct(self):
        index = WarrantLivenessIndex({
            "zero": WarrantProfile.zero(), "one": WarrantProfile.one(),
            "unknown": WarrantProfile.partial(()),
        }, epoch=EPOCH)
        for _ in range(3):
            index.apply(epoch=EPOCH, revoke=("missing",))
            self.assertIs(index.liveness("zero", epoch=EPOCH), Liveness.DEAD)
            self.assertIs(index.liveness("one", epoch=EPOCH), Liveness.LIVE)
            self.assertIs(index.liveness("unknown", epoch=EPOCH), Liveness.UNKNOWN)

    def test_upper_only_evidence_can_turn_unknown_dead(self):
        profile = WarrantProfile((), (frozenset({"upper-only"}),))
        self.assertFalse(profile.evidence)
        index = WarrantLivenessIndex({"p": profile}, epoch=EPOCH)
        delta = index.apply(epoch=EPOCH, revoke=("upper-only",))
        self.assertEqual(delta.changes["p"], (Liveness.UNKNOWN, Liveness.DEAD))
        self.assertEqual(delta.work.evidence_clause_visits, 1)
        delta = index.apply(epoch=EPOCH, reinstate=("upper-only",))
        self.assertEqual(delta.changes["p"], (Liveness.DEAD, Liveness.UNKNOWN))

    def test_known_support_loss_is_unknown_for_partial_profile(self):
        index = WarrantLivenessIndex({"p": WarrantProfile.of({"a"}, complete=False)}, epoch=EPOCH)
        index.apply(epoch=EPOCH, revoke=("a",))
        self.assertIs(index.liveness("p", epoch=EPOCH), Liveness.UNKNOWN)

    def test_alternative_support_is_not_conjunction(self):
        profile = WarrantProfile.of({"a"}, {"b"})
        index = WarrantLivenessIndex({"p": profile}, epoch=EPOCH)
        first = index.apply(epoch=EPOCH, revoke=("a",))
        self.assertFalse(first.changes)
        second = index.apply(epoch=EPOCH, revoke=("b",))
        self.assertEqual(second.changes["p"], (Liveness.LIVE, Liveness.DEAD))

    def test_conjunction_is_not_alternative_support(self):
        index = WarrantLivenessIndex({"p": WarrantProfile.of({"a", "b"})}, epoch=EPOCH)
        index.apply(epoch=EPOCH, revoke=("a",))
        self.assertIs(index.liveness("p", epoch=EPOCH), Liveness.DEAD)

    def test_multiple_blockers_require_all_to_be_restored(self):
        index = WarrantLivenessIndex({"p": WarrantProfile.of({"a", "b"})}, epoch=EPOCH)
        index.apply(epoch=EPOCH, revoke=("a", "b"))
        index.apply(epoch=EPOCH, reinstate=("a",))
        self.assertIs(index.liveness("p", epoch=EPOCH), Liveness.DEAD)
        index.apply(epoch=EPOCH, reinstate=("b",))
        self.assertIs(index.liveness("p", epoch=EPOCH), Liveness.LIVE)

    def test_mixed_swap_has_no_spurious_final_liveness_change(self):
        profile = WarrantProfile.of({"a"}, {"b"})
        index = WarrantLivenessIndex({"p": profile}, epoch=EPOCH, revoked=("a",))
        delta = index.apply(epoch=EPOCH, revoke=("b",), reinstate=("a",))
        self.assertFalse(delta.changes)
        self.assertEqual(delta.work.changed_clauses, 2)
        self.assertIs(index.liveness("p", epoch=EPOCH), Liveness.LIVE)

    def test_mixed_swap_inside_one_clause_uses_net_block_count(self):
        index = WarrantLivenessIndex({"p": WarrantProfile.of({"a", "b"})}, epoch=EPOCH, revoked=("a",))
        delta = index.apply(epoch=EPOCH, revoke=("b",), reinstate=("a",))
        self.assertEqual(delta.work.evidence_clause_visits, 2)
        self.assertEqual(delta.work.changed_clauses, 0)
        self.assertEqual(delta.work.clause_bound_visits, 0)
        self.assertIs(index.liveness("p", epoch=EPOCH), Liveness.DEAD)

    def test_overlapping_request_is_rejected_without_mutation(self):
        index = WarrantLivenessIndex({"p": WarrantProfile.of({"a"})}, epoch=EPOCH)
        before = dict(index.snapshot(epoch=EPOCH))
        with self.assertRaises(ValueError):
            index.apply(epoch=EPOCH, revoke=("a",), reinstate=("a",))
        self.assertEqual(dict(index.snapshot(epoch=EPOCH)), before)
        self.assertEqual(index.revoked_snapshot(epoch=EPOCH), frozenset())

    def test_input_failure_is_rejected_without_mutation(self):
        index = WarrantLivenessIndex({"p": WarrantProfile.of({"a"})}, epoch=EPOCH)
        def broken():
            yield "a"
            raise ValueError("broken iterable")
        with self.assertRaises(ValueError):
            index.apply(epoch=EPOCH, revoke=broken())
        self.assertIs(index.liveness("p", epoch=EPOCH), Liveness.LIVE)
        self.assertEqual(index.revoked_snapshot(epoch=EPOCH), frozenset())

    def test_unhashable_input_does_not_mutate(self):
        index = WarrantLivenessIndex({"p": WarrantProfile.of({"a"})}, epoch=EPOCH)
        with self.assertRaises(TypeError):
            index.apply(epoch=EPOCH, revoke=("a", []))
        self.assertIs(index.liveness("p", epoch=EPOCH), Liveness.LIVE)

    def test_stale_epoch_blocks_read_write_and_snapshots(self):
        index = WarrantLivenessIndex({"p": WarrantProfile.of({"a"})}, epoch=EPOCH)
        calls = (
            lambda: index.liveness("p", epoch="new"),
            lambda: index.apply(epoch="new", revoke=("a",)),
            lambda: index.snapshot(epoch="new"),
            lambda: index.revoked_snapshot(epoch="new"),
        )
        for call in calls:
            with self.assertRaises(CannotCheck):
                call()
        self.assertIs(index.liveness("p", epoch=EPOCH), Liveness.LIVE)

    def test_missing_identity_is_cannot_check_not_dead(self):
        index = WarrantLivenessIndex({}, epoch=EPOCH)
        with self.assertRaises(CannotCheck):
            index.liveness("missing", epoch=EPOCH)

    def test_idempotent_requests_have_no_incidence_work(self):
        index = WarrantLivenessIndex({"p": WarrantProfile.of({"a"})}, epoch=EPOCH)
        index.apply(epoch=EPOCH, revoke=("a",))
        delta = index.apply(epoch=EPOCH, revoke=("a",), reinstate=("not-revoked",))
        self.assertEqual(delta.work.changed_evidence, 0)
        self.assertEqual(delta.work.evidence_clause_visits, 0)
        self.assertFalse(delta.changes)

    def test_duplicate_input_consumption_is_charged(self):
        index = WarrantLivenessIndex({"p": WarrantProfile.of({"a"})}, epoch=EPOCH)
        delta = index.apply(epoch=EPOCH, revoke=("a", "a", "a"))
        self.assertEqual(delta.work.input_evidence_items, 3)
        self.assertEqual(delta.work.requested_evidence, 1)
        self.assertEqual(delta.work.changed_evidence, 1)
        self.assertEqual(delta.work.evidence_clause_visits, 1)

    def test_initial_duplicate_revocation_consumption_is_charged(self):
        index = WarrantLivenessIndex({}, epoch=EPOCH, revoked=("a", "a", "a"))
        self.assertEqual(index.size.initial_revocation_items, 3)

    def test_absent_evidence_is_retained_but_does_not_scan_profiles(self):
        index = WarrantLivenessIndex({"p": WarrantProfile.of({"a"})}, epoch=EPOCH)
        delta = index.apply(epoch=EPOCH, revoke=("absent",))
        self.assertEqual(delta.work.changed_evidence, 1)
        self.assertEqual(delta.work.evidence_clause_visits, 0)
        self.assertIn("absent", index.revoked_snapshot(epoch=EPOCH))
        index.apply(epoch=EPOCH, reinstate=("absent",))
        self.assertFalse(index.revoked_snapshot(epoch=EPOCH))

    def test_shared_clause_updates_all_consumers(self):
        profiles = {f"p:{i}": WarrantProfile.of({"shared"}) for i in range(200)}
        index = WarrantLivenessIndex(profiles, epoch=EPOCH)
        delta = index.apply(epoch=EPOCH, revoke=("shared",))
        self.assertEqual(index.size.distinct_clauses, 1)
        self.assertEqual(delta.work.evidence_clause_visits, 1)
        self.assertEqual(delta.work.clause_bound_visits, 400)
        self.assertEqual(len(delta.changes), 200)

    def test_unrelated_growth_does_not_add_update_incidence_work(self):
        small = WarrantLivenessIndex({"target": WarrantProfile.of({"target-e"})}, epoch=EPOCH)
        profiles = {"target": WarrantProfile.of({"target-e"})}
        profiles.update({f"unrelated:{i}": WarrantProfile.of({f"e:{i}"}) for i in range(5_000)})
        large = WarrantLivenessIndex(profiles, epoch=EPOCH)
        a = small.apply(epoch=EPOCH, revoke=("target-e",))
        b = large.apply(epoch=EPOCH, revoke=("target-e",))
        self.assertEqual(a.work, b.work)
        self.assertEqual(dict(a.changes), dict(b.changes))
        self.assertGreater(large.size.clause_bound_links, small.size.clause_bound_links)

    def test_caller_mapping_changes_do_not_rewrite_frozen_snapshot(self):
        profiles = {"p": WarrantProfile.of({"a"})}
        index = WarrantLivenessIndex(profiles, epoch=EPOCH)
        profiles["p"] = WarrantProfile.zero()
        self.assertIs(index.liveness("p", epoch=EPOCH), Liveness.LIVE)
        with self.assertRaises(CannotCheck):
            index.liveness("p", epoch="changed-field")
        rebuilt = WarrantLivenessIndex(profiles, epoch="changed-field")
        self.assertIs(rebuilt.liveness("p", epoch="changed-field"), Liveness.DEAD)

    def test_answers_and_delta_are_read_only(self):
        index = WarrantLivenessIndex({"p": WarrantProfile.of({"a"})}, epoch=EPOCH)
        snap = index.snapshot(epoch=EPOCH)
        with self.assertRaises(TypeError):
            snap["p"] = Liveness.DEAD
        delta = index.apply(epoch=EPOCH, revoke=("a",))
        with self.assertRaises(TypeError):
            delta.changes["p"] = (Liveness.LIVE, Liveness.LIVE)
        self.assertIs(snap["p"], Liveness.LIVE)

    def test_bad_constructor_inputs(self):
        for bad_epoch in (None, "", 42):
            with self.assertRaises(ValueError):
                WarrantLivenessIndex({}, epoch=bad_epoch)
        for bad_key in (None, "", 42):
            with self.assertRaises(ValueError):
                WarrantLivenessIndex({bad_key: WarrantProfile.one()}, epoch=EPOCH)
        with self.assertRaises(TypeError):
            WarrantLivenessIndex({"p": True}, epoch=EPOCH)

    def test_composed_profiles_match_direct_semantics(self):
        p = WarrantProfile.of({"a"}, {"b"}, complete=False)
        q = WarrantProfile((), (frozenset({"c"}),))
        profiles = {"meet": p.meet(q), "join": p.join(q)}
        for revoked in powerset(("a", "b", "c")):
            index = WarrantLivenessIndex(profiles, epoch=EPOCH, revoked=revoked)
            for key, profile in profiles.items():
                self.assertIs(index.liveness(key, epoch=EPOCH), profile.liveness(revoked))

    def test_random_mixed_batches_match_direct_evaluation(self):
        rng = random.Random(165_20260908)
        evidence = tuple(f"e:{i}" for i in range(12))
        profiles = {}
        for i in range(80):
            clauses = [{e for e in evidence if rng.random() < .2} for _ in range(rng.randrange(5))]
            profiles[f"p:{i}"] = WarrantProfile.of(*clauses, complete=(i % 3 != 0))
        index = WarrantLivenessIndex(profiles, epoch=EPOCH)
        revoked = set()
        for _ in range(300):
            target = {e for e in evidence if rng.random() < .5}
            index.apply(epoch=EPOCH, revoke=target - revoked, reinstate=revoked - target)
            self.assertEqual(dict(index.snapshot(epoch=EPOCH)), {
                key: profile.liveness(target) for key, profile in profiles.items()
            })
            revoked = target

    def test_planted_lower_only_incidence_mutant_is_detected(self):
        profile = WarrantProfile((), (frozenset({"u"}),))
        mutant = WarrantLivenessIndex({"p": profile}, epoch=EPOCH)
        mutant._incidence.clear()  # planted wrong optimization: index lower evidence only
        mutant.apply(epoch=EPOCH, revoke=("u",))
        self.assertIsNot(mutant.liveness("p", epoch=EPOCH), profile.liveness({"u"}))

    def test_planted_boolean_blocker_mutant_is_detected(self):
        profile = WarrantProfile.of({"a", "b"})
        mutant = WarrantLivenessIndex({"p": profile}, epoch=EPOCH, revoked=("a", "b"))
        mutant._blocked[0] = 1  # planted wrong optimization: a bit instead of blocker count
        mutant.apply(epoch=EPOCH, reinstate=("a",))
        self.assertIsNot(mutant.liveness("p", epoch=EPOCH), profile.liveness({"b"}))


if __name__ == "__main__":
    unittest.main()
