from __future__ import annotations

import importlib.util
from itertools import product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("g0", ROOT / "g0_register_core_v1.py")
g0 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = g0
spec.loader.exec_module(g0)

def independent_run(program, input_values, budget):
    errors = g0.validate_program(program)
    if errors:
        return ("MALFORMED_PROGRAM", (), 0)
    regs = {r:0 for r in program.registers}; pc = program.start_label; inp = list(input_values); pos = 0; out = []; steps = 0
    while steps < budget:
        ins = program.instructions[pc]; steps += 1; name = type(ins).__name__
        if name == "Halt": return ("HALTED", tuple(out), steps)
        if name == "Read":
            if pos >= len(inp): return ("INPUT_UNDERFLOW", tuple(out), steps)
            regs[ins.register] = inp[pos]; pos += 1; pc = ins.next_label
        elif name == "Inc": regs[ins.register] = regs[ins.register] + 1; pc = ins.next_label
        elif name == "DecJz":
            value = regs[ins.register]
            if value: regs[ins.register] = value - 1; pc = ins.nonzero_label
            else: pc = ins.zero_label
        elif name == "Emit": out.append(regs[ins.register]); pc = ins.next_label
        else: return ("MALFORMED_PROGRAM", tuple(out), steps)
    return ("STEP_BUDGET_EXHAUSTED", tuple(out), steps)

def run():
    states=(0,1); keys=((0,0),(0,1),(1,0),(1,1)); words=g0.all_binary_words(3)
    machines=comparisons=mismatches=terminal_failures=bound_failures=0
    for dbits in product((0,1),repeat=4):
        delta=dict(zip(keys,dbits))
        for obits in product((0,1),repeat=4):
            output=dict(zip(keys,obits)); m=g0.Mealy(states,0,delta,output); p=g0.compile_mealy(m); machines += 1
            if len(p.instructions)>22: bound_failures += 1
            for w in words:
                comparisons += 1; expected=g0.direct_mealy(m,w); terminal, got, steps = independent_run(p,tuple(w)+(2,),6*len(w)+5)
                if terminal!="HALTED": terminal_failures += 1
                if got!=expected: mismatches += 1
                if steps>6*len(w)+5: bound_failures += 1
    result={"schema":"GMI833G0RegisterIndependentOracleV1","machines":machines,"comparisons":comparisons,"behavior_mismatches":mismatches,"terminal_failures":terminal_failures,"bound_failures":bound_failures,"terminal":"GREEN" if mismatches==terminal_failures==bound_failures==0 else "RED"}
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    run()
