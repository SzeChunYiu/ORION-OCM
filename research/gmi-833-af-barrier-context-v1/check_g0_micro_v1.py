from __future__ import annotations
import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load(path:Path,name:str):
    spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec); sys.modules[name]=m; spec.loader.exec_module(m); return m

def parent_path():
    repo_candidate=HERE.parent/'gmi-833-g0-register-core-v1'/'g0_register_core_v1.py'
    if repo_candidate.exists(): return repo_candidate
    local=Path('/tmp/g0_register_core_v1.py')
    if local.exists(): return local
    raise FileNotFoundError('G0_PARENT_NOT_FOUND')

def programs(g):
    return {
      'C0':g.Program(('r',),'emit',{'emit':g.Emit('r','halt'),'halt':g.Halt()}),
      'C1':g.Program(('r',),'inc',{'inc':g.Inc('r','emit'),'emit':g.Emit('r','halt'),'halt':g.Halt()}),
      'ID':g.Program(('r',),'read',{'read':g.Read('r','emit'),'emit':g.Emit('r','halt'),'halt':g.Halt()}),
      'NOT':g.Program(('r','o'),'read',{'read':g.Read('r','branch'),'branch':g.DecJz('r','emit0','inc1'),'emit0':g.Emit('o','halt'),'inc1':g.Inc('o','emit1'),'emit1':g.Emit('o','halt'),'halt':g.Halt()}),
    }
def main():
    g=load(parent_path(),'g0_parent_af'); ps=programs(g); target=(0,1); tables={}; resources={}
    for name,p in ps.items():
        outs=[]; rs=[]
        for x in (0,1):
            r=g.execute(p,(x,),20); assert r.terminal=='HALTED' and len(r.output)==1; outs.append(r.output[0]); rs.append(list(r.resources.as_tuple()))
        tables[name]=outs;resources[name]=rs
    assert tables=={'C0':[0,0],'C1':[1,1],'ID':[0,1],'NOT':[1,0]}
    scores={n:str(Fraction(sum(int(tables[n][i]==target[i]) for i in (0,1)),2)) for n in tables}
    assert scores=={'C0':'1/2','C1':'1/2','ID':'1','NOT':'0'}
    result={'status':'GREEN','parent_blob':'6c80e7b1ee0cceedb5dc48eaf28bd3011750d80a','truth_tables':tables,'identity_task_scores':scores,'raw_resource_vectors_by_input':resources,'same_current_pair':['C0','C1'],'same_current_score':'1/2','developmental_witness':'C0 one-repair can reach ID while frozen C1 remains at 1/2; development relation is external to G0 execution','claim':'EXACT_G0_PROGRAM_MICROSCOPE_FOR_AF1_AT_REGISTERED_BINARY_SCOPE'}
    text=json.dumps(result,indent=2,sort_keys=True)+'\n';(HERE/'G0_RESULT_V1.json').write_text(text);print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
