"""Hostile tests for the G3.2 scoped failure-memory study.

Two of this study's own drafts were wrong in ways that would have produced a
publishable-looking negative from nothing, and both have tests here:

1. the first population never reached the length bound, so ZERO nogoods were
   recorded and FAILURE_MEMORY_NOT_USEFUL was returned from a run in which no
   failure occurred;
2. soundness was defined as "every row solved", which called the correct arm
   defective, because at the first budget every task is genuinely unreachable.

The third error was summing storage bits with prefix extensions, which is the
post-hoc scalarization #165 forbids.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent


def _load():
    spec = importlib.util.spec_from_file_location("g32", HERE / "experiment.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


E = _load()


class Keys(unittest.TestCase):
    """#165 forbids task-ID blacklist shortcuts by name."""

    def test_a_key_is_structural_and_carries_no_task_identity(self):
        store = E.FailureStore(scoped=True)
        key = store.key(("inc", "dec"), 5)
        self.assertEqual(key, (("inc", "dec"), 5))
        for part in key:
            self.assertNotIsInstance(part, dict)

    def test_the_store_signature_cannot_receive_a_task_at_all(self):
        import inspect
        for method in (E.FailureStore.key, E.FailureStore.blocked, E.FailureStore.record):
            names = set(inspect.signature(method).parameters)
            self.assertFalse(names & {"task", "fingerprint", "coefficients"},
                             f"{method.__name__} can see task identity")

    def test_an_unscoped_key_drops_the_budget_which_is_the_whole_defect(self):
        self.assertEqual(E.FailureStore(scoped=False).key(("inc",), 5), (("inc",),))
        self.assertEqual(E.FailureStore(scoped=True).key(("inc",), 5), (("inc",), 5))


class Reopening(unittest.TestCase):
    def test_a_scoped_store_reopens_stale_entries_on_a_regime_change(self):
        store = E.FailureStore(scoped=True)
        store.record(("inc",), 5)
        store.regime_change(5, 6)
        self.assertFalse(store.blocked(("inc",), 6))
        self.assertEqual(store.reopenings, 1)

    def test_an_unscoped_store_cannot_reopen_and_keeps_a_stale_block(self):
        """It has no budget on its entries, so it has no way to know which are
        still sound. This is the mechanism behind the unsoundness."""
        store = E.FailureStore(scoped=False)
        store.record(("inc",), 5)
        store.regime_change(5, 6)
        self.assertTrue(store.blocked(("inc",), 6))
        self.assertEqual(store.reopenings, 0)

    def test_maintenance_is_charged_even_when_nothing_is_reopened(self):
        store = E.FailureStore(scoped=False)
        store.record(("inc",), 5)
        store.regime_change(5, 6)
        self.assertGreater(store.maintenance, 0)


class Accounting(unittest.TestCase):
    def test_the_arm_reports_a_raw_vector_and_never_a_summed_total(self):
        """Bits are not extensions. Adding them is the post-hoc scalarization
        #165 forbids, and an earlier draft did exactly that."""
        source = (HERE / "experiment.py").read_text()
        self.assertIn("RAW VECTOR, never summed", source)
        self.assertNotIn("net_work", source)
        self.assertNotIn("memory_overhead", source)

    def test_pareto_needs_no_price_and_reports_incomparability(self):
        a = {"extensions": 1, "lookups": 9}
        b = {"extensions": 9, "lookups": 1}
        self.assertEqual(E.pareto(a, b), "INCOMPARABLE_WITHOUT_A_PRICE")
        self.assertEqual(E.pareto({"x": 1}, {"x": 2}), "A_DOMINATES")
        self.assertEqual(E.pareto({"x": 2}, {"x": 1}), "B_DOMINATES")
        self.assertEqual(E.pareto({"x": 1}, {"x": 1}), "EQUAL")

    def test_a_scalar_exists_only_against_declared_prices(self):
        self.assertEqual(set(E.PRICES), {"extensions", "lookups", "maintenance",
                                         "storage_bits"})
        self.assertEqual(E.value({"extensions": 2, "lookups": 0, "maintenance": 0,
                                  "storage_bits": 8}), 2 * 1.0 + 8 * 0.125)


class Search(unittest.TestCase):
    def test_a_blocked_prefix_costs_a_lookup_but_not_an_extension(self):
        """If a block still charged an extension the memory could never win, and
        if it charged no lookup the memory would be free. Both would be wrong."""
        source = (HERE / "experiment.py").read_text()
        body = source[source.index("def search("):source.index("def run_arm(")]
        self.assertLess(body.index("store.blocked"), body.index("extensions += 1"))
        self.assertIn("continue", body)


