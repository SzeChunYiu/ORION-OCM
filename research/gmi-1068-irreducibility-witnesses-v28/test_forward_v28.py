"""Actual unchanged free process, separate value/order recoverability targets."""
from fractions import Fraction as F
from itertools import product
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from support_v28 import core, forward, oracle, check_recovery
COVERAGE = {}


class ForwardTests(unittest.TestCase):
    def test_registered_contexts_and_decoder_targets(self):
        rewards = tuple(product(tuple(map(F, range(3))), repeat=2))
        contexts = {}
        tags = 0
        for values in rewards:
            encoded = forward.forward_context(values)
            expected = {"n": 2, "m": 3, "admitted": (True, True),
                        "defined": (True, True), "values": tuple(map(int, values)),
                        "order": tuple(tuple(a <= b for b in range(3)) for a in range(3))}
            oracle.certify_context(encoded, expected, oracle.SINGLETONS, tuple(map(F, range(3))))
            oracle.certify(forward.values_view(encoded), tuple(zip(oracle.SINGLETONS, values)))
            oracle.certify(forward.order_view(encoded), oracle.order_view(values))
            for history in oracle.SINGLETONS:
                oracle.certify(forward.forward_observe(values, history), oracle.forward_tag(values, history))
                tags += 1
            contexts[values] = encoded
        counts = dict(forward_contexts=len(contexts), singleton_tags=tags,
                      unchanged_process_pairs=0, context_decoder_decisions=0,
                      order_decoder_decisions=0, context_recoverable_pairs=0,
                      order_recoverable_pairs=0)
        for left, right in product(rewards, repeat=2):
            process = (forward.process_observation(), forward.process_observation())
            oracle.certify(process[0], ((1, ((0, 0), (0, 0))), (1,), ((0,), (0,))))
            oracle.certify(process[0], process[1])
            counts["unchanged_process_pairs"] += 1
            for field, targets in (
                ("context", (tuple(zip(oracle.SINGLETONS, left)), tuple(zip(oracle.SINGLETONS, right)))),
                ("order", (oracle.order_view(left), oracle.order_view(right)))):
                counts[field + "_recoverable_pairs"] += check_recovery(self, process, targets)
                counts[field + "_decoder_decisions"] += 1
        self.assertEqual((len(contexts), tags, counts["unchanged_process_pairs"]), (9, 18, 81))
        self.assertEqual((counts["context_decoder_decisions"], counts["order_decoder_decisions"]), (81, 81))
        COVERAGE.update(counts)

    def test_named_free_history_and_allowed_boundaries(self):
        rewards = (F(1), F(0))
        histories = ((0, ()), (0, (0, 0)), (0, (0, 1)), (0, (1, 0)), (0, (1, 1)))
        for history in histories:
            oracle.certify(forward.forward_observe(rewards, history), ("UNDEFINED", None))
        left, right = forward.forward_context(rewards), forward.forward_context((F(0), F(1)))
        self.assertNotEqual(forward.values_view(left), forward.values_view(right))
        self.assertNotEqual(forward.order_view(left), forward.order_view(right))
        self.assertNotEqual(oracle.SINGLETONS[0], oracle.SINGLETONS[1])
        COVERAGE.update(forward_long_or_empty_queries=len(histories), designated_reversal_controls=1)

        ctx = core.contexts
        c = ctx.Context(3, 2, (True,) * 3, (True,) * 3, (0, 0, 0),
                        ((True, True), (False, True)))
        allowed = {(0, 1, 1), (1, 0, 0)}
        low, high = ctx.opposite(c, 0, 1, 0, 1, lambda v: v in allowed)
        oracle.certify((low.values, high.values), ((0, 1, 1), (1, 0, 0)))
        rejected = 0
        for context, callback in (
            (c, lambda v: len(set(v)) == 1),
            (c, lambda v: 1),
            (ctx.Context(3, 2, (True,) * 3, (True,) * 3, (0, 0, 0),
                         ((True, True), (True, True))), lambda v: True),
            (ctx.Context(3, 2, (False, True, True), (True,) * 3, (0, 0, 0), c.order), lambda v: True),
            (ctx.Context(3, 2, (True,) * 3, (False, True, True), (None, 0, 0), c.order), lambda v: True)):
            with self.assertRaises(ValueError):
                ctx.opposite(context, 0, 1, 0, 1, callback)
            rejected += 1
        self.assertFalse(check_recovery(self, (("collapsed",), ("collapsed",)), ((0,), (1,))))
        COVERAGE.update(allowed_positive_revivals=1, forward_premise_rejections=rejected,
                        collapsed_history_controls=1)

        import io
        import json
        from contextlib import redirect_stdout
        old = core.source("check_r2", "gmi-1068-r2-context-irreducibility-v1")
        stream = io.StringIO()
        with redirect_stdout(stream):
            old.main()
        receipt = json.loads(stream.getvalue())
        self.assertEqual(receipt["reward_worlds"], 9)
        self.assertEqual(receipt["optimal_sets"], {"a0": 3, "a1": 3, "tie": 3})
        self.assertEqual(receipt["scalarization_separators"], 2)
        self.assertEqual(len(receipt["hostiles"]), 6)
        COVERAGE["original_checker_replays"] = 1
