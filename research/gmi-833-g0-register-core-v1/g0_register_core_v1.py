from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Any, Dict, Mapping, Sequence, Tuple
import json

SOURCE_MAIN = "7b68b0681a44157aab4864a66266ba598cce0fbc"
FREEZE_COMMIT = "7201b1a56d7eb62de0d405da45142b77f30920da"
CLAIM_CEILING = "GMI_G0_REGISTER_CORE_AND_FINITE_EMBEDDINGS_AT_DECLARED_SCOPE"
FORBIDDEN_PROMOTIONS = (
    "UNIQUE_MINIMAL_UNIVERSAL_GRAMMAR",
    "ARCHITECTURE_PRIOR_FREE_GRAMMAR",
    "UNBIASED_SEARCH",
    "ALL_COMPUTATIONAL_MODELS_EMBEDDED",
    "NEURAL_MORPHOLOGY_DERIVED",
    "PROBABILISTIC_MORPHOLOGY_DERIVED",
    "GRAMMAR_REPRESENTATION_INVARIANT",
    "MORPHOLOGY_SELECTION_INVARIANT",
    "COMPLETE_GMI",
)

@dataclass(frozen=True)
class Read:
    register: str
    next_label: str

@dataclass(frozen=True)
class Inc:
    register: str
    next_label: str

@dataclass(frozen=True)
class DecJz:
    register: str
    nonzero_label: str
    zero_label: str

@dataclass(frozen=True)
class Emit:
    register: str
    next_label: str

@dataclass(frozen=True)
class Halt:
    pass

INSTRUCTION_TYPES = (Read, Inc, DecJz, Emit, Halt)
INSTRUCTION_CLASS_NAMES = ("READ", "INC", "DECJZ", "EMIT", "HALT")

@dataclass(frozen=True)
class Program:
    registers: Tuple[str, ...]
    start_label: str
    instructions: Mapping[str, object]

@dataclass(frozen=True)
class Resources:
    program_instructions: int
    steps: int
    register_reads: int
    register_writes: int
    input_reads: int
    output_writes: int

    def as_tuple(self) -> Tuple[int, int, int, int, int, int]:
        return (
            self.program_instructions, self.steps, self.register_reads,
            self.register_writes, self.input_reads, self.output_writes,
        )

@dataclass(frozen=True)
class TraceEvent:
    label: str
    kind: str
    positive_branch: bool | None = None

@dataclass(frozen=True)
class ExecutionResult:
    terminal: str
    reason: str
    output: Tuple[int, ...]
    registers: Tuple[Tuple[str, int], ...]
    resources: Resources
    trace: Tuple[TraceEvent, ...]

def instruction_kind(instr: object) -> str:
    if isinstance(instr, Read): return "READ"
    if isinstance(instr, Inc): return "INC"
    if isinstance(instr, DecJz): return "DECJZ"
    if isinstance(instr, Emit): return "EMIT"
    if isinstance(instr, Halt): return "HALT"
    return "UNKNOWN"

def instruction_registers(instr: object) -> Tuple[str, ...]:
    if isinstance(instr, (Read, Inc, DecJz, Emit)):
        return (instr.register,)
    return ()

def successor_labels(instr: object) -> Tuple[str, ...]:
    if isinstance(instr, (Read, Inc, Emit)):
        return (instr.next_label,)
    if isinstance(instr, DecJz):
        return (instr.nonzero_label, instr.zero_label)
    if isinstance(instr, Halt):
        return ()
    return ()

def validate_program(program: Program) -> Tuple[str, ...]:
    errors = []
    if not isinstance(program.registers, tuple) or not program.registers:
        errors.append("REGISTERS_MUST_BE_NONEMPTY_TUPLE")
    elif len(set(program.registers)) != len(program.registers):
        errors.append("DUPLICATE_REGISTER")
    labels = tuple(program.instructions.keys())
    if not labels:
        errors.append("PROGRAM_MUST_BE_NONEMPTY")
    if program.start_label not in program.instructions:
        errors.append(f"MISSING_START_LABEL:{program.start_label}")
    regset = set(program.registers)
    labelset = set(labels)
    for label, instr in program.instructions.items():
        if not isinstance(label, str) or not label:
            errors.append("INVALID_LABEL")
        if not isinstance(instr, INSTRUCTION_TYPES):
            errors.append(f"UNKNOWN_INSTRUCTION:{label}")
            continue
        for r in instruction_registers(instr):
            if r not in regset:
                errors.append(f"MISSING_REGISTER:{label}:{r}")
        for target in successor_labels(instr):
            if target not in labelset:
                errors.append(f"MISSING_LABEL:{label}:{target}")
    return tuple(errors)

