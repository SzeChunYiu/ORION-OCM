"""Exhaustive independent P/E families with actual common-value decoding."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle_v23 as o
import contexts_v23 as c
import regimes_v23 as r
from test_diagrams_v23 import family
COVERAGE={}


class ContextTests(unittest.TestCase):
    def test_partial_context_corpus(self):
        counts=dict(families=0,interval_cases=0,boundaries=0,cells=0,whole_cell_memberships=0,
                    pair_cell_checks=0,boundary_memberships=0,decoded_observations=0,decoder_order_pairs=0,
                    actual_contexts=0,empty_active_cases=0,winner_ids=0)
        options=tuple(product(map(F,(-1,0,1)),map(F,(-1,0,1)),(False,True),(False,True)))
        for n in range(3):
            for chosen in product(options,repeat=n):
                rows=tuple((f'i{i}',a,b,p,e) for i,(a,b,p,e) in enumerate(chosen))
                model=family(rows);counts['families']+=1
                for lo0 in (-1,0,1):
                    for hi0 in (-1,0,1):
                        if lo0>hi0:continue
                        lo,hi=F(lo0),F(hi0);diagram=r.diagram(model,lo,hi)
                        for key,value in o.verify_diagram(rows,lo,hi,diagram).items():counts[key]+=value
                        counts['interval_cases']+=1
                        counts['empty_active_cases']+=int(not any(p and e for _,_,_,p,e in rows))
                        samples=tuple(sorted({t for t,_ in diagram['boundaries']}|{mid for _,_,mid,_ in diagram['cells']}))
                        for t in samples:
                            encoded=c.at(model,t)
                            expected=o.verify_codec(rows,t,encoded.context,encoded.decoder)
                            self.assertEqual(r.winner_ids(model,t),o.winners(rows,t))
                            for i,tag in enumerate(expected):
                                self.assertEqual(c.decoded(encoded,i),tag);counts['decoded_observations']+=1
                            counts['decoder_order_pairs']+=n*n;counts['actual_contexts']+=1
                            counts['winner_ids']+=len(o.winners(rows,t))
        self.assertEqual((counts['families'],counts['interval_cases']),(1333,7998))
        COVERAGE.update(counts)


if __name__=='__main__':
    import json
    run=unittest.main(exit=False,verbosity=2);print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not run.result.wasSuccessful())
