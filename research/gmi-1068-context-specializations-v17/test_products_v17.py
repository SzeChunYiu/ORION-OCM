"""Independent partial products and both empty-family domain conventions."""
from itertools import product
import json
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import products_v17 as core
from specializations_v17 import acceptance
from core_v17 import Context,observe,compare,domain
COVERAGE={}


class ProductTests(unittest.TestCase):
    def test_all_independently_partial_products(self):
        cases=observations=comparisons=projections=shared=shared_rejections=0
        values=tuple(product((None,False,True),repeat=3))
        for admitted in product((False,True),repeat=3):
            for left in values:
                first=acceptance(admitted,left)
                for right in values:
                    second=acceptance(admitted,right)
                    components=(first.context,second.context)
                    combined=core.independent_product(components,admitted)
                    expected_labels=tuple(product(range(components[0].m),range(components[1].m)))
                    self.assertEqual(core.product_labels(components),expected_labels)
                    self.assertEqual(combined.m,len(expected_labels))
                    self.assertEqual(combined.defined,tuple(a is not None and b is not None for a,b in zip(left,right)))
                    for h in range(3):
                        tag,index=observe(combined,h)
                        expected='ILLEGAL' if not admitted[h] else ('UNDEFINED' if left[h] is None or right[h] is None else 'VALUE')
                        self.assertEqual(tag,expected)
                        if tag=='VALUE':
                            codes=expected_labels[index]
                            self.assertEqual((first.labels[codes[0]],second.labels[codes[1]]),(left[h],right[h]))
                            for i in range(2):
                                self.assertEqual(core.projection_index(components,index,i),components[i].values[h])
                                projections+=1
                        observations+=1
                    for a,b in product(domain(combined),repeat=2):
                        self.assertEqual(compare(combined,a,b),
                                         compare(first.context,a,b) and compare(second.context,a,b))
                        comparisons+=1
                    if first.context.defined==second.context.defined:
                        self.assertEqual(core.shared_product(components,admitted,first.context.defined),combined)
                        shared+=1
                    else:
                        with self.assertRaises(ValueError):core.shared_product(components,admitted,first.context.defined)
                        shared_rejections+=1
                    cases+=1
        self.assertEqual(cases,5832)
        COVERAGE.update(independent_product_cases=cases,joint_observations=observations,
                        joint_comparisons=comparisons,projection_equations=projections,
                        shared_domain_products=shared,unequal_shared_domain_rejections=shared_rejections)

    def test_empty_families_and_malformed_inputs(self):
        controls=0
        for admitted in product((False,True),repeat=3):
            independent=core.independent_product((),admitted)
            self.assertEqual(independent.defined,(True,)*3)
            self.assertEqual(independent.values,(0,)*3)
            self.assertEqual(core.product_labels(()),((),))
            for defined in product((False,True),repeat=3):
                shared=core.shared_product((),admitted,defined)
                self.assertEqual(shared.defined,defined)
                for h in range(3):
                    expected='ILLEGAL' if not admitted[h] else ('VALUE' if defined[h] else 'UNDEFINED')
                    self.assertEqual(observe(shared,h),(expected,0 if expected=='VALUE' else None))
                controls+=1
        component=acceptance((True,),(True,)).context
        mismatched=acceptance((False,),(True,)).context
        invalid=[lambda:core.independent_product([component],(True,)),
                 lambda:core.independent_product((component,),(False,)),
                 lambda:core.independent_product((component,mismatched),(True,)),
                 lambda:core.independent_product((component,),(1,)),
                 lambda:core.shared_product((component,),(True,),(False,)),
                 lambda:core.shared_product((),(True,),(1,)),
                 lambda:core.projection_index((),0,0)]
        for index in (-1,1,True,0.0):
            invalid.append(lambda i=index:core.projection_index((component,),i,0))
        for position in (-1,1,True,0.0):
            invalid.append(lambda i=position:core.projection_index((component,),0,i))
        for i,call in enumerate(invalid):
            with self.subTest(case=i),self.assertRaises(ValueError):call()
        COVERAGE.update(empty_shared_family_controls=controls,empty_independent_family_controls=8,
                        product_malformed_rejections=len(invalid))


if __name__=='__main__':
    program=unittest.main(exit=False,verbosity=2)
    print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not program.result.wasSuccessful())