def execute(program: Program, input_values: Sequence[int] = (), step_budget: int = 1000) -> ExecutionResult:
    if step_budget < 0:
        raise ValueError("step_budget must be nonnegative")
    malformed = validate_program(program)
    static = len(program.instructions)
    zero_resources = Resources(static, 0, 0, 0, 0, 0)
    if malformed:
        return ExecutionResult("MALFORMED_PROGRAM", ";".join(malformed), (), (), zero_resources, ())
    if any(type(x) is not int or x < 0 for x in input_values):
        return ExecutionResult("MALFORMED_PROGRAM", "INPUT_VALUES_MUST_BE_NATURAL_NUMBERS", (), (), zero_resources, ())
    regs = {r: 0 for r in program.registers}
    inp = tuple(input_values)
    input_pos = 0
    out = []
    trace = []
    pc = program.start_label
    steps = rr = rw = ir = ow = 0
    while True:
        if steps >= step_budget:
            return ExecutionResult("STEP_BUDGET_EXHAUSTED", "step budget exhausted", tuple(out), tuple(sorted(regs.items())), Resources(static, steps, rr, rw, ir, ow), tuple(trace))
        instr = program.instructions[pc]
        if isinstance(instr, Halt):
            steps += 1
            trace.append(TraceEvent(pc, "HALT"))
            return ExecutionResult("HALTED", "success", tuple(out), tuple(sorted(regs.items())), Resources(static, steps, rr, rw, ir, ow), tuple(trace))
        if isinstance(instr, Read):
            steps += 1
            if input_pos >= len(inp):
                trace.append(TraceEvent(pc, "READ_UNDERFLOW"))
                return ExecutionResult("INPUT_UNDERFLOW", "read attempted past input", tuple(out), tuple(sorted(regs.items())), Resources(static, steps, rr, rw, ir, ow), tuple(trace))
            regs[instr.register] = inp[input_pos]
            input_pos += 1; rw += 1; ir += 1
            trace.append(TraceEvent(pc, "READ")); pc = instr.next_label; continue
        if isinstance(instr, Inc):
            steps += 1; rr += 1; rw += 1
            regs[instr.register] += 1
            trace.append(TraceEvent(pc, "INC")); pc = instr.next_label; continue
        if isinstance(instr, DecJz):
            steps += 1; rr += 1
            if regs[instr.register] > 0:
                regs[instr.register] -= 1; rw += 1
                trace.append(TraceEvent(pc, "DECJZ", True)); pc = instr.nonzero_label
            else:
                trace.append(TraceEvent(pc, "DECJZ", False)); pc = instr.zero_label
            continue
        if isinstance(instr, Emit):
            steps += 1; rr += 1; ow += 1
            out.append(regs[instr.register])
            trace.append(TraceEvent(pc, "EMIT")); pc = instr.next_label; continue
        raise AssertionError("validated instruction became unknown")

def recount_resources(program: Program, trace: Sequence[TraceEvent]) -> Resources:
    steps = rr = rw = ir = ow = 0
    for event in trace:
        steps += 1
        if event.kind == "READ": rw += 1; ir += 1
        elif event.kind == "READ_UNDERFLOW": pass
        elif event.kind == "INC": rr += 1; rw += 1
        elif event.kind == "DECJZ":
            rr += 1
            if event.positive_branch: rw += 1
        elif event.kind == "EMIT": rr += 1; ow += 1
        elif event.kind == "HALT": pass
        else: raise ValueError(f"unknown trace event {event.kind}")
    return Resources(len(program.instructions), steps, rr, rw, ir, ow)

def requirement_witnesses() -> Dict[str, Program]:
    return {
        "READ": Program(("r",), "read", {"read": Read("r", "emit"), "emit": Emit("r", "halt"), "halt": Halt()}),
        "EMIT": Program(("r",), "inc", {"inc": Inc("r", "emit"), "emit": Emit("r", "halt"), "halt": Halt()}),
        "INC": Program(("r",), "inc", {"inc": Inc("r", "emit"), "emit": Emit("r", "halt"), "halt": Halt()}),
        "DECJZ": Program(("r", "z"), "read", {"read": Read("r", "branch"), "branch": DecJz("r", "twice1", "once"), "once": Emit("z", "halt"), "twice1": Emit("z", "twice2"), "twice2": Emit("z", "halt"), "halt": Halt()}),
        "HALT": Program(("r",), "halt", {"halt": Halt()}),
    }

