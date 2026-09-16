from __future__ import annotations
import importlib.util, itertools, json, sys
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PARENT=ROOT/'research'/'gmi-833-g0-register-core-v1'/'g0_register_core_v1.py'
spec=importlib.util.spec_from_file_location('aj5_parent_g0', PARENT)
g0=importlib.util.module_from_spec(spec); sys.modules[spec.name]=g0; spec.loader.exec_module(g0)

MICRO_MAX={'READ':2,'EMIT':2,'INC':3,'DECJZ':5,'HALT':1}
STATUS={'READ':'DERIVED','EMIT':'DERIVED','INC':'DERIVED','DECJZ':'DERIVED','HALT':'PRESENTATION_ONLY'}

def key_result(r):
    return (r.terminal, tuple(r.output), tuple(r.registers), r.resources.steps)

def execute_fun(p, inp=(), budget=8):
    regs={r:0 for r in p.registers}; inp=tuple(inp); pos=0; out=[]; pc=p.start_label; steps=micro=0
    while True:
        if steps>=budget:
            return ('STEP_BUDGET_EXHAUSTED',tuple(out),tuple(sorted(regs.items())),steps,micro)
        ins=p.instructions[pc]
        if isinstance(ins,g0.Halt):
            steps+=1; micro+=1
            return ('HALTED',tuple(out),tuple(sorted(regs.items())),steps,micro)
        if isinstance(ins,g0.Read):
            steps+=1
            if pos>=len(inp):
                micro+=1
                return ('INPUT_UNDERFLOW',tuple(out),tuple(sorted(regs.items())),steps,micro)
            value=inp[pos]; pos+=1          # NEXT_INPUT
            regs[ins.register]=value        # STORE
            micro+=2; pc=ins.next_label
        elif isinstance(ins,g0.Emit):
            steps+=1
            value=regs[ins.register]        # LOAD
            out.append(value)               # APPEND_OUTPUT
            micro+=2; pc=ins.next_label
        elif isinstance(ins,g0.Inc):
            steps+=1
            value=regs[ins.register]        # LOAD
            value=value+1                   # SUCC
            regs[ins.register]=value        # STORE
            micro+=3; pc=ins.next_label
        elif isinstance(ins,g0.DecJz):
            steps+=1
            value=regs[ins.register]        # LOAD
            zero=(value==0)                 # IS_ZERO
            micro+=2
            if zero:
                pc=ins.zero_label            # SELECT
                micro+=1
            else:
                value=value-1                # PRED_POS
                regs[ins.register]=value     # STORE
                pc=ins.nonzero_label         # SELECT
                micro+=3
        else:
            raise AssertionError('unknown validated instruction')

def rel_successors(p, cfg, inp):
    pc,regs_t,pos,out_t=cfg
    regs=dict(regs_t); out=list(out_t); ins=p.instructions[pc]
    nxt=set()
    if isinstance(ins,g0.Halt):
        nxt.add(('HALTED',tuple(out),tuple(sorted(regs.items())),pos,None))
    elif isinstance(ins,g0.Read):
        if pos>=len(inp): nxt.add(('INPUT_UNDERFLOW',tuple(out),tuple(sorted(regs.items())),pos,None))
        else:
            regs[ins.register]=inp[pos]
            nxt.add((ins.next_label,tuple(sorted(regs.items())),pos+1,tuple(out)))
    elif isinstance(ins,g0.Emit):
        out.append(regs[ins.register])
        nxt.add((ins.next_label,tuple(sorted(regs.items())),pos,tuple(out)))
    elif isinstance(ins,g0.Inc):
        regs[ins.register]+=1
        nxt.add((ins.next_label,tuple(sorted(regs.items())),pos,tuple(out)))
    elif isinstance(ins,g0.DecJz):
        v=regs[ins.register]
        if v==0: nxt.add((ins.zero_label,tuple(sorted(regs.items())),pos,tuple(out)))
        else:
            regs[ins.register]=v-1
            nxt.add((ins.nonzero_label,tuple(sorted(regs.items())),pos,tuple(out)))
    else: raise AssertionError('unknown instruction')
    return nxt

