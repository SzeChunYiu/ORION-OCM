"""Development controls, not protected outcomes or a proof of host correctness."""
from __future__ import annotations

import itertools
import unittest
from dataclasses import FrozenInstanceError, replace

from authority_router import (
    Eligibility, Envelope, Kind, Preflight, Query, Route, RouteIndex, Status,
)


Q = Query("x", "lab", "FORMAL", "snapshot-0")
E = Envelope(1000, 10000)


def route(name="r", keys=("x",), work=1, size=10, kind=Kind.ANSWER):
    return Route(name, frozenset(keys), work, size, f"contract:{name}", kind)


def allow(_route, _query):
    return Eligibility.APPROVED


def reference(routes, query, check, envelope, priority):
    """Independent full scan + sort, with no index/production selector calls."""
    candidates = [r for r in routes if query.key in r.query_keys]
    if not candidates:
        return Status.NO_QUERY_MATCH, None
    affordable = [r for r in candidates if r.work_estimate <= envelope.work
                  and r.active_bytes_estimate <= envelope.active_bytes]
    labels = [(r, check(r, query)) for r in affordable]
    approved = [r for r, label in labels if label is Eligibility.APPROVED]
    if approved:
        if priority == "work_first":
            approved.sort(key=lambda r: (r.work_estimate, r.active_bytes_estimate, r.route_id))
        else:
            approved.sort(key=lambda r: (r.active_bytes_estimate, r.work_estimate, r.route_id))
        return Status.SELECTED, approved[0]
    if any(label is Eligibility.UNKNOWN for _, label in labels):
        return Status.UNRESOLVED, None
    return (Status.ENVELOPE if not affordable else Status.NO_ELIGIBLE), None


