"""Flat-antichain books versus operational Boolean-program wrappers."""
from fractions import Fraction as F
from itertools import combinations, product
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle_v18 as oracle
import prefix_v18 as core
COVERAGE = {}


def bits(word):
    return tuple(symbol == '1' for symbol in word)


def book(entries):
    return core.Book(2,tuple((bits(word),value) for word,value in entries))


class PrefixTests(unittest.TestCase):
    def test_exhaustive_finite_books_and_wrappers(self):
        counts = dict(prefix_domains=0,finite_books=0,wrapper_cases=0,wrapper_decode_queries=0,
                      shortest_output_equations=0,wrapper_profile_bounds=0,kraft_checks=0)
        domains = set()
        profiles = oracle.profiles(2)
        for entries in oracle.books(3):
            domains.add(tuple(word for word,_ in entries))
            base = book(entries)
            self.assertEqual(core.shortest(base),oracle.lengths(entries))
            base_weights = oracle.output_weights(entries)
            self.assertEqual(core.weights(base),base_weights)
            program_mass = sum((F(1,2**len(word)) for word,_ in entries),F(0))
            self.assertLessEqual(sum(base_weights.values(),F(0)),program_mass)
            self.assertLessEqual(program_mass,1)
            counts['finite_books'] += 1
            counts['kraft_checks'] += 1
            for target,padding in product(range(2),(2,3,4)):
                wrapped = core.Wrapped(base,target,padding)
                literal = (('0',target),)+tuple(('1'*padding+p,v) for p,v in entries)
                expected_weights = oracle.output_weights(literal)
                self.assertEqual(core.shortest(wrapped),oracle.lengths(literal))
                self.assertEqual(core.weights(wrapped),expected_weights)
                compiled = core.compiled(wrapped)
                self.assertEqual({(''.join('1' if b else '0' for b in p),v)
                                  for p,v in compiled.entries},set(literal))
                queries = {'','0','00','01'} | {'1'*n for n in range(padding)} | {
                    '1'*padding+p for p in oracle.words(3)}
                for program in queries:
                    expected = oracle.wrapper_decode(entries,target,padding,program)
                    self.assertEqual(core.decode(wrapped,bits(program)),expected)
                    self.assertEqual(core.decode(compiled,bits(program)),expected)
                    counts['wrapper_decode_queries'] += 1
                self.assertEqual(expected_weights[target],F(1,2))
                for value in range(2):
                    expected = F(1,2) if value == target else base_weights.get(value,F(0))/2**padding
                    self.assertEqual(expected_weights.get(value,F(0)),expected)
                    counts['shortest_output_equations'] += 1
                self.assertTrue(all(not a.startswith(b) and not b.startswith(a)
                                    for a,b in combinations((p for p,_ in literal),2)))
                self.assertLessEqual(sum((F(1,2**len(p)) for p,_ in literal),F(0)),1)
                counts['kraft_checks'] += 1
                for profile in profiles:
                    expected = sum((weight*profile[value] for value,weight in expected_weights.items()),F(0))
                    actual = core.score(wrapped,profile)
                    self.assertEqual(actual,expected)
                    self.assertGreaterEqual(actual,profile[target]/2)
                    self.assertLessEqual(actual,profile[target]/2+F(1,2**padding))
                    counts['wrapper_profile_bounds'] += 1
                counts['wrapper_cases'] += 1
        counts['prefix_domains'] = len(domains)
        self.assertEqual(counts,dict(prefix_domains=677,finite_books=15131,wrapper_cases=90786,
            wrapper_decode_queries=1906506,shortest_output_equations=181572,
            wrapper_profile_bounds=817074,kraft_checks=105917))
        COVERAGE.update(counts)

    def test_alias_padding_and_missing_output_controls(self):
        alias = book((('00',1),('01',1)))
        self.assertEqual(core.weights(alias),{1:F(1,4)})
        self.assertIsNone(core.decode(alias,()))
        self.assertEqual(core.decode(alias,(False,False)),1)
        empty = book(())
        self.assertEqual(core.weights(empty),{})
        self.assertEqual(core.shortest(core.Wrapped(empty,0,2)),{0:1})
        epsilon = book((('',1),))
        self.assertEqual(core.decode(epsilon,()),1)
        self.assertIsNone(core.decode(epsilon,(False,)))
        x,y = (F(1,2),F(0)),(F(0),F(1))
        small,large = core.Wrapped(epsilon,0,2),core.Wrapped(epsilon,0,3)
        self.assertEqual(core.score(small,x),core.score(small,y))
        self.assertGreater(core.score(large,x),core.score(large,y))
        legal_short = core.Wrapped(epsilon,0,1)
        self.assertEqual(core.weights(legal_short),{0:F(1,2),1:F(1,2)})
        tiny = core.Wrapped(epsilon,0,100)
        self.assertGreater(core.score(tiny,(F(0),F(1))),0)
        self.assertEqual(core.score(tiny,(F(0),F(1))),F(1,2**100))
        COVERAGE.update(alias_output_controls=1,empty_interpreter_controls=1,
                        epsilon_interpreter_controls=1,padding_margin_controls=3,tiny_weight_controls=1)


if __name__ == '__main__':
    result = unittest.main(exit=False,verbosity=2)
    print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not result.result.wasSuccessful())