def verify_positive_requirements() -> Dict[str, bool]:
    w = requirement_witnesses()
    rin0 = execute(w["READ"], (0,), 10); rin1 = execute(w["READ"], (1,), 10)
    b0 = execute(w["DECJZ"], (0,), 20); b1 = execute(w["DECJZ"], (1,), 20)
    return {
        "REQ-IN": rin0.terminal == rin1.terminal == "HALTED" and rin0.output != rin1.output,
        "REQ-OUT": execute(w["EMIT"], (), 10).output == (1,),
        "REQ-GEN": execute(w["INC"], (), 10).output == (1,),
        "REQ-BRANCH": b0.terminal == b1.terminal == "HALTED" and b0.output == (0,) and b1.output == (0, 0),
        "REQ-TERM": execute(w["HALT"], (), 2).terminal == "HALTED",
    }

def bounded_absence_census() -> Dict[str, Dict[str, int]]:
    labels = ("L0", "L1"); r = "r"
    def options_without(kind: str):
        opts = []
        if kind != "HALT": opts.append(Halt())
        if kind != "READ":
            for nxt in labels: opts.append(Read(r, nxt))
        if kind != "INC":
            for nxt in labels: opts.append(Inc(r, nxt))
        if kind != "DECJZ":
            for nz in labels:
                for z in labels: opts.append(DecJz(r, nz, z))
        if kind != "EMIT":
            for nxt in labels: opts.append(Emit(r, nxt))
        return tuple(opts)
    report: Dict[str, Dict[str, int]] = {}
    for missing in INSTRUCTION_CLASS_NAMES:
        opts = options_without(missing); checked = violations = successful_pairs = 0
        for pair in product(opts, repeat=2):
            p = Program((r,), "L0", {"L0": pair[0], "L1": pair[1]}); checked += 1
            if missing == "READ":
                a = execute(p, (0,), 8); b = execute(p, (1,), 8)
                if a.terminal == b.terminal == "HALTED":
                    successful_pairs += 1
                    if a.output != b.output or a.registers != b.registers: violations += 1
            elif missing == "EMIT":
                for inp in ((), (0,), (1,)):
                    if execute(p, inp, 8).output: violations += 1
            elif missing == "INC":
                x = execute(p, (), 8)
                if x.terminal == "HALTED":
                    successful_pairs += 1
                    if any(v > 0 for _, v in x.registers) or any(v > 0 for v in x.output): violations += 1
            elif missing == "DECJZ":
                a = execute(p, (0,), 8); b = execute(p, (1,), 8)
                if a.terminal == b.terminal == "HALTED":
                    successful_pairs += 1
                    if tuple(e.kind for e in a.trace) != tuple(e.kind for e in b.trace) or len(a.output) != len(b.output): violations += 1
            elif missing == "HALT":
                for inp in ((), (0,), (1,)):
                    if execute(p, inp, 8).terminal == "HALTED": violations += 1
        report[missing] = {"programs_checked": checked, "successful_controls": successful_pairs, "violations": violations}
    return report

@dataclass(frozen=True)
class Mealy:
    states: Tuple[int, ...]
    start: int
    delta: Mapping[Tuple[int, int], int]
    output: Mapping[Tuple[int, int], int]

def validate_mealy(m: Mealy) -> Tuple[str, ...]:
    errors = []
    if not m.states or len(set(m.states)) != len(m.states): errors.append("STATES")
    if m.start not in set(m.states): errors.append("START")
    keys = {(q, a) for q in m.states for a in (0, 1)}
    if set(m.delta) != keys or any(v not in set(m.states) for v in m.delta.values()): errors.append("DELTA")
    if set(m.output) != keys or any(v not in (0, 1) for v in m.output.values()): errors.append("OUTPUT")
    return tuple(errors)

def direct_mealy(m: Mealy, word: Sequence[int]) -> Tuple[int, ...]:
    errors = validate_mealy(m)
    if errors: raise ValueError(";".join(errors))
    q = m.start; out = []
    for a in word:
        if a not in (0, 1): raise ValueError("binary input required")
        out.append(m.output[(q, a)]); q = m.delta[(q, a)]
    return tuple(out)

