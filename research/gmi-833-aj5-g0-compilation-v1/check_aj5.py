from __future__ import annotations
import hashlib, importlib.util, itertools, json, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/"gmi-833-g0-register-core-v1"/"g0_register_core_v1.py"
PARENT_BLOB="6c80e7b1ee0cceedb5dc48eaf28bd3011750d80a"

def git_blob_sha(path:Path)->str:
    data=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

def load_parent():
    assert git_blob_sha(PARENT)==PARENT_BLOB
    spec=importlib.util.spec_from_file_location("g0_parent",PARENT)
    m=importlib.util.module_from_spec(spec); assert spec.loader is not None
    sys.modules[spec.name]=m
    spec.loader.exec_module(m); return m

def lower_execute(m, program, input_values=(), step_budget=8):
    regs={r:0 for r in program.registers}; inp=tuple(input_values); pos=0; out=[]; pc=program.start_label
    steps=0; micro=0
    while True:
        if steps>=step_budget:
            return ("STEP_BUDGET_EXHAUSTED",tuple(out),tuple(sorted(regs.items())),steps,micro)
        ins=program.instructions[pc]
        if isinstance(ins,m.Halt):
            micro+=1; steps+=1
            return ("HALTED",tuple(out),tuple(sorted(regs.items())),steps,micro)
        if isinstance(ins,m.Read):
            micro+=1; steps+=1
            if pos>=len(inp):
                return ("INPUT_UNDERFLOW",tuple(out),tuple(sorted(regs.items())),steps,micro)
            tmp=inp[pos]; pos+=1
            micro+=1; regs[ins.register]=tmp
            micro+=1; pc=ins.next_label
            continue
        if isinstance(ins,m.Inc):
            micro+=1; tmp=regs[ins.register]
            micro+=1; tmp=tmp+1
            micro+=1; regs[ins.register]=tmp
            micro+=1; pc=ins.next_label
            steps+=1; continue
        if isinstance(ins,m.DecJz):
            micro+=1; tmp=regs[ins.register]
            micro+=1; iszero=(tmp==0)
            micro+=1
            if iszero:
                pc=ins.zero_label
            else:
                micro+=1; tmp=tmp-1
                micro+=1; regs[ins.register]=tmp
                pc=ins.nonzero_label
            steps+=1; continue
        if isinstance(ins,m.Emit):
            micro+=1; tmp=regs[ins.register]
            micro+=1; out.append(tmp)
            micro+=1; pc=ins.next_label
            steps+=1; continue
        raise AssertionError("unexpected parent instruction")

def one_step_micro(m,ins,r,inp):
    inp=tuple(inp)
    if isinstance(ins,m.Halt): return ("HALT",None,r,inp,(),1)
    if isinstance(ins,m.Read):
        if not inp:return ("UNDERFLOW",None,r,inp,(),1)
        return ("CONT",ins.next_label,inp[0],inp[1:],(),3)
    if isinstance(ins,m.Inc): return ("CONT",ins.next_label,r+1,inp,(),4)
    if isinstance(ins,m.DecJz):
        return ("CONT",ins.zero_label,r,inp,(),3) if r==0 else ("CONT",ins.nonzero_label,r-1,inp,(),5)
    if isinstance(ins,m.Emit): return ("CONT",ins.next_label,r,inp,(r,),3)
    raise AssertionError

def relational_table(m,options):
    relation=set()
    for idx,ins in enumerate(options):
        for r in (0,1,2):
            for inp in ((),(0,),(1,)):
                if isinstance(ins,m.Halt): out=("HALT",None,r,inp,())
                elif isinstance(ins,m.Read):
                    out=("UNDERFLOW",None,r,inp,()) if not inp else ("CONT",ins.next_label,inp[0],inp[1:],())
                elif isinstance(ins,m.Inc): out=("CONT",ins.next_label,r+1,inp,())
                elif isinstance(ins,m.DecJz): out=("CONT",ins.zero_label,r,inp,()) if r==0 else ("CONT",ins.nonzero_label,r-1,inp,())
                elif isinstance(ins,m.Emit): out=("CONT",ins.next_label,r,inp,(r,))
                relation.add(((idx,r,inp),out))
    return relation

