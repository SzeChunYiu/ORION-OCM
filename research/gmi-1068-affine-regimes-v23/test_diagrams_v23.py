"""Exhaustive active-roster diagrams versus interval feasibility and the actual parent."""
from fractions import Fraction as F
from itertools import product
import importlib.util
from pathlib import Path
import sys
import unittest
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import oracle_v23 as o
import core_v23 as core
import regimes_v23 as r
COVERAGE={}


def old_module():
    path=HERE.parents[0]/'gmi-833-morphology-selection-schema-v1/morphology_selection_schema_v1.py'
    name='_v23_actual_affine_parent'
    if name not in sys.modules:
        spec=importlib.util.spec_from_file_location(name,path)
        module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return sys.modules[name]


def family(rows):
    return core.AffineFamily(*(tuple(row[k] for row in rows) for k in range(5)))


class DiagramTests(unittest.TestCase):
    def test_active_corpus(self):
        old=old_module();counts=dict(rosters=0,interval_cases=0,legacy_interval_cases=0,legacy_function_calls=0,
            boundaries=0,cells=0,whole_cell_memberships=0,pair_cell_checks=0,boundary_memberships=0,empty_cases=0)
        coefficients=tuple(product(map(F,(-1,0,1)),repeat=2))
        ranges=tuple((F(a),F(b)) for a in (-1,0,1) for b in (-1,0,1) if a<=b)
        def compare(fn,args,expected):
            self.assertEqual(fn(*args),expected);counts['legacy_function_calls']+=1
        for n in range(4):
            for lines in product(coefficients,repeat=n):
                rows=tuple((f'i{i}',a,b,True,True) for i,(a,b) in enumerate(lines))
                model=family(rows);counts['rosters']+=1
                parent=tuple(old.AffineCandidate(label,a,b) for label,a,b,_,_ in rows)
                for lo,hi in ranges:
                    diagram=r.diagram(model,lo,hi)
                    checked=o.verify_diagram(rows,lo,hi,diagram)
                    for key,value in checked.items():counts[key]+=value
                    counts['interval_cases']+=1;counts['empty_cases']+=int(n==0)
                    samples=tuple(sorted({t for t,_ in diagram['boundaries']}|{mid for _,_,mid,_ in diagram['cells']}))
                    for t in samples:self.assertEqual(r.winner_ids(model,t),o.winners(rows,t))
                    if not n:continue
                    counts['legacy_interval_cases']+=1
                    roots=old.pairwise_crossings(parent,lo,hi);counts['legacy_function_calls']+=1
                    self.assertEqual(tuple(sorted(set(roots)|{lo,hi})),tuple(t for t,_ in diagram['boundaries']))
                    compare(old.phase_cells,(parent,lo,hi),tuple((a,b,ids) for a,b,_,ids in diagram['cells']))
                    compare(old.critical_samples,(parent,lo,hi),samples)
                    compare(old.possible_winners,(parent,lo,hi),diagram['possible'])
                    compare(old.uncertainty_terminal,(parent,lo,hi),{'terminal':'ROBUST_UNIQUE' if len(diagram['possible'])==1 else 'AMBIGUOUS','possible_winners':list(diagram['possible'])})
                    for t in samples:compare(old.affine_argmin,(parent,t),o.winners(rows,t))
                    for label,_,_,_,_ in rows:compare(old.endpoint_strict_dominance,(parent,label,lo,hi),diagram['unique_everywhere']==label)
        self.assertEqual((counts['rosters'],counts['interval_cases'],counts['legacy_interval_cases']),(820,4920,4914))
        COVERAGE.update(counts)


if __name__=='__main__':
    import json
    run=unittest.main(exit=False,verbosity=2);print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not run.result.wasSuccessful())