def compile_mealy(m: Mealy) -> Program:
    errors = validate_mealy(m)
    if errors: raise ValueError(";".join(errors))
    state_index = {q: i for i, q in enumerate(m.states)}; I: Dict[str, object] = {}
    def read_label(q): return f"q{state_index[q]}_read"
    for q in m.states:
        i = state_index[q]
        I[f"q{i}_read"] = Read("rin", f"q{i}_d0")
        I[f"q{i}_d0"] = DecJz("rin", f"q{i}_d1", f"q{i}_out0")
        I[f"q{i}_d1"] = DecJz("rin", f"q{i}_d2", f"q{i}_out1")
        I[f"q{i}_d2"] = DecJz("rin", "invalid", "halt_eof")
        for a in (0, 1):
            base = f"q{i}_out{a}"; target = read_label(m.delta[(q, a)])
            if m.output[(q, a)] == 0:
                I[base] = Emit("rout", target)
            else:
                I[base] = Inc("rout", base + "_emit")
                I[base + "_emit"] = Emit("rout", base + "_clear")
                I[base + "_clear"] = DecJz("rout", target, target)
    I["halt_eof"] = Halt(); I["invalid"] = Inc("rin", "invalid")
    return Program(("rin", "rout"), read_label(m.start), I)

def execute_compiled_mealy(m: Mealy, word: Sequence[int]) -> ExecutionResult:
    p = compile_mealy(m); return execute(p, tuple(word) + (2,), 6 * len(word) + 5)

def all_binary_words(max_len: int) -> Tuple[Tuple[int, ...], ...]:
    out = []
    for n in range(max_len + 1): out.extend(product((0, 1), repeat=n))
    return tuple(tuple(w) for w in out)

def exhaustive_mealy_census() -> Dict[str, int]:
    states = (0, 1); keys = ((0,0),(0,1),(1,0),(1,1)); words = all_binary_words(3)
    machines = comparisons = mismatches = terminal_failures = overhead_failures = 0; max_program = max_steps = 0
    for delta_bits in product((0,1), repeat=4):
        delta = dict(zip(keys, delta_bits))
        for out_bits in product((0,1), repeat=4):
            out = dict(zip(keys, out_bits)); m = Mealy(states, 0, delta, out); p = compile_mealy(m); machines += 1
            max_program = max(max_program, len(p.instructions))
            if len(p.instructions) > 10 * len(states) + 2: overhead_failures += 1
            for w in words:
                comparisons += 1; direct = direct_mealy(m, w); got = execute_compiled_mealy(m, w); max_steps = max(max_steps, got.resources.steps)
                if got.terminal != "HALTED": terminal_failures += 1; continue
                if got.output != direct: mismatches += 1
                if got.resources.steps > 6 * len(w) + 5: overhead_failures += 1
                if recount_resources(p, got.trace) != got.resources: overhead_failures += 1
    return {"machines": machines, "words_per_machine": len(words), "comparisons": comparisons, "behavior_mismatches": mismatches, "terminal_failures": terminal_failures, "overhead_or_resource_failures": overhead_failures, "max_program_instructions": max_program, "max_execution_steps": max_steps}

def execute_counter_fragment(program: Program, step_budget: int = 16) -> Tuple[str, Tuple[Tuple[str,int],...], int]:
    if any(not isinstance(i, (Inc, DecJz, Halt)) for i in program.instructions.values()): raise ValueError("not counter fragment")
    malformed = validate_program(program)
    if malformed: return ("MALFORMED_PROGRAM", (), 0)
    regs = {r:0 for r in program.registers}; pc = program.start_label; steps = 0
    while True:
        if steps >= step_budget: return ("STEP_BUDGET_EXHAUSTED", tuple(sorted(regs.items())), steps)
        instr = program.instructions[pc]; steps += 1
        if isinstance(instr, Halt): return ("HALTED", tuple(sorted(regs.items())), steps)
        if isinstance(instr, Inc): regs[instr.register] += 1; pc = instr.next_label
        elif isinstance(instr, DecJz):
            if regs[instr.register] > 0: regs[instr.register] -= 1; pc = instr.nonzero_label
            else: pc = instr.zero_label
        else: raise AssertionError

def counter_fragment_census() -> Dict[str, int]:
    labels = ("L0","L1"); opts = [Halt()]; opts += [Inc("r", n) for n in labels]; opts += [DecJz("r", nz, z) for nz in labels for z in labels]
    programs = mismatches = 0
    for pair in product(opts, repeat=2):
        p = Program(("r",), "L0", {"L0":pair[0], "L1":pair[1]}); programs += 1
        src = execute_counter_fragment(p, 16); tgt = execute(p, (), 16)
        if src != (tgt.terminal, tgt.registers, tgt.resources.steps): mismatches += 1
    return {"programs": programs, "comparisons": programs, "mismatches": mismatches}

