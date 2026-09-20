"""Independent actual categories, generated histories and four recovery views."""
from fractions import Fraction as F
from itertools import product
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from support_v28 import core, reverse, oracle, check_recovery
COVERAGE = {}


class ReverseTests(unittest.TestCase):
    def test_registered_models_tags_and_decoders(self):
        histories = oracle.roster()
        self.assertEqual(len(histories), 30)
        models = {}
        counts = dict(reverse_contexts=0, reverse_tag_observations=0, reverse_model_pairs=0,
                      raw_admission_checks=0, primitive_roundtrips=0)
        for name in ("weak_state", "active_domain", "tagged", "domain_signature"):
            counts[name + "_decoder_decisions"] = 0
            counts[name + "_recoverable_pairs"] = 0
        for mask in oracle.masks():
            canonical = reverse.ReverseModel(mask, (0, 1), (True, True))
            expected = oracle.thin_data(mask)
            self.assertIs(type(canonical.category), core.categories.Typed)
            self.assertIs(type(canonical.category.table), core.partial.Table)
            self.assertEqual(canonical.category.object_count, 2)
            for name in ("source", "target", "identities"):
                oracle.certify(getattr(canonical.category, name), expected[name])
            oracle.certify(canonical.category.table.rows, expected["rows"])
            for name in ("ambient_to_local", "local_to_ambient"):
                oracle.certify(getattr(canonical, name), expected[name])
            oracle.certify((canonical.graph.vertices, canonical.graph.edges), (2, oracle.EDGES))
            recovered = core.history.decode_admission(
                canonical.graph, lambda h: reverse.generated_admitted(canonical, h))
            oracle.certify(recovered, mask)
            counts["primitive_roundtrips"] += 1
            for history in histories:
                oracle.certify(reverse.generated_admitted(canonical, history),
                               all(mask[e] for e in history[1]))
                counts["raw_admission_checks"] += 1
            for values, defined in product(product(range(2), repeat=2),
                                           product((False, True), repeat=2)):
                model = reverse.ReverseModel(mask, values, defined)
                encoded = reverse.reverse_context(model)
                oracle.certify_context(encoded, oracle.context_fields(mask, values, defined),
                                       histories, (F(0), F(1)))
                expected_views = oracle.expected_views(mask, values, defined)
                oracle.certify(reverse.views(model), expected_views)
                for index, history in enumerate(histories):
                    tag = oracle.reverse_tag(mask, values, defined, history)
                    oracle.certify(reverse.reverse_observe(model, history), tag)
                    oracle.certify(encoded.observe(index), tag)
                    counts["reverse_tag_observations"] += 1
                models[mask, values, defined] = expected_views
                counts["reverse_contexts"] += 1
        for values, defined in product(product(range(2), repeat=2),
                                       product((False, True), repeat=2)):
            for a, b in product(oracle.masks(), repeat=2):
                counts["reverse_model_pairs"] += 1
                for name in ("weak_state", "active_domain", "tagged", "domain_signature"):
                    observations = (models[a, values, defined][name], models[b, values, defined][name])
                    counts[name + "_recoverable_pairs"] += check_recovery(self, observations, (a, b))
                    counts[name + "_decoder_decisions"] += 1
        self.assertEqual((counts["reverse_contexts"], counts["reverse_tag_observations"],
                          counts["reverse_model_pairs"]), (64, 1920, 256))
        self.assertEqual((counts["raw_admission_checks"], counts["primitive_roundtrips"]), (120, 4))
        COVERAGE.update(counts)

    def test_named_observation_boundaries(self):
        a, b = oracle.masks()[:2]
        left = reverse.ReverseModel(a, (0, 1), (True, True))
        right = reverse.ReverseModel(b, (0, 1), (True, True))
        lv, rv = reverse.views(left), reverse.views(right)
        oracle.certify(lv["weak_state"], rv["weak_state"])
        h = (0, (1,))
        oracle.certify(reverse.reverse_observe(left, h), ("ILLEGAL", None))
        oracle.certify(reverse.reverse_observe(right, h), ("VALUE", F(1)))
        self.assertFalse(check_recovery(self, (lv["weak_state"], rv["weak_state"]), (a, b)))
        self.assertTrue(check_recovery(self, (lv["tagged"], rv["tagged"]), (a, b)))
        self.assertTrue(check_recovery(self, (lv["domain_signature"], rv["domain_signature"]), (a, b)))
        empty_left = reverse.ReverseModel(a, (0, 1), (False, False))
        empty_right = reverse.ReverseModel(b, (0, 1), (False, False))
        el, er = reverse.views(empty_left), reverse.views(empty_right)
        oracle.certify(el["active_domain"], er["active_domain"])
        self.assertFalse(check_recovery(self, (el["active_domain"], er["active_domain"]), (a, b)))
        self.assertTrue(check_recovery(self, (el["tagged"], er["tagged"]), (a, b)))
        collapsed = tuple(tuple((h, None) for h, _ in view["tagged"]) for view in (el, er))
        self.assertFalse(check_recovery(self, collapsed, (a, b)))
        graph = core.history.Graph(2, oracle.EDGES)
        callback = lambda h: len(h[1]) <= 1
        oracle.certify(core.history.decode_admission(graph, callback), (True,) * 4)
        composite = (0, (1, 2))
        self.assertFalse(callback(composite))
        self.assertTrue(core.history.admitted(graph, (True,) * 4, composite))
        reduced = tuple(tuple((h, yes) for h, yes in v["domain_signature"] if len(h[1]) == 0)
                        for v in (lv, rv))
        self.assertFalse(check_recovery(self, reduced, (a, b)))
        oracle.certify(core.history.decode_admission(core.history.Graph(0, ()), lambda h: True), ())
        self.assertTrue(check_recovery(self, (), ()))
        alg = core.algebra
        self.assertEqual(alg.fold(alg.c4(), (1, 1)), 2)
        self.assertEqual(alg.fold(alg.v4(), (1, 1)), 0)
        self.assertTrue(all(type(x) is int for m in (alg.c4(), alg.v4()) for row in m.table for x in row))
        COVERAGE.update(reverse_named_boundary_controls=10, same_admission_composition_controls=1)
