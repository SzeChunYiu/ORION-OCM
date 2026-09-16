from __future__ import annotations
import importlib.util, itertools, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
PARENT=ROOT/'research'/'gmi-833-g0-register-core-v1'/'g0_register_core_v1.py'
spec=importlib.util.spec_from_file_location('ai_g0_parent',PARENT); g0=importlib.util.module_from_spec(spec);sys.modules[spec.name]=g0;spec.loader.exec_module(g0)
from compile_core import direct_net, COEFF, BITS

def signed(z): return (max(z,0),max(-z,0))

def compile_truth_function(coeff):
    regs=('x0','x1','pos','neg'); I={}
    I['read0']=g0.Read('x0','branch0')
    I['branch0']=g0.DecJz('x0','read1_1','read1_0')
    for x0 in (0,1):
        I[f'read1_{x0}']=g0.Read('x1',f'branch1_{x0}')
        I[f'branch1_{x0}']=g0.DecJz('x1',f'leaf_{x0}_1_start',f'leaf_{x0}_0_start')
        for x1 in (0,1):
            z=direct_net(coeff,(x0,x1)); p,n=signed(z); start=f'leaf_{x0}_{x1}_start'; cur=start
            seq=[]
            for _ in range(p): seq.append(('INC','pos'))
            for _ in range(n): seq.append(('INC','neg'))
            seq += [('EMIT','pos'),('EMIT','neg')]
            if not seq: raise AssertionError
            labels=[cur]+[f'leaf_{x0}_{x1}_{j}' for j in range(1,len(seq))]
            for j,(kind,r) in enumerate(seq):
                nxt='halt' if j==len(seq)-1 else labels[j+1]
                I[labels[j]]=g0.Inc(r,nxt) if kind=='INC' else g0.Emit(r,nxt)
    I['halt']=g0.Halt()
    return g0.Program(regs,'read0',I)

def census():
    nets=evals=bad=0;max_code=max_steps=0;max_regs=0
    for coeff in itertools.product(COEFF,repeat=6):
        p=compile_truth_function(coeff); nets+=1; max_code=max(max_code,len(p.instructions));max_regs=max(max_regs,len(p.registers))
        assert not g0.validate_program(p)
        for x in BITS:
            r=g0.execute(p,x,50); evals+=1; max_steps=max(max_steps,r.resources.steps)
            expected=signed(direct_net(coeff,x)); bad+=int(r.terminal!='HALTED' or tuple(r.output)!=expected)
    assert nets==729 and evals==2916 and bad==0
    return {'compiled_networks':nets,'input_evaluations':evals,'semantic_mismatches':bad,'output_encoding':'signed_pair(pos,neg)','max_program_instructions':max_code,'max_runtime_steps':max_steps,'registers':max_regs,'compiler_style':'finite behavioral compiler into merged G0; lower arithmetic compiler separately preserves compositional construction'}