class Terminals(unittest.TestCase):
    def _doc(self, base, nogood, scoped, entries=10, reopenings=5):
        def arm(name, vector, solved_keys, extra=None):
            row = {"arm": name, "vector": vector, "solved_keys": solved_keys,
                   "tasks_solved": len(solved_keys), "rows_total": 4,
                   "charged": {"entries": entries, "reopenings": reopenings,
                               "hits": 0,
                               "lookups": vector["lookups"],
                               "maintenance": vector["maintenance"],
                               "storage_bits": vector["storage_bits"]}}
            row.update(extra or {})
            return row
        arms = {"NO_MEMORY": arm("NO_MEMORY", base, [("a", 6), ("b", 6)]),
                "NOGOOD": arm("NOGOOD", nogood, []),
                "SCOPED_NOGOOD": arm("SCOPED_NOGOOD", scoped, [("a", 6), ("b", 6)])}
        # Keep the synthetic doc coherent with Proposition 1: a hit is exactly one
        # extension the memoryless arm paid and the scoped arm did not.
        arms["SCOPED_NOGOOD"]["charged"]["hits"] = base["extensions"] - scoped["extensions"]
        reference = set(map(tuple, arms["NO_MEMORY"]["solved_keys"]))
        for row in arms.values():
            got = set(map(tuple, row["solved_keys"]))
            row["sound"] = got == reference
            row["lost_to_memory"] = sorted(reference - got)
        return {"arms": arms}

    def _v(self, ext, look=0, maint=0, bits=0):
        return {"extensions": ext, "lookups": look, "maintenance": maint,
                "storage_bits": bits}

    def test_a_run_that_recorded_no_failure_cannot_report_a_negative(self):
        """The exact vacuous case an earlier draft produced."""
        doc = self._doc(self._v(100), self._v(100), self._v(100), entries=0, reopenings=0)
        out = E.verdict(doc)
        self.assertEqual(out["terminal"], "CANNOT_CHECK_NO_FAILURE_WAS_EVER_RECORDED")
        self.assertIn("would be vacuous", out["terminal_reason"])

    def test_an_unsound_scoped_store_is_a_harness_defect_not_a_result(self):
        doc = self._doc(self._v(100), self._v(50), self._v(50))
        doc["arms"]["SCOPED_NOGOOD"]["solved_keys"] = []
        doc["arms"]["SCOPED_NOGOOD"]["sound"] = False
        doc["arms"]["SCOPED_NOGOOD"]["lost_to_memory"] = [("a", 6)]
        out = E.verdict(doc)
        self.assertEqual(out["terminal"], "CANNOT_CHECK_SCOPED_MEMORY_UNSOUND_HARNESS_DEFECT")

    def test_the_useful_terminal_requires_both_payback_and_a_scope_falsifier(self):
        doc = self._doc(self._v(1000), self._v(100), self._v(200, look=10))
        out = E.verdict(doc)
        self.assertEqual(out["terminal"], "FAILURE_MEMORY_USEFUL_AT_SCOPE")
        self.assertIn("demonstrated by a falsifier", out["terminal_reason"])

    def test_payback_without_a_scope_falsifier_says_scope_is_untested(self):
        doc = self._doc(self._v(1000), self._v(100), self._v(200, look=10))
        doc["arms"]["NOGOOD"]["solved_keys"] = [("a", 6), ("b", 6)]
        doc["arms"]["NOGOOD"]["sound"] = True
        out = E.verdict(doc)
        self.assertEqual(out["terminal"], "FAILURE_MEMORY_USEFUL_BUT_SCOPE_UNTESTED")

    def test_the_negative_does_not_claim_scope_is_unnecessary(self):
        """The load-bearing separation: the memory can fail to pay while scope is
        still demonstrably required. Conflating those would be the easy error."""
        doc = self._doc(self._v(100), self._v(50), self._v(90, look=500))
        out = E.verdict(doc)
        self.assertEqual(out["terminal"], "FAILURE_MEMORY_NOT_USEFUL")
        self.assertIn("NOT a finding that scope is unnecessary", out["terminal_reason"])
        self.assertTrue(out["scope_is_load_bearing"])

    def test_the_break_even_lookup_price_is_the_deciding_coordinate(self):
        doc = self._doc(self._v(1000), self._v(100), self._v(600, look=800))
        out = E.verdict(doc)
        self.assertAlmostEqual(out["break_even_lookup_price"], 400 / 800)
        self.assertIn("a real system can check", out["break_even_lookup_reading"])