def alpha_rename(program: Program, label_prefix: str, register_prefix: str) -> Program:
    lmap = {l: label_prefix + l for l in program.instructions}; rmap = {r: register_prefix + r for r in program.registers}; new = {}
    for label, instr in program.instructions.items():
        nl = lmap[label]
        if isinstance(instr, Read): new[nl] = Read(rmap[instr.register], lmap[instr.next_label])
        elif isinstance(instr, Inc): new[nl] = Inc(rmap[instr.register], lmap[instr.next_label])
        elif isinstance(instr, DecJz): new[nl] = DecJz(rmap[instr.register], lmap[instr.nonzero_label], lmap[instr.zero_label])
        elif isinstance(instr, Emit): new[nl] = Emit(rmap[instr.register], lmap[instr.next_label])
        elif isinstance(instr, Halt): new[nl] = Halt()
        else: new[nl] = instr
    return Program(tuple(rmap[r] for r in program.registers), lmap[program.start_label], new)

def sequential_compose(p: Program, q: Program) -> Program:
    if validate_program(p) or validate_program(q): raise ValueError("composition requires well-formed programs")
    pp = alpha_rename(p, "P::", "P::"); qq = alpha_rename(q, "Q::", "Q::"); link_reg = "LINK::zero"
    if link_reg in pp.registers or link_reg in qq.registers: raise ValueError("reserved link register collision")
    instructions = dict(pp.instructions); instructions.update(qq.instructions)
    for label, instr in list(instructions.items()):
        if label.startswith("P::") and isinstance(instr, Halt): instructions[label] = DecJz(link_reg, qq.start_label, qq.start_label)
    return Program(pp.registers + qq.registers + (link_reg,), pp.start_label, instructions)

def composition_control() -> Dict[str, Any]:
    p = Program(("r",), "inc", {"inc":Inc("r","emit"),"emit":Emit("r","halt"),"halt":Halt()})
    q = Program(("r",), "inc", {"inc":Inc("r","emit"),"emit":Emit("r","halt"),"halt":Halt()})
    c = sequential_compose(p,q); res = execute(c, (), 20)
    return {"terminal": res.terminal, "output": res.output, "program_instructions": res.resources.program_instructions, "steps": res.resources.steps}

def recurrence_control() -> Dict[str, Any]:
    p = Program(("r",), "i1", {"i1":Inc("r","i2"), "i2":Inc("r","i3"), "i3":Inc("r","loop"), "loop":DecJz("r","loop","halt"), "halt":Halt()})
    res = execute(p, (), 20); return {"terminal":res.terminal,"loop_visits":sum(e.label == "loop" for e in res.trace),"final_registers":res.registers}

def storage_control() -> Dict[str, Any]:
    p = Program(("cell7",), "inc", {"inc":Inc("cell7","emit"),"emit":Emit("cell7","halt"),"halt":Halt()}); res = execute(p, (), 10)
    return {"terminal":res.terminal,"output":res.output,"final_registers":res.registers}

def build_receipt() -> Dict[str, Any]:
    positive = verify_positive_requirements(); absence = bounded_absence_census(); mealy = exhaustive_mealy_census(); counter = counter_fragment_census(); comp = composition_control(); recur = recurrence_control(); storage = storage_control()
    terminal = "GMI_833_G0_REGISTER_CORE_V1_ALL_GREEN"
    if not all(positive.values()) or any(row["violations"] for row in absence.values()) or any(mealy[k] for k in ("behavior_mismatches","terminal_failures","overhead_or_resource_failures")) or counter["mismatches"]: terminal = "RED"
    if comp["terminal"] != "HALTED" or tuple(comp["output"]) != (1,1): terminal = "RED"
    if recur["terminal"] != "HALTED" or recur["loop_visits"] != 4: terminal = "RED"
    if storage["terminal"] != "HALTED" or tuple(storage["output"]) != (1,): terminal = "RED"
    return {"schema":"GMI833G0RegisterCoreReceiptV1","issue":868,"parent_issue":833,"source_main":SOURCE_MAIN,"freeze_commit":FREEZE_COMMIT,"claim_ceiling":CLAIM_CEILING,"instruction_classes":list(INSTRUCTION_CLASS_NAMES),"requirement_positive_controls":positive,"bounded_absence_census":absence,"mealy_compiler_census":mealy,"counter_fragment_identity":counter,"composition":comp,"recurrence":recur,"static_register_storage":storage,"resource_vector":["program_instructions","steps","register_reads","register_writes","input_reads","output_writes"],"forbidden_promotions":list(FORBIDDEN_PROMOTIONS),"terminal":terminal}

def main() -> None:
    print(json.dumps(build_receipt(), indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
