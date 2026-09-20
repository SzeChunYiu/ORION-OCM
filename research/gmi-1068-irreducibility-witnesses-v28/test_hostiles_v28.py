"""Strict malformed interfaces and independently certified semantic corruptions."""
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as F
from types import SimpleNamespace
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from support_v28 import core, forward, reverse, recovery, scalar, oracle, check_recovery
COVERAGE = {}


class HostileTests(unittest.TestCase):
    def test_malformed_and_semantic_controls(self):
        rejected = 0
        def bad(call):
            nonlocal rejected
            with self.assertRaises(ValueError):
                call()
            rejected += 1
        rewards = (F(1), F(0))
        model = reverse.ReverseModel((True, False, False, True), (0, 1), (True, True))
        for x in (None, [], (F(0),), (0, F(1)), (True, F(1)), (0.0, F(1)),
                  (F(3), F(1)), (F(1, 2), F(1)), (F(0), F(1), F(2))):
            bad(lambda x=x: forward.forward_context(x))
            bad(lambda x=x: forward.forward_observe(x, (0, (0,))))
        histories = (None, [], (), (0,), (True, (0,)), (-1, ()), (2, ()),
                     (0, []), (0, (True,)), (0, (-1,)), (0, (4,)), (0, (0.0,)),
                     (0, (0, None)), (0, (0,), 1))
        for h in histories:
            bad(lambda h=h: forward.forward_observe(rewards, h))
            bad(lambda h=h: reverse.reverse_observe(model, h))
            bad(lambda h=h: reverse.generated_admitted(model, h))
        with self.assertRaisesRegex(ValueError, "strict index"):
            reverse.generated_admitted(model, (0, (2, True)))
        rejected += 1
        for admission in (None, [], (True,), (1, False, False, True),
                          (True, False, False, 1.0), (False, True, True, True)):
            bad(lambda admission=admission: reverse.ReverseModel(admission, (0, 1), (True, True)))
        for values in ([], (True, 1), (0.0, 1), (F(0), 1), (2, 0), (0,), (0, 1, 0)):
            bad(lambda values=values: reverse.ReverseModel((True,) * 4, values, (True, True)))
        for defined in ([], (1, True), (True, 1.0), (True,), (True, None)):
            bad(lambda defined=defined: reverse.ReverseModel((True,) * 4, (0, 1), defined))
        for bad_model in (None, (), SimpleNamespace(admission=(True,) * 4)):
            bad(lambda bad_model=bad_model: reverse.reverse_context(bad_model))
            bad(lambda bad_model=bad_model: reverse.views(bad_model))
        for vector in (None, [], (True,), (1,), (1.0,), (F(1), None)):
            bad(lambda vector=vector: scalar.dot(vector, (F(0),)))
            bad(lambda vector=vector: scalar.dominates(vector, (F(0),)))
            bad(lambda vector=vector: scalar.strict_dominates((F(0),), vector))
        bad(lambda: scalar.dot((F(1),), ()))
        for observations, targets in (([], ()), ((), []), ((0,), ()), ((0.0,), (0,)),
                                      (([],), (0,)), (({},), (0,)), ((set(),), (0,))):
            bad(lambda observations=observations, targets=targets: recovery.recovery(observations, targets))
        e = forward.forward_context(rewards)
        for roster in ([], ((True, (0,)), (0, (1,))), ((0, (0,)), (0, (0,))),
                       ((0, [0]), (0, (1,))), ((0, (False,)), (0, (1,)))):
            bad(lambda roster=roster: core.Encoded(e.context, roster, e.decoder))
        for decoder in ([], (F(0), F(1)), (0, F(1), F(2)), (F(0), F(0), F(2))):
            bad(lambda decoder=decoder: core.Encoded(e.context, e.roster, decoder))
        bad(lambda: core.Encoded(None, e.roster, e.decoder))
        bad(lambda: recovery.verify_recovery((), (), None))
        oracle.certify(scalar.dot((), ()), F(0))
        oracle.certify(scalar.dominates((), ()), True)
        oracle.certify(scalar.strict_dominates((), ()), False)
        self.assertTrue(check_recovery(self, (), ()))
        aliases = (None, True, 1, F(1), "1", (1,))
        self.assertTrue(check_recovery(self, aliases, tuple(range(len(aliases)))))
        self.assertEqual(len(recovery.recovery(aliases, tuple(range(6))).observation_codes), 6)
        malformed = rejected

        # Corrupt outputs coherently; constructor validity is not semantic correspondence.
        expected = oracle.context_fields(model.admission, model.state_values, model.state_defined)
        original = reverse.reverse_context(model)
        self.assertTrue(oracle.certify_context(original, expected, oracle.roster(), (F(0), F(1))))
        mutations = []
        for field in ("admitted", "defined", "values"):
            values = list(getattr(original.context, field))
            values[1] = not values[1] if field != "values" else 1 - values[1]
            mutations.append((field, tuple(values)))
        mutations.extend((("n", 29), ("m", 3), ("order", ((True, False), (True, True)))))
        semantic = 0
        for field, value in mutations:
            attrs = {name: getattr(original.context, name) for name in expected}
            attrs[field] = value
            corrupt = SimpleNamespace(context=SimpleNamespace(**attrs),
                                      roster=original.roster, decoder=original.decoder)
            with self.assertRaises(ValueError):
                oracle.certify_context(corrupt, expected, oracle.roster(), (F(0), F(1)))
            semantic += 1
        for roster, decoder in ((original.roster[::-1], original.decoder),
                                (original.roster, original.decoder[::-1])):
            corrupt = SimpleNamespace(context=original.context, roster=roster, decoder=decoder)
            with self.assertRaises(ValueError):
                oracle.certify_context(corrupt, expected, oracle.roster(), (F(0), F(1)))
            semantic += 1
        views = reverse.views(model)
        oracle.certify(views, oracle.expected_views(model.admission, model.state_values, model.state_defined))
        for name in views:
            corrupt = deepcopy(views); corrupt[name] = corrupt[name][1:]
            with self.assertRaises(ValueError):
                oracle.certify(corrupt, oracle.expected_views(model.admission, model.state_values, model.state_defined))
            semantic += 1
        inputs, targets = (True, 1, F(1)), (0, 1, 2)
        cert = recovery.recovery(inputs, targets)
        self.assertTrue(recovery.verify_recovery(inputs, targets, cert))
        for field, value in (("observation_codes", (1, True, F(1))),
                             ("target_codes", (0, 1, True)),
                             ("observation_labels", (0, 0, 0)), ("target_labels", (0, 1, True)),
                             ("decoder", {0: 1, 1: 1, 2: 2}), ("decoder", {0: 0}),
                             ("decoder", {0: 0, 1: 1, 2: 2, 3: 3})):
            corrupt = replace(cert, **{field: value})
            try:
                accepted = recovery.verify_recovery(inputs, targets, corrupt)
            except ValueError:
                accepted = False
            self.assertFalse(accepted)
            semantic += 1
        oracle.certify(forward.process_observation(), ((1, ((0, 0), (0, 0))), (1,), ((0,), (0,))))
        with self.assertRaises(ValueError):
            oracle.certify(forward.process_observation(), ((1, ((0, 0),)), (1,), ((0,),)))
        semantic += 1
        COVERAGE.update(malformed_input_rejections=malformed, semantic_certificate_baselines=4,
                        semantic_mutation_rejections=semantic, empty_or_type_separation_controls=5)
