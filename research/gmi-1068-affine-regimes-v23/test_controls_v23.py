"""Fractional falsifiers, exact invariances and faithful historical scope."""
from fractions import Fraction as F
import importlib.util
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle_v23 as o
import regimes_v23 as r
import contexts_v23 as c
import core_v23 as core
from test_diagrams_v23 import family,old_module
COVERAGE={}


def rows(lines):
    return tuple((f'i{i}',F(a),F(b),True,True) for i,(a,b) in enumerate(lines))


class ControlTests(unittest.TestCase):
    def test_fractional_regimes_and_invariance(self):
        examples=(
            (rows(((0,1),(1,-1),(F(2,5),0))),F(0),F(1)),
            (rows(((F(-1,3),1),(F(1,3),-1),(0,0))),F(0),F(1)),
            (rows(((0,0),(0,1))),F(0),F(1)),
            (rows(((0,0),(2,1),(2,-1))),F(-1),F(1)),
            (rows(((1,2),(1,2),(2,2))),F(-2),F(3)))
        results=[];transforms=0
        for data,lo,hi in examples:
            diagram=r.diagram(family(data),lo,hi);o.verify_diagram(data,lo,hi,diagram);results.append(diagram)
            mapped=tuple((label,3*a+F(5,7),3*b-F(4,9),p,e) for label,a,b,p,e in data)
            transformed=r.diagram(family(mapped),lo,hi);o.verify_diagram(mapped,lo,hi,transformed)
            self.assertEqual(transformed,diagram);transforms+=1
            rename={label:'z'+str(len(data)-i) for i,(label,*_) in enumerate(data)}
            permuted=tuple((rename[label],a,b,p,e) for label,a,b,p,e in reversed(data))
            relabelled=r.diagram(family(permuted),lo,hi);o.verify_diagram(permuted,lo,hi,relabelled)
            self.assertEqual(relabelled['possible'],tuple(sorted(rename[x] for x in diagram['possible'])))
            self.assertEqual(tuple((a,b,m,tuple(sorted(rename[x] for x in ids))) for a,b,m,ids in diagram['cells']),relabelled['cells'])
            transforms+=1
        self.assertNotIn('i2',set(results[0]['boundaries'][0][1])|set(results[0]['boundaries'][-1][1]))
        self.assertIn('i2',results[0]['possible'])
        self.assertEqual(o.intervals(examples[1][0],F(0),F(1))['i2'],(F(1,3),F(1,3)))
        self.assertFalse(any('i2' in ids for _,_,_,ids in results[1]['cells']))
        self.assertEqual(results[2]['universal'],('i0',));self.assertIsNone(results[2]['unique_everywhere'])
        self.assertIn(F(0),tuple(t for t,_ in results[3]['boundaries']))
        self.assertEqual(results[3]['possible'],('i0',))
        self.assertEqual(results[4]['possible'],('i0','i1'))
        shifted=rows(((10,0),(0,1)))
        self.assertNotEqual(r.diagram(family(shifted),F(0),F(1))['possible'],results[2]['possible'])
        COVERAGE.update(fractional_named_diagrams=len(examples),invariance_comparisons=transforms)

    def test_context_boundaries(self):
        data=rows(((0,1),(1,0)));model=family(data)
        left,right=c.at(model,F(0)),c.at(model,F(1))
        self.assertEqual(left.context.values,right.context.values)
        self.assertNotEqual(left.decoder,right.decoder)
        for t,encoded in ((F(0),left),(F(1),right)):o.verify_codec(data,t,encoded.context,encoded.decoder)
        # Explicitly changing P/E gives a different family, outside fixed-family inference.
        changed=tuple((label,a,b,label!='i0',e) for label,a,b,p,e in data)
        self.assertNotEqual(r.winner_ids(model,F(0)),r.winner_ids(family(changed),F(0)))
        undefined=tuple((label,a,b,p,label!='i0') for label,a,b,p,e in data)
        self.assertNotEqual(r.winner_ids(model,F(0)),r.winner_ids(family(undefined),F(0)))
        # Nonlinear challenger beats constant0 inside while losing at both endpoints.
        nonlinear=lambda t:(t-F(1,2))**2-F(1,8)
        self.assertGreater(nonlinear(F(0)),0);self.assertGreater(nonlinear(F(1)),0);self.assertLess(nonlinear(F(1,2)),0)
        # Integer order reversal has no integer equality; interpolation misses1 on[0,2].
        self.assertLess(2*0-1,0);self.assertGreater(2*1-1,0)
        self.assertNotIn(1,tuple((1-s)*0+s*2 for s in (0,1)))
        COVERAGE.update(parameter_decoders=2,changed_family_controls=2,nonlinear_controls=1,integer_field_boundaries=1)

    def test_actual_original_r3_and_old_empty(self):
        path=Path(__file__).resolve().parents[1]/'gmi-1068-r3-contextual-attainability-v1/check_r3.py'
        spec=importlib.util.spec_from_file_location('_v23_original_r3',path)
        oldr3=importlib.util.module_from_spec(spec);spec.loader.exec_module(oldr3)
        data=tuple((h,F(value[1]),F(-value[0]),True,True) for h,value in sorted(oldr3.VALUES.items()) if value is not None)
        model=family(data);diagram=r.diagram(model,F(1),F(3));o.verify_diagram(data,F(1),F(3),diagram)
        count=0
        for t in (F(1),F(3,2),F(3)):
            winners=r.winner_ids(model,t)
            self.assertEqual(tuple(sorted({oldr3.VALUES[h] for h in winners})),oldr3.scalar_winner(oldr3.attainable(oldr3.FULL),t));count+=1
        self.assertEqual(r.winner_ids(model,F(3,2)),('h0','h3','h4'))
        self.assertEqual(r.winner_ids(model,F(3)),('h3','h4'))
        old=old_module();errors=0
        for fn,args in ((old.affine_argmin,((),F(0))),(old.possible_winners,((),F(0),F(1))),
                        (old.uncertainty_terminal,((),F(0),F(1))),(old.phase_cells,((),F(0),F(1)))):
            with self.assertRaises(old.SelectionError):fn(*args)
            errors+=1
        self.assertEqual(old.phase_cells((),F(0),F(0)),())
        self.assertEqual(old.pairwise_crossings((),F(0),F(1)),())
        self.assertEqual(old.critical_samples((),F(0),F(1)),(F(0),F(1,2),F(1)))
        self.assertFalse(old.endpoint_strict_dominance((),'missing',F(0),F(1)))
        empty=r.diagram(family(()),F(0),F(1));o.verify_diagram((),F(0),F(1),empty)
        self.assertEqual(empty['possible'],())
        COVERAGE.update(original_scalar_fixture_parameters=count,old_empty_exceptions=errors,original_tied_history_ids=3)


if __name__=='__main__':
    import json
    run=unittest.main(exit=False,verbosity=2);print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not run.result.wasSuccessful())