class RoutingTests(unittest.TestCase):
    def test_authority_before_ranking_has_negative_twin(self):
        cheap, valid = route("cheap", work=0), route("valid", work=10)
        def host(r, _q):
            return Eligibility.REJECTED if r == cheap else Eligibility.APPROVED
        result = RouteIndex((cheap, valid)).select(Q, host, E)
        self.assertEqual(result.route, valid)
        self.assertNotEqual(min((cheap, valid), key=lambda r: r.work_estimate), result.route)
        self.assertEqual(result.work.rejected, 1)

    def test_incomparable_summaries_are_not_ordered_by_size(self):
        sx = route("summary-x", ("x",), size=45)
        sy = route("summary-y", ("y",), size=54)
        full = route("full", ("x", "y", "xor"), size=715, work=20)
        index = RouteIndex((sx, sy, full))
        self.assertEqual(index.select(Q, allow, E).route, sx)
        self.assertEqual(index.select(replace(Q, key="y"), allow, E).route, sy)
        self.assertEqual(index.select(replace(Q, key="xor"), allow, E).route, full)

    def test_refine_is_not_an_answer(self):
        refine = route(kind=Kind.REFINE)
        selected = RouteIndex((refine,)).select(Q, allow, E)
        self.assertEqual(selected.status, Status.SELECTED)
        self.assertIs(selected.route.kind, Kind.REFINE)

    def test_unknown_is_not_false_or_approved(self):
        index = RouteIndex((route(),))
        self.assertEqual(index.select(Q, lambda r, q: Eligibility.UNKNOWN, E).status, Status.UNRESOLVED)
        self.assertEqual(index.select(Q, lambda r, q: Eligibility.REJECTED, E).status, Status.NO_ELIGIBLE)

    def test_known_route_can_survive_unknown_compact_alternative(self):
        a, b = route("a"), route("b", work=9)
        out = RouteIndex((a, b)).select(
            Q, lambda r, q: Eligibility.UNKNOWN if r == a else Eligibility.APPROVED, E)
        self.assertEqual(out.route, b)
        self.assertEqual(out.work.unknown, 1)

    def test_scope_and_formal_empirical_boundary_are_host_checked(self):
        def host(_r, q):
            return (Eligibility.APPROVED if q.context == "lab" and q.authority_kind == "FORMAL"
                    else Eligibility.REJECTED)
        index = RouteIndex((route(),))
        self.assertEqual(index.select(Q, host, E).status, Status.SELECTED)
        self.assertEqual(index.select(replace(Q, authority_kind="EMPIRICAL"), host, E).status, Status.NO_ELIGIBLE)
        self.assertEqual(index.select(replace(Q, context="outside"), host, E).status, Status.NO_ELIGIBLE)

    def test_live_alternative_support_and_withdrawal(self):
        # Fixture only: production must call OCM's existing support/authority code.
        revoked: set[str] = set()
        def host(_r, _q):
            alternatives = (frozenset(("a", "b")), frozenset(("c",)))
            return (Eligibility.APPROVED if any(not (w & revoked) for w in alternatives)
                    else Eligibility.REJECTED)
        index = RouteIndex((route(),))
        selected = index.select(Q, host, E)
        revoked.add("a")
        self.assertEqual(index.preflight(selected, Q, host), Preflight.READY)
        revoked.add("c")
        self.assertEqual(index.preflight(selected, Q, host), Preflight.REJECTED)
        self.assertEqual(index.select(Q, host, E).status, Status.NO_ELIGIBLE)
        revoked.remove("c")
        self.assertEqual(index.select(Q, host, E).status, Status.SELECTED)

    def test_stale_snapshot_refuses_even_if_callback_approves(self):
        index = RouteIndex((route(),))
        selected = index.select(Q, allow, E)
        self.assertEqual(index.preflight(selected, replace(Q, snapshot="snapshot-1"), allow), Preflight.STALE)

    def test_changed_query_context_or_authority_refuses(self):
        index = RouteIndex((route(),))
        selected = index.select(Q, allow, E)
        for q in (replace(Q, key="y"), replace(Q, context="other"),
                  replace(Q, authority_kind="EMPIRICAL")):
            self.assertEqual(index.preflight(selected, q, allow), Preflight.STALE)

    def test_replaced_contract_or_removed_route_refuses(self):
        r = route()
        selected = RouteIndex((r,)).select(Q, allow, E)
        changed = RouteIndex((replace(r, contract_ref="contract:v2"),))
        self.assertEqual(changed.preflight(selected, Q, allow), Preflight.CHANGED)
        self.assertEqual(RouteIndex(()).preflight(selected, Q, allow), Preflight.CHANGED)

    def test_callback_error_and_non_enum_fail_closed(self):
        def broken(_r, _q):
            raise RuntimeError("checker unavailable")
        index = RouteIndex((route(),))
        good = index.select(Q, allow, E)
        for fn in (broken, lambda r, q: True, lambda r, q: "APPROVED", lambda r, q: None):
            self.assertEqual(index.select(Q, fn, E).status, Status.CHECK_ERROR)
            self.assertEqual(index.preflight(good, Q, fn), Preflight.CHECK_ERROR)

    def test_preflight_unknown_and_no_selection(self):
        index = RouteIndex((route(),))
        good = index.select(Q, allow, E)
        self.assertEqual(index.preflight(good, Q, lambda r, q: Eligibility.UNKNOWN), Preflight.UNKNOWN)
        bad = index.select(replace(Q, key="absent"), allow, E)
        self.assertEqual(index.preflight(bad, Q, allow), Preflight.NO_SELECTION)

    def test_estimated_envelope_does_not_call_expensive_ineligible_work(self):
        index = RouteIndex((route(work=3, size=30),))
        def must_not_call(_r, _q):
            self.fail("outside-envelope candidate invoked eligibility")
        for env in (Envelope(2, 30), Envelope(3, 29)):
            out = index.select(Q, must_not_call, env)
            self.assertEqual(out.status, Status.ENVELOPE)
            self.assertEqual(out.work.eligibility_calls, 0)
        self.assertEqual(index.select(Q, allow, Envelope(3, 30)).status, Status.SELECTED)

    def test_resource_priorities_are_explicit_not_one_global_richness_order(self):
        work_small = route("work", work=1, size=100)
        bytes_small = route("bytes", work=10, size=1)
        index = RouteIndex((work_small, bytes_small))
        self.assertEqual(index.select(Q, allow, E, priority="work_first").route, work_small)
        self.assertEqual(index.select(Q, allow, E, priority="bytes_first").route, bytes_small)

    def test_exact_tie_is_input_order_independent(self):
        a, b = route("a"), route("b")
        for routes in ((a, b), (b, a)):
            self.assertEqual(RouteIndex(routes).select(Q, allow, E).route, a)

    def test_candidate_cap_refuses_instead_of_claiming_best_from_prefix(self):
        index = RouteIndex((route("a", work=10), route("b", work=0)))
        limited = index.select(Q, allow, E, max_candidates=1)
        self.assertEqual(limited.status, Status.LIMIT)
        self.assertIsNone(limited.route)
        self.assertEqual(limited.work.routes_inspected, 0)
        self.assertEqual(index.select(Q, allow, E, max_candidates=2).route.route_id, "b")

    def test_input_collections_are_detached_and_read_only(self):
        keys = {"x"}
        r = Route("r", keys, 1, 10, "contract:r")
        rows = [r]
        index = RouteIndex(rows)
        keys.add("y")
        rows.clear()
        self.assertEqual(index.select(Q, allow, E).route, r)
        self.assertEqual(index.select(replace(Q, key="y"), allow, E).status, Status.NO_QUERY_MATCH)
        with self.assertRaises(FrozenInstanceError):
            r.work_estimate = 0
        with self.assertRaises(TypeError):
            index._by_id["r"] = route("other")

    def test_bad_descriptors_and_duplicate_ids_rejected(self):
        for cost in (-1, True, 1.0, None):
            with self.assertRaises(ValueError):
                route(work=cost)
        with self.assertRaises(ValueError):
            Route("r", "xy", 1, 1, "contract")
        with self.assertRaises(ValueError):
            route(keys=())
        with self.assertRaises(ValueError):
            route(kind="ANSWER")
        with self.assertRaises(ValueError):
            RouteIndex((route(), route()))
        with self.assertRaises(ValueError):
            Query("x", "lab", "FORMAL", "")
        with self.assertRaises(ValueError):
            Envelope(-1, 4)
        with self.assertRaises(ValueError):
            RouteIndex((route(),)).select(Q, allow, E, priority="magical")
        with self.assertRaises(ValueError):
            RouteIndex((route(),)).select(Q, allow, E, max_candidates=-1)

    def test_unrelated_growth_changes_build_cost_not_query_candidate_visits(self):
        relevant = (route("a"), route("b", work=2))
        for n in (0, 100, 10000):
            distractors = tuple(route(f"d{i}", ("other",)) for i in range(n))
            index = RouteIndex(relevant + distractors)
            out = index.select(Q, allow, E)
            self.assertEqual(out.route, relevant[0])
            self.assertEqual(out.work.routes_inspected, 2)
            self.assertEqual(out.work.eligibility_calls, 2)
            self.assertEqual(index.index_references, n + 2)  # Preprocessing is not free.
            self.assertEqual(len(index.routes), n + 2)

    def test_exhaustive_index_equivalence_to_full_scan(self):
        rows = (route("a", ("x",), work=1, size=4),
                route("b", ("y",), work=2, size=3),
                route("c", ("x", "y"), work=3, size=2),
                route("d", ("x", "y", "xor"), work=4, size=1, kind=Kind.REFINE))
        index = RouteIndex(rows)
        cases = 0
        for labels in itertools.product(tuple(Eligibility), repeat=4):
            outcomes = dict(zip((r.route_id for r in rows), labels))
            def host(r, q):
                return outcomes[r.route_id]
            for key, envelope, priority in itertools.product(
                    ("x", "y", "xor", "absent"),
                    (Envelope(10, 10), Envelope(2, 4), Envelope(0, 0)),
                    ("work_first", "bytes_first")):
                query = replace(Q, key=key)
                got = index.select(query, host, envelope, priority=priority)
                expected = reference(rows, query, host, envelope, priority)
                self.assertEqual((got.status, got.route), expected)
                cases += 1
        self.assertEqual(cases, 1944)


if __name__ == "__main__":
    unittest.main()
