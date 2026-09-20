"""Actual old selected profiles versus independent full edge-path enumeration."""
from itertools import product
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle_v24 as o
import core_v24 as core
import af_model_v24 as af
import profiles_v24 as p
COVERAGE={}
NAMES=('C0','C1','ID','NOT')


def literal(graph):
    rows=tuple(tuple(None if edge is None else (edge[0],NAMES[edge[1]]) for edge in row) for row in graph.rows)
    return rows,dict(graph.provenance)


def certify(graph,start,target,horizon,test):
    rows,tags=literal(graph)
    full=o.paths(NAMES,rows,NAMES[start],horizon)
    lifted=tuple(sorted(((NAMES.index(terminal),tuple((NAMES.index(s),a) for s,a in edges),actions)
                         for terminal,edges,actions in full),key=lambda x:(len(x[1]),x[1],x[0])))
    expected=tuple((edges,o.profile(NAMES[terminal],actions,tags,NAMES[target])) for terminal,edges,actions in lifted)
    actual=p.full_profiles(graph,start,target,horizon)
    test.assertEqual(tuple(path for path,_ in actual),tuple(path for path,_ in expected))
    for (_,raw),(_,value) in zip(actual,expected):o.verify_raw(raw,value)
    test.assertEqual(p.edge_histories(graph,start,horizon),tuple((terminal,edges) for terminal,edges,_ in lifted))
    chosen=o.selected(full)
    saved=tuple(o.profile(terminal,actions,tags,NAMES[target]) for terminal,actions in chosen.items())
    selected=p.selected_profiles(graph,start,target)
    o.verify_raw(list(selected),list(saved))
    transitions={name:tuple(edge for edge in rows[i] if edge is not None) for i,name in enumerate(NAMES)}
    test.assertEqual(core.old_af.reachable(NAMES[start],transitions),chosen)
    o.verify_raw(core.old_af.gamma_profiles(NAMES[start],transitions,tags,NAMES[target]),list(saved))
    key=NAMES[target]+'_TASK'
    test.assertEqual(core.old_af.profile_capability_set(selected,key),sorted({raw['capability'][key] for _,raw in expected}))
    observations=0
    for (ctx,decoder),wanted in ((p.selected_context(graph,start,target),saved),
                                 (p.full_context(graph,start,target,horizon),expected)):
        n=len(wanted)
        test.assertEqual((ctx.n,ctx.m),(n,n));test.assertEqual(ctx.admitted,(True,)*n)
        test.assertEqual(ctx.defined,(True,)*n);test.assertEqual(ctx.values,tuple(range(n)))
        test.assertEqual(ctx.order,tuple(tuple(i==j for j in range(n)) for i in range(n)))
        o.verify_context(ctx,decoder,(True,)*n,(True,)*n,tuple(tuple(i==j for j in range(n)) for i in range(n)),wanted)
        test.assertEqual(decoder,wanted)
        for i in range(n):test.assertEqual(core.observe(ctx,i),('VALUE',i));observations+=1
    return len(full),len(saved),observations


class ProfileTests(unittest.TestCase):
    def corpus(self,label,vertices,width,horizon,expected):
        counts=dict(tables=0,case_tuples=0,full_histories=0,selected_histories=0,context_observations=0)
        for destinations in product((-1,)+vertices,repeat=len(vertices)*width):
            counts['tables']+=1
            for assignment in range(2):
                rows=[() for _ in NAMES];tags=[]
                for index,source in enumerate(vertices):
                    slots=[]
                    for slot in range(width):
                        destination=destinations[index*width+slot]
                        if destination==-1:slots.append(None);continue
                        action=f'{NAMES[source]}:{slot}';slots.append((action,destination))
                        tag=o.COMPUTE if assignment==0 else (o.OBS if (index*width+slot)%2==0 else o.ORACLE)
                        tags.append((action,(tag,)))
                    rows[source]=tuple(slots)
                graph=af.AFGraph(tuple(rows),tuple(tags))
                for start in vertices:
                    for target in range(4):
                        full,saved,observations=certify(graph,start,target,horizon,self)
                        counts['full_histories']+=full;counts['selected_histories']+=saved
                        counts['context_observations']+=observations;counts['case_tuples']+=1
        self.assertEqual((counts['tables'],counts['case_tuples']),expected)
        COVERAGE.update({label+'_'+key:value for key,value in counts.items()})

    def test_two_vertex_slots(self):self.corpus('a',(0,2),2,3,(81,1296))
    def test_four_vertex_slots(self):self.corpus('b',(0,1,2,3),1,4,(625,20000))


if __name__=='__main__':
    import json
    run=unittest.main(exit=False,verbosity=2);print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not run.result.wasSuccessful())
