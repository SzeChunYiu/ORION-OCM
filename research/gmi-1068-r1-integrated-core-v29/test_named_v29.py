"""Whole shared ambient query interfaces and guarded typed comparisons."""
import unittest
from support_v29 import adapter, chain, core, named, oracle, exact
COVERAGE = {}
CODEC_COSTS = {"models": []}


class NamedTests(unittest.TestCase):
    def test_both_full_ambient_query_rosters(self):
        full = chain()
        restricted, inclusion = core.restrictions.wide_restriction(full, oracle.RESTRICTED)
        adapters = (adapter(full), named.NamedAdapter(restricted,7,
                    tuple(oracle.LABELS[i] for i in inclusion.arrow_map),oracle.OBJECTS))
        CODEC_COSTS['models'] = [dict(ambient_size=x.ambient_size,
            object_decoder=list(x.object_decoder),arrow_labels=list(x.arrow_labels),
            identities=list(x.named.identities),ambient_to_local=list(x.ambient_to_local),
            local_to_presented=list(x.local_to_presented),presented_to_local=list(x.presented_to_local))
            for x in adapters]
        roster = oracle.queries()
        self.assertEqual(len(roster),82)
        count = named_calls = typed_queries = typed_calls = guards = 0
        successes = failures = 0
        for current, included in zip(adapters,(tuple(range(6)),oracle.RESTRICTED)):
            for tree in roster:
                expected = oracle.response(tree,included)
                exact(self,named.named_response(current,tree),expected)
                exact(self,named.named_word_response(current,tree),expected)
                named_calls += 2; count += 1
                successes += expected is not None; failures += expected is None
                decoded = named.typed_query(current,tree)
                if oracle.present(tree,included):
                    expected_tree = oracle.typed_tree(tree,included)
                    exact(self,decoded,expected_tree)
                    expected_bundle = oracle.bundle(expected,included)
                    for response in (core.trees.typed_eval(current.category,decoded),
                                     core.trees.typed_word(current.category,decoded)):
                        exact(self,response,expected_bundle)
                        encoded = named.encode_bundle(current,response)
                        want = None if expected is None else (
                            oracle.OBJECTS.index(expected_bundle[0]),
                            oracle.OBJECTS.index(expected_bundle[1]),expected)
                        exact(self,encoded,want);typed_calls += 1
                    typed_queries += 1
                else:
                    self.assertIsNone(decoded); guards += 1
        self.assertEqual((count,named_calls,typed_queries,typed_calls,guards),(164,328,108,216,56))
        COVERAGE.update(named_queries=count,named_parent_evaluations=named_calls,
                        typed_queries=typed_queries,typed_parent_evaluations=typed_calls,
                        absent_guard_cases=guards,successful_named_queries=successes,
                        failed_named_queries=failures)

    def test_wide_inclusion_only_present_queries(self):
        full = chain(); source, inclusion = core.restrictions.wide_restriction(full,oracle.RESTRICTED)
        restricted = named.NamedAdapter(source,7,tuple(oracle.LABELS[i] for i in inclusion.arrow_map),oracle.OBJECTS)
        target = adapter(full)
        exact(self,restricted.named.identities,(6,0,4))
        count = 0
        for tree in oracle.queries():
            if not oracle.present(tree,oracle.RESTRICTED):continue
            left = named.typed_query(restricted,tree)
            right = named.typed_query(target,tree)
            exact(self,core.functors.map_tree(inclusion,left),right)
            exact(self,core.functors.map_response(inclusion,core.trees.typed_eval(source,left)),
                  core.trees.typed_eval(full,right))
            exact(self,named.named_response(restricted,tree),named.named_response(target,tree))
            count += 1
        controls = 0
        for label in (3,5):
            tree = ('arrow',label)
            self.assertIsNone(named.typed_query(restricted,tree))
            self.assertIsNone(named.named_response(restricted,tree))
            exact(self,named.named_response(target,tree),label);controls += 1
        for current in (restricted,target):
            self.assertIsNone(named.named_response(current,('arrow',2)));controls += 1
        self.assertEqual(count,40)
        COVERAGE.update(inclusion_comparisons=count,availability_controls=controls)