def main():
    m=load_parent(); labels=("L0","L1"); r="r"
    options=[m.Halt()]
    options += [m.Read(r,n) for n in labels]
    options += [m.Inc(r,n) for n in labels]
    options += [m.DecJz(r,nz,z) for nz in labels for z in labels]
    options += [m.Emit(r,n) for n in labels]
    assert len(options)==11

    programs=0; runs=0; failures=0; total_micro=0
    for a,b in itertools.product(options,repeat=2):
        p=m.Program((r,),"L0",{"L0":a,"L1":b}); programs+=1
        for inp in ((),(0,),(1,),(2,)):
            parent=m.execute(p,inp,8); lower=lower_execute(m,p,inp,8); runs+=1
            got=(parent.terminal,parent.output,parent.registers,parent.resources.steps)
            failures += int(got != lower[:4])
            total_micro += lower[4]
            assert lower[4] <= 5*max(1,lower[3])

    relation=relational_table(m,options); rel_fail=0
    for idx,ins in enumerate(options):
        for rv in (0,1,2):
            for inp in ((),(0,),(1,)):
                micro=one_step_micro(m,ins,rv,inp)[:-1]
                expected=next(out for key,out in relation if key==(idx,rv,inp))
                rel_fail += int(micro!=expected)

    classification={
      "READ":{"status":"DERIVED","from":["INPUT_TAKE","REGISTER_WRITE","CONTROL_ROUTE"]},
      "EMIT":{"status":"DERIVED","from":["REGISTER_READ","OUTPUT_APPEND","CONTROL_ROUTE"]},
      "INC":{"status":"DERIVED","from":["REGISTER_READ","NATURAL_SUCCESSOR","REGISTER_WRITE","CONTROL_ROUTE"],"premise":"registered natural-number carrier"},
      "DECJZ":{"status":"DERIVED","from":["REGISTER_READ","ZERO_TEST","CONDITIONAL_ROUTE","POSITIVE_PREDECESSOR","REGISTER_WRITE"],"premise":"registered natural-number order/predecessor"},
      "HALT":{"status":"PRESENTATION_ONLY","from":["terminal/no-successor control convention"]}
    }
    assert failures==0 and rel_fail==0 and runs==484 and programs==121 and len(relation)==99
    result={
      "status":"GREEN","parent_g0_git_blob":PARENT_BLOB,
      "primitive_classification":classification,
      "two_label_programs":programs,"parent_vs_micro_runs":runs,"semantic_failures":failures,
      "total_lower_micro_ops":total_micro,"static_microcode_bound":"<=5 micro-ops per G0 instruction","runtime_bound":"<=5 lower micro-ops per executed G0 step",
      "persistent_space_overhead":"no new persistent register; O(1) scratch temporary/predicate",
      "precision_boundary":"inherits G0 unit-cost exact-natural-register convention; bit complexity not silently claimed",
      "alternate_relational_presentation_rows":len(relation),"alternate_presentation_failures":rel_fail,
      "invariants":["protected I/O trace","terminal outcome","final registered values at bounded execution scope"],
      "noninvariants":["surface code length","grammar reachability geometry","raw lower-level step count without compiler map"],
      "forbidden_promotions":["G0_IS_OPERATIONAL_BOTTOM","G0_PRIMITIVES_ONTOLOGICALLY_IRREDUCIBLE","DESCRIPTION_LENGTH_PRESENTATION_INVARIANT","SEARCH_GEOMETRY_PRESENTATION_INVARIANT","UNIT_COST_NATURAL_ARITHMETIC_IS_PHYSICAL_LAW"],
      "claim_ceiling":"AJ5_G0_COMPILED_FROM_LOWER_PROCESS_ROLES_AT_REGISTERED_BOUNDED_SCOPE"
    }
    (HERE/"RESULT_V1.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,sort_keys=True))
if __name__=="__main__": main()
