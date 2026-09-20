"""Registered E/F: enumerate actual attained-image decoders, including named units."""
from itertools import permutations, product
from math import comb, factorial
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle_v25 as o
import core_v25 as c
import presentations_v25 as p
import information_v25 as info
import named_v25 as named
COVERAGE={}

class InformationTests(unittest.TestCase):
    def test_e_presented_decoders(self):
        count=dict(models=0,basis_queries=0,model_pairs=0,decoder_cases=0,recoverable_cases=0)
        formula=0
        for n in range(3):
            models=[];cores=[];tables=[];vectors=[]
            for labels,rows in o.presented(n):
                model=p.Presented(n,labels,c.Table(rows));pad=o.pad(n,labels,rows);neutral=tuple(labels[i] for i in o.units(rows))
                vector=tuple(o.raw(pad,labels,neutral,t) for t in o.basis(n))
                o.certify(tuple(p.raw_eval(model,t) for t in o.basis(n)),vector)
                models.append(model);cores.append((labels,pad));tables.append(pad);vectors.append(vector)
                count['models']+=1;count['basis_queries']+=len(vector)
            expected_models=sum(comb(n,s)*len(o.catalog(s)) for s in range(n+1))
            self.assertEqual(len(models),expected_models);formula+=4*expected_models**2
            for i,j in product(range(len(models)),repeat=2):
                pair=(models[i],models[j]);count['model_pairs']+=1
                for codes in product((0,1),repeat=2):
                    expected=o.decodable(codes,(vectors[i],vectors[j]))
                    self.assertEqual(expected,o.decodable(codes,(cores[i],cores[j])))
                    self.assertEqual(expected,o.decodable(codes,(tables[i],tables[j])))
                    o.certify(info.core_recoverable(pair,codes),expected)
                    o.certify(info.table_recoverable(pair,codes),expected)
                    count['decoder_cases']+=1;count['recoverable_cases']+=expected
        self.assertEqual(count['decoder_cases'],formula)
        COVERAGE.update({'e_'+k:v for k,v in count.items()})

    def test_f_named_decoders(self):
        count=dict(named_models=0,basis_queries=0,groups=0,model_pairs=0,decoder_cases=0,recoverable_cases=0)
        formula=0
        for n in range(3):
            groups={}
            for labels,rows in o.presented(n):
                model=p.Presented(n,labels,c.Table(rows));pad=o.pad(n,labels,rows);neutral=tuple(labels[i] for i in o.units(rows))
                for identities in permutations(neutral):
                    wrapped=named.NamedPresented(model,identities);k=len(identities)
                    vector=tuple(o.raw(pad,labels,neutral,t,identities) for t in o.basis(n,k))
                    o.certify(tuple(named.named_eval(wrapped,t) for t in o.basis(n,k)),vector)
                    o.certify(tuple(named.named_word(wrapped,t) for t in o.basis(n,k)),vector)
                    o.certify(named.named_signature(wrapped),(pad,identities))
                    groups.setdefault(k,[]).append((wrapped,(pad,identities),vector))
                    count['named_models']+=1;count['basis_queries']+=len(vector)
            for k,models in sorted(groups.items()):
                expected=factorial(k)*sum(comb(n,s)*sum(len(o.units(rows))==k for rows in o.catalog(s)) for s in range(n+1))
                self.assertEqual(len(models),expected);formula+=4*expected**2;count['groups']+=1
                COVERAGE[f'f_models_n{n}_k{k}']=len(models)
                for first,second in product(models,repeat=2):
                    count['model_pairs']+=1
                    for codes in product((0,1),repeat=2):
                        wanted=o.decodable(codes,(first[2],second[2]))
                        self.assertEqual(wanted,o.decodable(codes,(first[1],second[1])))
                        o.certify(named.named_recoverable((first[0],second[0]),codes),wanted)
                        count['decoder_cases']+=1;count['recoverable_cases']+=wanted
        self.assertEqual(count['decoder_cases'],formula)
        COVERAGE.update({'f_'+k:v for k,v in count.items()})

if __name__=='__main__':
    result=unittest.main(exit=False,verbosity=2).result
    print(json.dumps(COVERAGE,sort_keys=True));raise SystemExit(not result.wasSuccessful())