class GuardExactness(unittest.TestCase):
    """The probe-skipping guard must not change any arm's behaviour.

    This class exists because an earlier guard DID change behaviour and the study
    did not notice. It skipped the probe whenever ``len(prefix) < budget``, on the
    argument that entries only ever live at depth ``budget + 1``. That is true of
    the scoped store, whose regime change purges other budgets, and false of the
    unscoped store, whose defining defect is that it keeps entries derived under a
    SMALLER budget -- exactly the entries that live at a shallower depth than the
    current budget implies. The unscoped store was therefore never probed where
    its stale entries sit, stopped losing solutions, and the scope falsifier went
    quiet while every other number improved. Nothing failed; the finding just
    disappeared. These tests make that failure mode loud.
    """

    def test_a_shorter_candidate_than_any_entry_is_a_guaranteed_miss(self):
        store = E.FailureStore(scoped=True)
        self.assertFalse(store.may_match(("a",)))          # empty store
        store.record(("a", "b", "c"), 2)
        self.assertFalse(store.may_match(("a",)))
        self.assertFalse(store.may_match(("a", "b")))
        self.assertTrue(store.may_match(("a", "b", "c")))
        self.assertTrue(store.may_match(("a", "b", "c", "d")))

    def test_the_guard_tracks_a_stale_shallower_entry_in_an_unscoped_store(self):
        """The precise case the old guard got wrong."""
        store = E.FailureStore(scoped=False)
        store.record(("a",) * 6, 5)          # recorded under budget 5
        store.regime_change(5, 6)            # unscoped: cannot reopen, entry stays
        # Under budget 6 a depth-6 candidate is feasible, and this is where the
        # stale entry wrongly blocks it. The guard must still allow the probe.
        self.assertTrue(store.may_match(("a",) * 6))
        self.assertTrue(store.blocked(("a",) * 6, 6))

    def test_the_guard_never_suppresses_a_probe_that_would_have_hit(self):
        """Exhaustive: for every stored entry, the guard admits its own probe."""
        for scoped in (True, False):
            store = E.FailureStore(scoped=scoped)
            for depth in (2, 4, 7):
                store.record(("t",) * depth, 3)
            for depth in range(1, 10):
                candidate = ("t",) * depth
                if store.key(candidate, 3) in store.entries:
                    self.assertTrue(store.may_match(candidate),
                                    f"guard suppressed a real hit at depth {depth}")

    def test_regime_change_recomputes_the_guard_after_reopening(self):
        store = E.FailureStore(scoped=True)
        store.record(("a", "b"), 1)
        store.record(("a", "b", "c"), 2)
        self.assertEqual(store.min_key_len, 2)
        store.regime_change(1, 2)            # drops the budget-1 entry
        self.assertEqual(store.min_key_len, 3)
        self.assertFalse(store.may_match(("a", "b")))


class Proposition1(unittest.TestCase):
    """The negative is an identity, not a price verdict."""

    def test_the_statement_names_its_own_escape_condition(self):
        for phrase in ("net = H - P - M", "goal-independent", "prunes a SUBTREE",
                       "escapes the proposition"):
            self.assertIn(phrase, E.PROPOSITION_1)

    def test_a_hit_saves_exactly_one_extension_so_net_cannot_be_positive(self):
        doc = self._run
        prop = doc["verdict"]["proposition_1"]
        self.assertTrue(prop["extensions_saved_equals_hits"],
                        "a hit that saved more or less than one extension would "
                        "break the proposition's step (2)")
        self.assertTrue(prop["identity_holds"])
        self.assertTrue(prop["bound_net_le_zero"])
        self.assertLessEqual(prop["hits"], prop["probes"])

    def test_the_negative_terminal_cites_the_identity_not_the_prices(self):
        reason = self._run["verdict"]["terminal_reason"]
        self.assertIn("Proposition 1", reason)
        self.assertIn("structural", reason)

    def test_the_scope_falsifier_still_fires_alongside_the_proposition(self):
        v = self._run["verdict"]
        self.assertTrue(v["scoped_is_sound"])
        self.assertFalse(v["unscoped_is_sound"])
        self.assertTrue(v["scope_is_load_bearing"])

    @classmethod
    def setUpClass(cls):
        cls._run = E.run(n_tasks=6)
        cls._run["verdict"] = E.verdict(cls._run)


if __name__ == "__main__":
    unittest.main(verbosity=2)