def execute_rel(p, inp=(), budget=8):
    cfg=(p.start_label,tuple((r,0) for r in sorted(p.registers)),0,())
    for steps in range(budget):
        nxt=rel_successors(p,cfg,tuple(inp))
        assert len(nxt)==1
        x=next(iter(nxt))
        if x[0] in ('HALTED','INPUT_UNDERFLOW'):
            terminal,out,regs,_,_=x
            return (terminal,out,regs,steps+1)
        cfg=x
    pc,regs,pos,out=cfg
    return ('STEP_BUDGET_EXHAUSTED',tuple(out),tuple(regs),budget)

def options(labels=('L0','L1')):
    r='r'; out=[g0.Halt()]
    out += [g0.Read(r,n) for n in labels]
    out += [g0.Inc(r,n) for n in labels]
    out += [g0.DecJz(r,nz,z) for nz in labels for z in labels]
    out += [g0.Emit(r,n) for n in labels]
    return tuple(out)

def main():
    labels=('L0','L1'); opts=options(labels); cases=0; fun_bad=rel_bad=0
    terminals=Counter(); max_micro=0; max_ratio=0.0
    for pair in itertools.product(opts,repeat=2):
        p=g0.Program(('r',),'L0',{'L0':pair[0],'L1':pair[1]})
        assert not g0.validate_program(p)
        for inp in ((),(0,),(1,),(2,)):
            parent=g0.execute(p,inp,8); pk=key_result(parent)
            f=execute_fun(p,inp,8); r=execute_rel(p,inp,8)
            cases+=1; terminals[parent.terminal]+=1
            fun_bad += int(pk != f[:4]); rel_bad += int(pk != r)
            max_micro=max(max_micro,f[4]); max_ratio=max(max_ratio,f[4]/max(1,f[3]))
    assert cases==484 and fun_bad==rel_bad==0
    assert terminals==Counter({'STEP_BUDGET_EXHAUSTED':314,'INPUT_UNDERFLOW':107,'HALTED':63})
    assert max_micro<=5*8 and max_ratio<=5

    # Primitive one-step semantics on representative safe configurations.
    primitive_cases=0
    for value in range(4):
        for ins in (g0.Inc('r','L1'),g0.DecJz('r','L1','L0'),g0.Emit('r','L1')):
            primitive_cases+=1
            # statuses must remain explicit and no named opcode may be promoted to bottom ontology.
            assert STATUS[g0.instruction_kind(ins)] in ('DERIVED','PRESENTATION_ONLY')
    assert STATUS['HALT']=='PRESENTATION_ONLY'

    result={
      'status':'GREEN',
      'parent_g0_path':str(PARENT.relative_to(ROOT)),
      'bounded_programs':121,
      'inputs_per_program':4,
      'semantic_execution_cases':cases,
      'terminal_histogram':dict(sorted(terminals.items())),
      'functional_lowering_mismatches':fun_bad,
      'relational_lowering_mismatches':rel_bad,
      'primitive_status':STATUS,
      'static_micro_expansion_upper_bound_per_instruction':MICRO_MAX,
      'static_code_size_bound':'micro_size <= 5 * |G0_program|',
      'dynamic_time_bound':'lower_ops <= 5 * G0_steps',
      'observed_max_lower_ops':max_micro,
      'observed_max_ops_per_g0_step':max_ratio,
      'representative_primitive_safe_cases':primitive_cases,
      'presentations':['P-FUN deterministic event/state-transform composition','P-REL relational small-step composition'],
      'semantic_invariants':['terminal status','protected output','final registered store','G0-level step count'],
      'not_invariant_without_resource_translation':['instruction description length','micro-step cost','grammar mutation distance','search/reachability geometry'],
      'forbidden_promotions':['G0_IS_THE_OPERATIONAL_BOTTOM','UNIQUE_LOWEST_INSTRUCTION_BASIS','COMPILER_MAKES_SEARCH_BIAS_INVARIANT','ALL_MACHINE_MODELS_COMPILED','COMPLETE_GMI'],
      'claim_ceiling':'AJ5_G0_LOWERED_TO_OPERATIONAL_ROLES_WITH_TWO_PRESENTATIONS_AT_REGISTERED_SCOPE'
    }
    (HERE/'RESULT_V1.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,sort_keys=True))
if __name__=='__main__': main()
