"""Exact finite linear calibration and nonlinear certification falsifiers."""
from fractions import Fraction as Q
import importlib.util
from itertools import product
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent

def load(name):
    spec = importlib.util.spec_from_file_location(name,HERE/(name+'.py'))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

core,oracle = load('linear_v16'),load('oracle_v16')
COVERAGE = {}


class LinearTests(unittest.TestCase):
    def test_all_coefficients_and_profiles(self):
        count = evaluations = representations = ordered = additive = homogeneous = negatives = normalized = 0
        dimensions = {i:0 for i in range(4)}
        for coeffs in oracle.coefficients():
            n = len(coeffs)
            function = lambda v,c=coeffs:core.weighted(c,v)
            self.assertEqual(core.basis_coefficients(function,n),coeffs)
            self.assertEqual(core.nonnegative(coeffs),all(c>=0 for c in coeffs))
            self.assertEqual(core.normalized(coeffs),sum(coeffs,Q(0))==1)
            ones,zero = (Q(1),)*n,(Q(0),)*n
            self.assertEqual(function(zero),Q(0))
            self.assertEqual(function(ones)==1,core.normalized(coeffs))
            count += 1
            dimensions[n] += 1
            normalized += core.normalized(coeffs)
            scores = {}
            for profile in oracle.profiles(n):
                scores[profile] = function(profile)
                self.assertEqual(scores[profile],oracle.score(coeffs,profile))
                evaluations += 1
                self.assertTrue(core.representation_at(function,coeffs,profile))
                representations += 1
                shifted = tuple(x+1 for x in profile)
                self.assertEqual(function(shifted),function(profile)+function(ones))
                additive += 1
                for scalar in (Q(-1),Q(0),Q(1,3),Q(2)):
                    self.assertEqual(function(tuple(scalar*x for x in profile)),scalar*function(profile))
                    homogeneous += 1
            observed_monotone = True
            for lower,upper in oracle.ordered_pairs(n):
                holds = scores[lower]<=scores[upper]
                observed_monotone = observed_monotone and holds
                if core.nonnegative(coeffs):
                    self.assertTrue(holds)
                ordered += 1
            self.assertEqual(observed_monotone,core.nonnegative(coeffs))
            for i,c in enumerate(coeffs):
                if c<0:
                    basis = tuple(Q(int(i==j)) for j in range(n))
                    self.assertGreater(function(zero),function(basis))
                    negatives += 1
        self.assertEqual(count,400)
        COVERAGE.update(coefficient_vectors=count,profile_evaluations=evaluations,
                        representation_equations=representations,ordered_profile_pairs=ordered,
                        additivity_probes=additive,homogeneity_probes=homogeneous,
                        negative_coefficient_witnesses=negatives,normalized_vectors=normalized)
        COVERAGE.update({'coefficient_dimension_'+str(k):v for k,v in dimensions.items()})

    def test_nonlinear_boundaries(self):
        profiles = oracle.profiles(2)
        monotone = symmetric = constants = exclusions = 0
        e0,e1,ones = (Q(1),Q(0)),(Q(0),Q(1)),(Q(1),Q(1))
        for function in (min,max):
            for v in profiles:
                self.assertEqual(function(v),function(tuple(reversed(v))))
                symmetric += 1
            for x,y in oracle.ordered_pairs(2):
                self.assertLessEqual(function(x),function(y))
                monotone += 1
            for c in oracle.PROFILE_VALUES:
                self.assertEqual(function((c,c)),c)
                constants += 1
            weights = core.basis_coefficients(function,2)
            self.assertFalse(core.representation_at(function,weights,ones))
            self.assertNotEqual(function(ones),function(e0)+function(e1))
            exclusions += 1
        self.assertLess(min((Q(2),Q(0))),min(ones))
        self.assertGreater(max((Q(2),Q(0))),max(ones))
        weights = (Q(1,2),Q(1,2))
        def impostor(v):
            return oracle.score(weights,v)+v[0]*v[1]*(v[0]-v[1])**2
        extracted = core.basis_coefficients(impostor,2)
        self.assertEqual(extracted,weights)
        self.assertTrue(core.representation_at(impostor,extracted,ones))
        probe = (Q(1),Q(2))
        self.assertFalse(core.representation_at(impostor,extracted,probe))
        self.assertNotEqual(impostor(probe),impostor(e0)+impostor((Q(0),Q(2))))
        basis_ones_only = lambda f:core.normalized(core.basis_coefficients(f,2)) and f(ones)==1
        self.assertTrue(basis_ones_only(impostor))
        self.assertFalse(basis_ones_only(impostor) and core.representation_at(impostor,extracted,probe))
        self.assertEqual(core.basis_coefficients(lambda _:Q(1),0),())
        self.assertFalse(core.representation_at(lambda _:Q(1),(),()))
        self.assertFalse(core.normalized(()))
        COVERAGE.update(minmax_monotonicity=monotone,minmax_symmetry=symmetric,
                        minmax_constant_preservation=constants,minmax_fixed_weight_exclusions=exclusions,
                        minmax_rank_reversals=1,nonlinear_impostor_rejections=1,
                        weak_basis_diagnostic_controls=1,empty_dimension_counterexamples=1)

    def test_malformed_linear_inputs(self):
        invalid = []
        for vector in ([Q(1)],(1,),(True,),(1.0,),None):
            invalid += [lambda v=vector:core.weighted(v,(Q(1),)),
                        lambda v=vector:core.weighted((Q(1),),v),
                        lambda v=vector:core.nonnegative(v),lambda v=vector:core.normalized(v)]
        invalid.append(lambda:core.weighted((),(Q(1),)))
        for n in (-1,True,1.0,None):
            invalid.append(lambda d=n:core.basis_coefficients(lambda _:Q(0),d))
        for result in (0,True,0.0,None):
            invalid += [lambda r=result:core.basis_coefficients(lambda _:r,0),
                        lambda r=result:core.basis_coefficients(lambda _:r,2),
                        lambda r=result:core.representation_at(lambda _:r,(),())]
        invalid += [lambda:core.basis_coefficients(None,0),lambda:core.representation_at(None,(),())]
        for i,call in enumerate(invalid):
            with self.subTest(case=i),self.assertRaises(ValueError):
                call()
        def unavailable(_):
            raise OSError('callback unavailable')
        with self.assertRaises(OSError):
            core.basis_coefficients(unavailable,0)
        with self.assertRaises(OSError):
            core.representation_at(unavailable,(),())
        COVERAGE.update(linear_malformed_rejections=len(invalid),callback_unavailability_controls=2)


if __name__ == '__main__':
    program = unittest.main(exit=False,verbosity=2)
    print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not program.result.wasSuccessful())
