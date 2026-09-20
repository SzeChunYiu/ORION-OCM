"""Finite decoder enumeration for actual common raw query responses."""
from itertools import product
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle_v19 as oracle
from partial_v19 import Table
from responses_v19 import Query,observe
COVERAGE={}


class RecoveryTests(unittest.TestCase):
    def test_all_two_model_binary_encodings(self):
        model_count=response_count=encoding_count=pair_count=0
        for n in range(3):
            queries=tuple(Query('empty',e) for e in range(n))+tuple(
                Query('word',word) for length in range(1,5) for word in product(range(n),repeat=length))
            models=tuple(oracle.tables(n))
            responses=[]
            for rows in models:
                table=Table(rows)
                actual=tuple(observe(table,query) for query in queries)
                self.assertEqual(actual,oracle.response_vector(rows))
                recovered=tuple(tuple(observe(table,Query('word',(x,y))) for y in range(n)) for x in range(n))
                self.assertEqual(recovered,rows)
                responses.append(actual)
                model_count+=1
                response_count+=len(queries)
            for i,j in product(range(len(models)),repeat=2):
                self.assertEqual(models[i]==models[j],responses[i]==responses[j])
                pair_count+=1
                for codes in product((0,1),repeat=2):
                    table_recovered=oracle.recoverable(codes,(models[i],models[j]))
                    response_recovered=oracle.recoverable(codes,(responses[i],responses[j]))
                    self.assertEqual(table_recovered,response_recovered)
                    self.assertEqual(table_recovered,codes[0]!=codes[1] or models[i]==models[j])
                    encoding_count+=1
        self.assertEqual((model_count,response_count,pair_count,encoding_count),(84,2602,6566,26264))
        COVERAGE.update(recovery_models=model_count,raw_response_checks=response_count,
                        model_pair_information_checks=pair_count,binary_encoding_decoder_checks=encoding_count)


if __name__=='__main__':
    result=unittest.main(exit=False,verbosity=2)
    print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not result.result.wasSuccessful())
